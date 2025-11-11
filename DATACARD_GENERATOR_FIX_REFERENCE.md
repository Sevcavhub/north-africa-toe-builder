# Datacard Generator Fix - Quick Reference

**Date**: November 10, 2025
**Status**: ✅ Fixed and Verified

---

## What Was Fixed

The datacard generator now correctly prioritizes `bg_reference_vehicles` data over `equipment_battlegroup` data.

### Data Priority Order (After Fix)

For equipment with `reference_vehicle_id` (96 items, 20.5%):

1. **Display Name** → `bg_reference_vehicles.name` ✅ TRUSTED
2. **Armor Values** → `bg_reference_vehicles.armor_front/side/rear` ✅ TRUSTED
3. **Movement** → `bg_reference_vehicles.off_road_inches/road_inches` ✅ TRUSTED
4. **Weapons** → `bg_reference_vehicles.weapon_1-4, mount_1-4, ammo_1-4` ✅ TRUSTED

For equipment without `reference_vehicle_id` (373 items, 79.5%):

1. Falls back to `equipment_battlegroup` ⚠️ SUSPECT (needs formula rebuild)

---

## Key Files

| File | Purpose |
|------|---------|
| `scripts/battlegroup/book/generate_book_datacards.py` | **MODIFIED** - Generator script |
| `test_bg_datacard_fix.py` | Test script to verify fix |
| `TEST_BG_REFERENCE_DATACARDS.html` | Sample output (5 datacards) |
| `BG_DATACARD_FIX_VERIFICATION.md` | Detailed verification report |
| `DATACARD_FIX_SUMMARY.md` | Executive summary |
| `BEFORE_AFTER_COMPARISON.html` | Visual comparison |

---

## Code Changes

### Location
`scripts/battlegroup/book/generate_book_datacards.py`
Lines 347-370

### Before
```python
# Always use equipment_battlegroup
armor_front = row['armor_front']           # ❌ Suspect
off_road = row['off_road_movement']        # ❌ Suspect
display_name = equipment['name']           # ❌ Generic
```

### After
```python
# Get defaults from equipment_battlegroup
armor_front_val = row['armor_front']
off_road_val = row['off_road_movement']
display_name = equipment['name']

# OVERRIDE with bg_reference_vehicles if available
if row['reference_vehicle_id']:
    bg_data = query_bg_reference_vehicles(...)
    if bg_data:
        armor_front_val = bg_data['armor_front']      # ✅ Trusted
        off_road_val = bg_data['off_road_inches']     # ✅ Trusted
        display_name = bg_data['name']                # ✅ Trusted
```

---

## Verification Commands

### Generate Test Datacards
```bash
cd D:\north-africa-toe-builder
python test_bg_datacard_fix.py
```

**Output**: `TEST_BG_REFERENCE_DATACARDS.html` (5 sample datacards)

### Regenerate Battle Books
```bash
# Single battle
python scripts/battlegroup/book/generate_book_datacards.py --battle battleaxe

# All battles
python scripts/battlegroup/book/generate_book_datacards.py --all
```

**Output**: Updated datacards in `books/[battle]/book/src/chapter2/*.md`

---

## Expected Results

### Before Fix (Suspect Data)
```
A13 Mk II (cruiser Mk IV)
Armor: [calculated]   ← From bad OCR
Movement: [calculated] ← From bad OCR
```

### After Fix (Trusted Data)
```
A13
Armor: M/N/O          ← Manual extraction from Canada's Crucible ✅
Movement: 9"/15"      ← Manual extraction from Canada's Crucible ✅
```

---

## Coverage Statistics

As of November 10, 2025:

| Metric | Count | Percentage |
|--------|-------|------------|
| Equipment with reference_vehicle_id | 80 | 17.0% |
| Equipment with reference_gun_id | 16 | 3.4% |
| **Total Linked (Trusted Data)** | **96** | **20.5%** |
| Unlinked (Suspect Data) | 373 | 79.5% |
| **Total Equipment** | **469** | **100%** |

