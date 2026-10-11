"""Inspect pause UI without changing progress or completing a level."""
import unreal,json
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
saved=ROOT/'Platformer_2D_Game/Saved'
phase=json.loads((saved/'PausePreview.json').read_text())['phase']
world=unreal.EditorLevelLibrary.get_game_world(); pc=unreal.GameplayStatics.get_player_controller(world,0)
if phase=='pause':
    if unreal.GameplayStatics.is_game_paused(world): pc.resume_game()
    pc.toggle_pause()
elif phase=='chooser': pc.get_editor_property('hud').open_level_chooser()
(saved/'PausePreviewResult.json').write_text(json.dumps({'phase':phase,'paused':unreal.GameplayStatics.is_game_paused(world),'highest_unlocked':pc.get_highest_unlocked_level()}))
print('PAUSE_PREVIEW_OK',phase,unreal.GameplayStatics.is_game_paused(world))
