"""Import original Blender kit and dress the existing level, preserving gameplay collision."""
import unreal
import json
import re
from pathlib import Path

ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
exec((ROOT/'Scripts/robot_material_animation.py').read_text(),globals())
OUT=ROOT/'Assets/Models'
BASE='/Game/Platformer/Art'
lib=unreal.EditorAssetLibrary
tools=unreal.AssetToolsHelpers.get_asset_tools()
mel=unreal.MaterialEditingLibrary
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
lib.make_directory(BASE+'/Meshes'); lib.make_directory(BASE+'/Materials')
if not level.save_current_level(): raise RuntimeError('Save before import failed')
if not level.load_level('/Game/Platformer/Levels/L_Platformer_Prototype'):
    raise RuntimeError('Prototype map missing')
if not (ROOT/'Assets/Models/L_Platformer_before_art.umap').exists():
    # Asset duplicate is a safe recovery point including serialized components.
    if not lib.does_asset_exist('/Game/Platformer/Levels/L_Platformer_BeforeArt'):
        lib.duplicate_asset('/Game/Platformer/Levels/L_Platformer_Prototype','/Game/Platformer/Levels/L_Platformer_BeforeArt')
        lib.save_asset('/Game/Platformer/Levels/L_Platformer_BeforeArt',False)

def asset(name, cls, factory):
    path=BASE+'/Materials/'+name
    return lib.load_asset(path) if lib.does_asset_exist(path) else tools.create_asset(name,BASE+'/Materials',cls,factory)

def shader(name, glow=False):
    mat=asset(name,unreal.Material,unreal.MaterialFactoryNew())
    mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
    mel.delete_all_material_expressions(mat)
    tint=mel.create_material_expression(mat,unreal.MaterialExpressionVectorParameter,-650,0)
    tint.set_editor_property('parameter_name','Tint'); tint.set_editor_property('default_value',unreal.LinearColor(.3,.4,.5,1))
    district=mel.create_material_expression(mat,unreal.MaterialExpressionVectorParameter,-650,-180)
    district.set_editor_property('parameter_name','DistrictFilter'); district.set_editor_property('default_value',unreal.LinearColor(1,1,1,1))
    filtered=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-440,0)
    assert mel.connect_material_expressions(tint,'',filtered,'A')
    assert mel.connect_material_expressions(district,'',filtered,'B')
    if glow:
        mel.connect_material_property(filtered,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    else:
        normal=mel.create_material_expression(mat,unreal.MaterialExpressionPixelNormalWS,-650,200)
        light=mel.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-650,350)
        light.set_editor_property('constant',unreal.LinearColor(.25,.65,.72,1))
        dot=mel.create_material_expression(mat,unreal.MaterialExpressionDotProduct,-440,200)
        mel.connect_material_expressions(normal,'',dot,'A'); mel.connect_material_expressions(light,'',dot,'B')
        clamp=mel.create_material_expression(mat,unreal.MaterialExpressionClamp,-280,200)
        clamp_input=mel.get_material_expression_input_names(clamp)[0]
        if not mel.connect_material_expressions(dot,'',clamp,clamp_input):
            raise RuntimeError('Could not connect shading clamp input '+clamp_input)
        mult=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-120,200)
        mult.set_editor_property('const_b',.7); mel.connect_material_expressions(clamp,'',mult,'A')
        add=mel.create_material_expression(mat,unreal.MaterialExpressionAdd,20,200)
        add.set_editor_property('const_b',.3); mel.connect_material_expressions(mult,'',add,'A')
        result=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,180,0)
        mel.connect_material_expressions(filtered,'',result,'A'); mel.connect_material_expressions(add,'',result,'B')
        mel.connect_material_property(result,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    configure_robot_animation(mat)
    mel.recompile_material(mat); lib.save_loaded_asset(mat,False)
    return mat

solid=shader('M_Industrial'); glow=shader('M_IndustrialGlow',True)
palette=json.loads((OUT/'manifest.json').read_text())['palette']
mats={}
for name,col in palette.items():
    mi=asset('MI_Kit_'+name,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi,glow if name in ('Cyan','Amber','Red','Glass') else solid)
    mel.set_material_instance_vector_parameter_value(mi,'Tint',unreal.LinearColor(*col))
    lib.save_loaded_asset(mi,False); mats[name]=mi

meshes={}
for source in sorted(OUT.glob('*.fbx')):
    task=unreal.AssetImportTask()
    task.set_editor_property('filename',str(source)); task.set_editor_property('destination_path',BASE+'/Meshes')
    task.set_editor_property('destination_name',source.stem); task.set_editor_property('automated',True)
    task.set_editor_property('replace_existing',True); task.set_editor_property('save',True)
    options=unreal.FbxImportUI()
    options.set_editor_property('import_mesh',True); options.set_editor_property('import_as_skeletal',False)
    options.set_editor_property('import_materials',True); options.set_editor_property('import_textures',False)
    options.set_editor_property('mesh_type_to_import',unreal.FBXImportType.FBXIT_STATIC_MESH)
    options.static_mesh_import_data.set_editor_property('combine_meshes',True)
    options.static_mesh_import_data.set_editor_property('auto_generate_collision',False)
    options.static_mesh_import_data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)
    task.set_editor_property('options',options)
    tools.import_asset_tasks([task])
    mesh=lib.load_asset(BASE+'/Meshes/'+source.stem)
    if not isinstance(mesh,unreal.StaticMesh): raise RuntimeError('Missing imported mesh: '+source.stem)
    for i,slot in enumerate(mesh.get_editor_property('static_materials')):
        name=str(slot.get_editor_property('material_slot_name')).replace('Scintilla_','')
        if name not in mats: raise RuntimeError('Unknown Blender material slot '+name)
        mesh.set_material(i,mats[name])
    lib.save_loaded_asset(mesh,False); meshes[source.stem]=mesh
    print('KIT_IMPORTED',source.stem,mesh.get_bounding_box())

