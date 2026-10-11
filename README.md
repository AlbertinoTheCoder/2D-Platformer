# SCINTILLA - 2D platformer

A maintenance robot restores power to eight fallen industrial districts. The blackout feels eerie; restoring power repairs the city, lights its windows, regrows its trees, and reveals the whole district before the mission rating and level selector.

Specification: [original brief](Docs/promptstart.md). Creative direction: [game design](Docs/game-design.md). Development plan: [implementation plan](Docs/implementation-plan.md). Completed checks and limitations: [validation](Docs/validation.md).

## Open and play

The Unreal Engine 5.8.3 project is `Platformer_2D_Game/Platformer_2D_Game.uproject`. Double-click `Open-Scintilla.cmd` or open the project in Unreal, then press **Play**. The startup map is `/Game/Platformer/Levels/L_Platformer_Prototype`.

The launcher script currently uses `E:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe`; update that path for another installation. It bypasses the Epic Launcher prerequisite check that can fail with `LS-0019-IS-0001`; it does not install or change Windows prerequisites. Build with Visual Studio C++ tools and a Windows SDK supported by UE 5.8. Generated binaries are excluded from this repository.

Reach the district generator to restore power. Energy pickups are optional. Death restores integrity at the latest maintenance checkpoint. Restarting clears the current level state. Unlocks persist between sessions.

| Action | Keyboard | Gamepad |
|---|---|---|
| Move | A/D or arrow keys | Left stick |
| Variable jump | Space (hold/release) | Bottom face button |
| Melee discharge | J | Left face button |
| Interact | E | Top face button |
| Pause / resume | U | Start |
| Face the camera / city | S / W | - |

A/D use mirrored walking profiles and animations. W/S change the model's orientation while movement remains on the platformer's XZ plane. The presentation uses 3D Blender models and an orthographic camera; Paper2D is enabled for optional 2D elements.

## Campaign and difficulty

The [campaign](Docs/campaign.md) contains Workshop 07, Foundry, Pipeworks, Central Tower, Cryo Labs, Scrap Yards, Solar Works, and Bio Gardens. Each has its own layout, colors, skyline, and props. Winning unlocks only the next district; replaying never removes unlocks. The pause menu offers **CHOOSE LEVEL** for any unlocked district.

After the generator, a 7.5-second [city restoration](Docs/city-restoration.md) ends with a [mission rating](Docs/mission-rating.md) based on speed, damage, and collected energy. **CONTINUE** then opens the district selector.

Choose Normal, Hard, or Hardcore with **U -> DIFFICULTY**. Attempt limits are 8, 5, and 3. Exhausting them restarts the level without energy or checkpoints, preserving campaign unlocks. Changing difficulty also restarts the current level and saves the setting.

All eight levels have an extended section with intermittent downward/backward wind, flying enemies, falling and retracting spikes, slippery ice, and rotating hammers/axes. Each extension adds seven platforms, two checkpoints, and seven energy pickups. See [difficulty](Docs/difficulty.md) for timings, behavior, and validation limits.

The [enemy roster](Docs/enemies.md) has 50 encounters: 37 ground enemies and 13 flyers. Cyan Scouts patrol, amber Chargers telegraph a dash, and purple Sentinels have two armor points. J defeats Scouts, Chargers, and flyers in one hit; Sentinels require two separate discharges or a stomp.

## Source and assets

