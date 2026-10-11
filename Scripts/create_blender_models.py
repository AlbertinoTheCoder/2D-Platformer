"""Original bevelled industrial models, export FBX and a Blender source scene."""
import bpy
import math
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
OUT = ROOT / 'Assets/Models'
OUT.mkdir(parents=True, exist_ok=True)
PALETTE = {
    'Steel': (.12,.19,.23,1), 'SteelLight': (.30,.40,.43,1),
    'Gold': (.83,.49,.12,1), 'Dark': (.025,.045,.065,1),
    'Cyan': (.1,.85,.85,1), 'Amber': (1,.64,.17,1),
    'Red': (.85,.10,.12,1), 'Brick': (.20,.23,.29,1),
    'Concrete': (.30,.33,.35,1), 'Glass': (.10,.27,.33,1),
}
materials = {}
for name, color in PALETTE.items():
    mat = bpy.data.materials.get('Scintilla_' + name) or bpy.data.materials.new('Scintilla_' + name)
    mat.diffuse_color = color
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Metallic'].default_value = .65 if name in ('Steel','SteelLight','Gold') else .1
    shader.inputs['Roughness'].default_value = .35
    if name in ('Cyan','Amber','Red'):
        shader.inputs['Emission Color'].default_value = color
        shader.inputs['Emission Strength'].default_value = 2
    materials[name] = mat

