You are working directly inside an Unreal Engine project through the Unreal Engine MCP integration.

Your goal is to BUILD a complete playable 2D platformer prototype inside Unreal Engine.

Do not only explain what should be done. Use the available Unreal Engine MCP tools to inspect the project, create assets, Blueprints, levels, components, input mappings, gameplay systems, UI, and configuration directly inside the project.

## CORE RULES

1. First inspect the current Unreal Engine project.
2. Detect the Unreal Engine version and existing project structure.
3. Do not delete or overwrite unrelated existing assets.
4. Create a clean folder structure specifically for this game.
5. Use Unreal Engine MCP tools whenever possible instead of asking me to manually create things.
6. Save all created assets.
7. Compile and validate Blueprints after meaningful changes.
8. Fix errors instead of leaving broken references.
9. Frequently test that the project is still playable.
10. Do not stop after creating the basic character. Continue until the full prototype described below is functional.

If something cannot be performed through MCP, create the required Blueprint/C++/configuration files using the safest available method and then integrate them into Unreal Engine.

## GAME

Create a polished 2D side-scrolling platformer.

Use Unreal's 2D systems such as Paper2D where appropriate.

The game should feel responsive rather than like the default Unreal Character template.

The player moves from left to right through a platforming level while avoiding hazards, collecting items, fighting simple enemies, activating checkpoints, and eventually reaching the end of the level.

The visual assets may initially use simple placeholder sprites, colored shapes, or procedural assets.

Gameplay quality is more important than final artwork.

## PROJECT STRUCTURE

Create something similar to:

Content/
    Platformer/
        Characters/
        Enemies/
        Levels/
        Blueprints/
        Components/
        Sprites/
        Tiles/
        Materials/
        UI/
        Audio/
        Pickups/
        Environment/
        GameModes/

Keep names consistent and readable.

Use prefixes where useful such as:

BP_
WBP_
M_
MI_
S_
T_
DA_

## PLAYER CHARACTER

Create the main player character.

The player must support:

- left movement
- right movement
- jumping
- variable jump height
- falling
- landing
- facing direction
- basic animation state handling
- collision with the environment

Movement must feel responsive.

Do NOT simply use Unreal's default movement values.

Implement platformer-oriented movement tuning.

Include:

Acceleration.

Deceleration.

Ground friction.

Air control.

Maximum movement speed.

Gravity tuning.

Jump velocity.

Variable jump height.

When the player releases the jump button early, reduce upward velocity so short taps produce smaller jumps.

## COYOTE TIME

Implement coyote time.

After walking off a platform, the player should still be allowed to jump for approximately:

0.10 to 0.15 seconds.

Expose the value so it can easily be changed later.

## JUMP BUFFERING

Implement jump buffering.

If the player presses jump shortly before touching the ground, the jump should automatically happen when the player lands.

Use approximately:

0.10 to 0.15 seconds.

Expose the value.

## BETTER FALLING

Make falling slightly faster than rising so jumping feels responsive.

Use gravity adjustments or another clean solution.

Avoid creating unstable physics behavior.

## CAMERA

Create a 2D side-scrolling camera.

The camera should:

follow the player smoothly

stay primarily focused on horizontal movement

avoid unnecessary rotation

have configurable smoothing

keep enough visibility ahead of the player

Optionally add a small amount of look-ahead based on the direction the player is moving.

The camera must not feel directly welded to the player.

## INPUT

Use Unreal Engine Enhanced Input.

Create actions for:

Move

Jump

Attack

Interact

Pause

Support:

A / D

Left / Right arrows

Space

and reasonable gamepad equivalents.

Movement should use an axis/action-based system rather than hardcoding keyboard checks.

## HEALTH

Give the player a simple health system.

Example:

3 hearts / 3 HP.

Create reusable damage handling instead of placing unrelated damage logic everywhere.

When taking damage:

reduce health

briefly prevent repeated damage

provide clear feedback

optionally knock the player backwards

When health reaches zero:

play the death state

disable normal control

wait briefly

respawn at the latest checkpoint

## CHECKPOINT SYSTEM

Create checkpoint actors.

When the player touches a checkpoint:

activate it

store its respawn position

visually indicate that it is active

Only the latest activated checkpoint should be used when the player dies.

If no checkpoint has been activated, respawn at the level's starting location.

## HAZARDS

Create reusable hazard actors.

Examples:

spikes

bottomless pits

moving hazard

Touching spikes should damage the player.

Falling into a kill zone should immediately trigger death/respawn.

Do not duplicate the entire damage system inside every hazard.

Use reusable interfaces, components, functions, or parent Blueprints.

## COLLECTIBLES

Create collectible items.

For the prototype use coins or crystals.

When collected:

play a small visual/audio reaction if possible

increase the collectible counter

remove or hide the collectible

update the HUD

Place multiple collectibles throughout the level.

## ENEMY

Create at least one basic enemy.

Example enemy:

a small creature that patrols between two points.

The enemy should:

walk back and forth

detect walls or patrol limits

turn around correctly

damage the player on contact

have a simple death mechanic

The player should be able to defeat the enemy either by:

jumping on its head

OR

using a basic attack.

