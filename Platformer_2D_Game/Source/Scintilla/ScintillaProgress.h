#pragma once
#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "ScintillaProgress.generated.h"

/** Campaign unlocks survive map travel and a fresh game session. Indices are zero based. */
UCLASS()
class SCINTILLA_API UScintillaProgress : public USaveGame
{
    GENERATED_BODY()
public:
    UPROPERTY(SaveGame) int32 HighestUnlocked = 0;
    UPROPERTY(SaveGame) int32 CompletedLevels = 0;
    UPROPERTY(SaveGame) int32 Difficulty = 0;
};
