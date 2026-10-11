"""Test sequential unlocks, persistence and chosen-map travel in isolated saves."""
import json, subprocess, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
project=ROOT/'Platformer_2D_Game/Platformer_2D_Game.uproject'
saved=project.parent/'Saved'
slot='ScintillaProgression_Test_'+uuid.uuid4().hex
maps=['L_Platformer_Prototype','L_02_Fonderia','L_Platformer_Prototype','L_03_Condotte','L_Platformer_Prototype','L_04_Torre','L_Platformer_Prototype','L_05_Cryo','L_Platformer_Prototype','L_06_Scrap','L_Platformer_Prototype','L_07_Solar','L_Platformer_Prototype','L_08_Bio']
reports=[]
for step,name in enumerate(maps):
    report=saved/f'ScintillaProgression{step}.json'
    if report.exists(): report.unlink()
    subprocess.run(['E:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe',str(project),
        '/Game/Platformer/Levels/'+name,'-game','-ScintillaProgressionSmoke',
        f'-ScintillaProgressionStep={step}',f'-ScintillaProgressSlot={slot}',
        '-nullrhi','-nosound','-unattended','-nosplash','-ExecCmds=t.MaxFPS 60',
        f'-abslog={saved}/Logs/ScintillaProgression{step}.log'],check=True,timeout=120)
    result=json.loads(report.read_text(encoding='utf-8-sig'))
    reports.append({'step':step,'map':name,**result})
    print('PROGRESSION_STEP',step,'checks',len(result['checks']),'failures',result['failures'],flush=True)
    if result['failures']: break
output={'save_slot':slot,'failures':sum(r['failures'] for r in reports),'steps':reports}
target=ROOT/'Assets/Models/progression_test_report.json'
target.write_text(json.dumps(output,indent=2))
if output['failures'] or len(reports)!=len(maps): raise SystemExit(1)
