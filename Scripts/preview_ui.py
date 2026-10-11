"""Transient UI preview in PIE; does not complete a district or write progress."""
import unreal
world=unreal.EditorLevelLibrary.get_game_world()
pc=unreal.GameplayStatics.get_player_controller(world,0)
pc.toggle_pause()
print('UI_PAUSE_PREVIEW_OK')