owned = bpy.data.collections.get('Scintilla_ModelKit')
if owned:
    for obj in list(owned.all_objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(owned)
owned = bpy.data.collections.new('Scintilla_ModelKit')
bpy.context.scene.collection.children.link(owned)
parts = []
models = {}

def adopt(obj, name, material):
    obj.name = name
    for coll in list(obj.users_collection):
        coll.objects.unlink(obj)
    owned.objects.link(obj)
    obj.data.materials.append(materials[material])
    parts.append(obj)
    return obj

def box(name, pos, size, material='Steel', bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    obj = adopt(bpy.context.object, name, material)
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new('Machined edge', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj

def cylinder(name, pos, radius, depth, material='Steel', axis='Z', vertices=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=pos)
    obj = adopt(bpy.context.object, name, material)
    if axis == 'Y': obj.rotation_euler.x = math.pi/2
    if axis == 'X': obj.rotation_euler.y = math.pi/2
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    mod = obj.modifiers.new('Rim bevel', 'BEVEL'); mod.width=.012; mod.segments=2
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj

def cable(name, points, radius=.025, material='Dark'):
    data = bpy.data.curves.new(name, 'CURVE'); data.dimensions='3D'; data.bevel_depth=radius; data.bevel_resolution=2
    spline=data.splines.new('POLY'); spline.points.add(len(points)-1)
    for p, xyz in zip(spline.points, points): p.co=(*xyz,1)
    obj=bpy.data.objects.new(name,data); owned.objects.link(obj); obj.data.materials.append(materials[material])
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); bpy.context.view_layer.objects.active=obj
    bpy.ops.object.convert(target='MESH'); parts.append(bpy.context.object)

def finish(name, normalize=False):
    global parts
    bpy.ops.object.select_all(action='DESELECT')
    for obj in parts: obj.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]
    bpy.ops.object.join()
    obj=bpy.context.object; obj.name=name
    bpy.context.scene.cursor.location=(0,0,0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    if normalize:
        # Native components still squash a unit-cube-sized visual at runtime.
        coords=[v.co.copy() for v in obj.data.vertices]
        lo=Vector([min(v[i] for v in coords) for i in range(3)])
        hi=Vector([max(v[i] for v in coords) for i in range(3)])
        center=(lo+hi)/2; size=hi-lo
        for v in obj.data.vertices:
            v.co=Vector([(v.co[i]-center[i])/size[i] for i in range(3)])
    # FBX's handedness conversion reverses Y: author the front for UE's +Y camera.
    obj.rotation_euler.z=math.pi
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')), use_selection=True,
        object_types={'MESH'}, axis_forward='-Y', axis_up='Z', add_leaf_bones=False,
        use_mesh_modifiers=True, bake_anim=False)
    obj.rotation_euler.z=math.pi
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    models[name]=obj; parts=[]

# Friendly but weathered maintenance robot: visor, antenna, battery, boots and tool.
box('Battery torso',(0,0,.61),(.54,.32,.46),'Gold',.07)
box('Head shell',(0,0,1.00),(.64,.37,.40),'Gold',.09)
box('Recessed visor',(0,.193,1.01),(.52,.055,.22),'Dark',.065)
cylinder('Cyclops bezel',(0,.232,1.01),.095,.035,'SteelLight','Y')
cylinder('Optic',(0,.255,1.01),.069,.035,'Cyan','Y')
box('Brow',(0,.233,1.15),(.49,.035,.035),'SteelLight',.008)
cylinder('Neck',(0,0,.80),.10,.09)
for side in (-1,1):
    cylinder('Shoulder joint',(side*.33,0,.73),.08,.12,'SteelLight','X')
    box('Arm',(side*.37,0,.57),(.13,.19,.24),'Steel',.04)
    cylinder('Hand',(side*.37,.07,.44),.08,.17,'SteelLight','Y')
    cylinder('Hip',(side*.16,0,.35),.07,.15,'SteelLight','X')
    box('Shin',(side*.16,0,.23),(.16,.18,.22),'Steel',.025)
    box('Boot',(side*.16,.055,.085),(.23,.32,.13),'Dark',.035)
    box('Toe armour',(side*.16,.205,.10),(.18,.04,.06),'SteelLight',.01)
    cylinder('Torso rivet',(side*.21,.172,.70),.019,.02,'SteelLight','Y',12)
box('Chest battery frame',(0,.176,.58),(.33,.035,.18),'Dark',.02)
for n in range(3): box('Battery cell',(-.09+n*.09,.201,.58),(.065,.025,.11),'Cyan',.01)
cylinder('Antenna',(-.22,0,1.29),.018,.22,'SteelLight')
cylinder('Signal tip',(-.22,0,1.40),.035,.035,'Amber')
box('Backpack',(0,-.23,.59),(.35,.15,.30),'Steel',.035)
box('Wrench handle',(.40,.18,.35),(.035,.035,.22),'Gold',.005)
finish('SM_Scintilla',True)

# Faulty security drone.
box('Drone shell',(0,0,.20),(.65,.40,.32),'SteelLight',.12)
box('Eye mask',(0,.215,.22),(.48,.045,.14),'Dark',.04)
box('Hostile optic',(0,.244,.22),(.22,.025,.055),'Red',.016)
for x in (-.46,.46):
    box('Rotor arm',(x*.7,0,.20),(.34,.07,.08),'Steel',.02)
    cylinder('Rotor housing',(x,0,.23),.17,.08,'Dark')
    box('Rotor blade',(x,0,.28),(.27,.055,.015),'SteelLight',.003)
cable('Dangling wire',[(-.1,-.1,.03),(-.15,0,-.12),(-.1,.08,-.20)],.016,'Red')
finish('SM_Drone',True)

# Generator with ribs, copper coils, gauge and status strips.
box('Foot',(0,0,.1),(1.3,.8,.2),'Dark',.045)
box('Cabinet',(0,0,.75),(1.05,.65,1.2),'Steel',.08)
box('Face',(0,.34,.76),(.87,.045,1.01),'SteelLight',.04)
cylinder('Gauge bezel',(-.24,.38,1.05),.16,.06,'Dark','Y')
cylinder('Gauge glass',(-.24,.42,1.05),.12,.025,'Cyan','Y')
for x in (.1,.24,.38): cylinder('Coil',(x,.40,.72),.045,.66,'Gold')
for z in (.34,.43): box('Vent',(0,.382,z),(.65,.018,.035),'Dark',.004)
box('Power core',(0,.37,1.37),(.45,.07,.10),'Amber',.02)
cable('Power cable',[(.51,0,1),(.72,0,1.05),(.78,0,.3),(.55,0,.15)],.04)
finish('SM_Generator',True)

# Maintenance checkpoint.
box('Plinth',(0,0,.06),(.46,.40,.12),'Dark',.02)
box('Charging tower',(0,0,.63),(.30,.24,1.08),'Steel',.05)
box('Charging face',(0,.135,.66),(.22,.04,.79),'Dark',.025)
for z in (.42,.65,.88): box('Charge strip',(0,.166,z),(.15,.025,.09),'Cyan',.012)
cable('Charging lead',[(.16,0,.85),(.29,0,.8),(.30,0,.3),(.18,.1,.2)],.018,'Gold')
finish('SM_Checkpoint',True)

# Modular props at real metric size, imported at centimetres by UE.
box('Lamp base',(0,0,.08),(.5,.42,.16),'Dark',.04)
cylinder('Lamp post',(0,0,1.55),.055,2.9,'SteelLight')
cable('Crooked neck',[(0,0,2.95),(.07,0,3.12),(.32,0,3.16),(.55,0,3.04)],.055,'SteelLight')
box('Lamp hood',(.53,0,3.02),(.55,.42,.17),'Dark',.06)
box('Lamp lens',(.53,0,2.94),(.40,.28,.045),'Amber',.015)
finish('SM_Lamp')

box('Crate',(0,0,.45),(.9,.65,.9),'Steel',.045)
for x in (-.38,.38): box('Corner rail',(x,.34,.45),(.07,.055,.80),'SteelLight',.012)
for z in (.08,.82): box('Rim rail',(0,.35,z),(.83,.055,.075),'SteelLight',.012)
for x in (-.22,0,.22): box('Crate vent',(x,.36,.46),(.055,.025,.45),'Dark',.01)
box('Warning plate',(0,.372,.20),(.33,.015,.11),'Gold',.004)
finish('SM_Crate')

box('Duct block',(0,0,1.3),(.35,.42,2.6),'Steel',.03)
for z in (.2,1.2,2.2): box('Pipe collar',(0,.01,z),(.43,.48,.09),'SteelLight',.01)
cable('Elbow',[(0,0,2.6),(0,0,2.8),(.2,0,2.98),(.65,0,3.02),(1.2,0,3.02)],.15,'Steel')
box('Outlet grille',(1.2,0,3.02),(.12,.44,.44),'Dark',.02)
finish('SM_Pipe')

box('Wall',(0,0,2.25),(4,.38,4.5),'Brick',.035)
for x in (-1.82,1.82): box('Pillar',(x,.25,2.25),(.18,.18,4.5),'Dark',.02)
for z in (.25,2.2,4.35): box('Cornice',(0,.27,z),(4,.22,.12),'Steel',.015)
for x in (-1.15,0,1.15):
    for z in (1.35,3.15):
        box('Window recess',(x,.21,z),(.81,.045,1.25),'Dark',.015)
        box('Window glass',(x,.24,z),(.64,.025,1.07),'Glass',.008)
        box('Window mullion',(x,.265,z),(.035,.025,1.08),'SteelLight',.003)
        box('Window sill',(x,.29,z-.59),(.92,.16,.08),'Steel',.012)
for z in (.65,2.65,3.95):
    for x in (-1.4,-.7,0,.7,1.4): box('Brick joint',(x,.20,z),(.53,.015,.018),'Dark',0)
cable('Wall conduit',[(1.65,.35,.4),(1.65,.35,2.8),(1.45,.35,2.95)],.03,'Gold')
finish('SM_Facade')

box('Platform slab',(0,0,-.20),(2.0,1,-.0+.4),'Steel',.025)
box('Walk surface',(0,0,.015),(2.0,1,.04),'Concrete',.008)
box('Front edge',(0,.52,-.07),(2.0,.055,.12),'Dark',.008)
for x in (-.85,-.6,-.35,-.1,.15,.4,.65,.9):
    stripe=box('Warning chevron',(x,.556,-.07),(.075,.02,.09),'Gold',.003)
    stripe.rotation_euler.y=-.35
for x in (-.65,.65): box('Support beam',(x,0,-.46),(.18,.9,.15),'Dark',.01)
finish('SM_Deck')

bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.22,location=(0,0,0))
obj=adopt(bpy.context.object,'Energy crystal','Cyan'); obj.scale=(.65,.65,1.4)
for z in (-.24,.24): cylinder('Energy cap',(0,0,z),.11,.06,'Gold')
finish('SM_Energy',True)

