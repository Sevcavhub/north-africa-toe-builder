# Quick Start: Gun Name Conversion

## TL;DR - Using the Conversion Table

### Option 1: Python Helper Function (Recommended)
```python
from database.gun_name_conversion_example import get_weapon_display_name

# Single weapon
display_name = get_weapon_display_name('75mmL46 (PaK40)', conn)
# Returns: '(PaK40)'

# Batch (more efficient)
from database.gun_name_conversion_example import get_weapon_display_names_batch
weapons = ['75mmL46 (PaK40)', 'Panzerfaust', '17 pdr']
conversions = get_weapon_display_names_batch(weapons, conn)
# Returns: {'75mmL46 (PaK40)': '(PaK40)', 'Panzerfaust': 'Pzerfst', '17 pdr': '17 pdr'}
```

### Option 2: SQL View (Simplest for queries)
```sql
-- Get vehicle weapons with abbreviated names
SELECT
    v.vehicle_name,
    vw.display_name AS main_gun,  -- Automatically abbreviated
    vw.he_effect,
    vw.ap_strength_0
FROM bg_builder_vehicles v
LEFT JOIN vw_weapon_display vw ON v.main_gun = vw.full_name
WHERE v.vehicle_id = 1;
```

### Option 3: Direct SQL Query
```sql
SELECT c.datacard_name
FROM bg_gun_name_conversion c
WHERE c.weapon_name = '75mmL46 (PaK40)';
-- Returns: (PaK40)
```

## Quick Examples

| Input | Output | Chars Saved |
|-------|--------|-------------|
| `75mmL46 (PaK40)` | `(PaK40)` | 9 |
| `150mmL12 (sIG33)` | `(sIG33)` | 9 |
| `Boys AT-rifle` | `Boyes ATR` | 4 |
| `Panzerfaust` | `Pzerfst` | 4 |
| `105mm LG40 recoilless gun` | `100mmLG40R` | 15 |

## Integration Steps (5 minutes)

1. **Import helper** (`generate_book_datacards.py` line ~10):
   ```python
   from database.gun_name_conversion_example import get_weapon_display_name
   ```

2. **Convert main gun** (after line 426):
   ```python
   main_gun_display = get_weapon_display_name(main_gun, self.conn) if main_gun else '-'
   ```

3. **Use in weapon table** (lines 799, 810):
   ```python
   <td>{main_gun_display}</td>
   ```

4. **Done!** Regenerate datacards to see abbreviated names.

## Files You Need

- **Helper functions**: `database/gun_name_conversion_example.py`
- **SQL view**: `database/create_weapon_display_view.sql` (already created)
- **Full docs**: `database/bg_gun_name_conversion_usage.md`

## Verification

```bash
# Test the conversion
python database/gun_name_conversion_example.py

# Should show:
#   75mmL46 (PaK40)      -> (PaK40)
#   Panzerfaust          -> Pzerfst
#   etc.
```

## Coverage

✅ **230/230 weapons mapped** (100% coverage)
✅ **Zero unmapped weapons**
✅ **All conversions tested**

---

**Need more details?** See `BG_GUN_NAME_CONVERSION_SUMMARY.md`
