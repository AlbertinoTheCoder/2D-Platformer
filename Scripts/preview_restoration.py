"""Freeze a transient PIE before/repair/reveal/chooser view for visual QA."""
import unreal,json
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
SAVED=ROOT/'Platformer_2D_Game/Saved'
settings=json.loads((SAVED/'RestorationPreview.json').read_text()); phase=settings['phase']
world=unreal.EditorLevelLibrary.get_game_world()
gs=unreal.GameplayStatics.get_game_state(world); pawn=unreal.GameplayStatics.get_player_pawn(world,0)
pawn.move_axis(0); pawn.set_actor_location(unreal.Vector(250,0,100),False,True)
for cam in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.ScintillaCamera):
    cam.set_editor_property('target',None)
    cam.get_component_by_class(unreal.CameraComponent).set_editor_property('ortho_width',2200)
    cam.set_actor_location(unreal.Vector(1200,1500,310),False,True)
started=unreal.GameplayStatics.get_time_seconds(world); triggered=False
def advance_preview(dt):
    global triggered
    elapsed=unreal.GameplayStatics.get_time_seconds(world)-started
    if elapsed<.4: return
    if phase!='before' and not triggered:
        if phase=='rating':
            gs.set_editor_property('run_seconds',69.0)
            gs.set_editor_property('damage_taken',1)
            gs.set_editor_property('energy',int(gs.get_editor_property('total_energy')*.8))
        gs.complete_level(); triggered=True
    if phase=='chooser' and gs.get_editor_property('restoration_ready'):
        unreal.GameplayStatics.get_player_controller(world,0).continue_from_rating()
    freeze=phase=='before' or (phase in ('rating','chooser') and gs.get_editor_property('restoration_ready')) or gs.get_editor_property('restoration_elapsed')>dict(repair=2.2,reveal=6.3).get(phase,100)
    if freeze:
        unreal.GameplayStatics.set_game_paused(world,True)
        unreal.unregister_slate_post_tick_callback(handle)
        (SAVED/'RestorationPreviewResult.json').write_text(json.dumps({'phase':phase,'ready':gs.get_editor_property('restoration_ready'),'time':gs.get_editor_property('restoration_elapsed')}))
        print('RESTORATION_PREVIEW_OK',phase)
handle=unreal.register_slate_post_tick_callback(advance_preview)
