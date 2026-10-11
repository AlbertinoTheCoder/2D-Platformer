"""Render the real Blender enemy meshes with their articulated parts assembled."""
import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
OUT=ROOT/'Assets/Models/Enemies'
stage=bpy.data.collections.get('Scintilla_EnemyPreview')
if stage:
    for obj in list(stage.objects): bpy.data.objects.remove(obj,do_unlink=True)
else:
    stage=bpy.data.collections.new('Scintilla_EnemyPreview'); bpy.context.scene.collection.children.link(stage)
def own(obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    stage.objects.link(obj)
bodies=['SM_EnemyScout','SM_EnemyCharger','SM_EnemySentinel']
for x,name in zip((-1.5,0,1.5),bodies): bpy.data.objects[name].location=(x,0,0)
for name,pos in [('SM_EnemyRotor',(-1.5,0,.76)),('SM_EnemyWheel',(-.28,0,.16)),('SM_EnemyWheel',(.28,0,.16))]:
    obj=bpy.data.objects[name].copy(); obj.data=bpy.data.objects[name].data; stage.objects.link(obj); obj.location=pos
bpy.ops.object.camera_add(location=(2.4,8,3.4)); cam=bpy.context.object; own(cam)
cam.rotation_euler=(Vector((0,0,.45))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'; cam.data.ortho_scale=5
for pos,power in [((0,3,5),500),((-3,0,3),350),((3,-2,4),450)]:
    bpy.ops.object.light_add(type='AREA',location=pos); lamp=bpy.context.object; own(lamp)
    lamp.data.energy=power; lamp.data.size=4
    lamp.rotation_euler=(Vector((0,0,.4))-lamp.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene; oldcam=scene.camera; hidden=[]
for obj in scene.objects:
    if obj.type=='MESH' and obj.name not in bodies and stage not in obj.users_collection:
        hidden.append((obj,obj.hide_render)); obj.hide_render=True
scene.camera=cam; scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1400; scene.render.resolution_y=700; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(OUT/'blender_enemy_preview.png')
try: bpy.ops.render.render(write_still=True)
finally:
    for obj,value in hidden: obj.hide_render=value
    scene.camera=oldcam
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Scintilla_EnemyKit.blend'),copy=True)
print('BLENDER_ENEMY_RENDER_OK')
