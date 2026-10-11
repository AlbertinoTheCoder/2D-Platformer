#include "ScintillaObstacles.h"
#include "ScintillaWorld.h"
#include "ScintillaPlayer.h"
#include "ScintillaHealth.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Engine/StaticMesh.h"

AScintillaObstacle::AScintillaObstacle()
{
    PrimaryActorTick.bCanEverTick=true;
    auto* Root=CreateDefaultSubobject<USceneComponent>(TEXT("Root")); SetRootComponent(Root);
    BaseMesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Base")); BaseMesh->SetupAttachment(Root);
    MovingMesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MovingPart")); MovingMesh->SetupAttachment(Root);
    WarningMesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Warning")); WarningMesh->SetupAttachment(Root);
    for(auto* Mesh:{BaseMesh.Get(),MovingMesh.Get(),WarningMesh.Get()}) { Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision); Mesh->SetMobility(EComponentMobility::Movable); }
}
void AScintillaObstacle::OnConstruction(const FTransform& T) { Super::OnConstruction(T); ConfigureObstacle(); }
void AScintillaObstacle::ConfigureObstacle()
{
    auto Set=[](UStaticMeshComponent* Mesh,const TCHAR* Name) { Mesh->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,*FString::Printf(TEXT("/Game/Platformer/Art/Difficulty/%s.%s"),Name,Name))); };
    BaseMesh->SetRelativeTransform(FTransform::Identity); MovingMesh->SetRelativeTransform(FTransform::Identity);
    MovingMesh->SetVisibility(ObstacleType!=EScintillaObstacleType::Ice);
    if(ObstacleType==EScintillaObstacleType::Wind)
    {
        Set(BaseMesh,TEXT("SM_WindHousing")); Set(MovingMesh,TEXT("SM_WindRotor"));
        const float MountZ=WindDirection.Z<-.5f ? -180.f : -100.f;
        BaseMesh->SetRelativeLocation(FVector(-180,-85,MountZ)); MovingMesh->SetRelativeLocation(FVector(-180,-31,MountZ+70));
    }
    else if(ObstacleType==EScintillaObstacleType::Ice) Set(BaseMesh,TEXT("SM_IceDeck"));
    else if(ObstacleType==EScintillaObstacleType::FallingSpikes)
    { Set(BaseMesh,TEXT("SM_SpikeRail")); BaseMesh->SetRelativeLocation(FVector(0,0,320)); Set(MovingMesh,TEXT("SM_SpikeRack")); MovingMesh->SetRelativeRotation(FRotator(180,0,0)); }
    else if(ObstacleType==EScintillaObstacleType::RisingSpikes)
    { Set(BaseMesh,TEXT("SM_RetractBase")); Set(MovingMesh,TEXT("SM_SpikeRack")); }
    else
    { Set(BaseMesh,TEXT("SM_TrapMotor")); BaseMesh->SetRelativeLocation(FVector(0,-40,220)); Set(MovingMesh,ObstacleType==EScintillaObstacleType::Hammer ? TEXT("SM_RotatingHammer") : TEXT("SM_RotatingAxe")); MovingMesh->SetRelativeLocation(FVector(0,0,220)); }
    WarningMesh->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cylinder.Cylinder")));
    WarningMesh->SetRelativeScale3D(FVector(1.6f,.7f,.025f)); WarningMesh->SetRelativeLocation(FVector(0,0,3));
    if(ObstacleType==EScintillaObstacleType::Wind) WarningMesh->SetRelativeLocation(FVector(-180,0,(WindDirection.Z<-.5f ? -180.f : -100.f)+3));
    if(auto* M=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Platformer/Art/Robot/M_RobotRigidGlow.M_RobotRigidGlow"))) WarningMesh->SetMaterial(0,M);
    WarningMesh->SetVisibility(false);
}
void AScintillaObstacle::BeginPlay() { Super::BeginPlay(); ConfigureObstacle(); Clock=PhaseOffset; Evaluate(Clock); }
bool AScintillaObstacle::IsSlipperyAt(FVector P) const
{ const FVector D=P-GetActorLocation(); return ObstacleType==EScintillaObstacleType::Ice && FMath::Abs(D.X)<RegionHalfWidth && FMath::Abs(D.Y)<95 && D.Z>=30 && D.Z<75; }
void AScintillaObstacle::HitPlayerAt(FVector Center,FVector Half)
{
    auto* P=Cast<AScintillaPlayer>(UGameplayStatics::GetPlayerPawn(this,0));
    if(!P || !P->ControlsAllowed()) return;
    const FVector D=P->GetActorLocation()-Center;
    if(FMath::Abs(D.X)<Half.X+24 && FMath::Abs(D.Y)<Half.Y+24 && FMath::Abs(D.Z)<Half.Z+44) P->ReceiveHazard(Center);
}
void AScintillaObstacle::Evaluate(float T)
{
    const float Cycle=FMath::Fmod(FMath::Max(0.f,T),6.f);
    Active=false; Warning=false;
    if(ObstacleType==EScintillaObstacleType::Wind)
    {
        Warning=Cycle>=1 && Cycle<2; Active=Cycle>=2 && Cycle<4;
        MovingMesh->SetRelativeRotation(FRotator(T*(Active ? 650.f : 70.f),0,0));
    }
    else if(ObstacleType==EScintillaObstacleType::FallingSpikes)
    {
        Warning=Cycle<1.0f; Active=Cycle>=1 && Cycle<2;
        float Z=320;
        if(Cycle>=1 && Cycle<1.45f) Z=FMath::Lerp(320.f,62.f,(Cycle-1)/.45f);
        else if(Cycle>=1.45f && Cycle<2) Z=62;
        else if(Cycle>=2 && Cycle<3) Z=FMath::Lerp(62.f,320.f,Cycle-2);
        MovingMesh->SetRelativeLocation(FVector(0,0,Z));
        if(Active) HitPlayerAt(GetActorLocation()+FVector(0,0,Z-31),FVector(70,35,31));
    }
    else if(ObstacleType==EScintillaObstacleType::RisingSpikes)
    {
        Warning=Cycle>=1 && Cycle<2;
        const float Rise=Cycle>=2 && Cycle<2.3f ? (Cycle-2)/.3f : Cycle>=2.3f && Cycle<3.5f ? 1.f : Cycle>=3.5f && Cycle<4 ? (4-Cycle)/.5f : 0.f;
        Active=Rise>.2f; MovingMesh->SetRelativeLocation(FVector(0,0,-65+65*Rise)); MovingMesh->SetVisibility(Rise>0);
        if(Active) HitPlayerAt(GetActorLocation()+FVector(0,0,20*Rise),FVector(70,35,30*Rise));
    }
    else if(ObstacleType==EScintillaObstacleType::Hammer || ObstacleType==EScintillaObstacleType::Axe)
    {
        // Long safe interval, amber cue, one full revolution, then park overhead.
        Warning=Cycle>=1 && Cycle<2; Active=Cycle>=2 && Cycle<4;
        const float Angle=Active ? 180+180*(Cycle-2) : 180;
        MovingMesh->SetRelativeRotation(FRotator(Angle,0,0));
        if(Active) HitPlayerAt(MovingMesh->GetComponentTransform().TransformPosition(FVector(ObstacleType==EScintillaObstacleType::Axe ? -40 : 0,0,-170)),FVector(ObstacleType==EScintillaObstacleType::Axe ? 48 : 55,38,28));
    }
    WarningMesh->SetVisibility(Warning || Active);
    if(auto* MI=WarningMesh->CreateAndSetMaterialInstanceDynamic(0)) MI->SetVectorParameterValue(TEXT("Tint"),Active ? FLinearColor(1,.16f,.06f) : FLinearColor(1,.65f,.1f));
}
void AScintillaObstacle::Tick(float Dt)
{
    Super::Tick(Dt);
    auto* GS=GetWorld()->GetGameState<AScintillaGameState>(); if(GS && GS->Completed) return;
    const int32 Difficulty=GS ? GS->Difficulty : 0;
    Clock+=Dt*(1+.18f*Difficulty); Evaluate(Clock);
    if(ObstacleType==EScintillaObstacleType::Wind && Active)
    {
        auto* P=Cast<AScintillaPlayer>(UGameplayStatics::GetPlayerPawn(this,0));
        if(!P || !P->ControlsAllowed()) return;
        const FVector D=P->GetActorLocation()-GetActorLocation();
        if(FMath::Abs(D.X)<RegionHalfWidth && FMath::Abs(D.Y)<100 && FMath::Abs(D.Z)<230)
        {
            const float Ramp=FMath::Clamp((FMath::Fmod(Clock,6.f)-2)/.35f,0.f,1.f);
            auto* M=P->GetCharacterMovement();
            M->AddForce(WindDirection.GetSafeNormal()*(160.f+70.f*Difficulty)*Ramp*M->Mass);
        }
    }
}
