"""Open a selected expansion district in the editor (PIE must be stopped)."""
import json,unreal
from pathlib import Path
ROOT=Path('C:/Users/alber/Documents/Codex/UEProjects/Platformer_2D_Game')
selection=ROOT/'Platformer_2D_Game/Saved/ExpansionPreview.json'
n=json.loads(selection.read_text())['level'] if selection.exists() else 5
cfg=json.loads((ROOT/'Config/campaign.json').read_text())['levels'][n-1]
if not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Platformer/Levels/'+cfg['name']): raise RuntimeError(cfg['name'])
print('EXPANSION_PREVIEW_OPEN',cfg['name'])
