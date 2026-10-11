"""Traverse the rebalanced final district on native ticks, without teleporting."""
import json,subprocess,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
project=ROOT/'Platformer_2D_Game/Platformer_2D_Game.uproject'
saved=project.parent/'Saved'; report=saved/'ScintillaTorreRoute.json'
if report.exists(): report.unlink()
subprocess.run(['E:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe',str(project),
    '/Game/Platformer/Levels/L_04_Torre','-game','-ScintillaRoute',f'-ScintillaProgressSlot=Torre_{uuid.uuid4().hex}','-nullrhi','-nosound','-unattended','-nosplash',
    '-ExecCmds=t.MaxFPS 60',f'-abslog={saved}/Logs/TorreTraversal.log'],check=True,timeout=120)
result=json.loads(report.read_text(encoding='utf-8-sig'))
(ROOT/'Assets/Models/torre_traversal.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
if result['failures']: raise SystemExit(1)
