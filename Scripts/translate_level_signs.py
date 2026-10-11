"""Translate placed TextRender signs in all campaign maps, with map backups."""
import unreal,json
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
translations=json.loads((ROOT/'Config/english-text.json').read_text(encoding='utf-8'))
lib=unreal.EditorAssetLibrary
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
lib.save_directory('/Game/Platformer',False,True)
report=[]
for cfg in json.loads((ROOT/'Config/campaign.json').read_text())['levels']:
    path='/Game/Platformer/Levels/'+cfg['name']
    backup=path+'_BeforeEnglish'
    if not lib.does_asset_exist(backup) and not lib.duplicate_asset(path,backup): raise RuntimeError(backup)
    if not level.load_level(path): raise RuntimeError(path)
    signs=[]
    for actor in actors.get_all_level_actors():
        for component in actor.get_components_by_class(unreal.TextRenderComponent):
            old=str(component.get_editor_property('text'))
            new=translations.get(old,old)
            if new!=old: component.set_text(new)
            signs.append({'before':old,'after':new})
    if not level.save_current_level(): raise RuntimeError(path)
    report.append({'level':cfg['index'],'signs':signs,'saved':True})
level.load_level('/Game/Platformer/Levels/L_Platformer_Prototype')
(ROOT/'Assets/UI/english_signs_report.json').write_text(json.dumps(report,indent=2))
print('ENGLISH_MAP_SIGNS_SAVED',report)
