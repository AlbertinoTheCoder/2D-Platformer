"""Temporary PIE showcase of the actual imported enemy models; never saves the map."""
import unreal
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
world=unreal.EditorLevelLibrary.get_game_world()
pawn=unreal.GameplayStatics.get_player_pawn(world,0)
pawn.move_axis(0); pawn.set_actor_location(unreal.Vector(0,0,80),False,True)
pawn.set_actor_hidden_in_game(True)
enemies=unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ScintillaEnemy)
used=[]
for kind,x in [('Scout',380),('Charger',560),('Sentinel',740)]:
    enemy=next(e for e in enemies if kind.upper() in str(e.get_editor_property('enemy_type')))
    used.append(enemy)
    enemy.set_actor_location(unreal.Vector(x,0,27),False,True)
    enemy.set_editor_property('patrol_min_x',x-55); enemy.set_editor_property('patrol_max_x',x+55)
    enemy.set_editor_property('speed',0)
for enemy in enemies:
    if enemy not in used: enemy.set_actor_hidden_in_game(True)
for cam in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ScintillaCamera):
    cam.set_editor_property('target',None)
    cam.get_component_by_class(unreal.CameraComponent).set_editor_property('ortho_width',850)
    cam.set_actor_location(unreal.Vector(560,1500,90),False,True)
started=unreal.GameplayStatics.get_time_seconds(world)
def freeze(dt):
    for cam in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ScintillaCamera):
        cam.set_actor_location(unreal.Vector(560,1500,90),False,True)
    if unreal.GameplayStatics.get_time_seconds(world)-started>.5:
        unreal.GameplayStatics.set_game_paused(world,True)
        unreal.unregister_slate_post_tick_callback(handle)
        (ROOT/'Platformer_2D_Game/Saved/EnemyPreviewResult.txt').write_text('OK')
handle=unreal.register_slate_post_tick_callback(freeze)
