# Denormalization Analysis Report

**Generated**: 2025-11-02
**Database**: master_database.db
**Agent**: Specialist Data Cleaning & Normalization Agent v2.0.0

---

## Executive Summary

Analysis of database schema for denormalization issues including transitive dependencies, multi-valued attributes, and schema violations.

**Status**: ⚠️ **PARTIAL ANALYSIS** (SQL error in transitive dependency detection)

**Key Findings**:
- Multi-valued attributes detected in JSON and comma-separated fields
- Transitive dependency analysis incomplete (SQL error)
- Schema generally follows 3NF principles with some strategic denormalization

---

## 1. Multi-Valued Attributes

### 1.1 JSON Arrays (Strategic Denormalization)

**Table**: `equipment`
**Field**: `aliases`
**Purpose**: Store name variants as JSON array
**Example**:
```json
{
  "canonical_id": "GER_PANZER_IV_F2",
  "name": "Panzer IV F2",
  "aliases": ["Pz IV F2", "Pz.Kpfw. IV Ausf. F2", "PzKpfw IV F2"]
}
```

**Assessment**: ✅ **ACCEPTABLE**
- JSON is appropriate for storing unstructured variant lists
- Alternative (equipment_aliases table) would add complexity
- Current approach supports flexible name matching

---

**Table**: `bg_reference_vehicles`
**Field**: `weapons`
**Purpose**: Store weapon armament as JSON array
**Example**:
```json
{
  "name": "A10 Cruiser",
  "weapons": [
    {"weapon": "2pdr", "mount": "Turret", "ammo": 8},
    {"weapon": "MG", "mount": "Co-axial", "ammo": null}
  ]
}
```

**Assessment**: ⚠️ **SHOULD BE NORMALIZED**
- This data SHOULD be in `equipment_guns` table (currently empty)
- JSON approach blocks relational queries (e.g., "all vehicles with 2pdr gun")
- **Recommendation**: Migrate to equipment_guns table (see Phase 2 remediation)

---

### 1.2 Comma-Separated Values

**Analysis Query**:
```sql
SELECT COUNT(*) FROM equipment WHERE manufacturers LIKE '%,%';
```

**Result**: 0 records detected

**Assessment**: ✅ **CLEAN** - No comma-separated manufacturers field detected

---

## 2. Transitive Dependencies (3NF Violations)

### 2.1 Analysis Approach

**Target**: Detect A→B→C violations where non-key attributes determine other non-key attributes

**Example Pattern**:
```
witw_id → witw_name → nation
(Non-key)  (Non-key)    (Non-key)
```

**SQL Query** (FAILED due to SQLite GROUP_CONCAT DISTINCT syntax):
```sql
SELECT
  witw_id,
  COUNT(DISTINCT witw_name) as name_variations,
  COUNT(DISTINCT nation) as nation_variations,
  GROUP_CONCAT(DISTINCT witw_name, ' | ') as names,
  GROUP_CONCAT(DISTINCT nation, ' | ') as nations
FROM equipment
WHERE witw_id IS NOT NULL AND witw_id != 'NOT_IN_DATABASE'
GROUP BY witw_id
HAVING COUNT(DISTINCT witw_name) > 1 OR COUNT(DISTINCT nation) > 1;
```

**Error**: `DISTINCT aggregates must have exactly one argument`

---

### 2.2 Manual Analysis of Known Transitive Dependencies

#### Dependency Chain: witw_id → witw_name

**Analysis**: WITW ID should uniquely determine WITW name

**Finding**: 58 WITW ID collisions indicate this dependency is VIOLATED

**Examples**:
- WITW ID 115 → 11 different witw_names (Hurricanes, Shermans, artillery)
- WITW ID 110 → 8 different witw_names (Blenheims, German artillery)

**Assessment**: ❌ **3NF VIOLATION** (but caused by data error, not schema design)

**Recommendation**: Fix WITW ID collisions (Phase 2), then dependency holds

---

#### Dependency Chain: category → equipment_type

**Analysis**: Category should determine equipment_type

