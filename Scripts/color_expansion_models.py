"""Give the Blender source meshes the same four palettes used by the game."""
import bpy,json,math
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
OUT=ROOT/'Assets/Models/Expansion'
source=(ROOT/'Scripts/build_expansion.py').read_text()
themes=eval(source.split('themes=',1)[1].split('\ncache=',1)[0],{'__builtins__':{},'dict':dict})
models={obj.name:obj for obj in bpy.data.collections['Scintilla_ExpansionKit'].objects if obj.type=='MESH'}
for name,obj in models.items():
    n=5 if any(s in name for s in ('Cryo','Ice')) else 6 if any(s in name for s in ('Salvage','Scrap')) else 7 if 'Solar' in name else 8
    for slot in obj.material_slots:
        original=slot.material; color_name=original.name.replace('Scintilla_','').split('_D')[0]
        color=themes[n]['palette'].get(color_name,tuple(original.diffuse_color))
        mat_name=f'Scintilla_{color_name}_D{n}'
        mat=bpy.data.materials.get(mat_name) or original.copy(); mat.name=mat_name
        mat.diffuse_color=color
        node=next(node for node in mat.node_tree.nodes if node.type=='BSDF_PRINCIPLED')
        node.inputs['Base Color'].default_value=color
        if color_name in ('Cyan','Amber','Red'): node.inputs['Emission Color'].default_value=color
        slot.material=mat
    pos=obj.location.copy(); obj.location=(0,0,0)
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); bpy.context.view_layer.objects.active=obj
    obj.rotation_euler.z=math.pi; bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=False)
    obj.rotation_euler.z=math.pi; bpy.ops.object.transform_apply(location=False,rotation=True,scale=True); obj.location=pos
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Scintilla_ExpansionKit.blend'),copy=True)
print('BLENDER_FOUR_PALETTES_OK')
