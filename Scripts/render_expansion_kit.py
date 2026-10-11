"""Render the actual Blender kit in four color groups, retaining the user's objects."""
import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
OUT=ROOT/'Assets/Models/Expansion'
groups=[('SM_CryoPod','SM_IceCluster','SM_DeckCryo'),('SM_SalvageGantry','SM_ScrapPile','SM_DeckScrap'),('SM_SolarDish','SM_SolarArray','SM_DeckSolar'),('SM_BloomTree','SM_Vivarium','SM_DeckBio')]
for i,group in enumerate(groups):
    for name,y in zip(group,(0,3,-3)): bpy.data.objects[name].location=(-6+i*4,y,0)
stage=bpy.data.collections.get('Scintilla_ExpansionPreview')
if not stage:
    stage=bpy.data.collections.new('Scintilla_ExpansionPreview'); bpy.context.scene.collection.children.link(stage)
else:
    for obj in list(stage.objects): bpy.data.objects.remove(obj,do_unlink=True)
def own(obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    stage.objects.link(obj)
bpy.ops.object.camera_add(location=(8,22,15)); camera=bpy.context.object; own(camera)
camera.rotation_euler=(Vector((0,0,1))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO'; camera.data.ortho_scale=21
for pos,power,size in (((0,9,12),2200,10),((-8,-2,8),1700,8),((9,-5,9),2000,7)):
    bpy.ops.object.light_add(type='AREA',location=pos); lamp=bpy.context.object; own(lamp)
    lamp.data.energy=power; lamp.data.shape='DISK'; lamp.data.size=size
    lamp.rotation_euler=(Vector((0,0,1))-lamp.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene; previous_camera=scene.camera; scene.camera=camera
hidden=[]
for obj in scene.objects:
    if obj.type=='MESH' and obj.name not in {name for group in groups for name in group}:
        hidden.append((obj,obj.hide_render)); obj.hide_render=True
scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1200; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(OUT/'blender_kit_preview.png')
try: bpy.ops.render.render(write_still=True)
finally:
    for obj,value in hidden: obj.hide_render=value
    scene.camera=previous_camera
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Scintilla_ExpansionKit.blend'),copy=True)
print('BLENDER_KIT_RENDER_OK')
