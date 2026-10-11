#include "ScintillaPlaytest.h"
#include "ScintillaPlayer.h"
#include "ScintillaHealth.h"
#include "ScintillaWorld.h"
#include "ScintillaUI.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/PlatformMisc.h"
#include "EngineUtils.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Components/StaticMeshComponent.h"
#include "Camera/CameraComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Animation/AnimSequence.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "ScintillaCampaign.h"
#include "Misc/PackageName.h"
#include "InputKeyEventArgs.h"
#include "InputMappingContext.h"
#include "ScintillaProgress.h"
#include "ScintillaObstacles.h"

AScintillaPlaytest::AScintillaPlaytest() { PrimaryActorTick.bCanEverTick=true; PrimaryActorTick.bTickEvenWhenPaused=true; }
void AScintillaPlaytest::Check(const FString& Name,bool Passed)
{
    Checks.Add(FString::Printf(TEXT("{\"name\":\"%s\",\"passed\":%s}"),*Name,Passed ? TEXT("true") : TEXT("false")));
    if (!Passed) ++Failures;
    UE_LOG(LogTemp,Display,TEXT("SCINTILLA_TEST %s: %s"),*Name,Passed ? TEXT("PASS") : TEXT("FAIL"));
}
void AScintillaPlaytest::Advance() { ++Stage; Elapsed=0; Released=false; }
void AScintillaPlaytest::Place(FVector Position)
{
    Player->MoveAxis(0); Player->SetBase(static_cast<FMovementBaseInterfaceData*>(nullptr));
    Player->SetActorLocation(Position,false,nullptr,ETeleportType::TeleportPhysics);
    Player->GetCharacterMovement()->StopMovementImmediately();
    Player->GetCharacterMovement()->SetMovementMode(MOVE_Falling);
}
void AScintillaPlaytest::Tick(float Dt)
{
    Super::Tick(Dt); Elapsed+=Dt;
    if (!Player) Player=Cast<AScintillaPlayer>(UGameplayStatics::GetPlayerPawn(this,0));
    if (!Player) return;
    RouteMode=FParse::Param(FCommandLine::Get(),TEXT("ScintillaRoute"));
    if (RouteMode) { TickRoute(Dt); return; }
    auto* GS=GetWorld()->GetGameState<AScintillaGameState>();
    auto* PC=Cast<AScintillaController>(Player->GetController());
    if(FParse::Param(FCommandLine::Get(),TEXT("ScintillaDifficultySmoke")))
    {
        const FString Pending=FPaths::ProjectSavedDir()/FString::Printf(TEXT("DifficultyPending%d.txt"),ScintillaCampaign::Index(this));
        FString Phase; FFileHelper::LoadFileToString(Phase,*Pending);
        if(Stage==0 && Elapsed>.7f && !Phase.IsEmpty())
        {
            if(Phase==TEXT("hard"))
            {
                Check(TEXT("hard_setting_persists_across_travel"),GS->Difficulty==1 && GS->AttemptLimit()==5);
                FFileHelper::SaveStringToFile(FString::Printf(TEXT("{\"failures\":%d,\"checks\":[%s]}"),Failures,*FString::Join(Checks,TEXT(","))),*(FPaths::ProjectSavedDir()/TEXT("ScintillaDifficultyHard.json")));
                FFileHelper::SaveStringToFile(TEXT("hardcore"),*Pending); PC->TogglePause(); PC->SetDifficulty(2); return;
            }
            if(Phase==TEXT("hardcore"))
            {
                Check(TEXT("hardcore_setting_persists_across_travel"),GS->Difficulty==2 && GS->AttemptLimit()==3);
                GS->Deaths=2; GS->Energy=5; GS->HasCheckpoint=true; GS->RespawnPosition=FVector(1200,0,200);
                Player->Health->Kill(); Check(TEXT("fatal_hit_consumes_last_attempt"),GS->Deaths==3);
                FFileHelper::SaveStringToFile(FString::Printf(TEXT("{\"failures\":%d,\"checks\":[%s]}"),Failures,*FString::Join(Checks,TEXT(","))),*(FPaths::ProjectSavedDir()/TEXT("ScintillaDifficultyHardcore.json")));
                FFileHelper::SaveStringToFile(TEXT("reset"),*Pending); Advance(); return;
            }
            if(Phase==TEXT("reset"))
            {
                Check(TEXT("attempt_reset_clears_checkpoint_energy_and_deaths"),GS->Deaths==0 && GS->Energy==0 && !GS->HasCheckpoint);
                Check(TEXT("attempt_reset_keeps_difficulty_and_unlocks"),GS->Difficulty==2 && PC->GetHighestUnlockedLevel()==0);
                Check(TEXT("attempt_reset_returns_to_start"),Player->GetActorLocation().X<200);
                Finish(TEXT("ScintillaDifficultyReset.json")); return;
            }
        }
        if(!Phase.IsEmpty()) return;
        if(Stage==0)
        {
            if(Elapsed<.7f) return;
            Check(TEXT("normal_has_eight_attempts"),GS->Difficulty==0 && GS->AttemptLimit()==8);
            PC->TogglePause(); PC->HUD->OpenDifficultyChooser(); Check(TEXT("difficulty_chooser_opens_from_pause"),PC->HUD->IsDifficultyChooserOpen());
            PC->HUD->OpenLevelChooser(); Check(TEXT("difficulty_chooser_back_returns_to_pause"),!PC->HUD->IsDifficultyChooserOpen()); PC->ResumeGame();
            int32 Count=0; TSet<EScintillaObstacleType> Types;
            bool DownWind=false,BackWind=false;
            for(TActorIterator<AScintillaObstacle> It(GetWorld());It;++It)
            {
                ++Count; Types.Add(It->ObstacleType); It->SetActorTickEnabled(false);
                Check(TEXT("obstacle_has_blender_mesh"),It->BaseMesh->GetStaticMesh()!=nullptr);
                if(It->ObstacleType==EScintillaObstacleType::Wind)
                { DownWind|=It->WindDirection.Z<-.5f; BackWind|=It->WindDirection.X<-.5f; }
                if(It->ObstacleType!=EScintillaObstacleType::Ice)
                {
                    It->Evaluate(It->ObstacleType==EScintillaObstacleType::FallingSpikes ? .5f : 1.5f);
                    Check(TEXT("hazard_warns_before_activation"),It->Warning && !It->Active);
                    It->Evaluate(It->ObstacleType==EScintillaObstacleType::FallingSpikes ? 1.6f : 3.f);
                    Check(TEXT("hazard_activates_after_warning"),It->Active);
                    It->Evaluate(4.5f); Check(TEXT("hazard_has_safe_recovery_window"),!It->Active && !It->Warning);
                }
            }
            Check(TEXT("all_six_obstacle_types_are_in_level"),Count==7 && Types.Num()==6);
            Check(TEXT("both_downward_and_backward_gusts_exist"),DownWind && BackWind);
            for(TActorIterator<AScintillaEnemy> It(GetWorld());It;++It)
                if(It->EnemyType==EScintillaEnemyType::Flyer) { EnemyProbe=*It; StartX=It->GetActorLocation().X; FullJumpPeak=It->GetActorLocation().Z; break; }
            Check(TEXT("aerial_enemy_exists"),EnemyProbe!=nullptr);
            for(TActorIterator<AScintillaObstacle> It(GetWorld());It;++It)
                if(It->ObstacleType==EScintillaObstacleType::Wind && It->WindDirection.X<-.5f)
                { Place(It->GetActorLocation()+FVector(0,0,100)); It->Clock=2.3f; It->Tick(.1f); break; }
            Advance(); return;
        }
        if(Stage==1 && Elapsed>.15f)
        {
            Check(TEXT("gust_physically_pushes_player_backward"),Player->GetVelocity().X<-.1f);
            Check(TEXT("flyer_patrols_without_ground_and_bobs"),EnemyProbe && FMath::Abs(EnemyProbe->GetActorLocation().X-StartX)>5 && FMath::Abs(EnemyProbe->GetActorLocation().Z-FullJumpPeak)>1);
            for(TActorIterator<AScintillaObstacle> It(GetWorld());It;++It) if(It->ObstacleType==EScintillaObstacleType::Ice)
            { Place(It->GetActorLocation()+FVector(0,0,46)); Player->GetCharacterMovement()->Velocity.X=400; break; }
            Advance(); return;
        }
        if(Stage==2 && Elapsed>.25f)
        {
            Check(TEXT("ice_reduces_friction_and_preserves_momentum"),Player->GetCharacterMovement()->GroundFriction<.3f && Player->GetVelocity().X>150);
            for(TActorIterator<AScintillaObstacle> It(GetWorld());It;++It) if(It->ObstacleType==EScintillaObstacleType::FallingSpikes)
            { Place(It->GetActorLocation()+FVector(0,0,45)); const int32 H=Player->Health->CurrentHealth; It->Evaluate(1.6f); Check(TEXT("falling_spike_causes_damage"),Player->Health->CurrentHealth==H-1); break; }
            Player->Health->ResetHealth(); Place(FVector(100,0,100)); Advance(); return;
        }
        if(Stage==3 && Elapsed>1.1f)
        {
            Check(TEXT("leaving_ice_restores_normal_braking"),Player->GetCharacterMovement()->GroundFriction==8 && Player->GetCharacterMovement()->BrakingDecelerationWalking==5000);
            for(TActorIterator<AScintillaObstacle> It(GetWorld());It;++It) if(It->ObstacleType==EScintillaObstacleType::RisingSpikes)
            { Place(It->GetActorLocation()+FVector(0,0,45)); const int32 H=Player->Health->CurrentHealth; It->Evaluate(2.8f); Check(TEXT("rising_spike_causes_damage"),Player->Health->CurrentHealth==H-1); break; }
            Player->Health->ResetHealth(); Place(FVector(100,0,100)); Advance(); return;
        }
        if(Stage==4 && Elapsed>1.1f)
        {
            for(TActorIterator<AScintillaObstacle> It(GetWorld());It;++It) if(It->ObstacleType==EScintillaObstacleType::Hammer)
            { Place(It->GetActorLocation()+FVector(0,0,45)); const int32 H=Player->Health->CurrentHealth; It->Evaluate(3.f); Check(TEXT("rotating_hammer_causes_damage"),Player->Health->CurrentHealth==H-1); break; }
            Player->Health->ResetHealth(); Place(FVector(100,0,100)); Advance(); return;
        }
        if(Stage==5 && Elapsed>.7f)
        {
            for(TActorIterator<AScintillaObstacle> It(GetWorld());It;++It) if(It->ObstacleType==EScintillaObstacleType::Axe)
            { Place(It->GetActorLocation()+FVector(-40,0,45)); const int32 H=Player->Health->CurrentHealth; It->Evaluate(3.f); Check(TEXT("rotating_axe_causes_damage"),Player->Health->CurrentHealth==H-1); break; }
            Player->Health->ResetHealth();
            if(EnemyProbe) { Place(EnemyProbe->GetActorLocation()-FVector(30,0,0)); Player->MoveAxis(1); Player->Attack(); Check(TEXT("aerial_enemy_can_be_defeated_by_discharge"),EnemyProbe->Defeated); }
            Place(FVector(100,0,100));
            for(TActorIterator<AScintillaGoal> It(GetWorld());It;++It) Check(TEXT("generator_moved_beyond_old_route"),It->GetActorLocation().X>12000);
            // Preserve the mechanism report before map travel recreates this probe.
            const FString R=FString::Printf(TEXT("{\"failures\":%d,\"checks\":[%s]}"),Failures,*FString::Join(Checks,TEXT(",")));
            FFileHelper::SaveStringToFile(R,*(FPaths::ProjectSavedDir()/TEXT("ScintillaDifficulty.json")));
            FFileHelper::SaveStringToFile(TEXT("hard"),*Pending); PC->TogglePause(); PC->SetDifficulty(1); return;
        }
        return;
    }
    if(FParse::Param(FCommandLine::Get(),TEXT("ScintillaRatingSmoke")))
    {
        if(Stage==0)
        {
            if(Elapsed<.7f) return;
            Check(TEXT("run_clock_counts_active_play"),GS->RunSeconds>.5f);
            StartX=GS->RunSeconds; PC->TogglePause(); RouteStep=0; Advance(); return;
        }
        if(Stage==1)
        {
            if(++RouteStep<60) return;
            Check(TEXT("pause_time_excluded_from_rating"),FMath::Abs(GS->RunSeconds-StartX)<.01f);
            PC->ResumeGame(); Advance(); return;
        }
        if(Stage==2)
        {
            if(Elapsed<.1f) return;
            Check(TEXT("accepted_damage_is_recorded"),Player->Health->ApplyHit(1,Player->GetActorLocation()-FVector(100,0,0)) && GS->DamageTaken==1);
            Check(TEXT("invulnerable_hits_do_not_count"),!Player->Health->ApplyHit(1,Player->GetActorLocation()) && GS->DamageTaken==1);
            Player->Health->Kill();
            Check(TEXT("fatal_damage_records_remaining_health"),GS->DamageTaken==3);
            Player->Health->ResetHealth(); Check(TEXT("respawn_health_reset_keeps_damage_total"),GS->DamageTaken==3);
            auto Rate=[&](float Time,int32 Damage,int32 Energy) { GS->RunSeconds=Time; GS->DamageTaken=Damage; GS->Energy=Energy; GS->CalculateRating(); return GS->RatingScore; };
            GS->TotalEnergy=10;
            Rate(60,0,10); Check(TEXT("perfect_run_receives_S"),GS->RatingGrade==TEXT("S") && GS->RatingScore==100);
            Rate(60,2,10); Check(TEXT("strong_run_receives_A"),GS->RatingGrade==TEXT("A") && GS->RatingScore==88);
            Rate(60,0,0); Check(TEXT("low_collection_receives_B"),GS->RatingGrade==TEXT("B"));
            Rate(ScintillaCampaign::RatingTargets[0]*1.5f,0,0); Check(TEXT("slower_run_receives_C"),GS->RatingGrade==TEXT("C"));
            Rate(ScintillaCampaign::RatingTargets[0]*2,5,0); Check(TEXT("rough_run_receives_D"),GS->RatingGrade==TEXT("D") && GS->RatingScore==0);
            const float Base=Rate(60,0,5);
            Check(TEXT("slower_speed_reduces_rating"),Rate(ScintillaCampaign::RatingTargets[0]*1.5f,0,5)<Base);
            Check(TEXT("more_damage_reduces_rating"),Rate(60,1,5)<Base);
            Check(TEXT("more_energy_improves_rating"),Rate(60,0,10)>Base);
            Rate(60,1,8); GS->CompleteLevel(); StartX=GS->RunSeconds; Advance(); return;
        }
        if(Stage==3)
        {
            if(Elapsed<.5f) return;
            PC->ContinueFromRating();
            Check(TEXT("cannot_continue_during_city_animation"),!GS->RatingDismissed && !PC->SelectLevel(0));
            Check(TEXT("completion_time_freezes_before_cinematic"),FMath::Abs(GS->RunSeconds-StartX)<.01f);
            Advance(); return;
        }
        if(Stage==4)
        {
            if(!GS->RestorationReady) return;
            Check(TEXT("rating_popup_precedes_map_selection"),PC->HUD->IsRatingVisible() && GS->RatingGrade==TEXT("A") && !GS->RatingDismissed && !PC->SelectLevel(0));
            PC->ContinueFromRating();
            Check(TEXT("continue_opens_unlocked_map_chooser"),GS->RatingDismissed && !PC->HUD->IsRatingVisible() && PC->HUD->IsLevelChoiceEnabled(0) && PC->HUD->IsLevelChoiceEnabled(1));
            Check(TEXT("continue_does_not_unlock_extra_levels"),PC->GetHighestUnlockedLevel()==1 && !PC->SelectLevel(2));
            PC->ContinueFromRating(); PC->ShowCompletion();
            Check(TEXT("repeated_continue_preserves_result"),GS->RatingGrade==TEXT("A") && GS->RatingScore==88 && !PC->HUD->IsRatingVisible());
            Finish(TEXT("ScintillaRating.json")); Stage=5; return;
        }
        return;
    }
    if(FParse::Param(FCommandLine::Get(),TEXT("ScintillaPauseSmoke")))
    {
        int32 Start=1; FParse::Value(FCommandLine::Get(),TEXT("ScintillaStartLevel="),Start);
        const FString Pending=FPaths::ProjectSavedDir()/FString::Printf(TEXT("PausePending%d.txt"),Start);
        auto Key=[PC](EInputEvent Event) { PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::U,Event,Event==IE_Pressed ? 1.f : 0.f)); };
        if(Stage==0)
        {
            if(Elapsed<.7f) return;
            FString Previous;
            if(FFileHelper::LoadFileToString(Previous,*Pending))
            {
                int32 Split=0; if(Previous.FindChar('\n',Split)) { Failures=FCString::Atoi(*Previous.Left(Split)); Checks.Add(Previous.Mid(Split+1)); }
                Check(TEXT("pause_selection_loads_requested_map"),ScintillaCampaign::Index(this)==0);
                Check(TEXT("selected_map_starts_unpaused_and_playable"),!PC->IsPaused() && Player->ControlsAllowed() && Player->Health->CurrentHealth==3 && GS && !GS->Completed && GS->Energy==0);
                Check(TEXT("pause_travel_preserves_unlocks"),PC->GetHighestUnlockedLevel()==Start-1);
                Finish(TEXT("ScintillaPause.json")); Stage=20; return;
            }
            bool HasU=false,HasEsc=false;
            for(const auto& Mapping:PC->MappingContext->GetMappings()) if(Mapping.Action==PC->PauseAction) { HasU|=Mapping.Key==EKeys::U; HasEsc|=Mapping.Key==EKeys::Escape; }
            Check(TEXT("pause_mapping_uses_U_and_not_escape"),HasU && !HasEsc);
            Check(TEXT("cannot_travel_from_active_game"),!PC->SelectLevel(0));
            Key(IE_Pressed); RouteStep=0; Advance(); return;
        }
        if(Stage==1)
        {
            if(++RouteStep<3) return;
            Check(TEXT("U_input_pauses_game"),PC->IsPaused()); Key(IE_Released);
            Check(TEXT("ordinary_pause_requires_opening_selector"),!PC->SelectLevel(0));
            PC->HUD->OpenLevelChooser();
            Check(TEXT("pause_selector_opens_without_winning"),PC->HUD->IsPauseLevelChooserOpen() && GS && !GS->Completed && PC->IsPaused());
            for(int32 Index=0;Index<8;++Index) Check(FString::Printf(TEXT("pause_level_%d_matches_unlocks"),Index+1),PC->HUD->IsLevelChoiceEnabled(Index)==(Index<Start));
            Check(TEXT("pause_selector_rejects_locked_and_invalid_maps"),!PC->SelectLevel(Start) && !PC->SelectLevel(-1) && !PC->SelectLevel(8));
            Check(TEXT("opening_selector_does_not_grant_unlocks"),PC->GetHighestUnlockedLevel()==Start-1 && !PC->IsLevelCompleted(Start-1));
            PC->HUD->OpenLevelChooser();
            Check(TEXT("back_returns_to_pause_without_resuming"),!PC->HUD->IsPauseLevelChooserOpen() && PC->IsPaused());
            RouteStep=0; Advance(); return;
        }
        if(Stage==2)
        {
            if(++RouteStep<3) return;
            Key(IE_Pressed); RouteStep=0; Advance(); return;
        }
        if(Stage==3)
        {
            if(++RouteStep<3) return;
            Check(TEXT("second_U_input_resumes_game"),!PC->IsPaused() && Player->ControlsAllowed()); Key(IE_Released);
            PC->TogglePause(); PC->HUD->OpenLevelChooser();
            FFileHelper::SaveStringToFile(FString::Printf(TEXT("%d\n%s"),Failures,*FString::Join(Checks,TEXT(","))),*Pending);
            if(!PC->SelectLevel(0)) { Check(TEXT("pause_accepts_unlocked_selection"),false); Finish(TEXT("ScintillaPause.json")); Stage=20; }
            return;
        }
        return;
    }
    if(FParse::Param(FCommandLine::Get(),TEXT("ScintillaRestorationSmoke")))
    {
        AScintillaCity* City=nullptr;
        for(TActorIterator<AScintillaCity> It(GetWorld());It;++It) { City=*It; break; }
        AScintillaCamera* Cam=nullptr;
        for(TActorIterator<AScintillaCamera> It(GetWorld());It;++It) { Cam=*It; break; }
        if(!City || !Cam || !GS || !PC) { Check(TEXT("restoration_actors_exist"),false); Finish(TEXT("ScintillaRestoration.json")); return; }
        TArray<UStaticMeshComponent*> Pieces; City->GetComponents(Pieces);
        auto Grounded=[&]()
        {
            bool Good=City->GroundProfile.Num()>=2; int32 Facades=0,Trees=0;
            for(auto* Piece:Pieces)
            {
                const FString Name=Piece->GetName(); const FVector Position=Piece->GetRelativeLocation();
                if(Name.StartsWith(TEXT("Facade")))
                {
                    ++Facades;
                    const float Half=Piece->GetStaticMesh()->GetBoundingBox().GetExtent().X*Piece->GetRelativeScale3D().X;
                    float Height=FMath::Min(City->GroundHeightAt(Position.X-Half),City->GroundHeightAt(Position.X+Half));
                    for(const auto& Point:City->GroundProfile) if(Point.X>Position.X-Half && Point.X<Position.X+Half) Height=FMath::Min(Height,static_cast<float>(Point.Y));
                    Good&=Position.Z<=Height+1 && Position.Z>=Height-25;
                }
                if(Name.StartsWith(TEXT("Tree")))
                {
                    ++Trees;
                    const float Bottom=Position.Z+Piece->GetStaticMesh()->GetBoundingBox().Min.Z*Piece->GetRelativeScale3D().Z;
                    Good&=FMath::Abs(Bottom-City->GroundHeightAt(Position.X)+6)<1;
                    for(auto* Leaf:Pieces) if(Leaf->GetName()==TEXT("Foliage")+Name.Mid(4)) Good&=Leaf->GetRelativeLocation().Equals(Position,.1f);
                }
            }
            return Good && Facades==24 && Trees==12;
        };
        UStaticMeshComponent* Roof=nullptr;
        for(auto* Piece:Pieces) if(Piece->GetName()==TEXT("Roof0")) Roof=Piece;
        if(Stage==0)
        {
            if(Elapsed<.7f) return;
            Check(TEXT("city_has_blender_facades_and_decay"),Pieces.Num()>=100 && Roof && Roof->GetStaticMesh() && Roof->GetStaticMesh()->GetName()==TEXT("SM_CityRoof"));
            Check(TEXT("roofs_start_collapsed"),Roof && FMath::Abs(Roof->GetRelativeRotation().Pitch)>10);
            Check(TEXT("city_starts_unpowered"),!City->Powered && City->PowerBlend==0);
            Check(TEXT("ruined_buildings_and_trees_follow_existing_ground"),Grounded());
            StartX=Cam->CameraComponent->OrthoWidth; GS->CompleteLevel();
            Check(TEXT("completion_locks_player_during_repair"),GS->Completed && !Player->ControlsAllowed());
            Check(TEXT("menu_and_travel_wait_for_reveal"),!GS->RestorationReady && !PC->bShowMouseCursor && !PC->SelectLevel(0));
            Advance(); return;
        }
        if(Stage==1)
        {
            if(Elapsed<2.5f) return;
            Check(TEXT("city_repair_progresses_over_time"),City->PowerBlend>.2f && City->PowerBlend<1);
            Check(TEXT("camera_pulls_back_smoothly"),Cam->CameraComponent->OrthoWidth>StartX+500 && Cam->CameraComponent->OrthoWidth<City->CityLength+1100);
            Check(TEXT("menu_remains_hidden_mid_animation"),!GS->RestorationReady && !PC->bShowMouseCursor);
            Advance(); return;
        }
        if(Stage==2)
        {
            if(!GS->RestorationReady) return;
            Check(TEXT("repair_finishes_before_chooser"),City->PowerBlend>=1 && GS->RestorationElapsed>=7.5f);
            Check(TEXT("roof_restored_upright"),Roof && FMath::Abs(Roof->GetRelativeRotation().Pitch)<.1f);
            bool Clean=true,Bloom=false;
            for(auto* Piece:Pieces)
            {
                if(Piece->GetName().StartsWith(TEXT("Rubble")) || Piece->GetName().StartsWith(TEXT("Decay"))) Clean&=!Piece->IsVisible();
                if(Piece->GetName().StartsWith(TEXT("Foliage"))) Bloom|=Piece->IsVisible() && Piece->GetRelativeScale3D().X>1;
            }
            Check(TEXT("rot_and_rubble_clear"),Clean); Check(TEXT("trees_bloom"),Bloom);
            Check(TEXT("restored_buildings_and_trees_follow_existing_ground"),Grounded());
            Check(TEXT("camera_frames_the_whole_district"),FMath::Abs(Cam->CameraComponent->OrthoWidth-City->CityLength-1100)<2 && FMath::Abs(Cam->GetActorLocation().X-City->CityLength*.5f)<2);
            Check(TEXT("rating_opens_after_reveal"),PC->bShowMouseCursor && PC->HUD && PC->HUD->IsRatingVisible() && !PC->SelectLevel(0));
            PC->ContinueFromRating();
            Check(TEXT("continue_opens_map_chooser"),GS->RatingDismissed && !PC->HUD->IsRatingVisible() && PC->HUD->IsLevelChoiceEnabled(0));
            Check(TEXT("only_next_district_unlocked"),PC->GetHighestUnlockedLevel()==FMath::Min(ScintillaCampaign::Index(this)+1,7));
            Finish(TEXT("ScintillaRestoration.json")); Stage=3; return;
        }
        return;
    }
    if(FParse::Param(FCommandLine::Get(),TEXT("ScintillaEnemiesSmoke")))
    {
        auto SpawnProbe=[this](EScintillaEnemyType Type)
        {
            FTransform Transform(FVector(450,0,27));
            EnemyProbe=GetWorld()->SpawnActorDeferred<AScintillaEnemy>(AScintillaEnemy::StaticClass(),Transform,this);
            EnemyProbe->EnemyType=Type; EnemyProbe->PatrolMinX=350; EnemyProbe->PatrolMaxX=550; EnemyProbe->Speed=100;
            UGameplayStatics::FinishSpawningActor(EnemyProbe,Transform);
        };
        switch(Stage)
        {
        case 0:
            if(Elapsed<.7f) return;
            Place(FVector(200,0,70)); SpawnProbe(EScintillaEnemyType::Scout); StartX=450; Advance(); return;
        case 1:
            if(Elapsed<.5f) return;
            Check(TEXT("scout_patrol_moves"),FMath::Abs(EnemyProbe->GetActorLocation().X-StartX)>20);
            Check(TEXT("scout_has_blender_body"),EnemyProbe->Visual->GetStaticMesh()->GetName()==TEXT("SM_EnemyScout"));
            Check(TEXT("scout_rotor_spins"),EnemyProbe->MotionPart->IsVisible() && !EnemyProbe->MotionPart->GetRelativeRotation().IsNearlyZero());
            Check(TEXT("scout_hovers_visually_without_moving_hitbox"),FMath::IsNearlyEqual(EnemyProbe->GetActorLocation().Z,27.f) && EnemyProbe->Visual->GetRelativeLocation().Z>-24);
            EnemyProbe->TakeStrike(); Check(TEXT("scout_one_hit_defeat"),EnemyProbe->Defeated);
            EnemyProbe->Destroy(); SpawnProbe(EScintillaEnemyType::Charger); StartX=450; Advance(); return;
        case 2:
            if(Elapsed<.2f) return;
            Check(TEXT("charger_warns_before_rushing"),EnemyProbe->Phase==EScintillaEnemyPhase::Windup && FMath::Abs(EnemyProbe->GetActorLocation().X-StartX)<2);
            Check(TEXT("charger_has_blender_body_and_wheels"),EnemyProbe->Visual->GetStaticMesh()->GetName()==TEXT("SM_EnemyCharger") && EnemyProbe->MotionPartRight->IsVisible());
            Advance(); return;
        case 3:
            if(Elapsed<.75f) return;
            Check(TEXT("charger_dashes_toward_player"),EnemyProbe->Phase==EScintillaEnemyPhase::Dashing && EnemyProbe->GetActorLocation().X<StartX-25);
            Check(TEXT("charger_wheels_animate"),FMath::Abs(EnemyProbe->MotionPart->GetRelativeRotation().Pitch)>5);
            Advance(); return;
        case 4:
            if(Elapsed<.55f) return;
            Check(TEXT("charger_recovers_after_dash"),EnemyProbe->Phase==EScintillaEnemyPhase::Recovery);
            Check(TEXT("charger_stays_inside_safe_patrol_bounds"),EnemyProbe->GetActorLocation().X>=350 && EnemyProbe->GetActorLocation().X<=550);
            EnemyProbe->TakeStrike(); Check(TEXT("charger_one_hit_defeat"),EnemyProbe->Defeated);
            EnemyProbe->Destroy(); SpawnProbe(EScintillaEnemyType::Sentinel); Advance(); return;
        case 5:
            if(Elapsed<.2f) return;
            Check(TEXT("sentinel_has_blender_shield_body"),EnemyProbe->Visual->GetStaticMesh()->GetName()==TEXT("SM_EnemySentinel"));
            Check(TEXT("sentinel_starts_with_two_armor"),EnemyProbe->Armor==2);
            EnemyProbe->TakeStrike(); Check(TEXT("sentinel_survives_first_strike"),EnemyProbe->Armor==1 && !EnemyProbe->Defeated);
            EnemyProbe->TakeStrike(); Check(TEXT("sentinel_ignores_duplicate_same_attack_hit"),EnemyProbe->Armor==1);
            Advance(); return;
        case 6:
            if(Elapsed<.3f) return;
            EnemyProbe->TakeStrike(); Check(TEXT("sentinel_second_strike_defeats"),EnemyProbe->Defeated);
            EnemyProbe->Destroy(); SpawnProbe(EScintillaEnemyType::Sentinel);
            Place(FVector(450,0,152)); Advance(); return;
        case 7:
            if(Elapsed<.38f) return;
            Check(TEXT("stomp_bypasses_sentinel_armor"),EnemyProbe->Defeated);
            Check(TEXT("stomp_bounces_player"),Player->GetVelocity().Z>0);
            Check(TEXT("enemy_fixture_preserves_player_health"),Player->Health->CurrentHealth==3);
            Finish(TEXT("ScintillaEnemies.json")); Stage=8; return;
        }
        return;
    }
    if(FParse::Param(FCommandLine::Get(),TEXT("ScintillaFacingSmoke")))
    {
        auto* Mesh=Player->GetMesh();
        auto Faces=[Mesh](FVector Direction){ return FVector::DotProduct(Mesh->GetRightVector(),Direction)>.99f; };
        switch(Stage)
        {
        case 0:
            if(Elapsed<.7f) return;
            Place(FVector(400,0,100)); Player->FaceCamera(); Advance(); return;
        case 1:
            if(Elapsed<.4f) return;
            Check(TEXT("S_faces_camera"),Faces(FVector(0,1,0)) && Player->LookDirection==EScintillaLookDirection::Camera);
            Player->FaceCity(); Advance(); return;
        case 2:
            if(Elapsed<.4f) return;
            Check(TEXT("W_faces_city"),Faces(FVector(0,-1,0)) && Player->LookDirection==EScintillaLookDirection::City);
            Check(TEXT("W_keeps_movement_plane"),FMath::Abs(Player->GetActorLocation().Y)<.01f && Player->GetActorRotation().IsNearlyZero());
            Player->FaceCamera(); Advance(); return;
        case 3:
            if(Elapsed<.4f) return;
            Check(TEXT("S_returns_from_city_to_camera"),Faces(FVector(0,1,0)));
            StartX=Player->GetActorLocation().X; Player->MoveAxis(-1); Advance(); return;
        case 4:
            if(Elapsed<.4f) return;
            Check(TEXT("A_walks_left"),Player->GetActorLocation().X<StartX-120 && Player->GetVelocity().X<-500);
            Check(TEXT("A_faces_left_profile"),Faces(FVector(-1,0,0)) && Player->LookDirection==EScintillaLookDirection::Left);
            Check(TEXT("A_plays_walk_animation"),Player->AnimationState==EScintillaState::Run && Mesh->GetSingleNodeInstance()->GetCurrentAsset()==Player->AnimationClips.FindRef(EScintillaState::Run) && Mesh->GetPosition()>.1f);
            Mesh->SetPosition(.2f,false); Mesh->RefreshBoneTransforms();
            LeftFootPhase=Mesh->GetBoneLocation(TEXT("foot_L"))-Player->GetActorLocation();
            Player->MoveAxis(0); Advance(); return;
        case 5:
            if(Elapsed<.3f) return;
            Check(TEXT("releasing_A_retains_left_pose"),Faces(FVector(-1,0,0)) && Player->AnimationState==EScintillaState::Idle);
            Player->FaceCamera(); Advance(); return;
        case 6:
            if(Elapsed<.4f) return;
            Check(TEXT("S_returns_from_left_to_camera"),Faces(FVector(0,1,0)));
            StartX=Player->GetActorLocation().X; Player->MoveAxis(1); Advance(); return;
        case 7:
            if(Elapsed<.4f) return;
            Check(TEXT("D_walks_right"),Player->GetActorLocation().X>StartX+120 && Player->GetVelocity().X>500);
            Check(TEXT("D_faces_right_profile"),Faces(FVector(1,0,0)) && Player->LookDirection==EScintillaLookDirection::Right);
            Check(TEXT("D_uses_same_walk_clip"),Mesh->GetSingleNodeInstance()->GetCurrentAsset()==Player->AnimationClips.FindRef(EScintillaState::Run));
            Mesh->SetPosition(.2f,false); Mesh->RefreshBoneTransforms();
            { FVector RightFoot=Mesh->GetBoneLocation(TEXT("foot_L"))-Player->GetActorLocation();
              Check(TEXT("left_and_right_gaits_are_mirrored"),FMath::Abs(LeftFootPhase.X+RightFoot.X)<.5f && FMath::Abs(LeftFootPhase.Y-RightFoot.Y)<.5f && FMath::Abs(LeftFootPhase.Z-RightFoot.Z)<.5f); }
            Player->MoveAxis(0); Player->FaceCity(); Advance(); return;
        case 8:
            if(Elapsed<.4f) return;
            Check(TEXT("W_returns_from_right_to_city"),Faces(FVector(0,-1,0)));
            Check(TEXT("turning_keeps_idle_grounded"),Player->GetCharacterMovement()->IsMovingOnGround() && Player->AnimationState==EScintillaState::Idle);
            PC->TogglePause(); Player->FaceCamera();
            Check(TEXT("paused_game_ignores_turn_commands"),Player->LookDirection==EScintillaLookDirection::City);
            PC->ResumeGame(); Player->Attack();
            Check(TEXT("attack_faces_last_walk_direction"),Player->LookDirection==EScintillaLookDirection::Right);
            Finish(TEXT("ScintillaFacing.json")); Stage=9; return;
        }
        return;
    }
    if (FParse::Param(FCommandLine::Get(),TEXT("ScintillaProgressionSmoke")))
    {
        int32 Step=0; FParse::Value(FCommandLine::Get(),TEXT("ScintillaProgressionStep="),Step);
        const int32 Initial[]={0,1,0,2,0,3,0,4,0,5,0,6,0,7};
        const int32 Destination[]={1,0,2,0,3,0,4,0,5,0,6,0,7,0};
        const int32 Before[]={0,1,2,2,3,3,4,4,5,5,6,6,7,7};
        if (Step<0 || Step>=UE_ARRAY_COUNT(Initial)) { Check(TEXT("valid_test_step"),false); Finish(TEXT("ScintillaProgression.json")); return; }
        const int32 Current=ScintillaCampaign::Index(this);
        const FString Pending=FPaths::ProjectSavedDir()/TEXT("ProgressionPending.txt");
        const FString Report=FString::Printf(TEXT("ScintillaProgression%d.json"),Step);
        if (Current==Destination[Step])
        {
            FString Previous;
            if (FFileHelper::LoadFileToString(Previous,*Pending))
            {
                int32 Split=0;
                if (Previous.FindChar('\n',Split)) { Failures=FCString::Atoi(*Previous.Left(Split)); Checks.Add(Previous.Mid(Split+1)); }
            }
            else Check(TEXT("selection_report_exists"),false);
            Check(TEXT("chosen_map_loaded"),true);
            Check(TEXT("selection_resets_level_state"),GS && !GS->Completed && GS->Energy==0 && Player->Health->CurrentHealth==3);
            Check(TEXT("progress_survives_map_travel"),PC->GetHighestUnlockedLevel()==FMath::Max(Before[Step],FMath::Min(Initial[Step]+1,ScintillaCampaign::Count-1)));
            Finish(Report); return;
        }
        if (Elapsed<.7f) return;
        if(Stage==0)
        {
            Check(TEXT("starts_in_expected_map"),Current==Initial[Step]);
            Check(TEXT("progress_loaded_in_fresh_process"),PC->GetHighestUnlockedLevel()==Before[Step]);
            Check(TEXT("cannot_select_before_winning"),!PC->SelectLevel(0));
            GS->CompleteLevel(); Advance(); return;
        }
        if(!GS->RestorationReady) return;
        PC->ContinueFromRating();
        const int32 Highest=FMath::Max(Before[Step],FMath::Min(Current+1,ScintillaCampaign::Count-1));
        Check(TEXT("completion_unlocks_only_next_level"),PC->GetHighestUnlockedLevel()==Highest && PC->IsLevelCompleted(Current));
        for (int32 Index=0;Index<ScintillaCampaign::Count;++Index)
            Check(FString::Printf(TEXT("chooser_level_%d_enabled_matches_unlock"),Index+1),PC->HUD && PC->HUD->IsLevelChoiceEnabled(Index)==(Index<=Highest));
        Check(TEXT("rejects_invalid_level_indices"),!PC->SelectLevel(-1) && !PC->SelectLevel(ScintillaCampaign::Count));
        if (Highest+1<ScintillaCampaign::Count) Check(TEXT("rejects_skipping_a_locked_district"),!PC->SelectLevel(Highest+1));
        if (Step==0) Check(TEXT("level_1_win_cannot_skip_to_3_or_4"),!PC->SelectLevel(2) && !PC->SelectLevel(3));
        if (Step==1) Check(TEXT("level_2_win_cannot_skip_to_4"),!PC->SelectLevel(3));
        if (Step==2) Check(TEXT("replaying_level_1_does_not_unlock_level_4"),!PC->SelectLevel(3));
        PC->ShowCompletion();
        Check(TEXT("repeated_completion_never_unlocks_extra_level"),PC->GetHighestUnlockedLevel()==Highest);
        FString Slot; FParse::Value(FCommandLine::Get(),TEXT("ScintillaProgressSlot="),Slot);
        auto* Saved=Cast<UScintillaProgress>(UGameplayStatics::LoadGameFromSlot(Slot,0));
        Check(TEXT("unlocks_written_to_save"),Saved && Saved->HighestUnlocked==Highest && (Saved->CompletedLevels & (1<<Current))!=0);
        FFileHelper::SaveStringToFile(FString::Printf(TEXT("%d\n%s"),Failures,*FString::Join(Checks,TEXT(","))),*Pending);
        if (!PC->SelectLevel(Destination[Step])) { Check(TEXT("unlocked_selection_accepted"),false); Finish(Report); }
        return;
    }
    if (FParse::Param(FCommandLine::Get(),TEXT("ScintillaCampaignSmoke")))
    {
        int32 Initial=2;
        FParse::Value(FCommandLine::Get(),TEXT("ScintillaStartLevel="),Initial);
        const int32 Current=ScintillaCampaign::Index(this)+1;
        const FString Pending=FPaths::ProjectSavedDir()/FString::Printf(TEXT("CampaignPending%d.txt"),Initial);
        const FString Report=FString::Printf(TEXT("ScintillaCampaign%02d.json"),Initial);
        if (Current!=Initial)
        {
            FString Previous;
            if (FFileHelper::LoadFileToString(Previous,*Pending))
            {
                int32 Split=0;
                if (Previous.FindChar('\n',Split)) { Failures=FCString::Atoi(*Previous.Left(Split)); Checks.Add(Previous.Mid(Split+1)); }
            }
            else Check(TEXT("previous_level_report_exists"),false);
            Check(TEXT("next_level_travel"),Current==Initial%ScintillaCampaign::Count+1);
            Check(TEXT("next_level_resets_health_and_progress"),GS && GS->Energy==0 && !GS->Completed && Player->Health->CurrentHealth==3);
            Finish(Report); return;
        }
        switch (Stage)
        {
        case 0:
            if (Elapsed<.7f) return;
            Check(TEXT("campaign_player_grounded"),Player->GetCharacterMovement()->IsMovingOnGround());
            Check(TEXT("campaign_hud_created"),PC && PC->HUD);
            Check(TEXT("campaign_energy_registered"),GS && GS->TotalEnergy>=10);
            { int32 Enemies=0; for (TActorIterator<AScintillaEnemy> It(GetWorld());It;++It) ++Enemies;
              const int32 Expected[]={2,3,4,5,5,5,6,7};
              Check(TEXT("campaign_enemy_difficulty_count"),Enemies==Expected[Current-1]); }
            Check(TEXT("campaign_next_map_exists"),FPackageName::DoesPackageExist(ScintillaCampaign::Next(this)));
            StartX=Player->GetActorLocation().X; Player->MoveAxis(1); Advance(); return;
        case 1:
            if (Elapsed<.4f) return;
            Check(TEXT("campaign_movement"),Player->GetActorLocation().X>StartX+120);
            Player->MoveAxis(0);
            for (TActorIterator<AScintillaCheckpoint> It(GetWorld());It;++It) { Place(It->GetActorLocation()+FVector(0,0,15)); break; }
            Advance(); return;
        case 2:
            if (Elapsed<.3f) return;
            Check(TEXT("campaign_checkpoint"),GS && GS->HasCheckpoint);
            Player->Health->Kill(); Advance(); return;
        case 3:
            if (Elapsed<1.2f) return;
            Check(TEXT("campaign_respawn"),Player->ControlsAllowed() && Player->Health->CurrentHealth==3 && GS && FMath::Abs(Player->GetActorLocation().X-GS->RespawnPosition.X)<5);
            PC->TogglePause(); Check(TEXT("campaign_pause"),PC->IsPaused()); PC->ResumeGame(); Check(TEXT("campaign_resume"),!PC->IsPaused());
            for (TActorIterator<AScintillaMovingPlatform> It(GetWorld());It;++It) { Place(It->GetActorLocation()+FVector(0,0,70)); StartX=Player->GetActorLocation().X; break; }
            Advance(); return;
        case 4:
            if (Elapsed<1.2f) return;
            for (TActorIterator<AScintillaMovingPlatform> It(GetWorld());It;++It)
                Check(TEXT("campaign_lift_carries_player"),Player->GetMovementBaseObject()==It->Surface && FMath::Abs(Player->GetActorLocation().X-StartX)>30);
            for (TActorIterator<AScintillaGoal> It(GetWorld());It;++It) { Place(It->GetActorLocation()); break; }
            Advance(); return;
        case 5:
            if (Elapsed<.3f || (GS && GS->Completed && !GS->RestorationReady)) return;
            Check(TEXT("campaign_goal"),GS && GS->Completed);
            PC->ContinueFromRating();
            for (TActorIterator<AScintillaCity> It(GetWorld());It;++It) Check(TEXT("campaign_city_power"),It->Powered);
            if (!GS || !GS->Completed) { Finish(Report); return; }
            FFileHelper::SaveStringToFile(FString::Printf(TEXT("%d\n%s"),Failures,*FString::Join(Checks,TEXT(","))),*Pending);
            if (!PC->SelectLevel(Initial%ScintillaCampaign::Count)) { Check(TEXT("next_level_is_unlocked"),false); Finish(Report); }
            return;
        }
        return;
    }
    switch (Stage)
    {
    case 0:
        if (Elapsed<.7f) break;
        Check(TEXT("player_spawns_grounded"),Player->GetCharacterMovement()->IsMovingOnGround());
        Check(TEXT("health_initial_3"),Player->Health->CurrentHealth==3);
        Check(TEXT("enhanced_input_assets"),PC && PC->MoveAction && PC->JumpAction && PC->MappingContext);
        Check(TEXT("hud_created"),PC && PC->HUD);
        { int32 Coins=0; for(TActorIterator<AScintillaCoin> It(GetWorld());It;++It) ++Coins;
          Check(TEXT("all_collectibles_registered"),GS && GS->TotalEnergy==Coins && Coins>=17); }
        Check(TEXT("robot_rig_and_eight_clips_loaded"),Player->GetMesh()->GetSkeletalMeshAsset() && Player->AnimationClips.Num()==8 && Player->GetMesh()->GetBoneIndex(TEXT("foot_L"))!=INDEX_NONE);
        Check(TEXT("robot_feet_at_walk_surface"),FMath::Abs(Player->GetMesh()->GetBoneLocation(TEXT("foot_L")).Z-5.6f-(Player->GetActorLocation().Z-41.65f))<1.f);
        StartX=Player->GetActorLocation().X; Player->MoveAxis(1); Advance(); break;
    case 1:
        if (Elapsed<.45f) break;
        Check(TEXT("horizontal_acceleration"),Player->GetActorLocation().X>StartX+150 && Player->GetVelocity().X>500);
        Check(TEXT("robot_run_clip_advances"),Player->GetMesh()->GetSingleNodeInstance() && Player->GetMesh()->GetSingleNodeInstance()->GetCurrentAsset()==Player->AnimationClips.FindRef(EScintillaState::Run) && Player->GetMesh()->GetPosition()>.1f);
        Player->MoveAxis(0); Advance(); break;
    case 2:
        if (Elapsed<.3f) break;
        Check(TEXT("ground_braking"),FMath::Abs(Player->GetVelocity().X)<1);
        Check(TEXT("robot_idle_replaces_run_when_stationary"),Player->AnimationState==EScintillaState::Idle && Player->GetMesh()->GetSingleNodeInstance()->GetCurrentAsset()==Player->AnimationClips.FindRef(EScintillaState::Idle));
        Player->PressJump(); FullJumpPeak=Player->GetActorLocation().Z; Advance(); break;
    case 3:
        if (Elapsed>.15f && !Released)
        {
            Check(TEXT("robot_jump_uses_skeletal_clip"),Player->AnimationState==EScintillaState::Jump && Player->GetMesh()->GetSingleNodeInstance()->GetCurrentAsset()==Player->AnimationClips.FindRef(EScintillaState::Jump));
            Released=true;
        }
        FullJumpPeak=FMath::Max(FullJumpPeak,static_cast<float>(Player->GetActorLocation().Z));
        if (Elapsed<1) break;
        Check(TEXT("full_jump_and_land"),FullJumpPeak>195 && Player->GetCharacterMovement()->IsMovingOnGround());
        Player->ReleaseJump(); Player->PressJump(); ShortJumpPeak=Player->GetActorLocation().Z; Advance(); break;
    case 4:
        if (Elapsed>.055f && !Released) { Player->ReleaseJump(); Released=true; }
        ShortJumpPeak=FMath::Max(ShortJumpPeak,static_cast<float>(Player->GetActorLocation().Z));
        if (Elapsed<.85f) break;
        Check(TEXT("short_jump_lower_than_full"),ShortJumpPeak<FullJumpPeak-60 && ShortJumpPeak>65);
        Place(FVector(500,0,80)); Advance(); break;
    case 5:
        if (Elapsed<.3f) break;
        Check(TEXT("coin_overlap_increments_once"),GS && GS->Energy>=1 && GS->Energy<=2);
        Place(FVector(3900,0,110)); Advance(); break;
    case 6:
        if (Elapsed<.3f) break;
        Check(TEXT("checkpoint_overlap"),GS && GS->HasCheckpoint && GS->ActiveCheckpoint);
        Player->Health->ApplyHit(1,Player->GetActorLocation()+FVector(100,0,0));
        Check(TEXT("reusable_damage"),Player->Health->CurrentHealth==2);
        Player->Health->ApplyHit(1,Player->GetActorLocation());
        Check(TEXT("invulnerability_blocks_repeated_hit"),Player->Health->CurrentHealth==2);
        Player->Health->Kill();
        Check(TEXT("death_disables_controls"),!Player->ControlsAllowed()); Advance(); break;
    case 7:
        if (Elapsed<1.3f) break;
        Check(TEXT("respawn_restores_health"),Player->Health->CurrentHealth==3 && Player->ControlsAllowed());
        Check(TEXT("respawn_latest_checkpoint"),FMath::Abs(Player->GetActorLocation().X-3900)<5);
        Check(TEXT("collection_persists_after_death"),GS && GS->Energy>=1);
        for (TActorIterator<AScintillaEnemy> It(GetWorld());It;++It) { StartX=LastEnemyX=It->GetActorLocation().X; EnemyTravelDistance=0; break; }
        Advance(); break;
    case 8:
        for(TActorIterator<AScintillaEnemy> It(GetWorld());It;++It) { EnemyTravelDistance+=FMath::Abs(It->GetActorLocation().X-LastEnemyX); LastEnemyX=It->GetActorLocation().X; break; }
        if (Elapsed<.5f) break;
        for (TActorIterator<AScintillaEnemy> It(GetWorld());It;++It)
        {
            Check(TEXT("enemy_patrol_moves"),EnemyTravelDistance>20 && It->GetActorLocation().X>=It->PatrolMinX && It->GetActorLocation().X<=It->PatrolMaxX);
            Place(It->GetActorLocation()+FVector(-65,0,19)); Player->Attack();
            Check(TEXT("dedicated_attack_defeats_enemy"),It->Defeated); break;
        }
        for (TActorIterator<AScintillaMovingPlatform> It(GetWorld());It;++It)
        { Place(It->GetActorLocation()+FVector(0,0,70)); StartX=Player->GetActorLocation().X; break; }
        Advance(); break;
    case 9:
        if (Elapsed<1.2f) break;
        Check(TEXT("moving_platform_carries_character"),Player->GetMovementBaseObject()!=nullptr && FMath::Abs(Player->GetActorLocation().X-StartX)>50);
        Place(FVector(3250,0,55)); Advance(); break;
    case 10:
        if (Elapsed<.25f) break;
        Check(TEXT("spike_overlap_damages"),Player->Health->CurrentHealth<3);
        Place(FVector(4000,0,-450)); Advance(); break;
    case 11:
        if (Elapsed<.1f) break;
        Check(TEXT("kill_zone_ignores_invulnerability"),Player->Health->IsDead()); Advance(); break;
    case 12:
        if (Elapsed<1.1f) break;
        Check(TEXT("kill_zone_respawn"),Player->ControlsAllowed());
        if (PC) { PC->TogglePause(); Check(TEXT("pause_menu_pauses_world"),PC->IsPaused()); PC->TogglePause(); Check(TEXT("pause_menu_resumes_world"),!PC->IsPaused()); }
        Place(FVector(930,0,90)); Advance(); break;
    case 13:
        if (Elapsed<.4f) break;
        Player->MoveAxis(1); Advance(); break;
    case 14:
        if (!Player->GetCharacterMovement()->IsFalling()) { Elapsed=0; break; }
        if (Elapsed<.065f) break;
        Player->PressJump();
        Check(TEXT("coyote_jump_after_leaving_edge"),Player->GetVelocity().Z>500);
        Player->MoveAxis(0); Place(FVector(750,0,160)); Advance(); break;
    case 15:
        if (!Released && Player->GetActorLocation().Z<95 && Player->GetVelocity().Z<0)
        { Player->PressJump(); Released=true; }
        if (Released && Player->GetVelocity().Z>500)
        { Check(TEXT("buffer_jump_before_landing"),true); for(TActorIterator<AScintillaGoal> It(GetWorld());It;++It) { Place(It->GetActorLocation()+FVector(0,0,40)); break; } Advance(); break; }
        if (Elapsed>1.5f)
        { Check(TEXT("buffer_jump_before_landing"),false); for(TActorIterator<AScintillaGoal> It(GetWorld());It;++It) { Place(It->GetActorLocation()+FVector(0,0,40)); break; } Advance(); }
        break;
    case 16:
        if (Elapsed<.4f) break;
        Check(TEXT("goal_completes_level"),GS && GS->Completed);
        Check(TEXT("goal_disables_gameplay"),!Player->ControlsAllowed());
        for (TActorIterator<AScintillaCity> It(GetWorld());It;++It) Check(TEXT("city_power_restored"),It->Powered);
        Advance(); break;
    case 17:
        {
            Finish(TEXT("ScintillaPlaytest.json")); Stage=18;
            break;
        }
    }
}
void AScintillaPlaytest::Finish(const FString& FileName)
{
    const FString Report=FString::Printf(TEXT("{\"failures\":%d,\"checks\":[%s]}"),Failures,*FString::Join(Checks,TEXT(",")));
    FFileHelper::SaveStringToFile(Report,*(FPaths::ProjectSavedDir()/FileName));
    UE_LOG(LogTemp,Display,TEXT("SCINTILLA_PLAYTEST_DONE failures=%d"),Failures);
    FPlatformMisc::RequestExit(false);
}
void AScintillaPlaytest::TickRoute(float Dt)
{
    const bool Condotte=UGameplayStatics::GetCurrentLevelName(this,true)==TEXT("L_03_Condotte");
    const bool Torre=UGameplayStatics::GetCurrentLevelName(this,true)==TEXT("L_04_Torre");
    const bool Expansion=ScintillaCampaign::Index(this)>=4;
    const FString RouteReport=Expansion ? FString::Printf(TEXT("ScintillaExpansionRoute%02d.json"),ScintillaCampaign::Index(this)+1) : Torre ? TEXT("ScintillaTorreRoute.json") : Condotte ? TEXT("ScintillaCondotteRoute.json") : TEXT("ScintillaRoute.json");
    RouteDuration+=Dt;
    if (Elapsed<.7f) return;
    auto* GS=GetWorld()->GetGameState<AScintillaGameState>();
    if (GS && GS->Completed)
    {
        Check(TEXT("full_level_within_attempt_budget"),RouteDuration<180 && GS->Deaths<GS->AttemptLimit());
        Check(FString::Printf(TEXT("checkpoint_respawns_%d"),GS->Deaths),true);
        Check(TEXT("route_activated_checkpoint"),GS->HasCheckpoint);
        Check(TEXT("route_collected_energy"),GS->Energy>0);
        Finish(RouteReport); RouteDuration=-10000; return;
    }
    if (RouteDuration>180)
    {
        Check(TEXT("full_level_without_teleport_or_death"),false);
        UE_LOG(LogTemp,Display,TEXT("Route failed at step %d, position %s"),RouteStep,*Player->GetActorLocation().ToString());
        Finish(RouteReport); RouteDuration=-10000; return;
    }
    if(Player->Health->IsDead()) { Player->MoveAxis(0); return; }
    const float X=Player->GetActorLocation().X;
    const double Now=GetWorld()->GetTimeSeconds();
    if (JumpReleaseAt>0 && Now>=JumpReleaseAt) { Player->ReleaseJump(); JumpReleaseAt=-1; }
    const bool Grounded=Player->GetCharacterMovement()->IsMovingOnGround();
    for (TActorIterator<AScintillaEnemy> It(GetWorld());It;++It)
        if (!It->Defeated && It->GetActorLocation().X-X>0 && It->GetActorLocation().X-X<125 && FMath::Abs(It->GetActorLocation().Z-Player->GetActorLocation().Z)<55)
        {
            Player->Attack();
            if(!It->Defeated && It->EnemyType==EScintillaEnemyType::Sentinel && Grounded) { Player->MoveAxis(0); return; }
        }
    float ChallengeStart=FLT_MAX;
    TArray<AScintillaPlatform*> RoutePlatforms;
    for(TActorIterator<AScintillaPlatform> It(GetWorld());It;++It)
        if(!Cast<AScintillaMovingPlatform>(*It))
        {
            RoutePlatforms.Add(*It);
            if(It->ActorHasTag(TEXT("ScintillaChallenge"))) ChallengeStart=FMath::Min(ChallengeStart,float(It->Surface->Bounds.Origin.X-It->Surface->Bounds.BoxExtent.X));
        }
    if(X>ChallengeStart-310)
    {
        for(TActorIterator<AScintillaObstacle> It(GetWorld());It;++It)
        {
            const float Ahead=It->GetActorLocation().X-X;
            if(It->ObstacleType!=EScintillaObstacleType::Ice && It->ObstacleType!=EScintillaObstacleType::Wind && Ahead>130 && Ahead<290 && Grounded)
            {
                const float C=FMath::Fmod(It->Clock,6.f);
                if(C<4.2f || C>5.7f) { Player->MoveAxis(0); return; }
            }
        }
        Player->MoveAxis(1);
        if(Grounded)
        {
            RoutePlatforms.Sort([](const AScintillaPlatform& A,const AScintillaPlatform& B){ return A.GetActorLocation().X<B.GetActorLocation().X; });
            for(auto* Platform:RoutePlatforms) if(Player->GetMovementBaseObject()==Platform->Surface)
            {
                const float Edge=Platform->Surface->Bounds.Origin.X+Platform->Surface->Bounds.BoxExtent.X;
                const int32 I=RoutePlatforms.IndexOfByKey(Platform);
                if(I+1<RoutePlatforms.Num() && X>=Edge-230)
                {
                    const auto* Next=RoutePlatforms[I+1];
                    const float Left=Next->Surface->Bounds.Origin.X-Next->Surface->Bounds.BoxExtent.X;
                    const float Right=Next->Surface->Bounds.Origin.X+Next->Surface->Bounds.BoxExtent.X;
                    for(TActorIterator<AScintillaObstacle> It(GetWorld());It;++It)
                        if(It->ObstacleType!=EScintillaObstacleType::Ice && It->ObstacleType!=EScintillaObstacleType::Wind && It->GetActorLocation().X>Left && It->GetActorLocation().X<Right)
                        { const float C=FMath::Fmod(It->Clock,6.f); if(C<4.2f || C>5.f) { Player->MoveAxis(0); return; } }
                }
                if(Platform!=RoutePlatforms.Last() && X>=Edge-60) { Player->PressJump(); return; }
            }
            for(TActorIterator<AScintillaEnemy> It(GetWorld());It;++It)
                if(!It->Defeated && (It->EnemyType==EScintillaEnemyType::Flyer || It->EnemyType==EScintillaEnemyType::SurveyFlyer) && It->GetActorLocation().X-X>100 && It->GetActorLocation().X-X<200) { Player->PressJump(); return; }
        }
        return;
    }
    if (ScintillaCampaign::Index(this)<ScintillaCampaign::Count)
    {
        TArray<AScintillaPlatform*> Platforms;
        AScintillaMovingPlatform* Lift=nullptr;
        for(TActorIterator<AScintillaPlatform> It(GetWorld());It;++It)
            if(auto* Moving=Cast<AScintillaMovingPlatform>(*It)) Lift=Moving; else Platforms.Add(*It);
        Platforms.Sort([](const AScintillaPlatform& A,const AScintillaPlatform& B){ return A.GetActorLocation().X<B.GetActorLocation().X; });
        if(!Lift || Platforms.Num()<6) { Check(TEXT("expansion_route_geometry"),false); Finish(RouteReport); return; }
        const float DockEdge=Platforms[4]->Surface->Bounds.Origin.X+Platforms[4]->Surface->Bounds.BoxExtent.X;
        const float ExitEdge=Platforms[5]->Surface->Bounds.Origin.X-Platforms[5]->Surface->Bounds.BoxExtent.X;
        if(RouteStep==0 && X>=DockEdge-55 && Grounded) { Player->MoveAxis(0); RouteStep=1; }
        if(RouteStep==1)
        {
            Player->MoveAxis(0);
            if(Grounded && Lift->GetActorLocation().X<DockEdge+230) { Player->PressJump(); RouteStep=2; }
            return;
        }
        if(RouteStep==2)
        {
            const float Desired=FMath::Clamp((Lift->GetActorLocation().X-X)*6.f,-300.f,300.f);
            Player->MoveAxis(FMath::Clamp((Desired-Player->GetVelocity().X)/100.f,-1.f,1.f));
            if(Grounded && Player->GetMovementBaseObject()==Lift->Surface) { Player->MoveAxis(0); RouteStep=3; }
            return;
        }
        if(RouteStep==3)
        {
            Player->MoveAxis(0);
            if(Grounded && Lift->GetActorLocation().X>ExitEdge-220) { Player->MoveAxis(1); Player->PressJump(); RouteStep=4; }
            return;
        }
        Player->MoveAxis(1);
        if(Grounded)
        {
            for(auto* Platform:Platforms)
                if(Player->GetMovementBaseObject()==Platform->Surface)
                {
                    const float Edge=Platform->Surface->Bounds.Origin.X+Platform->Surface->Bounds.BoxExtent.X;
                    if(Platform!=Platforms.Last() && X>=Edge-55)
                    {
                        UE_LOG(LogTemp,Display,TEXT("EXPANSION_JUMP x=%.1f edge=%.1f health=%d"),X,Edge,Player->Health->CurrentHealth);
                        Player->PressJump(); JumpReleaseAt=Now+.5f; return;
                    }
                }
            for(TActorIterator<AScintillaHazard> It(GetWorld());It;++It)
                if(!It->InstantKill && It->GetActorLocation().X-X>110 && It->GetActorLocation().X-X<190)
                { Player->PressJump(); JumpReleaseAt=Now+.18f; return; }
        }
        return;
    }
    if (RouteStep==0)
    {
        Player->MoveAxis(1);
        const bool JumpEdge=Torre ? ((X>=850 && X<935) || (X>=1490 && X<1570) || (X>=2130 && X<2210) || (X>=3420 && X<3500)) : Condotte ? ((X>=800 && X<935) || (X>=1440 && X<1570) || (X>=2080 && X<2210) || (X>=3240 && X<3370)) : ((X>=900 && X<1030) || (X>=1510 && X<1640) || (X>=2110 && X<2240) || (X>=3400 && X<3510));
        if (Grounded && JumpEdge) Player->PressJump();
        else if (Grounded && (Torre ? ((X>=320 && X<400) || (X>=3020 && X<3100) || (X>=3790 && X<3890)) : Condotte ? ((X>=2640 && X<2720) || (X>=3620 && X<3700)) : (X>=3110 && X<3200))) { Player->PressJump(); JumpReleaseAt=Now+.1f; }
        if (X>=(Torre ? 4290 : Condotte ? 4150 : 4180)) { Player->MoveAxis(0); RouteStep=1; }
        return;
    }
    AScintillaMovingPlatform* Bridge=nullptr;
    for (TActorIterator<AScintillaMovingPlatform> It(GetWorld());It;++It) { Bridge=*It; break; }
    if (RouteStep==1)
    {
        Player->MoveAxis(0);
        if (Bridge && Bridge->GetActorLocation().X<4480 && Grounded) { Player->PressJump(); RouteStep=2; }
        return;
    }
    if (RouteStep==2)
    {
        if (Bridge)
        {
            const float Desired=FMath::Clamp((Bridge->GetActorLocation().X-X)*6.f,-300.f,300.f);
            Player->MoveAxis(FMath::Clamp((Desired-Player->GetVelocity().X)/100.f,-1.f,1.f));
            if (Grounded && Player->GetMovementBaseObject()==Bridge->Surface) { Player->MoveAxis(0); RouteStep=3; }
        }
        return;
    }
    if (RouteStep==3)
    {
        Player->MoveAxis(0);
        if (Bridge && Bridge->GetActorLocation().X>((Condotte || Torre) ? 4720 : 4740) && Grounded) { Player->MoveAxis(1); Player->PressJump(); RouteStep=4; }
        return;
    }
    Player->MoveAxis(1);
    const bool FinalJump=Torre ? ((X>=5570 && X<5650) || (X>=6210 && X<6290) || (X>=6870 && X<6950)) : Condotte ? ((X>=5420 && X<5550) || (X>=6060 && X<6200) || (X>=6700 && X<6840)) : ((X>=5410 && X<5550) || (X>=5960 && X<6100) || (X>=6530 && X<6670));
    if (Grounded && FinalJump) Player->PressJump();
    else if (Grounded && Condotte && X>=7090 && X<7160) { Player->PressJump(); JumpReleaseAt=Now+.1f; }
    else if (Grounded && Torre && X>=7470 && X<7560) { Player->PressJump(); JumpReleaseAt=Now+.1f; }
}
