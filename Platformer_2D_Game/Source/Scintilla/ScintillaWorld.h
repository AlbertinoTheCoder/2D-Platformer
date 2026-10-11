#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/GameStateBase.h"
#include "ScintillaWorld.generated.h"
class AScintillaPlayer;
class UStaticMeshComponent;
class UBoxComponent;
class USoundBase;

UCLASS()
class SCINTILLA_API AScintillaGameState : public AGameStateBase
{
    GENERATED_BODY()
public:
    AScintillaGameState();
    virtual void Tick(float DeltaSeconds) override;
    UPROPERTY(BlueprintReadOnly) int32 Energy = 0;
    UPROPERTY(BlueprintReadOnly) int32 TotalEnergy = 0;
    UPROPERTY(BlueprintReadOnly) bool Completed = false;
    UPROPERTY(BlueprintReadOnly) bool RestorationReady = false;
    UPROPERTY(BlueprintReadOnly) float RestorationElapsed = 0;
    UPROPERTY(BlueprintReadOnly) float RunSeconds = 0;
    UPROPERTY(BlueprintReadOnly) int32 DamageTaken = 0;
    UPROPERTY(BlueprintReadOnly) int32 Difficulty = 0;
    UPROPERTY(BlueprintReadOnly) int32 Deaths = 0;
    UFUNCTION(BlueprintPure) int32 AttemptLimit() const { return Difficulty==2 ? 3 : Difficulty==1 ? 5 : 8; }
    UPROPERTY(BlueprintReadOnly) bool RatingDismissed = false;
    UPROPERTY(BlueprintReadOnly) FString RatingGrade;
    UPROPERTY(BlueprintReadOnly) float RatingScore = 0;
    UPROPERTY(BlueprintReadOnly) float SpeedPoints = 0;
    UPROPERTY(BlueprintReadOnly) float DamagePoints = 0;
    UPROPERTY(BlueprintReadOnly) float EnergyPoints = 0;
    UPROPERTY(BlueprintReadOnly) float RatingTargetSeconds = 60;
    void CalculateRating();
    static constexpr float RestorationDuration = 7.5f;
    UPROPERTY(BlueprintReadOnly) bool HasCheckpoint = false;
    UPROPERTY(BlueprintReadOnly) FVector RespawnPosition = FVector(100,0,100);
    UPROPERTY(BlueprintReadOnly) TObjectPtr<class AScintillaCheckpoint> ActiveCheckpoint;
    UFUNCTION(BlueprintCallable) void CompleteLevel();
};

UCLASS()
class SCINTILLA_API AScintillaGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    AScintillaGameMode();
};

UCLASS()
class SCINTILLA_API AScintillaPlatform : public AActor
{
    GENERATED_BODY()
public:
    AScintillaPlatform();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Surface;
};

UCLASS()
class SCINTILLA_API AScintillaMovingPlatform : public AScintillaPlatform
{
    GENERATED_BODY()
public:
    AScintillaMovingPlatform();
    virtual void Tick(float DeltaSeconds) override;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FVector EndOffset = FVector(400,0,0);
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float Speed = 150;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float WaitSeconds = .5f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) bool Loop = true;
protected:
    virtual void BeginPlay() override;
private:
    FVector StartPosition;
    float WaitRemaining = 0;
    bool ToEnd = true;
    bool Finished = false;
};

UCLASS(Abstract)
class SCINTILLA_API AScintillaTrigger : public AActor
{
    GENERATED_BODY()
public:
    AScintillaTrigger();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UBoxComponent> Trigger;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Visual;
protected:
    virtual void BeginPlay() override;
    virtual void Touch(AScintillaPlayer* Player) {}
    UFUNCTION() void OnOverlap(UPrimitiveComponent* Comp, AActor* Other, UPrimitiveComponent* OtherComp, int32 BodyIndex, bool Sweep, const FHitResult& Result);
};

UCLASS()
class SCINTILLA_API AScintillaCoin : public AScintillaTrigger
{
    GENERATED_BODY()
public:
    AScintillaCoin();
    UPROPERTY(EditAnywhere, Category="Audio") TObjectPtr<USoundBase> CollectSound;
protected:
    virtual void BeginPlay() override;
    virtual void Touch(AScintillaPlayer* Player) override;
private:
    bool Collected = false;
};

UCLASS()
class SCINTILLA_API AScintillaHazard : public AScintillaTrigger
{
    GENERATED_BODY()
public:
    AScintillaHazard();
    UPROPERTY(EditAnywhere, BlueprintReadWrite) bool InstantKill = false;
protected:
    virtual void BeginPlay() override;
    virtual void Touch(AScintillaPlayer* Player) override;
private:
    void CheckContacts();
    FTimerHandle ContactTimer;
};

