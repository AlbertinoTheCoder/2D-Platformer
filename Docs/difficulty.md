# Difficulty and longer routes

All eight campaign levels include the requested mechanics. The original route leads into seven new, wide challenge platforms, with short gaps, waiting areas, an entry checkpoint and a second checkpoint halfway through. The generator is at the new end of each route. The city restoration camera covers the full extended district.

## Difficulty selection

Press **U**, select **DIFFICULTY**, then choose **NORMAL**, **HARD**, or **HARDCORE**. Selecting a mode restarts the current level, as indicated in the menu. The setting persists across map travel and game sessions; campaign unlocks are preserved.

| Mode | Attempts per run | Trap cycle speed | Wind acceleration | Flying enemy speed |
| --- | --- | --- | --- | --- |
| Normal | 8 | 1x | 160 cm/s² | 1x |
| Hard | 5 | 1.18x | 230 cm/s² | 1.15x |
| Hardcore | 3 | 1.36x | 300 cm/s² | 1.30x |

The HUD shows the mode and remaining attempts. Each death consumes one attempt. Ordinary respawns retain collected energy and use the latest checkpoint. When attempts run out, the level reloads from its beginning: checkpoints, energy, enemy state, and the attempt counter reset. Unlocks and the selected difficulty remain saved.

## Mechanics

- **Intermittent wind:** separate backward and downward gust zones cross platform gaps. The fan and amber warning signal the gust; force ramps up over 0.35 seconds. Stronger difficulties increase force and shorten the cycle.
- **Flying enemies:** wasp and survey drones patrol independently of ground traces, bob vertically, and animate their wings. Discharge and stomping can defeat them.
- **Falling spikes:** a mounted rack warns before dropping, pauses near the platform, then retracts. Damage follows the moving rack.
- **Slippery floor:** cyan ice tiles reduce friction and braking while standing on them. Normal movement is restored on leaving the surface.
- **Rising spikes:** a pit warns before its rack rises, remains dangerous briefly, then retracts below the floor.
- **Rotating hammers and axes:** independent motor pivots animate a full revolution after an amber cue. Each tool parks overhead during its safe window; damage follows its moving head.
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

All six obstacle visuals and the difficulty chooser were inspected in PIE. Axe damage follows the blade side after FBX conversion, and mirrored drone wings extend outward. Warning signs reuse the engine distance-field font graph with unlit text so they remain readable before restoration. Saved map reports are in `Assets/Models/Difficulty`; the user campaign save is preserved by the previews. Unreal was reopened after compilation and left in a fresh playable session.
