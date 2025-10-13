# Validation Process

## Overview

Every unit undergoes **rigorous validation** before publication to ensure data accuracy, schema compliance, and historical plausibility. This page documents the complete validation workflow.

---

## Validation Phases

### Phase 1: Schema Validation

**Objective**: Verify JSON structure matches `unified_toe_schema.json v1.0.0`

**Automated Checks**:
- Required fields present
- Data types correct (string, number, boolean, array, object)
- Enum values valid (nation must be lowercase: british, german, italian, american)
- Nested structure correct (commander is object with name/rank/appointed fields)

**Tool**: `scripts/lib/validator.js`

**Example Error**:
```
❌ FAIL: Field "nation" must be lowercase
   Expected: "german"
   Found: "German"
```

**Pass Criteria**: Zero schema errors

---

### Phase 2: Mathematical Validation

**Objective**: Verify equipment and personnel totals sum correctly

#### Equipment Validation Rules

**Rule 1: Tank Totals**
```
tanks.total = tanks.heavy + tanks.medium + tanks.light
```
**Tolerance**: Exact match required (0% tolerance)

**Example**:
```json
{
  "tanks": {
    "total": 180,
    "heavy": 0,
    "medium": 120,
    "light": 60
  }
}
```
**Validation**: 180 = 0 + 120 + 60 ✅

---

**Rule 2: Artillery Minimum**
```
artillery_total ≥ field_artillery + anti_tank + anti_aircraft
```
**Tolerance**: Total must be at least sum of categories (allows for mortars, rocket artillery)

**Example**:
```json
{
  "artillery": {
    "total": 200,
    "field_artillery": 72,
    "anti_tank": 48,
    "anti_aircraft": 36,
    "mortars": 44
  }
}
```
**Validation**: 200 ≥ 72 + 48 + 36 = 156 ✅

---

**Rule 3: Ground Vehicles Minimum**
```
ground_vehicles_total ≥ tanks + trucks + motorcycles + armored_cars + support_vehicles
```
**Tolerance**: Total must be at least sum of categories

---

**Rule 4: Category = Sum of Variants**
```
category_total = sum(all_variants_in_category)
```
**Tolerance**: Exact match required

**Example**:
```json
{
  "medium_tanks": {
    "total": 120,
    "variants": [
      {"type": "Panzer III Ausf H", "count": 67},
      {"type": "Panzer III Ausf G", "count": 53}
    ]
  }
}
```
**Validation**: 120 = 67 + 53 ✅

---

#### Personnel Validation Rules

**Rule 5: Personnel Totals**
```
total_personnel ≈ officers + ncos + enlisted
```
**Tolerance**: ±5% (allows for rounding, temporary attachments)

**Example**:
```json
{
  "personnel": {
    "total": 10000,
    "officers": 580,
    "ncos": 1850,
    "enlisted": 7570
  }
}
```
**Validation**: 10000 vs (580 + 1850 + 7570 = 10000) → 0% difference ✅

---

**Rule 6: Percentage Totals**
```
officer_% + nco_% + enlisted_% ≈ 100%
```
**Tolerance**: ±0.5% (rounding)

---

#### Hierarchical Validation Rules

**Rule 7: Parent = Sum of Children**
```
parent_total ≈ sum(all_child_unit_totals)
```
**Tolerance**: ±5% (allows for corps-level assets, temporary attachments)

**Example**:
```
Division: 10,000 personnel
├─ Brigade A: 3,500
├─ Brigade B: 3,200
├─ Brigade C: 3,100
└─ Division troops: 200
Total children: 10,000 ✅
```

---

### Phase 3: Historical Accuracy Validation

**Objective**: Verify data is historically plausible for the quarter

#### Anachronism Checks

**Equipment Availability**:
- M4 Sherman not available in 1940-Q2 ❌
- Panzer III Ausf H available 1941-Q1+ ✅
- Tiger I not available until 1942-Q4 ❌

**Process**:
1. Check equipment variant against production date database
2. Compare production date to quarter date
3. Flag if equipment not yet produced

**Example Error**:
```
❌ ANACHRONISM: M4 Sherman listed in 1941-Q2
   First production: 1942-Q2
   Unit quarter: 1941-Q2
```

---

#### Commander Verification

**Requirements**:
- Commander name verified from 2+ sources
- Appointment date ≤ quarter end date
- Rank appropriate for unit type

