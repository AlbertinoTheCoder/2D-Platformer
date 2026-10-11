"""Native integration checks for three Blender enemy bodies and their actual behaviors."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
project=ROOT/'Platformer_2D_Game/Platformer_2D_Game.uproject'; saved=project.parent/'Saved'
report=saved/'ScintillaEnemies.json'
if report.exists(): report.unlink()
subprocess.run(['E:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe',str(project),
 '/Game/Platformer/Levels/L_Platformer_Prototype','-game','-ScintillaSmoke','-ScintillaEnemiesSmoke',
 '-ScintillaProgressSlot=Scintilla_Enemies_Automation','-nullrhi','-nosound','-unattended','-nosplash',
 '-ExecCmds=t.MaxFPS 60',f'-abslog={saved}/Logs/EnemyIntegration.log'],check=True,timeout=120,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
result=json.loads(report.read_text(encoding='utf-8-sig'))
(ROOT/'Assets/Models/Enemies/runtime_report.json').write_text(json.dumps(result,indent=2))
print('ENEMY_TEST',len(result['checks']),'checks',result['failures'],'failures')
if result['failures']: raise SystemExit(1)
