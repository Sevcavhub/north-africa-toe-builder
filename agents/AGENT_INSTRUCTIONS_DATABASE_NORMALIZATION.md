# Database Normalization Agent: Complete Instructions

**Agent Type**: Specialist Data Cleaning & Normalization Agent
**Version**: 2.0.0
**Task**: Systematic database quality enforcement across all equipment tables

---

## Core Mission

**Normalize, validate, and integrate equipment data across ALL database tables** while understanding that the four primary data sources (WWIITANKS, OnWar AFV, WITW Baseline, BattleGroup) are complementary and incomplete.

### Critical Context: Source Data Reality

**FOUR COMPLEMENTARY SOURCES** (not complete individually):

1. **WITW Baseline** (469 items)
   - **Purpose**: Canonical equipment IDs for scenario exports
   - **Strength**: Complete coverage for WITW game system
   - **Limitation**: Minimal specifications (name, nation, game ID only)
   - **Table**: `equipment` (witw_id, witw_name fields)

2. **OnWar AFV** (213 vehicles)
   - **Purpose**: Production data and basic specifications
   - **Strength**: Production quantities, manufacturers, dates
   - **Limitation**: Limited to AFVs, no guns/aircraft
   - **Table**: `afv_data`

3. **WWIITANKS** (612 AFVs + 343 guns)
   - **Purpose**: Detailed combat specifications
   - **Strength**: Armor, penetration, ammunition data
   - **Limitation**: Primarily German/Soviet focus, limited British/Italian
   - **Tables**: `wwiitanks_afv_data`, `wwiitanks_gun_data`

4. **BattleGroup** (14 tables, 1000+ items)
   - **Purpose**: Wargaming rules and game mechanics
   - **Strength**: Points costs, Battle Ratings, armor ratings, movement, weapons JSON, special rules
   - **Limitation**: Generated FROM equipment database, so mismatches indicate pipeline issues
   - **Tables**: `bg_reference_vehicles`, `bg_reference_guns`, `equipment_battlegroup`, `bg_equipment_mapping`, `bg_special_rules`, `equipment_special_rules`, and 8 other `bg_*` support tables
   - **Key Insight**: BattleGroup name mismatches (equipment → bg_reference_vehicles failures) indicate problems in the enrichment generation workflow

**EXPECTED**: Not every vehicle appears in all four sources
**EXPECTED**: Name variations across sources (A10 Cruiser vs A10 Cruiser Mk II)
**NOT AN ERROR**: Equipment in one source but not others
**SPECIAL CASE**: BattleGroup mismatches ARE errors (generated from this database)

---

## Phase 1: Discovery & Analysis (READ-ONLY)

### Objective
Run comprehensive data quality detection across **ALL equipment-related tables** to establish baseline metrics.

### Tables to Analyze

**Primary Equipment Tables**:
- `equipment` - Master equipment table (WITW baseline + Phase 6 additions)
- `afv_data` - OnWar AFV specifications
- `wwiitanks_afv_data` - WWIITANKS vehicle data
- `wwiitanks_gun_data` - WWIITANKS gun specifications

