#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "ScintillaHealth.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FScintillaHealthChanged, int32, Current, int32, Maximum);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FScintillaDamaged, FVector, Origin);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FScintillaDied);

UCLASS(ClassGroup=(Scintilla), meta=(BlueprintSpawnableComponent))
class SCINTILLA_API UScintillaHealth : public UActorComponent
{
    GENERATED_BODY()
public:
    UScintillaHealth();
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Health") int32 MaxHealth = 3;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Health") float InvulnerabilitySeconds = 1.f;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Health") int32 CurrentHealth = 3;
    UPROPERTY(BlueprintAssignable) FScintillaHealthChanged HealthChanged;
    UPROPERTY(BlueprintAssignable) FScintillaDamaged Damaged;
    UPROPERTY(BlueprintAssignable) FScintillaDied Died;
    UFUNCTION(BlueprintCallable) bool ApplyHit(int32 Amount, FVector Origin);
    UFUNCTION(BlueprintCallable) void Kill();
    UFUNCTION(BlueprintCallable) void ResetHealth();
    UFUNCTION(BlueprintPure) bool IsDead() const { return CurrentHealth <= 0; }
protected:
    virtual void BeginPlay() override;
private:
    double InvulnerableUntil = -1;
};
