"""Inspect a hazard in PIE without touching the campaign save."""
import unreal,json
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
kind=json.loads((ROOT/'Platformer_2D_Game/Saved/DifficultyPreview.json').read_text())['kind']
world=unreal.EditorLevelLibrary.get_game_world(); pawn=unreal.GameplayStatics.get_player_pawn(world,0)
obstacles=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ScintillaObstacle)
for a in obstacles: a.set_actor_tick_enabled(False); a.evaluate(4.5)
target=next(a for a in obstacles if a.get_editor_property('obstacle_type')==getattr(unreal.ScintillaObstacleType,kind))
target.evaluate(1.6 if kind in ('FALLING_SPIKES','RISING_SPIKES') else 1.4 if kind in ('HAMMER','AXE') else 3.0)
pos=target.get_actor_location(); pawn.set_actor_location(unreal.Vector(pos.x-180,0,pos.z+45 if kind!='WIND' else pos.z-55),False,False)
for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ScintillaCamera): a.set_actor_location(unreal.Vector(pos.x,1500,pos.z+160),False,False)
for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor): a.set_editor_property('custom_time_dilation',0.0)
(ROOT/'Platformer_2D_Game/Saved/DifficultyPreviewResult.json').write_text(json.dumps({'kind':kind,'position':str(pos)}))
print('DIFFICULTY_PREVIEW_READY',kind)
