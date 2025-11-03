# EXECUTE TIER 1 LINKAGE - QUICK START GUIDE

**Status**: Ready for Execution
**Risk**: Zero (perfect matches, full audit trail, rollback available)
**Time Required**: < 1 minute

---

## What Will Happen

When you execute the Tier 1 SQL script, it will:

1. ✅ Create `normalization_audit` table (if not exists) for rollback capability
2. ✅ Link **19 equipment items** to their BG reference vehicles
3. ✅ Set `reference_match_confidence = 100` for all matches
4. ✅ Handle multiple variants using MIN(id) strategy
5. ✅ Generate audit records with rollback SQL
6. ✅ Validate changes before commit

---

## Priority Test Cases - Before & After

### BEFORE Execution
| Equipment | reference_vehicle_id | weapon_description |
|-----------|---------------------|---------------------|
| GBR_MATILDA_II | NULL | None |
| USA_M4_SHERMAN | NULL | None |
| GER_PANZER_III_AUSF_F | NULL | None |
| GBR_25_POUNDER | NULL | None |

### AFTER Tier 1 Execution
| Equipment | reference_vehicle_id | weapon_description | Status |
|-----------|---------------------|---------------------|---------|
| GBR_MATILDA_II | **290** | 2 pdr (armor value, penetration loaded) | ✅ LINKED |
| USA_M4_SHERMAN | **203** | 75mm M3 (armor value, penetration loaded) | ✅ LINKED |
| GER_PANZER_III_AUSF_F | NULL | None | ❌ Needs Tier 2 |
| GBR_25_POUNDER | NULL | None | ❌ Architecture block |

**Result**: 2 of 4 priority test cases solved (50%)

---

## Expected Changes

### Database State Changes

**BEFORE**:
- equipment_battlegroup.reference_vehicle_id: 0/469 populated (0%)
- equipment_battlegroup.reference_match_confidence: 0/469 set

**AFTER**:
- equipment_battlegroup.reference_vehicle_id: **19/469 populated (4.1%)**
- equipment_battlegroup.reference_match_confidence: **19/469 set to 100**

### Items That Will Be Linked

#### American (6 items)
- USA_M10_WOLVERINE → id:228 (M10 Wolverine)
- USA_M3_LEE → id:233 (M3 Lee)
- USA_M4_HIGH_SPEED_TRACTOR → id:495 (M4 High Speed Tractor)
- USA_M4_SHERMAN → id:203 (M4 Sherman) - **Priority Test Case**
- USA_M5_HIGH_SPEED_TRACTOR → id:496 (M5 High Speed Tractor)
- USA_M8_GREYHOUND → id:242 (M8 Greyhound)

#### British (6 items)
- GBR_A10_CRUISER → id:294 (A10 Cruiser)
- GBR_A9_CRUISER → id:292 (A9 Cruiser)
- GBR_CHURCHILL_VII → id:344 (Churchill VII)
- GBR_HUMBER_SCOUT_CAR → id:334 (Humber Scout Car)
- GBR_MATILDA_II → id:290 (Matilda II) - **Priority Test Case**
- GBR_MORRIS_QUAD → id:446 (Morris Quad)

#### German (7 items)
- GER_SDKFZ_222 → id:20 (SdKfz 222)
- GER_SDKFZ_223 → id:378 (SdKfz 223)
- GER_SDKFZ_231 → id:380 (SdKfz 231)
- GER_SDKFZ_250 → id:386 (SdKfz 250)
- GER_SDKFZ_251_1 → id:23 (SdKfz 251/1)
- GER_SDKFZ_251_2 → id:24 (SdKfz 251/2)
- GER_SDKFZ_251_3 → id:25 (SdKfz 251/3)

---

## How to Execute

### Option 1: Using SQLite Command Line

```bash
# Navigate to project root
cd D:\north-africa-toe-builder

# Execute SQL script
sqlite3 database/master_database.db < scripts/linkage/tier1_exact_matches.sql
```

### Option 2: Using Python

```python
import sqlite3

# Connect to database
conn = sqlite3.connect('D:/north-africa-toe-builder/database/master_database.db')
cursor = conn.cursor()

# Read SQL script
with open('D:/north-africa-toe-builder/scripts/linkage/tier1_exact_matches.sql', 'r') as f:
    sql_script = f.read()

# Execute (SQLite executes all statements in script)
cursor.executescript(sql_script)

# Results are printed by the SQL summary report at end
conn.close()
```

