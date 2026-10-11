"""Capture each live hazard, then leave a fresh normal game running."""
import json,base64,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; saved=ROOT/'Platformer_2D_Game/Saved'
sys.argv=['capture_difficulty','noop']
from ui_editor import call
save=saved/'SaveGames/ScintillaCampaign.sav'; original=save.read_bytes() if save.exists() else None
def capture(name):
    r=call('EditorToolset.EditorAppToolset','CaptureEditorImage')['returnValue']
    (ROOT/'Assets/Models/Difficulty'/name).write_bytes(base64.b64decode(r['data']))
try:
    if not call('EditorToolset.EditorAppToolset','IsPIERunning')['returnValue']: call('EditorToolset.EditorAppToolset','StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
    for kind in ['WIND','FALLING_SPIKES','ICE','RISING_SPIKES','HAMMER','AXE']:
        marker=saved/'DifficultyPreviewResult.json'; marker.unlink(missing_ok=True)
        (saved/'DifficultyPreview.json').write_text(json.dumps({'kind':kind}))
        subprocess.run([sys.executable,str(ROOT/'Scripts/ui_editor.py'),'console','Scripts/preview_difficulty.py'],check=True,stdout=subprocess.DEVNULL)
        deadline=time.monotonic()+25
        while not marker.exists() and time.monotonic()<deadline: time.sleep(.2)
        if not marker.exists(): raise RuntimeError('Preview failed: '+kind)
        capture(kind.lower()+'.png')
    print('DIFFICULTY_LIVE_CAPTURES_OK')
finally:
    if call('EditorToolset.EditorAppToolset','IsPIERunning')['returnValue']: call('EditorToolset.EditorAppToolset','StopPIE')
    if original is not None: save.write_bytes(original)
    elif save.exists(): save.unlink()
    call('EditorToolset.EditorAppToolset','StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
