"""Read actual Slate references for the difficulty button."""
import json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.argv=['inspect','noop']
from ui_editor import call
if not call('EditorToolset.EditorAppToolset','IsPIERunning')['returnValue']: call('EditorToolset.EditorAppToolset','StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':1}})
(ROOT/'Platformer_2D_Game/Saved/PausePreview.json').write_text(json.dumps({'phase':'pause'}))
subprocess.run([sys.executable,str(ROOT/'Scripts/ui_editor.py'),'console','Scripts/preview_pause.py'],check=True,stdout=subprocess.DEVNULL)
slate='SlateInspectorToolset.SlateInspectorToolset'
call(slate,'Windows',{'action':'select','index':0}); observer=call(slate,'Observe',{'ref':'w1','maxDepth':45})['returnValue']
try:
    time.sleep(.2); s=call(slate,'Snapshot',{'ref':'w1','maxDepth':45})['returnValue']; (ROOT/'Platformer_2D_Game/Saved/DifficultySlate.txt').write_text(s)
    lines=s.splitlines()
    for i,line in enumerate(lines):
        if 'DIFFICULTY' in line: print('\n'.join(lines[max(0,i-3):i+2]))
finally: call(slate,'Unobserve',{'identifier':observer})