UCLASS()
class SCINTILLA_API AScintillaCheckpoint : public AScintillaTrigger
{
    GENERATED_BODY()
public:
    AScintillaCheckpoint();
    UPROPERTY(BlueprintReadOnly) bool Active = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FVector RespawnOffset = FVector(0,0,50);
    UPROPERTY(EditAnywhere, Category="Audio") TObjectPtr<USoundBase> ActivateSound;
    void SetActive(bool Value);
protected:
    virtual void Touch(AScintillaPlayer* Player) override;
};

UCLASS()
class SCINTILLA_API AScintillaGoal : public AScintillaTrigger
{
    GENERATED_BODY()
public:
    AScintillaGoal();
    UPROPERTY(EditAnywhere, Category="Audio") TObjectPtr<USoundBase> CompleteSound;
    UFUNCTION(BlueprintCallable) void Activate(AScintillaPlayer* Player);
protected:
    virtual void Touch(AScintillaPlayer* Player) override;
};

UENUM(BlueprintType)
enum class EScintillaEnemyType : uint8 { Scout, Charger, Sentinel, Flyer, SurveyFlyer };
UENUM(BlueprintType)
enum class EScintillaEnemyPhase : uint8 { Patrol, Windup, Dashing, Recovery };
UCLASS()
class SCINTILLA_API AScintillaEnemy : public AActor
{
    GENERATED_BODY()
public:
    AScintillaEnemy();
    virtual void Tick(float DeltaSeconds) override;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UBoxComponent> Collision;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Visual;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UBoxComponent> Contact;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> MotionPart;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> MotionPartRight;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) EScintillaEnemyType EnemyType = EScintillaEnemyType::Scout;
    UPROPERTY(BlueprintReadOnly) EScintillaEnemyPhase Phase = EScintillaEnemyPhase::Patrol;
    UPROPERTY(BlueprintReadOnly) int32 Armor = 1;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float PatrolMinX = 2530;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float PatrolMaxX = 3050;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float Speed = 90;
    UPROPERTY(BlueprintReadOnly) bool Defeated = false;
    UPROPERTY(EditAnywhere, Category="Audio") TObjectPtr<USoundBase> DeathSound;
    UFUNCTION(BlueprintCallable) void Defeat();
    UFUNCTION(BlueprintCallable) void TakeStrike();
    UFUNCTION(BlueprintCallable, CallInEditor) void ConfigureEnemy();
protected:
    virtual void BeginPlay() override;
private:
    UFUNCTION() void ContactPlayer(UPrimitiveComponent* Comp, AActor* Other, UPrimitiveComponent* OtherComp, int32 BodyIndex, bool Sweep, const FHitResult& Result);
    void CheckContact();
    float Direction = 1;
    float FlightHeight = 0;
    float PhaseRemaining = 0;
    float AnimationTime = 0;
    float PartAngle = 0;
    double NextHitTime = -100;
    UPROPERTY() TObjectPtr<class UMaterialInstanceDynamic> CoreMaterial;
    FTimerHandle ContactTimer;
};

UCLASS()
class SCINTILLA_API AScintillaCity : public AActor
{
    GENERATED_BODY()
public:
    AScintillaCity();
    UFUNCTION(BlueprintCallable, CallInEditor) void BuildCity();
    UFUNCTION(BlueprintCallable, CallInEditor) void GroundCity();
    UFUNCTION(BlueprintPure) float GroundHeightAt(float X) const;
    UPROPERTY(BlueprintReadOnly) TArray<FVector2D> GroundProfile;
    UFUNCTION(BlueprintCallable) void RestorePower();
    UPROPERTY(EditAnywhere, BlueprintReadWrite) TObjectPtr<class UMaterialInterface> ColorMaterial;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) bool Powered = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float CityLength = 8000;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FLinearColor DistrictTint = FLinearColor(.28f,.48f,.54f);
    UPROPERTY(BlueprintReadOnly) float PowerBlend = 0;
protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
private:
    UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> Windows;
    UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> Buildings;
    void AddBlock(FName Name, FVector Location, FVector Size, FLinearColor Color, bool Window);
    void ApplyColors(float Amount);
    struct FRepairPiece
    {
        UStaticMeshComponent* Mesh=nullptr;
        FTransform Intact;
        FTransform Broken;
        TArray<FLinearColor> Colors;
        bool Decay=false;
        bool Foliage=false;
        float Delay=0;
    };
    TArray<FRepairPiece> RepairPieces;
    float RepairTime=0;
    void AddModel(const FString& Name,const FString& Asset,FVector Location,FVector Scale);
    float FoundationHeight(float X,float HalfWidth) const;
};
