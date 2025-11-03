# Database Quality Baseline Report

**Generated**: 2025-11-02
**Database**: `D:\north-africa-toe-builder\database\master_database.db`
**Agent**: Specialist Data Cleaning & Normalization Agent v2.0.0
**Mode**: Phase 1 Discovery & Analysis (READ-ONLY)

---

## Executive Summary

Comprehensive data quality analysis of 42 tables containing ~21,000 records across equipment, BattleGroup, and supporting tables.

**CRITICAL FINDINGS**:
- **58 WITW ID collisions** affecting 169 equipment records (36% of equipment table)
- **4 aircraft categorized as tanks** (semantic violations)
- **99.6% NULL equipment_type** (467/469 records)
- **100% missing gun linkages** (112 tanks, 0 equipment_guns entries)
- **154 exact duplicate groups in bg_reference_vehicles**

---

## Summary Metrics

| Category | Count | Severity | Impact |
|----------|-------|----------|--------|
| **WITW ID collisions** | 58 collisions (169 records) | **CRITICAL** | Blocks Phase 10 scenario exports |
| **Aircraft-as-tanks** | 4 records | **CRITICAL** | Data corruption - tanks have aircraft WITW names |
| **NULL equipment_type** | 467/469 (99.6%) | **HIGH** | Missing categorization for all equipment |
| **Empty equipment_guns** | 112 tanks, 0 linkages | **HIGH** | Blocks Phase 9B book datacard generation |
| **Orphaned foreign keys** | 953 NULL equipment_ids | **HIGH** | Referential integrity violations |
| **Name mismatches** | 101 equipment items | **HIGH** | Equipment → bg_reference_vehicles lookup failures |
| **BattleGroup duplicates** | 154 groups (500+ records) | **MEDIUM** | Exact duplicates in bg_reference_vehicles |
| **Whitespace issues** | 0 detected | **LOW** | Clean |
| **Case inconsistencies** | 0 detected | **LOW** | Clean |

---

## Top 10 Critical Issues

### 1. WITW ID 115 Collision (11 items)
**Severity**: CRITICAL
**Type**: Multi-category collision (Hurricanes + Shermans + German artillery)

**Colliding Items**:
- 8 Hurricane aircraft variants (fighters + recon)
- 3 Sherman tanks (I, II, III)
- 1 German Sfh 18 15cm artillery

**Root Cause**: WITW ID assignment collision across categories
**Recommended Fix**: Set witw_id = NULL for all but one valid item (Phase 5 re-match)

---

### 2. WITW ID 110 Collision (8 items)
**Severity**: CRITICAL
**Type**: Multi-category collision (Blenheim bombers + German artillery)

**Colliding Items**:
- 7 Blenheim aircraft variants (bombers + reconnaissance)
- 1 German 10.5cm Lefh 18 artillery

**Recommended Fix**: Set witw_id = NULL for artillery, retain for primary Blenheim variant

---

### 3. Aircraft-as-Tanks Semantic Violations (4 items)
**Severity**: CRITICAL
**Type**: Data corruption

| canonical_id | name | witw_name | category |
|--------------|------|-----------|----------|
| GBR_CRUSADER_I | Crusader I | Lysander I (FI) | tanks |
| GBR_SHERMAN_I_M4 | Sherman I (M4) | Hurricane I (FI) | tanks |
| GBR_SHERMAN_II_M4A1 | Sherman II (M4A1) | Hurricane I (FI) | tanks |
| GBR_SHERMAN_III_M4A4 | Sherman III (M4A4) | Hurricane I (FI) | tanks |

**Root Cause**: WITW ID collision (IDs 115, 116) caused tanks to inherit aircraft names
**Recommended Fix**: Set witw_id = NULL, correct witw_name to match tank name

---

### 4. NULL equipment_type (467/469 records - 99.6%)
**Severity**: HIGH
**Type**: Missing categorization

**Impact**:
- Cannot infer equipment type for 99.6% of equipment
- Blocks type-based queries and filters
- Missing field required for equipment classification

**Recommended Fix**: Rules-based inference from `category` field
```sql
UPDATE equipment SET equipment_type =
  CASE
    WHEN category IN ('tanks', 'main_tanks', 'light_tanks', ...) THEN 'tank'
    WHEN category IN ('field_artillery', 'anti_tank', ...) THEN 'artillery'
    -- ... (see REMEDIATION_PLAN.md for complete rules)
  END
WHERE equipment_type IS NULL;
```

