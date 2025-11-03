# DATABASE LINKAGE MATCHING STRATEGY
**Date**: 2025-11-03
**Analyst**: Claude (Database Normalization Agent)
**Task**: Exact pattern matching for equipment_battlegroup.reference_vehicle_id

---

## Tier 1: Exact Matches - CONFIRMED

**Total Matches**: 19 equipment items (4.1% of 469)
**Confidence**: 100 (perfect name + nation match)
**Method**: `LOWER(TRIM(equipment.name)) = LOWER(TRIM(bg_ref.name)) AND nation = nation`

### American Equipment (6 matches)
| Equipment ID | Name | BG ID | Notes |
|--------------|------|-------|-------|
| USA_M10_WOLVERINE | M10 Wolverine | 228 | Single match |
| USA_M3_LEE | M3 Lee | 233 | Single match |
| USA_M4_HIGH_SPEED_TRACTOR | M4 High Speed Tractor | 495 | Single match |
| USA_M4_SHERMAN | M4 Sherman | **203** | MULTIPLE (203, 217) - using MIN |
| USA_M5_HIGH_SPEED_TRACTOR | M5 High Speed Tractor | 496 | Single match |
| USA_M8_GREYHOUND | M8 Greyhound | 242 | Single match |

### British Equipment (6 matches)
| Equipment ID | Name | BG ID | Notes |
|--------------|------|-------|-------|
| GBR_A10_CRUISER | A10 Cruiser | 294 | Single match |
| GBR_A9_CRUISER | A9 Cruiser | 292 | Single match |
| GBR_CHURCHILL_VII | Churchill VII | 344 | Single match |
| GBR_HUMBER_SCOUT_CAR | Humber Scout Car | 334 | Single match |
| GBR_MATILDA_II | Matilda II | 290 | **PRIORITY TEST CASE** |
| GBR_MORRIS_QUAD | Morris Quad | 446 | Single match |

### German Equipment (7 matches)
| Equipment ID | Name | BG ID | Notes |
|--------------|------|-------|-------|
| GER_SDKFZ_222 | SdKfz 222 | **20** | MULTIPLE (20,70,121,171,377) - using MIN |
| GER_SDKFZ_223 | SdKfz 223 | 378 | Single match |
| GER_SDKFZ_231 | SdKfz 231 | 380 | Single match |
| GER_SDKFZ_250 | SdKfz 250 | 386 | Single match |
| GER_SDKFZ_251_1 | SdKfz 251/1 | **23** | MULTIPLE (23,73,124,174,388) - using MIN |
| GER_SDKFZ_251_2 | SdKfz 251/2 | **24** | MULTIPLE (24,74,125,175) - using MIN |
| GER_SDKFZ_251_3 | SdKfz 251/3 | **25** | MULTIPLE (25,75,126,176) - using MIN |

### Priority Test Case Status
- ✅ GBR_MATILDA_II → 290 (Matilda II) - READY
- ✅ USA_M4_SHERMAN → 203 (M4 Sherman, MIN of 203,217) - READY
- ❌ GER_PANZER_III_AUSF_F → NOT IN TIER 1 (needs normalization)
- ❌ GBR_25_POUNDER → BLOCKED (artillery, no ref_gun_id column)

---

## Tier 2: Normalized Matches - ESTIMATED

**Method**: Apply normalization functions, then exact match

### Normalization Rules

#### Rule 1: Punctuation Removal
```python
def normalize_punctuation(name):
    # Remove periods from abbreviations
    name = name.replace('Pz.Kpfw.', 'Panzer')
    name = name.replace('PzKpfw', 'Panzer')
    name = name.replace('Mk.', 'Mk')
    name = name.replace('Ausf.', 'Ausf')
    return name
```

**Examples**:
- "Panzer III Ausf. F" → "Panzer III Ausf F"
- "A10 Cruiser Mk. II" → "A10 Cruiser Mk II"

#### Rule 2: Spacing Normalization
```python
def normalize_spacing(name):
    # Multiple spaces to single
    import re
    return re.sub(r'\s+', ' ', name).strip()
```

#### Rule 3: Case Normalization
```python
def normalize_case(name):
    return name.lower()
```

