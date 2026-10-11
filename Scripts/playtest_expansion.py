"""Exercise all four new maps, their moving lifts, completion and real route traversal."""
import json,subprocess,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
project=ROOT/'Platformer_2D_Game/Platformer_2D_Game.uproject'; saved=project.parent/'Saved'
maps=['L_05_Cryo','L_06_Scrap','L_07_Solar','L_08_Bio']
reports=[]
for n,name in enumerate(maps,5):
    for mode in ('fixture','route'):
        report=saved/(f'ScintillaCampaign{n:02}.json' if mode=='fixture' else f'ScintillaExpansionRoute{n:02}.json')
        if report.exists(): report.unlink()
        args=['-ScintillaCampaignSmoke',f'-ScintillaStartLevel={n}'] if mode=='fixture' else ['-ScintillaRoute']
        subprocess.run(['E:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe',str(project),
            '/Game/Platformer/Levels/'+name,'-game',*args,f'-ScintillaProgressSlot=Expansion_{uuid.uuid4().hex}',
            '-nullrhi','-nosound','-unattended','-nosplash','-ExecCmds=t.MaxFPS 60',
            f'-abslog={saved}/Logs/Expansion{n}_{mode}.log'],check=True,timeout=150,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
        result=json.loads(report.read_text(encoding='utf-8-sig'))
        reports.append(dict(level=n,mode=mode,**result))
        (ROOT/'Assets/Models/Expansion/runtime_report.json').write_text(json.dumps(reports,indent=2))
        print('EXPANSION_TEST',n,mode,len(result['checks']),'checks',result['failures'],'failures',flush=True)
        if result['failures']: raise SystemExit(1)
