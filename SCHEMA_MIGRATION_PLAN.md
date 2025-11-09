# bg_reference_vehicles Schema Migration Plan

**Date**: November 7, 2025
**Goal**: Migrate bg_reference_vehicles to match Excel template schema

---

## New Schema (28 columns total)

### From Excel Template (23 columns):
1. name
2. off_road_inches
3. road_inches
4. special_movement
5. armor_front
6. armor_side
7. armor_rear
8. **weapon_1** (NEW - split from weapons)
9. **weapon_2** (NEW - split from weapons)
10. **weapon_3** (NEW - split from weapons)
11. **mount_1** (NEW)
12. **mount_2** (NEW)
13. **mount_3** (NEW)
14. **ammo** (NEW)
15. armor_modifier (exists in current schema)
16. armor_side_schurzen (exists in current schema)
17. **ss_hits** (NEW - soft-skinned vehicles)
18. **ss_transport_capacity** (NEW - soft-skinned vehicles)
19. **ss_special** (NEW - soft-skinned vehicles)
20. year_range
21. vehicle_type
22. nation
23. **dc_meta** (NEW - datacard metadata/notes)

### Additional fields to keep (5 columns):
24. source_file
25. source_document
26. source_battle
27. extraction_method
28. screenshot_file

---

## Current Schema (26 columns)

**Keep (migrate to new schema)**:
- ✅ name, nation, year_range, vehicle_type
- ✅ off_road_inches, road_inches, special_movement
- ✅ armor_front, armor_side, armor_rear
- ✅ armor_modifier, armor_side_schurzen
- ✅ source_file, source_document, source_battle, extraction_method, screenshot_file

**Transform (needs parsing)**:
- ⚠️ weapons → weapon_1, weapon_2, weapon_3 (split comma-separated)
- ⚠️ special_rules → ss_special? (or dc_meta?)

**Delete (not in new schema)**:
- ❌ id (question: keep for foreign keys?)
- ❌ source_page
- ❌ extraction_confidence
- ❌ notes
- ❌ source_date
- ❌ extraction_notes
- ❌ master_id

**Missing in current schema (need data source)**:
- ❓ mount_1, mount_2, mount_3 (exists in bg_reference_vehicles_txt_final)
- ❓ ammo (exists in bg_reference_vehicles_txt_final)
- ❓ ss_hits (new for soft-skinned vehicles)
- ❓ ss_transport_capacity (new for soft-skinned vehicles)
- ❓ dc_meta (new field)

---

## Questions for User

### 1. **Weapon Splitting Logic**
Current: `weapons = "2 pdr, MG, MG"`
Target: `weapon_1 = "2 pdr"`, `weapon_2 = "MG"`, `weapon_3 = "MG"`

**Question**: Split on comma? What if vehicle has >3 weapons?

### 2. **Mount Data Source**
Mount fields (mount_1, mount_2, mount_3) don't exist in current bg_reference_vehicles, but DO exist in bg_reference_vehicles_txt_final.

**Question**: Should I migrate mount data from txt_final table for vehicles that exist in both?

### 3. **Ammo Data Source**
Same issue as mount - ammo field exists in txt_final but not bg_reference_vehicles.

**Question**: Migrate from txt_final? Or leave NULL for now?

### 4. **special_rules → ss_special or dc_meta?**
Current schema has `special_rules` field. New schema has:
- `ss_special` (soft-skinned vehicle special rules)
- `dc_meta` (datacard metadata)

**Question**: Where should special_rules data go? Or split based on vehicle type?

### 5. **ID Column**
Current schema has `id` (primary key).

**Question**: Keep for foreign key relationships? Or delete?

### 6. **New Fields Default Values**
For new fields: ss_hits, ss_transport_capacity, ss_special, dc_meta

**Question**: Set all to NULL initially? Or populate ss_* fields based on vehicle_type?

### 7. **Data Type Changes**
Excel shows:
- off_road_inches, road_inches as TEXT (e.g., "9\"")
- Current DB has them as INTEGER

**Question**: Keep as TEXT to match Excel format? Or parse to INTEGER?

---

## Migration Steps (Proposed)

### Step 1: Backup ✅
```sql
CREATE TABLE bg_reference_vehicles_backup_20251107 AS SELECT * FROM bg_reference_vehicles;
```

### Step 2: Create New Schema
```sql
CREATE TABLE bg_reference_vehicles_new (
    id INTEGER PRIMARY KEY,  -- Keep or remove?
    name TEXT,
    off_road_inches TEXT,  -- TEXT or INTEGER?
    road_inches TEXT,      -- TEXT or INTEGER?
    special_movement TEXT,
    armor_front TEXT,
    armor_side TEXT,
    armor_rear TEXT,
    weapon_1 TEXT,
    weapon_2 TEXT,
    weapon_3 TEXT,
    mount_1 TEXT,
    mount_2 TEXT,
    mount_3 TEXT,
    ammo TEXT,
    armor_modifier TEXT,
    armor_side_schurzen TEXT,
    ss_hits INTEGER,
    ss_transport_capacity INTEGER,
    ss_special TEXT,
    year_range TEXT,
    vehicle_type TEXT,
    nation TEXT,
    dc_meta TEXT,
    source_file TEXT,
    source_document TEXT,
    source_battle TEXT,
    extraction_method TEXT,
    screenshot_file TEXT
);
```

### Step 3: Migrate Data
- Split weapons field into weapon_1, weapon_2, weapon_3
- Migrate mount/ammo from txt_final if available
- Map special_rules to appropriate field

### Step 4: Rename Table
```sql
DROP TABLE bg_reference_vehicles;
ALTER TABLE bg_reference_vehicles_new RENAME TO bg_reference_vehicles;
```

### Step 5: Update V5 Datacard Script
- Update field references from weapons → weapon_1, weapon_2, weapon_3
- Add support for new fields

---

## Identified Issues

### Issue 1: **Mount/Ammo Data Availability**
Mount and ammo fields only exist in txt_final table, not in main bg_reference_vehicles table.

**Impact**: Only 39 vehicles (from txt_final) have this data. 500 vehicles in bg_reference_vehicles will have NULL.

### Issue 2: **Weapon Count Limit**
New schema supports max 3 weapons. Morris CS9 in txt_final has 14 weapons!

**Impact**: Need truncation or error handling.

### Issue 3: **Data Type Inconsistency**
Excel uses "9\"" format (TEXT), DB uses 9 (INTEGER).

**Impact**: Need to decide on canonical format.

---

## Recommendations

1. **Answer questions above** before proceeding
2. **Backup current table** ✅
3. **Test migration on 10 sample vehicles** first
4. **Validate V5 datacard script** with new schema
5. **Consider adding mount/ammo to ALL vehicles** (manual entry project?)

---

**Ready to proceed?** Please answer the 7 questions above and I'll implement the migration.
