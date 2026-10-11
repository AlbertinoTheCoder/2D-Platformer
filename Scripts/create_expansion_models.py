"""Build 12 original Blender meshes; retain every pre-existing scene object."""
import bpy, math, json
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
OUT=ROOT/'Assets/Models/Expansion'; OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'BeforeExpansion.blend'),copy=True)
source=(ROOT/'Scripts/create_blender_models.py').read_text().split('# Friendly but')[0]
source=source.replace("OUT = ROOT / 'Assets/Models'","OUT = ROOT / 'Assets/Models/Expansion'").replace('Scintilla_ModelKit','Scintilla_ExpansionKit')
# Use node types rather than a localized node name.
source=source.replace("mat.node_tree.nodes.get('Principled BSDF')","next(node for node in mat.node_tree.nodes if node.type=='BSDF_PRINCIPLED')")
exec(source,globals())

# Cryogenics: insulated capsule, lit observation slit, coolant coils.
box('Cryo plinth',(0,0,.12),(1.6,1.0,.24),'SteelLight')
cylinder('Insulated capsule',(0,0,1.4),.56,2.5,'SteelLight',vertices=32)
for z in (.35,1.0,1.85,2.6): cylinder('Cooling ring',(0,0,z),.63,.09,'Cyan',vertices=32)
box('Observation frame',(0,.56,1.5),(.62,.12,1.4),'Dark',.06)
box('Cold window',(0,.64,1.5),(.40,.035,1.16),'Cyan',.04)
for x in (-.68,.68): cable('Coolant line',[(x,0,.2),(x,0,2.5),(x*.6,0,2.65)],.06,'Gold')
finish('SM_CryoPod')
for x,z,r in ((-.4,.7,.22),(0,1.2,.3),(.4,.65,.2)):
    bpy.ops.mesh.primitive_cone_add(vertices=6,radius1=r,radius2=.02,depth=z,location=(x,0,z/2))
    adopt(bpy.context.object,'Ice crystal','Cyan')
finish('SM_IceCluster')

# Scrap yard: open steel salvage gantry and electromagnetic lifting head.
for x in (-.8,.8): box('Gantry leg',(x,0,1.35),(.23,.50,2.7),'SteelLight')
box('Overhead rail',(0,0,2.8),(2.0,.60,.25),'Gold')
for x in (-.8,-.4,0,.4,.8): box('Rail rivet',(x,.32,2.8),(.08,.05,.08),'Dark',.01)
box('Magnet cable',(0,0,2.2),(.04,.04,1.0),'Dark')
cylinder('Lifting magnet',(0,0,1.6),.53,.25,'Gold',vertices=32)
cylinder('Magnetic ring',(0,0,1.44),.48,.06,'Red',vertices=32)
finish('SM_SalvageGantry')
for j,(x,z) in enumerate(((-.45,.18),(.15,.2),(-.1,.55),(.45,.45))):
    obj=box('Scrap block',(x,0,z),(.65,.55,.34),'Steel' if j%2 else 'Gold',.025); obj.rotation_euler.y=.25*(-1 if j%2 else 1)
cylinder('Discarded wheel',(.6,.1,.8),.32,.12,'SteelLight','Y',24)
finish('SM_ScrapPile')

# Solar works: articulated photovoltaic wings and a parabolic receiver.
box('Panel base',(0,0,.1),(1.6,1,.2),'Dark')
cylinder('Panel mast',(0,0,.65),.1,1.0,'Gold')
for x in (-.65,.65):
    box('Panel frame',(x,0,1.15),(1.12,.55,.78),'SteelLight')
    box('Photovoltaic face',(x,.3,1.15),(1.0,.04,.65),'Glass')
    for dx in (-.28,0,.28): box('Cell divider',(x+dx,.335,1.15),(.02,.018,.65),'Cyan',.003)
finish('SM_SolarArray')
box('Dish foot',(0,0,.1),(1.4,1,.2),'Gold')
cylinder('Dish mast',(0,0,.9),.16,1.5,'SteelLight')
# Open receiver ring with radial spokes, deliberately distinct from a tank.
bpy.ops.mesh.primitive_torus_add(major_radius=.75,minor_radius=.07,major_segments=32,minor_segments=8,location=(0,0,1.9),rotation=(math.pi/2,0,0))
adopt(bpy.context.object,'Receiver rim','Gold')
for angle in range(0,360,45):
    a=math.radians(angle); cable('Receiver spoke',[(0,.1,1.9),(.72*math.cos(a),0,1.9+.72*math.sin(a))],.025,'SteelLight')
cylinder('Receiver lens',(0,.12,1.9),.17,.16,'Amber','Y')
finish('SM_SolarDish')

# Bio garden: branching trunk with faceted light blossoms and a glass vivarium.
cable('Tree trunk',[(0,0,0),(0,0,1),(-.15,0,2.2)],.13,'Gold')
for x,z in ((-.65,1.8),(.65,2.0),(-.35,2.55),(.35,2.75)):
    cable('Branch',[(0,0,1.1),(x*.7,0,z-.3),(x,0,z)],.045,'Gold')
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.4,location=(x,0,z)); adopt(bpy.context.object,'Light blossom','Cyan')
    cylinder('Blossom core',(x,.32,z),.09,.04,'Amber','Y')
finish('SM_BloomTree')
box('Vivarium base',(0,0,.12),(1.3,.9,.24),'SteelLight')
box('Glass chamber',(0,0,1.0),(1.0,.65,1.6),'Glass',.08)
for x in (-.56,.56): box('Vivarium frame',(x,0,1.0),(.1,.8,1.75),'Gold')
box('Growth lamp',(0,0,1.9),(1.3,.9,.16),'Cyan')
for x in (-.25,.25): cable('Plant shoot',[(x,.37,.3),(x,.37,.8),(x+.1,.37,1.25)],.035,'Amber')
finish('SM_Vivarium')

# Theme-specific traversal deck silhouettes, all sharing a safe flat top.
for name,rail in [('Cryo','Cyan'),('Scrap','Red'),('Solar','Amber'),('Bio','Cyan')]:
    box('Walkway',(0,0,-.08),(2,1,.16),'SteelLight',.015)
    for x in (-.8,-.4,0,.4,.8): box('Deck light',(x,.52,-.07),(.16,.035,.09),rail,.006)
    if name=='Scrap':
        for x in (-.75,0,.75): box('Truss',(x,0,-.28),(.12,.7,.3),'Gold')
    elif name=='Cryo': cylinder('Coolant underside',(0,0,-.23),.09,1.7,'Cyan','X')
    elif name=='Solar': box('Solar conductor',(0,0,-.22),(1.9,.25,.10),'Gold')
    else: cable('Deck vine',[(-.9,.48,-.18),(0,.48,-.28),(.9,.48,-.18)],.04,'Gold')
    finish('SM_Deck'+name)
for i,obj in enumerate(models.values()): obj.location=((i%4)*4,(i//4)*5,0)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Scintilla_ExpansionKit.blend'),copy=True)
(OUT/'manifest.json').write_text(json.dumps({'models':list(models),'source':'Scintilla_ExpansionKit.blend','palette':PALETTE},indent=2))
print('BLENDER_EXPANSION_OK',list(models))
