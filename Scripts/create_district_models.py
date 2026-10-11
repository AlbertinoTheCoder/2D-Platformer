"""Additional original Blender landmarks; preserve the existing model collection."""
import bpy
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
if bpy.data.filepath:
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Assets/Models/BeforeDistrictModels.blend'),copy=True)
source=(ROOT/'Scripts/create_blender_models.py').read_text().split('# Friendly but')[0]
exec(source.replace('Scintilla_ModelKit','Scintilla_DistrictKit'),globals())

# Foundry: heavy cylindrical furnace with firebox, rivets and chimney.
box('Furnace footing',(0,0,.12),(1.8,1.2,.24),'Dark',.04)
cylinder('Boiler',(0,0,1.15),.68,2.0,'Steel',vertices=32)
for z in (.35,1,1.9): cylinder('Boiler ring',(0,0,z),.73,.095,'SteelLight',vertices=32)
box('Firebox',(0,.65,.78),(1.0,.18,.72),'Dark',.08)
box('Fire',(0,.755,.78),(.75,.045,.46),'Amber',.04)
for x in (-.25,0,.25): box('Fire grate',(x,.79,.78),(.045,.03,.49),'SteelLight',.009)
cylinder('Chimney',(-.4,-.2,2.5),.18,1.1,'Dark')
cylinder('Chimney rim',(-.4,-.2,3.07),.24,.12,'SteelLight')
cable('Pressure pipe',[(.6,0,.4),(.95,0,.5),(.95,0,1.8),(.65,0,2)],.08,'Gold')
finish('SM_Furnace')

# Canal treatment plant: tall pressure tank, ribs and illuminated gauge.
box('Tank base',(0,0,.10),(1.5,1.1,.2),'SteelLight',.025)
cylinder('Pressure tank',(0,0,1.5),.55,2.8,'Steel',vertices=32)
for z in (.3,1.1,2.0,2.8): cylinder('Tank strap',(0,0,z),.60,.07,'SteelLight',vertices=32)
box('Gauge panel',(0,.57,1.65),(.45,.08,.8),'Dark',.04)
for z in (1.4,1.65,1.9): box('Pressure gauge',(0,.62,z),(.26,.025,.1),'Cyan',.015)
cable('Overflow',[(.50,0,2.7),(.85,0,2.7),(.95,0,2.4),(.95,0,.4)],.1,'Gold')
finish('SM_Tank')

# Large industrial extraction fan with open blades and protective cross.
cylinder('Fan rim',(0,0,1.1),1.0,.32,'SteelLight','Y',40)
cylinder('Fan cavity',(0,.18,1.1),.86,.025,'Dark','Y',40)
cylinder('Hub',(0,.23,1.1),.16,.14,'Gold','Y')
for angle in (0,1.5708,3.1416,4.7124):
    blade=box('Impeller',(0,.25,1.1),(.18,.05,1.25),'Steel',.025)
    blade.rotation_euler.y=angle+.4
for x in (-.48,.48): box('Fan leg',(x,0,.38),(.1,.30,.72),'SteelLight',.012)
finish('SM_Fan')

# Central tower: transformer cabinets, crystal channel and aerial array.
box('Relay foot',(0,0,.12),(1.45,1.0,.24),'Dark',.04)
box('Relay column',(0,0,1.4),(.80,.65,2.55),'Steel',.1)
box('Signal channel',(0,.36,1.45),(.32,.075,2.1),'Dark',.03)
for z in (.6,1.0,1.4,1.8,2.2): box('Signal cell',(0,.41,z),(.21,.025,.20),'Cyan',.02)
for x in (-.52,.52):
    box('Cooling fin',(x,0,1.4),(.18,.8,1.8),'SteelLight',.025)
    cylinder('Aerial',(x,0,2.8),.025,.9,'Gold')
    cylinder('Aerial cap',(x,0,3.26),.07,.06,'Amber')
finish('SM_Relay')

for i,obj in enumerate(models.values()): obj.location=(i*4,-5,0)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Assets/Models/Scintilla_DistrictKit.blend'),copy=True)
print('SCINTILLA_DISTRICT_MODELS_OK',list(models))
