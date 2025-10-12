# Unified Schema Examples & Guidelines

**Version:** 1.0.0
**Date:** 2025-10-12
**Purpose:** Reference for agents generating unit TO&E JSON files

---

## Critical Schema Rules

### ✅ CORRECT Structure (Unified Schema)

```json
{
  "schema_type": "division_toe",
  "schema_version": "1.0.0",

  "nation": "german",              // Top-level, lowercase only
  "quarter": "1941-Q2",            // Format: YYYY-QN
  "unit_designation": "15. Panzer-Division",
  "unit_type": "armored_division",
  "organization_level": "division", // Required!

  "command": {
    "commander": {                 // Nested object (NOT flat)
      "name": "Oberst Maximilian von Herff",
      "rank": "Oberst"
    }
  },

  "total_personnel": 15000,        // Top-level (NOT nested)
  "officers": 850,
  "ncos": 2800,
  "enlisted": 11350,

  "tanks": {                       // Top-level (NOT in equipment_summary)
    "heavy_tanks": 0,              // Direct values (NOT .total)
    "medium_tanks": 105,
    "light_tanks": 35,
    "total": 140
  },

  "artillery_total": 84,           // Top-level aggregate
  "ground_vehicles_total": 2890,  // Top-level aggregate

  "validation": {                  // Required object
    "source": [                    // Array of sources
      "Lexikon der Wehrmacht",
      "TM E 30-420"
    ],
    "confidence": 75,              // 0-100
    "last_updated": "2025-10-12",
    "known_gaps": [],
    "aggregation_status": "manually_entered"
  }
}
```

### ❌ INCORRECT Structures (DO NOT USE)

#### Wrong: Nested unit_identification

```json
{
  "unit_identification": {         // ❌ WRONG - Do not nest
    "nation": "italian",
    "quarter": "1941-Q2",
    "unit_designation": "132ª Ariete"
  }
}
```

**Correct:** Move all fields to top level

#### Wrong: Flat commander structure

```json
{
  "command": {
    "commander_name": "Ettore Baldassarre",  // ❌ WRONG - Flat structure
    "commander_rank": "Generale di Divisione"
  }
}
```

**Correct:** Use nested commander object

```json
{
  "command": {
    "commander": {                 // ✅ CORRECT
      "name": "Ettore Baldassarre",
      "rank": "Generale di Divisione"
    }
  }
}
```

#### Wrong: Nested personnel_summary

```json
{
  "personnel_summary": {           // ❌ WRONG - Do not nest
    "total_personnel": 6750,
    "officers": 340
  }
}
```

**Correct:** Use top-level fields

```json
{
  "total_personnel": 6750,         // ✅ CORRECT
  "officers": 340,
  "ncos": 1350,
  "enlisted": 5060
}
```

#### Wrong: Nested equipment_summary

```json
{
  "equipment_summary": {           // ❌ WRONG - Do not nest
    "tanks": {
      "total": 123
    }
  }
}
```

**Correct:** Use top-level equipment fields

```json
{
  "tanks": {                       // ✅ CORRECT
    "heavy_tanks": 0,
    "medium_tanks": 99,
    "light_tanks": 24,
    "total": 123
  },
  "artillery_total": 175,
  "ground_vehicles_total": 1123
}
```

---

## Nation Names (MUST USE EXACT VALUES)

**Allowed nation values (lowercase only):**
- `"german"` - Germany, Deutschland
- `"italian"` - Italy, Italia
- `"british"` - Britain, UK, Commonwealth (India, Australia, New Zealand, South Africa, Canada)
- `"american"` - USA, United States, US
- `"french"` - France

**❌ NEVER use:** "Germany", "Britain", "britain", "Italy", "USA", "America", "france"

---

## Quarter Format

**Correct:** `"1941-Q2"`, `"1942-Q3"`, `"1943-Q1"`

**Format:** `YYYY-QN` where N is 1, 2, 3, or 4

---

## Organization Level (Required Field)

**Allowed values:**
- `"theater"`
- `"corps"`
- `"division"`
- `"regiment"`
- `"battalion"`
- `"company"`
- `"platoon"`
- `"squad"`

---

## Validation Rules (Critical)

### 1. Tank Totals MUST Match

```json
{
  "tanks": {
    "heavy_tanks": 0,
    "medium_tanks": 99,
    "light_tanks": 24,
    "total": 123        // MUST equal 0 + 99 + 24 = 123
  }
}
```

❌ **Validation will FAIL if:** `total ≠ heavy_tanks + medium_tanks + light_tanks`

### 2. Personnel Totals MUST Approximately Match (±5%)

```json
{
  "total_personnel": 6750,
  "officers": 340,
  "ncos": 1350,
  "enlisted": 5060    // Sum = 6750 ✅
}
```

⚠️ **Warning if:** `|total_personnel - (officers + ncos + enlisted)| > 5%`

### 3. Commander Name Required When Confidence ≥ 50%

```json
{
  "command": {
    "commander": {
      "name": "Oberst von Herff",  // Required if confidence ≥ 50%
      "rank": "Oberst"
    }
  },
  "validation": {
    "confidence": 75    // ≥ 50%, so commander name is required
  }
}
```

