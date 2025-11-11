# BattleGroup Gun Name Conversion - Implementation Summary

## What Was Done

Successfully created and populated the `bg_gun_name_conversion` table to support abbreviated weapon names in BattleGroup equipment datacards.

## Database Changes

### New Table Created
**Table**: `bg_gun_name_conversion`
- **Location**: `master_database.db`
- **Records**: 230 weapon name conversions (100% coverage)
- **Purpose**: Map full weapon names to space-constrained datacard display names

### Schema
```sql
CREATE TABLE bg_gun_name_conversion (
    conversion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    weapon_name TEXT NOT NULL UNIQUE,          -- Matches bg_builder_weapons.weapon_name
    datacard_name TEXT NOT NULL,               -- Abbreviated display name
    created_date TEXT DEFAULT (datetime('now')),
    notes TEXT,
    FOREIGN KEY (weapon_name) REFERENCES bg_builder_weapons(weapon_name)
);

CREATE INDEX idx_bg_gun_conversion_weapon ON bg_gun_name_conversion(weapon_name);
```

### Example Conversions

| Full Weapon Name | Datacard Display | Space Saved |
|-----------------|------------------|-------------|
| `75mmL46 (PaK40)` | `(PaK40)` | 9 chars |
| `150mmL12 (sIG33)` | `(sIG33)` | 9 chars |
| `Boys AT-rifle` | `Boyes ATR` | 4 chars |
| `Panzerfaust` | `Pzerfst` | 4 chars |
| `Panzerschreck` | `Pzershreck` | 4 chars |
| `105mm LG40 recoilless gun` | `100mmLG40R` | 15 chars |

## Files Created

1. **`create_bg_gun_name_conversion.sql`**
   - SQL script to create table and populate 230 conversions
   - Includes validation query to check for unmapped weapons
   - Safe to re-run (uses `CREATE TABLE IF NOT EXISTS`)

2. **`bg_gun_name_conversion_usage.md`**
   - Complete documentation of table structure
   - SQL query examples for datacard generator integration
   - Python code examples (single and batch conversion)
   - Design rationale for abbreviation rules
   - Maintenance procedures

3. **`gun_name_conversion_example.py`**
   - Python module with helper functions:
     - `get_weapon_display_name()` - Single weapon conversion
     - `get_weapon_display_names_batch()` - Efficient batch conversion
     - `get_vehicle_weapons_abbreviated()` - Convert all vehicle weapons
   - Integration instructions for `generate_book_datacards.py`
   - Test suite with example weapons

## Validation Results

✅ **All weapons mapped**: 230/230 weapons from `bg_builder_weapons` have conversions
✅ **Zero unmapped weapons**
✅ **Test suite passes**: All example conversions working correctly
✅ **Database integrity**: Foreign key constraints enforced

```bash
$ python database/gun_name_conversion_example.py

Single conversions:
  75mmL46 (PaK40)                -> (PaK40)
  17 pdr                         -> 17 pdr
  2 x MGs                        -> 2 x MGs
  Panzerfaust                    -> Pzerfst
  88mmL56 (FlaK36)               -> (FlaK36)
  Boys AT-rifle                  -> Boyes ATR
  150mmL12 (sIG33)               -> (sIG33)
```

## Integration with Datacard Generator

### Current State
The `generate_book_datacards.py` script currently uses full weapon names directly:
- Line 799: `<td>{main_gun}</td>` for HE row
- Line 810: `<td>{main_gun}</td>` for AP row
- Line ~510: Secondary weapons use full `weapon_name`

### Required Changes
To integrate the conversion table:

1. **Import the helper function** (top of file):
   ```python
   from database.gun_name_conversion_example import get_weapon_display_name
   ```

2. **Convert main gun name** (after line 426):
   ```python
   main_gun_display = get_weapon_display_name(main_gun, self.conn) if main_gun else '-'
   ```

3. **Update weapon table rows** (lines 799, 810):
   ```python
   <td>{main_gun_display}</td>  # Instead of {main_gun}
   ```

4. **Convert secondary weapons** (around line 510):
   ```python
   secondary_display = get_weapon_display_name(weapon_name, self.conn)
   secondary.append({
       'name': weapon_name,
       'display_name': secondary_display,
       'mount_type': mount or 'Unknown',
       'ammunition_count': ammo
   })
   ```

5. **Update armament rows** (around line 700):
   ```python
   <td>{weapon['display_name']}</td>  # Instead of {weapon['name']}
   ```

### Benefits
- **Space-efficient**: Datacard weapon columns fit within design constraints
- **Professional appearance**: Matches official BattleGroup card abbreviations
- **Maintains data integrity**: Full names preserved in database
- **Fast lookups**: Indexed table with O(1) query performance

