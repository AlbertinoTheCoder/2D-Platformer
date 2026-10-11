"""Author an original industrial obstacle kit in the connected Blender."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
OUT=ROOT/'Assets/Models/Difficulty'; OUT.mkdir(parents=True,exist_ok=True)
if not (OUT/'BeforeDifficultyModels.blend').exists(): bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'BeforeDifficultyModels.blend'),copy=True)
bpy.ops.scene.new(type='NEW'); bpy.context.scene.name='Scintilla Difficulty Kit'
source=(ROOT/'Scripts/create_blender_models.py').read_text().split('# Friendly but')[0]
source=source.replace("OUT = ROOT / 'Assets/Models'","OUT = ROOT / 'Assets/Models/Difficulty'").replace('Scintilla_ModelKit','Scintilla_DifficultyKit').replace("'Scintilla_'","'Scintilla_Difficulty_'")
source=source.replace("mat.node_tree.nodes.get('Principled BSDF')","next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')")
exec(source,globals())
PALETTE={'Steel':(.12,.22,.28,1),'SteelLight':(.45,.60,.65,1),'Dark':(.022,.038,.055,1),'Gold':(.90,.51,.09,1),'Cyan':(.10,.85,.95,1),'Amber':(1,.48,.08,1),'Red':(.95,.14,.20,1),'Ice':(.30,.65,.79,1),'Violet':(.42,.18,.68,1)}
materials={}
for name,col in PALETTE.items():
    mat=bpy.data.materials.get('Scintilla_Difficulty_'+name) or bpy.data.materials.new('Scintilla_Difficulty_'+name); mat.use_nodes=True; mat.diffuse_color=col
    bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); bsdf.inputs['Base Color'].default_value=col
    bsdf.inputs['Metallic'].default_value=.65 if name in ('Steel','SteelLight','Gold') else .1
    bsdf.inputs['Roughness'].default_value=.22 if name=='Ice' else .42
    if name in ('Cyan','Amber','Red'): bsdf.inputs['Emission Color'].default_value=col; bsdf.inputs['Emission Strength'].default_value=1.8
    materials[name]=mat
def bolts(xs,z,y=.30):
    for x in xs: cylinder('Hex bolt',(x,y,z),.045,.035,'SteelLight','Y',6)
def stripe(x,z,w=.10):
    o=box('Warning stripe',(x,.34,z),(w,.025,.23),'Gold',.003); o.rotation_euler.y=.40
def cone(name,pos,radius,height,mat='SteelLight'):
    bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=radius,radius2=.008,depth=height,location=pos)
    return adopt(bpy.context.object,name,mat)
def polygon(name,pts,depth,mat):
    n=len(pts); verts=[(x,y,z) for y in (-depth/2,depth/2) for x,z in pts]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); owned.objects.link(o); o.data.materials.append(materials[mat]); parts.append(o)
    mod=o.modifiers.new('Forged edges','BEVEL'); mod.width=.02; mod.segments=2
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
    return o
# Wind unit with independent rotor and visible warning lamps.
box('Vent case',(0,0,.68),(1.48,.64,1.35),'Steel',.12)
cylinder('Duct rim',(0,.39,.70),.58,.17,'SteelLight','Y',32)
cylinder('Duct shadow',(0,.49,.70),.49,.04,'Dark','Y',32)
for x in (-.57,.57):
    box('Vent foot',(x,0,.09),(.30,.84,.18),'Dark',.025)
    cylinder('Status lamp',(x,.40,1.20),.075,.04,'Cyan','Y')
bolts([-.64,.64],.30); finish('SM_WindHousing')
cylinder('Fan axle',(0,0,0),.14,.15,'Gold','Y',24)
for a in range(5):
    angle=a*math.tau/5; o=box('Fan blade',(.25*math.sin(angle),0,.25*math.cos(angle)),(.19,.07,.48),'SteelLight',.04); o.rotation_euler.y=angle+.30
finish('SM_WindRotor')
# Two genuinely aerial silhouettes: angular wasp and rounded survey drone.
for variant in range(2):
    mat='Violet' if variant else 'Steel'
    box('Aerial carapace',(0,0,.18),(.82,.46,.36),mat,.13)
    box('Visor socket',(0,.25,.23),(.55,.08,.20),'Dark',.06)
    for x in (-.16,.16): cylinder('Optic',(x,.31,.23),.065,.035,'Amber' if variant else 'Cyan','Y',24)
    for x in (-.47,.47):
        cylinder('Thruster sleeve',(x,0,.10),.15,.32,'SteelLight')
        cylinder('Thruster nozzle',(x,0,-.08),.105,.04,'Cyan')
        cable('Antenna',[(x*.6,0,.38),(x*.8,0,.58),(x,0,.65)],.025,'Gold')
    cone('Tail fin',(0,-.29,.28),.20,.30,mat)
    finish('SM_FlyerSurvey' if variant else 'SM_FlyerWasp')
polygon('Swept wing',[(0,0),(.20,.06),(.65,.30),(.93,.16),(.62,-.04),(.23,-.10)],.09,'SteelLight')
box('Wing circuit',(.48,.065,.08),(.45,.025,.04),'Cyan',.008); finish('SM_FlyerWing')
# Falling spikes and retractable spikes share the replaceable toothed rack.
box('Overhead carriage',(0,0,0),(1.65,.60,.24),'Steel',.045)
for x in (-.70,.70):
    box('Rail strut',(x,-.20,.20),(.16,.18,.58),'SteelLight',.02)
    cylinder('Hydraulic pin',(x,0,-.22),.055,.35,'Gold')
for x in (-.52,-.26,0,.26,.52): stripe(x,0)
bolts([-.72,.72],0); finish('SM_SpikeRail')
box('Spike carrier',(0,0,.065),(1.42,.45,.13),'Dark',.015)
for x in (-.54,-.27,0,.27,.54):
    cylinder('Spike collar',(x,0,.13),.10,.07,'Gold')
    cone('Forged spike',(x,0,.38),.095,.48)
finish('SM_SpikeRack')
box('Retractor pit',(0,0,-.10),(1.65,.75,.20),'Steel',.035)
for y in (-.32,.32): box('Pit edge',(0,y,.015),(1.65,.09,.09),'SteelLight',.018)
for x in (-.66,.66): cylinder('Warning lens',(x,.39,-.06),.05,.025,'Red','Y')
for x in (-.52,-.26,0,.26,.52): stripe(x,-.10)
finish('SM_RetractBase')
# Slip deck: cyan ice shards and scored industrial perimeter.
box('Cold deck',(0,0,-.08),(3.0,1.10,.16),'Steel',.04)
box('Icy surface',(0,0,.015),(2.80,.94,.07),'Ice',.035)
for x in (-1.44,1.44): box('Edge strip',(x,0,.04),(.10,1.10,.06),'SteelLight',.01)
for i in range(7):
    o=box('Ice seam',(-1.05+i*.35,.1*math.sin(i),.057),(.025,.55,.008),'Cyan',.003); o.rotation_euler.z=.35*(-1 if i%2 else 1)
finish('SM_IceDeck')
# Motor and tools use the axle as their origin, ready for XZ plane rotation.
cylinder('Axle bearing',(0,0,0),.26,.34,'SteelLight','Y',24)
cylinder('Axle end',(0,.20,0),.16,.10,'Gold','Y',24)
for a in range(6):
    t=a*math.tau/6; cylinder('Axle bolt',(.20*math.cos(t),.22,.20*math.sin(t)),.032,.035,'Dark','Y',6)
box('Motor bracket',(0,-.10,.38),(.44,.38,.56),'Steel',.035); finish('SM_TrapMotor')
for axe in (False,True):
    box('Tool shaft',(0,0,-.85),(.16,.22,1.70),'SteelLight',.025)
    for z in (-.50,-1.10): box('Shaft collar',(0,0,z),(.27,.30,.14),'Gold',.015)
    if axe:
        polygon('Axe blade',[(-.05,-1.45),(.72,-1.22),(1.0,-1.42),(.82,-1.95),(.45,-2.10),(-.05,-1.85)],.22,'SteelLight')
        polygon('Axe dark cheek',[(.15,-1.50),(.62,-1.38),(.72,-1.48),(.57,-1.85),(.22,-1.81)],.25,'Steel')
    else:
        box('Hammer head',(0,0,-1.70),(1.0,.60,.45),'Steel',.065)
        for x in (-.48,.48): box('Hammer face',(x,0,-1.70),(.12,.64,.50),'Gold',.025)
        bolts([-.25,.25],-1.70,.33)
    finish('SM_RotatingAxe' if axe else 'SM_RotatingHammer')
# Lives terminal and individual replaceable battery cells.
box('Checkpoint terminal',(0,0,.76),(.68,.46,1.15),'Steel',.06)
box('Terminal base',(0,0,.10),(.88,.65,.20),'Dark',.04)
box('Terminal display',(0,.25,.96),(.50,.045,.32),'Dark',.02)
for i in range(3): box('Attempt bar',(-.16+i*.16,.285,.96),(.09,.02,.20),'Cyan',.009)
box('Warning beacon',(0,0,1.42),(.34,.28,.15),'Amber',.03)
bolts([-.26,.26],.45,.26); finish('SM_LivesTerminal')
cylinder('Battery',(0,0,.20),.10,.35,'Gold','Z',16)
cylinder('Battery cap',(0,0,.40),.06,.05,'SteelLight')
box('Battery light',(0,.09,.22),(.07,.03,.19),'Cyan',.006); finish('SM_LifeCell')
# Longer routes use new reinforced modules, not stretched existing artwork.
box('Walkway slab',(0,0,-.12),(3.0,1.55,.24),'Steel',.04)
for x in (-1.44,1.44): box('Deck rim',(x,0,-.02),(.12,1.60,.15),'SteelLight',.025)
for x in (-1.10,-.70,-.30,.10,.50,.90,1.25):
    box('Deck tread',(x,0,.018),(.075,1.40,.035),'Dark',.008)
    stripe(x,-.12,.13)
box('Underbeam',(0,0,-.29),(2.90,.60,.20),'Gold',.025); finish('SM_LongDeck')
box('Support pillar',(0,0,-1.3),(.32,.45,2.60),'Steel',.04)
box('Support foot',(0,0,-2.65),(.72,.72,.15),'Dark',.025)
for z in (-.55,-1.60): box('Support collar',(0,0,z),(.47,.56,.15),'Gold',.02)
finish('SM_LongColumn')
for x in (-1.30,1.30): box('Arch post',(x,0,1.20),(.20,.25,2.4),'SteelLight',.02)
box('Arch lintel',(0,0,2.40),(2.8,.30,.24),'Steel',.03)
for x in (-.8,0,.8): box('Arch light',(x,.18,2.40),(.32,.04,.08),'Cyan',.01)
finish('SM_LongArch')
# Place model families as assembled exhibits; export origins remain at component pivots.
placements={
'SM_WindHousing':(0,0,0),'SM_WindRotor':(0,.54,.70),
'SM_FlyerWasp':(4,0,.50),'SM_FlyerWing':(4.42,0,.70),'SM_FlyerSurvey':(7,0,.50),
'SM_SpikeRail':(11,0,2.20),'SM_SpikeRack':(11,0,.03),'SM_RetractBase':(14,0,0),
'SM_IceDeck':(0,-5,0),'SM_TrapMotor':(4,-5,2.3),'SM_RotatingHammer':(4,-4.70,2.30),
'SM_RotatingAxe':(8,-4.70,2.30),'SM_LivesTerminal':(11,-5,0),'SM_LifeCell':(12,-5,0),
'SM_LongDeck':(0,-10,2.7),'SM_LongColumn':(0,-10,2.7),'SM_LongArch':(4,-10,0)}
manifest={'source':'Scintilla_DifficultyKit.blend','palette':PALETTE,'models':[],'units':'meters; FBX exported with unit scale to Unreal centimeters','animation':'moving components have independent pivots; gameplay controls their motion'}
for name,obj in models.items():
    manifest['models'].append({'name':name,'vertices':len(obj.data.vertices),'polygons':len(obj.data.polygons),'dimensions_m':list(obj.dimensions),'pivot':'mechanical axis' if name in ('SM_WindRotor','SM_RotatingHammer','SM_RotatingAxe','SM_FlyerWing') else 'placement origin'})
    obj.location=placements[name]
# Add the symmetric wing and an assembled rising rack in the source gallery.
for name,pos,scale in [('SM_FlyerWing',(3.58,0,.70),(-1,1,1)),('SM_SpikeRack',(14,0,0),(1,1,1)),('SM_TrapMotor',(8,-5,2.3),(1,1,1))]:
    o=models[name].copy(); o.data=models[name].data; owned.objects.link(o); o.location=pos; o.scale=scale; o.name=name+'_DisplayCopy'
scene=bpy.context.scene; scene.unit_settings.system='METRIC'; scene.render.resolution_x=1600; scene.render.resolution_y=950; scene.render.resolution_percentage=100
world=bpy.data.worlds.new('Difficulty Studio'); scene.world=world; world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND'); bg.inputs[0].default_value=(.035,.055,.075,1); bg.inputs[1].default_value=.6
bpy.ops.object.camera_add(location=(20,19,17)); camera=bpy.context.object; camera.rotation_euler=(Vector((6,-4,1))-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.type='ORTHO'; camera.data.ortho_scale=22; scene.camera=camera
for pos,power,size in [((3,3,12),2200,10),((14,-4,10),1800,8),((-4,-8,6),1300,7)]:
    bpy.ops.object.light_add(type='AREA',location=pos); l=bpy.context.object; l.data.energy=power; l.data.shape='DISK'; l.data.size=size; l.rotation_euler=(Vector((6,-4,0))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.select_all(action='DESELECT')
for obj in models.values(): obj.select_set(True)
bpy.context.view_layer.objects.active=models['SM_WindHousing']
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.shading.type='MATERIAL'
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Scintilla_DifficultyKit.blend'))
print('DIFFICULTY_MODELS_CREATED',len(models),list(models))