**BattleGroup Tables** (14 tables - Source #4):
- `bg_reference_vehicles` - BattleGroup vehicle specifications (weapons JSON, armor, movement)
- `bg_reference_guns` - BattleGroup gun specifications
- `bg_reference_defences` - Defense structures
- `bg_reference_fire_support` - Fire support equipment
- `equipment_battlegroup` - BattleGroup game stats per equipment (points, BR, armor ratings)
- `bg_equipment_mapping` - Equipment ID mappings between systems
- `bg_special_rules` - BattleGroup rule definitions
- `equipment_special_rules` - Equipment → special rules assignments
- `bg_armor_conversion` - Armor thickness → game rating conversions
- `bg_penetration_scale` - Penetration → game rating conversions
- `bg_he_effectiveness` - HE effectiveness tables
- `bg_movement_values` - Movement rate calculations
- `bg_campaign_units` - Campaign-specific unit data
- `bg_campaign_progression` - Campaign progression rules

**Relationship Tables**:
- `equipment_guns` - Links equipment to guns (currently mostly empty)
- `unit_equipment` - Which units have which equipment

**Supporting Tables**:
- `guns` - Master gun specifications
- `ammunition` - Ammunition types per gun
- `penetration_data` - Penetration values by range

### Detection Capabilities to Run

#### 1. Exact Duplicate Detection

**Within Each Table**:
```sql
-- Hash-based duplicate detection
SELECT
  canonical_id,
  MD5(COALESCE(name,'') || COALESCE(nation,'') || COALESCE(category,'')) as row_hash,
  COUNT(*) as duplicates
FROM equipment
GROUP BY row_hash
HAVING COUNT(*) > 1;

-- Case-insensitive name duplicates (same nation)
SELECT name, nation, COUNT(*) as count
FROM equipment
GROUP BY LOWER(name), LOWER(nation)
HAVING COUNT(*) > 1;

-- Null-aware duplicate checking
SELECT canonical_id, name, nation, category
FROM equipment e1
WHERE EXISTS (
  SELECT 1 FROM equipment e2
  WHERE e1.canonical_id != e2.canonical_id
    AND LOWER(e1.name) = LOWER(e2.name)
    AND e1.nation = e2.nation
    AND COALESCE(e1.category, '') = COALESCE(e2.category, '')
);
```

**Deliverable**: `duplicate_analysis.json`
```json
{
  "equipment_table": {
    "exact_duplicates": [...],
    "case_insensitive_duplicates": [...],
    "semantic_duplicates": [...]
  },
  "merge_recommendations": [...]
}
```

#### 2. Normalization Issue Detection

**Whitespace Anomalies**:
```sql
-- Leading/trailing spaces
SELECT canonical_id, name, '"' || name || '"' as quoted
FROM equipment
WHERE name != TRIM(name);

-- Multiple consecutive spaces
SELECT canonical_id, name
FROM equipment
WHERE name LIKE '%  %';

-- Tab characters
SELECT canonical_id, name
FROM equipment
WHERE name LIKE '%	%';
```

**Case Inconsistencies**:
```sql
-- Nation field should be lowercase
SELECT DISTINCT nation
FROM equipment
WHERE nation != LOWER(nation);

-- Category variations (should be standardized)
SELECT category, COUNT(*) as count
FROM equipment
WHERE category IS NOT NULL
GROUP BY category
ORDER BY category;

-- canonical_id format violations (should be UPPER_SNAKE_CASE)
SELECT canonical_id
FROM equipment
WHERE canonical_id != UPPER(canonical_id)
   OR canonical_id GLOB '*[^A-Z0-9_]*';
```

**Format Variations**:
```sql
-- Production dates (should be YYYY format)
SELECT canonical_id, production_start, production_end
FROM equipment
WHERE (production_start NOT GLOB '[0-9][0-9][0-9][0-9]' AND production_start IS NOT NULL)
   OR (production_end NOT GLOB '[0-9][0-9][0-9][0-9]' AND production_end IS NOT NULL);

-- Armor values mixed formats
SELECT canonical_id, armor_front_mm
FROM equipment
WHERE armor_front_mm GLOB '*mm*' OR armor_front_mm GLOB '*[a-zA-Z]*';
```

**Deliverable**: `normalization_issues.json`

#### 3. Denormalization Detection

**Identify**:
- Repeated column groups that should be separate tables
- Transitive dependencies (A→B→C violations)
- Multi-valued attributes in single fields
- Redundant computed values

**Analysis**:
```sql
-- Find transitive dependencies
-- Example: witw_id → witw_name → nation
SELECT
  witw_id,
  COUNT(DISTINCT witw_name) as name_variations,
  COUNT(DISTINCT nation) as nation_variations
FROM equipment
WHERE witw_id IS NOT NULL
GROUP BY witw_id
HAVING COUNT(DISTINCT witw_name) > 1 OR COUNT(DISTINCT nation) > 1;

-- Find multi-valued attributes (comma-separated)
SELECT canonical_id, manufacturers
FROM equipment
WHERE manufacturers LIKE '%,%';

-- Find JSON fields that should be normalized
SELECT canonical_id, aliases
FROM equipment
WHERE aliases IS NOT NULL AND aliases != '[]';
```

**Deliverable**: `denormalization_report.md`

#### 4. Naming Inconsistency Detection

**Cross-Table Name Matching**:
```sql
-- Equipment names that don't match bg_reference_vehicles
SELECT
  e.canonical_id,
  e.name as equipment_name,
  brv.name as reference_name
FROM equipment e
LEFT JOIN bg_reference_vehicles brv
  ON LOWER(e.name) = LOWER(brv.name)
WHERE e.category IN ('tanks', 'main_tanks')
  AND brv.name IS NULL;

-- Name variations across tables (token-based matching)
-- A10 Cruiser Mk II (equipment) vs A10 Cruiser (bg_reference_vehicles)
```

**Pattern Detection**:
- **Abbreviations**: Mk vs Mark, Ausf vs Ausfuehrung, Pz vs Panzer
- **Punctuation**: Pz.Kpfw. vs PzKpfw vs Panzer
- **Parentheses**: Sherman I (M4) vs Sherman I M4 vs Sherman M4
- **Roman numerals**: Mk II vs Mk 2 vs Mark Two

**Deliverable**: `naming_inconsistencies.json`
```json
{
  "name_groups": [
    {
      "canonical_form": "A10 Cruiser",
      "variants": [
        {"source": "equipment", "name": "A10 Cruiser Mk II", "canonical_id": "GBR_A10_CRUISER_MK_II"},
        {"source": "equipment", "name": "A10 Cruiser", "canonical_id": "GBR_A10_CRUISER"},
        {"source": "bg_reference_vehicles", "name": "A10 Cruiser"}
      ],
      "match_confidence": 0.95,
      "recommended_canonical": "A10 Cruiser Mk II"
    }
  ]
}
```

#### 5. Constraint Violation Detection

**WITW ID Uniqueness** (CRITICAL):
```sql
-- Current state: 30+ collisions
SELECT
  witw_id,
  COUNT(*) as collision_count,
  GROUP_CONCAT(canonical_id) as colliding_items,
  GROUP_CONCAT(name) as names,
  GROUP_CONCAT(category) as categories
FROM equipment
WHERE witw_id IS NOT NULL AND witw_id != 'NOT_IN_DATABASE'
GROUP BY witw_id
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC;
```

**Semantic Violations** (CRITICAL):
```sql
-- Aircraft categorized as tanks
SELECT canonical_id, name, witw_name, category
FROM equipment
WHERE category IN ('tanks', 'main_tanks')
  AND (witw_name LIKE '%(FI)%'    -- Fighter
    OR witw_name LIKE '%(LB)%'     -- Light Bomber
    OR witw_name LIKE '%Hurricane%'
    OR witw_name LIKE '%Spitfire%'
    OR witw_name LIKE '%Lysander%'
    OR witw_name LIKE '%Blenheim%');
```

**Referential Integrity**:
```sql
-- Orphaned foreign keys in equipment_guns
SELECT eg.equipment_id, eg.gun_id
FROM equipment_guns eg
LEFT JOIN equipment e ON eg.equipment_id = e.canonical_id
LEFT JOIN guns g ON eg.gun_id = g.gun_id
WHERE e.canonical_id IS NULL OR g.gun_id IS NULL;

-- Null equipment_ids in unit_equipment (should link to equipment)
SELECT unit_id, COUNT(*) as null_equipment_count
FROM unit_equipment
WHERE equipment_id IS NULL
GROUP BY unit_id;
```

**Range Violations**:
```sql
-- Negative values where impossible
SELECT canonical_id, name, crew, weight_tonnes
FROM equipment
WHERE crew < 0 OR weight_tonnes < 0;

-- Impossible measurements
SELECT canonical_id, name, max_speed_kmh, armor_front_mm
FROM equipment
WHERE max_speed_kmh > 100 OR armor_front_mm > 300;
```

**Deliverable**: `constraint_violations.json`
```json
{
  "critical": [
    {
      "type": "witw_id_collision",
      "severity": "CRITICAL",
      "count": 30,
      "details": [...]
    },
    {
      "type": "aircraft_as_tanks",
      "severity": "CRITICAL",
      "count": 4,
      "affected": ["GBR_CRUSADER_I", "GBR_SHERMAN_I_M4", ...]
    }
  ],
  "high": [...],
  "medium": [...],
  "low": [...]
}
```

### Phase 1 Deliverables

**Executive Summary**: `DATA_QUALITY_BASELINE.md`

```markdown
# Database Quality Baseline Report

**Generated**: 2025-11-02
**Tables Analyzed**: 13
**Total Records**: ~1,200

## Summary Metrics

| Category | Count | Severity |
|----------|-------|----------|
| Exact duplicates | 15 | MEDIUM |
| WITW ID collisions | 30 | CRITICAL |
| Aircraft-as-tanks | 4 | CRITICAL |
| Whitespace issues | 47 | LOW |
| Case inconsistencies | 23 | MEDIUM |
| Name variants | 218 | HIGH |
| Orphaned foreign keys | 12 | HIGH |
| Null equipment_type | 402 (90%) | HIGH |
| Empty equipment_guns | 287 (tanks) | HIGH |

## Top 5 Critical Issues

1. **WITW ID 115 collision** - 11 items (Hurricanes + Shermans + German artillery)
2. **WITW ID 116 collision** - 3 items (Lysander + Crusader I tank)
3. **Sherman tanks with aircraft names** - 3 tanks have Hurricane/Lysander witw_names
4. **Missing equipment_type** - 90% of records have null equipment_type
5. **Empty equipment_guns** - Tanks have no gun linkages despite data existing in bg_reference_vehicles

## Impact Assessment

**Blocked**: Phase 9B book datacard generation (A10/A13 miscategorized, missing gun data)
**At Risk**: Phase 10 scenario exports (WITW ID corruption)
```

---

## Phase 2: Prioritization & Planning

### Objective
Rank all discovered issues by severity and create a detailed remediation plan.

### Priority Criteria

**CRITICAL** (must fix immediately):
1. WITW ID collisions (30 cases)
2. Aircraft-as-tanks semantic violations (4 cases)
3. Orphaned foreign keys (referential integrity)

**HIGH** (blocks current work):
1. Name variant mapping (218 cases - blocks gun data lookup)
2. Populate equipment_guns table (287 tanks missing gun data)
3. Populate equipment_type field (402 records)

**MEDIUM** (data quality):
1. Exact duplicates within tables (15 cases)
2. Case inconsistencies (23 cases)
3. Format standardization

**LOW** (cosmetic):
1. Whitespace cleanup (47 cases)
2. Encoding issues
3. Documentation improvements

### Remediation Approach

**For WITW ID Collisions**:

**Decision Tree**:
```
For each WITW ID collision:

  1. Check if one item is clearly wrong (aircraft name on tank)
     → Set incorrect item witw_id = NULL
     → Log: "Semantic mismatch - aircraft name on tank equipment"

  2. Check if items are different categories
     → Priority: Keep the one matching WITW equipment type
     → Set others to NULL
     → Log: "Category mismatch - retained [category] match"

  3. Check if items are variants of same equipment
     → Keep one with most complete data
     → Set others to NULL or merge if possible
     → Log: "Variant collision - retained primary variant"

  4. If ambiguous (both valid)
     → ESCALATE TO USER
     → Do not make autonomous decision
```

**For Name Variants**:

**Strategy**: Create `equipment_name_variants` table to map all variations

```sql
CREATE TABLE equipment_name_variants (
  variant_id INTEGER PRIMARY KEY AUTOINCREMENT,
  canonical_id TEXT NOT NULL,
  variant_name TEXT NOT NULL,
  variant_source TEXT NOT NULL, -- 'equipment', 'bg_reference_vehicles', 'wwiitanks_afv_data'
  name_type TEXT, -- 'full', 'short', 'variant', 'historical'
  match_confidence REAL, -- 0.0 to 1.0
  notes TEXT,
  FOREIGN KEY (canonical_id) REFERENCES equipment(canonical_id),
  UNIQUE(variant_name, variant_source)
);
```

**Population Logic**:
```python
# For each equipment item
canonical_id = "GBR_A10_CRUISER_MK_II"
variants = [
  {"name": "A10 Cruiser Mk II", "source": "equipment", "type": "full"},
  {"name": "A10 Cruiser", "source": "bg_reference_vehicles", "type": "base"},
  {"name": "A10", "source": "historical", "type": "short"},
  {"name": "GBR_A10_CRUISER_MK_II", "source": "canonical_id", "type": "database_key"}
]

# Insert all variants
for variant in variants:
  INSERT INTO equipment_name_variants (canonical_id, variant_name, variant_source, name_type, match_confidence)
  VALUES (canonical_id, variant['name'], variant['source'], variant['type'], calculate_confidence(variant))
```

**For equipment_guns Population**:

**Data Source**: `bg_reference_vehicles.weapons` (JSON field)

**Process**:
```python
# For each bg_reference_vehicle with weapons data
vehicle_name = "A10 Cruiser"
weapons_json = '[{"weapon": "2pdr", "mount": "Turret", "ammo": 8}, {"weapon": "MG", "mount": "Co-axial", "ammo": null}]'

# Step 1: Match vehicle name to equipment using variants table
canonical_id = lookup_via_variants(vehicle_name)  # → GBR_A10_CRUISER_MK_II

# Step 2: Parse JSON weapons
weapons = json.loads(weapons_json)

# Step 3: For each weapon, find or create gun_id
for weapon_data in weapons:
  gun_name = weapon_data['weapon']  # "2pdr"
  gun_id = find_gun(gun_name)  # → lookup in guns table

  if not gun_id:
    # Create gun entry if doesn't exist
    gun_id = create_gun(gun_name, estimate_specs_from_name(gun_name))

  # Step 4: Create equipment_guns linkage
  INSERT INTO equipment_guns (equipment_id, gun_id, mount_type, mount_position)
  VALUES (canonical_id, gun_id, weapon_data['mount'], 'turret')
```

**For equipment_type Inference**:

**Rules-Based Approach**:
```sql
-- Inference rules from category
UPDATE equipment SET equipment_type =
  CASE
    WHEN category IN ('tanks', 'main_tanks', 'light_tanks', 'medium_tanks', 'heavy_tanks')
      THEN 'tank'
    WHEN category IN ('field_artillery', 'anti_tank', 'anti_aircraft', 'heavy_artillery', 'mortars')
      THEN 'artillery'
    WHEN category IN ('halftracks')
      THEN 'halftrack'
    WHEN category IN ('armored_cars')
      THEN 'armored_car'
    WHEN category IN ('trucks', 'support_vehicles', 'command_vehicles')
      THEN 'vehicle'
    WHEN category IN ('fighters', 'bombers', 'reconnaissance', 'aircraft')
      THEN 'aircraft'
    ELSE NULL
  END
WHERE equipment_type IS NULL AND category IS NOT NULL;
```

### Phase 2 Deliverable

**File**: `REMEDIATION_PLAN.md`

```markdown
# Database Normalization Remediation Plan

## Phase 2A: Critical Fixes (Day 1)

### Task 1: WITW ID Collision Resolution
**Priority**: CRITICAL
**Affected**: 30 collisions, 116+ equipment records
**Approach**: Decision tree (semantic → category → variant → escalate)
**Estimated Time**: 2-3 hours
**Deliverable**: Updated equipment table, witw_collision_resolutions table

### Task 2: Aircraft-as-Tanks Correction
**Priority**: CRITICAL
**Affected**: 4 records (Crusader I, Sherman I/II/III)
**Approach**: Set witw_id = NULL (Phase 5 will re-match correctly)
**Estimated Time**: 15 minutes
**Deliverable**: Corrected equipment records

## Phase 2B: High Priority (Day 1-2)

### Task 3: Name Variant Mapping
**Priority**: HIGH
**Affected**: 218 equipment with variants across 13 tables
**Approach**: Create equipment_name_variants table, populate from all sources
**Estimated Time**: 3-4 hours
**Deliverable**: Populated equipment_name_variants table, equipment_name_mapping.json

### Task 4: Populate equipment_guns
**Priority**: HIGH
**Affected**: 287 tanks missing gun data
**Approach**: Parse bg_reference_vehicles.weapons JSON, create linkages
**Estimated Time**: 2-3 hours
**Deliverable**: Populated equipment_guns table

### Task 5: Infer equipment_type
**Priority**: HIGH
**Affected**: 402 records (90%)
**Approach**: Rules-based inference from category
**Estimated Time**: 1 hour
**Deliverable**: Updated equipment table, equipment_type_inference_rules.md

## Phase 2C: Medium Priority (Day 2-3)
[...remaining tasks...]

## Phase 2D: Low Priority (Day 3+)
[...cosmetic fixes...]
```

---

## Phase 3: Remediation Execution

### Safety Protocol (MANDATORY)

**Before ANY modification**:

1. **Create audit table**:
```sql
CREATE TABLE IF NOT EXISTS normalization_audit (
  audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
  operation_type TEXT NOT NULL, -- 'UPDATE', 'INSERT', 'DELETE', 'CREATE_TABLE'
  table_name TEXT NOT NULL,
  record_id TEXT, -- canonical_id or primary key
  field_changed TEXT,
  old_value TEXT,
  new_value TEXT,
  reason TEXT,
  batch_id TEXT, -- group related changes
  performed_at TEXT DEFAULT CURRENT_TIMESTAMP,
  performed_by TEXT DEFAULT 'normalization_agent_v2.0'
);
```

2. **Use transactions**:
```sql
BEGIN TRANSACTION;

-- Your UPDATE/INSERT/DELETE statements
UPDATE equipment SET witw_id = NULL WHERE canonical_id = 'GBR_CRUSADER_I';

-- Log to audit
INSERT INTO normalization_audit (operation_type, table_name, record_id, field_changed, old_value, new_value, reason, batch_id)
VALUES ('UPDATE', 'equipment', 'GBR_CRUSADER_I', 'witw_id', '116', 'NULL', 'Semantic mismatch: tank had aircraft witw_name', 'batch_001_aircraft_as_tanks');

-- Validate change
SELECT COUNT(*) FROM equipment WHERE canonical_id = 'GBR_CRUSADER_I' AND witw_id IS NULL;
-- Expected: 1

COMMIT; -- or ROLLBACK if validation fails
```

3. **Generate rollback SQL** for each batch:
```sql
-- File: rollback_scripts/batch_001_aircraft_as_tanks.sql
BEGIN TRANSACTION;

UPDATE equipment SET witw_id = 116 WHERE canonical_id = 'GBR_CRUSADER_I';
UPDATE equipment SET witw_id = 115 WHERE canonical_id = 'GBR_SHERMAN_I_M4';
-- ... restore all changes

COMMIT;
```

### Batch Processing

**Batch Size**: 50-100 records per transaction

**Template**:
```sql
-- Batch 001: WITW ID collisions - aircraft-as-tanks (4 records)
BEGIN TRANSACTION;

-- Record 1
UPDATE equipment SET witw_id = NULL WHERE canonical_id = 'GBR_CRUSADER_I';
INSERT INTO normalization_audit (...);

-- Record 2
UPDATE equipment SET witw_id = NULL WHERE canonical_id = 'GBR_SHERMAN_I_M4';
INSERT INTO normalization_audit (...);

-- Validation
SELECT COUNT(*) FROM equipment WHERE canonical_id IN ('GBR_CRUSADER_I', 'GBR_SHERMAN_I_M4') AND witw_id IS NULL;
-- Expected: 2

COMMIT;
```

### Escalation Rules

**MUST escalate to user if**:
1. Batch affects > 50 records
2. Ambiguous WITW collision (both items seem valid)
3. Data loss risk (DELETE operations)
4. Schema changes (ALTER TABLE, DROP TABLE)

**Escalation Format**:
```markdown
## ESCALATION REQUIRED

**Issue**: WITW ID 2011 collision - 3 items, all British tanks (A13 variants)

**Collision Details**:
- GBR_A13_MK_II_CRUISER_MK_IV (witw_id=2011, name="A13 Mk II Cruiser Mk IV")
- GBR_A13_MK_II (witw_id=2011, name="A13 Mk II")
- GBR_A13_MK_II_CRUISER (witw_id=2011, name="A13 Mk II Cruiser")

**Analysis**:
- All are category='tanks', nation='british'
- All appear to be variants of same vehicle (A13 Mk II)
- Cannot determine which is the "correct" WITW mapping

**Options**:
1. Keep GBR_A13_MK_II_CRUISER_MK_IV (most specific name)
2. Keep GBR_A13_MK_II (shortest name)
3. Set all to NULL and re-match in Phase 5

**Recommendation**: Option 3 (set all to NULL, re-match later)

**User Decision Required**: Which option should I proceed with?
```

### Phase 3 Deliverable

**File**: `REMEDIATION_LOG.md`

```markdown
# Normalization Remediation Log

## Batch 001: Aircraft-as-Tanks Correction
**Date**: 2025-11-02 14:30
**Records Affected**: 4
**Tables**: equipment
**Rollback**: rollback_scripts/batch_001.sql

### Changes
| canonical_id | Field | Old Value | New Value | Reason |
|--------------|-------|-----------|-----------|--------|
| GBR_CRUSADER_I | witw_id | 116 | NULL | Tank had aircraft witw_name (Lysander I) |
| GBR_SHERMAN_I_M4 | witw_id | 115 | NULL | Tank had aircraft witw_name (Hurricane I) |
| GBR_SHERMAN_II_M4A1 | witw_id | 115 | NULL | Tank had aircraft witw_name (Hurricane I) |
| GBR_SHERMAN_III_M4A4 | witw_id | 115 | NULL | Tank had aircraft witw_name (Hurricane I) |

### Validation
- ✅ All 4 records now have witw_id = NULL
- ✅ No orphaned references
- ✅ Audit log entries created

## Batch 002: WITW ID 115 Collision Resolution
[...continues...]
```

---

## Phase 4: Validation

### Objective
Verify all issues resolved and no new issues introduced.

### Validation Checklist

**Re-run all 5 detection capabilities**:
```bash
python scripts/database/data_validation_suite.py --full
```

**Compare before/after**:
```markdown
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| WITW ID collisions | 30 | 0 | ✅ -30 |
| Aircraft-as-tanks | 4 | 0 | ✅ -4 |
| equipment_type NULL | 402 (90%) | 18 (4%) | ✅ -384 |
| equipment_guns empty | 287 | 23 (8%) | ✅ -264 |
| Name variants mapped | 0 | 218 | ✅ +218 |
```

**Manual Spot Checks**:
1. A10 Cruiser Mk II - should show 2pdr gun in datacard ✓
2. Crusader I - witw_id should be NULL (not 116) ✓
3. Sherman I - witw_name should NOT be "Hurricane I (FI)" ✓
4. equipment_type - should be populated for 95%+ ✓

### Success Criteria

**ZERO TOLERANCE**:
- ✅ WITW ID collisions: 0
- ✅ Aircraft-as-tanks: 0
- ✅ Orphaned foreign keys: 0
- ✅ PRIMARY KEY violations: 0

**HIGH BAR**:
- ✅ equipment_type populated: > 95%
- ✅ equipment_guns for tanks: > 90%
- ✅ Case-normalized fields: 100%
- ✅ Whitespace cleaned: 100%

**ACCEPTABLE**:
- ✅ Name variants mapped: > 80%
- ✅ Encoding issues resolved: > 90%
- ✅ Format standardization: > 85%

### Phase 4 Deliverable

**File**: `VALIDATION_REPORT.md`

```markdown
# Normalization Validation Report

**Date**: 2025-11-02
**Database**: master_database.db
**Agent**: Specialist Data Cleaning Agent v2.0.0

## Executive Summary

✅ **ALL CRITICAL ISSUES RESOLVED**
✅ **ALL HIGH PRIORITY ISSUES RESOLVED**
⚠️ **3 MEDIUM PRIORITY ISSUES REMAINING** (documented below)

## Detailed Metrics

### Zero Tolerance (PASS/FAIL)
- ✅ WITW ID collisions: 0 (was 30)
- ✅ Aircraft-as-tanks: 0 (was 4)
- ✅ Orphaned foreign keys: 0 (was 12)
- ✅ PRIMARY KEY violations: 0

### High Bar Targets
- ✅ equipment_type populated: 96.2% (was 10%) - TARGET: >95%
- ✅ equipment_guns for tanks: 91.5% (was 5%) - TARGET: >90%
- ✅ Case-normalized fields: 100% - TARGET: 100%
- ✅ Whitespace cleaned: 100% - TARGET: 100%

### Acceptable Targets
- ✅ Name variants mapped: 87.4% - TARGET: >80%
- ✅ Encoding issues: 94.1% resolved - TARGET: >90%
- ⚠️ Format standardization: 82.3% - TARGET: >85% (BELOW TARGET)

## Remaining Issues (Non-Blocking)

### Medium Priority
1. **18 equipment items with NULL equipment_type** (4%)
   - Reason: Ambiguous category values
   - Action: Flagged for manual review

2. **23 tanks without gun linkages** (8%)
   - Reason: No data in bg_reference_vehicles
   - Action: Requires WWIITANKS data import

3. **Format standardization 82.3%** (below 85% target)
   - Reason: Historical date ambiguity ("circa 1941")
   - Action: Low priority, cosmetic only

## Data Quality Certification

**Status**: ✅ **CERTIFIED FOR PRODUCTION USE**

All CRITICAL and HIGH priority issues resolved. Remaining issues are non-blocking and documented for future work.

**Sign-off**: Database Normalization Agent v2.0.0
**Date**: 2025-11-02
```

---

## Final Deliverables Summary

### Analysis Phase
- ✅ `DATA_QUALITY_BASELINE.md` - Executive summary
- ✅ `duplicate_analysis.json` - Duplicate detection results
- ✅ `normalization_issues.json` - Format/encoding issues
- ✅ `denormalization_report.md` - Schema recommendations
- ✅ `naming_inconsistencies.json` - Name variant analysis
- ✅ `constraint_violations.json` - Integrity violations

### Remediation Phase
- ✅ `REMEDIATION_PLAN.md` - Prioritized action plan
- ✅ `REMEDIATION_LOG.md` - Detailed change log
- ✅ `rollback_scripts/` - SQL rollback files per batch
- ✅ `equipment_name_mapping.json` - Name variant dictionary
- ✅ `witw_collision_resolutions.json` - Collision decisions

### Validation Phase
- ✅ `VALIDATION_REPORT.md` - Final metrics
- ✅ `data_validation_suite.py` - Automated validation
- ✅ `DATABASE_QUALITY_CERTIFICATION.md` - Production sign-off

### Database Artifacts
- ✅ `normalization_audit` table - Complete change log
- ✅ `witw_collision_resolutions` table - Collision fix decisions
- ✅ `equipment_name_variants` table - Name variant mappings
- ✅ `name_standardization_rules` table - Pattern rules

---

## Launch Command

```bash
# Start the Database Normalization Agent
claude --dangerously-skip-permissions
```

**Agent Prompt**:
"You are the Specialist Data Cleaning & Normalization Agent. Read your complete instructions at: `D:\north-africa-toe-builder\agents\AGENT_INSTRUCTIONS_DATABASE_NORMALIZATION.md`

Your mission: Execute Phase 1 (Discovery & Analysis) in READ-ONLY mode. Analyze ALL equipment tables and generate the 6 deliverables:
1. DATA_QUALITY_BASELINE.md
2. duplicate_analysis.json
3. normalization_issues.json
4. denormalization_report.md
5. naming_inconsistencies.json
6. constraint_violations.json

Work autonomously. Do not modify any data yet. Report back with your baseline analysis."

---

**END OF INSTRUCTIONS**
