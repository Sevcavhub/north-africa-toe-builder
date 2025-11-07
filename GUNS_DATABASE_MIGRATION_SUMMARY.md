# Guns Database Migration Summary

**Date**: November 5, 2025
**Status**: ✅ COMPLETE - Database schema updated, ready for data import
**Issue Addressed**: Missing HE range columns + gun name alias support

---

## 🚨 Problem Discovered

While preparing to import British gun data, two critical issues were found:

### Issue 1: Missing HE Range Columns

**Problem**: `bg_reference_guns` table had AP range data but NO HE range data
- ✅ Had: 6 AP range columns (`ap_0_10` through `ap_50_70`)
- ❌ Missing: 6 HE range columns (`he_0_10` through `he_50_70`)
- ⚠️ Only had: `he_dice` and `he_target` (no range bands)

**Impact**: Cannot properly model HE effectiveness at different ranges

### Issue 2: Gun Name Aliases

**Problem**: Vehicles reference guns by short names (e.g., "2 pdr") but database only has official names (e.g., "Ordnance QF 2-pounder")

**Examples**:
| Official Name | Vehicle Weapon Alias |
|---------------|---------------------|
| Ordnance QF 2-pounder | 2 pdr |
| 75mm Gun M3 | 75mmL40 |
| 3-inch Howitzer | 3in How |
| 280mm Petard Mortar | Petard |

**Impact**: Cannot match vehicle weapons to gun database entries

---

## ✅ Solution Implemented

### Part 1: Database Schema Migration

**File**: `scripts/battlegroup/manual_extraction/migrate_guns_add_he_ranges_and_variants.sql`

**Changes Made**:
1. ✅ Added 6 HE range columns to `bg_reference_guns`:
   - `he_0_10`, `he_10_20`, `he_20_30`, `he_30_40`, `he_40_50`, `he_50_70`

2. ✅ Added `common_name` column to `bg_reference_guns`:
   - Stores primary alias (e.g., "2 pdr")

3. ✅ Created `gun_name_variants` table:
   ```sql
   CREATE TABLE gun_name_variants (
       variant_id INTEGER PRIMARY KEY AUTOINCREMENT,
       gun_id INTEGER NOT NULL,
       variant_name TEXT NOT NULL UNIQUE,
       variant_source TEXT,  -- 'vehicle_weapon', 'datacard', 'official'
       is_official BOOLEAN DEFAULT 0,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (gun_id) REFERENCES bg_reference_guns(id)
   );
   ```

4. ✅ Populated initial variants:
   - 26 existing guns → 26 official name variants

**Verification**:
```bash
HE columns: ['he_dice', 'he_target', 'he_0_10', 'he_10_20', 'he_20_30',
             'he_30_40', 'he_40_50', 'he_50_70']
Gun name variants: 26 entries
```

---

### Part 2: Updated CSV Template

**Old CSV** (`british_datacards_ALL_GUNS.csv`):
- 11 columns (missing HE ranges and alias)

**New CSV** (`british_datacards_ALL_GUNS_UPDATED.csv`):
- 18 columns (added HE ranges + common_name)

**New Columns**:
| Column | Description | Example |
|--------|-------------|---------|
| `common_name` | Alias used in vehicle weapons | "2 pdr" |
| `he_0_10` | HE effectiveness 0-10" | 4 |
| `he_10_20` | HE effectiveness 10-20" | 4 |
| `he_20_30` | HE effectiveness 20-30" | 4 |
| `he_30_40` | HE effectiveness 30-40" | 3 |
| `he_40_50` | HE effectiveness 40-50" | 2 |
| `he_50_70` | HE effectiveness 50-70" | - |

**Template Structure**:
```csv
name,common_name,nation,caliber_mm,he_dice,he_target,he_0_10,he_10_20,he_20_30,he_30_40,he_40_50,he_50_70,ap_0_10,ap_10_20,ap_20_30,ap_30_40,ap_40_50,ap_50_70
15mm Besa,15mm Besa,british,15,,,,,,,,,,,,,,
2 pdr,2 pdr,british,40,,,,,,,,,,,,,,
...
```

---

### Part 3: Enhanced Import Script

**File**: `scripts/battlegroup/manual_extraction/import_british_datacards_guns.py`

**New Features**:

1. **HE Range Import**:
   - Imports all 6 HE range columns
   - Validates HE data completeness

2. **Gun Name Variants**:
   - Automatically creates variants for each gun:
     - Official name variant (e.g., "Ordnance QF 2-pounder")
     - Common name variant (e.g., "2 pdr")
   - Enables vehicle weapon lookups by alias

3. **Duplicate Detection**:
   - Checks for duplicates by **name OR common_name**
   - Merges nations for multi-nation guns (e.g., Canadian, British)
   - Adds variants for existing guns

