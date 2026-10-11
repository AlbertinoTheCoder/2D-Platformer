#include "ScintillaHealth.h"
#include "Engine/World.h"
#include "ScintillaWorld.h"
UScintillaHealth::UScintillaHealth() { PrimaryComponentTick.bCanEverTick = false; }
void UScintillaHealth::BeginPlay() { Super::BeginPlay(); ResetHealth(); }
bool UScintillaHealth::ApplyHit(int32 Amount, FVector Origin)
{
    if (Amount <= 0 || IsDead() || !GetWorld() || GetWorld()->GetTimeSeconds() < InvulnerableUntil) return false;
    if(auto* GS=GetWorld()->GetGameState<AScintillaGameState>()) if(!GS->Completed) GS->DamageTaken+=FMath::Min(CurrentHealth,Amount);
    CurrentHealth = FMath::Max(0, CurrentHealth - Amount);
    InvulnerableUntil = GetWorld()->GetTimeSeconds() + InvulnerabilitySeconds;
    HealthChanged.Broadcast(CurrentHealth, MaxHealth);
    Damaged.Broadcast(Origin);
    if (IsDead()) Died.Broadcast();
    return true;
}
void UScintillaHealth::Kill()
{
    if (IsDead()) return;
    if(GetWorld()) if(auto* GS=GetWorld()->GetGameState<AScintillaGameState>()) if(!GS->Completed) GS->DamageTaken+=CurrentHealth;
    CurrentHealth = 0;
    HealthChanged.Broadcast(0, MaxHealth);
    Died.Broadcast();
}
void UScintillaHealth::ResetHealth()
{
    CurrentHealth = FMath::Max(1, MaxHealth);
    InvulnerableUntil = GetWorld() ? GetWorld()->GetTimeSeconds() + .5f : -1;
    HealthChanged.Broadcast(CurrentHealth, MaxHealth);
}
