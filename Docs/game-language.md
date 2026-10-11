# Game language

All player-facing text is English. **SCINTILLA** remains the game and protagonist name.

The first four districts are Workshop 07, Foundry, Pipeworks, and Central Tower. Cryo Labs, Scrap Yards, Solar Works, and Bio Gardens retain their names. The HUD, controls, objectives, checkpoint messages, pause controls, locked level messages, death/reboot message, restoration captions, and mission rating popup use English.

Placed tutorial signs are translated in the saved campaign maps. Original maps are preserved as `_BeforeEnglish` copies. `Assets/UI/english_signs_report.json` records every inspected sign across all eight districts. Builders and campaign display titles use English so regenerating assets does not restore Italian instructions.

Asset paths and save identifiers retain their existing names to preserve campaign progress and references. The language of the Unreal and Blender applications follows their own preferences.

`Config/english-text.json` contains the display text mapping. Its Italian keys and the before/after values in historical migration reports are retained as source evidence, rather than translated again. `Scripts/translate_game_sources.py` applies it to the native UI and original sign builder; `Scripts/translate_level_signs.py` updates placed signs in the editor.

Validation: the Development Editor build succeeded and all 35 existing gameplay/HUD integration checks passed. The English rating popup, Continue flow, district selector, pause menu, and gameplay HUD were inspected in PIE. Captures are in `Assets/UI`: `rating_popup.png`, `rating_continue_chooser.png`, `english_pause.png`, and `english_gameplay.png`. Unreal was reopened after compilation and left running with the game resumed.

## Repository language

Documentation, source comments, script messages, and player-facing text use English. Keep **SCINTILLA** as the game and protagonist name. Do not translate Unreal package paths, reflected function names, Blender collection names, or save identifiers: these are stable technical references. The original brief was already English. Local recovery copies and generated build/save data are excluded from version control.
