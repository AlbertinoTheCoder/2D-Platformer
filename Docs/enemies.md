# SCINTILLA enemies

Three original ground enemy families were modeled and colored in the connected Blender instance, with beveled metal parts, glowing visors, and distinct silhouettes. Source: `Assets/Models/Enemies/Scintilla_EnemyKit.blend`; Blender preview: `blender_enemy_preview.png`. Five FBX files are imported under `/Game/Platformer/Art/Enemies`, with materials separate from the robot and districts.

| Type | Appearance | Behavior | How to defeat it |
|---|---|---|---|
| Scout | Petrol cyan, circular eye, turbines and rotor | Patrols, gently floats, and spins its rotor | One J discharge or a stomp |
| Charger | Amber, broad armor, horns and wheels | 0.8-second glowing warning, 300 cm/s dash, 1.4-second recovery; animated wheels | One J discharge or a stomp |
| Sentinel | Purple, hexagonal shield and glowing core | Slow patrol; core turns cyan after the first hit | Two separate J discharges or a stomp |

Hitboxes remain stable during visual movement. Chargers stay within patrol bounds and stop dashing before an edge or obstacle. One discharge cannot remove both armor points. A stomp bypasses the shield and bounces Scintilla upward.

The ground roster contains 37 enemies, up from the earlier 28: 2, 3, 4, 5, 5, 5, 6, and 7 in levels 1-8. Scouts appear in level 1, Chargers from level 2, and Sentinels from level 3. Encounters are separated from checkpoints, generators, and traps; expansion ground enemies are at least 350 cm from traps to leave landing room.

The [difficulty extension](difficulty.md) adds 13 aerial encounters: one per level in levels 1-3 and two per level in levels 4-8, for 50 enemies overall. Wasp and Survey flyers use original Blender bodies and separate animated wings from `Assets/Models/Difficulty/Scintilla_DifficultyKit.blend`. They patrol and bob independently of ground edge detection and can be defeated by discharge or stomp.

## Scripts and recovery

- `Scripts/create_enemy_models.py`: creates and exports the three bodies, wheel, and rotor in Blender.
- `Scripts/render_enemy_kit.py`: assembles the parts for the Blender preview.
- `Scripts/import_enemy_assets.py`: imports meshes and materials in Unreal with PIE stopped.
- `Scripts/prepare_enemies.py`: prepares types and positions in configuration files; called by campaign preparation.
- `Scripts/apply_enemy_roster.py`: updates only enemy actors in the eight maps and saves the three family Blueprints.
- `Scripts/playtest_enemies.py`: checks meshes, rotor, wheels, dash warning/recovery, armor, discharges, and stomps in an isolated session.

Recovery maps use `_BeforeEnemyRoster`; the prior Blender scene is `BeforeEnemyModels.blend`. Recovery copies are local and excluded from version control. The revision does not change campaign unlocks. Unreal preview: `Assets/UI/enemies_in_unreal.png`.
