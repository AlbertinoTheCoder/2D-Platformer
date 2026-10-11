#include "ScintillaObstacles.h"
#include "ScintillaWorld.h"
#include "ScintillaPlayer.h"
#include "ScintillaHealth.h"
#include "Components/StaticMeshComponent.h"
#include "Components/CapsuleComponent.h"
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
    for(int32 I=0;I<3;++I)
    {
        auto* Streak=CreateDefaultSubobject<UStaticMeshComponent>(*FString::Printf(TEXT("WindStreak%d"),I));
        Streak->SetupAttachment(Root); Streak->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Streak->SetMobility(EComponentMobility::Movable); WindStreaks.Add(Streak);
    }
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
    else if(ObstacleType==EScintillaObstacleType::Ice)
    {
        Set(BaseMesh,TEXT("SM_IceDeck"));
        BaseMesh->SetRelativeScale3D(FVector(RegionHalfWidth/150.f,200.f/110.f,1));
        BaseMesh->SetRelativeLocation(FVector(0,0,-6.2f));
        if(auto* Ice=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Platformer/Art/Difficulty/MI_Difficulty_Ice.MI_Difficulty_Ice")))
            for(int32 I=0;I<BaseMesh->GetNumMaterials();++I) BaseMesh->SetMaterial(I,Ice);
    }
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
    for(auto& Streak:WindStreaks)
    {
        Streak->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cone.Cone")));
        Streak->SetRelativeScale3D(FVector(.13f,.13f,.40f));
        Streak->SetRelativeRotation(WindDirection.Z<-.5f ? FRotator(180,0,0) : FRotator(90,0,0));
        if(auto* M=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Platformer/Art/Difficulty/MI_Difficulty_Cyan.MI_Difficulty_Cyan"))) Streak->SetMaterial(0,M);
        Streak->SetVisibility(false);
    }
}
void AScintillaObstacle::BeginPlay() { Super::BeginPlay(); ConfigureObstacle(); Clock=PhaseOffset; Evaluate(Clock); }
bool AScintillaObstacle::IsSlipperyAt(FVector P) const
{ const FVector D=P-GetActorLocation(); return ObstacleType==EScintillaObstacleType::Ice && FMath::Abs(D.X)<=RegionHalfWidth+24 && FMath::Abs(D.Y)<125 && D.Z>=30 && D.Z<75; }
void AScintillaObstacle::HitPlayerAt(FVector Center,FVector Half)
{
    auto* P=Cast<AScintillaPlayer>(UGameplayStatics::GetPlayerPawn(this,0));
    if(!P || !P->ControlsAllowed()) return;
    const FVector D=P->GetActorLocation()-Center;
    if(FMath::Abs(D.X)<Half.X+24 && FMath::Abs(D.Y)<Half.Y+24 && FMath::Abs(D.Z)<Half.Z+44) P->ReceiveHazard(Center);
}
bool AScintillaObstacle::TouchesToolAt(FVector Center,float Radius,float HalfHeight) const
{
    if(ObstacleType!=EScintillaObstacleType::Hammer && ObstacleType!=EScintillaObstacleType::Axe) return false;
    // Match the authored FBX head/blade outline, rather than a world-aligned box.
    TArray<FVector2D> Outline;
    float Depth=32.f;
    if(ObstacleType==EScintillaObstacleType::Hammer)
        Outline={FVector2D(-54,-195),FVector2D(54,-195),FVector2D(54,-145),FVector2D(-54,-145)};
    else
    {
        Outline={FVector2D(5,-145),FVector2D(-72,-122),FVector2D(-100,-142),FVector2D(-82,-195),FVector2D(-45,-210),FVector2D(5,-185)};
        Depth=12.5f;
    }
    const float SegmentHalf=FMath::Max(0.f,HalfHeight-Radius);
    const FVector S=Center-FVector(0,0,SegmentHalf), E=Center+FVector(0,0,SegmentHalf);
    const FTransform Transform=MovingMesh->GetComponentTransform();
    const FVector Local=Transform.InverseTransformPosition(Center);
    bool Positive=false,Negative=false;
    for(int32 I=0;I<Outline.Num();++I)
    {
        const FVector2D A=Outline[I],B=Outline[(I+1)%Outline.Num()];
        const double Cross=(B.X-A.X)*(Local.Z-A.Y)-(B.Y-A.Y)*(Local.X-A.X);
        Positive|=Cross>UE_KINDA_SMALL_NUMBER; Negative|=Cross<-UE_KINDA_SMALL_NUMBER;
    }
    // A capsule wholly inside the solid may not intersect any surface triangle.
    if(FMath::Abs(Local.Y)<=Depth && !(Positive && Negative)) return true;
    TArray<FVector> V;
    for(float Y:{-Depth,Depth}) for(const auto& P:Outline) V.Add(Transform.TransformPosition(FVector(P.X,Y,P.Y)));
    auto TouchesTriangle=[&](FVector A,FVector B,FVector C)
    {
        FVector Intersection,Normal;
        if(FMath::SegmentTriangleIntersection(S,E,A,B,C,Intersection,Normal)) return true;
        float Distance=FMath::Min(FVector::DistSquared(S,FMath::ClosestPointOnTriangleToPoint(S,A,B,C)),FVector::DistSquared(E,FMath::ClosestPointOnTriangleToPoint(E,A,B,C)));
        for(const auto& Edge:TArray<TPair<FVector,FVector>>{{A,B},{B,C},{C,A}})
        {
            FVector P,Q; FMath::SegmentDistToSegmentSafe(S,E,Edge.Key,Edge.Value,P,Q);
            Distance=FMath::Min(Distance,float(FVector::DistSquared(P,Q)));
        }
        return Distance<=Radius*Radius;
    };
    const int32 N=Outline.Num();
    for(int32 I=1;I<N-1;++I)
        if(TouchesTriangle(V[0],V[I],V[I+1]) || TouchesTriangle(V[N],V[N+I],V[N+I+1])) return true;
    for(int32 I=0;I<N;++I)
    {
        const int32 J=(I+1)%N;
        if(TouchesTriangle(V[I],V[J],V[N+J]) || TouchesTriangle(V[I],V[N+J],V[N+I])) return true;
    }
    return false;
}
bool AScintillaObstacle::IsCrossingSafe(float LookAheadSeconds) const
{
    const auto* GS=GetWorld()->GetGameState<AScintillaGameState>();
    const float Speed=1+.18f*(GS ? GS->Difficulty : 0);
    for(int32 I=0;I<=4;++I)
    {
        const float T=Clock+(LookAheadSeconds+I*(ObstacleType==EScintillaObstacleType::Wind ? .3f : .1f))*Speed;
        if(ObstacleType==EScintillaObstacleType::Hammer || ObstacleType==EScintillaObstacleType::Axe)
        { if(FMath::Cos(T*2.f*PI/2.8f)>.25f) return false; }
        else if(ObstacleType==EScintillaObstacleType::RisingSpikes)
        { const float C=FMath::Fmod(T,2.4f); if(C>.8f && C<2.12f) return false; }
        else if(ObstacleType==EScintillaObstacleType::FallingSpikes)
        { const float C=FMath::Fmod(T,6.f); if(C>.65f && C<3.15f) return false; }
        else if(ObstacleType==EScintillaObstacleType::Wind)
        { const float C=FMath::Fmod(T,6.f); if(C>1.5f && C<4.1f) return false; }
    }
    return true;
}
void AScintillaObstacle::Evaluate(float T)
{
    const float Cycle=FMath::Fmod(FMath::Max(0.f,T),6.f);
    Active=false; Warning=false;
    if(ObstacleType==EScintillaObstacleType::Wind)
    {
        Warning=Cycle>=1 && Cycle<2; Active=Cycle>=2 && Cycle<4;
        // Rotor angle is integrated in Tick, so gust transitions do not snap it.
        for(int32 I=0;I<WindStreaks.Num();++I)
        {
            const float Travel=FMath::Fmod(T*1.8f+I/3.f,1.f);
            const FVector Origin=WindDirection.Z<-.5f ? FVector(0,-38,180) : FVector(RegionHalfWidth,-38,25+I*25);
            WindStreaks[I]->SetRelativeLocation(Origin+WindDirection.GetSafeNormal()*Travel*(WindDirection.Z<-.5f ? 270.f : RegionHalfWidth*2));
            WindStreaks[I]->SetVisibility(Active);
        }
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
        const float SpikeCycle=FMath::Fmod(FMath::Max(0.f,T),2.4f);
        Warning=SpikeCycle>=.8f && SpikeCycle<1.15f;
        float Rise=0;
        if(SpikeCycle>=1.15f && SpikeCycle<1.29f) Rise=FMath::SmoothStep(0.f,1.f,(SpikeCycle-1.15f)/.14f);
        else if(SpikeCycle>=1.29f && SpikeCycle<1.94f) Rise=1;
        else if(SpikeCycle>=1.94f && SpikeCycle<2.12f) Rise=1-FMath::SmoothStep(0.f,1.f,(SpikeCycle-1.94f)/.18f);
        // Keep the carrier inside the housing: only the teeth emerge above the deck.
        Active=Rise>.3f; MovingMesh->SetRelativeLocation(FVector(0,0,-68+54*Rise)); MovingMesh->SetVisibility(true);
        if(Active) HitPlayerAt(GetActorLocation()+FVector(0,0,-38+54*Rise),FVector(64,30,22));
    }
    else if(ObstacleType==EScintillaObstacleType::Hammer || ObstacleType==EScintillaObstacleType::Axe)
    {
        // Continuous full revolutions; wrapping the angle preserves the same transform.
        const float Angle=FMath::Fmod(T*360.f/2.8f,360.f);
        MovingMesh->SetRelativeRotation(FRotator(Angle,0,0));
        Active=true;
        auto* P=Cast<AScintillaPlayer>(UGameplayStatics::GetPlayerPawn(this,0));
        if(P && P->ControlsAllowed())
        {
            auto* Capsule=P->GetCapsuleComponent();
            if(TouchesToolAt(Capsule->GetComponentLocation(),Capsule->GetScaledCapsuleRadius(),Capsule->GetScaledCapsuleHalfHeight()))
                P->ReceiveHazard(MovingMesh->GetComponentLocation());
        }
    }
    WarningMesh->SetVisibility(Warning || Active);
    if(auto* MI=WarningMesh->CreateAndSetMaterialInstanceDynamic(0)) MI->SetVectorParameterValue(TEXT("Tint"),Active ? FLinearColor(1,.16f,.06f) : FLinearColor(1,.65f,.1f));
}
void AScintillaObstacle::Tick(float Dt)
{
    Super::Tick(Dt);
    auto* GS=GetWorld()->GetGameState<AScintillaGameState>(); if(GS && GS->Completed) return;
    const int32 Difficulty=GS ? GS->Difficulty : 0;
    const float PreviousClock=Clock;
    Clock+=Dt*(1+.18f*Difficulty);
    const bool Tool=ObstacleType==EScintillaObstacleType::Hammer || ObstacleType==EScintillaObstacleType::Axe;
    const int32 Steps=Tool ? FMath::Clamp(FMath::CeilToInt((Clock-PreviousClock)*360.f/2.8f/4.f),1,90) : 1;
    for(int32 I=1;I<=Steps;++I) Evaluate(FMath::Lerp(PreviousClock,Clock,float(I)/Steps));
    if(ObstacleType==EScintillaObstacleType::Wind)
    {
        RotorAngle=FMath::Fmod(RotorAngle+Dt*(Active ? 900.f : 100.f),360.f);
        MovingMesh->SetRelativeRotation(FRotator(RotorAngle,0,0));
    }
    if(ObstacleType==EScintillaObstacleType::Wind && Active)
    {
        auto* P=Cast<AScintillaPlayer>(UGameplayStatics::GetPlayerPawn(this,0));
        if(!P || !P->ControlsAllowed()) { PlayerInGust=false; return; }
        const FVector D=P->GetActorLocation()-GetActorLocation();
        if(FMath::Abs(D.X)<RegionHalfWidth && FMath::Abs(D.Y)<100 && FMath::Abs(D.Z)<230)
        {
            const float Ramp=FMath::Clamp((FMath::Fmod(Clock,6.f)-2)/.35f,0.f,1.f);
            auto* M=P->GetCharacterMovement();
            // A brief entry impulse makes the gust perceptible even against air control.
            if(!PlayerInGust) M->AddImpulse(WindDirection.GetSafeNormal()*(WindDirection.Z<-.5f ? 130.f : 150.f),true);
            const float Strength=(WindDirection.Z<-.5f ? 600.f : 1100.f)*(1+.2f*Difficulty);
            M->AddForce(WindDirection.GetSafeNormal()*Strength*Ramp*M->Mass);
            // CharacterMovement otherwise restores full running speed against the force
            // every frame. Ramp the opposing speed limit so a running player feels it too.
            if(WindDirection.X<-.5f && M->Velocity.X>0)
                M->Velocity.X=FMath::Min(M->Velocity.X,M->MaxWalkSpeed*FMath::Lerp(1.f,.60f-.05f*Difficulty,Ramp));
            PlayerInGust=true;
        }
        else PlayerInGust=false;
    }
    else PlayerInGust=false;
}
