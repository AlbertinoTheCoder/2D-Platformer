"""Create the three owned campaign maps using the original Blender art kit."""
import json
import re
from pathlib import Path
import unreal

ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
lib=unreal.EditorAssetLibrary
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
campaign=json.loads((ROOT/'Config/campaign.json').read_text())
meshes={p.stem:lib.load_asset('/Game/Platformer/Art/Meshes/'+p.stem) for p in (ROOT/'Assets/Models').glob('*.fbx')}
if not all(meshes.values()): raise RuntimeError('Import art kit first')
classes={}
for name,folder in [('BP_Platform','Environment'),('BP_MovingPlatform','Environment'),('BP_Hazard','Environment'),('BP_Checkpoint','Environment'),('BP_Goal','Environment'),('BP_City','Environment'),('BP_Coin','Pickups'),('BP_PatrolEnemy','Enemies')]:
    classes[name]=lib.load_asset('/Game/Platformer/'+folder+'/'+name).generated_class()

def spawn(cls,pos,label):
    a=actors.spawn_actor_from_class(cls,unreal.Vector(*pos),unreal.Rotator())
    if not a: raise RuntimeError(label)
    a.set_actor_label(label); a.set_folder_path('Scintilla')
    return a

def visual(actor,name,scale,offset=(0,0,0)):
    c=actor.get_editor_property('visual'); c.set_static_mesh(meshes[name]); c.set_editor_property('override_materials',[])
    c.set_relative_scale3d(unreal.Vector(*scale)); c.set_relative_location(unreal.Vector(*offset),False,False)