box('Hazard base',(0,0,0),(1,.5,.1),'Dark',.01)
for x in (-.35,0,.35):
    bpy.ops.mesh.primitive_cone_add(vertices=6,radius1=.14,radius2=.012,depth=.37,location=(x,0,.23))
    adopt(bpy.context.object,'Live electrode','SteelLight')
    cylinder('Warning collar',(x,0,.075),.15,.045,'Red')
finish('SM_Electrodes',True)

# Gallery arrangement keeps all source models editable and visible in Blender.
for i,(name,obj) in enumerate(models.items()): obj.location=(i%4*5,i//4*5,0)
scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.world.color=(.08,.08,.08)
bpy.ops.object.camera_add(location=(3.8,6,3))
cam=bpy.context.object; cam.name='Scintilla_PreviewCamera'
for coll in list(cam.users_collection): coll.objects.unlink(cam)
owned.objects.link(cam)
target=Vector((0,0,0)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'; cam.data.ortho_scale=1.85; scene.camera=cam
for pos,power,color,size in (((2,3,4),500,(.55,.8,1),4),((-2,1,2),350,(1,.62,.25),3),((0,-2,3),700,(.35,.7,1),3)):
    bpy.ops.object.light_add(type='AREA',location=pos)
    light=bpy.context.object; light.data.energy=power; light.data.color=color; light.data.shape='DISK';light.data.size=size
    light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
    for coll in list(light.users_collection): coll.objects.unlink(light)
    owned.objects.link(light)
for obj in list(scene.objects): obj.hide_render=obj.name not in owned.all_objects
for obj in models.values(): obj.hide_render=obj.name!='SM_Scintilla'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Scintilla_ModelKit.blend'))
scene.render.filepath=str(OUT/'Scintilla_preview.png')
bpy.ops.render.render(write_still=True)
(OUT/'manifest.json').write_text(json.dumps({'models':list(models),'palette':PALETTE},indent=2))
print('SCINTILLA_MODELS_OK',len(models))