---

### 5. Empty equipment_guns Table (112 tanks, 0 linkages - 100% missing)
**Severity**: HIGH
**Type**: Missing relational data

**Impact**:
- Blocks Phase 9B book datacard generation (A10/A13 tanks need gun specs)
- Cannot display gun armament for any tank
- Data exists in `bg_reference_vehicles.weapons` JSON but not linked

**Recommended Fix**: Parse bg_reference_vehicles.weapons JSON, create equipment_guns linkages

---

### 6. Orphaned Foreign Keys in unit_equipment (953 NULL equipment_ids)
**Severity**: HIGH
**Type**: Referential integrity violation

**Count**: 953/953 unit_equipment records have NULL equipment_id (100%)

**Impact**:
- unit_equipment table is effectively unusable
- Cannot link units to their equipment

**Recommended Fix**: Investigate data source - may require re-import or manual linking

---

### 7-10. WITW ID Collisions (Multiple Categories)

| WITW ID | Collision Count | Categories Affected | Severity |
|---------|----------------|---------------------|----------|
| 100032 | 7 items | trucks + anti_aircraft | HIGH |
| 100043 | 7 items | command_vehicles + trucks | HIGH |
| 251 | 5 items | armored_cars + halftracks | HIGH |
| 626 | 5 items | support_vehicles + trucks | HIGH |

---

## Detailed Analysis by Detection Capability

### 1. Exact Duplicate Detection

**Equipment Table**: ✅ **CLEAN** (0 duplicates)

**BattleGroup Tables**:
- `bg_reference_vehicles`: **154 duplicate groups** affecting ~500+ records
  - Examples:
    - "Ambulance" - 6 duplicates
    - "Forward Headquarters" - 11 duplicates
    - "Sniper" - 10 duplicates
    - "Supply Column" - 10 duplicates

**Root Cause**: BattleGroup data includes generic unit types that appear in multiple nations/campaigns

**Recommendation**: These may be intentional (same unit used across different factions). Requires domain expert review.

---

### 2. Normalization Issue Detection

**Status**: ✅ **CLEAN**

- **Whitespace**: 0 issues detected
- **Case inconsistencies**: 0 issues detected
- **Format variations**: 0 issues detected

**Assessment**: Equipment table has excellent normalization standards.

---

### 3. Denormalization Detection

**Status**: ⚠️ **PARTIAL** (SQL error during transitive dependency detection)

**Multi-valued Attributes**: Not detected in this analysis (requires manual review of JSON fields)

**Recommendation**: Manual review of:
- `equipment.aliases` (JSON arrays)
- `equipment.manufacturers` (comma-separated values)
- `bg_reference_vehicles.weapons` (JSON arrays)

---

### 4. Naming Inconsistency Detection

**Status**: ⚠️ **101 MISMATCHES** (equipment → bg_reference_vehicles)

**Severity**: HIGH - Blocks gun data lookup for book datacards

**Top Mismatch Categories**:
- British tanks: 48 mismatches
- German tanks: 32 mismatches
- Italian tanks: 8 mismatches
- American tanks: 13 mismatches

**Example Mismatches**:
| Equipment Name | Best BG Match | Similarity | Issue |
|----------------|---------------|------------|-------|
| Panzer II Ausf C | Panzer II C | 75% | "Ausf" abbreviation |
| Valentine Mk II | Valentine II | 66.7% | "Mk" vs Roman numeral |
| Crusader Mk I | Crusader I AA Mk I | 75% | AA variant mismatch |

**Recommended Fix**: Create `equipment_name_variants` table with fuzzy matching rules

---

### 5. Constraint Violation Detection

**CRITICAL Violations**:
- ✅ **58 WITW ID collisions** (169 records affected)
- ✅ **4 aircraft-as-tanks** semantic violations

**HIGH Priority Violations**:
- ⚠️ **99.6% NULL equipment_type** (467/469)
- ⚠️ **100% missing equipment_guns** (112 tanks)
- ⚠️ **100% NULL equipment_id** in unit_equipment (953/953)

---

## Impact Assessment

### Phase 9B: Book Datacard Generation (BLOCKED)
**Status**: ❌ **BLOCKED BY CRITICAL ISSUES**

