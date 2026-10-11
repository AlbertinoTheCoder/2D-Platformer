using UnrealBuildTool;
using System.Collections.Generic;
public class Platformer_2D_GameEditorTarget : TargetRules
{
    public Platformer_2D_GameEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;
        ExtraModuleNames.Add("Scintilla");
    }
}
