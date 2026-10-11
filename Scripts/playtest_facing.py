"""Verify the four facing directions, mirrored gait and unchanged movement plane."""
import subprocess,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
project=ROOT/'Platformer_2D_Game/Platformer_2D_Game.uproject'; saved=project.parent/'Saved'
report=saved/'ScintillaFacing.json'
if report.exists(): report.unlink()
subprocess.run(['E:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe',str(project),
 '/Game/Platformer/Levels/L_Platformer_Prototype','-game','-ScintillaSmoke','-ScintillaFacingSmoke',
 '-ScintillaProgressSlot=Scintilla_Facing_Automation','-nullrhi','-nosound','-unattended','-nosplash',
 '-ExecCmds=t.MaxFPS 60',f'-abslog={saved}/Logs/FacingIntegration.log'],check=True,timeout=120,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
result=json.loads(report.read_text(encoding='utf-8-sig'))
(ROOT/'Assets/Models/RobotRig/facing_report.json').write_text(json.dumps(result,indent=2))
print('FACING_TEST',len(result['checks']),'checks',result['failures'],'failures')
if result['failures']: raise SystemExit(1)
