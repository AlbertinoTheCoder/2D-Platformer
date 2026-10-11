# SCINTILLA prototype validation

This document records the successive implementation passes. Counts, limitations, and screenshots describe each pass rather than implying that older results cover later changes. The latest difficulty results are at the end. Reports in `Saved/` are local outputs; retained reports and previews are under `Assets/`.

## Gameplay

Runtime reports from October 10, 2026 record 30 successful integration checks and three successful route checks, with no failures:

- `Platformer_2D_Game/Saved/ScintillaPlaytest.json`: movement, braking, variable jump, coyote time, jump buffering, collection, checkpoints, health, invulnerability, death/respawn, patrol, attack, moving platform, hazards, pause, and completion.
- `Platformer_2D_Game/Saved/ScintillaRoute.json`: full traversal without teleporting or death, checkpoint activation, and energy collection.

These use programmed input with rendering disabled. They do not verify scene visibility or physical keyboard/gamepad controls.

## Camera

During visual playtesting the scene was black while the HUD remained readable. The orthographic camera used manual exposure with physical camera exposure enabled. The fix explicitly disables physical exposure, sets compensation to zero, and preserves horizontal field of view for stable framing across viewport aspect ratios.

The Development Editor build passed. After restart, a PIE capture with postprocessing enabled confirmed visible character, platforms, buildings, and HUD.

## Original Blender kit

Eleven Blender static meshes were imported with dedicated materials, and 58 decorations without collision were applied. The player uses the new robot; drone and pickups have new meshes, and checkpoints, generator, and hazards were replaced. Facades retain the native city's color transformation. Source: `Assets/Models/Scintilla_ModelKit.blend`; import report: `Assets/Models/unreal_import_report.json`.

Visual PIE inspection confirmed robot and environment visibility with postprocessing enabled. All 30 runtime checks passed again after import, with no failures. Report: `Saved/ScintillaPlaytest.json`; log: `Saved/Logs/ScintillaArtSmoke.log`. The visible editor remained open while the separate test ran.

## Input correction

Movement only worked to the right because the generator wrote modifiers into the deprecated `mappings` array, while UE 5.8 reads `default_key_mappings`. The runtime asset and script now use the latter. Readback confirmed `InputModifierNegate` on A and Left, and the stick dead zone. The game restarted without closing the editor.

## First procedural animation, later replaced by the rig

Imported mesh/capsule alignment was corrected so soles meet the platform's visual surface, including landing squash. The first mechanical material animation alternated arms/legs, posed jumps and attacks, and moved the idle head slightly. Collision continued to use the capsule; this pass was not yet a Blender skeletal rig.

The Development Editor build passed. All 34 runtime checks passed, including four new checks for grounding, running parameters, stopping, and airborne pose. Report: `Saved/ScintillaPlaytest.json`; log: `Saved/Logs/ScintillaAnimationSmoke.log`. Ground contact was also checked in PIE. Unreal reopened automatically after building and was left playing.

## Blender rig and mechanical clips

Static-model deformation was replaced by `SK_Scintilla`: nine original bones plus the FBX armature node, rigid single-bone weights, and eight Blender clips. The generator verifies that every vertex belongs to one joint. No animation contains scale keys. Robot materials set World Position Offset to zero, and the player no longer squashes the mesh. Source: `Assets/Models/RobotRig/Scintilla_Rig.blend`; `manifest.json`, `import_report.json`, and `configure_report.json` record generation, clip durations, and Blueprint configuration.

The Development Editor build passed. `-ScintillaSmoke` now has 35 checks, including rig/eight-clip presence, sole grounding, run advancement, idle return, and jump selection. Run, attack, and jump poses were inspected closely in PIE. Stride was shortened to avoid overlapping boots, and the tool arm direction was corrected. Clip transitions are direct; there is no blending AnimBlueprint. Collision remains on the Character capsule.

The final rerun after clip corrections passed all 35 checks. Retained report: `Assets/Models/RobotRig/runtime_report.json`; log: `Saved/Logs/ScintillaRigSmoke.log`. Unreal reopened visibly and remained playing Pipeworks, with normal camera and automatic animation restored after inspection.

## District revision after playtesting

Maps gained separate copper/orange, green/lime, and purple/magenta palettes, with Blender furnaces, tanks, fans, and relays. Previous maps were saved with `_BeforeDistrictRevision`. Level 3 was rebalanced with 220 cm gaps, wider landings, rises up to 65 cm, a 280 cm lift at 125 cm/s, and one-second endpoint waits. A trap and drone were moved to separate encounters. Central Tower's final jump gained 50 cm margin.

The initial complete route test found a punishing encounter before the checkpoint. After separating encounters, the native test traversed all of Pipeworks without death or teleporting; all three route checks passed. Three district themes were visually inspected in PIE. The build passed; the editor reopened automatically and remained on the third district.