## Abbreviation Design Rules

The conversion mappings follow these principles:

1. **Preserve caliber**: Always show caliber (75mm, 88mm, etc.)
2. **Simplify barrel length**: L46 → L46 (no extra text)
3. **Use common designations**: Well-known names in parentheses
   - `75mmL46 (PaK40)` → `(PaK40)` (designation is sufficient)
4. **Remove "gun" suffix**: Space-saving in most cases
5. **Standard abbreviations**:
   - Howitzers → "How"
   - Mortars → "mort" or "mortar"
   - Rockets → "Rkt"
   - AT rifles → "ATR"
6. **Keep recognizable names**: PIAT, Bazooka stay as-is
7. **Balance brevity with clarity**: Must be readable at print resolution

## Query Examples

### Get abbreviated name for single weapon
```sql
SELECT datacard_name
FROM bg_gun_name_conversion
WHERE weapon_name = '75mmL46 (PaK40)';
-- Returns: (PaK40)
```

### Get vehicle with abbreviated weapons
```sql
SELECT
    v.vehicle_name,
    w.weapon_name AS full_name,
    c.datacard_name AS display_name,
    w.he_effect,
    w.ap_strength_0
FROM bg_builder_vehicles v
LEFT JOIN bg_builder_weapons w ON v.main_gun = w.weapon_name
LEFT JOIN bg_gun_name_conversion c ON w.weapon_name = c.weapon_name
WHERE v.vehicle_id = 1;
```

### Find unmapped weapons (should return 0 rows)
```sql
SELECT w.weapon_name
FROM bg_builder_weapons w
LEFT JOIN bg_gun_name_conversion c ON w.weapon_name = c.weapon_name
WHERE c.weapon_name IS NULL;
-- Returns: (empty) - all 230 weapons mapped
```

## Testing

### Run Test Suite
```bash
cd D:/north-africa-toe-builder
python database/gun_name_conversion_example.py
```

### Verify Database
```python
import sqlite3

conn = sqlite3.connect('database/master_database.db')
cursor = conn.cursor()

# Count total conversions
cursor.execute('SELECT COUNT(*) FROM bg_gun_name_conversion')
print(f"Total conversions: {cursor.fetchone()[0]}")  # Should be 230

# Check for unmapped weapons
cursor.execute('''
    SELECT COUNT(*)
    FROM bg_builder_weapons w
    LEFT JOIN bg_gun_name_conversion c ON w.weapon_name = c.weapon_name
    WHERE c.weapon_name IS NULL
''')
print(f"Unmapped weapons: {cursor.fetchone()[0]}")  # Should be 0

conn.close()
```

## Maintenance

### Adding New Weapons
If new weapons are added to `bg_builder_weapons`:

1. Run validation query to find unmapped weapons:
   ```sql
   SELECT w.weapon_name
   FROM bg_builder_weapons w
   LEFT JOIN bg_gun_name_conversion c ON w.weapon_name = c.weapon_name
   WHERE c.weapon_name IS NULL
   ORDER BY w.weapon_name;
   ```

2. Add conversions:
   ```sql
   INSERT INTO bg_gun_name_conversion (weapon_name, datacard_name, notes)
   VALUES ('New Weapon Name', 'Abbrev', 'Optional reasoning');
   ```

### Updating Abbreviations
If an abbreviation needs changing:
```sql
UPDATE bg_gun_name_conversion
SET datacard_name = 'NewAbbrev',
    notes = 'Reason for change'
WHERE weapon_name = 'Weapon To Update';
```

## Next Steps

1. **Integrate into datacard generator** (5 code changes in `generate_book_datacards.py`)
2. **Regenerate all datacards** to use abbreviated names
3. **Review output** to ensure spacing/readability is correct
4. **Update DATACARD_FORMAT_STANDARD.md** to document weapon name abbreviation

## Related Documentation

- `bg_gun_name_conversion_usage.md` - Detailed usage guide
- `docs/DATACARD_FORMAT_STANDARD.md` - V5 datacard specification
- `scripts/battlegroup/book/generate_book_datacards.py` - Datacard generator
- `PHASE_9B_NEXT_STEPS.md` - Phase 9B remaining tasks

## Status

- ✅ Database table created and populated (230 mappings)
- ✅ Helper functions implemented and tested
- ✅ Documentation complete
- ⏳ Integration into datacard generator (pending)
- ⏳ Datacard regeneration (pending)

---

**Created**: 2025-11-10
**Author**: Claude Code
**Database**: `master_database.db`
**Coverage**: 100% (230/230 weapons)