- `Platformer_2D_Game/Source/Scintilla/`: player, camera, health, world actors, obstacles, controller/UMG, progress, and integration probes. Blueprints under `/Game/Platformer` configure and present these native systems.
- `Config/platformer.json`, `Config/campaign.json`: offline layout and gameplay manifests, rather than native Unreal configuration.
- `Assets/Models/Scintilla_ModelKit.blend`: original 11-model kit and FBX exports, imported under `/Game/Platformer/Art/Meshes`. The original art pass added 58 decorations without collision.
- `Assets/Models/Scintilla_DistrictKit.blend`: foundry furnaces, pipeworks tanks/fans, and tower relays.
- `Assets/Models/Expansion/Scintilla_ExpansionKit.blend`: 12 models for the four expansion districts, imported under `/Game/Platformer/Art/Expansion`.
- `Assets/Models/RobotRig/Scintilla_Rig.blend`: nine-bone robot rig with eight clips (idle, run, jump, fall, land, attack, hurt, death), imported under `/Game/Platformer/Art/Robot`.
- `Assets/Models/Enemies/Scintilla_EnemyKit.blend`: three ground enemy bodies, rotor, and wheel.
- `Assets/Models/City/Scintilla_CityKit.blend`: nine city models, including broken masonry, roofs, rubble, dry vines, bare trees, foliage, and terrain.
- `Assets/Models/Difficulty/Scintilla_DifficultyKit.blend`: 17 trap, flyer, and extension models.
- `Assets/Audio`: seven original synthesized placeholder effects.
- `Assets/UI` and model subdirectories: previews and recorded validation reports. Older screenshots show earlier versions of the game.

Robot vertices have rigid single-bone weights; joints rotate without deforming the metal body. Materials have zero World Position Offset. Native code selects clips through Animation Single Node, with direct transitions rather than an AnimBlueprint with blending. The discharge gesture lasts 0.3 seconds while preserving its separate damage window.

Asset paths, reflected function names, and save identifiers retain their existing spelling to preserve references and progress. All player-facing text and repository documentation are English; **SCINTILLA** keeps its name. `Config/english-text.json` intentionally retains Italian source strings as keys for the migration tools. See [game language](Docs/game-language.md).

## Generation and editor workflow

`Scripts/create_blender_models.py` creates the original kit in Blender. `Scripts/blender_bridge.py --script Scripts/create_blender_models.py` runs it through the active local add-on. `Scripts/import_model_kit.py` imports the FBX files in Unreal with PIE stopped. Regeneration replaces the kit collection, kit assets, and owned `Art_` actors; save manual edits to those elements separately before regenerating.

Other `create_*`, `import_*`, `prepare_*`, and `apply_*` scripts handle the specialized kits. Editor asset scripts must run through Unreal's Python after compiling the native module. Created assets are included in the project. Recovery copies are created locally by the scripts and excluded from version control.

`Scripts/configure_native.py` configures modules, plugins, input, and the startup map, backing up originals under `Saved/ScintillaBackup/BeforeNative`. `Scripts/build_unreal_assets.py` performs initial asset creation and refuses to replace an existing map. `Scripts/finalize_unreal_assets.py` updates prototype visuals and compiles/saves Blueprints. `Scripts/generate_audio.py` generates the audio sources.

`Scripts/revise_districts.py` applies district themes after making recovery copies. Pipeworks has wider platforms, accessible jumps, and separated encounters. `Scripts/rebalance_torre.py` adjusts Central Tower. Buildings and trees follow the terrain profile; their placement is fixed without flattening the ground.

## Validation

`-ScintillaSmoke` and `-ScintillaRoute` run automated checks in a separate game process and close it on completion. Smoke checks isolate systems using controlled positions; route checks use movement and jumps without teleporting. Reports are written to `Platformer_2D_Game/Saved/ScintillaPlaytest.json` and `ScintillaRoute.json`.

The final difficulty pass recorded 645 successful checks, including all eight complete Normal routes within the available attempts. Hard and Hardcore settings, persistence, and resets were checked; full routes in those modes remain unverified. Read [validation](Docs/validation.md) for the history and limits of each pass.

## Offline preparation

These Python 3 commands require no external dependencies and do not launch or connect to Unreal:

```powershell
python Scripts/inspect_workspace.py
python Scripts/prepare_platformer.py --check
python Scripts/prepare_platformer.py
```

The first reads project descriptors. The second checks parameters and distances. The third writes `Build/Preparation/platformer_plan.json` with planned assets, layout, and theoretical jump checks. Change `Config/platformer.json` to alter this derived report. Analytical jump checks alone do not prove runtime playability.
