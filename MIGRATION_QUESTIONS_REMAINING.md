# Schema Migration - Outstanding Questions

**Date**: November 7, 2025
**Status**: special_rules parsing COMPLETE ✅, ready for final migration

---

## Current Status Summary

### ✅ What We Have (Good News!)

**From Excel Template (23 columns):**
- ✅ **20/23 columns** already exist in current schema!
- ✅ mount_1, mount_2, mount_3 (created during special_rules parsing)
- ✅ ss_hits, ss_transport_capacity, ss_special (parsed from special_rules)
- ✅ dc_meta (parsed from special_rules)
- ✅ armor_modifier, armor_side_schurzen (already existed)
- ✅ name, nation, year_range, vehicle_type (core fields)
- ✅ off_road_inches, road_inches, special_movement (movement)
- ✅ armor_front, armor_side, armor_rear (armor)

**Additional fields to keep:**
- ✅ source_file, source_document, source_battle, extraction_method, screenshot_file

### ❌ What's Missing (Need to Create)

**Missing from Excel template:**
- ❌ weapon_1 (need to split from weapons field)
- ❌ weapon_2 (need to split from weapons field)
- ❌ weapon_3 (need to split from weapons field)
- ❌ ammo (new field, currently doesn't exist)

### 🗑️ What to Delete

**Old fields no longer needed:**
- weapons (will be split to weapon_1/2/3)
- source_page
- extraction_confidence
- notes
- source_date
- extraction_notes
- master_id

---

## Outstanding Questions for User

### 1. **ID Column** ❓
**Question**: Keep or delete the `id` column (primary key)?

**Context**:
- Used for foreign keys and relationships
- Not in Excel template
- Good practice to have primary key

**Recommendation**: **KEEP** (even though not in template, needed for DB integrity)

---

### 2. **Weapon Splitting** ❓
**Question**: How to handle vehicle with 4 weapons?

**Issue Found**:
- **M3 Medium AFV** (ID 5) has **4 weapons**: "75mmL40, 37mmL53, MG, MG"
- Excel template only has weapon_1, weapon_2, weapon_3 (3 columns)

**Options**:
1. Truncate to first 3 weapons (lose "MG")
2. Add weapon_4 field to schema (deviates from template)
3. Combine last two: weapon_3 = "MG, MG"
4. Manual review/decision for this one vehicle

**Your choice?**

---

### 3. **Ammo Field** ❓
**Question**: Ammo field doesn't exist currently. What should we populate it with?

**Context**:
- Excel template has `ammo` column
- Current schema has NO ammo data
- We parsed ammo from special_rules earlier (e.g., "12 ammo"), but those went to dc_meta or were lost

**Options**:
1. Leave NULL for all vehicles (manual entry later)
2. Try to parse from dc_meta/notes if present
3. Look for ammo in weapons field (e.g., Humber IV has "12 ammo" somewhere)

**Your choice?**

---

### 4. **Data Type: Movement Fields** ❓
**Question**: Keep movement as INTEGER or convert to TEXT?

**Current**: `off_road_inches = 9` (INTEGER)
**Excel shows**: `off_road_inches = "9\""` (TEXT with quote marks)

**Options**:
1. Keep as INTEGER (cleaner, sortable, no quotes needed)
2. Convert to TEXT to match Excel exactly (add quotes: "9\"")

**Recommendation**: **Keep as INTEGER** (more practical for database)

**Your choice?**

---

### 5. **Field Deletion Confirmation** ❓
**Question**: Confirm OK to delete these 7 fields?

Fields to delete:
- weapons (migrated to weapon_1/2/3)
- source_page (not in template)
- extraction_confidence (not in template)
- notes (not in template)
- source_date (not in template)
- extraction_notes (not in template)
- master_id (not in template)

**Confirm deletion?** (Yes/No)

---

## Migration Plan Summary

**Once questions answered, the migration will:**

1. ✅ Backup current table
2. ✅ Create new table with Excel template schema + additional fields
3. ✅ Add weapon_1, weapon_2, weapon_3 (split from weapons)
4. ✅ Add ammo field (per your decision)
5. ✅ Copy all existing data
6. ✅ Delete old fields
7. ✅ Rename tables
8. ✅ Update V5 datacard script to use new field names

---

## Estimated Impact

**Records affected**: 144 vehicles (all manual entries)
**Fields changed**:
- Add: weapon_1, weapon_2, weapon_3, ammo (4 new)
- Delete: weapons, source_page, extraction_confidence, notes, source_date, extraction_notes, master_id (7 old)
- Net change: -3 columns (more streamlined!)

**Time estimate**: 5-10 minutes to implement after questions answered

---

**Ready to proceed once you answer the 5 questions above!**
