import unreal,json
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
lib=unreal.EditorAssetLibrary
paths=['/Engine/EngineMaterials/DefaultTextMaterialOpaque','/Engine/EngineMaterials/DefaultTextMaterialTranslucent']
data={'materials':[], 'api':[x for x in dir(unreal.MaterialEditingLibrary) if 'property_input' in x]}
for path in paths:
    m=lib.load_asset(path)
    if m: data['materials'].append({'path':path,'shading_model':str(m.get_editor_property('shading_model'))})
(ROOT/'Platformer_2D_Game/Saved/TextMaterialInspection.json').write_text(json.dumps(data,indent=2))
print('TEXT_MATERIALS_INSPECTED')
