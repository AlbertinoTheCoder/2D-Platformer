#include "ScintillaWorld.h"
#include "ScintillaPlayer.h"
#include "ScintillaHealth.h"
#include "ScintillaUI.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"
#include "TimerManager.h"
#include "UObject/ConstructorHelpers.h"
#include "Engine/StaticMesh.h"
#include "StaticMeshResources.h"
#include "ScintillaCampaign.h"

namespace
{
    void SetColor(UStaticMeshComponent* Mesh,FLinearColor Color)
    {
        if (auto* MI=Mesh->CreateAndSetMaterialInstanceDynamic(0)) MI->SetVectorParameterValue(TEXT("Tint"),Color);
    }
    void SetupCube(UStaticMeshComponent* Mesh)
    {
        static UStaticMesh* Cube=LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube"));
        Mesh->SetStaticMesh(Cube);
    }
}
AScintillaGameMode::AScintillaGameMode()
{
    DefaultPawnClass=AScintillaPlayer::StaticClass();
    PlayerControllerClass=AScintillaController::StaticClass();
    GameStateClass=AScintillaGameState::StaticClass();
}
AScintillaGameState::AScintillaGameState() { PrimaryActorTick.bCanEverTick=true; }
void AScintillaGameState::Tick(float Dt)
{
    Super::Tick(Dt);
    if(!Completed) { RunSeconds+=Dt; return; }
    if(RestorationReady) return;
    RestorationElapsed+=Dt;
    if(RestorationElapsed>=RestorationDuration)
    {
        RestorationReady=true;
        if(auto* PC=Cast<AScintillaController>(UGameplayStatics::GetPlayerController(this,0))) PC->ShowCompletion();
    }
}
void AScintillaGameState::CalculateRating()
{
    RatingTargetSeconds=ScintillaCampaign::RatingTargets[ScintillaCampaign::Index(this)];
    SpeedPoints=40.f*FMath::Clamp(2.f-RunSeconds/RatingTargetSeconds,0.f,1.f);
    DamagePoints=30.f*FMath::Clamp(1.f-DamageTaken/5.f,0.f,1.f);
    EnergyPoints=30.f*(TotalEnergy>0 ? FMath::Clamp(float(Energy)/TotalEnergy,0.f,1.f) : 0.f);
    RatingScore=SpeedPoints+DamagePoints+EnergyPoints;
    RatingGrade=RatingScore>=90 ? TEXT("S") : RatingScore>=80 ? TEXT("A") : RatingScore>=65 ? TEXT("B") : RatingScore>=50 ? TEXT("C") : TEXT("D");
}
void AScintillaGameState::CompleteLevel()
{
    if (Completed) return;
    CalculateRating(); RatingDismissed=false;
    Completed=true;
    float Length=8000;
    for (TActorIterator<AScintillaCity> It(GetWorld());It;++It) { It->RestorePower(); Length=It->CityLength; }
    for(TActorIterator<AScintillaCamera> It(GetWorld());It;++It) It->BeginCityReveal(FVector(Length*.5f,1500,350),Length+1100);
    if (auto* P=Cast<AScintillaPlayer>(UGameplayStatics::GetPlayerPawn(this,0)))
    { P->GetCharacterMovement()->StopMovementImmediately(); P->GetCharacterMovement()->DisableMovement(); P->Feedback(TEXT("Complete")); }
    if (auto* PC=Cast<AScintillaController>(UGameplayStatics::GetPlayerController(this,0))) PC->ShowCompletion();
}
AScintillaPlatform::AScintillaPlatform()
{
    Surface=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Surface")); SetRootComponent(Surface);
    SetupCube(Surface);
    Surface->SetCollisionProfileName(TEXT("BlockAll"));
}
AScintillaMovingPlatform::AScintillaMovingPlatform()
{
    PrimaryActorTick.bCanEverTick=true;
    Surface->SetMobility(EComponentMobility::Movable);
    PrimaryActorTick.TickGroup=TG_PrePhysics;
}
void AScintillaMovingPlatform::BeginPlay() { Super::BeginPlay(); StartPosition=GetActorLocation(); }
void AScintillaMovingPlatform::Tick(float Dt)
{
    Super::Tick(Dt);
    if (Finished) return;
    if (WaitRemaining>0) { WaitRemaining-=Dt; return; }
    const FVector Dest=StartPosition+(ToEnd ? EndOffset : FVector::ZeroVector);
    SetActorLocation(FMath::VInterpConstantTo(GetActorLocation(),Dest,Dt,FMath::Max(0.f,Speed)));
    if (GetActorLocation().Equals(Dest,.1f))
    {
        WaitRemaining=WaitSeconds;
        if (!Loop) Finished=true;
        ToEnd=!ToEnd;
    }
}
AScintillaTrigger::AScintillaTrigger()
{
    PrimaryActorTick.bCanEverTick=false;
    Trigger=CreateDefaultSubobject<UBoxComponent>(TEXT("Trigger")); SetRootComponent(Trigger);
    Trigger->SetBoxExtent(FVector(35,80,45));
    Trigger->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    Trigger->SetCollisionObjectType(ECC_WorldDynamic);
    Trigger->SetCollisionResponseToAllChannels(ECR_Ignore);
    Trigger->SetCollisionResponseToChannel(ECC_Pawn,ECR_Overlap);
    Trigger->SetGenerateOverlapEvents(true);
    Visual=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Visual"));
    Visual->SetupAttachment(Trigger); SetupCube(Visual);
    Visual->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Visual->SetRelativeScale3D(FVector(.4f,.25f,.6f));
}
void AScintillaTrigger::BeginPlay()
{ Super::BeginPlay(); Trigger->OnComponentBeginOverlap.AddDynamic(this,&AScintillaTrigger::OnOverlap); }
void AScintillaTrigger::OnOverlap(UPrimitiveComponent*,AActor* Other,UPrimitiveComponent*,int32,bool,const FHitResult&)
{ if (auto* Player=Cast<AScintillaPlayer>(Other)) if (Player->ControlsAllowed()) Touch(Player); }
AScintillaCoin::AScintillaCoin()
{
    Trigger->SetBoxExtent(FVector(25,70,25));
    Visual->SetRelativeScale3D(FVector(.18f,.12f,.28f));
    Visual->SetRelativeRotation(FRotator(0,0,35));
}
void AScintillaCoin::BeginPlay()
{
    Super::BeginPlay(); SetColor(Visual,FLinearColor(.1f,1,.9f));
    if (auto* GS=GetWorld()->GetGameState<AScintillaGameState>()) ++GS->TotalEnergy;
}
void AScintillaCoin::Touch(AScintillaPlayer* P)
{
    if (Collected) return;
    Collected=true;
    Trigger->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    if (auto* GS=GetWorld()->GetGameState<AScintillaGameState>()) ++GS->Energy;
    if (auto* PC=Cast<AScintillaController>(P->GetController())) PC->RefreshHUD();
    if (CollectSound) UGameplayStatics::PlaySoundAtLocation(this,CollectSound,GetActorLocation());
    P->Feedback(TEXT("Coin"));
    Visual->SetRelativeScale3D(Visual->GetRelativeScale3D()*1.6f);
    SetLifeSpan(.12f);
}
AScintillaHazard::AScintillaHazard()
{
    Trigger->SetBoxExtent(FVector(50,90,20));
    Visual->SetRelativeScale3D(FVector(1,.5f,.25f));
}
void AScintillaHazard::BeginPlay()
{
    Super::BeginPlay(); SetColor(Visual,FLinearColor(1,.08f,.1f));
    if (InstantKill) Visual->SetVisibility(false);
    GetWorldTimerManager().SetTimer(ContactTimer,this,&AScintillaHazard::CheckContacts,.1f,true);
}
void AScintillaHazard::CheckContacts()
{
    TArray<AActor*> Actors; Trigger->GetOverlappingActors(Actors,AScintillaPlayer::StaticClass());
    for (auto* Actor:Actors) if (auto* P=Cast<AScintillaPlayer>(Actor)) if (P->ControlsAllowed()) Touch(P);
}
void AScintillaHazard::Touch(AScintillaPlayer* P)
{ if (InstantKill) P->Health->Kill(); else P->ReceiveHazard(GetActorLocation()); }
AScintillaCheckpoint::AScintillaCheckpoint() { Visual->SetRelativeScale3D(FVector(.25f,.3f,.9f)); }
void AScintillaCheckpoint::SetActive(bool Value)
{ Active=Value; SetColor(Visual,Value ? FLinearColor(.2f,1,.6f) : FLinearColor(.1f,.3f,.5f)); }
void AScintillaCheckpoint::Touch(AScintillaPlayer* P)
{
    auto* GS=GetWorld()->GetGameState<AScintillaGameState>();
    if (!GS || Active) return;
    if (GS->ActiveCheckpoint) GS->ActiveCheckpoint->SetActive(false);
    GS->ActiveCheckpoint=this; GS->HasCheckpoint=true; GS->RespawnPosition=GetActorLocation()+RespawnOffset;
    SetActive(true);
    if (ActivateSound) UGameplayStatics::PlaySoundAtLocation(this,ActivateSound,GetActorLocation());
    P->Feedback(TEXT("Checkpoint"));
    if (auto* PC=Cast<AScintillaController>(P->GetController())) PC->RefreshHUD();
}
AScintillaGoal::AScintillaGoal() { Trigger->SetBoxExtent(FVector(55,80,90)); Visual->SetRelativeScale3D(FVector(.9f,.5f,1.5f)); }
void AScintillaGoal::Touch(AScintillaPlayer* P) { Activate(P); }
void AScintillaGoal::Activate(AScintillaPlayer* P)
{
    if (!P || !P->ControlsAllowed()) return;
    if (auto* GS=GetWorld()->GetGameState<AScintillaGameState>())
    {
        if (GS->Completed) return;
        SetColor(Visual,FLinearColor(1,.6f,.12f));
        if (CompleteSound) UGameplayStatics::PlaySoundAtLocation(this,CompleteSound,GetActorLocation());
        GS->CompleteLevel();
    }
}
AScintillaEnemy::AScintillaEnemy()
{
    PrimaryActorTick.bCanEverTick=true;
    Collision=CreateDefaultSubobject<UBoxComponent>(TEXT("Collision")); SetRootComponent(Collision);
    Collision->SetBoxExtent(FVector(27,25,25));
    Collision->SetCollisionObjectType(ECC_WorldDynamic);
    Collision->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    Collision->SetCollisionResponseToAllChannels(ECR_Block);
    Collision->SetCollisionResponseToChannel(ECC_Pawn,ECR_Ignore);
    Visual=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Visual")); Visual->SetupAttachment(Collision);
    SetupCube(Visual); Visual->SetRelativeScale3D(FVector(.54f,.5f,.5f)); Visual->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Contact=CreateDefaultSubobject<UBoxComponent>(TEXT("Contact")); Contact->SetupAttachment(Collision);
    Contact->SetBoxExtent(FVector(31,60,32));
    Contact->SetCollisionEnabled(ECollisionEnabled::QueryOnly); Contact->SetCollisionResponseToAllChannels(ECR_Ignore);
    Contact->SetCollisionResponseToChannel(ECC_Pawn,ECR_Overlap); Contact->SetGenerateOverlapEvents(true);
    MotionPart=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MotionPart")); MotionPart->SetupAttachment(Visual);
    MotionPartRight=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MotionPartRight")); MotionPartRight->SetupAttachment(Visual);
    MotionPart->SetCollisionEnabled(ECollisionEnabled::NoCollision); MotionPartRight->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}