def prop(name,pos,scale,label,parent=None):
    a=spawn(unreal.StaticMeshActor,pos,'Art_'+label)
    c=a.get_component_by_class(unreal.StaticMeshComponent)
    c.set_mobility(unreal.ComponentMobility.MOVABLE if parent else unreal.ComponentMobility.STATIC)
    c.set_static_mesh(meshes[name]); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    a.set_actor_scale3d(unreal.Vector(*scale))
    if parent: a.attach_to_actor(parent,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
    return a

lib.save_directory('/Game/Platformer',False,True)
reports=[]
REBUILD_OWNED_MAPS=globals().get('REBUILD_OWNED_MAPS',set())
for cfg in campaign['levels'][1:]:
    path='/Game/Platformer/Levels/'+cfg['name']
    if lib.does_asset_exist(path):
        if cfg['name'] not in REBUILD_OWNED_MAPS:
            reports.append({'map':path,'status':'already_exists'}); continue
        if not level.load_level(path): raise RuntimeError('Cannot load '+path)
        for a in list(actors.get_all_level_actors()):
            if a.get_actor_label().startswith('Art_'): actors.destroy_actor(a)
        for a in list(actors.get_all_level_actors()):
            if str(a.get_folder_path())=='Scintilla': actors.destroy_actor(a)
    elif not level.new_level(path): raise RuntimeError('Cannot create '+path)
    spawn(unreal.PlayerStart,cfg['spawn'],'PlayerStart_Scintilla')
    city=spawn(classes['BP_City'],(0,0,0),'City_BlackoutToWarm')
    city.set_editor_property('color_material',lib.load_asset('/Game/Platformer/Materials/M_Color')); city.build_city()
    for c in city.get_components_by_class(unreal.StaticMeshComponent):
        pos=c.get_editor_property('relative_location'); pos.y=-abs(pos.y); c.set_relative_location(pos,False,False)
        match=re.fullmatch(r'Tower(\d+)',c.get_name())
        if match:
            n=int(match.group(1)); height=380+(n*137)%430+cfg['index']*20
            c.set_static_mesh(meshes['SM_Facade']); c.set_editor_property('override_materials',[])
            c.set_relative_scale3d(unreal.Vector(.725,2.1,height/450)); pos.z=-70
            c.set_relative_location(pos,False,False)
        window=re.fullmatch(r'Window(\d+)_(\d+)',c.get_name())
        if window:
            n,j=map(int,window.groups()); height=380+(n*137)%430+cfg['index']*20
            c.set_relative_location(unreal.Vector(-300+n*400+(-83 if j%2==0 else 83),-310,-70+(135 if j<2 else 315)*height/450),False,False)
            c.set_relative_scale3d(unreal.Vector(.44,.1,.72*height/450))
    for p in cfg['platforms']:
        a=spawn(classes['BP_Platform'],(p['x']+p['width']/2,0,p['top']-30),'Platform_'+p['id'])
        s=a.get_editor_property('surface'); s.set_world_scale3d(unreal.Vector(p['width']/100,2,.6)); s.set_visibility(False)
        for i in range((p['width']+199)//200):
            width=min(200,p['width']-i*200)
            prop('SM_Deck',(p['x']+i*200+width/2,0,p['top']+1),(width/200,2,1),p['id']+'_deck_'+str(i))
        prop('SM_Pipe',(p['x']+p['width']*.75,-130,p['top']),(.8,.8,.8),p['id']+'_pipe')
        if p['width']>500:
            for j,x in enumerate((p['x']+85,p['x']+p['width']-100)):
                prop('SM_Lamp',(x,-100,p['top']),(1,1,1),p['id']+'_lamp_'+str(j))
            prop('SM_Crate',(p['x']+170,-95,p['top']),(.7,.7,.7),p['id']+'_crate')
    m=cfg['moving_platform']; pos=list(m['start']); pos[2]-=15
    lift=spawn(classes['BP_MovingPlatform'],pos,'MovingPlatform_ServiceLift')
    lift.set_editor_property('end_offset',unreal.Vector(*[b-a for a,b in zip(m['start'],m['end'])]))
    lift.set_editor_property('speed',m['speed']); lift.set_editor_property('wait_seconds',m['wait_seconds'])
    s=lift.get_editor_property('surface'); s.set_world_scale3d(unreal.Vector(m['width']/100,1.5,.3)); s.set_visibility(False)
    prop('SM_Deck',m['start'],(m['width']/200,1.5,.65),'LiftDeck',lift)
    for j,pos in enumerate(cfg['collectibles']): spawn(classes['BP_Coin'],pos,f'Energy_{j:02}')
    for j,pos in enumerate(cfg['checkpoints']):
        a=spawn(classes['BP_Checkpoint'],pos,f'MaintenanceStation_{j}')
        visual(a,'SM_Checkpoint',(.65,.6,1.5),(0,0,25))
        a.set_editor_property('activate_sound',lib.load_asset('/Game/Platformer/Audio/S_Checkpoint'))
    for e in cfg['enemies']:
        a=spawn(classes['BP_PatrolEnemy'],e['position'],'Drone_'+e['id'])
        a.set_editor_property('patrol_min_x',e['patrol_min_x']); a.set_editor_property('patrol_max_x',e['patrol_max_x']); a.set_editor_property('speed',e['speed'])
        if 'kind' in e:
            a.set_editor_property('enemy_type',getattr(unreal.ScintillaEnemyType,e['kind'].upper())); a.configure_enemy()
    for h in cfg['hazards']:
        a=spawn(classes['BP_Hazard'],h['position'],'ExposedCable_'+h['id']); visual(a,'SM_Electrodes',(1,.5,.4))
    a=spawn(classes['BP_Hazard'],cfg['kill_zone']['center'],'KillZone')
    a.set_editor_property('instant_kill',True); a.get_editor_property('trigger').set_box_extent(unreal.Vector(*cfg['kill_zone']['extent']))
    a.get_editor_property('visual').set_visibility(False)
    a=spawn(classes['BP_Goal'],cfg['goal'],'Generator_RestoreCity'); visual(a,'SM_Generator',(1.4,.9,2.1),(0,0,55))
    a.set_editor_property('complete_sound',lib.load_asset('/Game/Platformer/Audio/S_Complete'))
    actors.set_selected_level_actors([])
    if not level.save_current_level(): raise RuntimeError('Save failed: '+path)
    reports.append(dict(map=path,status='created',platforms=len(cfg['platforms']),enemies=len(cfg['enemies']),hazards=len(cfg['hazards']),energy=len(cfg['collectibles']),lift_width=m['width'],lift_speed=m['speed']))
lib.save_directory('/Game/Platformer',False,True)
level.load_level('/Game/Platformer/Levels/L_Platformer_Prototype')
(ROOT/'Assets/Models/campaign_build_report.json').write_text(json.dumps(reports,indent=2))
print('SCINTILLA_CAMPAIGN_CREATED',reports)
