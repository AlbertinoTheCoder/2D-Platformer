"""Patch Torre's collision and deck tiles, keeping its purple art and skyline."""
import unreal,json,re
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
cfg=json.loads((ROOT/'Config/campaign.json').read_text())['levels'][3]
lib=unreal.EditorAssetLibrary
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert level.save_current_level()
path='/Game/Platformer/Levels/L_04_Torre'
backup=path+'_BeforeBalance'
if not lib.does_asset_exist(backup):
    assert lib.duplicate_asset(path,backup); assert lib.save_asset(backup,False)
assert level.load_level(path)
existing={a.get_actor_label():a for a in actors.get_all_level_actors()}
deck=lib.load_asset('/Game/Platformer/Art/Meshes/SM_Deck')
# Reuse the map's purple material slots, not the kit's neutral palette.
template=existing['Art_start_deck_0'].get_component_by_class(unreal.StaticMeshComponent)
deck_materials=[template.get_material(i) for i in range(template.get_num_materials())]
old_platforms={}
for p in cfg['platforms']:
    a=existing['Platform_'+p['id']]
    s=a.get_editor_property('surface')
    loc=a.get_actor_location(); scale=s.get_world_scale()
    old_platforms[p['id']]={'x':loc.x-scale.x*50,'width':scale.x*100,'top':loc.z+30}
    a.set_actor_location(unreal.Vector(p['x']+p['width']/2,0,p['top']-30),False,False)
    s.set_world_scale3d(unreal.Vector(p['width']/100,2,.6))
    s.set_visibility(False)
    for label,obj in list(existing.items()):
        if re.fullmatch('Art_'+p['id']+r'_deck_\d+',label): actors.destroy_actor(obj)
    for i in range((p['width']+199)//200):
        width=min(200,p['width']-i*200)
        a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(p['x']+i*200+width/2,0,p['top']+1),unreal.Rotator())
        a.set_actor_label('Art_'+p['id']+'_deck_'+str(i)); a.set_folder_path('Scintilla')
        c=a.get_component_by_class(unreal.StaticMeshComponent)
        c.set_static_mesh(deck); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        for slot,mat in enumerate(deck_materials): c.set_material(slot,mat)
        a.set_actor_scale3d(unreal.Vector(width/200,2,1))
    # Keep each platform's existing set dressing anchored to its new span.
    old=old_platforms[p['id']]
    for label,obj in existing.items():
        if label.startswith('Art_'+p['id']+'_') and not re.fullmatch('Art_'+p['id']+r'_deck_\d+',label):
            pos=obj.get_actor_location(); fraction=(pos.x-old['x'])/old['width']
            obj.set_actor_location(unreal.Vector(p['x']+fraction*p['width'],pos.y,pos.z+p['top']-old['top']),False,False)
m=cfg['moving_platform']; lift=existing['MovingPlatform_ServiceLift']
lift.set_actor_location(unreal.Vector(m['start'][0],0,m['start'][2]-15),False,False)
lift.set_editor_property('end_offset',unreal.Vector(*[b-a for a,b in zip(m['start'],m['end'])]))
lift.set_editor_property('speed',m['speed']); lift.set_editor_property('wait_seconds',m['wait_seconds'])
lift.get_editor_property('surface').set_world_scale3d(unreal.Vector(m['width']/100,1.5,.3))
existing['Art_LiftDeck'].set_actor_scale3d(unreal.Vector(m['width']/200,1.5,.65))
existing['Art_LiftDeck'].set_actor_location(unreal.Vector(*m['start']),False,False)
for e in cfg['enemies']:
    a=existing['Drone_'+e['id']]; a.set_actor_location(unreal.Vector(*e['position']),False,False)
    for key in ('speed','patrol_min_x','patrol_max_x'): a.set_editor_property(key,e[key])
for h in cfg['hazards']:
    a=existing['ExposedCable_'+h['id']]; a.set_actor_location(unreal.Vector(*h['position']),False,False)
    a.get_editor_property('trigger').set_box_extent(unreal.Vector(h['width']/2,45,22))
    a.get_editor_property('visual').set_relative_scale3d(unreal.Vector(.8,.5,.4))
for i,pos in enumerate(cfg['collectibles']): existing[f'Energy_{i:02}'].set_actor_location(unreal.Vector(*pos),False,False)
for i,pos in enumerate(cfg['checkpoints']):
    label='MaintenanceStation_'+str(i)
    if label in existing: a=existing[label]
    else:
        cls=lib.load_asset('/Game/Platformer/Environment/BP_Checkpoint').generated_class()
        a=actors.spawn_actor_from_class(cls,unreal.Vector(*pos),unreal.Rotator()); a.set_actor_label(label); a.set_folder_path('Scintilla')
        src=existing['MaintenanceStation_0'].get_editor_property('visual'); visual=a.get_editor_property('visual')
        visual.set_static_mesh(src.get_editor_property('static_mesh'))
        visual.set_relative_scale3d(unreal.Vector(.65,.6,1.5)); visual.set_relative_location(unreal.Vector(0,0,25),False,False)
        for slot in range(src.get_num_materials()): visual.set_material(slot,src.get_material(slot))
        a.set_editor_property('activate_sound',lib.load_asset('/Game/Platformer/Audio/S_Checkpoint'))
    a.set_actor_location(unreal.Vector(*pos),False,False)
existing['Generator_RestoreCity'].set_actor_location(unreal.Vector(*cfg['goal']),False,False)
assert level.save_current_level()
(ROOT/'Assets/Models/torre_balance_report.json').write_text(json.dumps(cfg,indent=2))
print('TORRE_BALANCE_OK')
