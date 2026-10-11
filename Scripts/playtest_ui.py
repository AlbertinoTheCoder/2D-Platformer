"""Run the existing HUD/gameplay integration probe without changing player progress."""
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
project=ROOT/'Platformer_2D_Game/Platformer_2D_Game.uproject'
saved=project.parent/'Saved'
report=saved/'ScintillaPlaytest.json'
if report.exists(): report.unlink()
subprocess.run(['E:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe',str(project),
    '/Game/Platformer/Levels/L_Platformer_Prototype','-game','-ScintillaSmoke',
    '-ScintillaProgressSlot=Scintilla_UI_Automation','-nullrhi','-nosound','-unattended','-nosplash',
    '-ExecCmds=t.MaxFPS 60',f'-abslog={saved}/Logs/UIIntegration.log'],check=True,timeout=120)
result=json.loads(report.read_text(encoding='utf-8-sig'))
(ROOT/'Assets/UI/integration_report.json').write_text(json.dumps(result,indent=2))
print('UI_INTEGRATION',len(result['checks']),'checks',result['failures'],'failures')
if result['failures']: raise SystemExit(1)
