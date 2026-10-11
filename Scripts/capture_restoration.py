"""Capture actual PIE restoration stages and restore the user's saved progress afterward."""
import base64,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SAVED=ROOT/'Platformer_2D_Game/Saved'
sys.argv=['capture_restoration','noop']
from ui_editor import call
save=SAVED/'SaveGames/ScintillaCampaign.sav'; original=save.read_bytes() if save.exists() else None
try:
    for phase in ('before','repair','reveal','chooser'):
        if call('EditorToolset.EditorAppToolset','IsPIERunning')['returnValue']: call('EditorToolset.EditorAppToolset','StopPIE')
        marker=SAVED/'RestorationPreviewResult.json'
        if marker.exists(): marker.unlink()
        (SAVED/'RestorationPreview.json').write_text(json.dumps({'phase':phase}))
        call('EditorToolset.EditorAppToolset','StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
        subprocess.run([sys.executable,str(ROOT/'Scripts/ui_editor.py'),'console','Scripts/preview_restoration.py'],check=True,stdout=subprocess.DEVNULL)
        deadline=time.monotonic()+55
        while not marker.exists() and time.monotonic()<deadline: time.sleep(.3)
        if not marker.exists(): raise RuntimeError('Preview did not finish: '+phase)
        data=json.loads(marker.read_text()); assert data['phase']==phase,data
        time.sleep(.3)
        capture=call('EditorToolset.EditorAppToolset','CaptureEditorImage')['returnValue']
        (ROOT/'Assets/UI'/('city_'+phase+'.png')).write_bytes(base64.b64decode(capture['data']))
        print('CITY_CAPTURE',data,flush=True)
finally:
    if call('EditorToolset.EditorAppToolset','IsPIERunning')['returnValue']: call('EditorToolset.EditorAppToolset','StopPIE')
    if original is not None: save.write_bytes(original)
    elif save.exists(): save.unlink()
    call('EditorToolset.EditorAppToolset','StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
