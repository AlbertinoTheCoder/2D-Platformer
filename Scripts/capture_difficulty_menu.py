"""Preview the difficulty chooser through its shared UI entry point, then resume."""
import json,base64,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.argv=['capture_difficulty_menu','noop']
from ui_editor import call
slate='SlateInspectorToolset.SlateInspectorToolset'
(ROOT/'Platformer_2D_Game/Saved/PausePreview.json').write_text(json.dumps({'phase':'pause'}))
subprocess.run([sys.executable,str(ROOT/'Scripts/ui_editor.py'),'console','Scripts/preview_pause.py'],check=True,stdout=subprocess.DEVNULL)
try:
    command="py import unreal; unreal.GameplayStatics.get_player_controller(unreal.EditorLevelLibrary.get_game_world(),0).get_editor_property('hud').open_difficulty_chooser()"
    subprocess.run([sys.executable,str(ROOT/'Scripts/ui_editor.py'),'console',command],check=True,stdout=subprocess.DEVNULL)
    time.sleep(.25)
    r=call('EditorToolset.EditorAppToolset','CaptureEditorImage')['returnValue']
    (ROOT/'Assets/Models/Difficulty/difficulty_menu.png').write_bytes(base64.b64decode(r['data']))
finally:
    call(slate,'PressKey',{'key':'U'})
print('DIFFICULTY_MENU_CAPTURED')