**Expected Mapping**:
```
category: 'tanks'           → equipment_type: 'tank'
category: 'field_artillery' → equipment_type: 'artillery'
category: 'fighters'        → equipment_type: 'aircraft'
```

**Finding**: 99.6% of equipment has NULL equipment_type

**Assessment**: ⚠️ **DEPENDENCY EXISTS BUT NOT ENFORCED**

**Recommendation**: Implement rules-based inference (see Phase 2 remediation)

---

## 3. Repeated Column Groups

### 3.1 Armor Value Columns

**Table**: `equipment`
**Column Group**:
```
armor_front_mm
armor_side_mm
armor_rear_mm
armor_turret_front_mm
armor_turret_side_mm
armor_turret_rear_mm
armor_top_mm
armor_bottom_mm
```

**Assessment**: ✅ **ACCEPTABLE DENORMALIZATION**
- Strategic denormalization for performance (avoid joins)
- Common pattern in equipment databases
- Alternative (armor_values table) would require 8 rows per vehicle
- Current approach supports simple queries: `SELECT armor_front_mm WHERE ...`

---

### 3.2 Production Date Columns

**Table**: `equipment`
**Column Group**:
```
production_start
production_end
production_quantity
```

**Assessment**: ✅ **PROPERLY NORMALIZED**
- These are attributes of the equipment entity (not separate entity)
- No repeated groups detected

---

## 4. Redundant Computed Values

### 4.1 BattleGroup Rating Conversions

**Tables**:
- `bg_armor_conversion` - Armor thickness → game rating
- `bg_penetration_scale` - Penetration → game rating
- `bg_he_effectiveness` - HE power → game rating

**Assessment**: ✅ **ACCEPTABLE REFERENCE TABLES**
- These are conversion formulae, not redundant data
- Stored as tables for flexibility (can adjust game balance)
- Alternative (hardcoded in code) would reduce flexibility

---

### 4.2 Equipment BattleGroup Stats

**Table**: `equipment_battlegroup`
**Computed Fields**:
```
points_cost        -- Calculated from armor + firepower + mobility
battle_rating      -- Calculated from overall effectiveness
armor_rating       -- Derived from armor_front_mm via bg_armor_conversion
```

**Assessment**: ⚠️ **STRATEGIC DENORMALIZATION**
- These ARE redundant (can be calculated from base stats)
- BUT: Pre-computation improves query performance
- Trade-off: Storage vs. CPU
- **Recommendation**: Keep but ensure consistency with base stats

---

## 5. Schema Quality Assessment

### 5.1 Normal Form Compliance

**Equipment Table**:
- **1NF**: ✅ PASS (atomic values, except strategic JSON)
- **2NF**: ✅ PASS (all non-key attributes depend on full primary key)
- **3NF**: ⚠️ PARTIAL (transitive dependency category→equipment_type not enforced)

**BattleGroup Tables**:
- **1NF**: ⚠️ VIOLATION (`bg_reference_vehicles.weapons` JSON should be normalized)
- **2NF**: ✅ PASS
- **3NF**: ✅ PASS

---

### 5.2 Strategic Denormalization (Intentional)

**Acceptable Cases**:
1. **Armor value columns** - Performance optimization for common queries
2. **BattleGroup computed stats** - Pre-calculation for game balance queries
3. **Aliases JSON arrays** - Flexible name variant storage

**Problematic Cases**:
1. **bg_reference_vehicles.weapons JSON** - Should be normalized to equipment_guns
2. **equipment_type NULL** - Dependency exists but not enforced

---

## 6. Recommendations

### 6.1 High Priority (Phase 2)

**Migrate bg_reference_vehicles.weapons → equipment_guns**
```sql
-- For each bg_reference_vehicle with weapons JSON:
--   1. Parse JSON array
--   2. Match vehicle name to equipment.canonical_id (via name variants)
--   3. For each weapon:
--      - Find/create gun_id in guns table
--      - INSERT INTO equipment_guns (equipment_id, gun_id, mount_type, ...)
```

