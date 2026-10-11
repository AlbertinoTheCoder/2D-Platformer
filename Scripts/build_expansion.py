"""Import the Blender expansion kit, build only new maps and dress them by theme."""
import unreal,json,re
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
lib=unreal.EditorAssetLibrary; tools=unreal.AssetToolsHelpers.get_asset_tools(); mel=unreal.MaterialEditingLibrary
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lib.save_directory('/Game/Platformer',False,True)
BASE='/Game/Platformer/Art/Expansion'; lib.make_directory(BASE)
kit={}
for source in sorted((ROOT/'Assets/Models/Expansion').glob('*.fbx')):
    task=unreal.AssetImportTask(); task.set_editor_property('filename',str(source))
    task.set_editor_property('destination_path',BASE); task.set_editor_property('destination_name',source.stem)
    task.set_editor_property('automated',True); task.set_editor_property('save',True); task.set_editor_property('replace_existing',True)
    opt=unreal.FbxImportUI(); opt.set_editor_property('import_materials',False); opt.set_editor_property('import_textures',False)
    opt.set_editor_property('mesh_type_to_import',unreal.FBXImportType.FBXIT_STATIC_MESH)
    opt.static_mesh_import_data.set_editor_property('combine_meshes',True); opt.static_mesh_import_data.set_editor_property('auto_generate_collision',False)
    task.set_editor_property('options',opt); tools.import_asset_tasks([task])
    mesh=lib.load_asset(BASE+'/'+source.stem)
    if not mesh: raise RuntimeError('Import failed '+source.stem)
    kit[source.stem]=mesh

# The shared builder skips every existing map. No original district is rebuilt.
exec((ROOT/'Scripts/build_campaign.py').read_text(),{})
cfgs=json.loads((ROOT/'Config/campaign.json').read_text())['levels'][4:]
base=json.loads((ROOT/'Assets/Models/manifest.json').read_text())['palette']
themes={
 5:dict(landmark='SM_CryoPod',prop='SM_IceCluster',deck='SM_DeckCryo',filter=(1.6,3.0,3.8),palette=dict(Steel=(.12,.31,.36,1),SteelLight=(.48,.73,.80,1),Gold=(.12,.50,.57,1),Dark=(.015,.045,.065,1),Cyan=(.25,.85,1,1),Glass=(.12,.40,.50,1),Amber=(.65,1,1,1))),
 6:dict(landmark='SM_SalvageGantry',prop='SM_ScrapPile',deck='SM_DeckScrap',filter=(4,.55,.35),palette=dict(Steel=(.30,.07,.04,1),SteelLight=(.60,.21,.12,1),Gold=(.85,.25,.09,1),Dark=(.07,.017,.01,1),Cyan=(1,.13,.07,1),Glass=(.30,.06,.025,1),Amber=(1,.42,.16,1))),
 7:dict(landmark='SM_SolarDish',prop='SM_SolarArray',deck='SM_DeckSolar',filter=(4,3,.4),palette=dict(Steel=(.28,.23,.06,1),SteelLight=(.64,.55,.22,1),Gold=(1,.70,.08,1),Dark=(.055,.045,.013,1),Cyan=(1,.8,.18,1),Glass=(.035,.09,.16,1),Amber=(1,.95,.50,1))),
 8:dict(landmark='SM_BloomTree',prop='SM_Vivarium',deck='SM_DeckBio',filter=(4,.65,2.4),palette=dict(Steel=(.26,.075,.17,1),SteelLight=(.58,.24,.41,1),Gold=(.32,.12,.22,1),Dark=(.05,.012,.035,1),Cyan=(1,.16,.55,1),Glass=(.24,.035,.13,1),Amber=(.70,.95,.25,1))),
}
cache={}
def material(n,name,live=False):
    key=(n,name,live)
    if key in cache: return cache[key]
    folder=BASE+'/Materials'; lib.make_directory(folder)
    label=f'MI_Exp{n}_{name}'+('_City' if live else '')
    path=folder+'/'+label
    mi=lib.load_asset(path) if lib.does_asset_exist(path) else tools.create_asset(label,folder,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    parent=lib.load_asset('/Game/Platformer/Art/Materials/M_IndustrialGlow' if live or name in ('Cyan','Glass','Amber','Red') else '/Game/Platformer/Art/Materials/M_Industrial')
    mel.set_material_instance_parent(mi,parent)
    color=themes[n]['palette'].get(name,base.get(name,base['Steel']))
    mel.set_material_instance_vector_parameter_value(mi,'Tint',unreal.LinearColor(*color))
    mel.set_material_instance_vector_parameter_value(mi,'DistrictFilter',unreal.LinearColor(*(themes[n]['filter'] if live else (1,1,1)),1))
    lib.save_loaded_asset(mi,False); cache[key]=mi
    return mi
def tint(comp,n,live=False):
    mesh=comp.get_editor_property('static_mesh')
    if not mesh: return
    for i,slot in enumerate(mesh.get_editor_property('static_materials')):
        name=str(slot.get_editor_property('material_slot_name')).replace('Scintilla_','').split('_D')[0]
        comp.set_material(i,material(n,name if name in base else 'Steel',live and i==0))
def prop(name,pos,scale,label,n):
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos),unreal.Rotator())
    a.set_actor_label('Art_Expansion_'+label); a.set_folder_path('Scintilla')
    c=a.get_component_by_class(unreal.StaticMeshComponent); c.set_static_mesh(kit[name]); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    a.set_actor_scale3d(unreal.Vector(*scale)); tint(c,n)
    return a
