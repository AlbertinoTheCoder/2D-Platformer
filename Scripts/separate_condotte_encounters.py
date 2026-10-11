"""Separate the canal's combat and hazard encounters without replacing the dressed map."""
import unreal
from pathlib import Path
import json
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
cfg=json.loads((ROOT/'Config/campaign.json').read_text())['levels'][2]
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not level.load_level('/Game/Platformer/Levels/L_03_Condotte'): raise RuntimeError('Map missing')
for a in actors.get_all_level_actors():
    if a.get_actor_label()=='ExposedCable_cable_1':
        a.set_actor_location(unreal.Vector(*cfg['hazards'][1]['position']),False,False)
    if a.get_actor_label()=='Drone_drone_1':
        e=cfg['enemies'][1]; a.set_actor_location(unreal.Vector(*e['position']),False,False)
        a.set_editor_property('patrol_min_x',e['patrol_min_x']); a.set_editor_property('patrol_max_x',e['patrol_max_x'])
if not level.save_current_level(): raise RuntimeError('Save failed')
print('SCINTILLA_CONDOTTE_ENCOUNTERS_SEPARATED')
