# Mission rating

On level completion, the city repairs itself and the camera reveals the panorama. After 7.5 seconds, the mission rating appears. **CONTINUE** then opens the selector, where only unlocked districts are available.

The popup shows the grade, score out of 100, elapsed time, damage taken, and collected energy versus the total. The grade is calculated when the generator activates; restoration, the popup, and pauses do not add time. Damage counts integrity points actually lost, including after respawns. Hits ignored during invulnerability do not count.

| Criterion | Points | Calculation |
|---|---|---|
| Speed | 40 | Full points up to the target time; decreases linearly to zero at twice that time |
| Integrity | 30 | Deduct six points for each point of damage taken, down to zero |
| Collection | 30 | Proportional to collected energy versus the level total |

Target times for levels 1-8 are 100, 110, 115, 120, 125, 130, 135, and 140 seconds, adjusted for the extended routes and new traps. They are defined in `ScintillaCampaign.h` and can be tuned after further playtesting.

| Grade | Score |
|---|---|
| S | 90 or higher |
| A | 80-89 |
| B | 65-79 |
| C | 50-64 |
| D | Below 50 |

Thresholds use the actual score; the popup displays its integer part. Ratings do not restrict unlocks: completing a district unlocks only the next one. The pause menu's level selector remains independent of the final rating.

`python Scripts/playtest_rating.py` checks scoring, pauses, damage, respawns, and the selector flow. `python Scripts/capture_rating.py` captures the popup and activates CONTINUE in the live editor, preserving the player's save and restarting a normal game afterwards.
