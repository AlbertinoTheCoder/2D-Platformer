"""PIE-only close-up of a real directional pose; freezes after its turn settles."""
import unreal,json
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
world=unreal.EditorLevelLibrary.get_game_world()
pc=unreal.GameplayStatics.get_player_controller(world,0); pawn=unreal.GameplayStatics.get_player_pawn(world,0)
unreal.GameplayStatics.set_game_paused(world,False)
mode=json.loads((ROOT/'Platformer_2D_Game/Saved/FacingPreview.json').read_text())['direction']
pawn.move_axis(0); pawn.get_component_by_class(unreal.CharacterMovementComponent).stop_movement_immediately()
pawn.set_actor_location(unreal.Vector(450,0,100),False,True)
for cam in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ScintillaCamera):
    cam.get_component_by_class(unreal.CameraComponent).set_editor_property('ortho_width',650)
    cam.set_editor_property('target',None)
    cam.set_actor_location(unreal.Vector(450,1500,100),False,True)
if mode=='Left': pawn.move_axis(-1)
elif mode=='Right': pawn.move_axis(1)
elif mode=='Camera': pawn.face_camera()
else: pawn.face_city()
preview_started=unreal.GameplayStatics.get_time_seconds(world)
def freeze_facing(dt):
    preview_elapsed=unreal.GameplayStatics.get_time_seconds(world)-preview_started
    pos=pawn.get_actor_location()
    for camera in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ScintillaCamera):
        camera.set_actor_location(unreal.Vector(pos.x,1500,pos.z+55),False,True)
    if preview_elapsed>.4:
        pawn.move_axis(0)
        pos=pawn.get_actor_location()
        unreal.GameplayStatics.set_game_paused(world,True)
        unreal.unregister_slate_post_tick_callback(preview_handle)
        (ROOT/'Platformer_2D_Game/Saved/FacingPreviewResult.json').write_text(json.dumps({'direction':mode,'look_direction':str(pawn.get_editor_property('look_direction')),'position':str(pos)}))
        print('FACING_PREVIEW_OK',mode,pawn.get_editor_property('look_direction'))
preview_handle=unreal.register_slate_post_tick_callback(freeze_facing)
