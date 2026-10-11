"""Update the eight animation clips on the existing skeleton, with recovery copies."""
import unreal
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
exec((ROOT/'Scripts/import_robot_rig.py').read_text().split("mesh=import_fbx('SK_Scintilla')")[0],globals())
mesh=lib.load_asset(BASE+'/SK_Scintilla'); skeleton=mesh.get_editor_property('skeleton')
for name in ('Idle','Run','Jump','Fall','Attack','Hurt','Death','Land'):
    asset=BASE+'/A_Scintilla_'+name; backup=asset+'_BeforeFacing'
    if not lib.does_asset_exist(backup):
        assert lib.duplicate_asset(asset,backup); lib.save_asset(backup,False)
    clip=import_fbx('A_Scintilla_'+name,skeleton)
    assert clip.get_editor_property('skeleton')==skeleton and clip.get_play_length()>0
lib.save_directory(BASE,False,True)
print('DIRECTIONAL_ANIMATIONS_IMPORTED')
