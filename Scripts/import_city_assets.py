"""Import the nine Blender city meshes and preserve their authored color slots."""
import unreal,json
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
OUT=ROOT/'Assets/Models/City'; BASE='/Game/Platformer/Art/City'
lib=unreal.EditorAssetLibrary; tools=unreal.AssetToolsHelpers.get_asset_tools(); mel=unreal.MaterialEditingLibrary
lib.make_directory(BASE); lib.save_directory('/Game/Platformer',False,True)
palette=json.loads((OUT/'manifest.json').read_text())['palette']; mats={}
for name,col in palette.items():
    path=BASE+'/MI_City_'+name
    mi=lib.load_asset(path) if lib.does_asset_exist(path) else tools.create_asset('MI_City_'+name,BASE,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    parent=lib.load_asset('/Game/Platformer/Art/Robot/M_RobotRigidGlow' if name=='Glass' else '/Game/Platformer/Art/Robot/M_RobotRigid')
    mel.set_material_instance_parent(mi,parent); mel.set_material_instance_vector_parameter_value(mi,'Tint',unreal.LinearColor(*col))
    lib.save_loaded_asset(mi,False); mats[name]=mi
imported=[]
for source in sorted(OUT.glob('*.fbx')):
    task=unreal.AssetImportTask()
    for key,value in dict(filename=str(source),destination_path=BASE,destination_name=source.stem,automated=True,save=True,replace_existing=True).items(): task.set_editor_property(key,value)
    opt=unreal.FbxImportUI(); opt.set_editor_property('import_materials',False); opt.set_editor_property('import_textures',False)
    opt.set_editor_property('mesh_type_to_import',unreal.FBXImportType.FBXIT_STATIC_MESH)
    opt.static_mesh_import_data.set_editor_property('combine_meshes',True); opt.static_mesh_import_data.set_editor_property('auto_generate_collision',False)
    task.set_editor_property('options',opt); tools.import_asset_tasks([task])
    mesh=lib.load_asset(BASE+'/'+source.stem)
    if not isinstance(mesh,unreal.StaticMesh): raise RuntimeError(source.stem)
    for i,slot in enumerate(mesh.get_editor_property('static_materials')):
        name=str(slot.get_editor_property('material_slot_name')).replace('Scintilla_City_','')
        if name not in mats: raise RuntimeError('Unknown city material '+name)
        mesh.set_material(i,mats[name])
    lib.save_loaded_asset(mesh,False); imported.append(source.stem)
(OUT/'import_report.json').write_text(json.dumps({'imported':imported,'saved':True},indent=2))
print('CITY_ASSETS_IMPORTED',imported)
