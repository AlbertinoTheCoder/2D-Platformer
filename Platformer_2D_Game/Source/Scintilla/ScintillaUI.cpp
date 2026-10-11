#include "ScintillaUI.h"
#include "ScintillaPlayer.h"
#include "ScintillaHealth.h"
#include "ScintillaWorld.h"
#include "ScintillaPlaytest.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Blueprint/WidgetTree.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Components/Button.h"
#include "Components/Border.h"
#include "Components/SizeBox.h"
#include "Components/UniformGridPanel.h"
#include "Components/UniformGridSlot.h"
#include "ScintillaProgress.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputMappingContext.h"
#include "InputAction.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "ScintillaCampaign.h"
#include "Components/ProgressBar.h"
#include "Brushes/SlateRoundedBoxBrush.h"
#include "Misc/Paths.h"

namespace
{
    UTextBlock* Label(UWidgetTree* Tree,FName Name,int32 Size,FLinearColor Color)
    {
        auto* Text=Tree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(),Name);
        // Condensed headings and terminal-style small readouts, using bundled engine fonts.
        const TCHAR* Face=Size>=28 ? TEXT("Roboto-BlackItalic.ttf") : Size>=18 ? TEXT("Roboto-BoldCondensed.ttf") : TEXT("DroidSansMono.ttf");
        FSlateFontInfo Font(FPaths::EngineContentDir()/TEXT("Slate/Fonts")/Face,Size);
        Text->SetFont(Font);
        Text->SetShadowOffset(FVector2D(0,1)); Text->SetShadowColorAndOpacity(FLinearColor(0,0,0,.6f));
        Text->SetColorAndOpacity(FSlateColor(Color)); return Text;
    }
    void Place(UCanvasPanel* Canvas,UWidget* Widget,FVector2D Position,FVector2D Size,FAnchors Anchors=FAnchors(0,0),FVector2D Alignment=FVector2D::ZeroVector)
    {
        auto* Slot=Canvas->AddChildToCanvas(Widget);
        Slot->SetAnchors(Anchors); Slot->SetAlignment(Alignment); Slot->SetPosition(Position); Slot->SetSize(Size);
    }
    const FLinearColor Ink(.018f,.032f,.05f,.96f);
    const FLinearColor Cyan(.16f,.86f,.94f);
    const FLinearColor Amber(1,.67f,.23f);
    const FLinearColor DistrictColors[]={FLinearColor(.16f,.75f,1),FLinearColor(1,.48f,.18f),FLinearColor(.35f,.92f,.55f),FLinearColor(.7f,.5f,1),FLinearColor(.5f,.95f,1),FLinearColor(1,.3f,.25f),FLinearColor(1,.85f,.25f),FLinearColor(1,.45f,.8f)};
    UBorder* Panel(UWidgetTree* Tree,FLinearColor Fill,FLinearColor Edge,float Radius=8)
    {
        auto* Border=Tree->ConstructWidget<UBorder>();
        const FSlateRoundedBoxBrush Brush(Fill,Radius,Edge,1.f);
        Border->SetBrush(Brush); Border->SetPadding(FMargin(0));
        Border->SetVisibility(ESlateVisibility::HitTestInvisible);
        return Border;
    }
    void StyleButton(UButton* Button,FLinearColor Accent,bool Enabled=true)
    {
        auto Style=Button->GetStyle();
        Style.Normal=FSlateRoundedBoxBrush(Ink,6.f,Enabled ? Accent.CopyWithNewOpacity(.55f) : FLinearColor(.18f,.21f,.25f),1.f);
        Style.Hovered=FSlateRoundedBoxBrush(FLinearColor(.045f,.11f,.15f,1),6.f,Accent,2.f);
        Style.Pressed=FSlateRoundedBoxBrush(Accent.CopyWithNewOpacity(.2f),6.f,Accent,2.f);
        Style.Disabled=Style.Normal;
        Style.NormalPadding=FMargin(16,10); Style.PressedPadding=FMargin(16,11,16,9);
        Button->SetStyle(Style); Button->SetBackgroundColor(FLinearColor::White);
    }
}
TSharedRef<SWidget> UScintillaHUD::RebuildWidget()
{
    SetIsFocusable(true);
    if (!WidgetTree) WidgetTree=NewObject<UWidgetTree>(this);
    auto* Canvas=WidgetTree->ConstructWidget<UCanvasPanel>(); WidgetTree->RootWidget=Canvas;
    const FLinearColor Pale(.88f,.95f,1);
    Place(Canvas,Panel(WidgetTree,Ink,Cyan.CopyWithNewOpacity(.35f)),{24,24},{440,174});
    auto* Brand=Label(WidgetTree,TEXT("Brand"),30,Pale); Brand->SetText(FText::FromString(TEXT("SCINTILLA")));
    Place(Canvas,Brand,{44,32},{240,42});
    auto* Tag=Label(WidgetTree,TEXT("UnitTag"),12,Amber); Tag->SetText(FText::FromString(TEXT("UNIT / 01")));
    Place(Canvas,Tag,{322,48},{125,20});
    HealthLabel=Label(WidgetTree,TEXT("Health"),13,Pale); Place(Canvas,HealthLabel,{44,80},{240,24});
    HealthCells.Reset();
    for(int32 Cell=0;Cell<3;++Cell)
    {
        auto* Bar=Panel(WidgetTree,Cyan,FLinearColor::Transparent,2);
        Place(Canvas,Bar,{322.f+Cell*40.f,83},{30,9}); HealthCells.Add(Bar);
    }
    CheckpointLabel=Label(WidgetTree,TEXT("Checkpoint"),12,FLinearColor(.58f,.73f,.79f));
    CheckpointLabel->SetAutoWrapText(true); Place(Canvas,CheckpointLabel,{44,110},{400,40});
    AttemptsLabel=Label(WidgetTree,TEXT("Attempts"),12,Amber); Place(Canvas,AttemptsLabel,{44,160},{400,22});
    Place(Canvas,Panel(WidgetTree,Ink,Amber.CopyWithNewOpacity(.4f)),{-24,24},{260,100},FAnchors(1,0),{1,0});
    EnergyLabel=Label(WidgetTree,TEXT("Energy"),20,Amber); Place(Canvas,EnergyLabel,{-44,42},{220,30},FAnchors(1,0),{1,0});
    EnergyMeter=WidgetTree->ConstructWidget<UProgressBar>();
    FProgressBarStyle MeterStyle;
    MeterStyle.BackgroundImage=FSlateRoundedBoxBrush(FLinearColor(.08f,.12f,.16f),3.f);
    MeterStyle.FillImage=FSlateRoundedBoxBrush(FLinearColor::White,3.f);
    EnergyMeter->SetWidgetStyle(MeterStyle); EnergyMeter->SetFillColorAndOpacity(Amber);
    Place(Canvas,EnergyMeter,{-44,88},{220,10},FAnchors(1,0),{1,0});
    Place(Canvas,Panel(WidgetTree,Ink,Cyan.CopyWithNewOpacity(.2f)),{0,-24},{830,46},FAnchors(.5f,1),{.5f,1});
    auto* Hint=Label(WidgetTree,TEXT("Controls"),13,FLinearColor(.65f,.79f,.84f));
    Hint->SetJustification(ETextJustify::Center);
    Hint->SetText(FText::FromString(TEXT("[A/D] MOVE   [W/S] TURN   [SPACE] JUMP   [J] DISCHARGE   [E] ACTIVATE   [U] PAUSE")));
    Place(Canvas,Hint,{0,-35},{810,24},FAnchors(.5f,1),{.5f,1});
    MenuBackdrop=Panel(WidgetTree,FLinearColor(0,.008f,.018f,.76f),FLinearColor::Transparent,0);
    CinematicCaption=Label(WidgetTree,TEXT("RestorationCaption"),26,Pale);
    CinematicCaption->SetJustification(ETextJustify::Center);
    Place(Canvas,CinematicCaption,{0,-95},{900,74},FAnchors(.5f,1),{.5f,1});
    CinematicCaption->SetVisibility(ESlateVisibility::Collapsed);
    auto* BackSlot=Canvas->AddChildToCanvas(MenuBackdrop); BackSlot->SetAnchors(FAnchors(0,0,1,1)); BackSlot->SetOffsets(FMargin(0));
    MenuPanel=Panel(WidgetTree,Ink,Cyan.CopyWithNewOpacity(.65f),12);
    Place(Canvas,MenuPanel,{0,0},{840,820},FAnchors(.5f,.5f),{.5f,.5f});
    Message=Label(WidgetTree,TEXT("Message"),32,Pale); Message->SetJustification(ETextJustify::Center);
    Place(Canvas,Message,{0,-220},{660,100},FAnchors(.5f,.5f),{.5f,.5f});
    Menu=WidgetTree->ConstructWidget<UVerticalBox>(); Place(Canvas,Menu,{0,-235},{760,570},FAnchors(.5f,.5f),{.5f,0});
    RatingPanel=WidgetTree->ConstructWidget<UVerticalBox>(); Menu->AddChild(RatingPanel);
    RatingLetter=Label(WidgetTree,TEXT("RatingLetter"),112,Amber); RatingLetter->SetJustification(ETextJustify::Center); RatingPanel->AddChild(RatingLetter);
    RatingTotal=Label(WidgetTree,TEXT("RatingTotal"),22,Pale); RatingTotal->SetJustification(ETextJustify::Center); RatingPanel->AddChild(RatingTotal);
    RatingDetails=Label(WidgetTree,TEXT("RatingDetails"),19,Pale); RatingDetails->SetJustification(ETextJustify::Center); RatingPanel->AddChild(RatingDetails);
    RatingPanel->SetVisibility(ESlateVisibility::Collapsed);
    LevelButtons.Reset(); LevelCaptions.Reset();
    LevelChooser=WidgetTree->ConstructWidget<UUniformGridPanel>(UUniformGridPanel::StaticClass(),TEXT("LevelChooser"));
    LevelChooser->SetSlotPadding(FMargin(6)); Menu->AddChild(LevelChooser);
    for (int32 Index=0;Index<ScintillaCampaign::Count;++Index)
    {
        auto* Button=WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(),FName(*FString::Printf(TEXT("Level%d"),Index+1)));
        StyleButton(Button,DistrictColors[Index]);
        auto* Caption=Label(WidgetTree,NAME_None,20,Pale);
        Caption->SetJustification(ETextJustify::Center); Button->AddChild(Caption);
        auto* Box=WidgetTree->ConstructWidget<USizeBox>(); Box->SetHeightOverride(96); Box->SetWidthOverride(368); Box->AddChild(Button);
        auto* GridSlot=LevelChooser->AddChildToUniformGrid(Box,Index/2,Index%2);
        GridSlot->SetHorizontalAlignment(HAlign_Fill); GridSlot->SetVerticalAlignment(VAlign_Fill);
        LevelButtons.Add(Button); LevelCaptions.Add(Caption);
    }
    LevelButtons[0]->OnClicked.AddDynamic(this,&UScintillaHUD::ChooseOfficina);
    LevelButtons[1]->OnClicked.AddDynamic(this,&UScintillaHUD::ChooseFonderia);
    LevelButtons[2]->OnClicked.AddDynamic(this,&UScintillaHUD::ChooseCondotte);
    LevelButtons[3]->OnClicked.AddDynamic(this,&UScintillaHUD::ChooseTorre);
    LevelButtons[4]->OnClicked.AddDynamic(this,&UScintillaHUD::ChooseCryo);
    LevelButtons[5]->OnClicked.AddDynamic(this,&UScintillaHUD::ChooseScrap);
    LevelButtons[6]->OnClicked.AddDynamic(this,&UScintillaHUD::ChooseSolar);
    LevelButtons[7]->OnClicked.AddDynamic(this,&UScintillaHUD::ChooseBio);
    LevelChooser->SetVisibility(ESlateVisibility::Collapsed);
    ContinueButton=AddButton(TEXT("CONTINUE")); ContinueButton->OnClicked.AddDynamic(this,&UScintillaHUD::ContinueRating);
    ContinueButton->SetVisibility(ESlateVisibility::Collapsed);
    ResumeButton=AddButton(TEXT("RESUME")); ResumeButton->OnClicked.AddDynamic(this,&UScintillaHUD::Resume);
    ChooseLevelButton=AddButton(TEXT("CHOOSE LEVEL")); ChooseLevelButton->OnClicked.AddDynamic(this,&UScintillaHUD::OpenLevelChooser);
    DifficultyButton=AddButton(TEXT("DIFFICULTY: NORMAL (CHANGE & RESTART)")); DifficultyButton->OnClicked.AddDynamic(this,&UScintillaHUD::ChangeDifficulty);
    NormalButton=AddButton(TEXT("NORMAL / 8 ATTEMPTS")); NormalButton->OnClicked.AddDynamic(this,&UScintillaHUD::ChooseNormal);
    HardButton=AddButton(TEXT("HARD / 5 ATTEMPTS")); HardButton->OnClicked.AddDynamic(this,&UScintillaHUD::ChooseHard);
    HardcoreButton=AddButton(TEXT("HARDCORE / 3 ATTEMPTS")); HardcoreButton->OnClicked.AddDynamic(this,&UScintillaHUD::ChooseHardcore);
    RestartButton=AddButton(TEXT("RESTART")); RestartButton->OnClicked.AddDynamic(this,&UScintillaHUD::Restart);
    QuitButton=AddButton(TEXT("QUIT")); QuitButton->OnClicked.AddDynamic(this,&UScintillaHUD::Quit);
    Menu->SetVisibility(ESlateVisibility::Collapsed);
    MenuBackdrop->SetVisibility(ESlateVisibility::Collapsed); MenuPanel->SetVisibility(ESlateVisibility::Collapsed);
    Refresh();
    return Super::RebuildWidget();
}
void UScintillaHUD::NativeConstruct() { Super::NativeConstruct(); Refresh(); }
UButton* UScintillaHUD::AddButton(const FString& Text)
{
    auto* Button=WidgetTree->ConstructWidget<UButton>();
    StyleButton(Button,Cyan);
    auto* Caption=Label(WidgetTree,NAME_None,20,FLinearColor(.8f,1,.95f)); Caption->SetText(FText::FromString(Text));
    Button->AddChild(Caption);
    auto* Box=WidgetTree->ConstructWidget<USizeBox>(); Box->SetHeightOverride(52); Box->AddChild(Button);
    auto* ButtonSlot=Menu->AddChildToVerticalBox(Box); ButtonSlot->SetPadding(FMargin(0,6));
    return Button;
}
void UScintillaHUD::Refresh()
{
    if (!HealthLabel) return;
    RatingPanel->SetVisibility(ESlateVisibility::Collapsed); ContinueButton->SetVisibility(ESlateVisibility::Collapsed);
    DifficultyButton->SetVisibility(PausedMenu && !PauseChoosing && !DifficultyChoosing ? ESlateVisibility::Visible : ESlateVisibility::Collapsed);
    for(auto* B:{NormalButton.Get(),HardButton.Get(),HardcoreButton.Get()}) B->SetVisibility(DifficultyChoosing ? ESlateVisibility::Visible : ESlateVisibility::Collapsed);
    auto* P=Cast<AScintillaPlayer>(GetOwningPlayerPawn());
    auto* GS=GetWorld()->GetGameState<AScintillaGameState>();
    if (P)
    {
        HealthLabel->SetText(FText::FromString(FString::Printf(TEXT("INTEGRITY  %02d / %02d"),P->Health->CurrentHealth,P->Health->MaxHealth)));
        for(int32 Cell=0;Cell<HealthCells.Num();++Cell)
            HealthCells[Cell]->SetBrushColor(Cell<P->Health->CurrentHealth ? (P->Health->CurrentHealth==1 ? Amber : Cyan) : FLinearColor(.12f,.17f,.2f));
    }
    if (GS)
    {
        const TCHAR* Mode=GS->Difficulty==2 ? TEXT("HARDCORE") : GS->Difficulty==1 ? TEXT("HARD") : TEXT("NORMAL");
        AttemptsLabel->SetText(FText::FromString(FString::Printf(TEXT("%s  |  ATTEMPTS %d / %d"),Mode,FMath::Max(0,GS->AttemptLimit()-GS->Deaths),GS->AttemptLimit())));
        if(auto* Caption=Cast<UTextBlock>(DifficultyButton->GetChildAt(0))) Caption->SetText(FText::FromString(FString::Printf(TEXT("DIFFICULTY: %s (CHANGE & RESTART)"),Mode)));
        EnergyLabel->SetText(FText::FromString(FString::Printf(TEXT("ENERGY  %d / %d"),GS->Energy,GS->TotalEnergy)));
        EnergyMeter->SetPercent(GS->TotalEnergy>0 ? float(GS->Energy)/GS->TotalEnergy : 0);
        const int32 District=ScintillaCampaign::Index(this);
        CheckpointLabel->SetText(FText::FromString(FString::Printf(TEXT("%d / %d - %s | %s"),District+1,ScintillaCampaign::Count,ScintillaCampaign::Titles[District],GS->HasCheckpoint ? TEXT("Checkpoint active") : TEXT("Reach the generator"))));
        if(DifficultyChoosing)
        {
            Message->SetText(FText::FromString(TEXT("CHOOSE DIFFICULTY\nChanging restarts this level")));
            ResumeButton->SetVisibility(ESlateVisibility::Collapsed); RestartButton->SetVisibility(ESlateVisibility::Collapsed); QuitButton->SetVisibility(ESlateVisibility::Collapsed);
            ChooseLevelButton->SetVisibility(ESlateVisibility::Visible);
            if(auto* Caption=Cast<UTextBlock>(ChooseLevelButton->GetChildAt(0))) Caption->SetText(FText::FromString(TEXT("BACK TO PAUSE")));
            return;
        }
        if (auto* Caption=Cast<UTextBlock>(RestartButton->GetChildAt(0)))
            Caption->SetText(FText::FromString(GS->Completed ? TEXT("REPLAY THIS LEVEL") : TEXT("RESTART")));
        if (GS->Completed || PauseChoosing)
        {
            if(GS->Completed && !GS->RestorationReady)
            {
                Menu->SetVisibility(ESlateVisibility::Collapsed); LevelChooser->SetVisibility(ESlateVisibility::Collapsed);
                MenuBackdrop->SetVisibility(ESlateVisibility::Collapsed); MenuPanel->SetVisibility(ESlateVisibility::Collapsed);
                Message->SetText(FText::GetEmpty());
                CinematicCaption->SetVisibility(ESlateVisibility::HitTestInvisible);
                CinematicCaption->SetText(FText::FromString(GS->RestorationElapsed<4.7f ? TEXT("THE HEART OF THE CITY BEATS AGAIN\nRestoration in progress...") : TEXT("FROM RUST TO LIGHT")));
                return;
            }
            CinematicCaption->SetVisibility(ESlateVisibility::Collapsed);
            if(GS->Completed && !GS->RatingDismissed)
            {
                auto Clock=[](float Seconds) { const int32 T=FMath::Max(0,FMath::FloorToInt(Seconds)); return FString::Printf(TEXT("%02d:%02d"),T/60,T%60); };
                if(auto* RatingPanelSlot=Cast<UCanvasPanelSlot>(MenuPanel->Slot)) RatingPanelSlot->SetSize(FVector2D(840,700));
                if(auto* RatingMessageSlot=Cast<UCanvasPanelSlot>(Message->Slot)) RatingMessageSlot->SetPosition(FVector2D(0,-285));
                if(auto* RatingMenuSlot=Cast<UCanvasPanelSlot>(Menu->Slot)) RatingMenuSlot->SetPosition(FVector2D(0,-190));
                Message->SetText(FText::FromString(TEXT("DISTRICT RESTORED\nMISSION RATING")));
                RatingLetter->SetText(FText::FromString(GS->RatingGrade));
                RatingLetter->SetColorAndOpacity(FSlateColor(GS->RatingGrade==TEXT("S") ? Amber : GS->RatingGrade==TEXT("A") ? Cyan : GS->RatingGrade==TEXT("B") ? FLinearColor(.35f,.92f,.55f) : FLinearColor(.88f,.95f,1)));
                RatingTotal->SetText(FText::FromString(FString::Printf(TEXT("SCORE  %d / 100"),FMath::FloorToInt(GS->RatingScore))));
                RatingDetails->SetText(FText::FromString(FString::Printf(TEXT("\nTIME  %s  |  TARGET  %s\nDAMAGE TAKEN  %d\nENERGY  %d / %d\n\nSPEED %d/40  |  INTEGRITY %d/30  |  COLLECTION %d/30\n"),*Clock(GS->RunSeconds),*Clock(GS->RatingTargetSeconds),GS->DamageTaken,GS->Energy,GS->TotalEnergy,FMath::FloorToInt(GS->SpeedPoints),FMath::FloorToInt(GS->DamagePoints),FMath::FloorToInt(GS->EnergyPoints))));
                MenuBackdrop->SetVisibility(ESlateVisibility::HitTestInvisible); MenuPanel->SetVisibility(ESlateVisibility::HitTestInvisible);
                Menu->SetVisibility(ESlateVisibility::Visible); RatingPanel->SetVisibility(ESlateVisibility::Visible);
                LevelChooser->SetVisibility(ESlateVisibility::Collapsed); ContinueButton->SetVisibility(ESlateVisibility::Visible);
                ResumeButton->SetVisibility(ESlateVisibility::Collapsed); ChooseLevelButton->SetVisibility(ESlateVisibility::Collapsed); RestartButton->SetVisibility(ESlateVisibility::Collapsed);
                QuitButton->SetVisibility(ESlateVisibility::Collapsed); return;
            }
            if (auto* MessageSlot=Cast<UCanvasPanelSlot>(Message->Slot)) MessageSlot->SetPosition(FVector2D(0,-335));
            if (auto* PanelSlot=Cast<UCanvasPanelSlot>(MenuPanel->Slot)) PanelSlot->SetSize(FVector2D(840,820));
            Message->SetText(FText::FromString(FString::Printf(TEXT("%s\nChoose your next district"),District==ScintillaCampaign::Count-1 ? TEXT("CITY RESTORED") : TEXT("DISTRICT RESTORED"))));
            if(PauseChoosing) Message->SetText(FText::FromString(TEXT("CHOOSE DISTRICT\nUnlocked levels only")));
            if (auto* MenuSlot=Cast<UCanvasPanelSlot>(Menu->Slot)) MenuSlot->SetPosition(FVector2D(0,-235));
            MenuBackdrop->SetVisibility(ESlateVisibility::HitTestInvisible); MenuPanel->SetVisibility(ESlateVisibility::HitTestInvisible);
            LevelChooser->SetVisibility(ESlateVisibility::Visible);
            auto* PC=Cast<AScintillaController>(GetOwningPlayer());
            for (int32 Index=0;Index<LevelButtons.Num();++Index)
            {
                const bool Unlocked=PC && PC->IsLevelUnlocked(Index);
                LevelButtons[Index]->SetIsEnabled(Unlocked);
                StyleButton(LevelButtons[Index],DistrictColors[Index],Unlocked);
                const FString Status=Unlocked ? (PC->IsLevelCompleted(Index) ? TEXT("COMPLETED - REPLAY") : TEXT("AVAILABLE")) : FString::Printf(TEXT("LOCKED: complete level %d"),Index);
                LevelCaptions[Index]->SetColorAndOpacity(FSlateColor(Unlocked ? DistrictColors[Index] : FLinearColor(.5f,.55f,.6f)));
                LevelCaptions[Index]->SetText(FText::FromString(FString::Printf(TEXT("%02d / %s\n%s"),Index+1,ScintillaCampaign::Titles[Index],*Status)));
            }
            Menu->SetVisibility(ESlateVisibility::Visible);
            ResumeButton->SetVisibility(PauseChoosing ? ESlateVisibility::Visible : ESlateVisibility::Collapsed);
            ChooseLevelButton->SetVisibility(PauseChoosing ? ESlateVisibility::Visible : ESlateVisibility::Collapsed);
            if(auto* Caption=Cast<UTextBlock>(ChooseLevelButton->GetChildAt(0))) Caption->SetText(FText::FromString(TEXT("BACK TO PAUSE")));
            RestartButton->SetVisibility(PauseChoosing ? ESlateVisibility::Collapsed : ESlateVisibility::Visible);
            QuitButton->SetVisibility(PauseChoosing ? ESlateVisibility::Collapsed : ESlateVisibility::Visible);
            return;
        }
    }
    if (auto* MessageSlot=Cast<UCanvasPanelSlot>(Message->Slot)) MessageSlot->SetPosition(FVector2D(0,-235));
    if (PausedMenu) Message->SetText(FText::FromString(TEXT("SYSTEM ON STANDBY\nPAUSED")));
    else Message->SetText(FText::FromString(P && P->Health->IsDead() ? (GS && GS->Deaths>=GS->AttemptLimit() ? TEXT("ATTEMPTS EXHAUSTED\nRestarting level...") : TEXT("SCINTILLA OFFLINE\nRebooting...")) : TEXT("")));
}
void UScintillaHUD::NativeTick(const FGeometry& Geometry,float Dt)
{ Super::NativeTick(Geometry,Dt); Refresh(); }
FReply UScintillaHUD::NativeOnKeyDown(const FGeometry& Geometry,const FKeyEvent& Event)
{
    if (PausedMenu && (Event.GetKey()==EKeys::U || Event.GetKey()==EKeys::Gamepad_Special_Right))
    { Resume(); return FReply::Handled(); }
    return Super::NativeOnKeyDown(Geometry,Event);
}
void UScintillaHUD::ShowPause(bool Value)
{
    LevelChooser->SetVisibility(ESlateVisibility::Collapsed);
    PauseChoosing=false; DifficultyChoosing=false;
    if (auto* MenuSlot=Cast<UCanvasPanelSlot>(Menu->Slot)) MenuSlot->SetPosition(FVector2D(0,-110));
    if (auto* PanelSlot=Cast<UCanvasPanelSlot>(MenuPanel->Slot)) PanelSlot->SetSize(FVector2D(840,Value ? 600 : 820));
    MenuBackdrop->SetVisibility(Value ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
    MenuPanel->SetVisibility(Value ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
    PausedMenu=Value; Menu->SetVisibility(Value ? ESlateVisibility::Visible : ESlateVisibility::Collapsed);
    ResumeButton->SetVisibility(ESlateVisibility::Visible); Refresh();
    ChooseLevelButton->SetVisibility(Value ? ESlateVisibility::Visible : ESlateVisibility::Collapsed);
    if(auto* Caption=Cast<UTextBlock>(ChooseLevelButton->GetChildAt(0))) Caption->SetText(FText::FromString(TEXT("CHOOSE LEVEL")));
    RestartButton->SetVisibility(ESlateVisibility::Visible); QuitButton->SetVisibility(ESlateVisibility::Visible);
    if (Value) ResumeButton->SetKeyboardFocus();
}
void UScintillaHUD::OpenLevelChooser()
{
    auto* PC=Cast<AScintillaController>(GetOwningPlayer());
    if(!PC || !PC->IsPaused()) return;
    if(DifficultyChoosing) { ShowPause(true); return; }
    if(PauseChoosing) { ShowPause(true); return; }
    PauseChoosing=true; Refresh();
    if(LevelButtons.IsValidIndex(ScintillaCampaign::Index(this))) LevelButtons[ScintillaCampaign::Index(this)]->SetUserFocus(PC);
}
void UScintillaHUD::FocusRestart()
{
    if (auto* PC=Cast<AScintillaController>(GetOwningPlayer()))
    {
        if(IsRatingVisible()) { ContinueButton->SetUserFocus(PC); return; }
        const int32 Preferred=FMath::Min(ScintillaCampaign::Index(this)+1,PC->GetHighestUnlockedLevel());
        if (LevelButtons.IsValidIndex(Preferred) && LevelButtons[Preferred]->GetIsEnabled())
        { LevelButtons[Preferred]->SetUserFocus(PC); return; }
    }
    if (RestartButton) RestartButton->SetUserFocus(GetOwningPlayer());
}
bool UScintillaHUD::IsRatingVisible() const { return RatingPanel && RatingPanel->GetVisibility()==ESlateVisibility::Visible; }
void UScintillaHUD::ContinueRating() { if(auto* PC=Cast<AScintillaController>(GetOwningPlayer())) PC->ContinueFromRating(); }
void UScintillaHUD::ChangeDifficulty()
{ OpenDifficultyChooser(); }
void UScintillaHUD::OpenDifficultyChooser()
{ if(PausedMenu && !PauseChoosing) { DifficultyChoosing=true; Refresh(); NormalButton->SetKeyboardFocus(); } }
void UScintillaHUD::ChooseNormal() { if(auto* PC=Cast<AScintillaController>(GetOwningPlayer())) PC->SetDifficulty(0); }
void UScintillaHUD::ChooseHard() { if(auto* PC=Cast<AScintillaController>(GetOwningPlayer())) PC->SetDifficulty(1); }
void UScintillaHUD::ChooseHardcore() { if(auto* PC=Cast<AScintillaController>(GetOwningPlayer())) PC->SetDifficulty(2); }
bool UScintillaHUD::IsLevelChoiceEnabled(int32 Index) const
{ return LevelButtons.IsValidIndex(Index) && LevelButtons[Index]->GetIsEnabled(); }
void UScintillaHUD::ChooseOfficina() { if (auto* PC=Cast<AScintillaController>(GetOwningPlayer())) PC->SelectLevel(0); }
void UScintillaHUD::ChooseFonderia() { if (auto* PC=Cast<AScintillaController>(GetOwningPlayer())) PC->SelectLevel(1); }
void UScintillaHUD::ChooseCondotte() { if (auto* PC=Cast<AScintillaController>(GetOwningPlayer())) PC->SelectLevel(2); }
void UScintillaHUD::ChooseTorre() { if (auto* PC=Cast<AScintillaController>(GetOwningPlayer())) PC->SelectLevel(3); }
void UScintillaHUD::ChooseCryo() { if (auto* PC=Cast<AScintillaController>(GetOwningPlayer())) PC->SelectLevel(4); }
void UScintillaHUD::ChooseScrap() { if (auto* PC=Cast<AScintillaController>(GetOwningPlayer())) PC->SelectLevel(5); }
void UScintillaHUD::ChooseSolar() { if (auto* PC=Cast<AScintillaController>(GetOwningPlayer())) PC->SelectLevel(6); }
void UScintillaHUD::ChooseBio() { if (auto* PC=Cast<AScintillaController>(GetOwningPlayer())) PC->SelectLevel(7); }
void UScintillaHUD::Resume() { if (auto* PC=Cast<AScintillaController>(GetOwningPlayer())) PC->ResumeGame(); }
void UScintillaHUD::Restart() { if (auto* PC=Cast<AScintillaController>(GetOwningPlayer())) PC->RestartPrototype(); }
void UScintillaHUD::Quit() { if (auto* PC=Cast<AScintillaController>(GetOwningPlayer())) PC->QuitGame(); }
AScintillaController::AScintillaController() { HUDClass=UScintillaHUD::StaticClass(); }
void AScintillaController::LoadInputAssets()
{
    auto Load=[this](const TCHAR* Name) { return LoadObject<UInputAction>(nullptr,*FString::Printf(TEXT("/Game/Platformer/Input/IA_%s.IA_%s"),Name,Name)); };
    if (!MoveAction) MoveAction=Load(TEXT("Move"));
    if (!JumpAction) JumpAction=Load(TEXT("Jump"));
    if (!AttackAction) AttackAction=Load(TEXT("Attack"));
    if (!InteractAction) InteractAction=Load(TEXT("Interact"));
    if (!PauseAction) PauseAction=Load(TEXT("Pause"));
    if (!MappingContext) MappingContext=LoadObject<UInputMappingContext>(nullptr,TEXT("/Game/Platformer/Input/IMC_Platformer.IMC_Platformer"));
}
void AScintillaController::SetupInputComponent()
{
    Super::SetupInputComponent(); LoadInputAssets();
    if (auto* EIC=Cast<UEnhancedInputComponent>(InputComponent))
        if (PauseAction) EIC->BindAction(PauseAction,ETriggerEvent::Started,this,&AScintillaController::TogglePause);
}
void AScintillaController::BeginPlay()
{
    Super::BeginPlay(); LoadInputAssets(); LoadProgress();
    if(auto* GS=GetWorld()->GetGameState<AScintillaGameState>()) GS->Difficulty=FMath::Clamp(Progress->Difficulty,0,2);
    if (auto* Local=GetLocalPlayer())
        if (auto* Subsystem=Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
            if (MappingContext) Subsystem->AddMappingContext(MappingContext,0);
    HUD=CreateWidget<UScintillaHUD>(this,HUDClass);
    if (HUD) HUD->AddToViewport();
    bShowMouseCursor=false; SetInputMode(FInputModeGameOnly());
    if (FParse::Param(FCommandLine::Get(),TEXT("ScintillaSmoke")) || FParse::Param(FCommandLine::Get(),TEXT("ScintillaRoute")) || FParse::Param(FCommandLine::Get(),TEXT("ScintillaCampaignSmoke")) || FParse::Param(FCommandLine::Get(),TEXT("ScintillaProgressionSmoke"))) GetWorld()->SpawnActor<AScintillaPlaytest>();
}
void AScintillaController::TogglePause()
{
    auto* GS=GetWorld()->GetGameState<AScintillaGameState>();
    if (GS && GS->Completed) return;
    if (IsPaused()) { ResumeGame(); return; }
    SetPause(true); bShowMouseCursor=true;
    if (auto* P=Cast<AScintillaPlayer>(GetPawn())) P->MoveAxis(0);
    if (HUD) { FInputModeGameAndUI Mode; Mode.SetWidgetToFocus(HUD->TakeWidget()); SetInputMode(Mode); HUD->ShowPause(true); }
}
void AScintillaController::ResumeGame()
{
    SetPause(false); bShowMouseCursor=false;
    SetInputMode(FInputModeGameOnly());
    if (HUD) HUD->ShowPause(false);
}
void AScintillaController::RestartPrototype()
{
    SetPause(false);
    UGameplayStatics::OpenLevel(this,FName(*UGameplayStatics::GetCurrentLevelName(this,true)));
}
void AScintillaController::SetDifficulty(int32 Value)
{
    auto* GS=GetWorld()->GetGameState<AScintillaGameState>();
    if(!Progress || !GS || GS->Completed || !IsPaused() || Value<0 || Value>2) return;
    Progress->Difficulty=Value;
    UGameplayStatics::SaveGameToSlot(Progress,ProgressSlot(),0);
    RestartPrototype();
}
void AScintillaController::QuitGame()
{
    SetPause(false);
    // QuitGame stops the PIE game session; it does not close the Unreal Editor.
    UKismetSystemLibrary::QuitGame(this,this,EQuitPreference::Quit,false);
}
void AScintillaController::ShowCompletion()
{
    const auto* GS=GetWorld()->GetGameState<AScintillaGameState>();
    if (!GS || !GS->Completed) return;
    const int32 Current=ScintillaCampaign::Index(this);
    if (!CompletionSaved && IsLevelUnlocked(Current))
    {
        Progress->CompletedLevels|=1<<Current;
        Progress->HighestUnlocked=FMath::Max(Progress->HighestUnlocked,FMath::Min(Current+1,ScintillaCampaign::Count-1));
        if (!UGameplayStatics::SaveGameToSlot(Progress,ProgressSlot(),0))
            UE_LOG(LogTemp,Warning,TEXT("Campaign progress could not be saved"));
        CompletionSaved=true;
    }
    if(!GS->RestorationReady) return;
    bShowMouseCursor=true;
    if (HUD) { HUD->Refresh(); FInputModeUIOnly Mode; Mode.SetWidgetToFocus(HUD->TakeWidget()); SetInputMode(Mode); HUD->FocusRestart(); }
}
void AScintillaController::RefreshHUD() { if (HUD) HUD->Refresh(); }
void AScintillaController::ContinueFromRating()
{
    auto* GS=GetWorld()->GetGameState<AScintillaGameState>();
    if(!GS || !GS->Completed || !GS->RestorationReady || GS->RatingDismissed) return;
    GS->RatingDismissed=true;
    if(HUD) { HUD->Refresh(); HUD->FocusRestart(); }
}
FString AScintillaController::ProgressSlot() const
{
    // Automated fixtures have their own saves and never unlock the user's campaign.
    FString TestSlot;
    const bool Test=FParse::Param(FCommandLine::Get(),TEXT("ScintillaSmoke")) || FParse::Param(FCommandLine::Get(),TEXT("ScintillaRoute")) || FParse::Param(FCommandLine::Get(),TEXT("ScintillaCampaignSmoke")) || FParse::Param(FCommandLine::Get(),TEXT("ScintillaProgressionSmoke"));
    if (Test && FParse::Value(FCommandLine::Get(),TEXT("ScintillaProgressSlot="),TestSlot)) return TestSlot;
    return Test ? TEXT("ScintillaCampaign_Automation") : TEXT("ScintillaCampaign");
}
void AScintillaController::LoadProgress()
{
    Progress=Cast<UScintillaProgress>(UGameplayStatics::LoadGameFromSlot(ProgressSlot(),0));
    if (!Progress) Progress=Cast<UScintillaProgress>(UGameplayStatics::CreateSaveGameObject(UScintillaProgress::StaticClass()));
    Progress->HighestUnlocked=FMath::Clamp(Progress->HighestUnlocked,0,ScintillaCampaign::Count-1);
    Progress->CompletedLevels&=(1<<ScintillaCampaign::Count)-1;
    // A save that finished the original campaign can immediately enter Cryo Labs.
    if (Progress->HighestUnlocked==3 && (Progress->CompletedLevels & (1<<3))!=0)
        Progress->HighestUnlocked=4;
    // Existing district fixture tests enter maps directly instead of playing earlier ones.
    if (FParse::Param(FCommandLine::Get(),TEXT("ScintillaCampaignSmoke")) || FParse::Param(FCommandLine::Get(),TEXT("ScintillaRestorationSmoke")))
    {
        int32 Start=2; FParse::Value(FCommandLine::Get(),TEXT("ScintillaStartLevel="),Start);
        Progress->HighestUnlocked=FMath::Max(Progress->HighestUnlocked,FMath::Clamp(Start-1,0,ScintillaCampaign::Count-1));
    }
}
int32 AScintillaController::GetHighestUnlockedLevel() const { return Progress ? Progress->HighestUnlocked : 0; }
bool AScintillaController::IsLevelUnlocked(int32 Index) const
{ return Index>=0 && Index<ScintillaCampaign::Count && Index<=GetHighestUnlockedLevel(); }
bool AScintillaController::IsLevelCompleted(int32 Index) const
{ return Index>=0 && Index<ScintillaCampaign::Count && Progress && (Progress->CompletedLevels & (1<<Index))!=0; }
bool AScintillaController::SelectLevel(int32 Index)
{
    const auto* GS=GetWorld()->GetGameState<AScintillaGameState>();
    const bool FromPause=GS && !GS->Completed && IsPaused() && HUD && HUD->IsPauseLevelChooserOpen();
    if (!GS || (!FromPause && (!GS->Completed || !GS->RestorationReady || !GS->RatingDismissed)) || !IsLevelUnlocked(Index)) return false;
    SetPause(false);
    UGameplayStatics::OpenLevel(this,FName(*ScintillaCampaign::MapPath(Index)));
    return true;
}
