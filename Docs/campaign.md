# SCINTILLA campaign

Eight districts unlock sequentially. After restoring the generator, the player can choose any unlocked district. The first Workshop victory unlocks Foundry; Pipeworks stays locked until Foundry is completed, and Central Tower until Pipeworks is completed. Earlier levels can be replayed without losing unlocks. Locked buttons state which level must be completed and remain disabled; loading also rejects locked or invalid indices.

Restoration includes a 7.5-second [repair sequence](city-restoration.md). The fallen city realigns, lights up, and regrows while the camera reveals the whole district. A [mission rating](mission-rating.md) then appears; **CONTINUE** opens the selector. Map selection stays blocked until that confirmation, while victory is saved immediately.

Unlocks and completed levels are stored in the local `ScintillaCampaign` slot at `Platformer_2D_Game/Saved/SaveGames/ScintillaCampaign.sav`, reloaded on startup and map travel. Only level 1 is initially available. Repeated victories do not unlock another level, and completing Central Tower never resets progress. **REPLAY THIS LEVEL** and the pause menu's **RESTART** reload the current level. Each load restores integrity to three and clears energy/checkpoints.

## Base campaign layouts

The following counts describe the campaign before the difficulty extension. The [extension](difficulty.md) adds seven platforms, two checkpoints, seven energy pickups, seven obstacles, and one or two flying enemies to each level. Ground enemy counts remain as listed.

| Level | District | Ground enemies | Original hazards | Original energy | Lift width / speed |
|---|---|---:|---:|---:|---|
| 1 | Workshop 07 | 2 | 1 | 10 | 220 cm / 150 cm/s |
| 2 | Foundry | 3 | 2 | 10 | 200 cm / 150 cm/s |
| 3 | Pipeworks | 4 | 3 | 12 | 280 cm / 125 cm/s |
| 4 | Central Tower | 5 | 4 | 14 | 300 cm / 145 cm/s |
| 5 | Cryo Labs | 5 | 3 | 12 | 320 cm / 145 cm/s |
| 6 | Scrap Yards | 5 | 3 | 13 | 320 cm / 150 cm/s |
| 7 | Solar Works | 6 | 3 | 14 | 320 cm / 155 cm/s |
| 8 | Bio Gardens | 7 | 3 | 15 | 320 cm / 160 cm/s |

The [enemy revision](enemies.md) replaced red drones with cyan Scouts, amber Chargers, and purple Sentinels made in Blender. Their behavior and durability differ; they appear progressively in the first three levels.

Difficulty originally increased through more encounters and more precise jumps, with two checkpoints in level 3 and three in level 4. Following playtest feedback, Pipeworks received wider platforms, 220 cm fixed gaps, rises up to 65 cm, and a wider lift waiting one second at each end. Central Tower uses 240 cm fixed gaps, rises up to 70 cm, and landing surfaces at least 400 cm wide. Its 300 cm lift travels at 145 cm/s and waits one second. Five ground enemies use type-specific speeds and are separated from four 80 cm traps. Checkpoints are before the bridge, after the bridge, and at the final section's entrance. Pickups remain optional.

## District identities

| District | Palette | Distinctive props |
|---|---|---|
| Workshop 07 | Petrol blue / cyan | Workshop facades, streetlights, crates |
| Foundry | Orange / copper | Furnaces, chimneys, extractors |
| Pipeworks | Green / lime | Pressurized tanks and large fans |
| Central Tower | Purple / magenta | Relay columns, antennas, signals |
| Cryo Labs | Ice cyan / white | Cooling capsules, crystals, refrigerant pipe decks |
| Scrap Yards | Rust red / copper | Magnetic cranes, scrap piles, crossbeam decks |
| Solar Works | Gold / photovoltaic blue | Circular receivers, solar panels, conductors |
| Bio Gardens | Pink / plum | Glowing trees, vivariums, vine-covered decks |

The four district props are saved in `Assets/Models/Scintilla_DistrictKit.blend`. Separate map materials apply palettes and skylines while keeping Scintilla recognizable and preserving restoration. Recovery maps use `_BeforeDistrictRevision` and are generated locally.

