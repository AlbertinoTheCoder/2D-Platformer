# Difficulty and longer routes

All eight campaign levels include the requested mechanics. Seven additional wide platforms extend each route, with short gaps and two additional checkpoints. Obstacles are scattered across both the original route and the extension, and flyers use separate stations away from existing ground encounters, using a different reproducible random seed per district. Spawn areas, lift gaps, checkpoints, and existing encounters are protected from overlapping placements. The generator is at the new end of each route. The city restoration camera covers the full extended district.

## Difficulty selection

Press **U**, select **DIFFICULTY**, then choose **NORMAL**, **HARD**, or **HARDCORE**. Selecting a mode restarts the current level, as indicated in the menu. The setting persists across map travel and game sessions; campaign unlocks are preserved.

| Mode | Attempts per run | Trap cycle speed | Wind acceleration | Flying enemy speed |
| --- | --- | --- | --- | --- |
| Normal | 8 | 1x | 1100 backward / 600 downward cm/s^2 | 1x |
| Hard | 5 | 1.18x | 1320 backward / 720 downward cm/s^2 | 1.15x |
| Hardcore | 3 | 1.36x | 1540 backward / 840 downward cm/s^2 | 1.30x |

The HUD shows the mode and remaining attempts. Each death consumes one attempt. Ordinary respawns retain collected energy and use the latest checkpoint. When attempts run out, the level reloads from its beginning: checkpoints, energy, enemy state, and the attempt counter reset. Unlocks and the selected difficulty remain saved.

## Mechanics

- **Intermittent wind:** separate backward and downward gust zones cross platform gaps. The fan, amber warning, and moving cyan airflow arrows signal the gust. An entry impulse makes it noticeable against air control; continuous force ramps up over 0.35 seconds. Backward gusts also ramp the opposing running speed to 60%/55%/50%, so movement input cannot erase the wind each frame. Rotor speed changes without resetting its angle. Stronger difficulties increase force and shorten the cycle.
- **Flying enemies:** wasp and survey drones patrol independently of ground traces, bob vertically, and animate their wings. Discharge and stomping can defeat them.
- **Falling spikes:** a mounted rack warns before dropping, pauses near the platform, then retracts. Damage follows the moving rack.
- **Slippery floor:** cyan ice covers the entire supporting platform, including both edges, and reduces friction and braking while standing on it. Capsule overhang remains slippery until Scintilla actually leaves the platform, so there is no dry braking strip at the end. Normal movement is restored on landing on a non-icy surface.
- **Rising spikes:** a 2.4-second cycle includes a 0.35-second warning, smooth 0.14-second rise, 0.65-second hold, and 0.18-second retraction. The carrier stays inside the housing; the mesh does not pop in and out of visibility.
- **Rotating hammers and axes:** independent pivots turn through full 360-degree revolutions with a 2.8-second period in Normal. There is no parked interval or angle snap; damage follows the rotating head or blade shape and uses the actual rounded player capsule, rather than a world-aligned bounding box. Rotation is sampled between frames to avoid missing fast contacts. Cross when the head swings away.
- **Limited attempts:** full restart after 8, 5, or 3 deaths, according to the chosen mode.
- **Longer levels:** seven additional platforms, seven energy pickups, both wind directions, all trap families and one or two flying enemies in each district. New warning signs are English.

## Blender sources and recovery

17 original bevelled industrial meshes were authored in the connected Blender. The kit includes separate rotors, wings, spike racks, motor bearings, hammer/axe tools, an ice deck, attempt terminal and battery cell, and reinforced walkway modules. Mechanical origins match their animation pivots.

- Source: `Assets/Models/Difficulty/Scintilla_DifficultyKit.blend`.
- FBX, palette and mesh metadata: `Assets/Models/Difficulty/manifest.json`.
- Gallery: `Assets/Models/Difficulty/kit_preview.png`.
- Unreal meshes: `/Game/Platformer/Art/Difficulty`.
- Original maps: copies ending in `_BeforeDifficulty`.
- Rebuild steps: `create_difficulty_models.py`, `import_difficulty_assets.py`, `prepare_difficulty.py`, and `apply_difficulty_maps.py`.

The new fixed jumps have at least 338.2 cm of analytical horizontal margin with the existing jump settings. This measures geometry; actual trap timing, wind and combat are checked separately in the runtime tests.

Validation scripts: `playtest_difficulty.py` exercises contacts, wind, sliding, aerial combat, persistence and real reset travel on every map; `playtest_difficulty_routes.py` traverses the extended routes with real movement and attacks. Both use isolated campaign saves. `capture_difficulty.py` inspects the live obstacle visuals and restores a fresh game afterward.

Final validation: 376 mechanic/menu/persistence checks across all eight maps passed, together with 144 restoration checks, 20 rating checks, 35 gameplay/HUD checks and 40 pause/level-selection checks. All eight full Normal routes were completed with native movement, combat and checkpoint respawns, within their attempt budgets: levels 3 and 6 used one respawn, 4 and 7 used two, and the others completed without deaths. Route reports contain 30 checks; total 645 successful checks, zero failures in the final reports. Earlier probe failures caused by old collectible counts and generator coordinates were corrected to test the extended levels.

All six obstacle visuals and the difficulty chooser were inspected in PIE. Axe damage follows the blade side after FBX conversion, and mirrored drone wings extend outward. Saved map reports are in `Assets/Models/Difficulty`; the user campaign save is preserved by the previews. Unreal was reopened after compilation and left in a fresh playable session.

Obstacle instruction signs and the prototype's jump, drone, and lift tutorial signs have been removed. Players discover the mechanics through attempts and deaths. The level build scripts no longer generate these hints. `Scripts/remove_obstacle_hints.py` creates `_BeforeHintRemoval` recovery copies and reloads every saved campaign map to verify removal; results are recorded in `Assets/Models/Difficulty/hint_removal_report.json`.

## Scattered obstacle revision

`python Scripts/scatter_difficulty.py` plans seeded placements. `Scripts/apply_scattered_difficulty.py` moves existing obstacles, supports, and flyers in the editor after creating `_BeforeObstacleScatter` recovery copies. It preserves platforms, terrain, generators, and checkpoints. Three to five of the seven obstacles now appear before the extension in each district. Replaying keeps positions stable; different districts use different seeds.

The earlier validation totals above describe the initial obstacle pass; the revision results are recorded in [validation](validation.md).

Ice and aerial patrols use wider stations rather than narrow takeoff/landing platforms. This leaves room to recover momentum without forcing a difficult jump immediately after a slip.

Scattered revision results: 384 mechanic/menu/contact checks and 32 complete-route checks passed. All eight Normal routes completed within their attempt budgets; some needed checkpoint respawns. Hard and Hardcore complete routes remain unverified. See the latest section in `Docs/validation.md`.
