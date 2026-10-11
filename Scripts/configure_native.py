"""Configure this project's native module, preserving existing configuration."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "Platformer_2D_Game"
BACKUP = PROJECT / "Saved/ScintillaBackup/BeforeNative"


def set_ini(path, section, values):
    text = path.read_text(encoding="utf-8-sig") if path.exists() else ""
    lines = text.splitlines()
    header = f"[{section}]"
    if header not in lines:
        lines.extend(["", header])
    start = lines.index(header) + 1
    end = next((i for i in range(start, len(lines)) if lines[i].startswith("[")), len(lines))
    body = [line for line in lines[start:end] if line.split("=", 1)[0] not in values]
    lines[start:end] = body + [f"{key}={value}" for key, value in values.items()] + [""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    files = [PROJECT / "Platformer_2D_Game.uproject", PROJECT / "Config/DefaultEngine.ini", PROJECT / "Config/DefaultInput.ini"]
    BACKUP.mkdir(parents=True, exist_ok=True)
    for path in files:
        dest = BACKUP / path.name
        if path.exists() and not dest.exists():
            shutil.copy2(path, dest)
    descriptor = json.loads(files[0].read_text(encoding="utf-8-sig"))
    modules = descriptor.setdefault("Modules", [])
    if not any(m["Name"] == "Scintilla" for m in modules):
        modules.append({"Name": "Scintilla", "Type": "Runtime", "LoadingPhase": "Default"})
    plugins = descriptor.setdefault("Plugins", [])
    for name in ("Paper2D", "EnhancedInput", "PythonScriptPlugin", "EditorScriptingUtilities"):
        entry = next((p for p in plugins if p["Name"] == name), None)
        if entry is None:
            plugins.append({"Name": name, "Enabled": True})
        else:
            entry["Enabled"] = True
    files[0].write_text(json.dumps(descriptor, indent=2) + "\n", encoding="utf-8")
    set_ini(files[2], "/Script/Engine.InputSettings", {
        "DefaultPlayerInputClass": "/Script/EnhancedInput.EnhancedPlayerInput",
        "DefaultInputComponentClass": "/Script/EnhancedInput.EnhancedInputComponent",
    })
    set_ini(files[1], "/Script/EngineSettings.GameMapsSettings", {
        "EditorStartupMap": "/Game/Platformer/Levels/L_Platformer_Prototype",
        "GameDefaultMap": "/Game/Platformer/Levels/L_Platformer_Prototype",
        "GlobalDefaultGameMode": "/Game/Platformer/GameModes/BP_PlatformerGameMode.BP_PlatformerGameMode_C",
    })
    print("Native module configured. Original settings backed up in Saved/ScintillaBackup/BeforeNative.")


if __name__ == "__main__":
    main()
