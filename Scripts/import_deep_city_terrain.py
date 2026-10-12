"""Reimport only the deeper city terrain and verify reveal coverage in all maps."""
import unreal, json
from pathlib import Path
ROOT = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
lib = unreal.EditorAssetLibrary
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
original_map = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name().split('.')[0]
path = '/Game/Platformer/Art/City/SM_CityTerrain'
if not lib.save_directory('/Game/Platformer', False, True):
    raise RuntimeError('Save before terrain import failed')
backup = path + '_BeforeDeepTerrain'
if not lib.does_asset_exist(backup) and not lib.duplicate_asset(path, backup):
    raise RuntimeError('Terrain backup failed')
mesh = lib.load_asset(path)
before = lib.load_asset(backup).get_bounding_box()
if mesh.get_bounding_box().min.z > -3999:
    materials = [slot.get_editor_property('material_interface') for slot in mesh.get_editor_property('static_materials')]
    task = unreal.AssetImportTask()
    for key, value in dict(filename=str(ROOT / 'Assets/Models/City/SM_CityTerrain.fbx'),
            destination_path='/Game/Platformer/Art/City', destination_name='SM_CityTerrain',
            automated=True, save=True, replace_existing=True).items():
        task.set_editor_property(key, value)
    options = unreal.FbxImportUI()
    options.set_editor_property('import_materials', False)
    options.set_editor_property('import_textures', False)
    options.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_STATIC_MESH)
    options.static_mesh_import_data.set_editor_property('combine_meshes', True)
    options.static_mesh_import_data.set_editor_property('auto_generate_collision', False)
    task.set_editor_property('options', options)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    mesh = lib.load_asset(path)
    for index, material in enumerate(materials):
        mesh.set_material(index, material)
after = mesh.get_bounding_box()
if abs(after.max.z - before.max.z) > .1 or abs(after.min.x - before.min.x) > .1 or abs(after.max.x - before.max.x) > .1:
    raise RuntimeError('Terrain surface or width changed')
if after.min.z > -3999:
    raise RuntimeError('Terrain did not import at the intended depth')
if not lib.save_loaded_asset(mesh, False):
    raise RuntimeError('Terrain save failed')
if not lib.save_directory('/Game/Platformer', False, True):
    raise RuntimeError('Could not save maps affected by the shared mesh reimport')
report = []
for cfg in json.loads((ROOT / 'Config/campaign.json').read_text())['levels']:
    level_path = '/Game/Platformer/Levels/' + cfg['name']
    if not levels.load_level(level_path):
        raise RuntimeError(level_path)
    city = next(a for a in actors.get_all_level_actors() if isinstance(a, unreal.ScintillaCity))
    terrain = next(c for c in city.get_components_by_class(unreal.StaticMeshComponent) if c.get_name() == 'Terrain')
    if terrain.get_editor_property('static_mesh') != mesh:
        raise RuntimeError('Map is not using shared terrain: ' + level_path)
    bottom = city.get_actor_location().z + terrain.get_editor_property('relative_location').z + after.min.z * terrain.get_editor_property('relative_scale3d').z
    reveal_width = city.get_editor_property('city_length') + 1100
    # Use a taller 4:3 frame as well as the normal widescreen reveal.
    frame_bottom = 350 - reveal_width / (4 / 3) / 2
    if bottom >= frame_bottom - 1000:
        raise RuntimeError('Insufficient ground depth: ' + level_path)
    report.append({'level': cfg['index'], 'terrain_bottom_cm': bottom,
        'reveal_bottom_4_3_cm': frame_bottom, 'clearance_cm': frame_bottom - bottom,
        'verified': True})
    del city, terrain
    if not levels.save_current_level():
        raise RuntimeError('Could not save checked map: ' + level_path)
if not levels.load_level(original_map):
    raise RuntimeError('Could not restore original editor map')
output = {'mesh_bottom_before_cm': before.min.z, 'mesh_bottom_after_cm': after.min.z,
    'surface_height_unchanged': True, 'maps': report}
(ROOT / 'Assets/Models/City/terrain_depth_report.json').write_text(json.dumps(output, indent=2) + '\n')
print('DEEP_TERRAIN_IMPORTED', output)
