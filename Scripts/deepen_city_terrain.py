"""Lower only the city bank's bottom vertices and export the shared Blender mesh."""
import bpy, math, shutil, json
from pathlib import Path
ROOT = Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
out = ROOT / 'Assets/Models/City'
source = out / 'Scintilla_CityKit.blend'
backup = ROOT / 'Platformer_2D_Game/Saved/ScintillaBackup/BeforeDeepTerrain'
backup.mkdir(parents=True, exist_ok=True)
for path in (source, out / 'SM_CityTerrain.fbx'):
    if not (backup / path.name).exists():
        shutil.copy2(path, backup / path.name)
with bpy.data.libraries.load(str(source), link=False) as (src, dst):
    dst.scenes = src.scenes
scene = dst.scenes[0]
terrain = next(obj for obj in scene.objects if obj.name.startswith('SM_CityTerrain'))
surface = [tuple(v.co) for v in terrain.data.vertices if v.co.z > -1]
bottom = min(v.co.z for v in terrain.data.vertices)
changed = 0
for vertex in terrain.data.vertices:
    if abs(vertex.co.z - bottom) < .001:
        vertex.co.z = -40
        changed += 1
terrain.data.update()
assert surface == [tuple(v.co) for v in terrain.data.vertices if v.co.z > -1]
bpy.data.libraries.write(str(source), {scene}, fake_user=True, compress=True)
export_scene = bpy.data.scenes.new('TerrainExport')
export = terrain.copy()
export.data = terrain.data.copy()
export_scene.collection.objects.link(export)
export.location = (0, 0, 0)
export.rotation_euler.z = math.pi
export.select_set(True, view_layer=export_scene.view_layers[0])
export_scene.view_layers[0].objects.active = export
previous_scene = bpy.context.window.scene
try:
    bpy.context.window.scene = export_scene
    bpy.ops.export_scene.fbx(filepath=str(out / 'SM_CityTerrain.fbx'), use_selection=True,
        object_types={'MESH'}, axis_forward='-Y', axis_up='Z', add_leaf_bones=False,
        use_mesh_modifiers=True, bake_anim=False)
finally:
    bpy.context.window.scene = previous_scene
bpy.data.objects.remove(export, do_unlink=True)
bpy.data.scenes.remove(export_scene)
report = {'bottom_before_m': bottom, 'bottom_after_m': -40,
          'lowered_vertices': changed, 'surface_unchanged': True}
(out / 'terrain_depth_source_report.json').write_text(json.dumps(report, indent=2) + '\n')
print('CITY_TERRAIN_DEEPENED', report)
