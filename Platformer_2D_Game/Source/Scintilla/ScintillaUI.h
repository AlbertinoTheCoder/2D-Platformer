#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "GameFramework/PlayerController.h"
#include "ScintillaUI.generated.h"
class UInputAction;
class UInputMappingContext;
class UTextBlock;
class UVerticalBox;
class UButton;
class UUniformGridPanel;
class UScintillaProgress;
class UBorder;
class UProgressBar;

UCLASS()
class SCINTILLA_API UScintillaHUD : public UUserWidget
{
    GENERATED_BODY()
public:
    void Refresh();
    void ShowPause(bool Value);
    void FocusRestart();
    bool IsLevelChoiceEnabled(int32 Index) const;
    UFUNCTION(BlueprintCallable) void OpenLevelChooser();
    UFUNCTION(BlueprintCallable) void OpenDifficultyChooser();
    bool IsDifficultyChooserOpen() const { return PausedMenu && DifficultyChoosing; }
    bool IsPauseLevelChooserOpen() const { return PausedMenu && PauseChoosing; }
    bool IsRatingVisible() const;
protected:
    virtual TSharedRef<SWidget> RebuildWidget() override;
    virtual void NativeConstruct() override;
    virtual void NativeTick(const FGeometry& Geometry, float DeltaSeconds) override;
    virtual FReply NativeOnKeyDown(const FGeometry& Geometry, const FKeyEvent& Event) override;
private:
    UPROPERTY() TObjectPtr<UTextBlock> HealthLabel;
    UPROPERTY() TObjectPtr<UTextBlock> EnergyLabel;
    UPROPERTY() TObjectPtr<UTextBlock> CheckpointLabel;
    UPROPERTY() TObjectPtr<UTextBlock> AttemptsLabel;
    UPROPERTY() TObjectPtr<UTextBlock> Message;
    UPROPERTY() TObjectPtr<UTextBlock> CinematicCaption;
    UPROPERTY() TObjectPtr<UBorder> MenuBackdrop;
    UPROPERTY() TObjectPtr<UBorder> MenuPanel;
    UPROPERTY() TObjectPtr<UProgressBar> EnergyMeter;
    UPROPERTY() TArray<TObjectPtr<UBorder>> HealthCells;
    UPROPERTY() TObjectPtr<UVerticalBox> Menu;
    UPROPERTY() TObjectPtr<UButton> ResumeButton;
    UPROPERTY() TObjectPtr<UButton> ChooseLevelButton;
    UPROPERTY() TObjectPtr<UButton> DifficultyButton;
    UPROPERTY() TObjectPtr<UButton> NormalButton;
    UPROPERTY() TObjectPtr<UButton> HardButton;
    UPROPERTY() TObjectPtr<UButton> HardcoreButton;
    UPROPERTY() TObjectPtr<UButton> RestartButton;
    UPROPERTY() TObjectPtr<UButton> QuitButton;
    UPROPERTY() TObjectPtr<UUniformGridPanel> LevelChooser;
    UPROPERTY() TObjectPtr<UVerticalBox> RatingPanel;
    UPROPERTY() TObjectPtr<UTextBlock> RatingLetter;
    UPROPERTY() TObjectPtr<UTextBlock> RatingTotal;
    UPROPERTY() TObjectPtr<UTextBlock> RatingDetails;
    UPROPERTY() TObjectPtr<UButton> ContinueButton;
    UPROPERTY() TArray<TObjectPtr<UButton>> LevelButtons;
    UPROPERTY() TArray<TObjectPtr<UTextBlock>> LevelCaptions;
    UButton* AddButton(const FString& Text);
    UFUNCTION() void Resume();
    UFUNCTION() void Restart();
    UFUNCTION() void Quit();
    UFUNCTION() void ContinueRating();
    UFUNCTION() void ChangeDifficulty();
    UFUNCTION() void ChooseNormal();
    UFUNCTION() void ChooseHard();
    UFUNCTION() void ChooseHardcore();
    UFUNCTION() void ChooseOfficina();
    UFUNCTION() void ChooseFonderia();
    UFUNCTION() void ChooseCondotte();
    UFUNCTION() void ChooseTorre();
    UFUNCTION() void ChooseCryo();
    UFUNCTION() void ChooseScrap();
    UFUNCTION() void ChooseSolar();
    UFUNCTION() void ChooseBio();
    bool PausedMenu = false;
    bool PauseChoosing = false;
    bool DifficultyChoosing = false;
};

UCLASS()
class SCINTILLA_API AScintillaController : public APlayerController
{
    GENERATED_BODY()
public:
    AScintillaController();
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TObjectPtr<UInputAction> MoveAction;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TObjectPtr<UInputAction> JumpAction;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TObjectPtr<UInputAction> AttackAction;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TObjectPtr<UInputAction> InteractAction;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TObjectPtr<UInputAction> PauseAction;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TObjectPtr<UInputMappingContext> MappingContext;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TSubclassOf<UScintillaHUD> HUDClass;
    UPROPERTY(BlueprintReadOnly) TObjectPtr<UScintillaHUD> HUD;
    UFUNCTION(BlueprintCallable) void TogglePause();
    UFUNCTION(BlueprintCallable) void ResumeGame();
    UFUNCTION(BlueprintCallable) void RestartPrototype();
    UFUNCTION(BlueprintCallable) void QuitGame();
    UFUNCTION(BlueprintCallable) void ShowCompletion();
    UFUNCTION(BlueprintCallable) void ContinueFromRating();
    UFUNCTION(BlueprintCallable) void RefreshHUD();
    UFUNCTION(BlueprintPure) bool IsLevelUnlocked(int32 Index) const;
    UFUNCTION(BlueprintPure) bool IsLevelCompleted(int32 Index) const;
    UFUNCTION(BlueprintPure) int32 GetHighestUnlockedLevel() const;
    UFUNCTION(BlueprintCallable) bool SelectLevel(int32 Index);
    UFUNCTION(BlueprintCallable) void SetDifficulty(int32 Value);
protected:
    virtual void BeginPlay() override;
    virtual void SetupInputComponent() override;
private:
    void LoadInputAssets();
    void LoadProgress();
    FString ProgressSlot() const;
    UPROPERTY() TObjectPtr<UScintillaProgress> Progress;
    bool CompletionSaved=false;
};