**Example**:
```json
{
  "commander": {
    "name": "Major-General Sir Michael O'Moore Creagh",
    "rank": "Major-General",
    "appointed": "1939-12-04"
  },
  "quarter": "1940-Q2"
}
```
**Validation**: Appointed 1939-12-04, quarter ends 1940-06-30 → Valid ✅

---

#### Unit Designation Verification

**Requirements**:
- Unit designation historically accurate
- Nickname verified (if present)
- Subordinate units existed in quarter

**Example**:
- "7th Armoured Division" ✅
- Nickname: "Desert Rats" ✅ (adopted April 1940)
- Subordinate: "4th Armoured Brigade" ✅ (renamed from "4th Heavy Armoured Brigade" April 14, 1940)

---

### Phase 4: Template Compliance Validation

**Objective**: Verify MDBook chapter follows template v2.0

#### Section Presence Check

**All 16 required sections must be present**:
1. ✅ Header
2. ✅ Division/Unit Overview
3. ✅ Command
4. ✅ Personnel Strength
5. ✅ Armoured Strength
6. ✅ Artillery Strength
7. ✅ Armoured Cars
8. ✅ Transport & Vehicles
9. ✅ Organizational Structure
10. ✅ Supply Status
11. ✅ Tactical Doctrine & Capabilities
12. ✅ Critical Equipment Shortages
13. ✅ Historical Context
14. ✅ Wargaming Data
15. ✅ Data Quality & Known Gaps
16. ✅ Conclusion

**Automated Check**: Search for section headers in markdown file

---

#### Variant Detail Compliance

**Rule**: Every variant in summary table must have detail section

**Process**:
1. Parse summary table, extract variants
2. Search for detail section for each variant
3. Flag missing detail sections

**Example**:
```markdown
## Artillery Strength

| Type | Total |
|------|-------|
| **Field Artillery** | **96** |
| ↳ Ordnance QF 25-pounder | 72 |
| ↳ QF 4.5-inch Howitzer | 24 |

### Ordnance QF 25-pounder - 72 guns
✅ Detail section present

### QF 4.5-inch Howitzer - 24 guns
✅ Detail section present
```

**Validation**: 2 variants in table, 2 detail sections → Pass ✅

---

#### Formatting Compliance

**Requirements**:
- Category totals use **bold**
- Variants use `↳` symbol (not -, *, •)
- Tables properly formatted
- Readiness percentages calculated correctly
- Data source footer present in Conclusion

---

### Phase 5: Cross-Reference Validation

**Objective**: Verify JSON data matches MDBook chapter data

#### Key Data Points to Cross-Check

**From JSON → MDBook Chapter**:
- Commander name and rank
- Total personnel
- Tank totals (all categories)
- Artillery totals
- Unit designation
- Confidence score

**Process**:
1. Read JSON file
2. Read MDBook chapter file
3. Extract matching data points
4. Compare values
5. Flag discrepancies

**Example**:
```
JSON: "total_personnel": 10000
MDBook: "**Total Personnel** | **10,000**"
✅ Match
```

---

### Phase 6: Source Quality Validation

**Objective**: Verify adequate source citations

#### Citation Requirements

**Critical Facts** (require 2+ sources):
- Unit commander
- Unit designation
- Major equipment types
- Battle participation

**Important Facts** (require 1+ source):
- Personnel strength
- Equipment variants
- Subordinate units

**Process**:
1. Identify critical facts
2. Check source citations in JSON metadata
3. Flag facts with insufficient citations

**Example**:
```json
{
  "commander": {
    "name": "Major-General O'Moore Creagh",
    "sources": [
      "British Army List Q2 1941, page 45",
      "desertrats.org.uk"
    ]
  }
}
```
**Validation**: 2 sources for commander → Pass ✅

---

## Validation Outputs

### Validation Report Structure

```json
{
  "unit": "britain_1940q2_7th_armoured_division_toe",
  "validation_date": "2025-10-12",
  "overall_status": "PASS",
  "phases": {
    "phase1_schema": {
      "status": "PASS",
      "errors": []
    },
    "phase2_mathematical": {
      "status": "PASS",
      "warnings": [
        "Personnel total 9,995 vs sum 10,000 (-0.05% difference - acceptable)"
      ]
    },
    "phase3_historical": {
      "status": "PASS",
      "checks": {
        "anachronisms": "PASS - No anachronistic equipment",
        "commander": "PASS - Appointment date verified",
        "designation": "PASS - Unit designation verified"
      }
    },
    "phase4_template": {
      "status": "PASS",
      "sections_present": 16,
      "sections_required": 16,
      "variant_detail_compliance": "PASS"
    },
    "phase5_cross_reference": {
      "status": "PASS",
      "mismatches": []
    },
    "phase6_source_quality": {
      "status": "PASS",
      "sources_total": 7,
      "tier1_sources": 3,
      "tier2_sources": 4,
      "critical_facts_verified": "100%"
    }
  },
  "confidence_score": 85,
  "recommendation": "PUBLISH"
}
```

