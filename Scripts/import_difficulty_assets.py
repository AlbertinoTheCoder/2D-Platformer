"""Import the original Blender hazard meshes with their authored material slots."""
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
source=(ROOT/'Scripts/import_city_assets.py').read_text()
source=source.replace('nine Blender city meshes','Blender difficulty meshes').replace('Assets/Models/City','Assets/Models/Difficulty').replace('/Art/City','/Art/Difficulty').replace('MI_City_','MI_Difficulty_').replace('Scintilla_City_','Scintilla_Difficulty_').replace("name=='Glass'","name in ('Cyan','Amber','Red')").replace('CITY_ASSETS_IMPORTED','DIFFICULTY_ASSETS_IMPORTED')
source=source.replace("        if name not in mats:","        if name not in mats and name.rsplit('_',1)[-1].isdigit(): name=name.rsplit('_',1)[0]\n        if name not in mats:")
exec(compile(source,'import_difficulty_assets.py','exec'),globals())