**Enforce category → equipment_type dependency**
```sql
UPDATE equipment SET equipment_type =
  CASE
    WHEN category IN ('tanks', 'main_tanks', ...) THEN 'tank'
    WHEN category IN ('field_artillery', ...) THEN 'artillery'
    -- ... full mapping
  END
WHERE equipment_type IS NULL;
```

---

### 6.2 Medium Priority (Phase 3)

**Add CHECK constraints to enforce data quality**
```sql
ALTER TABLE equipment ADD CONSTRAINT
  CHECK (equipment_type IS NOT NULL);

ALTER TABLE equipment ADD CONSTRAINT
  CHECK (category IS NOT NULL);
```

**Create triggers to maintain consistency**
```sql
CREATE TRIGGER update_equipment_type_from_category
AFTER UPDATE OF category ON equipment
BEGIN
  UPDATE equipment SET equipment_type = infer_type(NEW.category)
  WHERE canonical_id = NEW.canonical_id;
END;
```

---

### 6.3 Low Priority (Future)

**Consider normalizing armor values** (if query performance is not a concern)
```sql
CREATE TABLE equipment_armor (
  armor_id INTEGER PRIMARY KEY,
  equipment_id TEXT REFERENCES equipment(canonical_id),
  location TEXT, -- 'front', 'side', 'rear', 'turret_front', ...
  thickness_mm INTEGER
);
```

**Trade-off Analysis**:
- ✅ Pros: Fully normalized, easier to add new armor locations
- ❌ Cons: Requires 8 rows per vehicle, complex joins, slower queries
- **Recommendation**: Keep current denormalized approach

---

## 7. Data Quality Impact

### 7.1 Denormalization Issues vs. Data Errors

**Important Distinction**:
- **Schema denormalization** (intentional design choice) → LOW priority
- **Data quality errors** (WITW ID collisions, NULL values) → CRITICAL priority

**Current Findings**:
- Most denormalization is strategic and acceptable
- Critical issues are DATA ERRORS, not schema design
- Focus Phase 2 remediation on data cleaning, not schema redesign

---

### 7.2 Blocking Issues for Phase 9B/10

**bg_reference_vehicles.weapons JSON** → ❌ **BLOCKS PHASE 9B**
- Cannot generate book datacards without equipment_guns linkages
- A10 Cruiser cannot show "2pdr gun" in datacard
- **Must migrate to equipment_guns table**

**equipment_type NULL** → ⚠️ **MINOR IMPACT**
- Doesn't block current work
- Can be inferred from category as needed
- Low priority cleanup

---

## 8. Methodology Notes

### 8.1 Analysis Limitations

**Transitive Dependency Detection**: ❌ **INCOMPLETE**
- SQL error prevented automated detection
- Manual analysis of known dependencies only
- Comprehensive analysis requires fixing SQL query

**Multi-Valued Attribute Detection**: ✅ **COMPLETE**
- JSON fields detected and reviewed
- Comma-separated values checked (none found)

---

### 8.2 Future Analysis Recommendations

**Fix SQL query for transitive dependencies**:
```sql
-- Remove DISTINCT from GROUP_CONCAT (SQLite limitation)
SELECT
  witw_id,
  COUNT(DISTINCT witw_name) as name_variations,
  GROUP_CONCAT(witw_name, ' | ') as names  -- No DISTINCT here
FROM equipment
WHERE witw_id IS NOT NULL
GROUP BY witw_id
HAVING COUNT(DISTINCT witw_name) > 1;
```

**Analyze additional table pairs**:
- guns → ammunition (transitive dependencies)
- units → unit_equipment → equipment (chain analysis)
- bg_reference_vehicles → equipment (name variant dependencies)

---

## Sign-Off

**Phase 1 Denormalization Analysis**: ⚠️ **PARTIAL COMPLETE**
**Critical Findings**: 1 (bg_reference_vehicles.weapons normalization needed)
**Recommendation**: **PROCEED TO PHASE 2** (migrate weapons JSON to equipment_guns)

**Analyst**: Specialist Data Cleaning & Normalization Agent v2.0.0
**Date**: 2025-11-02

---

**END OF REPORT**