---

### Status Levels

**PASS**: No errors, all requirements met
**PASS_WITH_WARNINGS**: Minor issues, acceptable for publication
**FAIL**: Critical errors, requires correction before publication

---

## Common Validation Errors

### Schema Errors

**Error**: `Nation must be lowercase`
```json
❌ "nation": "German"
✅ "nation": "german"
```

**Error**: `Commander must be object`
```json
❌ "commander": "Erwin Rommel"
✅ "commander": {"name": "Erwin Rommel", "rank": "Generalleutnant"}
```

**Error**: `Organization level invalid`
```json
❌ "organization_level": "army"
✅ "organization_level": "division"
```

---

### Mathematical Errors

**Error**: `Tank totals don't match`
```json
❌ "tanks": {"total": 200, "medium": 120, "light": 70}
   200 ≠ 120 + 70 (=190)
✅ "tanks": {"total": 190, "medium": 120, "light": 70}
```

**Error**: `Personnel sum exceeds total (tolerance > 5%)`
```json
❌ "personnel": {"total": 10000, "officers": 600, "ncos": 2000, "enlisted": 8000}
   Sum: 10,600 vs Total: 10,000 = +6% (exceeds ±5% tolerance)
```

---

### Historical Errors

**Error**: `Anachronistic equipment`
```
❌ Unit: 15. Panzer-Division, Quarter: 1940-Q4
   Equipment: Panzer III Ausf J (first produced 1941-Q2)
```

**Error**: `Commander appointed after quarter`
```
❌ Commander: von Bismarck, Appointed: 1941-09-01
   Quarter: 1941-Q2 (ends 1941-06-30)
```

---

### Template Errors

**Error**: `Missing required section`
```
❌ Chapter missing Section 12: Critical Equipment Shortages
```

**Error**: `Variant detail missing`
```
❌ Table lists "Panzer IV Ausf F" but no detail section found
```

**Error**: `Data source footer missing`
```
❌ Conclusion section lacks required footer with schema version, confidence score
```

---

## Validation Tools

### Automated Tools

**scripts/lib/validator.js**:
- Schema validation
- Mathematical validation
- Cross-reference checking

**Usage**:
```bash
node scripts/lib/validator.js data/output/units/britain_1940q2_7th_armoured_division_toe.json
```

---

### Manual Validation

**Checklist** (see [Data Quality Standards](./data-quality.md)):
- [ ] Confidence score ≥ 75%
- [ ] Schema validation passes
- [ ] All 16 sections present
- [ ] Variant details match tables
- [ ] Critical facts cited (2+ sources)
- [ ] No anachronisms
- [ ] Commander verified
- [ ] Gaps documented

---

## Continuous Validation

### Version Control

**Track validation over time**:
- Initial validation date
- Last validation date
- Validation history (pass/fail record)
- Fixes applied

**Example**:
```json
{
  "validation_history": [
    {
      "date": "2025-10-10",
      "status": "FAIL",
      "issues": ["Tank totals mismatch", "Commander not verified"]
    },
    {
      "date": "2025-10-12",
      "status": "PASS",
      "issues": []
    }
  ]
}
```

---

### Re-Validation Triggers

**Re-validate when**:
- Schema version updated
- Template version updated
- Unit data modified
- New sources added
- Periodic review (quarterly)

---

## Further Reading

- [Research Methodology](./research-methodology.md) - Overall process
- [Data Quality Standards](./data-quality.md) - Quality requirements
- [Source Hierarchy](./source-hierarchy.md) - Source quality tiers

---

**Last Updated**: 2025-10-12
**Validation Standard**: unified_toe_schema.json v1.0.0 + MDBOOK_CHAPTER_TEMPLATE.md v2.0
**Pass Requirement**: All 6 phases PASS or PASS_WITH_WARNINGS