Prefer implementing both if practical.

## PLAYER ATTACK

Create a very simple attack mechanic.

For example:

a short melee attack in front of the player.

The attack should:

respect player facing direction

have a short cooldown

detect enemies

damage or defeat enemies

not permanently display its collision box

Use a dedicated attack hitbox or trace rather than using the entire player's collision capsule.

## MOVING PLATFORM

Create a reusable moving platform Blueprint.

Expose:

starting point

end point

speed

wait time

loop behavior

The player should remain properly attached to or carried by the platform while standing on it.

Place at least one moving platform in the level.

## LEVEL DESIGN

Create a complete test level rather than an empty flat room.

The level should contain multiple platforming sections.

Include:

starting area

basic jumping tutorial section

different platform heights

gaps

spikes

collectibles

at least one enemy

at least one checkpoint

moving platform section

more difficult final platforming section

goal/end area

The level should gradually increase in difficulty.

Do not make jumps impossible.

Use the actual character movement values when designing jump distances.

## LEVEL GOAL

Create a goal object near the end of the level.

Example:

portal

door

flag

crystal

When the player reaches it:

disable normal gameplay

display a LEVEL COMPLETE UI

show collected items

allow the player to restart the level

## HUD

Create a clean HUD.

Display:

health

collectibles

Optional:

current checkpoint indicator

Use Unreal UMG.

Do not make the UI unnecessarily large.

Anchor elements correctly so they work at multiple resolutions.

## PAUSE MENU

Create a pause menu.

Pressing Escape / Start should pause the game.

Include:

Resume

Restart Level

Quit

If running in editor, make sure the Quit behavior does not cause unnecessary problems.

## DEATH UI

When the player dies, show a small transition or message such as:

YOU DIED

Then respawn.

Do not require manually restarting the entire game every time.

## ANIMATION SYSTEM

Even if final artwork does not exist yet, structure the player so these states exist:

Idle

Run

Jump

Fall

Attack

Hurt

Death

If actual frame animations cannot be generated reasonably, use placeholder sprite states while keeping the animation state architecture ready for replacement.

## PLAYER STATE

Avoid putting every gameplay system into one giant Blueprint graph.

Separate reusable functionality where reasonable.

Examples:

Health Component

Checkpoint system

Damage interface

Collectible manager

Player movement logic

Game state

Keep the architecture understandable.

## VISUAL FEEDBACK

Add basic game feel where possible.

Examples:

slight player squash/stretch on landing

small landing effect

collectible pop effect

enemy death effect

damage flash

camera shake on strong impacts

small particles

Do not overdo screen shake.

Gameplay readability comes first.

## AUDIO

Create hooks/placeholders for:

jump

landing

collectible

damage

enemy death

checkpoint

level complete

If no audio files exist, structure the events so sounds can easily be inserted later.

Do not block development because audio assets are unavailable.

## GAME MODE

Create the necessary:

GameMode

Player Controller if needed

Player Character/Pawn

Game Instance only if actually useful

Set the correct GameMode for the platformer level.

Make sure Play In Editor starts with the correct player automatically.

## DEBUGGING

Add useful temporary debugging where needed while building.

Examples:

attack hitbox visualization

checkpoint status

enemy patrol points

collision debugging

Remove or disable intrusive debug visuals when the system is confirmed working.

## PERFORMANCE

The prototype should not rely on expensive Tick logic everywhere.

Prefer:

events

timers

components

collision events

state changes

Use Tick only when it makes sense.

## COLLISION

Create clear collision channels or presets when useful.

Make sure:

player does not fall through platforms

attacks do not incorrectly collide with the environment

collectibles overlap instead of blocking

enemy damage works consistently

checkpoints overlap

hazards detect the player

moving platforms interact correctly

## MCP WORKFLOW

Work iteratively through the Unreal MCP.

For every major system:

1. Inspect relevant existing assets.
2. Create or modify the necessary assets.
3. Compile.
4. Check for errors.
5. Save.
6. Test or inspect the result.
7. Fix problems before moving on.

Do not build twenty dependent Blueprints without compiling them.

When creating references between assets, verify the referenced asset exists.

## TESTING

Before declaring the task complete, verify at minimum:

The player spawns.

The player can move.

The player can jump.

Coyote time works.

Jump buffering works.

The camera follows.

Platforms have working collision.

Collectibles work.

HUD updates.

Player can take damage.

Player can die.

Player respawns.

Checkpoints change the respawn point.

Enemy patrol works.

Enemy can damage the player.

Enemy can be defeated.

Moving platform works.

Pause menu works.

Goal works.

Level Complete screen works.

The level can be played from beginning to end.

There should be no major Blueprint compile errors.

## IMPORTANT

Do not stop after creating an architecture document.

Do not give me a tutorial telling me how to make the game.

Do not ask me to manually create Blueprints that the MCP can create.

You are the developer operating Unreal Engine through MCP.

Actually build the game.

Make sensible decisions independently when small details are unspecified.

Prioritize:

1. working gameplay
2. clean architecture
3. responsive movement
4. reliable collision
5. polished game feel
6. visuals

Start by inspecting the Unreal Engine project and determining what currently exists.

Then begin implementation.