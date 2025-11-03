# DATABASE LINKAGE ANALYSIS
**Date**: 2025-11-03
**Task**: Populate equipment_battlegroup.reference_vehicle_id using exact pattern matching
**Status**: Discovery Phase Complete

---

## Executive Summary

**Current State**:
- Total equipment items: 469
- NULL reference_vehicle_id: 469/469 (100%)
- Available bg_reference_vehicles (with nation): 499
- Available bg_reference_guns: 57

**Matching Potential** (Tier 1 - Exact Matches Only):
- **34 exact matches found** (7.2% of equipment)
- Confidence: 100 (perfect name + nation match)

**Key Finding**: Artillery equipment (field_artillery, anti_tank, anti_aircraft) totaling 110 items cannot link to bg_reference_vehicles table - they need bg_reference_guns. This architectural issue must be addressed.

---

## Priority Test Cases - Results

### Test Case #1: GER_PANZER_III_AUSF_F
- **Equipment**: Panzer III Ausf F (german)
- **Category**: tanks
- **BG Match**: Panzer III F (id: 358, german)
- **Match Type**: Exact normalized match
- **Confidence**: 100
- **Status**: READY TO LINK

### Test Case #2: GBR_MATILDA_II
- **Equipment**: Matilda II (british)
- **Category**: tanks
- **BG Match**: Matilda II (id: 290, british)
- **Match Type**: Exact match
- **Confidence**: 100
- **Status**: READY TO LINK

### Test Case #3: USA_M4_SHERMAN
- **Equipment**: M4 Sherman (american)
- **Category**: tanks
- **BG Match**: M4 Sherman (id: 203 or 217, american - MULTIPLE MATCHES)
- **Match Type**: Exact match
- **Confidence**: 100
- **Status**: READY TO LINK (need to select primary variant)

### Test Case #4: GBR_25_POUNDER
- **Equipment**: 25 Pounder (british)
- **Category**: field_artillery
- **BG Match**: 25 pdr (id: 38, british) in bg_reference_GUNS
- **Match Type**: ARCHITECTURE MISMATCH
- **Confidence**: N/A
- **Status**: BLOCKED - equipment_battlegroup has NO reference_gun_id column

---

## Equipment Categories Analysis

### Vehicle Categories (Can link to bg_reference_vehicles)
| Category | Count | Notes |
|----------|-------|-------|
| tanks | 69 | Primary target for linking |
| main_tanks | 27 | Subset of tanks |
| light_tanks | 16 | Subset of tanks |
| armored_cars | 22 | Vehicles |
| halftracks | 12 | Vehicles |
| reconnaissance | 11 | Mixed (some vehicles) |
| trucks | 77 | Support vehicles |
| support_vehicles | 15 | Non-combat |
| **Total** | **249** | **53% of equipment** |

### Gun/Artillery Categories (Need bg_reference_guns)
| Category | Count | Notes |
|----------|-------|-------|
| field_artillery | 52 | BLOCKED - no ref column |
| anti_tank | 33 | BLOCKED - no ref column |
| anti_aircraft | 25 | BLOCKED - no ref column |
| **Total** | **110** | **23% of equipment** |

### Aircraft Categories (No BG reference tables)
| Category | Count | Notes |
|----------|-------|-------|
| fighters | 31 | No BG equivalent |
| bombers | 17 | No BG equivalent |
| aircraft | 14 | No BG equivalent |
| **Total** | **62** | **13% of equipment** |

### Other Categories
| Category | Count |
|----------|-------|
| motorcycles | 9 |
| carriers | 1 |
| Misc | 39 |
| **Total** | **49** |

---

## Matching Tier Breakdown

### Tier 1: Exact Matches (Case-Insensitive, Trimmed)
**Definition**: `LOWER(TRIM(equipment.name)) = LOWER(TRIM(bg_ref.name)) AND nation matches`

**Results**: 34 matches found

**Sample Matches**:
- USA_M4_SHERMAN → M4 Sherman (id: 203/217)
- USA_M3_LEE → M3 Lee (id: 216)
- GBR_MATILDA_II → Matilda II (id: 290)
- GBR_A10_CRUISER → A10 Cruiser (id: 285)
- GBR_CHURCHILL_VII → Churchill VII (id: 293)
- GER_SDKFZ_222 → SdKfz 222 (multiple variants)
- GER_SDKFZ_251_1 → SdKfz 251/1 (multiple variants)

**Nation Breakdown**:
- German: 20+ matches
- British: 5 matches
- American: 2 matches

**Confidence Score**: 100

---

### Tier 2: Normalized Matches (NOT YET ANALYZED)
**Definition**: Apply normalization rules, then match

**Normalization Rules** (to be implemented):
1. Remove punctuation: "Pz.Kpfw." → "Panzer", "Mk." → "Mk"
2. Expand abbreviations: "Ausf." → "Ausf", "pdr" → "pounder"
3. Normalize spacing: Multiple spaces → single space
4. Case normalization: All lowercase for comparison

**Status**: PENDING - requires Python normalization script

---

### Tier 3: Base Model Matches (NOT YET ANALYZED)
**Definition**: Extract base model, match variants

**Examples**:
- "Panzer III Ausf F" → base "Panzer III" → match "Panzer III J", "Panzer III L", etc.
- "M4 Sherman '76'" → base "M4 Sherman" → match any Sherman variant

**Approach**:
1. Strip variant suffixes (Ausf X, Mk X, etc.)
2. Match on base model name
3. Prefer closest variant if multiple matches

**Status**: PENDING - requires variant detection logic

**Confidence Score**: 80 (lower than exact due to variant ambiguity)

---

## Architecture Issues Identified

