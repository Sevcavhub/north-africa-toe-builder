# BattleGroup Gun Name Conversion Table

## Purpose
Maps full weapon names from `bg_builder_weapons` to abbreviated datacard display names for space-constrained equipment cards.

## Database Schema

**Table**: `bg_gun_name_conversion`

| Column | Type | Description |
|--------|------|-------------|
| `conversion_id` | INTEGER PRIMARY KEY | Auto-incrementing unique identifier |
| `weapon_name` | TEXT NOT NULL UNIQUE | Full weapon name (matches `bg_builder_weapons.weapon_name`) |
| `datacard_name` | TEXT NOT NULL | Abbreviated name for datacard display |
| `created_date` | TEXT | Timestamp of record creation |
| `notes` | TEXT | Optional documentation/rationale |

**Foreign Key**: `weapon_name` → `bg_builder_weapons.weapon_name`

**Index**: `idx_bg_gun_conversion_weapon` on `weapon_name` (fast lookup)

## Coverage
- **230 weapon mappings** (100% of bg_builder_weapons)
- **0 unmapped weapons**

## Usage in Datacard Generator

### Simple JOIN Query
```sql
-- Get weapon stats with abbreviated names
SELECT
    v.vehicle_name,
    w.weapon_name AS full_weapon_name,
    c.datacard_name AS display_name,
    w.he_effect,
    w.ap_effect,
    w.ap_strength_0,
    w.ap_strength_10
FROM bg_builder_vehicles v
LEFT JOIN bg_builder_weapons w ON v.main_gun = w.weapon_name
LEFT JOIN bg_gun_name_conversion c ON w.weapon_name = c.weapon_name
WHERE v.vehicle_id = ?;
```

### Python Example
```python
import sqlite3

def get_weapon_display_name(weapon_name):
    """Convert full weapon name to abbreviated datacard name."""
    conn = sqlite3.connect('database/master_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT datacard_name
        FROM bg_gun_name_conversion
        WHERE weapon_name = ?
    ''', (weapon_name,))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else weapon_name  # Fallback to full name

# Usage in datacard generation
full_name = "75mmL46 (PaK40)"
display_name = get_weapon_display_name(full_name)  # Returns: "(PaK40)"
```

### Batch Conversion
```python
def convert_vehicle_weapons(vehicle_data):
    """Convert all weapon names in a vehicle record."""
    conn = sqlite3.connect('database/master_database.db')
    cursor = conn.cursor()

    # Get all conversions in one query
    weapon_fields = ['main_gun', 'coaxial_mg', 'hull_mg', 'aa_mg']
    weapon_names = [vehicle_data.get(field) for field in weapon_fields if vehicle_data.get(field)]

    if not weapon_names:
        return vehicle_data

    placeholders = ','.join('?' * len(weapon_names))
    cursor.execute(f'''
        SELECT weapon_name, datacard_name
        FROM bg_gun_name_conversion
        WHERE weapon_name IN ({placeholders})
    ''', weapon_names)

    conversion_map = dict(cursor.fetchall())
    conn.close()

    # Apply conversions
    for field in weapon_fields:
        if vehicle_data.get(field) in conversion_map:
            vehicle_data[f'{field}_display'] = conversion_map[vehicle_data[field]]

    return vehicle_data
```

## Examples

### Common Tank Guns
| Full Name | Datacard Name | Usage |
|-----------|---------------|-------|
| `75mmL46 (PaK40)` | `(PaK40)` | German tank destroyer main gun |
| `75mmL24` | `75mmL24` | Early Panzer IV short gun |
| `76mmL55` | `76mmL55` | Sherman 76mm gun |
| `17 pdr` | `17 pdr` | British 17-pounder anti-tank gun |
| `88mmL56 (FlaK36)` | `(FlaK36)` | German 88mm dual-purpose gun |

