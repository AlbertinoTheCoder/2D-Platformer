"""Back up maps, soften district 3, import landmarks and apply isolated palettes."""
import unreal
import json
import re
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
lib=unreal.EditorAssetLibrary
tools=unreal.AssetToolsHelpers.get_asset_tools()
mel=unreal.MaterialEditingLibrary
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
cfgs=json.loads((ROOT/'Config/campaign.json').read_text())['levels']
lib.save_directory('/Game/Platformer',False,True)
for cfg in cfgs:
    src='/Game/Platformer/Levels/'+cfg['name']; backup=src+'_BeforeDistrictRevision'
    if not lib.does_asset_exist(backup):
        if not lib.duplicate_asset(src,backup): raise RuntimeError('Backup failed '+src)
        lib.save_asset(backup,False)

# Regenerate shared parents with a neutral-by-default district filter.
exec((ROOT/'Scripts/import_model_kit.py').read_text().split('meshes={}')[0],globals())
for name in ('SM_Furnace','SM_Tank','SM_Fan','SM_Relay'):
    task=unreal.AssetImportTask(); task.set_editor_property('filename',str(ROOT/'Assets/Models'/f'{name}.fbx'))
    task.set_editor_property('destination_path','/Game/Platformer/Art/Meshes'); task.set_editor_property('destination_name',name)
    task.set_editor_property('automated',True); task.set_editor_property('save',True); task.set_editor_property('replace_existing',True)
    opt=unreal.FbxImportUI(); opt.set_editor_property('import_materials',True); opt.set_editor_property('import_textures',False)
    opt.set_editor_property('mesh_type_to_import',unreal.FBXImportType.FBXIT_STATIC_MESH)
    opt.static_mesh_import_data.set_editor_property('combine_meshes',True); opt.static_mesh_import_data.set_editor_property('auto_generate_collision',False)
    task.set_editor_property('options',opt); tools.import_asset_tasks([task])
    mesh=lib.load_asset('/Game/Platformer/Art/Meshes/'+name)
    if not mesh: raise RuntimeError(name)
    for i,s in enumerate(mesh.get_editor_property('static_materials')):
        matname=str(s.get_editor_property('material_slot_name')).replace('Scintilla_','')
        mesh.set_material(i,mats[matname])
    lib.save_loaded_asset(mesh,False)

# Rebuild the softened canal route and the safer last landing in the tower.
exec((ROOT/'Scripts/build_campaign.py').read_text(),dict(REBUILD_OWNED_MAPS={'L_03_Condotte','L_04_Torre'}))
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
meshes={p.stem:lib.load_asset('/Game/Platformer/Art/Meshes/'+p.stem) for p in (ROOT/'Assets/Models').glob('*.fbx')}
base=json.loads((ROOT/'Assets/Models/manifest.json').read_text())['palette']
themes={
    2:dict(filter=(4,1,.35),landmark='SM_Furnace',palette=dict(Steel=(.27,.13,.07,1),SteelLight=(.60,.33,.18,1),Gold=(1,.32,.055,1),Brick=(.23,.085,.04,1),Dark=(.065,.025,.013,1),Concrete=(.34,.21,.14,1),Glass=(.27,.075,.018,1),Cyan=(1,.32,.06,1),Amber=(1,.48,.06,1))),
    3:dict(filter=(.65,3,.75),landmark='SM_Tank',palette=dict(Steel=(.065,.22,.13,1),SteelLight=(.23,.48,.29,1),Gold=(.48,.72,.09,1),Brick=(.035,.13,.065,1),Dark=(.012,.04,.018,1),Concrete=(.20,.35,.25,1),Glass=(.045,.23,.085,1),Cyan=(.10,.75,.22,1),Amber=(.7,1,.14,1))),
    4:dict(filter=(3,.7,3),landmark='SM_Relay',palette=dict(Steel=(.19,.085,.30,1),SteelLight=(.48,.28,.66,1),Gold=(.82,.16,.55,1),Brick=(.13,.04,.22,1),Dark=(.025,.01,.06,1),Concrete=(.33,.20,.45,1),Glass=(.19,.06,.33,1),Cyan=(.62,.19,1,1),Amber=(1,.27,.67,1))),
}
material_cache={}
def themed(n,name,live=False,sky=False):
    key=(n,name,live,sky)
    if key in material_cache: return material_cache[key]
    suffix=('Live' if live else '')+('Sky' if sky else '')+name
    path=f'/Game/Platformer/Art/Materials/Districts/MI_D{n}_{suffix}'
    lib.make_directory('/Game/Platformer/Art/Materials/Districts')
    mi=lib.load_asset(path) if lib.does_asset_exist(path) else tools.create_asset(path.rsplit('/',1)[1],path.rsplit('/',1)[0],unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    parent=lib.load_asset('/Game/Platformer/Art/Materials/M_IndustrialGlow' if sky or name in ('Glass','Cyan','Amber','Red') else '/Game/Platformer/Art/Materials/M_Industrial')
    mel.set_material_instance_parent(mi,parent)
    color=themes[n]['palette'].get(name,base.get(name,base['Steel']))
    mel.set_material_instance_vector_parameter_value(mi,'Tint',unreal.LinearColor(*color))
    mel.set_material_instance_vector_parameter_value(mi,'DistrictFilter',unreal.LinearColor(*(themes[n]['filter'] if live else (1,1,1)),1))
    lib.save_loaded_asset(mi,False); material_cache[key]=mi
    return mi

def color_component(comp,n,live=False,sky=False):
    mesh=comp.get_editor_property('static_mesh')
    if not mesh: return
    for i,s in enumerate(mesh.get_editor_property('static_materials')):
        name=str(s.get_editor_property('material_slot_name')).replace('Scintilla_','')
        comp.set_material(i,themed(n,name if name in base else 'Steel',live and i==0,sky))

def decoration(meshname,pos,scale,label,n):
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos),unreal.Rotator())
    a.set_actor_label('Art_District_'+label); a.set_folder_path('Scintilla')
    c=a.get_component_by_class(unreal.StaticMeshComponent); c.set_static_mesh(meshes[meshname])
    c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); a.set_actor_scale3d(unreal.Vector(*scale)); color_component(c,n)