## Other checks at that stage

The post-victory selector passed 87 checks across six separate sessions with a save isolated from the player's progress. Checks covered actual selected-map loading, replay without lost unlocks, rejected locked/out-of-range indices, disk persistence, at most one new unlock per victory, and retained unlocks after the finale. Script: `Scripts/playtest_progression.py`; report: `Assets/Models/progression_test_report.json`. Victories were triggered directly to verify menu flow. The menu was also inspected in PIE without writing the player's save; card widths and locked-button text were corrected.

After visual adjustments, the build and all 35 regression checks passed (`Assets/Models/chooser_smoke_report.json`, `Saved/Logs/ScintillaChooserSmoke.log`). The final menu capture confirmed fitting cards and labels. Preview gameplay restarted without saving simulated victories; Unreal remained open and playable on level 1.

The campaign added three maps and travel between four districts. The new maps passed 45 runtime checks and 21 analytical jump checks. Actual next-level loading, including returning from Central Tower to Workshop for replay, was verified. Details and limits: [campaign](campaign.md).

Graphics and audio were provisional. Human checks remained for hardware controls, stomp input, restart/quit buttons, and different frame rates and resolutions.

## Blender expansion: levels 5-8

The Development Editor build passed. Twelve models were created and colored in the connected Blender instance, exported as FBX, and imported into four maps with distinct palettes/skylines. All 38 fixed jumps passed analytical checks with at least 117.5 cm margin.

Eight-level progression passed 266 checks across 14 sessions with an isolated save. The four new maps passed 60 integration checks and 12 full-route checks: all four were traversed without teleporting or death, with checkpoints activated and energy collected. Reports: `Assets/Models/progression_test_report.json` and `Assets/Models/Expansion/runtime_report.json`. Integration checks reposition the player to isolate systems; route checks use actual movement, jumping, attacks, and lifts.

The four palettes and eight selector buttons were inspected in PIE. A save that completed the original campaign showed Cryo Labs unlocked and later districts locked. Unreal reopened after each build and remained playing Cryo Labs.

## Facing and directional walking

A/D show actual side profiles using the same mirrored Blender walk cycle. S faces the camera and W the city, changing only the model with a brief interpolated turn. Facing remains after release, and new A/D movement restores the matching side profile. Attacks use the last walking direction.

The eight clips were re-exported from Blender with limb motion on the travel axis. Recovery animations use `_BeforeFacing`; the earlier rig is under `Assets/Models/RobotRig/BeforeFacing` locally.

The Development Editor build passed, along with 17 directional and 35 gameplay checks: A/D profiles, same clip/mirrored pose, S/W, held facing, plane constraint, ground contact, pause, and attack direction. Script: `Scripts/playtest_facing.py`; report: `Assets/Models/RobotRig/facing_report.json`.

## Blender enemies and additional encounters

Three original bodies (Scout, Charger, Sentinel) and two animated parts (rotor/wheel) were exported and imported with their own materials. All eight maps were saved with 37 enemies, up from 28. Recovery maps use `_BeforeEnemyRoster`. The Development Editor build passed; the existing Slate font constructor deprecation warning remained, without compilation errors.

The revision passed 133 runtime checks: 20 enemy checks, 35 gameplay regression checks, 60 integration checks on maps 5-8, and 18 full-route checks on Pipeworks, Central Tower, and levels 5-8. All six traversals passed without death or teleporting. The first Scrap Yards probe found a Charger near a post-trap landing. After increasing expansion enemy/trap separation to 350 cm, all four expansion maps passed integration and route checks again.

Specific checks cover actual Blender meshes, moving rotor/wheels, dash warning/recovery/patrol bounds, two distinct hits for Sentinels, stomps bypassing shields, and player bounce. Reports: `Assets/Models/Enemies/runtime_report.json`, `Assets/UI/integration_report.json`, `Assets/Models/Expansion/runtime_report.json`, `Assets/Models/condotte_traversal.json`, and `Assets/Models/torre_traversal.json`. Isolated checks use controlled positions; traversals use native movement/combat.

Previews were inspected in Blender and PIE: `Assets/Models/Enemies/blender_enemy_preview.png` and `Assets/UI/enemies_in_unreal.png`. The temporary showcase was removed by restarting normal gameplay. Unreal reopened after compilation and remained in PIE on Workshop.

## Fallen cities and repair before selection

Nine original assets were modeled in connected Blender and imported with instances of the existing rigid materials. Each of the eight districts had 123 city components, plus decorative props tagged for repair. The application script verifies that generated components have no collision and all eight map saves succeed. Recovery: `_BeforeRestoration` maps and `Assets/Models/City/BeforeCityModels.blend` locally.

