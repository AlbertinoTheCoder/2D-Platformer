"""Traverse Condotte on the native game tick, without editor callbacks."""
import json
import subprocess
import uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
project=ROOT/'Platformer_2D_Game/Platformer_2D_Game.uproject'
saved=project.parent/'Saved'
subprocess.run(['E:/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe',str(project),
    '/Game/Platformer/Levels/L_03_Condotte','-game','-ScintillaRoute',f'-ScintillaProgressSlot=Condotte_{uuid.uuid4().hex}','-nullrhi','-nosound','-unattended','-nosplash',
    '-ExecCmds=t.MaxFPS 60',f'-abslog={saved}/Logs/CondotteTraversal.log'],check=True)
report=json.loads((saved/'ScintillaCondotteRoute.json').read_text(encoding='utf-8-sig'))
(ROOT/'Assets/Models/condotte_traversal.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
if report['failures']: raise SystemExit(1)
