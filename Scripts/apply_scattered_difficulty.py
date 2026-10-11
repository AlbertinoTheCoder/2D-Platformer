"""Move existing traps, supports, signs, and flyers; keep routes and terrain intact."""
import unreal, json
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
lib=unreal.EditorAssetLibrary
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
lib.save_directory('/Game/Platformer',False,True)
report=[]
for cfg in json.loads((ROOT/'Config/campaign.json').read_text())['levels']:
    path='/Game/Platformer/Levels/'+cfg['name']
    backup=path+'_BeforeObstacleScatter'
    if not lib.does_asset_exist(backup) and not lib.duplicate_asset(path,backup): raise RuntimeError(backup)
    if not levels.load_level(path): raise RuntimeError(path)
    bylabel={a.get_actor_label():a for a in actors.get_all_level_actors()}
    ext=cfg['difficulty_extension']
    kinds=['Wind','FallingSpikes','Ice','Flyer','RisingSpikes','Hammer','Axe']
    for i,h in enumerate(ext['obstacles']):
        a=bylabel['Difficulty_hazard_'+str(i)]
        before=a.get_actor_location(); target=unreal.Vector(*h['position']); delta=target-before
        a.set_actor_location(target,False,False)
        a.set_editor_property('phase_offset',h['phase_offset'])
        a.set_editor_property('region_half_width',h['half_width'])
        if 'direction' in h: a.set_editor_property('wind_direction',unreal.Vector(*h['direction']))
        a.configure_obstacle()
        for side in (-1,1):
            label='Difficulty_trap_support_'+str(i)+'_'+str(side)
            if label in bylabel: bylabel[label].set_actor_location(bylabel[label].get_actor_location()+delta,False,False)
        if h['kind']!='Wind' or h['direction'][0]<0:
            sign=bylabel['Difficulty_sign_challenge_'+str(kinds.index(h['kind']))]
            sign.set_actor_location(unreal.Vector(target.x,-55,target.z+(345 if h['kind'] in ('Hammer','Axe') else 110 if h['kind']=='Wind' else 195)),False,False)
    for i,e in enumerate(ext['flyers']):
        a=bylabel['Difficulty_flyer_'+str(i)]
        a.set_actor_location(unreal.Vector(*e['position']),False,False)
        for k in ('patrol_min_x','patrol_max_x','speed'): a.set_editor_property(k,e[k])
        a.configure_enemy()
        if i==0: bylabel['Difficulty_sign_challenge_3'].set_actor_location(unreal.Vector(e['position'][0],-55,e['position'][2]+80),False,False)
    if not levels.save_current_level(): raise RuntimeError(path)
    report.append({'level':cfg['index'],'moved_obstacles':len(ext['obstacles']),'saved':True})
levels.load_level('/Game/Platformer/Levels/L_Platformer_Prototype')
(ROOT/'Assets/Models/Difficulty/scatter_map_report.json').write_text(json.dumps(report,indent=2))
print('SCATTER_MAPS_SAVED')