The final Development Editor build passed. After visual corrections, `python Scripts/playtest_restoration.py` passed all 120 checks across eight maps: Blender facades, initially collapsed roofs, timed progress, blocked input/travel during repair, completion before the menu, aligned roofs, hidden rubble/dry vegetation, regrown foliage, centered camera wide enough for the district, selector only after 7.5 seconds, and only the next level unlocked.

The new wait also passed all 266 progression checks across 14 sessions. After terrain/pose adjustments, all 35 gameplay regression checks passed again. Revision total: 421 checks, no failures. Reports: `Assets/Models/City/runtime_report.json`, `Assets/Models/City/validation_report.json`, `Assets/Models/progression_test_report.json`, and `Assets/UI/integration_report.json`. These verify systems and the sequence, not new full-route traversals.

The four final stages were inspected in PIE: `Assets/UI/city_before.png`, `city_repair.png`, `city_reveal.png`, and `city_chooser.png`. Roof rotation was corrected to the visible platformer plane; rolling terrain was added and the repair light line checked. Previews restored the player's original save. Unreal reopened after every build and remained playing Workshop.

## U pause and level selection

Keyboard pause uses U; gamepad pause remains Start. Enhanced Input no longer maps Escape to IA_Pause, and the footer displays U. Earlier input copy: `IMC_Platformer_BeforePauseU`. Pause includes **CHOOSE LEVEL**; the selector keeps the world paused, enables only unlocked districts, and offers **RESUME** and **BACK TO PAUSE**. Choosing a map starts a fresh run without awarding victories or unlocks. Post-victory selection still waits for repair and, after the later rating change, CONTINUE.

The build passed. `python Scripts/playtest_pause.py` passed 40 checks in two sessions with isolated saves: actual U input events for pause/resume, selector without victory, all eight button states, refused locked/invalid indices, return to pause, replay, and Foundry-to-Workshop travel with reset health/state and retained unlocks. All 35 gameplay regression checks passed too: 75 checks, no failures.

Both screens were inspected in PIE (`Assets/UI/pause_U.png`, `pause_level_chooser.png`). U pressed through Slate while the selector had focus resumed the game, verified in the live world. Reports: `Assets/UI/pause_input_report.json` and `pause_runtime_report.json`. Unreal reopened after compilation and remained in normal gameplay without the pause menu.

## Buildings and trees grounded on slopes

Fixed the constant height that left some buildings and trees floating over depressions. Foundations follow the lowest point under facade width; roofs and attached vegetation receive the same offset. Trunks and canopies share the local surface elevation. Terrain was not regenerated, moved, or modified: `SM_CityTerrain.uasset` retained the same SHA-256 and its component transform was identical across all eight maps.

The build passed. `Scripts/ground_city_scenery.py` saved eight maps after making `_BeforeGrounding` copies. All 136 `Scripts/playtest_restoration.py` checks passed, including every district's 24 facades and 12 trees before/after repair, plus the sequence and selector. Reports: `Assets/Models/City/grounding_map_report.json`, `grounding_validation_report.json`, and `runtime_report.json`.

Foundry was inspected closely in the fallen pose and fully repaired panorama (`Assets/UI/city_before.png`, `city_reveal.png`). Roots and foundations follow the existing slopes. Previews preserved the original save. Unreal reopened after building and remained playing Foundry.

## Rating before level selection

The generator freezes time, damage, and energy metrics and computes an S/A/B/C/D grade. After repair, the popup shows the three results and their points; **CONTINUE** opens the selector. Travel remains blocked until confirmation. Pauses do not count toward elapsed time, respawns preserve cumulative damage, and grades do not change unlocks.

The Development Editor build passed. Rating tests passed 20 checks: five grades, variation in three criteria, pause, invulnerability, death/respawn, frozen time, confirmation blocked during repair, and selector after CONTINUE. Eight maps passed 144 checks of the complete sequence. All 40 pause and 35 gameplay/HUD checks passed, with no failures.

The popup and subsequent menu were inspected in PIE. CONTINUE was activated through actual Slate input, and confirmation was verified in GameState. Images: `Assets/UI/rating_popup.png` and `rating_continue_chooser.png`; reports: `rating_runtime_report.json` and `rating_live_report.json`. The player's save was preserved. Unreal reopened after compilation and remained in normal gameplay.

Progression was rechecked in 14 separate sessions with an isolated save. All checks passed, including persistence, replay, map travel, and refusing locked levels after rating confirmation. Updated report: `Assets/Models/progression_test_report.json`.

## Difficulty, traps, and extended routes