#### Rule 4: Variant Suffix Removal (for base matching)
```python
def extract_base_model(name):
    # Remove common variant patterns
    patterns = [
        r'\s+Ausf\s+[A-Z]$',  # "Panzer III Ausf F" → "Panzer III"
        r'\s+Mk\s+[IVX]+$',   # "Churchill Mk IV" → "Churchill"
        r'\s+[IVX]+$',        # "Crusader III" → "Crusader"
        r'\s+M[0-9]+A[0-9]+$' # "Sherman M4A1" → "Sherman"
    ]
    base = name
    for pattern in patterns:
        base = re.sub(pattern, '', base, flags=re.IGNORECASE)
    return base
```

### Tier 2A: Punctuation + Spacing Normalization
**Estimated Matches**: 20-30 items

**Sample Candidates** (from analysis):
- GER_PANZER_III_AUSF_F ("Panzer III Ausf F") → Match "Panzer III F" (id: 358)
  - Normalized: "panzer iii ausf f" vs "panzer iii f"
  - **PRIORITY TEST CASE** - needs variant tolerance

- USA_M3A1_STUART ("M3A1 Stuart") → Match "M5 Stuart" or variant?
  - Potential: id 216 "M5 Stuart (A1, A2, A3)"

- GBR_A13_CRUISER_MK1 ("A13 Cruiser Mk1") → Match "A13 Mk I Cruiser" (id: 295)
  - Normalized: "a13 cruiser mk1" vs "a13 mk i cruiser"
  - Need Roman numeral normalization: "Mk1" → "Mk I"

### Tier 2B: Variant Name Patterns
**Estimated Matches**: 15-25 items

**Pattern**: Equipment uses "Model Variant" vs BG uses "Variant Model"

**Examples**:
- USA_LEE_M3 ("Lee M3") → Match "M3 Lee" (id: 233) - REVERSE ORDER
- USA_SHERMAN_M4 ("Sherman M4") → Match "M4 Sherman" (id: 203) - REVERSE ORDER
- USA_SHERMAN_M4A1 ("Sherman M4A1") → Match "M4A1 Sherman" or base "M4 Sherman"

**Strategy**: Try both orderings during normalization

### Tier 2C: Abbreviation Expansion
**Estimated Matches**: 5-10 items

**Abbreviations**:
- "pdr" → "pounder" (artillery)
- "Pz" → "Panzer"
- "SPG" → "Self-Propelled Gun"
- "AAA" → "Anti-Aircraft Artillery"

**Examples** (would need ref_gun_id):
- "25 pdr" → "25 Pounder"
- "17 pdr" → "17 Pounder"

---

## Tier 3: Base Model Matching - ESTIMATED

**Method**: Strip variant suffixes, match on base model name
**Confidence**: 80 (lower due to variant ambiguity)
**Estimated Matches**: 10-20 items

### Matching Strategy

1. **Extract base model** from equipment name
2. **Search for base model** in bg_reference_vehicles
3. **If multiple variants found**:
   - Prefer exact variant if available
   - Otherwise use MIN(id) for primary variant
   - OR: Match to most common/representative variant

### Examples

#### Panzer Variants
- Equipment: "Panzer III Ausf F" → Base: "Panzer III"
- BG Matches: Panzer III D (356), E (357), **F (358)**, G (365), H (367), J (369), L (360)
- Best Match: **358** (exact variant "F")

#### Sherman Variants
- Equipment: "M4A1 Sherman" → Base: "M4"
- BG Matches: M4 Sherman (203, 217), M4 Sherman '76' (219), M4A3E8 (218), etc.
- Best Match: **203** or **217** (base M4, use MIN → 203)

#### Churchill Variants
- Equipment: "Churchill Mk IV" → Base: "Churchill"
- BG Matches: Churchill III (341), Churchill VII (344), Churchill VIII (345), etc.
- Best Match: Ambiguous - could be id 341 (closest variant) or need manual review

### Variant Preference Metadata (Future Enhancement)

Create lookup table for preferred variants:
```sql
CREATE TABLE variant_preferences (
    base_model TEXT,
    nation TEXT,
    preferred_bg_id INTEGER,
    reason TEXT
);

INSERT INTO variant_preferences VALUES
('Panzer III', 'german', 369, 'J variant most common in North Africa'),
('Churchill', 'british', 341, 'Churchill III standard mid-war'),
('M4 Sherman', 'american', 203, 'Base M4 most common early/mid-war');
```

---

## Implementation Plan

### Phase 1: Tier 1 Exact Matches (READY NOW)

