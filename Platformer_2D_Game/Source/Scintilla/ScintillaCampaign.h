#pragma once
#include "Kismet/GameplayStatics.h"

namespace ScintillaCampaign
{
    inline constexpr int32 Count=8;
    inline constexpr float RatingTargets[]={100,110,115,120,125,130,135,140};
    inline constexpr const TCHAR* Maps[]={TEXT("L_Platformer_Prototype"),TEXT("L_02_Fonderia"),TEXT("L_03_Condotte"),TEXT("L_04_Torre"),TEXT("L_05_Cryo"),TEXT("L_06_Scrap"),TEXT("L_07_Solar"),TEXT("L_08_Bio")};
    inline constexpr const TCHAR* Titles[]={TEXT("WORKSHOP 07"),TEXT("FOUNDRY"),TEXT("PIPEWORKS"),TEXT("CENTRAL TOWER"),TEXT("CRYO LABS"),TEXT("SCRAP YARDS"),TEXT("SOLAR WORKS"),TEXT("BIO GARDENS")};
    inline int32 Index(const UObject* Context)
    {
        const FString Current=UGameplayStatics::GetCurrentLevelName(Context,true);
        for (int32 i=0;i<Count;++i) if (Current==Maps[i]) return i;
        return 0;
    }
    inline FString MapPath(int32 Index) { return FString(TEXT("/Game/Platformer/Levels/"))+Maps[Index]; }
    inline FString Next(const UObject* Context) { return MapPath((Index(Context)+1)%Count); }
}
