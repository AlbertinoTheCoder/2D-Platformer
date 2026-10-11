#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ScintillaObstacles.generated.h"
class UStaticMeshComponent;
class AScintillaPlayer;
UENUM(BlueprintType)
enum class EScintillaObstacleType : uint8 { Wind, Ice, FallingSpikes, RisingSpikes, Hammer, Axe };
UCLASS()
class SCINTILLA_API AScintillaObstacle : public AActor
{
    GENERATED_BODY()
public:
    AScintillaObstacle();
    virtual void Tick(float DeltaSeconds) override;
    virtual void OnConstruction(const FTransform& Transform) override;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) EScintillaObstacleType ObstacleType=EScintillaObstacleType::Wind;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float PhaseOffset=0;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) FVector WindDirection=FVector(-1,0,0);
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float RegionHalfWidth=160;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> BaseMesh;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> MovingMesh;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> WarningMesh;
    UPROPERTY(BlueprintReadOnly) bool Active=false;
    UPROPERTY(BlueprintReadOnly) bool Warning=false;
    UPROPERTY(BlueprintReadOnly) float Clock=0;
    UFUNCTION(BlueprintCallable,CallInEditor) void ConfigureObstacle();
    UFUNCTION(BlueprintPure) bool IsSlipperyAt(FVector Position) const;
    UFUNCTION(BlueprintPure) bool IsCrossingSafe(float LookAheadSeconds=0) const;
    UFUNCTION(BlueprintPure) bool TouchesToolAt(FVector CapsuleCenter,float Radius,float HalfHeight) const;
    UFUNCTION(BlueprintCallable) void Evaluate(float Time);
protected:
    virtual void BeginPlay() override;
private:
    UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> WindStreaks;
    float RotorAngle=0;
    bool PlayerInGust=false;
    void HitPlayerAt(FVector Center,FVector HalfSize);
};