void AScintillaEnemy::ConfigureEnemy()
{
    if(EnemyType==EScintillaEnemyType::Flyer || EnemyType==EScintillaEnemyType::SurveyFlyer)
    {
        const TCHAR* Model=EnemyType==EScintillaEnemyType::Flyer ? TEXT("SM_FlyerWasp") : TEXT("SM_FlyerSurvey");
        Visual->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,*FString::Printf(TEXT("/Game/Platformer/Art/Difficulty/%s.%s"),Model,Model)));
        Visual->EmptyOverrideMaterials(); Visual->SetRelativeScale3D(FVector(.8f)); Visual->SetRelativeLocation(FVector(0,0,-15));
        Collision->SetBoxExtent(FVector(35,25,25)); Contact->SetBoxExtent(FVector(38,60,32));
        auto* Wing=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Platformer/Art/Difficulty/SM_FlyerWing.SM_FlyerWing"));
        MotionPart->SetStaticMesh(Wing); MotionPartRight->SetStaticMesh(Wing);
        MotionPart->SetRelativeLocation(FVector(36,0,12)); MotionPartRight->SetRelativeLocation(FVector(-36,0,12));
        MotionPart->SetRelativeScale3D(FVector(-.8f,.8f,.8f)); MotionPartRight->SetRelativeScale3D(FVector(.8f));
        MotionPart->SetVisibility(true); MotionPartRight->SetVisibility(true); Armor=1; return;
    }
    const TCHAR* Name=EnemyType==EScintillaEnemyType::Scout ? TEXT("Scout") : EnemyType==EScintillaEnemyType::Charger ? TEXT("Charger") : TEXT("Sentinel");
    const FString Path=FString::Printf(TEXT("/Game/Platformer/Art/Enemies/SM_Enemy%s.SM_Enemy%s"),Name,Name);
    if(auto* Mesh=LoadObject<UStaticMesh>(nullptr,*Path)) Visual->SetStaticMesh(Mesh);
    Visual->EmptyOverrideMaterials(); Visual->SetRelativeScale3D(FVector(.7f)); Visual->SetRelativeLocation(FVector(0,0,-27));
    Collision->SetBoxExtent(FVector(EnemyType==EScintillaEnemyType::Charger ? 34 : 27,25,25));
    Contact->SetBoxExtent(FVector(EnemyType==EScintillaEnemyType::Charger ? 37 : 31,60,32));
    MotionPart->SetVisibility(EnemyType!=EScintillaEnemyType::Sentinel); MotionPartRight->SetVisibility(EnemyType==EScintillaEnemyType::Charger);
    const FString Part=EnemyType==EScintillaEnemyType::Scout ? TEXT("Rotor") : TEXT("Wheel");
    auto* PartMesh=LoadObject<UStaticMesh>(nullptr,*FString::Printf(TEXT("/Game/Platformer/Art/Enemies/SM_Enemy%s.SM_Enemy%s"),*Part,*Part));
    MotionPart->SetStaticMesh(PartMesh); MotionPartRight->SetStaticMesh(PartMesh);
    MotionPart->SetRelativeScale3D(FVector(1)); MotionPartRight->SetRelativeScale3D(FVector(1));
    MotionPart->SetRelativeLocation(EnemyType==EScintillaEnemyType::Scout ? FVector(0,0,76) : FVector(-28,0,16));
    MotionPartRight->SetRelativeLocation(FVector(28,0,16));
    Armor=EnemyType==EScintillaEnemyType::Sentinel ? 2 : 1;
}
void AScintillaEnemy::BeginPlay()
{
    Super::BeginPlay(); ConfigureEnemy(); FlightHeight=GetActorLocation().Z;
    for(int32 Slot=0;Slot<Visual->GetNumMaterials();++Slot)
        if(Visual->GetMaterialSlotNames()[Slot].ToString().Contains(TEXT("Optic")))
        { CoreMaterial=Visual->CreateAndSetMaterialInstanceDynamic(Slot); break; }
    Contact->OnComponentBeginOverlap.AddDynamic(this,&AScintillaEnemy::ContactPlayer);
    GetWorldTimerManager().SetTimer(ContactTimer,this,&AScintillaEnemy::CheckContact,.1f,true);
}
void AScintillaEnemy::ContactPlayer(UPrimitiveComponent*,AActor* Other,UPrimitiveComponent*,int32,bool,const FHitResult&)
{
    auto* P=Cast<AScintillaPlayer>(Other);
    if (!P || Defeated || !P->ControlsAllowed()) return;
    if (P->GetVelocity().Z < -30 && P->GetActorLocation().Z-44 >= GetActorLocation().Z+10)
    { Defeat(); P->LaunchCharacter(FVector(0,0,520),false,true); }
    else P->ReceiveHazard(GetActorLocation());
}
void AScintillaEnemy::CheckContact()
{
    TArray<AActor*> Actors; Contact->GetOverlappingActors(Actors,AScintillaPlayer::StaticClass());
    for (auto* A:Actors) ContactPlayer(nullptr,A,nullptr,0,false,FHitResult());
}
void AScintillaEnemy::Tick(float Dt)
{
    Super::Tick(Dt);
    if (Defeated) return;
    if(auto* GS=GetWorld()->GetGameState<AScintillaGameState>()) if(GS->Completed) return;
    AnimationTime+=Dt;
    if(EnemyType==EScintillaEnemyType::Flyer || EnemyType==EScintillaEnemyType::SurveyFlyer)
    {
        FVector Pos=GetActorLocation();
        if(Pos.X>=PatrolMaxX) Direction=-1; if(Pos.X<=PatrolMinX) Direction=1;
        const auto* GS=GetWorld()->GetGameState<AScintillaGameState>();
        Pos.X=FMath::Clamp(Pos.X+Direction*Speed*(1+.15f*(GS ? GS->Difficulty : 0))*Dt,PatrolMinX,PatrolMaxX);
        Pos.Z=FlightHeight+28*FMath::Sin(AnimationTime*1.8f);
        SetActorLocation(Pos,false);
        MotionPart->SetRelativeRotation(FRotator(25*FMath::Sin(AnimationTime*14),0,0));
        MotionPartRight->SetRelativeRotation(FRotator(-25*FMath::Sin(AnimationTime*14),0,0));
        Visual->SetRelativeRotation(FRotator(Direction*5,0,0)); return;
    }
    float MoveSpeed=EnemyType==EScintillaEnemyType::Sentinel ? FMath::Min(Speed,55.f) : Speed;
    if(EnemyType==EScintillaEnemyType::Charger)
    {
        PhaseRemaining-=Dt;
        if(Phase==EScintillaEnemyPhase::Patrol)
        {
            auto* P=Cast<AScintillaPlayer>(UGameplayStatics::GetPlayerPawn(this,0));
            if(P && P->ControlsAllowed() && FMath::Abs(P->GetActorLocation().X-GetActorLocation().X)<280 && FMath::Abs(P->GetActorLocation().Z-GetActorLocation().Z)<65)
            { Phase=EScintillaEnemyPhase::Windup; PhaseRemaining=.8f; Direction=P->GetActorLocation().X<GetActorLocation().X ? -1 : 1; }
        }
        else if(PhaseRemaining<=0)
        {
            if(Phase==EScintillaEnemyPhase::Windup) { Phase=EScintillaEnemyPhase::Dashing; PhaseRemaining=.4f; }
            else if(Phase==EScintillaEnemyPhase::Dashing) { Phase=EScintillaEnemyPhase::Recovery; PhaseRemaining=1.4f; }
            else Phase=EScintillaEnemyPhase::Patrol;
        }
        MoveSpeed=Phase==EScintillaEnemyPhase::Dashing ? 300.f : Phase==EScintillaEnemyPhase::Patrol ? Speed : 0.f;
        if(CoreMaterial) CoreMaterial->SetVectorParameterValue(TEXT("Tint"),Phase==EScintillaEnemyPhase::Windup ? FLinearColor(2,1.1f,.1f)*(1.f+.35f*FMath::Sin(AnimationTime*22)) : FLinearColor(1,.63f,.15f));
    }
    Visual->SetRelativeLocation(FVector(0,0,-27+(EnemyType==EScintillaEnemyType::Scout ? 5+2*FMath::Sin(AnimationTime*5) : 0)));
    Visual->SetRelativeRotation(FRotator(EnemyType==EScintillaEnemyType::Charger && Phase==EScintillaEnemyPhase::Windup ? Direction*-5.f : 0,0,0));
    PartAngle+=Dt*(EnemyType==EScintillaEnemyType::Scout ? 1100.f : Direction*MoveSpeed*5);
    MotionPart->SetRelativeRotation(EnemyType==EScintillaEnemyType::Scout ? FRotator(0,PartAngle,0) : FRotator(PartAngle,0,0));
    MotionPartRight->SetRelativeRotation(FRotator(PartAngle,0,0));
    if(EnemyType==EScintillaEnemyType::Sentinel && CoreMaterial)
        CoreMaterial->SetVectorParameterValue(TEXT("Tint"),(Armor==2 ? FLinearColor(.72f,.36f,1) : FLinearColor(.25f,1,1))*(1.f+.08f*FMath::Sin(AnimationTime*4)));
    FVector Pos=GetActorLocation();
    if(EnemyType!=EScintillaEnemyType::Charger || Phase==EScintillaEnemyPhase::Patrol)
    {
        if (Pos.X>=PatrolMaxX) Direction=-1;
        if (Pos.X<=PatrolMinX) Direction=1;
    }
    FHitResult Ground;
    FCollisionQueryParams Params; Params.AddIgnoredActor(this);
    const FVector Probe=Pos+FVector(Direction*45,0,0);
    if (!GetWorld()->LineTraceSingleByChannel(Ground,Probe,Probe-FVector(0,0,100),ECC_Visibility,Params))
    {
        if(EnemyType==EScintillaEnemyType::Charger && Phase==EScintillaEnemyPhase::Dashing) { Phase=EScintillaEnemyPhase::Recovery; PhaseRemaining=1.4f; MoveSpeed=0; }
        else Direction=-Direction;
    }
    FHitResult Wall;
    const float NextX=FMath::Clamp(Pos.X+Direction*MoveSpeed*Dt,PatrolMinX,PatrolMaxX);
    AddActorWorldOffset(FVector(NextX-Pos.X,0,0),true,&Wall);
    if(EnemyType==EScintillaEnemyType::Charger && Phase==EScintillaEnemyPhase::Dashing && (Wall.bBlockingHit || NextX==PatrolMinX || NextX==PatrolMaxX))
    { Phase=EScintillaEnemyPhase::Recovery; PhaseRemaining=1.4f; }
    if (Wall.bBlockingHit) Direction=-Direction;
}
void AScintillaEnemy::TakeStrike()
{
    if(Defeated || GetWorld()->GetTimeSeconds()<NextHitTime) return;
    NextHitTime=GetWorld()->GetTimeSeconds()+.2;
    if(--Armor<=0) { Defeat(); return; }
    if(CoreMaterial) CoreMaterial->SetVectorParameterValue(TEXT("Tint"),FLinearColor(.25f,1,1));
}
void AScintillaEnemy::Defeat()
{
    if (Defeated) return;
    Defeated=true; SetActorTickEnabled(false); GetWorldTimerManager().ClearTimer(ContactTimer);
    Contact->SetCollisionEnabled(ECollisionEnabled::NoCollision); Collision->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Visual->SetRelativeScale3D(Visual->GetRelativeScale3D()*FVector(1.1f,1,.2f));
    MotionPart->SetVisibility(false); MotionPartRight->SetVisibility(false);
    if (DeathSound) UGameplayStatics::PlaySoundAtLocation(this,DeathSound,GetActorLocation());
    SetLifeSpan(.25f);
}
AScintillaCity::AScintillaCity()
{
    PrimaryActorTick.bCanEverTick=true;
    auto* Root=CreateDefaultSubobject<USceneComponent>(TEXT("Root")); SetRootComponent(Root);
}
void AScintillaCity::AddBlock(FName Name,FVector Location,FVector Size,FLinearColor Color,bool Window)
{
    auto* Mesh=NewObject<UStaticMeshComponent>(this,Name);
    AddInstanceComponent(Mesh); Mesh->SetupAttachment(GetRootComponent());
    Mesh->SetMobility(EComponentMobility::Movable); SetupCube(Mesh);
    Mesh->SetRelativeLocation(Location); Mesh->SetRelativeScale3D(Size/100.f);
    Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    if (ColorMaterial) Mesh->SetMaterial(0,ColorMaterial);
    Mesh->RegisterComponent(); SetColor(Mesh,Color);
    if (Window) Windows.Add(Mesh); else Buildings.Add(Mesh);
}
void AScintillaCity::BuildCity()
{
    // Idempotent, only replaces this actor's generated components.
    TArray<UStaticMeshComponent*> Existing; GetComponents(Existing);
    for (auto* Mesh:Existing) { RemoveInstanceComponent(Mesh); Mesh->DestroyComponent(); }
    Windows.Empty(); Buildings.Empty();
    AddBlock(TEXT("Backdrop"),FVector(CityLength*.5f,-1000,350),FVector(CityLength+6000,30,16000),FLinearColor(.006f,.01f,.025f),false);
    AddModel(TEXT("Terrain"),TEXT("SM_CityTerrain"),FVector(CityLength*.5f,-900,-350),FVector((CityLength+2200)/800.f,1,5));
    AddBlock(TEXT("RepairPulse"),FVector(0,80,400),FVector(8,6,1400),FLinearColor(.3f,2,1.4f),true);
    // Uneven heights, setbacks and staggered streets replace the repeated factory skyline.
    for (int32 i=0;i<24;++i)
    {
        const float X=-200+i*(CityLength+300)/23.f;
        const float H=380+(i*137)%650;
        const float Y=-420-(i%3)*110;
        const float Width=270+(i*53)%120;
        const int32 Variant=i%3+1;
        const float ScaleZ=H/(320+(Variant-1)*30);
        AddModel(FString::Printf(TEXT("Facade%d"),i),FString::Printf(TEXT("SM_CityFacade%d"),Variant),FVector(X,Y,-60),FVector(Width/(230+(Variant-1)*15),.95f,ScaleZ));
        AddModel(FString::Printf(TEXT("Roof%d"),i),TEXT("SM_CityRoof"),FVector(X,Y,H-60),FVector(Width/250,.95f,1));
        AddModel(FString::Printf(TEXT("Decay%d"),i),TEXT("SM_CityDecay"),FVector(X-Width*.22f,Y+65,H-450),FVector(1.3f,1,1.5f));
        AddModel(FString::Printf(TEXT("Rubble%d"),i),TEXT("SM_CityRubble"),FVector(X+Width*.3f,Y+80,-55),FVector(1.7f,1.1f,1.4f));
        if(i%2==0)
        {
            const FVector Tree(X-Width*.65f,Y+130,-60);
            AddModel(FString::Printf(TEXT("Tree%d"),i),TEXT("SM_CityDeadTree"),Tree,FVector(1.7f));
            AddModel(FString::Printf(TEXT("Foliage%d"),i),TEXT("SM_CityFoliage"),Tree,FVector(1.7f));
        }
    }
    GroundCity();
}
float AScintillaCity::GroundHeightAt(float X) const
{
    if(GroundProfile.IsEmpty()) return -60;
    for(int32 i=1;i<GroundProfile.Num();++i)
        if(X<=GroundProfile[i].X)
        {
            const auto& A=GroundProfile[i-1]; const auto& B=GroundProfile[i];
            return FMath::Lerp(A.Y,B.Y,FMath::Clamp((X-A.X)/(B.X-A.X),0.,1.));
        }
    return GroundProfile.Last().Y;
}
float AScintillaCity::FoundationHeight(float X,float HalfWidth) const
{
    float Height=FMath::Min(GroundHeightAt(X-HalfWidth),GroundHeightAt(X+HalfWidth));
    for(const auto& Point:GroundProfile) if(Point.X>X-HalfWidth && Point.X<X+HalfWidth) Height=FMath::Min(Height,static_cast<float>(Point.Y));
    return Height;
}
void AScintillaCity::GroundCity()
{
    TArray<UStaticMeshComponent*> Meshes; GetComponents(Meshes);
    UStaticMeshComponent* Terrain=nullptr;
    for(auto* Mesh:Meshes) if(Mesh->GetName()==TEXT("Terrain")) Terrain=Mesh;
#if WITH_EDITOR
    // Read the existing imported surface, including its actual FBX orientation.
    // Persist the profile in the map so packaged games need no CPU mesh buffers.
    if(Terrain && Terrain->GetStaticMesh() && Terrain->GetStaticMesh()->GetRenderData() && Terrain->GetStaticMesh()->GetRenderData()->LODResources.Num())
    {
        GroundProfile.Empty();
        const auto& Positions=Terrain->GetStaticMesh()->GetRenderData()->LODResources[0].VertexBuffers.PositionVertexBuffer;
        for(uint32 i=0;i<Positions.GetNumVertices();++i)
        {
            const FVector Point=Terrain->GetRelativeTransform().TransformPosition(FVector(Positions.VertexPosition(i)));
            auto* Existing=GroundProfile.FindByPredicate([&Point](const FVector2D& P){ return FMath::Abs(P.X-Point.X)<.1; });
            if(Existing) Existing->Y=FMath::Max(Existing->Y,Point.Z); else GroundProfile.Add(FVector2D(Point.X,Point.Z));
        }
        GroundProfile.Sort([](const FVector2D& A,const FVector2D& B){ return A.X<B.X; });
    }
#endif
    if(GroundProfile.Num()<2) return;
    for(auto* Mesh:Meshes)
    {
        const FString Name=Mesh->GetName(); if(!Name.StartsWith(TEXT("Facade")) || !Mesh->GetStaticMesh()) continue;
        const float HalfWidth=Mesh->GetStaticMesh()->GetBoundingBox().GetExtent().X*Mesh->GetRelativeScale3D().X;
        const float Bottom=Mesh->GetStaticMesh()->GetBoundingBox().Min.Z*Mesh->GetRelativeScale3D().Z;
        FVector Position=Mesh->GetRelativeLocation();
        // Bury the foundation slightly so its flat base also meets sloping ground
        // at both corners, including the small rotation of the ruined facade.
        const float Base=FoundationHeight(Position.X,HalfWidth)-Bottom-18;
        const float Shift=Base-Position.Z; Position.Z=Base; Mesh->SetRelativeLocation(Position);
        const FString Suffix=Name.Mid(6);
        for(auto* Part:Meshes)
            if(Part->GetName()==TEXT("Roof")+Suffix || Part->GetName()==TEXT("Decay")+Suffix)
                Part->AddLocalOffset(FVector(0,0,Shift));
    }
    for(auto* Mesh:Meshes)
    {
        const FString Name=Mesh->GetName(); if(!Mesh->GetStaticMesh()) continue;
        if(Name.StartsWith(TEXT("Tree")))
        {
            FVector Position=Mesh->GetRelativeLocation();
            Position.Z=GroundHeightAt(Position.X)-Mesh->GetStaticMesh()->GetBoundingBox().Min.Z*Mesh->GetRelativeScale3D().Z-6;
            Mesh->SetRelativeLocation(Position);
            for(auto* Part:Meshes) if(Part->GetName()==TEXT("Foliage")+Name.Mid(4)) Part->SetRelativeLocation(Position);
        }
        else if(Name.StartsWith(TEXT("Rubble")))
        {
            FVector Position=Mesh->GetRelativeLocation(); const auto Box=Mesh->GetStaticMesh()->GetBoundingBox();
            Position.Z=FoundationHeight(Position.X,Box.GetExtent().X*Mesh->GetRelativeScale3D().X)-Box.Min.Z*Mesh->GetRelativeScale3D().Z-6;
            Mesh->SetRelativeLocation(Position);
        }
    }
}
void AScintillaCity::AddModel(const FString& Name,const FString& Asset,FVector Location,FVector Scale)
{
    auto* Mesh=NewObject<UStaticMeshComponent>(this,FName(*Name)); AddInstanceComponent(Mesh); Mesh->SetupAttachment(GetRootComponent());
    Mesh->SetMobility(EComponentMobility::Movable);
    Mesh->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,*FString::Printf(TEXT("/Game/Platformer/Art/City/%s.%s"),*Asset,*Asset)));
    Mesh->SetRelativeLocation(Location); Mesh->SetRelativeScale3D(Scale);
    Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision); Mesh->RegisterComponent();
}
void AScintillaCity::BeginPlay()
{
    Super::BeginPlay();
    // Instance components persist in the map; recover arrays after loading.
    GroundCity();
    Windows.Empty(); Buildings.Empty();
    TArray<UStaticMeshComponent*> Meshes; GetComponents(Meshes);
    for (auto* M:Meshes)
    {
        FVector Position=M->GetRelativeLocation(); Position.Y=-FMath::Abs(Position.Y); M->SetRelativeLocation(Position);
        if (M->GetName().StartsWith(TEXT("Window"))) Windows.Add(M); else Buildings.Add(M);
    }
    for(TActorIterator<AActor> It(GetWorld());It;++It)
        if(It->ActorHasTag(TEXT("ScintillaRestore")))
        {
            TArray<UStaticMeshComponent*> Props; It->GetComponents(Props);
            for(auto* Prop:Props) { Prop->SetMobility(EComponentMobility::Movable); Meshes.Add(Prop); }
        }
    RepairPieces.Empty(); RepairTime=0;
    float Origin=CityLength;
    for(TActorIterator<AScintillaGoal> It(GetWorld());It;++It) Origin=It->GetActorLocation().X;
    for(auto* Mesh:Meshes)
    {
        FRepairPiece Piece; Piece.Mesh=Mesh; Piece.Intact=Mesh->GetRelativeTransform(); Piece.Broken=Piece.Intact;
        const FString Name=Mesh->GetName();
        Piece.Decay=Name.StartsWith(TEXT("Decay")) || Name.StartsWith(TEXT("Rubble"));
        Piece.Foliage=Name.StartsWith(TEXT("Foliage"));
        Piece.Delay=.25f+1.8f*FMath::Clamp(FMath::Abs(Mesh->GetComponentLocation().X-Origin)/CityLength,0.f,1.f);
        if(Name.StartsWith(TEXT("Roof")))
        {
            const float Sign=Meshes.IndexOfByKey(Mesh)%2 ? 1.f : -1.f;
            Piece.Broken.SetRotation(FRotator(Sign*19,0,0).Quaternion());
            Piece.Broken.AddToTranslation(FVector(Sign*45,50,-95));
        }
        else if(Name.StartsWith(TEXT("Facade")))
        {
            Piece.Broken.SetRotation(FRotator((Meshes.IndexOfByKey(Mesh)%2 ? 1.f : -1.f)*3.5f,0,0).Quaternion());
            Piece.Broken.SetScale3D(Piece.Intact.GetScale3D()*FVector(1,1,.90f));
        }
        else if(Mesh->GetOwner()!=this)
        {
            Piece.Broken.SetRotation((FRotator(8,0,0).Quaternion()*Piece.Intact.GetRotation()).GetNormalized());
            Piece.Broken.AddToTranslation(FVector(0,0,-25));
        }
        for(int32 Slot=0;Slot<Mesh->GetNumMaterials();++Slot)
        {
            auto* MI=Mesh->CreateAndSetMaterialInstanceDynamic(Slot);
            FLinearColor Tint=MI ? MI->K2_GetVectorParameterValue(TEXT("Tint")) : FLinearColor::White;
            if(Mesh->GetOwner()==this && !Mesh->GetMaterialSlotNames()[Slot].ToString().Contains(TEXT("Glass"))) Tint*=DistrictTint*2.f;
            Piece.Colors.Add(Tint);
        }
        RepairPieces.Add(Piece);
    }
    PowerBlend=Powered ? 1.f : 0.f;
    ApplyColors(PowerBlend); SetActorTickEnabled(Powered && PowerBlend<1);
}
void AScintillaCity::RestorePower() { if(Powered) return; Powered=true; RepairTime=0; SetActorTickEnabled(true); }
void AScintillaCity::ApplyColors(float Amount)
{
    for(auto& Piece:RepairPieces)
    {
        auto* Mesh=Piece.Mesh; if(!IsValid(Mesh)) continue;
        if(Mesh->GetName().StartsWith(TEXT("RepairPulse")))
        {
            Mesh->SetVisibility(Powered && RepairTime>.25f && RepairTime<2.9f);
            Mesh->SetRelativeLocation(FVector(CityLength*(1-FMath::Clamp((RepairTime-.25f)/2.6f,0.f,1.f)),80,400));
            if(auto* MI=Cast<UMaterialInstanceDynamic>(Mesh->GetMaterial(0))) MI->SetVectorParameterValue(TEXT("Tint"),FLinearColor(.3f,2,1.4f));
            continue;
        }
        const float T=Amount>=1 ? 1 : Powered ? FMath::Clamp((RepairTime-Piece.Delay)/2.6f,0.f,1.f) : 0;
        const float Smooth=T*T*(3-2*T);
        FTransform Transform; Transform.Blend(Piece.Broken,Piece.Intact,Smooth);
        if(Piece.Decay)
        {
            Transform.SetScale3D(Piece.Intact.GetScale3D()*FMath::Max(.001f,1-Smooth));
            Transform.AddToTranslation(FVector(0,-30*Smooth,70*FMath::Sin(T*PI)));
        }
        if(Piece.Foliage) Transform.SetScale3D(Piece.Intact.GetScale3D()*FMath::Max(.001f,Smooth));
        Mesh->SetRelativeTransform(Transform);
        Mesh->SetVisibility(!(Piece.Decay && T>=1) && !(Piece.Foliage && T<=0));
        for(int32 Slot=0;Slot<Piece.Colors.Num();++Slot)
            if(auto* MI=Cast<UMaterialInstanceDynamic>(Mesh->GetMaterial(Slot)))
            {
                const bool Glass=Mesh->GetMaterialSlotNames()[Slot].ToString().Contains(TEXT("Glass"));
                FLinearColor Tint=Piece.Colors[Slot]*FMath::Lerp(.32f,1.15f,Smooth);
                if(Glass) Tint=FMath::Lerp(FLinearColor(.025f,.045f,.04f),FLinearColor(1.8f,1.1f,.38f)*(FLinearColor(.7f,.7f,.7f)+DistrictTint*.7f),Smooth);
                if(Mesh->GetName()==TEXT("Backdrop")) Tint=FMath::Lerp(FLinearColor(.008f,.016f,.02f),FLinearColor(.045f,.095f,.13f),Smooth);
                MI->SetVectorParameterValue(TEXT("Tint"),Tint);
            }
    }
}
void AScintillaCity::Tick(float Dt)
{
    Super::Tick(Dt); RepairTime+=Dt; PowerBlend=FMath::Min(1.f,RepairTime/4.7f); ApplyColors(PowerBlend);
    if (PowerBlend>=1) SetActorTickEnabled(false);
}