report=[]
for cfg in cfgs:
    n=cfg['index']; theme=themes[n]; path='/Game/Platformer/Levels/'+cfg['name']
    if not level.load_level(path): raise RuntimeError(path)
    for a in list(actors.get_all_level_actors()):
        label=a.get_actor_label()
        if isinstance(a,unreal.ScintillaEnemy): actors.destroy_actor(a); continue
        if label.startswith('Art_Expansion_') or (label.startswith('Art_') and any(s in label for s in ('_pipe','_lamp_','_crate'))):
            actors.destroy_actor(a); continue
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if label.startswith('Art_') and ('_deck_' in label or 'LiftDeck' in label): c.set_static_mesh(kit[theme['deck']])
            tint(c,n,isinstance(a,unreal.ScintillaCity))
        if isinstance(a,unreal.ScintillaCity):
            step=(cfg['goal'][0]+600)/21
            for c in a.get_components_by_class(unreal.StaticMeshComponent):
                match=re.fullmatch(r'Tower(\d+)',c.get_name())
                if match:
                    j=int(match.group(1)); mesh=kit[theme['landmark'] if j%2==0 else theme['prop']]
                    c.set_static_mesh(mesh); bounds=mesh.get_bounding_box(); size=bounds.max-bounds.min
                    c.set_relative_scale3d(unreal.Vector(320/size.x,140/size.y,(430+(j*83)%330)/size.z))
                    c.set_relative_location(unreal.Vector(-300+j*step,-400,-70),False,False); tint(c,n,True)
                elif c.get_name().startswith('Window'): c.set_visibility(False)
                elif c.get_name()=='Backdrop':
                    c.set_relative_location(unreal.Vector(cfg['goal'][0]/2,-700,350),False,False)
                    c.set_relative_scale3d(unreal.Vector((cfg['goal'][0]+2500)/100,.30,24))
                elif c.get_name().startswith('Cable'): c.set_visibility(False)
        if isinstance(a,unreal.ScintillaHazard) and not a.get_editor_property('instant_kill'):
            h=next(h for h in cfg['hazards'] if label=='ExposedCable_'+h['id'])
            a.get_editor_property('trigger').set_box_extent(unreal.Vector(h['width']/2,45,25))
    for p in cfg['platforms']:
        prop(theme['prop'],(p['x']+p['width']*.72,-170,p['top']),(.55,.6,.65),p['id']+'_prop',n)
        if p['width']>=700:
            prop(theme['landmark'],(p['x']+180,-200,p['top']),(.7,.7,.7),p['id']+'_landmark',n)
    enemy_class=lib.load_asset('/Game/Platformer/Enemies/BP_PatrolEnemy').generated_class()
    for e in cfg['enemies']:
        a=actors.spawn_actor_from_class(enemy_class,unreal.Vector(*e['position']),unreal.Rotator())
        a.set_actor_label('Drone_'+e['id']); a.set_folder_path('Scintilla')
        a.set_editor_property('patrol_min_x',e['patrol_min_x']); a.set_editor_property('patrol_max_x',e['patrol_max_x']); a.set_editor_property('speed',e['speed'])
        if 'kind' in e:
            a.set_editor_property('enemy_type',getattr(unreal.ScintillaEnemyType,e['kind'].upper())); a.configure_enemy()
    actors.set_selected_level_actors([])
    if not level.save_current_level(): raise RuntimeError('Save failed '+path)
    report.append(dict(map=path,theme=theme['landmark'],platforms=len(cfg['platforms']),landmarks=sum(a.get_actor_label().startswith('Art_Expansion_') for a in actors.get_all_level_actors()),saved=True))
lib.save_directory('/Game/Platformer',False,True)
level.load_level('/Game/Platformer/Levels/L_05_Cryo')
(ROOT/'Assets/Models/Expansion/unreal_build_report.json').write_text(json.dumps(report,indent=2))
print('EXPANSION_UNREAL_OK',report)