def set_visual(comp,name,scale=None):
    comp.set_static_mesh(meshes[name])
    # Remove old cube material overrides; retain authored Blender material slots.
    comp.set_editor_property('override_materials',[])
    if scale: comp.set_relative_scale3d(unreal.Vector(*scale))

bp=lib.load_asset('/Game/Platformer/Characters/BP_Player')
cdo=unreal.get_default_object(bp.generated_class())
set_visual(cdo.get_editor_property('body'),'SM_Scintilla')
cdo.get_editor_property('eye').set_visibility(False)
unreal.BlueprintEditorLibrary.compile_blueprint(bp); lib.save_loaded_asset(bp,False)

for name,meshname in (('BP_Coin','SM_Energy'),('BP_PatrolEnemy','SM_Drone')):
    folder='Pickups' if name=='BP_Coin' else 'Enemies'
    bp=lib.load_asset('/Game/Platformer/'+folder+'/'+name)
    set_visual(unreal.get_default_object(bp.generated_class()).get_editor_property('visual'),meshname)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp); lib.save_loaded_asset(bp,False)

# Decoration-only meshes keep collision of existing platforms and triggers intact.
for actor in list(actors.get_all_level_actors()):
    if actor.get_actor_label().startswith('Art_'): actors.destroy_actor(actor)

