"""PIE-only completion-menu layout preview using the currently loaded unlocks.

Restart PIE afterwards: this changes only transient GameState, never the save.
"""
import unreal
world=unreal.EditorLevelLibrary.get_game_world()
pc=unreal.GameplayStatics.get_player_controller(world,0)
state=unreal.GameplayStatics.get_game_state(world)
state.set_editor_property('completed',True)
state.set_editor_property('restoration_ready',True)
state.set_editor_property('rating_dismissed',True)
pc.refresh_hud()
assert pc.is_level_unlocked(0)
print('LEVEL_CHOOSER_PREVIEW_OK')
