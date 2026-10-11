"""Verify the complete restoration, camera and delayed chooser on all eight maps."""
import json,subprocess,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
project=ROOT/'Platformer_2D_Game/Platformer_2D_Game.uproject'; saved=project.parent/'Saved'
reports=[]
for cfg in json.loads((ROOT/'Config/campaign.json').read_text())['levels']:
    n=cfg['index']; report=saved/'ScintillaRestoration.json'
    if report.exists(): report.unlink()
    subprocess.run(['E:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe',str(project),
        '/Game/Platformer/Levels/'+cfg['name'],'-game','-ScintillaSmoke','-ScintillaRestorationSmoke',
        f'-ScintillaStartLevel={n}',f'-ScintillaProgressSlot=Restoration_{uuid.uuid4().hex}',
        '-nullrhi','-nosound','-unattended','-nosplash','-ExecCmds=t.MaxFPS 60',
        f'-abslog={saved}/Logs/Restoration{n}.log'],check=True,timeout=90,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
    data=json.loads(report.read_text(encoding='utf-8-sig')); reports.append({'level':n,**data})
    (ROOT/'Assets/Models/City/runtime_report.json').write_text(json.dumps(reports,indent=2))
    print('RESTORATION_TEST',n,len(data['checks']),'checks',data['failures'],'failures',flush=True)
    if data['failures']: raise SystemExit(1)
