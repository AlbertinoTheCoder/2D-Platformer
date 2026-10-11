"""Capture the rating popup and activate Continue through the real focused UI button."""
import base64,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; saved=ROOT/'Platformer_2D_Game/Saved'
sys.argv=['capture_rating','noop']
from ui_editor import call
save=saved/'SaveGames/ScintillaCampaign.sav'; original=save.read_bytes() if save.exists() else None
def capture(name):
    result=call('EditorToolset.EditorAppToolset','CaptureEditorImage')['returnValue']
    (ROOT/'Assets/UI'/name).write_bytes(base64.b64decode(result['data']))
try:
    if call('EditorToolset.EditorAppToolset','IsPIERunning')['returnValue']: call('EditorToolset.EditorAppToolset','StopPIE')
    marker=saved/'RestorationPreviewResult.json'
    if marker.exists(): marker.unlink()
    (saved/'RestorationPreview.json').write_text(json.dumps({'phase':'rating'}))
    call('EditorToolset.EditorAppToolset','StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
    subprocess.run([sys.executable,str(ROOT/'Scripts/ui_editor.py'),'console','Scripts/preview_restoration.py'],check=True,stdout=subprocess.DEVNULL)
    deadline=time.monotonic()+55
    while not marker.exists() and time.monotonic()<deadline: time.sleep(.3)
    if not marker.exists(): raise RuntimeError('Rating preview timed out')
    time.sleep(.3); capture('rating_popup.png')
    if not call('SlateInspectorToolset.SlateInspectorToolset','PressKey',{'key':'Enter'})['returnValue']: raise RuntimeError('Continue key failed')
    time.sleep(.5); capture('rating_continue_chooser.png')
    subprocess.run([sys.executable,str(ROOT/'Scripts/ui_editor.py'),'console','Scripts/verify_rating_continue.py'],check=True,stdout=subprocess.DEVNULL)
    result=json.loads((saved/'RatingContinueResult.json').read_text())
    assert result['dismissed'] and result['ready'],result
    (ROOT/'Assets/UI/rating_live_report.json').write_text(json.dumps(result,indent=2))
    print('RATING_CONTINUE_UI_OK',result,flush=True)
finally:
    if call('EditorToolset.EditorAppToolset','IsPIERunning')['returnValue']: call('EditorToolset.EditorAppToolset','StopPIE')
    if original is not None: save.write_bytes(original)
    elif save.exists(): save.unlink()
    call('EditorToolset.EditorAppToolset','StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