❌ **Validation will FAIL if:** `confidence ≥ 50% AND commander.name is NULL or "Unknown"`

### 4. Required Top-Level Fields

**ALL units MUST have:**
- `schema_type`
- `schema_version`
- `nation`
- `quarter`
- `unit_designation`
- `organization_level`
- `validation` (with source, confidence, last_updated)

---

## Complete Minimal Example

```json
{
  "schema_type": "division_toe",
  "schema_version": "1.0.0",

  "nation": "german",
  "quarter": "1941-Q2",
  "unit_designation": "15. Panzer-Division",
  "unit_type": "armored_division",
  "organization_level": "division",

  "command": {
    "commander": {
      "name": "Oberst Maximilian von Herff",
      "rank": "Oberst"
    },
    "headquarters_location": "Libya (Tobruk sector)"
  },

  "total_personnel": 15000,
  "officers": 850,
  "ncos": 2800,
  "enlisted": 11350,

  "top_3_infantry_weapons": [
    {
      "weapon": "Karabiner 98k",
      "quantity": 9800,
      "percentage_of_total": 65.3,
      "witw_id": "GER_RIFLE_K98K"
    },
    {
      "weapon": "MP 40",
      "quantity": 1200,
      "percentage_of_total": 8.0,
      "witw_id": "GER_SMG_MP40"
    },
    {
      "weapon": "MG 34",
      "quantity": 420,
      "percentage_of_total": 2.8,
      "witw_id": "GER_MG_MG34"
    }
  ],

  "tanks": {
    "heavy_tanks": 0,
    "medium_tanks": 105,
    "light_tanks": 35,
    "total": 140
  },

  "artillery_total": 84,
  "ground_vehicles_total": 2890,

  "subordinate_units": [
    {
      "unit_designation": "Panzer-Regiment 8",
      "unit_type": "tank_regiment",
      "commander": "Oberst Gustav-Georg Knabe",
      "strength": 2200
    }
  ],

  "validation": {
    "source": [
      "Lexikon der Wehrmacht - 15. Panzer-Division entry",
      "TM E 30-420 - German Military Forces",
      "Afrika Korps deployment records"
    ],
    "confidence": 75,
    "last_updated": "2025-10-12",
    "known_gaps": [
      "Exact tank variant distribution (Ausf G vs H for Pz.III)",
      "Precise subordinate unit commander names",
      "Exact operational tank counts"
    ],
    "aggregation_status": "manually_entered"
  }
}
```

---

## Validation Commands

**Before saving any unit JSON:**

```javascript
const { validateUnit } = require('./scripts/lib/validator');

const result = validateUnit(unitObject);

if (result.critical.length > 0) {
    console.error('❌ Validation failed:', result.critical);
    // DO NOT SAVE - fix issues first
} else if (result.warnings.length > 0) {
    console.warn('⚠️  Warnings:', result.warnings);
    // OK to save, but review warnings
} else {
    console.log('✅ Validation passed');
    // Safe to save
}
```

**Run full validation:**

```bash
npm run validate
```

---

## Common Mistakes to Avoid

### ❌ 1. Using uppercase nation names

```json
{ "nation": "German" }  // ❌ WRONG
{ "nation": "german" }  // ✅ CORRECT
```

### ❌ 2. Wrong quarter format

```json
{ "quarter": "Q2 1941" }  // ❌ WRONG
{ "quarter": "1941-Q2" }  // ✅ CORRECT
```

### ❌ 3. Nested structure

```json
{
  "unit_identification": {        // ❌ WRONG
    "nation": "italian"
  }
}
```

Use top-level instead:

```json
{
  "nation": "italian"             // ✅ CORRECT
}
```

### ❌ 4. Flat commander

```json
{
  "command": {
    "commander_name": "..."       // ❌ WRONG
  }
}
```

Use nested object:

```json
{
  "command": {
    "commander": {                // ✅ CORRECT
      "name": "...",
      "rank": "..."
    }
  }
}
```

### ❌ 5. Missing required fields

```json
{
  "nation": "german",
  "quarter": "1941-Q2"
  // ❌ Missing: organization_level, validation
}
```

Always include:

```json
{
  "nation": "german",
  "quarter": "1941-Q2",
  "organization_level": "division",  // ✅ REQUIRED
  "validation": {                    // ✅ REQUIRED
    "source": [...],
    "confidence": 75
  }
}
```

---

## Schema Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-12 | Initial unified schema standard. Transformation of all 69 units completed. |

---

## For Agent Developers

**When generating unit JSON files:**

1. **ALWAYS** use this unified schema structure
2. **NEVER** nest `unit_identification`, `personnel_summary`, or `equipment_summary`
3. **ALWAYS** use nested `commander` object (not flat `commander_name`)
4. **ALWAYS** use lowercase nation names from allowed list
5. **ALWAYS** include `organization_level` field
6. **ALWAYS** include `validation` object with sources and confidence
7. **VALIDATE** before saving using `validateUnit()` from scripts/lib/validator.js

**Reference:** See `schemas/unified_toe_schema.json` for complete field definitions.

**Validation:** Run `npm run validate` to check all units for compliance.