4. **Data Validation**:
   - Warns if HE or AP data is missing
   - Prompts user to confirm import of incomplete data

**Usage**:
```bash
# After filling british_datacards_ALL_GUNS_UPDATED.csv with data
python scripts/battlegroup/manual_extraction/import_british_datacards_guns.py
```

---

## 📊 Database Architecture

### Before Migration
```
bg_reference_guns (26 guns)
├── name, nation, caliber_mm
├── he_dice, he_target (NO RANGE DATA)
├── ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70
└── points_cost, battle_rating, source_file, etc.
```

### After Migration
```
bg_reference_guns (26 guns)
├── name, common_name, nation, caliber_mm
├── he_dice, he_target
├── he_0_10, he_10_20, he_20_30, he_30_40, he_40_50, he_50_70 ← NEW
├── ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70
└── points_cost, battle_rating, source_file, etc.

gun_name_variants (26 variants) ← NEW TABLE
├── variant_id, gun_id
├── variant_name (UNIQUE)
├── variant_source ('official', 'vehicle_weapon', 'datacard')
└── is_official, created_at
```

---

## 🔍 How Gun Name Variants Work

### Example: British 2-pounder Gun

**Database Entry** (`bg_reference_guns`):
| id | name | common_name | caliber_mm | nation |
|----|------|-------------|------------|--------|
| 5 | Ordnance QF 2-pounder | 2 pdr | 40 | British, Canadian |

**Variants** (`gun_name_variants`):
| variant_id | gun_id | variant_name | variant_source | is_official |
|------------|--------|--------------|----------------|-------------|
| 10 | 5 | Ordnance QF 2-pounder | official | 1 |
| 11 | 5 | 2 pdr | vehicle_weapon | 0 |
| 12 | 5 | 2-pdr | vehicle_weapon | 0 |
| 13 | 5 | QF 2-pounder | datacard | 1 |

**Vehicle Weapon Lookup**:
```sql
-- Vehicle has weapon "2 pdr" - find gun details
SELECT g.*
FROM bg_reference_guns g
JOIN gun_name_variants v ON g.id = v.gun_id
WHERE v.variant_name = '2 pdr';
-- Returns: Ordnance QF 2-pounder with full stats
```

---

## 📋 Next Steps

### For User: Fill CSV with Data

**File to Complete**: `british_datacards_ALL_GUNS_UPDATED.csv`

**Required Data** (15 guns):
1. **HE Range Values** (he_0_10 through he_50_70)
   - Use BattleGroup DataCards PDF as reference
   - Fill in HE effectiveness at each range band
   - Use "-" for out-of-range bands

2. **AP Penetration Values** (ap_0_10 through ap_50_70)
   - Use BattleGroup DataCards PDF as reference
   - Fill in AP penetration at each range band

3. **Common Names** (already filled with best guesses)
   - Verify aliases match vehicle weapon names
   - Adjust if needed

**Example Row** (with data):
```csv
2 pdr,2 pdr,british,40,6,4+,6,6,6,5,4,-,7,6,5,4,3,2
```

### Run Import Script

Once CSV is complete:
```bash
python scripts/battlegroup/manual_extraction/import_british_datacards_guns.py
```

**Expected Output**:
- Duplicate detection for Canadian/British shared guns
- Gun name variants created automatically
- Validation warnings if data is incomplete
- Summary showing guns inserted and variants added

---

## ✅ Benefits

### 1. Complete HE Range Modeling
- HE effectiveness now varies by range (like AP)
- Matches official BattleGroup rules
- Enables accurate datacard generation

### 2. Flexible Gun Lookups
- Vehicles can reference guns by any known alias
- No need to standardize vehicle weapon names
- Supports multiple naming conventions

### 3. Multi-Nation Support
- Same gun used by multiple nations (e.g., 2 pdr by Canadian, British)
- Nation field updated to "Canadian, British"
- Variants shared across nations

### 4. Consistent Architecture
- Follows Phase 5.5 `equipment_name_variants` pattern
- Proper database normalization
- Scalable for future gun additions

---

## 📁 Files Created/Modified

**Migration**:
- ✅ `scripts/battlegroup/manual_extraction/migrate_guns_add_he_ranges_and_variants.sql`

**CSV Template**:
- ✅ `british_datacards_ALL_GUNS_UPDATED.csv` (with new columns)

**Import Script**:
- ✅ `scripts/battlegroup/manual_extraction/import_british_datacards_guns.py` (updated)

**Documentation**:
- ✅ `GUNS_DATABASE_MIGRATION_SUMMARY.md` (this file)

---

**Migration Complete**: November 5, 2025
**Ready for**: User data entry → Import → British guns in database with full HE/AP range data and aliases