**Blocking Issues**:
1. Missing gun linkages (equipment_guns empty)
2. Name mismatches (A10/A13 tanks cannot find gun data)
3. NULL equipment_type (cannot categorize tanks)

**Example**: A10 Cruiser Mk II datacard cannot display 2pdr gun specifications

---

### Phase 10: WITW Scenario Exports (AT RISK)
**Status**: ⚠️ **CRITICAL CORRUPTION RISK**

**Risk**:
- 58 WITW ID collisions → scenario exports would assign wrong equipment
- 4 aircraft-as-tanks → tanks would export as aircraft
- 169/469 equipment records (36%) have corrupted WITW IDs

**Recommended**: DO NOT export scenarios until WITW ID collisions resolved

---

### Phase 5: Equipment Matching (PAUSED)
**Status**: ⏸️ **CORRECTLY PAUSED**

**Rationale**: Phase 5 matching would be corrupted by existing WITW ID collisions. Must clean database first.

---

## Data Quality Certification

**Status**: ❌ **FAILS PRODUCTION READINESS**

**Zero Tolerance Failures**:
- ❌ WITW ID collisions: 58 (target: 0)
- ❌ Aircraft-as-tanks: 4 (target: 0)
- ❌ Orphaned foreign keys: 953 (target: 0)

**High Priority Failures**:
- ❌ equipment_type populated: 0.4% (target: >95%)
- ❌ equipment_guns for tanks: 0% (target: >90%)

**Recommendation**: **PROCEED TO PHASE 2 - PRIORITIZATION & REMEDIATION**

---

## Next Steps: Phase 2 Remediation Planning

### Immediate Actions (CRITICAL)

1. **Resolve 58 WITW ID collisions**
   - Decision tree: semantic → category → variant → escalate
   - Estimated time: 3-4 hours
   - Deliverable: `witw_collision_resolutions.json`

2. **Fix 4 aircraft-as-tanks violations**
   - Set witw_id = NULL (Phase 5 will re-match)
   - Estimated time: 15 minutes
   - Deliverable: Corrected equipment records

### High Priority Actions (Day 1-2)

3. **Create name variant mapping table**
   - Populate equipment_name_variants from all sources
   - Estimated time: 3-4 hours
   - Deliverable: `equipment_name_variants` table

4. **Populate equipment_guns table**
   - Parse bg_reference_vehicles.weapons JSON
   - Create gun linkages for 112 tanks
   - Estimated time: 2-3 hours
   - Deliverable: Populated equipment_guns table

5. **Infer equipment_type from category**
   - Rules-based UPDATE query
   - Estimated time: 1 hour
   - Deliverable: 95%+ population rate

### Medium Priority Actions (Day 2-3)

6. **Review bg_reference_vehicles duplicates**
   - Manual review of 154 duplicate groups
   - Determine if intentional or merge-able
   - Estimated time: 2-3 hours

7. **Investigate unit_equipment orphaned FKs**
   - Determine root cause of 953 NULL equipment_ids
   - Re-import or manually link
   - Estimated time: 3-4 hours

---

## Deliverables Summary

### Phase 1 Outputs (COMPLETE)
- ✅ `DATA_QUALITY_BASELINE.md` (this file)
- ✅ `duplicate_analysis.json`
- ✅ `normalization_issues.json`
- ✅ `denormalization_report.json`
- ✅ `naming_inconsistencies.json`
- ✅ `constraint_violations.json`

### Phase 2 Outputs (PENDING)
- ⏳ `REMEDIATION_PLAN.md`
- ⏳ `witw_collision_resolutions.json`
- ⏳ `equipment_name_mapping.json`

---

## Database Statistics

### Tables Analyzed: 42

**Equipment Tables** (4):
- `equipment`: 469 records
- `afv_data`: 211 records
- `wwiitanks_afv_data`: 612 records
- `wwiitanks_gun_data`: 343 records

**BattleGroup Tables** (14):
- `bg_reference_vehicles`: 954 records (**154 duplicate groups**)
- `bg_reference_guns`: 57 records
- `bg_reference_defences`: 55 records
- `bg_reference_fire_support`: 77 records
- `equipment_battlegroup`: 469 records
- `bg_equipment_mapping`: 0 records
- `bg_special_rules`: 57 records
- `equipment_special_rules`: 1,599 records
- `bg_armor_conversion`: 16 records
- `bg_penetration_scale`: 24 records
- `bg_he_effectiveness`: 9 records
- `bg_movement_values`: 20 records
- `bg_campaign_units`: 0 records
- `bg_campaign_progression`: 1 record

