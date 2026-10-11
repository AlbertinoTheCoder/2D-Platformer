using UnrealBuildTool;
using System.Collections.Generic;
public class Platformer_2D_GameTarget : TargetRules
{
    public Platformer_2D_GameTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;
        ExtraModuleNames.Add("Scintilla");
    }
}