All eight requested mechanics were implemented with 17 new models created in connected Blender and imported in Unreal. Each map gained seven platforms, two checkpoints, seven energy fragments, two wind zones, ice, falling/retracting spikes, rotating hammer/axe, and one or two flying enemies. Length increased 50-79%; the campaign now has 50 enemies. Original maps use `_BeforeDifficulty` locally. English signs use an unlit font material to stay readable in the blackout.

Normal/Hard/Hardcore are selected from pause. Selecting one restarts the level and persists the setting. Attempts are 8/5/3. Exhausting attempts performs actual map travel, clearing energy/checkpoints without losing unlocks. The build passed. Final successful checks:

| Report group | Checks |
|---|---:|
| Mechanics and difficulty menu | 376 |
| Restoration | 144 |
| Mission rating | 20 |
| Gameplay/HUD | 35 |
| Pause | 40 |
| Complete Normal routes | 30 |
| Total | 645 |

All eight complete Normal routes passed within available attempts using native input and checkpoint respawns. Some routes required respawns; this is not a zero-death claim. Hard and Hardcore passed settings, persistence, and reset checks; complete routes were tested only in Normal. Final reports had no failures.

The kit, six trap types, and difficulty menu were visually inspected. Drone wings and axe contact match FBX conversion. Reports and images: `Assets/Models/Difficulty`; details: [difficulty](difficulty.md). Previews preserve the player's save. Unreal reopened after every build and remained in visible normal gameplay; the resolved map-save error log window was closed.

## Scattered obstacles and continuous motion

Existing obstacle actors, signs, supports, and flying patrols were moved in all eight saved maps after creating `_BeforeObstacleScatter` recovery copies. Seeded placements put three to five of the seven obstacles on each original route, with the rest spread through the extension. Ice and aerial encounters use wide stations; existing platforms, terrain, checkpoints, and generators are preserved.

Backward wind now combines an entry impulse, continuous force, and a ramped opposing speed limit, so running input no longer erases its effect. Cyan airflow arrows show the force direction. Rotor angle is integrated without snapping at activation. Hammer and axe motion is a continuous 2.8-second pendulum cycle; the spike carrier stays inside its housing with a 0.14-second rise and 0.18-second retraction on a 2.4-second cycle.

The Development Editor build passed. All 384 final mechanics, contact, difficulty, persistence, and reset checks passed across eight maps. These include noticeable backward push, reduced opposing running velocity, continuous tool motion without wraparound snaps, fast spike extension without visibility popping, damage contacts, and obstacle distribution before the extension. Report: `Assets/Models/Difficulty/runtime_report.json`. All six obstacle types were inspected in PIE; captures are in the same folder.

Earlier complete-route probes timed out on Pipeworks because the bot made full-length jumps into suspended heads and stopped partway through a timed crossing. The route controller now uses short jumps onto the challenge waiting pads, waits outside the tool's reach, and commits to a crossing rather than stopping beneath the moving head. Wind checks look ahead through the jump window. This changes the test controller, not player controls or collision. Full-route results are recorded in `Assets/Models/Difficulty/traversal_report.json`; only completed passing entries count as verified routes. Human input, full Hard/Hardcore traversals, and frame-rate variations remain outside this validation pass.

The completed traversal reports contain 32 successful checks: all eight Normal routes completed within the eight-attempt budget, using native movement, combat, and checkpoint respawns without scripted teleporting. Together with the 384 mechanics checks, this revision records 416 successful checks. Unreal was reopened after compilation and left in a fresh playable PIE session.

## Full rotation and tool-shaped hitboxes

Hammer and axe damage previously used a world-aligned box around an approximate moving center, treating the player's capsule as a rectangle. At rotated angles this could count empty corners as hits. Tool damage now uses the authored hammer-head outline or asymmetric FBX axe-blade outline extruded through its thickness, transformed with the visible component, against the actual scaled, rounded player capsule. Solid interior contacts are included. The shaft is not the damaging surface. Scintilla's movement capsule remains unchanged.

Both tools now make continuous full 360-degree revolutions every 2.8 seconds in Normal, accelerated by difficulty. Runtime motion is sampled at intervals of at most four degrees during ordinary frame times to catch fast contacts. The route helper uses the full rotation rather than the old pendulum safe window.

The Development Editor build passed. New runtime checks cover head/blade contact at five orientations, misses on the empty side, rounded-capsule corner misses, continuous motion, wraparound continuity, and actual health loss. Visual PIE captures show the head/blade above the pivot at half a revolution, which the old pendulum could not reach. Reports are in `Assets/Models/Difficulty/runtime_report.json`; the older traversal report predates this rotation change and is not a new complete-route validation. Unreal was reopened and the previews preserve the player's campaign save.

Final result: 432 checks passed across all eight maps, with zero failures. The editor is open with a fresh PIE game running.
