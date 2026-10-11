"""Ground existing scenery in eight maps without rebuilding or moving the terrain."""
import unreal,json,hashlib
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
terrain_file=ROOT/'Platformer_2D_Game/Content/Platformer/Art/City/SM_CityTerrain.uasset'
digest=lambda:hashlib.sha256(terrain_file.read_bytes()).hexdigest()
before_hash=digest(); lib=unreal.EditorAssetLibrary
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem); level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
lib.save_directory('/Game/Platformer',False,True); report=[]
for cfg in json.loads((ROOT/'Config/campaign.json').read_text())['levels']:
    path='/Game/Platformer/Levels/'+cfg['name']; backup=path+'_BeforeGrounding'
    if not lib.does_asset_exist(backup) and not lib.duplicate_asset(path,backup): raise RuntimeError(backup)
    if not level.load_level(path): raise RuntimeError(path)
    city=next(a for a in actors.get_all_level_actors() if isinstance(a,unreal.ScintillaCity))
    pieces=city.get_components_by_class(unreal.StaticMeshComponent)
    terrain=next(p for p in pieces if p.get_name()=='Terrain')
    transform=str(terrain.get_relative_transform()); mesh=terrain.get_editor_property('static_mesh').get_path_name()
    city.ground_city()
    if len(city.get_editor_property('ground_profile'))<2: raise RuntimeError('Terrain profile missing')
    if str(terrain.get_relative_transform())!=transform or terrain.get_editor_property('static_mesh').get_path_name()!=mesh: raise RuntimeError('Terrain changed')
    if not level.save_current_level(): raise RuntimeError(path)
    report.append({'level':cfg['index'],'terrain_unchanged':True,'profile_points':len(city.get_editor_property('ground_profile')),'saved':True})
level.load_level('/Game/Platformer/Levels/L_Platformer_Prototype')
after_hash=digest()
if after_hash!=before_hash: raise RuntimeError('Terrain asset changed')
(ROOT/'Assets/Models/City/grounding_map_report.json').write_text(json.dumps({'terrain_sha256_before':before_hash,'terrain_sha256_after':after_hash,'maps':report},indent=2))
print('CITY_GROUNDING_SAVED',report,'TERRAIN_ASSET_UNCHANGED')
