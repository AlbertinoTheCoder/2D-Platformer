"""Capture all four poses in the live editor, then restore a fresh playable game."""
import subprocess,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def ui(*args): subprocess.run([sys.executable,str(ROOT/'Scripts/ui_editor.py'),*args],check=True)
ui('save'); ui('start')
for direction in ('Left','Right','Camera','City'):
    (ROOT/'Platformer_2D_Game/Saved/FacingPreview.json').write_text(json.dumps(dict(direction=direction)))
    result=ROOT/'Platformer_2D_Game/Saved/FacingPreviewResult.json'
    if result.exists(): result.unlink()
    ui('console','Scripts/preview_facing.py')
    deadline=time.monotonic()+5
    while not result.exists() and time.monotonic()<deadline: time.sleep(.1)
    if not result.exists() or json.loads(result.read_text())['direction']!=direction: raise RuntimeError('Facing preview did not complete: '+direction)
    ui('capture','facing_'+direction.lower())
ui('app','StopPIE'); ui('start')