### Infantry Weapons
| Full Name | Datacard Name | Usage |
|-----------|---------------|-------|
| `Panzerfaust` | `Pzerfst` | German one-shot AT weapon |
| `Panzerschreck` | `Pzershreck` | German reloadable rocket launcher |
| `Bazooka` | `Bazooka` | American rocket launcher |
| `PIAT` | `PIAT` | British anti-tank projector |
| `Boys AT-rifle` | `Boyes ATR` | British anti-tank rifle |

### Artillery & Mortars
| Full Name | Datacard Name | Usage |
|-----------|---------------|-------|
| `25 pdr` | `25 pdr` | British field gun |
| `150mmL12 (sIG33)` | `(sIG33)` | German heavy infantry gun |
| `105mm Howitzer 10-Veld` | `10How Veld` | South African howitzer |
| `81mm mortar` | `81mm mort` | Standard infantry mortar |
| `150mm Nebelwerfer` | `150mm Neblwfr` | German rocket artillery |

## Maintenance

### Adding New Conversions
```sql
INSERT INTO bg_gun_name_conversion (weapon_name, datacard_name, notes)
VALUES ('New Weapon Name', 'Abbrev', 'Optional note explaining abbreviation');
```

### Finding Unmapped Weapons
```sql
SELECT w.weapon_name
FROM bg_builder_weapons w
LEFT JOIN bg_gun_name_conversion c ON w.weapon_name = c.weapon_name
WHERE c.weapon_name IS NULL
ORDER BY w.weapon_name;
```

### Updating Existing Conversion
```sql
UPDATE bg_gun_name_conversion
SET datacard_name = 'NewAbbrev',
    notes = 'Reason for change'
WHERE weapon_name = 'Weapon To Update';
```

## Design Rationale

### Abbreviation Rules
1. **Caliber preservation**: Always show caliber (75mm, 88mm, etc.)
2. **Barrel length simplification**: L46 → L46, no extra text
3. **Common names in parentheses**: Show designation in parens if well-known
   - Example: `75mmL46 (PaK40)` → `(PaK40)` (designation alone is sufficient)
4. **Remove "gun" suffix**: Space-saving in most cases
5. **Howitzers**: Abbreviate to "How"
6. **Mortars**: Abbreviate to "mort" or "mortar" depending on space
7. **Rockets**: Abbreviate to "Rkt"
8. **Machine guns**: Keep as "MG", "LMG", or specific (Besa, Bofors)
9. **AT weapons**: Keep recognizable (PIAT, Bazooka) or abbreviate (ATR for AT-rifle)

### Space Constraints
Datacard weapon tables have limited column width (~15-20 characters max):
- Must be readable at print resolution
- Balance between brevity and recognition
- Preserve essential tactical information (caliber, designation)

## Integration Notes

### For `generate_book_datacards.py`
The script should:
1. Query `bg_builder_vehicles` joined with `bg_builder_weapons`
2. Apply `bg_gun_name_conversion` to all weapon fields
3. Use `datacard_name` in generated markdown weapon tables
4. Fallback to full `weapon_name` if no conversion exists (defensive coding)

### For Weapon Performance Tables
When generating multi-row armament tables (V5 datacard format):
```markdown
| Weapon | HE | Range | AP | +10" | +20" | +30" | +40" | +50" |
|--------|-------|-------|-------|------|------|------|------|------|
| (PaK40) | 3D6 | 60" | 10 | 9 | 8 | 6 | 4 | 2 |
| 2 x MGs | - | 30" | - | - | - | - | - | - |
```

Note the abbreviated weapon names in the "Weapon" column.

## See Also
- `bg_builder_weapons` table - Full weapon statistics
- `bg_builder_vehicles` table - Vehicle equipment assignments
- `docs/DATACARD_FORMAT_STANDARD.md` - V5 datacard specification
- `scripts/battlegroup/book/generate_book_datacards.py` - Datacard generator

---

**Created**: 2025-11-10
**Status**: COMPLETE (230/230 weapons mapped)
**Last Updated**: 2025-11-10
