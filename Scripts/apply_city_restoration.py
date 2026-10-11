"""Back up maps and build weathered, repairable city assemblies for all districts."""
import unreal,json
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
lib=unreal.EditorAssetLibrary; actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
lib.save_directory('/Game/Platformer',False,True)
themes=[(.38,.60,.68,1),(.85,.42,.23,1),(.35,.66,.42,1),(.62,.40,.78,1),(.52,.78,.85,1),(.78,.38,.26,1),(.85,.72,.37,1),(.77,.43,.59,1)]
report=[]
for cfg,tint in zip(json.loads((ROOT/'Config/campaign.json').read_text())['levels'],themes):
    path='/Game/Platformer/Levels/'+cfg['name']; backup=path+'_BeforeRestoration'
    if not lib.does_asset_exist(backup):
        if not lib.duplicate_asset(path,backup): raise RuntimeError(backup)
    if not level.load_level(path): raise RuntimeError(path)
    cities=[]; props=0
    for actor in actors.get_all_level_actors():
        label=actor.get_actor_label().lower()
        if isinstance(actor,unreal.ScintillaCity): cities.append(actor)
        if label.startswith('art_') and 'deck' not in label and 'lift' not in label:
            tags=list(actor.get_editor_property('tags'))
            if 'ScintillaRestore' not in [str(tag) for tag in tags]: tags.append('ScintillaRestore')
            actor.set_editor_property('tags',tags); props+=1
    if len(cities)!=1: raise RuntimeError('Expected one city: '+path)
    city=cities[0]
    data=json.loads((ROOT/'Config/platformer.json').read_text())['level'] if cfg['index']==1 else cfg
    city.set_editor_property('city_length',data['goal'][0]+350)
    city.set_editor_property('district_tint',unreal.LinearColor(*tint))
    city.set_editor_property('powered',False)
    city.set_editor_property('color_material',lib.load_asset('/Game/Platformer/Art/Robot/M_RobotRigid'))
    city.build_city()
    pieces=city.get_components_by_class(unreal.StaticMeshComponent)
    if len(pieces)<100 or any(not p.get_editor_property('static_mesh') for p in pieces): raise RuntimeError('Missing city geometry')
    if any(p.get_collision_enabled()!=unreal.CollisionEnabled.NO_COLLISION for p in pieces): raise RuntimeError('City scenery must not block gameplay')
    actors.set_selected_level_actors([])
    if not level.save_current_level(): raise RuntimeError('Save failed '+path)
    report.append({'level':cfg['index'],'pieces':len(pieces),'repairable_props':props,'saved':True})
lib.save_directory('/Game/Platformer',False,True)
level.load_level('/Game/Platformer/Levels/L_Platformer_Prototype')
(ROOT/'Assets/Models/City/map_report.json').write_text(json.dumps(report,indent=2))
print('CITY_RESTORATION_APPLIED',report)
