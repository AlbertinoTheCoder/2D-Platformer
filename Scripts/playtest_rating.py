"""Check scoring factors, damage/time bookkeeping, rating popup and Continue gate."""
import json,subprocess,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; project=ROOT/'Platformer_2D_Game/Platformer_2D_Game.uproject'; saved=project.parent/'Saved'
report=saved/'ScintillaRating.json'
if report.exists(): report.unlink()
subprocess.run(['E:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe',str(project),'/Game/Platformer/Levels/L_Platformer_Prototype',
    '-game','-ScintillaSmoke','-ScintillaRatingSmoke',f'-ScintillaProgressSlot=Rating_{uuid.uuid4().hex}',
    '-nullrhi','-nosound','-unattended','-nosplash','-ExecCmds=t.MaxFPS 60',f'-abslog={saved}/Logs/Rating.log'],check=True,timeout=90,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
result=json.loads(report.read_text(encoding='utf-8-sig'))
(ROOT/'Assets/UI/rating_runtime_report.json').write_text(json.dumps(result,indent=2))
print('RATING_TEST',len(result['checks']),'checks',result['failures'],'failures')
if result['failures']: raise SystemExit(1)