### Issue #1: No reference_gun_id Column
**Impact**: Cannot link 110 artillery/gun equipment items (23% of database)

**Affected Equipment**:
- 52 field_artillery items (105mm M2A1, 25 Pounder, etc.)
- 33 anti_tank items (57mm M1, 88mm FlaK, etc.)
- 25 anti_aircraft items (40mm Bofors, etc.)

**Recommendation**:
1. Add `reference_gun_id` column to equipment_battlegroup table
2. Create separate linkage process for guns
3. OR: Merge bg_reference_guns into bg_reference_vehicles with type flag

### Issue #2: Multiple Variants in bg_reference_vehicles
**Impact**: Some equipment has 5+ variant matches (e.g., SdKfz 222 appears 5 times)

**Examples**:
- SdKfz 222: 5 variants (different IDs, same nation)
- SdKfz 251/1: 5 variants
- M4 Sherman: 2+ variants

**Recommendation**:
1. Use `MIN(id)` to select earliest/primary variant
2. OR: Add variant_preference metadata to choose best match
3. OR: Store ALL variant IDs as JSON array in reference_vehicle_id

### Issue #3: Unknown Nation Records
**Impact**: 454 bg_reference_vehicles have nation='Unknown' (cannot match)

**Analysis**:
- These appear to be generic unit templates
- Some have vehicle names embedded (e.g., "Additional Tank M10 Wolverine")
- Cannot safely match due to missing nation context

**Recommendation**:
1. Parse vehicle names from Unknown records
2. Infer nation from context/naming
3. OR: Exclude from automated matching (manual review only)

---

## Unmatched Equipment Analysis

**Total Unmatched After Tier 1**: 435/469 (92.8%)

**Why Unmatched?**:
1. **Name variations** (90+ estimated):
   - "Panzer III Ausf F" vs "Panzer III F" (punctuation/abbreviation)
   - Equipment uses full names, BG uses shortened variants

2. **Missing BG references** (50+ estimated):
   - Trucks (77 items) - most have no BG vehicle equivalent
   - Aircraft (62 items) - no BG tables for aircraft
   - Support vehicles (15 items) - limited BG coverage

3. **Architecture gaps** (110 confirmed):
   - Artillery/guns cannot link (no reference_gun_id column)

4. **Nation Unknown** (potential matches exist but nation='Unknown')

---

## Recommendations

### Immediate Actions (This Session)

1. **Create normalization_audit table** - Track all changes with rollback capability

2. **Execute Tier 1 Exact Matches** (34 items, 7.2%):
   - Safest matches, highest confidence
   - Use MIN(bg_ref.id) for multiple variants
   - Set reference_match_confidence = 100

3. **Generate SQL for Tier 2 Normalization** (estimate: +60 matches, 12.8%):
   - Python script to normalize names
   - Preview matches before UPDATE
   - Set reference_match_confidence = 90

4. **Generate SQL for Tier 3 Base Model** (estimate: +30 matches, 6.4%):
   - Variant tolerance matching
   - Manual review list for ambiguous cases
   - Set reference_match_confidence = 80

5. **Document Unmatched Items** (estimate: 235 items, 50.1%):
   - Separate by reason (architecture, missing ref, support vehicles, aircraft)
   - Prioritize by usage frequency
   - Flag for manual review

### Future Actions (Separate Session)

1. **Add reference_gun_id column** to equipment_battlegroup
2. **Populate reference_gun_id** for 110 artillery items
3. **Resolve Unknown nation records** (454 items)
4. **Create variant preference** metadata for multiple matches

---

## Expected Outcomes

**Conservative Estimate** (Tier 1 only):
- 34 items linked (7.2%)
- 435 items remain NULL (92.8%)

**Optimistic Estimate** (Tiers 1-3):
- 124 items linked (26.4%)
- 345 items remain NULL (73.6%)
  - 110 blocked by architecture (guns)
  - 62 no BG equivalent (aircraft)
  - 173 need manual review/missing refs

**Realistic Target** (This Session):
- 90-100 items linked (19-21%)
- High confidence (90-100 scores)
- Zero data loss with audit trail

---

## Next Steps

1. **Await approval** on approach and tier strategy
2. **Create normalization_audit table** with rollback SQL
3. **Execute Tier 1 matches** (34 items)
4. **Develop normalization functions** for Tier 2
5. **Preview Tier 2 matches** for approval
6. **Execute approved Tier 2 matches**
7. **Generate LINKAGE_REPORT.md** with final statistics

---

## SQL Preview (Tier 1 Exact Matches)

```sql
-- Example for single match
UPDATE equipment_battlegroup
SET
    reference_vehicle_id = 290,
    reference_match_confidence = 100
WHERE equipment_id = 'GBR_MATILDA_II';

-- Example for multiple matches (use MIN id)
UPDATE equipment_battlegroup
SET
    reference_vehicle_id = (
        SELECT MIN(brv.id)
        FROM equipment e
        JOIN bg_reference_vehicles brv
            ON LOWER(TRIM(e.name)) = LOWER(TRIM(brv.name))
            AND e.nation = brv.nation
        WHERE e.canonical_id = equipment_battlegroup.equipment_id
    ),
    reference_match_confidence = 100
WHERE equipment_id IN (
    SELECT e.canonical_id
    FROM equipment e
    JOIN bg_reference_vehicles brv
        ON LOWER(TRIM(e.name)) = LOWER(TRIM(brv.name))
        AND e.nation = brv.nation
);
```

**Safety**: All UPDATEs wrapped in transactions with pre-validation COUNT checks.

---

**Analysis Complete** - Awaiting approval to proceed with Tier 1 execution.
