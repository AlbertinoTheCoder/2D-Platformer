"""Exercise hazard contacts, physics, difficulty persistence and real reset travel."""
import json,subprocess,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; project=ROOT/'Platformer_2D_Game/Platformer_2D_Game.uproject'; saved=project.parent/'Saved'
reports=[]
for cfg in json.loads((ROOT/'Config/campaign.json').read_text())['levels']:
    for name in ['ScintillaDifficulty.json','ScintillaDifficultyHard.json','ScintillaDifficultyHardcore.json','ScintillaDifficultyReset.json',f"DifficultyPending{cfg['index']-1}.txt"]:
        (saved/name).unlink(missing_ok=True)
    subprocess.run(['E:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe',str(project),'/Game/Platformer/Levels/'+cfg['name'],'-game','-ScintillaSmoke','-ScintillaDifficultySmoke',f'-ScintillaProgressSlot=Difficulty_{uuid.uuid4().hex}','-nullrhi','-nosound','-unattended','-nosplash','-ExecCmds=t.MaxFPS 60',f"-abslog={saved}/Logs/Difficulty{cfg['index']}.log"],check=True,timeout=150,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
    results=[json.loads((saved/n).read_text(encoding='utf-8-sig')) for n in ['ScintillaDifficulty.json','ScintillaDifficultyHard.json','ScintillaDifficultyHardcore.json','ScintillaDifficultyReset.json']]
    report={'level':cfg['index'],'failures':sum(r['failures'] for r in results),'checks':[c for r in results for c in r['checks']]}; reports.append(report)
    (ROOT/'Assets/Models/Difficulty/runtime_report.json').write_text(json.dumps(reports,indent=2))
    print('DIFFICULTY_TEST',cfg['index'],len(report['checks']),'checks',report['failures'],'failures',flush=True)
    if report['failures']: raise SystemExit(1)