report=[]
for cfg in cfgs[1:]:
    n=cfg['index']; path='/Game/Platformer/Levels/'+cfg['name']
    if not level.load_level(path): raise RuntimeError(path)
    for a in list(actors.get_all_level_actors()):
        label=a.get_actor_label()
        if label.startswith('Art_District_') or (label.startswith('Art_') and ('_pipe' in label or '_crate' in label or ('_lamp_' in label and n in (2,4)))):
            actors.destroy_actor(a); continue
        if label.startswith('Art_') or isinstance(a,(unreal.ScintillaGoal,unreal.ScintillaCheckpoint)):
            for c in a.get_components_by_class(unreal.StaticMeshComponent): color_component(c,n)
        if isinstance(a,unreal.ScintillaCity):
            for c in a.get_components_by_class(unreal.StaticMeshComponent):
                match=re.fullmatch(r'Tower(\d+)',c.get_name())
                if match:
                    tower=int(match.group(1))
                    if tower%3:
                        mesh=meshes[themes[n]['landmark']]; h=380+(tower*137)%430+n*20
                        bounds=mesh.get_bounding_box(); size=bounds.max-bounds.min
                        c.set_static_mesh(mesh); c.set_editor_property('override_materials',[])
                        c.set_relative_scale3d(unreal.Vector(280/size.x,100/size.y,h/size.z))
                        p=c.get_editor_property('relative_location'); p.z=-70; c.set_relative_location(p,False,False)
                win=re.fullmatch(r'Window(\d+)_(\d+)',c.get_name())
                if win: c.set_visibility(int(win.group(1))%3==0)
                color_component(c,n,live=True,sky=bool(win) or c.get_name()=='Backdrop')
    for p in cfg['platforms']:
        if p['width']>500:
            decoration(themes[n]['landmark'],(p['x']+p['width']*.65,-150,p['top']),(.65,.65,.65),p['id']+'_landmark',n)
            if n==3: decoration('SM_Fan',(p['x']+150,-160,p['top']),(.55,.55,.55),p['id']+'_fan',n)
            if n==2: decoration('SM_Fan',(p['x']+110,-200,p['top']+160),(.5,.5,.5),p['id']+'_extractor',n)
        elif n==4:
            decoration('SM_Relay',(p['x']+p['width']/2,-150,p['top']),(.35,.45,.45),p['id']+'_beacon',n)
    actors.set_selected_level_actors([])
    if not level.save_current_level(): raise RuntimeError('Save failed '+path)
    report.append(dict(map=path,theme=themes[n]['landmark'],saved=True))
lib.save_directory('/Game/Platformer',False,True)
level.load_level('/Game/Platformer/Levels/L_03_Condotte')
(ROOT/'Assets/Models/district_revision_report.json').write_text(json.dumps(report,indent=2))
print('SCINTILLA_DISTRICT_REVISION_OK')
