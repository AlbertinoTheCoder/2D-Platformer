"""Build a rigid, single-weight robot rig and baked clips in the live Blender scene."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
OUT=ROOT/'Assets/Models/RobotRig'; OUT.mkdir(parents=True,exist_ok=True)
if not (OUT/'BeforeRobotRig.blend').exists():
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'BeforeRobotRig.blend'),copy=True)
source=(ROOT/'Scripts/create_blender_models.py').read_text()
helpers=source.split('# Friendly but')[0].replace("'Scintilla_ModelKit'","'Scintilla_Rig'")
helpers=helpers.replace("mat.node_tree.nodes.get('Principled BSDF')","next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')")
exec(helpers,globals())
OUT=ROOT/'Assets/Models/RobotRig'
robot=source.split('# Friendly but')[1].split('\n',1)[1].split("finish('SM_Scintilla',True)")[0]
exec(robot,globals())
# FBX front conversion also reverses X. Put the tool on UE's leading arm.
for obj in parts:
    if obj.name.split('.')[0]=='Wrench handle': obj.location.x=-.40
# Each metal piece belongs entirely to one bone. No soft skinning or scale keys.
def owner(obj):
    name=obj.name.split('.')[0]; side='R' if obj.location.x<0 else 'L'
    if name in ('Head shell','Recessed visor','Cyclops bezel','Optic','Brow','Antenna','Signal tip'): return 'head'
    if name in ('Arm','Shoulder joint','Hand'): return 'arm_'+side
    if name=='Wrench handle': return 'arm_R'
    if name in ('Hip','Shin'): return 'leg_'+side
    if name in ('Boot','Toe armour'): return 'foot_'+side
    return 'torso'
for obj in parts:
    # Root at the soles, preserve proportions, 78 cm to the antenna tip.
    obj.location.z-=.02
    bpy.context.view_layer.objects.active=obj
    group=obj.vertex_groups.new(name=owner(obj))
    group.add(list(range(len(obj.data.vertices))),1.0,'REPLACE')
    obj.select_set(True)
bpy.ops.object.select_all(action='DESELECT')
for obj in parts: obj.select_set(True)
bpy.context.view_layer.objects.active=parts[0]; bpy.ops.object.join()
mesh=bpy.context.object; mesh.name='SK_Scintilla'
bpy.context.scene.cursor.location=(0,0,0); bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
arm_data=bpy.data.armatures.new('ScintillaSkeleton')
rig=bpy.data.objects.new('ScintillaRig',arm_data); owned.objects.link(rig)
bpy.ops.object.select_all(action='DESELECT'); rig.select_set(True); bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
spec={'root':((0,0,0),None),'torso':((0,0,.59),'root'),'head':((0,0,.78),'torso')}
for side,x in [('L',.16),('R',-.16)]:
    spec['leg_'+side]=((x,0,.33),'root')
    spec['foot_'+side]=((x,0,.10),'leg_'+side)
    spec['arm_'+side]=((.33 if side=='L' else -.33,0,.71),'torso')
for name,(pos,parent) in spec.items():
    bone=arm_data.edit_bones.new(name); bone.head=pos; bone.tail=Vector(pos)+Vector((0,0,.1))
    if parent: bone.parent=arm_data.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT')
mod=mesh.modifiers.new('Rigid joints','ARMATURE'); mod.object=rig; mesh.parent=rig
for bone in rig.pose.bones: bone.rotation_mode='XYZ'
scene=bpy.context.scene; scene.render.fps=30
def reset():
    for b in rig.pose.bones: b.location=(0,0,0); b.rotation_euler=(0,0,0); b.scale=(1,1,1)
def angle(name,a):
    # Forward is +Y: hinge around world/local X for a genuine side-view stride.
    rig.pose.bones[name].rotation_euler.x=a
def pose(kind,t):
    reset(); p=2*math.pi*t
    if kind=='Idle':
        angle('head',.025*math.sin(p)); angle('arm_L',.035); angle('arm_R',-.035)
    elif kind=='Run':
        for side,sign in [('L',1),('R',-1)]:
            # Short mechanical steps keep the wide boots from intersecting.
            swing=.45*math.sin(p)*sign
            angle('leg_'+side,swing); angle('foot_'+side,-swing)
            rig.pose.bones['leg_'+side].location.y=-.23*(1-math.cos(swing))
            angle('arm_'+side,-swing*.7)
        # The torso stays rigid; the head remains readable.
        angle('head',.015*math.sin(p))
    elif kind in ('Jump','Fall'):
        k=1 if kind=='Jump' else .55
        angle('leg_L',-.22*k); angle('leg_R',.22*k)
        angle('foot_L',.22*k); angle('foot_R',-.22*k)
        angle('arm_L',-.30*k); angle('arm_R',.30*k)
    elif kind=='Land':
        k=math.sin(math.pi*t)*.18
        angle('leg_L',-k); angle('leg_R',k); angle('foot_L',k); angle('foot_R',-k)
        angle('arm_L',-.15*math.sin(math.pi*t)); angle('arm_R',.15*math.sin(math.pi*t))
    elif kind=='Attack':
        a=math.sin(math.pi*t)
        angle('arm_R',-1.25*a); angle('arm_L',-.18*a); angle('head',-.08*a)
    elif kind=='Hurt':
        angle('torso',.12*math.sin(math.pi*t)); angle('arm_L',-.3); angle('arm_R',.3)
    elif kind=='Death':
        angle('torso',min(t*2,1)*1.1); angle('head',.25); angle('arm_L',-.4); angle('arm_R',.4)
clips={'Idle':60,'Run':20,'Jump':12,'Fall':12,'Land':8,'Attack':9,'Hurt':12,'Death':24}
actions={}
rig.animation_data_create()
# Export the entire rig with a common uniform scale and front orientation.
rig.scale=(.56,.56,.56); rig.rotation_euler.z=math.pi
def export(name,animated):
    bpy.ops.object.select_all(action='DESELECT'); rig.select_set(True); mesh.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,
        object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',add_leaf_bones=False,
        use_mesh_modifiers=True,bake_anim=animated,bake_anim_use_all_actions=False,
        bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,
        bake_anim_force_startend_keying=True)
reset(); scene.frame_set(1); export('SK_Scintilla',False)
for kind,count in clips.items():
    action=bpy.data.actions.new('A_Scintilla_'+kind); rig.animation_data.action=action
    actions[kind]=action
    scene.frame_start=1; scene.frame_end=count+1
    for frame in range(1,count+2):
        scene.frame_set(frame); pose(kind,(frame-1)/count)
        for b in rig.pose.bones:
            b.keyframe_insert('rotation_euler',frame=frame); b.keyframe_insert('location',frame=frame)
    export('A_Scintilla_'+kind,True)
# Verify topology and rigid weights before handing the files to Unreal.
assert all(len(v.groups)==1 and abs(v.groups[0].weight-1)<1e-5 for v in mesh.data.vertices)
rig.animation_data.action=actions['Idle']; scene.frame_start=1; scene.frame_end=61; scene.frame_set(1)
rig.show_in_front=True
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Scintilla_Rig.blend'),copy=True)
(OUT/'manifest.json').write_text(json.dumps({'bones':list(spec),'clips':clips,'vertices':len(mesh.data.vertices),'rigid_weights':True,'scale':.56},indent=2))
print('ROBOT_RIG_OK',len(spec),'bones',len(clips),'clips')