### Option 3: Using MCP SQLite Tool (Recommended for Review)

Execute each section of the SQL file step-by-step to review results:

1. Create audit table
2. Preview matches
3. Execute UPDATE with transaction
4. Validate results
5. Review summary report

---

## Validation Checks Built Into Script

The SQL script includes these automatic validations:

1. ✅ **Pre-execution count**: Verify 469 NULL references
2. ✅ **Match preview**: Show all 19 matches before UPDATE
3. ✅ **Audit count**: Verify 19 audit records created
4. ✅ **Update count**: Verify 19 records updated
5. ✅ **Post-execution validation**: Check reference_vehicle_id populated correctly
6. ✅ **Percentage calculation**: Verify 4.1% coverage achieved

**If any validation fails, transaction will ROLLBACK (no changes made)**

---

## What Happens After Linking

Once reference_vehicle_id is populated, the BG datacard generation will:

1. ✅ **Load armor values** from bg_reference_vehicles.armor_* columns
2. ✅ **Load movement values** from bg_reference_vehicles.road_movement, off_road_movement
3. ✅ **Load weapons data** from bg_reference_vehicles.weapons JSON
4. ✅ **Load penetration data** from penetration values in weapons
5. ✅ **Display "Weapon: [actual weapon]"** instead of "Weapon: None"
6. ✅ **Show penetration values** instead of NULL

### Example: GBR_MATILDA_II Datacard

**BEFORE** (reference_vehicle_id = NULL):
```
Matilda II
Armor: Front 7 | Side 7 | Rear 6 | Turret 7/7/6
Movement: 5 | 8
Weapon: None
Penetration: [null values]
```

**AFTER** (reference_vehicle_id = 290):
```
Matilda II
Armor: Front 7 | Side 7 | Rear 6 | Turret 7/7/6
Movement: 5 | 8
Weapon: 2 pdr
Penetration: 0-10": +6 | 10-20": +5 | 20-30": +4 | 30-40": +3 | 40-50": +2 | 50-70": +1
HE: 1D6 | Target: 6
Points: 124 (Regular) | BR: 10
```

---

## Rollback Procedure (If Needed)

If you need to undo the Tier 1 changes:

```sql
BEGIN TRANSACTION;

-- Restore NULL values
UPDATE equipment_battlegroup
SET
    reference_vehicle_id = NULL,
    reference_match_confidence = NULL
WHERE equipment_id IN (
    SELECT equipment_id
    FROM normalization_audit
    WHERE match_tier = 'Tier 1' AND operation = 'UPDATE_TIER1'
);

-- Remove audit records
DELETE FROM normalization_audit
WHERE match_tier = 'Tier 1' AND operation = 'UPDATE_TIER1';

COMMIT;
```

**Rollback time**: < 10 seconds

---

## Next Steps After Execution

### Immediate (This Session)
1. ✅ Execute Tier 1 SQL script
2. ✅ Verify 19 items linked
3. ✅ Test BG datacard generation for priority cases (Matilda II, M4 Sherman)
4. ⏳ Review unlinked items for Tier 2 candidates

### Follow-Up (Next Session)
1. ⏳ Develop Tier 2 Python normalization script
2. ⏳ Preview Tier 2 matches (estimated +40-60 items)
3. ⏳ Execute approved Tier 2 matches
4. ⏳ Address architecture issue (add reference_gun_id for artillery)

---

## Success Criteria

**Tier 1 execution is successful if**:
- ✅ 19 records updated in equipment_battlegroup
- ✅ 19 audit records created in normalization_audit
- ✅ reference_match_confidence = 100 for all 19
- ✅ GBR_MATILDA_II linked to id:290
- ✅ USA_M4_SHERMAN linked to id:203
- ✅ No errors during transaction
- ✅ Summary report shows 4.1% coverage

**Execute when ready** - all safety protocols in place.

---

## Quick Reference

| Item | Value |
|------|-------|
| SQL Script Path | D:\north-africa-toe-builder\scripts\linkage\tier1_exact_matches.sql |
| Database Path | D:\north-africa-toe-builder\database\master_database.db |
| Records to Update | 19 |
| Confidence Score | 100 |
| Estimated Time | < 1 minute |
| Risk Level | Zero (full rollback available) |
| Priority Test Cases Solved | 2/4 (50%) |

**Ready to execute** - approve to proceed.
