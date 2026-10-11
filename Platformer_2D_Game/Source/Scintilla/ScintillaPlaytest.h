#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ScintillaPlaytest.generated.h"
class AScintillaPlayer;

/** Opt-in runtime integration probe. Only spawned with -ScintillaSmoke. */
UCLASS(NotBlueprintable)
class AScintillaPlaytest : public AActor
{
    GENERATED_BODY()
public:
    AScintillaPlaytest();
    virtual void Tick(float DeltaSeconds) override;
private:
    void Check(const FString& Name,bool Passed);
    void Advance();
    void Place(FVector Position);
    void TickRoute(float DeltaSeconds);
    void Finish(const FString& FileName);
    UPROPERTY() TObjectPtr<AScintillaPlayer> Player;
    float Elapsed=0;
    int32 Stage=0;
    float StartX=0;
    float FullJumpPeak=0;
    float ShortJumpPeak=0;
    bool Released=false;
    TArray<FString> Checks;
    int32 Failures=0;
    bool RouteMode=false;
    int32 RouteStep=0;
    double JumpReleaseAt=-1;
    float RouteDuration=0;
    float CrossUntilX=-FLT_MAX;
    FVector LeftFootPhase=FVector::ZeroVector;
    float EnemyTravelDistance=0;
    float LastEnemyX=0;
    UPROPERTY() TObjectPtr<class AScintillaEnemy> EnemyProbe;
};