**Supporting Tables** (9):
- `guns`: 348 records
- `ammunition`: 162 records
- `penetration_data`: 1,296 records
- `equipment_guns`: **0 records** ⚠️
- `unit_equipment`: 953 records (all NULL equipment_id) ⚠️
- `units`: 484 records
- `match_reviews`: 959 records
- `import_log`: 41 records
- `extraction_log`: 9 records

**WITW Tables** (5):
- `witw_devices`: 1,074 records
- `witw_ground_vehicles`: 1,118 records
- `witw_ground_weapons`: 2,327 records
- `witw_leaders`: 4,096 records
- `witw_toe_ob`: 2,151 records

**Other Tables** (10):
- `master_equipment`: 1,230 records
- `aircraft`: 1,010 records
- `infantry_squads`: 17 records
- `infantry_weapons`: 154 records
- `squad_weapons`: 41 records
- `infantry_weapon_types`: 15 records
- `Other_game_conversion_formulas`: 30 records
- `schema_version`: 2 records
- `bg_extraction_log`: 7 records
- `sqlite_sequence`: 19 records

**Total Records**: ~21,000

---

## Methodology

### Tools Used
- Python 3.10 + sqlite3
- Custom detection scripts (phase1_full_analysis.py)
- 5 specialized detectors:
  1. DuplicateDetector
  2. NormalizationDetector
  3. DenormalizationDetector
  4. NamingInconsistencyDetector
  5. ConstraintViolationDetector

### Analysis Approach
- READ-ONLY queries (no data modifications)
- Hash-based duplicate detection
- Fuzzy name matching (Jaccard similarity, 60% threshold)
- Pattern-based normalization checks
- Cross-table referential integrity validation

### Limitations
- Denormalization detector encountered SQL error (transitive dependencies not fully analyzed)
- BattleGroup duplicate analysis limited to bg_reference_vehicles only
- Name matching limited to equipment → bg_reference_vehicles (other table pairs not analyzed)

---

## Sign-Off

**Phase 1 Status**: ✅ **COMPLETE**
**Database Certification**: ❌ **FAILS PRODUCTION READINESS**
**Recommendation**: **PROCEED TO PHASE 2 REMEDIATION**

**Analyst**: Specialist Data Cleaning & Normalization Agent v2.0.0
**Date**: 2025-11-02
**Report Version**: 1.0.0

---

## Appendix: Sample Data

### Sample WITW ID Collision (ID 115)

```json
{
  "witw_id": 115,
  "collision_count": 11,
  "colliding_items": [
    "GBR_HURRICANE_MK1",
    "GBR_HAWKER_HURRICANE_MK_I",
    "GBR_HAWKER_HURRICANE_MK_II",
    "GBR_HAWKER_HURRICANE_MK_IIC",
    "GBR_HAWKER_HURRICANE_MK_IID",
    "GBR_SHERMAN_I_M4",           // <-- TANK with AIRCRAFT ID
    "GBR_SHERMAN_II_M4A1",        // <-- TANK with AIRCRAFT ID
    "GBR_HURRICANE_MK2",
    "GBR_HURRICANE_RECON",
    "GBR_SHERMAN_III_M4A4",       // <-- TANK with AIRCRAFT ID
    "GER_SFH_18_15CM"             // <-- ARTILLERY with AIRCRAFT ID
  ],
  "categories": ["fighters", "fighters", "fighters", "fighters", "fighters",
                 "tanks", "tanks", "fighters", "reconnaissance", "tanks",
                 "field_artillery"]
}
```

### Sample Name Mismatch

```json
{
  "canonical_id": "GBR_VALENTINE_MK_II",
  "equipment_name": "Valentine Mk II",
  "category": "main_tanks",
  "bg_exact_match": false,
  "bg_fuzzy_matches": [
    {
      "bg_name": "Valentine II",
      "similarity": 0.667
    }
  ]
}
```

**Analysis**: Equipment uses "Mk II" notation, BattleGroup uses "II" notation. Need variant mapping to link these.

---

**END OF REPORT**
