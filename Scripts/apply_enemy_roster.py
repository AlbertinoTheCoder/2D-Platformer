"""Back up each map and replace the owned enemy population with three new families."""
import unreal,json
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
lib=unreal.EditorAssetLibrary; actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem); level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
lib.save_directory('/Game/Platformer',False,True)
families={}
for name in ('Scout','Charger','Sentinel'):
    path='/Game/Platformer/Enemies/BP_'+name
    if not lib.does_asset_exist(path): assert lib.duplicate_asset('/Game/Platformer/Enemies/BP_PatrolEnemy',path)
    bp=lib.load_asset(path); unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    cdo=unreal.get_default_object(bp.generated_class()); cdo.set_editor_property('enemy_type',getattr(unreal.ScintillaEnemyType,name.upper()))
    cdo.configure_enemy(); unreal.BlueprintEditorLibrary.compile_blueprint(bp); assert lib.save_loaded_asset(bp,False)
    families[name]=bp.generated_class()
cfgs=json.loads((ROOT/'Config/campaign.json').read_text())['levels']; base=json.loads((ROOT/'Config/platformer.json').read_text())['level']
reports=[]
for cfg in cfgs:
    data=base if cfg['index']==1 else cfg
    path='/Game/Platformer/Levels/'+cfg['name']; backup=path+'_BeforeEnemyRoster'
    if not lib.does_asset_exist(backup): assert lib.duplicate_asset(path,backup); lib.save_asset(backup,False)
    if not level.load_level(path): raise RuntimeError(path)
    for a in list(actors.get_all_level_actors()):
        if isinstance(a,unreal.ScintillaEnemy): actors.destroy_actor(a)
    for e in data['enemies']:
        a=actors.spawn_actor_from_class(families[e['kind']],unreal.Vector(*e['position']),unreal.Rotator())
        if not a: raise RuntimeError(e['id'])
        a.set_actor_label('Enemy_'+e['id']+'_'+e['kind']); a.set_folder_path('Scintilla')
        for key in ('patrol_min_x','patrol_max_x','speed'): a.set_editor_property(key,e[key])
        a.configure_enemy()
    actors.set_selected_level_actors([])
    if not level.save_current_level(): raise RuntimeError(path)
    reports.append(dict(level=cfg['index'],count=len(data['enemies']),types=sorted({e['kind'] for e in data['enemies']}),saved=True))
lib.save_directory('/Game/Platformer',False,True); level.load_level('/Game/Platformer/Levels/L_Platformer_Prototype')
(ROOT/'Assets/Models/Enemies/roster_report.json').write_text(json.dumps(reports,indent=2))
print('ENEMY_ROSTER_APPLIED',reports)
