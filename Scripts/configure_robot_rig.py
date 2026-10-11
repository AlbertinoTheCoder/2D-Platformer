"""Set and verify the inherited character Mesh on BP_Player after the native build."""
import unreal,json
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
lib=unreal.EditorAssetLibrary
bp=lib.load_asset('/Game/Platformer/Characters/BP_Player')
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
cdo=unreal.get_default_object(bp.generated_class())
mesh=cdo.get_component_by_class(unreal.SkeletalMeshComponent)
asset=lib.load_asset('/Game/Platformer/Art/Robot/SK_Scintilla')
mesh.set_skeletal_mesh_asset(asset)
mesh.set_relative_location(unreal.Vector(0,0,-41.65),False,False)
mesh.set_relative_rotation(unreal.Rotator(0,0,0),False,False)
mesh.set_relative_scale3d(unreal.Vector(1,1,1))
mesh.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
mesh.set_editor_property('override_materials',[])
cdo.get_editor_property('body').set_visibility(False)
cdo.get_editor_property('eye').set_visibility(False)
clips=cdo.get_editor_property('animation_clips')
assert len(clips)==8,'Missing native clip references'
assert mesh.get_num_bones()==10,mesh.get_num_bones() # FBX armature node plus nine authored bones.
assert mesh.get_bone_index('foot_L')>=0
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
assert lib.save_loaded_asset(bp,False)
(ROOT/'Assets/Models/RobotRig/configure_report.json').write_text(json.dumps({'mesh':asset.get_path_name(),'bones':mesh.get_num_bones(),'clips':len(clips),'offset':-41.65},indent=2))
print('ROBOT_CONFIGURE_OK')
