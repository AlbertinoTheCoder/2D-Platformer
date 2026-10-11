"""Extend each icy surface to the exact bounds of its supporting platform."""
import unreal,json
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
lib=unreal.EditorAssetLibrary
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
report=[]
for cfg in json.loads((ROOT/'Config/campaign.json').read_text())['levels']:
    path='/Game/Platformer/Levels/'+cfg['name']
    backup=path+'_BeforeFullPlatformIce'
    if not lib.does_asset_exist(backup) and not lib.duplicate_asset(path,backup): raise RuntimeError(backup)
    if not levels.load_level(path): raise RuntimeError(path)
    bylabel={a.get_actor_label():a for a in actors.get_all_level_actors()}
    i,h=next((i,h) for i,h in enumerate(cfg['difficulty_extension']['obstacles']) if h['kind']=='Ice')
    a=bylabel['Difficulty_hazard_'+str(i)]
    a.set_actor_location(unreal.Vector(*h['position']),False,False)
    a.set_editor_property('region_half_width',h['half_width'])
    a.configure_obstacle()
    bylabel['Difficulty_sign_challenge_2'].set_actor_location(unreal.Vector(h['position'][0],-55,h['position'][2]+195),False,False)
    if not levels.save_current_level(): raise RuntimeError(path)
    report.append({'level':cfg['index'],'width_cm':h['half_width']*2,'position':h['position'],'saved':True})
levels.load_level('/Game/Platformer/Levels/L_Platformer_Prototype')
(ROOT/'Assets/Models/Difficulty/full_platform_ice_report.json').write_text(json.dumps(report,indent=2))
print('FULL_PLATFORM_ICE_SAVED')
