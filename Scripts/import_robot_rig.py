"""Import the Blender skeleton and eight clips without changing any level geometry."""
import unreal, json
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
OUT=ROOT/'Assets/Models/RobotRig'; BASE='/Game/Platformer/Art/Robot'
lib=unreal.EditorAssetLibrary; tools=unreal.AssetToolsHelpers.get_asset_tools(); mel=unreal.MaterialEditingLibrary
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
lib.make_directory(BASE)
bp=lib.load_asset('/Game/Platformer/Characters/BP_Player')
backup='/Game/Platformer/Characters/BP_Player_BeforeRig'
if not lib.does_asset_exist(backup):
    assert lib.duplicate_asset(bp.get_path_name(),backup)
    lib.save_asset(backup,False)
def import_fbx(name,skeleton=None):
    options=unreal.FbxImportUI()
    options.set_editor_property('automated_import_should_detect_type',False)
    options.set_editor_property('import_as_skeletal',True)
    options.set_editor_property('import_mesh',skeleton is None)
    options.set_editor_property('import_animations',skeleton is not None)
    options.set_editor_property('import_materials',False)
    options.set_editor_property('import_textures',False)
    options.set_editor_property('create_physics_asset',False)
    options.set_editor_property('mesh_type_to_import',unreal.FBXImportType.FBXIT_ANIMATION if skeleton else unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    if skeleton:
        options.set_editor_property('skeleton',skeleton)
        options.anim_sequence_import_data.set_editor_property('animation_length',unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
        options.anim_sequence_import_data.set_editor_property('use_default_sample_rate',True)
    else:
        options.skeletal_mesh_import_data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)
    task=unreal.AssetImportTask()
    for k,v in dict(filename=str(OUT/(name+'.fbx')),destination_path=BASE,destination_name=name,automated=True,replace_existing=True,save=True,options=options).items(): task.set_editor_property(k,v)
    tools.import_asset_tasks([task])
    loaded=[lib.load_asset(p) for p in task.get_editor_property('imported_object_paths')]
    cls=unreal.AnimSequence if skeleton else unreal.SkeletalMesh
    found=[a for a in loaded if isinstance(a,cls)]
    if not found: raise RuntimeError('Import failed '+name+' '+str(loaded))
    result=found[0]
    if result.get_name()!=name:
        assert lib.rename_asset(result.get_path_name(),BASE+'/'+name)
        result=lib.load_asset(BASE+'/'+name)
    return result
mesh=import_fbx('SK_Scintilla'); skeleton=mesh.get_editor_property('skeleton')
# Dedicated copies of the existing shaders: remove WPO only from the robot.
parents={}
for old,new in [('M_Industrial','M_RobotRigid'),('M_IndustrialGlow','M_RobotRigidGlow')]:
    path=BASE+'/'+new
    if not lib.does_asset_exist(path): assert lib.duplicate_asset('/Game/Platformer/Art/Materials/'+old,path)
    mat=lib.load_asset(path)
    zero=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,800,500)
    assert mel.connect_material_property(zero,'',unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    mat.set_editor_property('used_with_skeletal_mesh',True)
    mel.recompile_material(mat); lib.save_loaded_asset(mat,False); parents[old]=mat
palette=json.loads((ROOT/'Assets/Models/manifest.json').read_text())['palette']
slots=mesh.get_editor_property('materials')
for i,slot in enumerate(slots):
    name=str(slot.get_editor_property('material_slot_name')).replace('Scintilla_','')
    assert name in palette,name
    path=BASE+'/MI_Robot_'+name
    mi=lib.load_asset(path) if lib.does_asset_exist(path) else tools.create_asset('MI_Robot_'+name,BASE,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    parent='M_IndustrialGlow' if name in ('Cyan','Amber','Red','Glass') else 'M_Industrial'
    mel.set_material_instance_parent(mi,parents[parent])
    mel.set_material_instance_vector_parameter_value(mi,'Tint',unreal.LinearColor(*palette[name]))
    lib.save_loaded_asset(mi,False); slot.set_editor_property('material_interface',mi); slots[i]=slot
mesh.set_editor_property('materials',slots)
lib.save_loaded_asset(mesh,False)
clips={}
for name in json.loads((OUT/'manifest.json').read_text())['clips']:
    clip=import_fbx('A_Scintilla_'+name,skeleton)
    assert clip.get_editor_property('skeleton')==skeleton
    clips[name]={'asset':clip.get_path_name(),'duration':clip.get_play_length()}
    assert clips[name]['duration']>0
lib.save_directory(BASE,False,True)
(OUT/'import_report.json').write_text(json.dumps({'mesh':mesh.get_path_name(),'skeleton':skeleton.get_path_name(),'clips':clips},indent=2))
print('ROBOT_IMPORT_OK',json.dumps(clips))
