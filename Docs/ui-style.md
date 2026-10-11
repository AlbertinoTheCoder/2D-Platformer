# Scintilla interface

The HUD uses navy instrument panels with thin cyan outlines, amber energy,
three integrity segments, and an energy meter. Typography combines Roboto
Black Italic for titles, Roboto Bold Condensed for buttons, and Droid Sans
Mono for small instrument readouts. These fonts are bundled with Unreal.

Pause and completion screens dim the world behind a centered panel.
After the city restoration, completion first shows a large S/A/B/C/D grade,
the score out of 100, elapsed time, damage taken, and energy collected.
**CONTINUE** opens the unlocked district selector. See
[mission rating](mission-rating.md) for the scoring rules.
Press **U** to pause or resume. The pause menu includes **CHOOSE LEVEL**,
which opens the eight district cards while the world stays paused. Only
unlocked districts can be selected. **BACK TO PAUSE** returns to the
pause controls, and **RESUME** continues the current run. Choosing a map
starts that district with fresh health and level state, preserving unlocks.
District buttons use blue for Workshop 07, orange for Foundry, green for
Pipeworks, and purple for Central Tower. Disabled districts keep their lock text and
muted appearance. Campaign unlocks and saved progress are unchanged.

Validation: Development Editor build succeeded; the existing runtime
integration probe passed all 35 checks. Gameplay, pause, and completion
layouts were also inspected in PIE. Screenshots and the runtime report are
in `Assets/UI`.

To repeat the runtime probe, run `python Scripts/playtest_ui.py`. It uses
an automation save slot and does not change the player's campaign save.
