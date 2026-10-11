"""Update only the keyboard pause mapping, preserving all movement modifiers."""
import unreal,json
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
lib=unreal.EditorAssetLibrary
path='/Game/Platformer/Input/IMC_Platformer'; backup=path+'_BeforePauseU'
if not lib.does_asset_exist(backup): lib.duplicate_asset(path,backup)
context=lib.load_asset(path); action=lib.load_asset('/Game/Platformer/Input/IA_Pause')
data=context.get_editor_property('default_key_mappings'); mappings=list(data.get_editor_property('mappings'))
changed=0
for mapping in mappings:
    if mapping.get_editor_property('action')==action and str(mapping.get_editor_property('key').get_editor_property('key_name'))=='Escape':
        key=unreal.Key(); key.set_editor_property('key_name','U'); mapping.set_editor_property('key',key); changed+=1
data.set_editor_property('mappings',mappings); context.set_editor_property('default_key_mappings',data)
action.set_editor_property('trigger_when_paused',True)
keys=[str(m.get_editor_property('key').get_editor_property('key_name')) for m in mappings if m.get_editor_property('action')==action]
if 'U' not in keys or 'Escape' in keys: raise RuntimeError(keys)
lib.save_loaded_asset(context,False); lib.save_loaded_asset(action,False)
(ROOT/'Assets/UI/pause_input_report.json').write_text(json.dumps({'keys':keys,'changed':changed,'saved':True},indent=2))
print('PAUSE_INPUT_U_OK',keys)
