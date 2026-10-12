"""Remove obstacle/tutorial signs from campaign maps, preserving recovery copies."""
import json
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())).parent
HINTS = {
    'GUSTS / WATCH THE FAN', 'FALLING SPIKES / WAIT FOR CLEAR',
    'ICE / BRAKE BEFORE THE EDGE', 'FLYERS / DISCHARGE OR STOMP',
    'RISING SPIKES / WAIT FOR CLEAR', 'HAMMER / WATCH THE SWING',
    'AXE / CROSS WHEN CLEAR', 'SPACE / HOLD TO JUMP HIGHER',
    'J / DISCHARGE   or jump on the drone', 'WAIT FOR THE LIFT',
    'SPAZIO / TIENI PER SALTARE PIU IN ALTO',
    'J / SCARICA   oppure salta sul drone', 'ASPETTA IL MONTACARICHI',
}
lib = unreal.EditorAssetLibrary
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
original_map = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name().split('.')[0]

def is_hint(actor):
    return actor.get_actor_label().startswith('Difficulty_sign_') or any(
        str(component.get_editor_property('text')) in HINTS
        for component in actor.get_components_by_class(unreal.TextRenderComponent)
    )

if not lib.save_directory('/Game/Platformer', False, True):
    raise RuntimeError('Could not save project before removing hints')
report = []
for cfg in json.loads((ROOT / 'Config/campaign.json').read_text())['levels']:
    path = '/Game/Platformer/Levels/' + cfg['name']
    backup = path + '_BeforeHintRemoval'
    if not lib.does_asset_exist(backup) and not lib.duplicate_asset(path, backup):
        raise RuntimeError('Could not back up ' + path)
    if not levels.load_level(path):
        raise RuntimeError('Could not load ' + path)
    removed = []
    for actor in list(actors.get_all_level_actors()):
        if not is_hint(actor):
            continue
        removed.append({'actor': actor.get_actor_label(), 'text': [
            str(component.get_editor_property('text'))
            for component in actor.get_components_by_class(unreal.TextRenderComponent)
        ]})
        if not actors.destroy_actor(actor):
            raise RuntimeError('Could not remove ' + removed[-1]['actor'])
    if not levels.save_current_level():
        raise RuntimeError('Could not save ' + path)
    if not levels.load_level(path):
        raise RuntimeError('Could not reload ' + path)
    if any(is_hint(actor) for actor in actors.get_all_level_actors()):
        raise RuntimeError('Obstacle hint still present in ' + path)
    report.append({'level': cfg['index'], 'map': path, 'removed': removed, 'verified': True})
if not levels.load_level(original_map):
    raise RuntimeError('Could not restore original editor map: ' + original_map)
output = ROOT / 'Assets/Models/Difficulty/hint_removal_report.json'
output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('OBSTACLE_HINTS_REMOVED', sum(len(row['removed']) for row in report), 'across', len(report), 'maps')