The original maps under `/Game/Platformer/Levels` are `L_Platformer_Prototype`, `L_02_Fonderia`, `L_03_Condotte`, and `L_04_Torre`. Internal asset names retain their original spelling to preserve references. All eight campaign maps are configured for packaging; no distributable executable has been produced.

`Config/campaign.json` contains layouts. `Scripts/prepare_campaign.py` prepares them and analytically checks fixed jumps. `Scripts/build_campaign.py` creates maps using original Blender assets and refuses to overwrite existing maps by default. `revise_districts.py` explicitly enables reconstruction of project-owned actors after making recovery copies. `create_district_models.py` generates the props in Blender.

## Original campaign validation

`python Scripts/playtest_progression.py` checks level selection using 14 game processes and an isolated save. All 266 checks passed: sequential unlocks, refusing level 1 to 3/4 skips, returning to earlier levels, replay without extra unlocks, persistence across maps/sessions, matching button availability, and reset state after selection. Report: `Assets/Models/progression_test_report.json`. These tests activate victory through GameState; they are not complete route tests.

- 21 fixed jumps in the original added levels were checked using actual movement/gravity/jump values, leaving at least 25 cm after taking off 55 cm before an edge.
- 45 runtime checks passed (15 per added level): spawn, HUD, collection registration, drone count, movement, checkpoints, respawn, pause, lift, generator, restoration, and actual next-level travel with reset health/progress.
- Foundry, Pipeworks, and Central Tower palettes and props were visually checked in PIE.
- After rebalancing, the full Pipeworks route passed with native movement, jumping, attack, and lift use, without teleporting or death. Checkpoint and pickups were confirmed. Command: `python Scripts/playtest_condotte.py`; reports: `Saved/ScintillaCondotteRoute.json` and `Assets/Models/condotte_traversal.json`.

Campaign integration checks use controlled positions to isolate systems. Pipeworks and Central Tower route tests traverse their full levels. After rebalancing, Central Tower passed three route checks: completion without teleport/death, checkpoint activation, and energy collection. Command: `python Scripts/playtest_torre.py`; reports: `Assets/Models/torre_traversal.json` and `Saved/ScintillaTorreRoute.json`. At that stage, Foundry had no full automated route test; the later difficulty pass covered all eight Normal routes. Human playtesting remains useful for difficulty and pacing.

Other reports: `Assets/Models/campaign_build_report.json`, `Assets/Models/campaign_jump_validation.json`, and `Platformer_2D_Game/Saved/ScintillaCampaign02.json`, `ScintillaCampaign03.json`, `ScintillaCampaign04.json`.

## Expansion to eight districts

Before the difficulty extension, levels 5-8 had 10, 11, 12, and 13 platforms, three checkpoints each, and distinct routes. Fixed gaps were 220, 230, 240, and 250 cm respectively; 38 jumps retained at least 117.5 cm theoretical margin with takeoff 55 cm before the edge. Patrols stay near platform centers, lifts wait 1.1 seconds at endpoints, and the camera follows the longer routes.

Twelve assets were modeled and colored in the connected Blender instance. Source: `Assets/Models/Expansion/Scintilla_ExpansionKit.blend`; preview: `blender_kit_preview.png`. FBX files and separate materials are imported under `/Game/Platformer/Art/Expansion`. New maps: `L_05_Cryo`, `L_06_Scrap`, `L_07_Solar`, and `L_08_Bio`, all included in packaging. `create_expansion_models.py`, `color_expansion_models.py`, `prepare_expansion.py`, and `build_expansion.py` rebuild the expansion; maps 1-4 are not reconstructed by that builder.

Winning level 4 unlocks level 5; each subsequent first victory unlocks only the next. Saves that completed the old Central Tower campaign automatically make Cryo Labs available, leaving levels 6-8 locked. The selector has eight cards in two columns and four rows. Final victory preserves every unlock.

`python Scripts/playtest_expansion.py` checks checkpoints, respawn, pause, lift, completion, and next-level travel, then traverses each new route using actual movement, jumping, and attack. Report: `Assets/Models/Expansion/runtime_report.json`. Map and selector previews: `Assets/UI/expansion_*.png`.

Expansion results: 60 integration checks and 12 full-route checks passed, with no deaths or teleporting on those original traversals. All palettes and eight selector cards were inspected in PIE. For current extended routes and difficulty validation, see [validation](validation.md).
