#include "ScintillaPlayer.h"
#include "ScintillaHealth.h"
#include "ScintillaWorld.h"
#include "ScintillaUI.h"
#include "ScintillaObstacles.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimSequence.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "EnhancedInputComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/OverlapResult.h"
#include "EngineUtils.h"
#include "TimerManager.h"
#include "DrawDebugHelpers.h"
#include "UObject/ConstructorHelpers.h"
#include "InputCoreTypes.h"

AScintillaPlayer::AScintillaPlayer()
{
    PrimaryActorTick.bCanEverTick = true;
    GetCapsuleComponent()->InitCapsuleSize(24,44);
    bUseControllerRotationYaw = false;
    auto* Movement = GetCharacterMovement();
    Movement->MaxWalkSpeed = 600;
    Movement->MaxAcceleration = 4200;
    Movement->BrakingDecelerationWalking = 5000;
    Movement->GroundFriction = 8;
    Movement->AirControl = .8f;
    Movement->JumpZVelocity = 780;
    Movement->GravityScale = 1800.f / 980.f;
    Movement->bOrientRotationToMovement = false;
    Movement->bConstrainToPlane = true;
    Movement->SetPlaneConstraintNormal(FVector(0,1,0));
    Movement->bSnapToPlaneAtStart = true;
    Health = CreateDefaultSubobject<UScintillaHealth>(TEXT("Health"));
    Body = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Body"));
    Body->SetupAttachment(GetRootComponent());
    Body->SetRelativeScale3D(FVector(.42f,.3f,.62f));
    Body->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Eye = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Eye"));
    Eye->SetupAttachment(GetRootComponent());
    Eye->SetRelativeLocation(FVector(8,17,12));
    Eye->SetRelativeScale3D(FVector(.15f,.045f,.12f));
    Eye->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    if (Cube.Succeeded()) { Body->SetStaticMesh(Cube.Object); Eye->SetStaticMesh(Cube.Object); }
    static ConstructorHelpers::FObjectFinder<USkeletalMesh> Robot(TEXT("/Game/Platformer/Art/Robot/SK_Scintilla.SK_Scintilla"));
    if (Robot.Succeeded()) GetMesh()->SetSkeletalMesh(Robot.Object);
    GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    GetMesh()->SetRelativeLocation(FVector(0,0,-41.65f));
    GetMesh()->SetRelativeRotation(FRotator::ZeroRotator);
    GetMesh()->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    const TCHAR* Names[]={TEXT("Idle"),TEXT("Run"),TEXT("Jump"),TEXT("Fall"),TEXT("Attack"),TEXT("Hurt"),TEXT("Death"),TEXT("Land")};
    for (int32 Index=0;Index<UE_ARRAY_COUNT(Names);++Index)
    {
        const FString Path=FString::Printf(TEXT("/Game/Platformer/Art/Robot/A_Scintilla_%s.A_Scintilla_%s"),Names[Index],Names[Index]);
        ConstructorHelpers::FObjectFinder<UAnimSequence> Clip(*Path);
        if (Clip.Succeeded()) AnimationClips.Add(static_cast<EScintillaState>(Index),Clip.Object);
    }
}
void AScintillaPlayer::BeginPlay()
{
    Super::BeginPlay();
    if (GetMesh()->GetSkeletalMeshAsset()) { Body->SetVisibility(false); Eye->SetVisibility(false); }
    Health->Damaged.AddDynamic(this, &AScintillaPlayer::OnDamaged);
    Health->Died.AddDynamic(this, &AScintillaPlayer::OnDied);
    auto* GS = GetWorld()->GetGameState<AScintillaGameState>();
    if (GS && !GS->HasCheckpoint) GS->RespawnPosition = GetActorLocation();
    AScintillaCamera* Cam = GetWorld()->SpawnActor<AScintillaCamera>();
    if (Cam) { Cam->Target=this; Cam->SnapToTarget(); Camera=Cam; }
    if (auto* PC=Cast<APlayerController>(GetController())) PC->SetViewTarget(Cam ? static_cast<AActor*>(Cam) : this);
}
bool AScintillaPlayer::ControlsAllowed() const
{
    const auto* GS = GetWorld() ? GetWorld()->GetGameState<AScintillaGameState>() : nullptr;
    return Health && !Health->IsDead() && (!GS || !GS->Completed);
}
void AScintillaPlayer::SetupPlayerInputComponent(UInputComponent* Input)
{
    Super::SetupPlayerInputComponent(Input);
    auto* EIC=Cast<UEnhancedInputComponent>(Input);
    auto* PC=Cast<AScintillaController>(GetController());
    if (!EIC || !PC) return;
    EIC->BindAction(PC->MoveAction,ETriggerEvent::Triggered,this,&AScintillaPlayer::MoveInput);
    EIC->BindAction(PC->MoveAction,ETriggerEvent::Completed,this,&AScintillaPlayer::MoveInput);
    EIC->BindAction(PC->JumpAction,ETriggerEvent::Started,this,&AScintillaPlayer::PressJump);
    EIC->BindAction(PC->JumpAction,ETriggerEvent::Completed,this,&AScintillaPlayer::ReleaseJump);
    EIC->BindAction(PC->JumpAction,ETriggerEvent::Canceled,this,&AScintillaPlayer::ReleaseJump);
    EIC->BindAction(PC->AttackAction,ETriggerEvent::Started,this,&AScintillaPlayer::Attack);
    EIC->BindAction(PC->InteractAction,ETriggerEvent::Started,this,&AScintillaPlayer::Interact);
    Input->BindKey(EKeys::S,IE_Pressed,this,&AScintillaPlayer::FaceCamera);
    Input->BindKey(EKeys::W,IE_Pressed,this,&AScintillaPlayer::FaceCity);
}
void AScintillaPlayer::MoveInput(const FInputActionValue& Value) { MoveAxis(Value.Get<float>()); }
void AScintillaPlayer::MoveAxis(float Axis)
{
    MoveValue=ControlsAllowed() ? FMath::Clamp(Axis,-1.f,1.f) : 0;
    if (FMath::Abs(MoveValue)>.1f)
    {
        Facing=FMath::Sign(MoveValue);
        LookDirection=Facing<0 ? EScintillaLookDirection::Left : EScintillaLookDirection::Right;
    }
}
void AScintillaPlayer::FaceCamera()
{
    if(ControlsAllowed() && (!GetWorld()->GetFirstPlayerController() || !GetWorld()->GetFirstPlayerController()->IsPaused())) LookDirection=EScintillaLookDirection::Camera;
}
void AScintillaPlayer::FaceCity()
{
    if(ControlsAllowed() && (!GetWorld()->GetFirstPlayerController() || !GetWorld()->GetFirstPlayerController()->IsPaused())) LookDirection=EScintillaLookDirection::City;
}
void AScintillaPlayer::PressJump()
{
    if (!ControlsAllowed()) return;
    JumpHeld=true;
    JumpPressedTime=GetWorld()->GetTimeSeconds();
    TryBufferedJump();
}
void AScintillaPlayer::ReleaseJump()
{
    JumpHeld=false;
    if (GetCharacterMovement()->Velocity.Z>0)
        GetCharacterMovement()->Velocity.Z *= JumpReleaseMultiplier;
}
void AScintillaPlayer::TryBufferedJump()
{
    if (!ControlsAllowed()) return;
    const double Now=GetWorld()->GetTimeSeconds();
    auto* M=GetCharacterMovement();
    if (Now-JumpPressedTime > JumpBufferSeconds || JumpConsumed) return;
    if (!M->IsMovingOnGround() && Now-LastGroundTime>CoyoteSeconds) return;
    M->SetMovementMode(MOVE_Falling);
    M->Velocity.Z=M->JumpZVelocity * (JumpHeld ? 1.f : JumpReleaseMultiplier);
    JumpConsumed=true;
    JumpPressedTime=-100;
    LastGroundTime=-100;
    if (JumpSound) UGameplayStatics::PlaySoundAtLocation(this,JumpSound,GetActorLocation());
    Feedback(TEXT("Jump"));
}
void AScintillaPlayer::Landed(const FHitResult& Hit)
{
    Super::Landed(Hit);
    LastGroundTime=GetWorld()->GetTimeSeconds();
    JumpConsumed=false;
    LandingSquash=.15f;
    LandUntil=GetWorld()->GetTimeSeconds()+.2667;
    if (LandSound) UGameplayStatics::PlaySoundAtLocation(this,LandSound,GetActorLocation());
    Feedback(TEXT("Land"));
    // CharacterMovement establishes its walking base after Landed returns.
    // Consume the buffer on the next actor tick instead of replacing that base here.
}
void AScintillaPlayer::Tick(float Dt)
{
    Super::Tick(Dt);
    auto* M=GetCharacterMovement();
    const double Now=GetWorld()->GetTimeSeconds();
    bool Slipping=false;
    if(M->IsMovingOnGround()) for(TActorIterator<AScintillaObstacle> It(GetWorld());It;++It)
        if(It->IsSlipperyAt(GetActorLocation())) { Slipping=true; break; }
    const auto* Run=GetWorld()->GetGameState<AScintillaGameState>();
    M->GroundFriction=Slipping ? .20f : 8.f;
    M->BrakingDecelerationWalking=Slipping ? (Run && Run->Difficulty>0 ? 100.f : 180.f) : 5000.f;
    M->BrakingFrictionFactor=Slipping ? 0.f : 2.f;
    if (ControlsAllowed())
    {
        AddMovementInput(FVector(1,0,0),MoveValue);
        if (M->IsMovingOnGround()) { LastGroundTime=Now; JumpConsumed=false; }
        TryBufferedJump();
    }
    M->GravityScale=RisingGravity / FMath::Max(1.f,FMath::Abs(GetWorld()->GetGravityZ())) * (M->Velocity.Z<0 ? FallingMultiplier : 1.f);
    if (Health->IsDead()) AnimationState=EScintillaState::Death;
    else if (Now<HurtUntil-Health->InvulnerabilitySeconds+.4f) AnimationState=EScintillaState::Hurt;
    else if (Now<AttackPoseUntil) AnimationState=EScintillaState::Attack;
    else if (M->IsFalling()) AnimationState=M->Velocity.Z>0 ? EScintillaState::Jump : EScintillaState::Fall;
    else if (Now<LandUntil && FMath::Abs(M->Velocity.X)<20) AnimationState=EScintillaState::Land;
    else AnimationState=FMath::Abs(M->Velocity.X)>20 ? EScintillaState::Run : EScintillaState::Idle;
    if (GetMesh()->GetSkeletalMeshAsset())
    {
        // The rig's front is +Y. Opposite side profiles are exact world-X mirrors.
        const float Yaw=LookDirection==EScintillaLookDirection::Left ? 90.f : LookDirection==EScintillaLookDirection::Right ? -90.f : LookDirection==EScintillaLookDirection::City ? 180.f : 0.f;
        GetMesh()->SetRelativeRotation(FMath::RInterpTo(GetMesh()->GetRelativeRotation(),FRotator(0,Yaw,0),Dt,14.f));
        GetMesh()->SetRelativeScale3D(FVector(LookDirection==EScintillaLookDirection::Left ? -1.f : 1.f,1,1));
        if (PlayingState!=AnimationState)
        {
            if (const auto* Clip=AnimationClips.Find(AnimationState))
                GetMesh()->PlayAnimation(*Clip,AnimationState==EScintillaState::Idle || AnimationState==EScintillaState::Run);
            PlayingState=AnimationState;
        }
        GetMesh()->SetPlayRate(AnimationState==EScintillaState::Run ? FMath::Clamp(FMath::Abs(M->Velocity.X)/600.f,.35f,1.3f) : 1.f);
        GetMesh()->SetVisibility(Health->IsDead() || Now>=HurtUntil || (static_cast<int>(Now*18)%2)==0);
        Body->SetVisibility(false); Eye->SetVisibility(false);
    }
    if (GetActorLocation().Z < -500 && ControlsAllowed()) Health->Kill();
}
void AScintillaPlayer::Attack()
{
    const double Now=GetWorld()->GetTimeSeconds();
    if (!ControlsAllowed() || Now<NextAttackTime) return;
    LookDirection=Facing<0 ? EScintillaLookDirection::Left : EScintillaLookDirection::Right;
    NextAttackTime=Now+AttackCooldown;
    AttackUntil=Now+.1f;
    AttackPoseUntil=Now+.3f;
    const FVector Center=GetActorLocation()+FVector(Facing*(AttackReach*.5f+20),0,0);
    const FVector Extent(AttackReach*.5f,65,42);
    TArray<FOverlapResult> Results;
    FCollisionQueryParams Params; Params.AddIgnoredActor(this);
    GetWorld()->OverlapMultiByObjectType(Results,Center,FQuat::Identity,FCollisionObjectQueryParams(ECC_WorldDynamic),FCollisionShape::MakeBox(Extent),Params);
    TSet<AScintillaEnemy*> HitEnemies;
    for (const auto& Result:Results) if (auto* Enemy=Cast<AScintillaEnemy>(Result.GetActor())) HitEnemies.Add(Enemy);
    for (auto* Enemy:HitEnemies) Enemy->TakeStrike();
    if (DebugAttack) DrawDebugBox(GetWorld(),Center,Extent,FColor::Cyan,false,.1f);
    Feedback(TEXT("Attack"));
}
void AScintillaPlayer::Interact()
{
    if (!ControlsAllowed()) return;
    for (TActorIterator<AScintillaGoal> It(GetWorld());It;++It)
        if (FVector::DistSquared(It->GetActorLocation(),GetActorLocation()) < FMath::Square(180.f)) It->Activate(this);
}
void AScintillaPlayer::ReceiveHazard(FVector Origin)
{
    if (ControlsAllowed()) Health->ApplyHit(1,Origin);
}
void AScintillaPlayer::OnDamaged(FVector Origin)
{
    HurtUntil=GetWorld()->GetTimeSeconds()+Health->InvulnerabilitySeconds;
    LaunchCharacter(FVector(GetActorLocation().X>=Origin.X ? 230 : -230,0,280),true,true);
    if (DamageSound) UGameplayStatics::PlaySoundAtLocation(this,DamageSound,GetActorLocation());
    Feedback(TEXT("Damage"));
}
void AScintillaPlayer::OnDied()
{
    if(auto* GS=GetWorld()->GetGameState<AScintillaGameState>()) if(!GS->Completed) ++GS->Deaths;
    MoveValue=0;
    JumpPressedTime=LastGroundTime=-100;
    JumpHeld=false;
    GetCharacterMovement()->DisableMovement();
    GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Feedback(TEXT("Death"));
    GetWorldTimerManager().SetTimer(RespawnTimer,this,&AScintillaPlayer::Respawn,.8f,false);
}
void AScintillaPlayer::Respawn()
{
    auto* GS=GetWorld()->GetGameState<AScintillaGameState>();
    if (GS && GS->Completed) return;
    if(GS && GS->Deaths>=GS->AttemptLimit())
    { if(auto* PC=Cast<AScintillaController>(GetController())) PC->RestartPrototype(); return; }
    SetBase(static_cast<FMovementBaseInterfaceData*>(nullptr));
    SetActorLocation(GS ? GS->RespawnPosition : FVector(100,0,100),false,nullptr,ETeleportType::TeleportPhysics);
    GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    GetCharacterMovement()->SetMovementMode(MOVE_Falling);
    GetCharacterMovement()->StopMovementImmediately();
    JumpPressedTime=LastGroundTime=-100;
    JumpConsumed=false; JumpHeld=false; MoveValue=0;
    HurtUntil=GetWorld()->GetTimeSeconds()+.5f;
    PlayingState=EScintillaState::Death;
    AttackPoseUntil=LandUntil=-100;
    Health->ResetHealth();
    if (Camera.IsValid()) Camera->SnapToTarget();
}
AScintillaCamera::AScintillaCamera()
{
    PrimaryActorTick.bCanEverTick=true;
    CameraComponent=CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
    SetRootComponent(CameraComponent);
    CameraComponent->ProjectionMode=ECameraProjectionMode::Orthographic;
    CameraComponent->OrthoWidth=1600;
    CameraComponent->bConstrainAspectRatio=false;
    CameraComponent->bOverrideAspectRatioAxisConstraint=true;
    CameraComponent->AspectRatioAxisConstraint=EAspectRatioAxisConstraint::AspectRatio_MaintainXFOV;
    CameraComponent->PostProcessSettings.bOverride_AutoExposureMethod=true;
    CameraComponent->PostProcessSettings.AutoExposureMethod=EAutoExposureMethod::AEM_Manual;
    // Flat emissive art uses unit exposure, independent of photographic camera settings.
    CameraComponent->PostProcessSettings.bOverride_AutoExposureApplyPhysicalCameraExposure=true;
    CameraComponent->PostProcessSettings.AutoExposureApplyPhysicalCameraExposure=false;
    CameraComponent->PostProcessSettings.bOverride_AutoExposureBias=true;
    CameraComponent->PostProcessSettings.AutoExposureBias=0;
}
void AScintillaCamera::SnapToTarget()
{
    if (!Target) return;
    for (TActorIterator<AScintillaGoal> It(GetWorld());It;++It)
        CameraMaxX=FMath::Max(7300.f,It->GetActorLocation().X-300.f);
    SetActorLocation(FVector(Target->GetActorLocation().X+100,1500,Target->GetActorLocation().Z+160));
    SetActorRotation(FRotator(0,-90,0));
}
void AScintillaCamera::Tick(float Dt)
{
    Super::Tick(Dt);
    if(CityReveal)
    {
        RevealTime+=Dt;
        const float T=FMath::Clamp((RevealTime-.45f)/5.f,0.f,1.f);
        const float Smooth=T*T*(3-2*T);
        SetActorLocation(FMath::Lerp(RevealStart,RevealCenter,Smooth));
        CameraComponent->OrthoWidth=FMath::Lerp(RevealStartWidth,RevealWidth,Smooth);
        return;
    }
    if (!Target) return;
    const FVector Position=Target->GetActorLocation();
    FVector Current=GetActorLocation();
    const float Ahead=FMath::Clamp(Target->GetVelocity().X/600.f,-1.f,1.f)*LookAhead;
    Current.X=FMath::FInterpTo(Current.X,FMath::Clamp(Position.X+Ahead,500.f,CameraMaxX),Dt,HorizontalSmoothing);
    Current.Z=FMath::FInterpTo(Current.Z,FMath::Clamp(Position.Z+160,200.f,400.f),Dt,VerticalSmoothing);
    SetActorLocation(Current);
}
void AScintillaCamera::BeginCityReveal(FVector Center,float Width)
{
    if(CityReveal) return;
    CityReveal=true; RevealTime=0; RevealStart=GetActorLocation(); RevealCenter=Center;
    RevealStartWidth=CameraComponent->OrthoWidth; RevealWidth=FMath::Max(Width,RevealStartWidth);
}
