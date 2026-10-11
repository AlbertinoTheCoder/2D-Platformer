"""Read transient completion state after clicking Continue in PIE."""
import unreal,json
from pathlib import Path
world=unreal.EditorLevelLibrary.get_game_world(); gs=unreal.GameplayStatics.get_game_state(world)
out=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game/Platformer_2D_Game/Saved/RatingContinueResult.json')
out.write_text(json.dumps({'dismissed':gs.get_editor_property('rating_dismissed'),'ready':gs.get_editor_property('restoration_ready'),'grade':gs.get_editor_property('rating_grade')}))