def prop(name,pos,scale=(1,1,1),label='',parent=None):
    actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos),unreal.Rotator())
    actor.set_actor_label('Art_'+(label or name))
    comp=actor.get_component_by_class(unreal.StaticMeshComponent)
    comp.set_mobility(unreal.ComponentMobility.MOVABLE if parent else unreal.ComponentMobility.STATIC)
    comp.set_static_mesh(meshes[name]); comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    actor.set_actor_scale3d(unreal.Vector(*scale))
    if parent:
        actor.attach_to_actor(parent,'',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
    return actor

for actor in actors.get_all_level_actors():
    if isinstance(actor,unreal.ScintillaCoin): set_visual(actor.get_editor_property('visual'),'SM_Energy')
    elif isinstance(actor,unreal.ScintillaEnemy): set_visual(actor.get_editor_property('visual'),'SM_Drone')
    elif isinstance(actor,unreal.ScintillaGoal):
        set_visual(actor.get_editor_property('visual'),'SM_Generator',(1.4,.9,2.1))
        actor.get_editor_property('visual').set_relative_location(unreal.Vector(0,0,55),False,False)
    elif isinstance(actor,unreal.ScintillaCheckpoint):
        set_visual(actor.get_editor_property('visual'),'SM_Checkpoint',(.65,.6,1.5))
        actor.get_editor_property('visual').set_relative_location(unreal.Vector(0,0,25),False,False)
    elif isinstance(actor,unreal.ScintillaHazard) and not actor.get_editor_property('instant_kill'):
        set_visual(actor.get_editor_property('visual'),'SM_Electrodes',(1,.5,.4))
    elif isinstance(actor,unreal.ScintillaCity):
        for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
            match=re.fullmatch(r'Tower(\d+)',comp.get_name())
            if match:
                n=int(match.group(1)); height=380+(n*137)%430
                set_visual(comp,'SM_Facade',(.725,2.1,height/450))
                pos=comp.get_editor_property('relative_location'); pos.z=-70
                comp.set_relative_location(pos,False,False)
                comp.set_material(0,mats['Brick'])
            window=re.fullmatch(r'Window(\d+)_(\d+)',comp.get_name())
            if window:
                n,j=map(int,window.groups()); height=380+(n*137)%430
                comp.set_relative_location(unreal.Vector(-300+n*400+(-83 if j%2==0 else 83),-310,-70+(135 if j<2 else 315)*height/450),False,False)
                comp.set_relative_scale3d(unreal.Vector(.44,.1,.72*height/450))
    elif isinstance(actor,unreal.TextRenderActor):
        actor.set_actor_rotation(unreal.Rotator(0,-90,0),False)

config=json.loads((ROOT/'Config/platformer.json').read_text())['level']
platforms={a.get_actor_label():a for a in actors.get_all_level_actors() if isinstance(a,unreal.ScintillaPlatform)}
for p in config['platforms']:
    for i in range((p['width']+199)//200):
        width=min(200,p['width']-i*200)
        prop('SM_Deck',(p['x']+i*200+width/2,0,p['top']+1),(width/200,2,1),p['id']+'_deck_'+str(i))
    for i,x in enumerate((p['x']+90,p['x']+p['width']-110)):
        if p['width']>500:
            prop('SM_Lamp',(x,-100,p['top']),(1,1,1),p['id']+'_lamp_'+str(i))
    prop('SM_Pipe',(p['x']+p['width']*.70,-130,p['top']),(.8,.8,.8),p['id']+'_pipe')
    if p['width']>600:
        for i in range(2): prop('SM_Crate',(p['x']+150+i*86,-100,p['top']),(.7,.7,.7),p['id']+'_crate_'+str(i))
bridge=platforms.get('MovingPlatform_ServiceLift')
if bridge:
    loc=bridge.get_actor_location()
    prop('SM_Deck',(loc.x,loc.y,loc.z+16),(1.1,1.5,.65),'MovingLiftDeck',bridge)
actors.set_selected_level_actors([])
if not level.save_current_level(): raise RuntimeError('Level save failed')
lib.save_directory('/Game/Platformer',False,True)
(OUT/'unreal_import_report.json').write_text(json.dumps({'imported':list(meshes),'decorations':sum(a.get_actor_label().startswith('Art_') for a in actors.get_all_level_actors()),'saved':True},indent=2))
print('SCINTILLA_ART_IMPORT_OK')
