"""Walk extended levels with real movement, attacks and native checkpoint respawns."""
import json,subprocess,uuid,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; project=ROOT/'Platformer_2D_Game/Platformer_2D_Game.uproject'; saved=project.parent/'Saved'; reports=[]
start=int(sys.argv[1]) if len(sys.argv)>1 else 1
if start>1:
    reports=[r for r in json.loads((ROOT/'Assets/Models/Difficulty/traversal_report.json').read_text()) if r['level']<start and r['failures']==0]
for cfg in json.loads((ROOT/'Config/campaign.json').read_text())['levels']:
    n=cfg['index']
    if n<start: continue
    # The original second map shares the prototype route controller.
    filename=f'ScintillaExpansionRoute{n:02}.json' if n>=5 else 'ScintillaTorreRoute.json' if n==4 else 'ScintillaCondotteRoute.json' if n==3 else 'ScintillaRoute.json'
    (saved/filename).unlink(missing_ok=True)
    subprocess.run(['E:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe',str(project),'/Game/Platformer/Levels/'+cfg['name'],'-game','-ScintillaRoute',f'-ScintillaProgressSlot=DifficultyRoute_{uuid.uuid4().hex}','-nullrhi','-nosound','-unattended','-nosplash','-ExecCmds=t.MaxFPS 60',f'-abslog={saved}/Logs/DifficultyRoute{n}.log'],check=True,timeout=240,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
    result=json.loads((saved/filename).read_text(encoding='utf-8-sig')); reports.append({'level':n,**result})
    (ROOT/'Assets/Models/Difficulty/traversal_report.json').write_text(json.dumps(reports,indent=2))
    print('DIFFICULTY_ROUTE',n,'failures',result['failures'],flush=True)
    if result['failures']: raise SystemExit(1)
