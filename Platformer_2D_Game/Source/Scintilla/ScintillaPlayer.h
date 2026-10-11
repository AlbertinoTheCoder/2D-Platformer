#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "InputActionValue.h"
#include "ScintillaPlayer.generated.h"
class UScintillaHealth;
class UStaticMeshComponent;
class USoundBase;
class UAnimSequence;
class AScintillaCamera;

UENUM(BlueprintType)
enum class EScintillaState : uint8 { Idle, Run, Jump, Fall, Attack, Hurt, Death, Land };
UENUM(BlueprintType)
enum class EScintillaLookDirection : uint8 { Left, Right, Camera, City };

UCLASS()
class SCINTILLA_API AScintillaPlayer : public ACharacter
{
    GENERATED_BODY()
public:
    AScintillaPlayer();
    virtual void Tick(float DeltaSeconds) override;
    virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
    virtual void Landed(const FHitResult& Hit) override;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UScintillaHealth> Health;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Body;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMeshComponent> Eye;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Movement") float CoyoteSeconds = .12f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Movement") float JumpBufferSeconds = .12f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Movement") float RisingGravity = 1800.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Movement") float FallingMultiplier = 1.5f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Movement") float JumpReleaseMultiplier = .45f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat") float AttackCooldown = .3f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat") float AttackReach = 85.f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat") bool DebugAttack = false;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) EScintillaState AnimationState = EScintillaState::Idle;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) float Facing = 1.f;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) EScintillaLookDirection LookDirection = EScintillaLookDirection::Camera;
    UPROPERTY(EditDefaultsOnly, Category="Animation") TMap<EScintillaState, TObjectPtr<UAnimSequence>> AnimationClips;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Audio") TObjectPtr<USoundBase> JumpSound;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Audio") TObjectPtr<USoundBase> LandSound;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Audio") TObjectPtr<USoundBase> DamageSound;
    UFUNCTION(BlueprintCallable) void ReceiveHazard(FVector Origin);
    UFUNCTION(BlueprintCallable) void Respawn();
    UFUNCTION(BlueprintCallable) void Attack();
    UFUNCTION(BlueprintCallable) void Interact();
    UFUNCTION(BlueprintCallable) void PressJump();
    UFUNCTION(BlueprintCallable) void ReleaseJump();
    UFUNCTION(BlueprintCallable) void MoveAxis(float Axis);
    UFUNCTION(BlueprintCallable) void FaceCamera();
    UFUNCTION(BlueprintCallable) void FaceCity();
    UFUNCTION(BlueprintPure) bool ControlsAllowed() const;
    UFUNCTION(BlueprintImplementableEvent) void Feedback(FName Event);
protected:
    virtual void BeginPlay() override;
private:
    void MoveInput(const FInputActionValue& Value);
    void TryBufferedJump();
    UFUNCTION() void OnDamaged(FVector Origin);
    UFUNCTION() void OnDied();
    double LastGroundTime = -100;
    double JumpPressedTime = -100;
    double AttackUntil = -100;
    double NextAttackTime = -100;
    double HurtUntil = -100;
    double LandUntil = -100;
    double AttackPoseUntil = -100;
    EScintillaState PlayingState = EScintillaState::Death;
    float MoveValue = 0;
    float LandingSquash = 0;
    float WalkPhase = 0;
    bool JumpHeld = false;
    bool JumpConsumed = false;
    FTimerHandle RespawnTimer;
    TWeakObjectPtr<AScintillaCamera> Camera;
};

UCLASS()
class SCINTILLA_API AScintillaCamera : public AActor
{
    GENERATED_BODY()
public:
    AScintillaCamera();
    virtual void Tick(float DeltaSeconds) override;
    UPROPERTY(VisibleAnywhere) TObjectPtr<class UCameraComponent> CameraComponent;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float HorizontalSmoothing = 8;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float VerticalSmoothing = 4;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float LookAhead = 180;
    UPROPERTY(BlueprintReadWrite) TObjectPtr<AScintillaPlayer> Target;
    void SnapToTarget();
    void BeginCityReveal(FVector Center,float Width);
private:
    float CameraMaxX=7300.f;
    bool CityReveal=false;
    float RevealTime=0;
    float RevealStartWidth=1600;
    float RevealWidth=9000;
    FVector RevealStart;
    FVector RevealCenter;
};
