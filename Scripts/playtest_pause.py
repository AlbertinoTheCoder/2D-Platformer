"""Exercise actual U input, paused selector, locked buttons and replay/map travel."""
import json,subprocess,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; project=ROOT/'Platformer_2D_Game/Platformer_2D_Game.uproject'; saved=project.parent/'Saved'
reports=[]
for n,name in [(1,'L_Platformer_Prototype'),(2,'L_02_Fonderia')]:
    for p in [saved/'ScintillaPause.json',saved/f'PausePending{n}.txt']:
        if p.exists(): p.unlink()
    subprocess.run(['E:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe',str(project),'/Game/Platformer/Levels/'+name,
        '-game','-ScintillaSmoke','-ScintillaPauseSmoke','-ScintillaCampaignSmoke',f'-ScintillaStartLevel={n}',
        f'-ScintillaProgressSlot=Pause_{uuid.uuid4().hex}','-nullrhi','-nosound','-unattended','-nosplash',
        '-ExecCmds=t.MaxFPS 60',f'-abslog={saved}/Logs/Pause{n}.log'],check=True,timeout=90,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
    result=json.loads((saved/'ScintillaPause.json').read_text(encoding='utf-8-sig')); reports.append({'start_level':n,**result})
    (ROOT/'Assets/UI/pause_runtime_report.json').write_text(json.dumps(reports,indent=2))
    print('PAUSE_TEST',n,len(result['checks']),'checks',result['failures'],'failures',flush=True)
    if result['failures']: raise SystemExit(1)
