"""Weathered modular city pieces, authored and exported in Blender."""
import bpy,math,json,random
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
OUT=ROOT/'Assets/Models/City'; OUT.mkdir(parents=True,exist_ok=True)
if not (OUT/'BeforeCityModels.blend').exists(): bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'BeforeCityModels.blend'),copy=True)
source=(ROOT/'Scripts/create_blender_models.py').read_text().split('# Friendly but')[0]
source=source.replace("OUT = ROOT / 'Assets/Models'","OUT = ROOT / 'Assets/Models/City'").replace('Scintilla_ModelKit','Scintilla_CityKit').replace("'Scintilla_'","'Scintilla_City_'")
source=source.replace("mat.node_tree.nodes.get('Principled BSDF')","next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')")
exec(source,globals())
PALETTE={'Stone':(.32,.35,.34,1),'Brick':(.30,.20,.16,1),'Trim':(.40,.45,.43,1),'Dark':(.025,.039,.045,1),'Glass':(.19,.48,.48,1),'Rust':(.27,.105,.04,1),'Rot':(.10,.13,.075,1),'Bark':(.16,.105,.065,1),'Leaf':(.27,.46,.17,1)}
materials={}
for name,col in PALETTE.items():
    mat=bpy.data.materials.get('Scintilla_City_'+name) or bpy.data.materials.new('Scintilla_City_'+name)
    mat.diffuse_color=col; mat.use_nodes=True
    bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value=col; bsdf.inputs['Roughness'].default_value=.86
    materials[name]=mat
rng=random.Random(208)
for variant in range(3):
    width=2.3+variant*.15; height=3.2+variant*.3
    box('Masonry',(0,0,height/2),(width,.70,height),'Brick' if variant==1 else 'Stone',.04)
    for floor in range(3):
        z=.55+floor*.95
        box('Stone course',(0,.38,z-.25),(width+.15,.15,.10),'Trim',.015)
        for side in (-1,1):
            x=side*.55
            box('Window recess',(x,.39,z+.17),(.60,.09,.64),'Dark',.03)
            box('Window glass',(x,.445,z+.17),(.46,.025,.51),'Glass',.015)
            box('Window cross',(x,.475,z+.17),(.035,.02,.56),'Trim',.002)
            box('Sill',(x,.48,z-.16),(.68,.24,.09),'Trim',.012)
    for side in (-1,1):
        box('Corner pier',(side*(width/2-.08),.38,height/2),(.16,.16,height),'Trim',.012)
    for i in range(12):
        x=rng.uniform(-width*.45,width*.45); z=rng.uniform(.18,height-.18)
        box('Exposed masonry',(x,.365,z),(rng.uniform(.12,.28),.025,.075),'Brick',.004)
    finish('SM_CityFacade'+str(variant+1))
box('Roof cornice',(0,0,.08),(2.65,.95,.16),'Trim',.025)
for side in (-1,1): box('Roof parapet',(side*1.2,0,.27),(.15,.9,.35),'Stone',.02)
box('Roof cap',(0,0,.33),(2.55,.95,.10),'Trim',.018)
cylinder('Chimney',(.65,-.12,.64),.15,.58,'Brick')
finish('SM_CityRoof')
for i in range(15):
    obj=box('Collapsed brick',(rng.uniform(-1.0,1.0),rng.uniform(-.32,.32),rng.uniform(.07,.18)),(rng.uniform(.15,.37),.20,.15),'Rust' if i%3==0 else 'Stone',.035)
    obj.rotation_euler=(rng.uniform(-.3,.3),rng.uniform(-.3,.3),rng.uniform(-1,1))
for i in range(3): cable('Bent rebar',[(i*.3-.3,0,.05),(i*.3-.35,.15,.42),(i*.3-.12,.12,.63)],.018,'Rust')
finish('SM_CityRubble')
for strand in range(4):
    points=[(strand*.23-.35+.08*math.sin(j*1.7+strand),0,2.7-j*.27) for j in range(11)]
    cable('Hanging vine',points,.018,'Rot')
    for j,(x,y,z) in enumerate(points[1:]):
        leaf=box('Withered leaf',(x+(-1 if j%2 else 1)*.075,.035,z),(.18,.035,.095),'Rot',.03)
        leaf.rotation_euler.y=(-1 if j%2 else 1)*.5
for i in range(5):
    box('Rust drip',(rng.uniform(-.4,.4),.005,1.3+rng.random()),(.045,.015,rng.uniform(.35,.9)),'Rust',.01)
for x in (-.3,.18):
    cable('Masonry fracture',[(x,.07,2.55),(x+.09,.075,2.2),(x-.08,.07,1.95),(x+.06,.075,1.65),(x-.03,.07,1.4)],.019,'Dark')
finish('SM_CityDecay')
cable('Dead trunk',[(0,0,0),(.05,0,.55),(-.04,0,1.1),(.10,0,1.65)],.065,'Bark')
for side in (-1,1):
    cable('Bare branch',[(0,0,.8),(side*.3,.02,1.15),(side*.48,.03,1.4)],.035,'Bark')
    cable('Twig',[(side*.3,.02,1.15),(side*.40,-.05,1.18),(side*.63,-.10,1.2)],.018,'Bark')
finish('SM_CityDeadTree')
for pos,size in [((0,0,1.7),(.75,.50,.65)),((-.45,0,1.35),(.65,.45,.50)),((.45,0,1.35),(.65,.45,.55))]:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=pos)
    obj=adopt(bpy.context.object,'New foliage','Leaf'); obj.scale=size
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
finish('SM_CityFoliage')
# A gently uneven earthen bank gives the skyline a real ground plane.
profile=[(-4,.2),(-3,.7),(-2,.35),(-1,1.05),(0,.55),(1,.8),(2,.35),(3,1.0),(4,.25)]
verts=[]
for y in (-.4,.4):
    verts.extend([(x,y,z) for x,z in profile]); verts.extend([(4,y,-40),(-4,y,-40)])
count=len(profile)+2
faces=[tuple(range(count-1,-1,-1)),tuple(range(count,count*2))]
faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
data=bpy.data.meshes.new('Earthen bank'); data.from_pydata(verts,[],faces); data.update()
obj=bpy.data.objects.new('Uneven ground',data); owned.objects.link(obj); obj.data.materials.append(materials['Rot']); parts.append(obj)
finish('SM_CityTerrain')
for i,obj in enumerate(models.values()): obj.location=(i*3,0,0)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Scintilla_CityKit.blend'),copy=True)
(OUT/'manifest.json').write_text(json.dumps({'models':list(models),'palette':PALETTE},indent=2))
print('CITY_MODELS_BLENDER_OK',list(models))