```sql
-- Create audit table
CREATE TABLE IF NOT EXISTS normalization_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id TEXT NOT NULL,
    operation TEXT NOT NULL,
    old_reference_vehicle_id INTEGER,
    new_reference_vehicle_id INTEGER,
    old_confidence INTEGER,
    new_confidence INTEGER,
    match_tier TEXT,
    match_method TEXT,
    bg_vehicle_name TEXT,
    equipment_name TEXT,
    nation TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    rollback_sql TEXT
);

-- Generate rollback SQL for each UPDATE
-- INSERT INTO normalization_audit (...) VALUES (...)

-- Execute Tier 1 UPDATEs
BEGIN TRANSACTION;

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

-- Validate: Expect 19 rows affected
SELECT CHANGES(); -- Should return 19

-- Log to audit table
INSERT INTO normalization_audit (
    equipment_id, operation, new_reference_vehicle_id, new_confidence,
    match_tier, match_method, equipment_name, nation
)
SELECT
    eb.equipment_id,
    'UPDATE',
    eb.reference_vehicle_id,
    100,
    'Tier 1',
    'exact_match',
    e.name,
    e.nation
FROM equipment_battlegroup eb
JOIN equipment e ON eb.equipment_id = e.canonical_id
WHERE eb.reference_match_confidence = 100;

COMMIT;
```

### Phase 2: Tier 2 Normalization (REQUIRES PYTHON)

Create Python script `scripts/linkage/normalize_and_match.py`:

```python
import sqlite3
import re

def normalize_name(name):
    """Apply all normalization rules"""
    # Punctuation
    name = name.replace('Pz.Kpfw.', 'Panzer')
    name = name.replace('PzKpfw', 'Panzer')
    name = name.replace('Mk.', 'Mk')
    name = name.replace('Ausf.', 'Ausf')

    # Spacing
    name = re.sub(r'\s+', ' ', name).strip()

    # Case
    name = name.lower()

    return name

def try_reverse_order(name):
    """Try reversing 'Sherman M4' → 'M4 Sherman'"""
    parts = name.split()
    if len(parts) == 2:
        return f"{parts[1]} {parts[0]}"
    return None

# Match with normalization
# Match with reverse order
# Generate SQL for matches found
```

### Phase 3: Tier 3 Base Model Matching (MANUAL REVIEW REQUIRED)

- Generate candidate matches
- Export to CSV for review
- Import approved matches
- Execute UPDATEs with confidence = 80

---

## Safety Protocol

### Pre-Execution Checks
1. ✅ Backup database: `master_database_backup_YYYYMMDD.db`
2. ✅ Create normalization_audit table
3. ✅ Generate rollback SQL for all UPDATEs
4. ✅ Validate COUNT before COMMIT

### Batch Processing
- Process in batches of 50 records
- COMMIT after each successful batch
- Stop on first error (don't continue with remaining batches)

### Rollback Capability
```sql
-- Rollback Tier 1 changes
UPDATE equipment_battlegroup
SET
    reference_vehicle_id = NULL,
    reference_match_confidence = NULL
WHERE equipment_id IN (
    SELECT equipment_id
    FROM normalization_audit
    WHERE match_tier = 'Tier 1'
);

DELETE FROM normalization_audit WHERE match_tier = 'Tier 1';
```

---

## Expected Outcomes

### Conservative (Tier 1 Only)
- **19 items linked** (4.1% of 469)
- **450 items remain NULL** (95.9%)

### Moderate (Tier 1 + Tier 2A)
- **39-49 items linked** (8.3-10.4%)
- **420-430 items remain NULL** (89.6-91.7%)

### Optimistic (Tier 1 + Tier 2 + Tier 3)
- **60-80 items linked** (12.8-17.1%)
- **389-409 items remain NULL** (82.9-87.2%)

### Realistic (After addressing architecture issues)
- **Tier 1-3 vehicles**: 60-80 items (12.8-17.1%)
- **Add ref_gun_id**: +50-70 guns (10.7-14.9%)
- **Total**: 110-150 items (23.5-32.0%)
- **Remaining NULL**: 319-359 items (68.0-76.5%)
  - Aircraft: 62 (no BG tables)
  - Trucks/Support: 92 (limited BG coverage)
  - Missing refs: 165-205

---

## Recommendations for Approval

1. **Execute Tier 1 immediately** (19 items, 100% confidence, zero risk)
2. **Develop Tier 2 Python script** (estimate: +20-30 items)
3. **Preview Tier 2 matches** for approval before UPDATE
4. **Hold Tier 3** for future session (requires variant preference logic)
5. **Address architecture** - add reference_gun_id column

**Awaiting approval to proceed with Tier 1 execution.**
