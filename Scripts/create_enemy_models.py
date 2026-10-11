"""Original bevelled enemy machines and moving parts, authored in live Blender."""
import bpy,math,json
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
OUT=ROOT/'Assets/Models/Enemies'; OUT.mkdir(parents=True,exist_ok=True)
if not (OUT/'BeforeEnemyModels.blend').exists(): bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'BeforeEnemyModels.blend'),copy=True)
source=(ROOT/'Scripts/create_blender_models.py').read_text().split('# Friendly but')[0]
source=source.replace("OUT = ROOT / 'Assets/Models'","OUT = ROOT / 'Assets/Models/Enemies'").replace('Scintilla_ModelKit','Scintilla_EnemyKit').replace("'Scintilla_'","'Scintilla_Enemy_'")
source=source.replace("mat.node_tree.nodes.get('Principled BSDF')","next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')")
exec(source,globals())
PALETTE={
 'ScoutShell':(.075,.30,.34,1),'ChargeShell':(.65,.24,.065,1),'GuardShell':(.22,.09,.38,1),
 'Black':(.016,.024,.035,1),'Trim':(.40,.52,.59,1),'Rubber':(.035,.045,.055,1),
 'OpticTeal':(.12,.9,.82,1),'OpticAmber':(1,.63,.15,1),'OpticViolet':(.72,.36,1,1),
}
materials={}
for name,col in PALETTE.items():
    mat=bpy.data.materials.get('Scintilla_Enemy_'+name) or bpy.data.materials.new('Scintilla_Enemy_'+name)
    mat.diffuse_color=col; mat.use_nodes=True
    node=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    node.inputs['Base Color'].default_value=col; node.inputs['Metallic'].default_value=.65; node.inputs['Roughness'].default_value=.32
    if name.startswith('Optic'): node.inputs['Emission Color'].default_value=col; node.inputs['Emission Strength'].default_value=2
    materials[name]=mat

# Scout: pressure hull, protruding cyclops lens, twin turbines and a spinning crown.
box('Scout belly',(0,0,.30),(.72,.42,.33),'ScoutShell',.11)
box('Visor well',(0,.24,.38),(.48,.10,.27),'Black',.07)
cylinder('Lens bezel',(0,.305,.38),.115,.045,'Trim','Y',32)
cylinder('Teal optic',(0,.34,.38),.085,.032,'OpticTeal','Y',32)
for x in (-.42,.42):
    cylinder('Turbine shroud',(x,0,.26),.14,.35,'Trim','Z',24)
    cylinder('Thruster glow',(x,0,.075),.10,.04,'OpticTeal','Z',24)
    box('Wing brace',(x*.8,0,.37),(.25,.24,.06),'Black')
    cylinder('Antenna',(x*.65,0,.62),.02,.30,'Trim')
    cylinder('Antenna bulb',(x*.65,0,.79),.045,.04,'OpticTeal')
cylinder('Rotor post',(0,0,.63),.045,.25,'Trim')
finish('SM_EnemyScout')

# Charger: broad armored beetle chassis, an aggressive slit and segmented bumper.
box('Charger hull',(0,0,.38),(.88,.49,.42),'ChargeShell',.12)
box('Armor spine',(0,0,.60),(.58,.40,.10),'Trim',.04)
box('Dark visor',(0,.27,.43),(.64,.09,.16),'Black',.04)
box('Amber slit',(0,.325,.43),(.51,.025,.065),'OpticAmber',.02)
for x in (-.37,.37):
    box('Bumper',(x,.27,.22),(.19,.16,.13),'Trim',.025)
    cable('Charging horn',[(x,0,.58),(x*.9,.02,.76),(x*.75,.16,.82)],.035,'Trim')
for x in (-.22,0,.22): box('Status bar',(x,.275,.58),(.075,.03,.07),'OpticAmber',.01)
box('Drive axle',(0,0,.16),(.68,.35,.09),'Black',.02)
finish('SM_EnemyCharger')

# Sentinel: tall shield guard, a hexagonal chest shield, narrow violet visor.
for x in (-.19,.19):
    box('Guard foot',(x,.03,.075),(.23,.36,.15),'Black',.04)
    cylinder('Leg piston',(x,0,.23),.065,.20,'Trim')
box('Guard torso',(0,0,.48),(.53,.32,.40),'GuardShell',.07)
box('Guard helmet',(0,0,.78),(.59,.34,.27),'GuardShell',.08)
box('Guard visor well',(0,.19,.79),(.42,.07,.10),'Black',.025)
box('Violet eye',(0,.23,.79),(.29,.02,.045),'OpticViolet',.015)
for x in (-.34,.34):
    cylinder('Shoulder',(x,0,.57),.105,.14,'Trim','X')
    box('Guard arm',(x,0,.39),(.13,.23,.29),'GuardShell',.035)
cylinder('Hex shield',(0,.20,.46),.30,.08,'Trim','Y',6)
cylinder('Shield inset',(0,.255,.46),.255,.025,'GuardShell','Y',6)
cylinder('Shield core',(0,.28,.46),.085,.04,'OpticViolet','Y',6)
finish('SM_EnemySentinel')

# Rigid parts are exported at their own pivot for engine-driven articulation.
cylinder('Wheel tire',(0,0,0),.16,.16,'Rubber','Y',32)
cylinder('Wheel hub',(0,.09,0),.115,.045,'Trim','Y',24)
for angle in (0,math.pi/2,math.pi,math.pi*1.5):
    spoke=box('Wheel spoke',(0,.12,0),(.03,.025,.24),'OpticAmber',.006); spoke.rotation_euler.y=angle
finish('SM_EnemyWheel')
cylinder('Rotor hub',(0,0,0),.07,.07,'Trim')
for angle in (0,2*math.pi/3,4*math.pi/3):
    x,y=.17*math.cos(angle),.17*math.sin(angle)
    blade=box('Swept rotor blade',(x,y,0),(.30,.075,.035),'Trim',.012); blade.rotation_euler.z=angle+.2
finish('SM_EnemyRotor')
for i,obj in enumerate(models.values()): obj.location=(i*2,0,0)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Scintilla_EnemyKit.blend'),copy=True)
(OUT/'manifest.json').write_text(json.dumps({'models':list(models),'palette':PALETTE,'source':'Scintilla_EnemyKit.blend'},indent=2))
print('ENEMY_MODELS_BLENDER_OK',list(models))
