"""Reuse the engine font graph with unlit text, preserving all glyph masking."""
import unreal,json
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
lib=unreal.EditorAssetLibrary; mel=unreal.MaterialEditingLibrary
path='/Game/Platformer/Materials/M_HazardText'
mat=lib.load_asset(path) if lib.does_asset_exist(path) else lib.duplicate_asset('/Engine/EngineMaterials/DefaultTextMaterialOpaque',path)
if not mat: raise RuntimeError('Font material duplication failed')
node=mel.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR)
output=mel.get_material_property_input_node_output_name(mat,unreal.MaterialProperty.MP_BASE_COLOR)
if not node: raise RuntimeError('Engine font color node missing')
mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property('two_sided',True)
if not mel.connect_material_property(node,'' if not output or str(output)=='None' else str(output),unreal.MaterialProperty.MP_EMISSIVE_COLOR): raise RuntimeError('Font emissive connection failed')
mel.recompile_material(mat)
if not lib.save_loaded_asset(mat,False): raise RuntimeError('Font material save failed')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem); levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); report=[]
levels.save_current_level()
for cfg in json.loads((ROOT/'Config/campaign.json').read_text())['levels']:
    if not levels.load_level('/Game/Platformer/Levels/'+cfg['name']): raise RuntimeError(cfg['name'])
    count=0
    for a in actors.get_all_level_actors():
        for c in a.get_components_by_class(unreal.TextRenderComponent):
            c.set_material(0,mat); c.set_text_render_color(unreal.Color(185,235,255,255)); c.set_hidden_in_game(False); a.set_actor_hidden_in_game(False); count+=1
    if not levels.save_current_level(): raise RuntimeError('Map save failed')
    report.append({'level':cfg['index'],'readable_signs':count,'saved':True})
levels.load_level('/Game/Platformer/Levels/L_Platformer_Prototype')
(ROOT/'Assets/Models/Difficulty/sign_readability_report.json').write_text(json.dumps(report,indent=2))
print('HAZARD_TEXT_UNLIT_SAVED',report)