---

## Test Cases

All 5 test cases verified:

1. ✅ **A10** - Armor M/N/O, Movement 5"/8"
2. ✅ **A13** - Armor M/N/O, Movement 9"/15"
3. ✅ **Humber II** - Armor N/O/O, Movement 8"/24"
4. ✅ **Matilda II** - Armor J/K/L, Movement 5"/8"
5. ✅ **Morris CS9** - Armor O/O/O, Movement 8"/12"

---

## Database Schema

### bg_reference_vehicles (Trusted Source)
```sql
CREATE TABLE bg_reference_vehicles (
    id INTEGER PRIMARY KEY,
    name TEXT,                    -- Official BG name
    armor_front TEXT,             -- Letter scale (A-O, SS)
    armor_side TEXT,
    armor_rear TEXT,
    off_road_inches INTEGER,      -- Movement in inches
    road_inches INTEGER,
    weapon_1 TEXT,
    weapon_2 TEXT,
    weapon_3 TEXT,
    weapon_4 TEXT,
    mount_1 TEXT,
    mount_2 TEXT,
    mount_3 TEXT,
    mount_4 TEXT,
    ammo_1 INTEGER,
    ammo_2 INTEGER,
    ammo_3 INTEGER,
    ammo_4 INTEGER,
    ...
);
```

### equipment_battlegroup (Suspect Source)
```sql
CREATE TABLE equipment_battlegroup (
    equipment_id TEXT PRIMARY KEY,
    armor_front TEXT,             -- Calculated (suspect)
    armor_side TEXT,              -- Calculated (suspect)
    armor_rear TEXT,              -- Calculated (suspect)
    off_road_movement INTEGER,    -- Calculated (suspect)
    road_movement INTEGER,        -- Calculated (suspect)
    reference_vehicle_id INTEGER, -- Link to bg_reference_vehicles
    reference_gun_id INTEGER,     -- Link to bg_reference_guns
    ...
);
```

---

## Next Steps

1. **Manual Extraction** (Ongoing)
   - Current: 205 vehicles
   - Target: 300-350 vehicles
   - Remaining: 100-150 vehicles

2. **Formula Validation** (When 300+ vehicles available)
   - Reverse-engineer conversions using clean data
   - Target: 90%+ accuracy vs official BG supplements

3. **Rebuild equipment_battlegroup** (After validation)
   - Clear suspect data
   - Repopulate with validated formulas

4. **Track Progress**
   - Current: 20.5% trusted data
   - Target: 100% trusted data

---

## Troubleshooting

### Issue: Datacard shows "None" for armor
**Cause**: `reference_vehicle_id` is NULL, falling back to suspect data
**Solution**: Continue manual extraction, run comprehensive_linkage.py to auto-link

### Issue: Display name shows WITW ID instead of BG name
**Cause**: `reference_vehicle_id` is NULL or `bg_reference_vehicles.name` is NULL
**Solution**: Check bg_reference_vehicles table, ensure name field populated

### Issue: Movement shows wrong format
**Cause**: Generator using `off_road_movement` instead of `off_road_inches`
**Solution**: Verify fix applied correctly (lines 347-370 in generator script)

---

## Quick Verification

To verify the fix is working:

1. Open `TEST_BG_REFERENCE_DATACARDS.html` in browser
2. Check equipment names show BG reference names (A10, A13, not full WITW names)
3. Check armor shows letter grades (M, N, O, not numeric values)
4. Check movement shows inches format (9", 15" not decimal values)

If all three pass → Fix is working correctly ✅

---

## Contact / Questions

For questions about this fix, refer to:
- `BG_DATACARD_FIX_VERIFICATION.md` - Detailed technical report
- `DATACARD_FIX_SUMMARY.md` - Executive summary
- `BEFORE_AFTER_COMPARISON.html` - Visual before/after comparison
