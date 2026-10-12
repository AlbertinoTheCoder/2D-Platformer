"""Append authored challenge sections; preserve existing routes and map backups."""
import unreal,json
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
lib=unreal.EditorAssetLibrary; actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem); levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
lib.save_directory('/Game/Platformer',False,True); report=[]
platform=lib.load_asset('/Game/Platformer/Environment/BP_Platform').generated_class()
coin=lib.load_asset('/Game/Platformer/Pickups/BP_Coin').generated_class()
checkpoint=lib.load_asset('/Game/Platformer/Environment/BP_Checkpoint').generated_class()
def spawn(cls,pos,label):
    a=actors.spawn_actor_from_class(cls,unreal.Vector(*pos)); a.set_actor_label('Difficulty_'+label); a.set_folder_path('Scintilla/Difficulty'); a.set_editor_property('tags',[unreal.Name('ScintillaChallenge')]); return a
def prop(mesh,pos,scale,label):
    a=spawn(unreal.StaticMeshActor,pos,label); c=a.get_component_by_class(unreal.StaticMeshComponent)
    c.set_static_mesh(lib.load_asset('/Game/Platformer/Art/Difficulty/'+mesh)); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); a.set_actor_scale3d(unreal.Vector(*scale)); return a
for cfg in json.loads((ROOT/'Config/campaign.json').read_text())['levels']:
    path='/Game/Platformer/Levels/'+cfg['name']; backup=path+'_BeforeDifficulty'
    if not lib.does_asset_exist(backup) and not lib.duplicate_asset(path,backup): raise RuntimeError(backup)
    if not levels.load_level(path): raise RuntimeError(path)
    for a in list(actors.get_all_level_actors()):
        if a.get_actor_label().startswith('Difficulty_'): actors.destroy_actor(a)
    ext=cfg['difficulty_extension']
    for p in ext['platforms']:
        a=spawn(platform,(p['x']+340,0,p['top']-15),p['id']); c=a.get_editor_property('surface'); c.set_world_scale3d(unreal.Vector(6.80,2,.3)); c.set_visibility(False)
        for i in range(3):
            prop('SM_LongDeck',(p['x']+113.33+i*226.67,0,p['top']),(226.67/300,1.3,1),p['id']+'_deck_'+str(i))
        prop('SM_LongColumn',(p['x']+340,-70,p['top']),(1,1,1.5),p['id']+'_support')
    for i,h in enumerate(ext['obstacles']):
        a=spawn(unreal.ScintillaObstacle,h['position'],'hazard_'+str(i)); a.set_editor_property('obstacle_type',getattr(unreal.ScintillaObstacleType,{'Wind':'WIND','Ice':'ICE','FallingSpikes':'FALLING_SPIKES','RisingSpikes':'RISING_SPIKES','Hammer':'HAMMER','Axe':'AXE'}[h['kind']]))
        a.set_editor_property('phase_offset',h['phase_offset']); a.set_editor_property('region_half_width',h['half_width'])
        if 'direction' in h: a.set_editor_property('wind_direction',unreal.Vector(*h['direction']))
        a.configure_obstacle()
        if h['kind'] in ('FallingSpikes','Hammer','Axe'):
            height=320 if h['kind']=='FallingSpikes' else 220
            for side in (-1,1): prop('SM_LongColumn',(h['position'][0]+side*95,-90,h['position'][2]+height),(.55,.55,height/265),'trap_support_'+str(i)+'_'+str(side))
    for i,e in enumerate(ext['flyers']):
        a=spawn(unreal.ScintillaEnemy,e['position'],'flyer_'+str(i)); a.set_editor_property('enemy_type',unreal.ScintillaEnemyType.FLYER if e['kind']=='Flyer' else unreal.ScintillaEnemyType.SURVEY_FLYER)
        for k in ('patrol_min_x','patrol_max_x','speed'): a.set_editor_property(k,e[k])
        a.configure_enemy()
    for i,pos in enumerate(ext['collectibles']): spawn(coin,pos,'energy_'+str(i))
    a=spawn(checkpoint,ext['checkpoint'],'checkpoint'); a.get_editor_property('visual').set_static_mesh(lib.load_asset('/Game/Platformer/Art/Difficulty/SM_LivesTerminal')); a.get_editor_property('visual').set_relative_scale3d(unreal.Vector(.8))
    a=spawn(checkpoint,(ext['platforms'][0]['x']+70,0,ext['platforms'][0]['top']+50),'entry_checkpoint'); a.get_editor_property('visual').set_static_mesh(lib.load_asset('/Game/Platformer/Art/Difficulty/SM_LivesTerminal')); a.get_editor_property('visual').set_relative_scale3d(unreal.Vector(.8))
    prop('SM_LongArch',(ext['platforms'][0]['x']+30,-110,ext['platforms'][0]['top']),(1,1,1),'entry_arch')
    for a in actors.get_all_level_actors():
        if isinstance(a,unreal.ScintillaGoal): a.set_actor_location(unreal.Vector(*ext['goal']),False,False)
        if isinstance(a,unreal.TextRenderActor) and str(a.get_component_by_class(unreal.TextRenderComponent).get_editor_property('text'))=='RESTORE POWER TO THE CITY': a.set_actor_location(unreal.Vector(ext['goal'][0]-160,-25,ext['goal'][2]+300),False,False)
        if isinstance(a,unreal.ScintillaHazard) and a.get_editor_property('instant_kill'):
            a.set_actor_location(unreal.Vector(ext['goal'][0]/2,0,-700),False,False); a.get_editor_property('trigger').set_box_extent(unreal.Vector(ext['goal'][0]/2+1200,200,200))
        if isinstance(a,unreal.ScintillaCity): a.set_editor_property('city_length',ext['goal'][0]+350); a.build_city()
    if not levels.save_current_level(): raise RuntimeError(path)
    report.append({'level':cfg['index'],'new_platforms':7,'hazards':len(ext['obstacles']),'flyers':len(ext['flyers']),'length_before_cm':ext['original_goal'][0],'length_after_cm':ext['goal'][0],'saved':True})
levels.load_level('/Game/Platformer/Levels/L_Platformer_Prototype')
(ROOT/'Assets/Models/Difficulty/map_report.json').write_text(json.dumps(report,indent=2))
print('DIFFICULTY_MAPS_SAVED',report)

# Keep obstacle placement consistent with the current seeded campaign plan.
exec((ROOT/'Scripts/apply_scattered_difficulty.py').read_text(), globals())
