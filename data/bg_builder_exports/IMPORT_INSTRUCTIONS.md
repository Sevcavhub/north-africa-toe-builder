
# BattleGroup Builder Import Instructions

## How to Import These Forces to BattlegroupBuilder.io

1. Open https://osjones.github.io/BattlegroupBuilder/

2. Click the "Import" or "Load List" button (typically in top menu)

3. Select one of the force JSON files:
   - `bg_builder_german_*.json` - German forces
   - `bg_builder_british_*.json` - British forces
   - `bg_builder_italian_*.json` - Italian forces

4. The force will load with:
   - All units pre-selected
   - Correct points costs
   - Battle Rating calculated
   - Troop quality options (Veteran/Regular/Elite)

5. Customize the force:
   - Add/remove units
   - Adjust troop quality
   - Add special rules or upgrades
   - View army list printout

6. Export back:
   - Use "Export" button to save customized list
   - Import back to North Africa TO&E Builder with bg_builder_import.py

## File Format

Each force file contains:
```json
{
  "name": "Force Name",
  "forceName": "BattleGroup Type",
  "battleRating": 42,
  "totalPoints": 190,
  "units": [...]
}
```

## Scenario Files

Complete scenario exports include both forces:
- `bg_builder_complete_scenario_*.json` - Full scenario with attacker/defender

These include:
- Both forces (attacker and defender)
- Terrain setup
- Victory conditions
- Special rules
- Turn limit and table size

## Re-importing to Phase 9B

To re-import customized forces:

1. Export from BG Builder (same JSON format)
2. Place in `data/bg_builder_imports/`
3. Run: `python scripts/phase9b/bg_builder_import.py`
4. Generate scenario: `python scripts/phase9b/scenario_auto_generator.py`

This creates a bidirectional workflow between Phase 9B and BattlegroupBuilder.io!
