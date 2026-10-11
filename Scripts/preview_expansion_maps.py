"""Capture each new district in PIE, then leave Cryo Labs ready to play."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
selection=ROOT/'Platformer_2D_Game/Saved/ExpansionPreview.json'
def ui(*args):
    subprocess.run([sys.executable,str(ROOT/'Scripts/ui_editor.py'),*args],check=True)
ui('app','StopPIE')
for n,name in ((6,'scrap'),(7,'solar'),(8,'bio')):
    selection.write_text(json.dumps({'level':n}))
    ui('console','Scripts/open_expansion.py'); ui('start')
    ui('capture','expansion_'+name); ui('app','StopPIE')
    print('EXPANSION_VISUAL_CAPTURED',n,flush=True)
selection.write_text(json.dumps({'level':5}))
ui('console','Scripts/open_expansion.py'); ui('start')
print('EXPANSION_READY_TO_PLAY',flush=True)
