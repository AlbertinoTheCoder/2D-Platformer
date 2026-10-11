# Implementation plan

## Initial status and constraints

This plan records the original offline preparation phase. The user initially requested preparation without starting Unreal, connecting to MCP, or assuming an engine version before authorization. That authorization was subsequently given and implementation is now complete; see [validation](validation.md) for the actual results.

The initial workspace contained only `Docs/promptstart.md`, with no `.uproject`, assets, or C++ module. `Docs/Prompt.MD`, mentioned in the IDE, was not present on disk. The original brief remains the functional specification. The initial preparation files were working inputs, not an implemented game or directly importable Unreal assets.

## Initial decisions

- Coordinates in centimeters: movement on X, locked depth Y, height Z. Orthographic camera facing the XZ plane.
- Modular Blueprints with CharacterMovement as the foundation; Paper2D for visual representation and states. Enhanced Input for every control.
- Parameters and positions in `Config/platformer.json`, an offline manifest rather than a native Unreal configuration file.
- Assets under `/Game/Platformer`, using the brief's subfolders plus `Input`. Do not overwrite unrelated content.
- Use C++ only after verifying engine version, toolchain, and MCP capabilities. Do not generate fake `.uasset` files or graphs in assumed serialization formats.

The implementation later adopted a native `Scintilla` module with configurable Blueprints and Blender models. These choices retain the original gameplay contracts.

## Phases and exit criteria

1. **Inspection after authorization:** identify the active project, actual editor version, Paper2D/Enhanced Input plugins, maps, input settings, available MCP tools, and graph/UMG creation capabilities. Inventory collision and existing assets. Verify saving and compilation on a minimal asset before adding dependencies.
2. **Foundations:** create folders, damage interface, health and feedback components, input, GameMode, Controller, and GameState. Compile and save small batches. Every reference must resolve.
3. **Movement vertical slice:** temporary room, player, camera, acceleration/braking, variable jump, coyote time, and jump buffer. Test PIE before building the full level.
4. **Lifecycle:** damage, invulnerability, death, checkpoints, respawn, hazards, and kill zone. Death must trigger once; respawn must release all control locks.
5. **Interactions:** coins, HUD, patrol, stomp, attack, and moving platform. Test each actor in isolation and then with the player.
6. **Full level:** generate geometry from the manifest, opening tutorial, combat, checkpoint, moving section, and finale. Correct distances using actual PIE measurements.
7. **UI and feedback:** pause, death, completion, restart, animation states, and audio hooks. Check gamepad input, UI focus, and resizing.
8. **Playable delivery:** complete route, Blueprint compilation, saving, map reopening, and fresh PIE. Record actual results and limitations.

## System contracts

| System | Responsibility and communication |
|---|---|
| BPC_Health | HP, timed invulnerability, HealthChanged/Damaged/Died events; emit death once. Kill zones call an explicit death function that bypasses invulnerability. |
| BPI_Damageable | Shared entry point for attack, contact, and hazard damage; delegates to health. |
| BP_Player | Input, locomotion, facing, animation state, dedicated attack; no direct widget management. |
| BP_PlatformerGameState | Collectibles and Playing/Dead/Complete state; UI events. Collected items and defeated enemies persist after ordinary respawn; restart reloads and clears the level. |
| BP_PlatformerController | Mapping context, camera, UI creation/focus, pause/resume/restart. Pause input also works while paused. |
| BP_Checkpoint | Respawn transform with a clear capsule; activate the latest checkpoint and deactivate the previous one. Fall back to initial spawn. |
| BP_PatrolEnemy | Patrol limits, wall/edge probes, contact, death; recognize stomp before contact damage. |
| BP_MovingPlatform | Moving blocking surface, endpoints, speed, waits, ping-pong. Use CharacterMovement's movement base rather than manually attaching the player. |
| BPC_Feedback | Jump/Land/Coin/Damage/EnemyDeath/Checkpoint/Complete events, optional sounds, replaceable visual feedback. |

## Algorithms to implement

Jump: retain timestamps for last ground contact and Jump press. Consume a request when grounded or inside the coyote window, only if the current jump has not already been consumed. Rearm on landing and consume any valid buffer. Distinguish walking off an edge from jumping deliberately to prevent double jumps; do not rely only on default `CanJump` for coyote time. Releasing Jump cuts positive Z velocity once. Buffered requests retain button state so an already released tap produces a short jump. Clear timestamps on death, respawn, and completion.

Gravity: base value while rising, multiplier while falling, reset on landing/respawn. Convert configured absolute acceleration to GravityScale using the inspected world's actual gravity. Do not add impulses each frame.

Attack: separate cooldown and active window; box/trace ahead of facing, Damageable filter, and a per-attack set of already hit targets. Debug is off by default. Stomps require downward movement and contact with the enemy's top, followed by a controlled bounce.

Hazards: initial overlap plus a timer while inside allow further damage after invulnerability; cancel timers on exit/destruction. Coins disable collision before emitting collection to prevent double counting.

Pause: Pause input works while paused; focus Resume and restore the correct input mode on return. Restart reopens only the current map. Quit stops PIE through editor capabilities without closing the editor; packaged builds quit the game. The current implementation uses U instead of Escape to avoid the editor's Stop PIE shortcut.

Collision: ground blocks Pawn; collectibles/checkpoints/goals overlap only the player; attacks ignore ground and player. Confirm existing presets before adding channels. Keep the capsule unchanged during visual squash/stretch.

Limit Tick to movement, camera, platforms, and logic that requires it. Drive health, UI, checkpoints, and feedback through events/timers.

## Layout and offline validation

The preparation script computes apex and range with separate rising/falling gravity. It reserves 20% of theoretical range and adds the capsule diameter to the gap. It assumes a held jump and maximum horizontal speed; it does not prove playability with acceleration, collision, or moving platforms. Cross the bridge by waiting for and riding its platform rather than jumping the entire gap.

## Required editor checks

- Automatic correct spawn and constrained movement; A/D, arrows, and gamepad.
- Distinct short/long jumps; coyote valid at 0.10 s and expired at 0.16 s; buffer valid at 0.10 s before landing and expired at 0.16 s, allowing one frame of tolerance.
- No double jump; checks at 30/60/120 fps; smooth camera without unexpected rotation.
- Solid collision, jumping under platforms, moving-platform transport and reversal at endpoints.
- Single collection, correct counter, HP/HUD updates, invulnerability, repeated spike damage.
- Death from HP and kill zones, message, respawn without stale input; latest checkpoint and initial fallback.
- Patrol reversal at wall/limit/edge; contact, stomp, attack, cooldown without duplicate damage.
- Gamepad pause/resume, restart while paused, safe Quit in PIE; HUD at 1280x720, 1920x1080, and ultrawide.
- Goal locks gameplay, shows collection total, allows restart; no death after Complete.
- Reachable Idle/Run/Jump/Fall/Attack/Hurt/Death states; safe optional audio hooks.
- Complete playable route, no significant Blueprint errors, saved assets and valid references after reopening.

These are acceptance requirements, not a claim that every hardware, resolution, or frame-rate combination has been tested. See [validation](validation.md) for completed checks.
