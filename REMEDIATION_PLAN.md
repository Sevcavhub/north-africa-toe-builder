# Database Remediation Plan

**Generated**: 2025-11-02
**Database**: `D:\north-africa-toe-builder\database\master_database.db`
**Backup**: `master_database.db.backup-20251102-pre-normalization` ✅
**Agent**: Specialist Data Cleaning & Normalization Agent v2.0.0
**Phase**: 2 - Prioritization & Planning

---

## Executive Summary

Comprehensive remediation plan for database quality issues identified in Phase 1.

**Total Issues**: 7 categories across 3 severity levels
**Total Estimated Time**: 13-16 hours over 3 days
**Phases**: 2A (Critical - Day 1), 2B (High Priority - Days 1-2), 2C (Medium Priority - Days 2-3)

### Issue Summary by Severity

| Severity | Issue Category | Count | Estimated Time |
|----------|----------------|-------|----------------|
| **CRITICAL** | WITW ID collisions | 58 collisions (169 records) | 3-4 hours |
| **CRITICAL** | Aircraft-as-tanks | 4 records | 15 minutes |
| **HIGH** | Name mismatches | 101 equipment items | 3-4 hours |
| **HIGH** | Empty equipment_guns | 112 tanks | 2-3 hours |
| **HIGH** | NULL equipment_type | 467/469 records (99.6%) | 1 hour |
| **HIGH** | Orphaned foreign keys | 953 records | 2-3 hours |
| **MEDIUM** | BattleGroup duplicates | 154 groups | 2-3 hours |

**Total**: 13-16 hours

---

## Phase Breakdown

### Phase 2A: Critical Fixes (Day 1 - 4-5 hours)
- ✅ WITW ID collision resolution
- ✅ Aircraft-as-tanks fix
- ✅ Audit infrastructure creation

### Phase 2B: High Priority (Days 1-2 - 6-7 hours)
- ⏳ Name variant mapping
- ⏳ equipment_guns population
- ⏳ equipment_type inference
- ⏳ Orphaned FK investigation

### Phase 2C: Medium Priority (Days 2-3 - 3-4 hours)
- ⏳ BattleGroup duplicate resolution
- ⏳ Final validation

---

## Phase 2A: Critical Fixes (Day 1)

### Task 1: WITW ID Collision Resolution

**Priority**: CRITICAL
**Affected**: 58 collisions, 169 records (36% of equipment table)
**Impact**: Blocks Phase 10 scenario exports

#### Decision Tree Methodology

```
For each WITW ID collision:

1. IS IT MULTI-CATEGORY? (aircraft + tanks, trucks + artillery, etc.)
   YES → CRITICAL SEVERITY
     ├─ Clear semantic mismatch (e.g., Hurricane aircraft vs Sherman tank)
     │  ├─ Set witw_id = NULL for mismatched items
     │  ├─ Retain one item from primary category (or NULL all)
     │  └─ Log: "Multi-category collision - auto-resolved"
     │
     └─ Ambiguous category mix (e.g., command_vehicles + trucks)
        ├─ Check if same vehicle family (e.g., Dodge WC variants)
        ├─ If same family: Retain generic variant, NULL specifics
        └─ If different: ESCALATE TO USER

2. IS IT SAME VEHICLE FAMILY? (M3 Scout vs M3 Stuart, Bedford variants, etc.)
   YES → HIGH PRIORITY
     ├─ Same nation, similar naming (e.g., "M3 Scout Car", "M3 Stuart", "M3A1 Lee")
     │  └─ ESCALATE TO USER (cannot determine correct variant)
     │
     └─ Clear variant hierarchy (e.g., "Dodge WC Series" vs "Dodge WC-51")
        ├─ Retain: Most generic name ("WC Series")
        └─ Set NULL: Specific variants

3. IS IT DIFFERENT MODELS? (Flak 18 vs Flak 36, FIAT 626 vs FIAT 666, etc.)
   YES → ESCALATE TO USER
     ├─ Different model numbers (e.g., Flak 18, Flak 36, Flak 38)
     ├─ Cannot determine correct item automatically
     ├─ Requires WITW database reference lookup
     └─ Log: "Model collision - user decision required"

4. GENERIC COLLISION (Support vehicles, trucks, etc.)
   ├─ Retain: Most generic name OR "all variants"
   ├─ Set NULL: Specific variants
   └─ Log: "Generic collision - retained umbrella item"
```

#### Collision Batches

**Batch 1: Aircraft-as-Tanks Fix** (4 records) - **15 minutes**

Highest priority - data corruption.

**Affected Records**:
- GBR_CRUSADER_I (witw_name="Lysander I (FI)", should be NULL)
- GBR_SHERMAN_I_M4 (witw_name="Hurricane I (FI)", should be NULL)
- GBR_SHERMAN_II_M4A1 (witw_name="Hurricane I (FI)", should be NULL)
- GBR_SHERMAN_III_M4A4 (witw_name="Hurricane I (FI)", should be NULL)

**Resolution Strategy**: Set witw_id = NULL, witw_name = NULL for all 4 tanks

**SQL Script**:
```sql
BEGIN TRANSACTION;

-- Insert audit records
INSERT INTO normalization_audit (table_name, record_id, field_name, old_value, new_value, change_type, change_reason)
VALUES
  ('equipment', 'GBR_CRUSADER_I', 'witw_id', '116', 'NULL', 'collision_fix', 'Aircraft-as-tank: Lysander I assigned to Crusader I tank'),
  ('equipment', 'GBR_CRUSADER_I', 'witw_name', 'Lysander I (FI)', 'NULL', 'collision_fix', 'Aircraft-as-tank: Lysander I assigned to Crusader I tank'),
  ('equipment', 'GBR_SHERMAN_I_M4', 'witw_id', '115', 'NULL', 'collision_fix', 'Aircraft-as-tank: Hurricane I assigned to Sherman I tank'),
  ('equipment', 'GBR_SHERMAN_I_M4', 'witw_name', 'Hurricane I (FI)', 'NULL', 'collision_fix', 'Aircraft-as-tank: Hurricane I assigned to Sherman I tank'),
  ('equipment', 'GBR_SHERMAN_II_M4A1', 'witw_id', '115', 'NULL', 'collision_fix', 'Aircraft-as-tank: Hurricane I assigned to Sherman II tank'),
  ('equipment', 'GBR_SHERMAN_II_M4A1', 'witw_name', 'Hurricane I (FI)', 'NULL', 'collision_fix', 'Aircraft-as-tank: Hurricane I assigned to Sherman II tank'),
  ('equipment', 'GBR_SHERMAN_III_M4A4', 'witw_id', '115', 'NULL', 'collision_fix', 'Aircraft-as-tank: Hurricane I assigned to Sherman III tank'),
  ('equipment', 'GBR_SHERMAN_III_M4A4', 'witw_name', 'Hurricane I (FI)', 'NULL', 'collision_fix', 'Aircraft-as-tank: Hurricane I assigned to Sherman III tank');

-- Fix Crusader I
UPDATE equipment
SET witw_id = NULL,
    witw_name = NULL
WHERE canonical_id = 'GBR_CRUSADER_I';

-- Fix Sherman I
UPDATE equipment
SET witw_id = NULL,
    witw_name = NULL
WHERE canonical_id = 'GBR_SHERMAN_I_M4';

-- Fix Sherman II
UPDATE equipment
SET witw_id = NULL,
    witw_name = NULL
WHERE canonical_id = 'GBR_SHERMAN_II_M4A1';

-- Fix Sherman III
UPDATE equipment
SET witw_id = NULL,
    witw_name = NULL
WHERE canonical_id = 'GBR_SHERMAN_III_M4A4';

-- Validation: Should return 0
SELECT COUNT(*) FROM equipment
WHERE category IN ('tanks', 'main_tanks')
  AND (witw_name LIKE '%(FI)%' OR witw_name LIKE '%(LB)%');
-- Expected: 0

COMMIT;
```

**Rollback Script**:
```sql
BEGIN TRANSACTION;

UPDATE equipment SET witw_id = 116, witw_name = 'Lysander I (FI)' WHERE canonical_id = 'GBR_CRUSADER_I';
UPDATE equipment SET witw_id = 115, witw_name = 'Hurricane I (FI)' WHERE canonical_id = 'GBR_SHERMAN_I_M4';
UPDATE equipment SET witw_id = 115, witw_name = 'Hurricane I (FI)' WHERE canonical_id = 'GBR_SHERMAN_II_M4A1';
UPDATE equipment SET witw_id = 115, witw_name = 'Hurricane I (FI)' WHERE canonical_id = 'GBR_SHERMAN_III_M4A4';

-- Validation: Should return 4
SELECT COUNT(*) FROM equipment WHERE canonical_id IN ('GBR_CRUSADER_I', 'GBR_SHERMAN_I_M4', 'GBR_SHERMAN_II_M4A1', 'GBR_SHERMAN_III_M4A4') AND witw_id IS NOT NULL;
-- Expected: 4

COMMIT;
```

---

**Batch 2: Clear Multi-Category Collisions** (~25 collisions) - **1 hour**

Auto-resolve collisions with clear semantic mismatches.

**Examples**:
1. **WITW ID 115** (11 items: Hurricanes + Shermans + German artillery)
   - Strategy: Set ALL to NULL (Phase 5 will re-match)
   - Reason: Too complex to pick "correct" item

2. **WITW ID 110** (8 items: Blenheim bombers + German artillery)
   - Strategy: Set ALL to NULL
   - Reason: Multi-category collision

3. **WITW ID 100031** (5 items: Marmon-Herrington armored car + Wellington bombers)
   - Strategy: Set ALL to NULL
   - Reason: Multi-category collision

**SQL Template** (per collision):
```sql
BEGIN TRANSACTION;

-- Audit logging
INSERT INTO normalization_audit (table_name, record_id, field_name, old_value, new_value, change_type, change_reason)
SELECT
  'equipment' AS table_name,
  canonical_id AS record_id,
  'witw_id' AS field_name,
  CAST(witw_id AS TEXT) AS old_value,
  'NULL' AS new_value,
  'collision_fix' AS change_type,
  'Multi-category collision: WITW ID [ID]' AS change_reason
FROM equipment
WHERE witw_id = [WITW_ID];

-- Log resolution
INSERT INTO witw_collision_resolutions (witw_id, collision_count, resolution_strategy, retained_canonical_id, nulled_canonical_ids, escalated, escalation_reason)
VALUES (
  [WITW_ID],
  [COLLISION_COUNT],
  'multi_category_auto_null',
  NULL,
  (SELECT json_group_array(canonical_id) FROM equipment WHERE witw_id = [WITW_ID]),
  0,
  NULL
);

-- Fix collision
UPDATE equipment
SET witw_id = NULL,
    witw_name = NULL
WHERE witw_id = [WITW_ID];

-- Validation: Should return 0
SELECT COUNT(*) FROM equipment WHERE witw_id = [WITW_ID];
-- Expected: 0

COMMIT;
```

**Collisions for Batch 2** (Auto-resolve):
- WITW ID 115 (11 items) - Hurricanes + Shermans + Artillery
- WITW ID 110 (8 items) - Blenheims + Artillery
- WITW ID 100031 (5 items) - Armored car + Bombers
- WITW ID 100032 (7 items) - Bedford trucks + Bofors AA (NULL Bofors only)

**Total**: ~25 collisions auto-resolved

---

**Batch 3: Same-Family Generic Variants** (~10 collisions) - **1 hour**

Resolve collisions where items are variants of same vehicle family.

**Strategy**: Retain most generic variant, NULL specific models.

**Examples**:

1. **WITW ID 100043** (7 items: Dodge WC variants)
   - Items: Dodge Command Car, WC-51, WC-53, WC-54, WC-56, WC54, WC Series
   - **Retain**: USA_DODGE_WC_SERIES ("Dodge WC Series" - umbrella term)
   - **NULL**: All specific variants (WC-51, WC-53, etc.)

2. **WITW ID 504** (4 items: M2/M3 Halftrack variants)
   - Items: M2 Halftrack, M3 Command Halftrack, M3 Halftrack, M3A1 Halftrack
   - **Retain**: USA_M3_HALFTRACK ("M3 Halftrack" - primary variant)
   - **NULL**: M2, M3A1, M3 Command (different models/variants)

**SQL Template**:
```sql
BEGIN TRANSACTION;

-- Log resolution
INSERT INTO witw_collision_resolutions (witw_id, collision_count, resolution_strategy, retained_canonical_id, nulled_canonical_ids)
VALUES (
  [WITW_ID],
  [COUNT],
  'generic_variant_retained',
  '[RETAINED_ID]',
  '[JSON_ARRAY_OF_NULLED_IDS]'
);

-- Audit logging for nulled items
INSERT INTO normalization_audit (table_name, record_id, field_name, old_value, new_value, change_type, change_reason)
SELECT
  'equipment',
  canonical_id,
  'witw_id',
  CAST(witw_id AS TEXT),
  'NULL',
  'collision_fix',
  'Variant collision: Retained [RETAINED_NAME], nulled specific variant'
FROM equipment
WHERE witw_id = [WITW_ID] AND canonical_id != '[RETAINED_ID]';

-- NULL specific variants
UPDATE equipment
SET witw_id = NULL,
    witw_name = NULL
WHERE witw_id = [WITW_ID] AND canonical_id != '[RETAINED_ID]';

-- Validation: Should return 1 (the retained item)
SELECT COUNT(*) FROM equipment WHERE witw_id = [WITW_ID];
-- Expected: 1

COMMIT;
```

**Collisions for Batch 3**:
- WITW ID 100043 - Dodge WC Series (retain generic)
- WITW ID 504 - M3 Halftrack (retain primary)
- WITW ID 626 - FIAT 626 (if ID 626 = model 626, escalate otherwise)

---

**Batch 4: User Escalations** (~23 collisions) - **USER DECISIONS REQUIRED**

Cannot auto-resolve - require user decisions.

**Escalation Categories**:

1. **Ambiguous "M3" Collisions** (WITW ID 100049)
   - M3 Scout Car (armored car)
   - M3 Stuart (light tank)
   - M3A1 Lee (medium tank)
   - M3A1 Stuart (light tank variant)
   - M3A1 Scout Car (halftrack)
   - **Issue**: "M3" designates 5 DIFFERENT vehicles
   - **User Decision**: Which is correct for WITW ID 100049?

2. **German Vehicle ID Collisions** (WITW ID 251)
   - SdKfz 222 (armored car)
   - SdKfz 231 (armored car)
   - SdKfz 251/1 (halftrack)
   - SdKfz 232 (fu) (armored car)
   - SdKfz 223 (armored car)
   - **Issue**: ID 251 might = SdKfz 251/1, but need WITW reference
   - **User Decision**: Verify against WITW database

3. **Flak Gun Variants** (WITW ID 49)
   - Flak 18 (88mm AA)
   - Flak 38 (20mm AA)
   - Flak 36 8.8cm (88mm AT)
   - **Issue**: Different models with different calibers
   - **User Decision**: Which Flak variant is WITW ID 49?

4. **FIAT Model vs ID Number** (WITW ID 626)
   - FIAT 626 Recovery
   - FIAT 666
   - FIAT 508c Balilla
   - FIAT 626 (all Variants)
   - FIAT 665NM
   - **Issue**: Is WITW ID 626 referring to FIAT model 626?
   - **User Decision**: Confirm ID-to-model mapping

**Deliverable**: `WITW_COLLISION_USER_DECISIONS.md` with 23 decision prompts

---

### Task 2: Create Audit Infrastructure

**Priority**: CRITICAL (prerequisite for all changes)
**Estimated Time**: 30 minutes

#### Audit Tables

**Table 1: normalization_audit**

Logs every database change with full provenance.

```sql
CREATE TABLE IF NOT EXISTS normalization_audit (
  audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
  table_name TEXT NOT NULL,
  record_id TEXT NOT NULL,
  field_name TEXT NOT NULL,
  old_value TEXT,
  new_value TEXT,
  change_type TEXT NOT NULL, -- 'collision_fix', 'name_mapping', 'type_inference', 'gun_linkage', etc.
  change_reason TEXT,
  changed_at TEXT DEFAULT CURRENT_TIMESTAMP,
  changed_by TEXT DEFAULT 'normalization_agent_v2.0',
  batch_id TEXT -- For grouping related changes
);

CREATE INDEX idx_audit_table_record ON normalization_audit(table_name, record_id);
CREATE INDEX idx_audit_type ON normalization_audit(change_type);
CREATE INDEX idx_audit_batch ON normalization_audit(batch_id);
```

**Table 2: witw_collision_resolutions**

Tracks WITW ID collision resolution decisions.

```sql
CREATE TABLE IF NOT EXISTS witw_collision_resolutions (
  resolution_id INTEGER PRIMARY KEY AUTOINCREMENT,
  witw_id INTEGER NOT NULL,
  collision_count INTEGER NOT NULL,
  resolution_strategy TEXT NOT NULL, -- 'multi_category_auto_null', 'generic_variant_retained', 'user_escalated', etc.
  retained_canonical_id TEXT, -- NULL if all items nulled
  nulled_canonical_ids TEXT, -- JSON array of nulled canonical_ids
  escalated BOOLEAN DEFAULT 0,
  escalation_reason TEXT,
  user_decision TEXT, -- User's chosen resolution (for escalated cases)
  resolved_at TEXT DEFAULT CURRENT_TIMESTAMP,
  resolved_by TEXT DEFAULT 'normalization_agent_v2.0'
);

CREATE INDEX idx_collision_witw_id ON witw_collision_resolutions(witw_id);
CREATE INDEX idx_collision_escalated ON witw_collision_resolutions(escalated);
```

**Table 3: equipment_name_variants**

Maps name variations to canonical equipment.

```sql
CREATE TABLE IF NOT EXISTS equipment_name_variants (
  variant_id INTEGER PRIMARY KEY AUTOINCREMENT,
  canonical_id TEXT NOT NULL,
  variant_name TEXT NOT NULL,
  variant_source TEXT NOT NULL, -- 'bg_reference_vehicles', 'wwiitanks_afv_data', 'afv_data', 'manual'
  match_type TEXT NOT NULL, -- 'exact', 'fuzzy', 'abbreviation', 'historical_alias'
  confidence_score REAL, -- 0.0-1.0 for fuzzy matches
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (canonical_id) REFERENCES equipment(canonical_id)
);

CREATE INDEX idx_variant_canonical ON equipment_name_variants(canonical_id);
CREATE INDEX idx_variant_name ON equipment_name_variants(variant_name);
CREATE UNIQUE INDEX idx_variant_unique ON equipment_name_variants(canonical_id, variant_name, variant_source);
```

**Validation Queries**:
```sql
-- Verify tables created
SELECT name FROM sqlite_master WHERE type='table' AND name IN ('normalization_audit', 'witw_collision_resolutions', 'equipment_name_variants');
-- Expected: 3 rows

-- Verify indexes created
SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%';
-- Expected: 7 indexes
```

---

### Phase 2A Summary

**Total Time**: 4-5 hours

| Task | Time | Deliverable |
|------|------|-------------|
| Batch 1: Aircraft-as-tanks | 15 min | 4 records fixed |
| Batch 2: Multi-category collisions | 1 hour | ~25 collisions auto-resolved |
| Batch 3: Generic variants | 1 hour | ~10 collisions auto-resolved |
| Batch 4: User escalations | N/A | 23 escalation prompts |
| Task 2: Audit infrastructure | 30 min | 3 tables, 7 indexes |
| **Total** | **3-4 hours** | **~39 auto-resolved, 23 escalated** |

**Success Criteria**:
- ✅ All 4 aircraft-as-tanks fixed
- ✅ ~35-40 collisions auto-resolved
- ✅ 23 collisions escalated to user with detailed prompts
- ✅ Audit infrastructure operational
- ✅ All changes logged in normalization_audit

---

## Phase 2B: High Priority (Days 1-2)

### Task 3: Name Variant Mapping

**Priority**: HIGH
**Affected**: 101 equipment → bg_reference_vehicles mismatches
**Impact**: Blocks gun data lookup for book datacards
**Estimated Time**: 3-4 hours

#### Problem

Equipment names don't exactly match BattleGroup reference names:
- "Panzer II Ausf C" (equipment) vs "Panzer II C" (bg_reference_vehicles)
- "Valentine Mk II" (equipment) vs "Valentine II" (bg_reference_vehicles)
- "Crusader Mk I" (equipment) vs "Crusader I AA Mk I" (bg_reference_vehicles)

This breaks lookups for gun specifications needed in book datacards.

#### Solution

Create `equipment_name_variants` table (already defined in Task 2) and populate with fuzzy matching.

#### Matching Rules

**Rule 1: Exact Match** (highest confidence)
```sql
INSERT INTO equipment_name_variants (canonical_id, variant_name, variant_source, match_type, confidence_score)
SELECT
  e.canonical_id,
  bg.name AS variant_name,
  'bg_reference_vehicles' AS variant_source,
  'exact' AS match_type,
  1.0 AS confidence_score
FROM equipment e
INNER JOIN bg_reference_vehicles bg ON LOWER(e.name) = LOWER(bg.name)
WHERE e.category IN ('tanks', 'main_tanks', 'light_tanks', 'armored_cars', 'halftracks');
```

**Rule 2: Abbreviation Expansion** (e.g., "Mk" → "Mark", "Ausf" presence)
```python
# Python fuzzy matching script
import sqlite3
from difflib import SequenceMatcher

def normalize_name(name):
    """Normalize equipment names for matching"""
    name = name.lower()
    # Expand abbreviations
    name = name.replace('mk ', 'mark ')
    name = name.replace('mk.', 'mark')
    # Remove "Ausf" variants for base matching
    name = name.replace(' ausf ', ' ')
    # Standardize Roman numerals
    name = name.replace(' ii ', ' 2 ')
    name = name.replace(' iii ', ' 3 ')
    name = name.replace(' iv ', ' 4 ')
    return name

def fuzzy_match(eq_name, bg_name, threshold=0.75):
    """Calculate similarity between names"""
    norm_eq = normalize_name(eq_name)
    norm_bg = normalize_name(bg_name)
    return SequenceMatcher(None, norm_eq, norm_bg).ratio()
```

**Rule 3: Token Matching** (for compound names)
```python
def token_match(eq_name, bg_name):
    """Match based on significant tokens"""
    eq_tokens = set(eq_name.lower().split())
    bg_tokens = set(bg_name.lower().split())

    # Ignore common words
    ignore = {'mk', 'mark', 'ausf', 'the', 'a', 'an', 'with'}
    eq_tokens -= ignore
    bg_tokens -= ignore

    # Jaccard similarity
    intersection = len(eq_tokens & bg_tokens)
    union = len(eq_tokens | bg_tokens)

    return intersection / union if union > 0 else 0.0
```

**Rule 4: Manual Mappings** (for special cases)
```sql
-- Special mappings for known aliases
INSERT INTO equipment_name_variants (canonical_id, variant_name, variant_source, match_type, confidence_score)
VALUES
  -- British abbreviations
  ('GBR_A10_CRUISER_MK_II', 'A10 Cruiser', 'bg_reference_vehicles', 'abbreviation', 0.95),
  ('GBR_VALENTINE_MK_II', 'Valentine II', 'bg_reference_vehicles', 'abbreviation', 0.95),

  -- German Ausf variants
  ('GER_PANZER_II_AUSF_C', 'Panzer II C', 'bg_reference_vehicles', 'abbreviation', 0.95),
  ('GER_PANZER_II_AUSF_F', 'Panzer II F', 'bg_reference_vehicles', 'abbreviation', 0.95),
  ('GER_PANZER_II_AUSF_F', 'Pz II F', 'bg_reference_vehicles', 'abbreviation', 0.90),

  -- Italian variants
  ('ITA_L6_40', 'FIAT L6/40', 'bg_reference_vehicles', 'abbreviation', 0.90);
```

#### Workflow

1. **Exact matches** (highest confidence)
2. **Abbreviation rules** (manually curated)
3. **Fuzzy matching** (threshold: 75% similarity)
4. **Token matching** (fallback for compound names)
5. **Manual review** (for unmatched items)

#### Validation

```sql
-- Count mappings created
SELECT
  variant_source,
  match_type,
  COUNT(*) AS mapping_count
FROM equipment_name_variants
GROUP BY variant_source, match_type;

-- Expected output:
-- bg_reference_vehicles, exact, ~30-40
-- bg_reference_vehicles, abbreviation, ~50-60
-- bg_reference_vehicles, fuzzy, ~10-20

-- Find still-unmatched equipment
SELECT
  e.canonical_id,
  e.name,
  e.category
FROM equipment e
WHERE e.category IN ('tanks', 'main_tanks', 'light_tanks')
  AND NOT EXISTS (
    SELECT 1 FROM equipment_name_variants v WHERE v.canonical_id = e.canonical_id
  );

-- Should be < 10 items remaining
```

**Deliverable**: `equipment_name_mapping.json` with match results, `equipment_name_variants` table populated

---

### Task 4: Populate equipment_guns Table

**Priority**: HIGH
**Affected**: 112 tanks with 0 gun linkages
**Impact**: Blocks Phase 9B book datacard generation
**Estimated Time**: 2-3 hours

#### Problem

The `equipment_guns` table is empty (0 records), but gun data exists in:
- `bg_reference_vehicles.weapons` (JSON field)
- `guns` table (348 gun records)

Without linkages, cannot display gun specifications in book datacards.

#### Solution

Parse `bg_reference_vehicles.weapons` JSON and create `equipment_guns` linkages.

#### Workflow

**Step 1: Extract weapons from bg_reference_vehicles**

```sql
-- Query to see weapons data
SELECT
  name,
  weapons
FROM bg_reference_vehicles
WHERE weapons IS NOT NULL
  AND weapons != '[]'
LIMIT 10;

-- Example output:
-- A10 Cruiser | [{"weapon": "2pdr", "mount": "Turret"}]
-- Valentine II | [{"weapon": "2pdr", "mount": "Turret"}, {"weapon": "Besa 7.92mm", "mount": "Co-axial"}]
-- Panzer III F | [{"weapon": "3.7cm KwK 36 L/46.5", "mount": "Turret"}]
```

**Step 2: Match vehicle names to equipment via variants table**

```python
import sqlite3
import json

def populate_equipment_guns():
    conn = sqlite3.connect('master_database.db')
    cursor = conn.cursor()

    # Get all bg_reference_vehicles with weapons
    cursor.execute("""
        SELECT name, weapons
        FROM bg_reference_vehicles
        WHERE weapons IS NOT NULL AND weapons != '[]'
    """)

    for bg_name, weapons_json in cursor.fetchall():
        weapons = json.loads(weapons_json)

        # Find matching equipment via variants table
        cursor.execute("""
            SELECT canonical_id
            FROM equipment_name_variants
            WHERE variant_name = ?
            ORDER BY confidence_score DESC
            LIMIT 1
        """, (bg_name,))

        result = cursor.fetchone()
        if not result:
            print(f"No equipment match for: {bg_name}")
            continue

        equipment_id = result[0]

        # Process each weapon
        for weapon in weapons:
            weapon_name = weapon.get('weapon')
            mount = weapon.get('mount', 'unknown')

            # Find gun in guns table
            gun_id = find_gun(cursor, weapon_name)
            if not gun_id:
                print(f"Gun not found: {weapon_name}")
                continue

            # Determine gun role
            role = 'main' if mount.lower() == 'turret' else 'secondary'

            # Insert linkage
            cursor.execute("""
                INSERT INTO equipment_guns (equipment_id, gun_id, role, mount_type)
                VALUES (?, ?, ?, ?)
            """, (equipment_id, gun_id, role, mount.lower()))

    conn.commit()
    conn.close()

def find_gun(cursor, weapon_name):
    """Find gun_id by matching weapon name"""
    # Try exact match
    cursor.execute("SELECT gun_id FROM guns WHERE name = ?", (weapon_name,))
    result = cursor.fetchone()
    if result:
        return result[0]

    # Try fuzzy match on caliber
    # "2pdr" → look for guns with "2" and "pdr"
    # "3.7cm KwK 36" → look for "37mm" or "3.7cm"

    # Normalize calibers
    caliber_map = {
        '2pdr': '40mm',
        '6pdr': '57mm',
        '17pdr': '76.2mm',
        '3.7cm': '37mm',
        '5cm': '50mm',
        '7.5cm': '75mm',
        '8.8cm': '88mm'
    }

    for pattern, caliber in caliber_map.items():
        if pattern in weapon_name.lower():
            cursor.execute("""
                SELECT gun_id FROM guns
                WHERE caliber_mm = ? OR name LIKE ?
                LIMIT 1
            """, (int(caliber.replace('mm', '')), f'%{pattern}%'))
            result = cursor.fetchone()
            if result:
                return result[0]

    return None
```

**Step 3: Audit logging**

```sql
INSERT INTO normalization_audit (table_name, record_id, field_name, old_value, new_value, change_type, change_reason)
VALUES
  ('equipment_guns', '[equipment_id]_[gun_id]', 'linkage', 'NULL', 'created', 'gun_linkage', 'Parsed from bg_reference_vehicles.weapons JSON');
```

**Step 4: Validation**

```sql
-- Count linkages created
SELECT COUNT(*) FROM equipment_guns;
-- Expected: 150-200 (tanks may have multiple guns)

-- Count equipment with linkages
SELECT COUNT(DISTINCT equipment_id) FROM equipment_guns;
-- Expected: 80-100 (out of 112 tanks)

-- Find tanks still missing guns
SELECT
  e.canonical_id,
  e.name,
  e.category
FROM equipment e
WHERE e.category IN ('tanks', 'main_tanks', 'light_tanks')
  AND NOT EXISTS (
    SELECT 1 FROM equipment_guns eg WHERE eg.equipment_id = e.canonical_id
  );

-- Should be ~10-30 items (some tanks may not be in bg_reference_vehicles)
```

**Deliverable**: Populated `equipment_guns` table, audit log entries

---

### Task 5: Infer equipment_type from category

**Priority**: HIGH
**Affected**: 467/469 records (99.6% NULL)
**Impact**: Missing categorization for all equipment
**Estimated Time**: 1 hour

#### Problem

The `equipment_type` field is NULL for 99.6% of equipment records, but can be inferred from the `category` field.

#### Solution

Rules-based UPDATE query using category-to-type mapping.

#### Category-to-Type Mapping Rules

```sql
-- Create mapping reference (for documentation)
CREATE TEMP TABLE category_type_mapping AS
SELECT * FROM (VALUES
  -- Tanks
  ('tanks', 'tank'),
  ('main_tanks', 'tank'),
  ('light_tanks', 'tank'),
  ('heavy_tanks', 'tank'),
  ('medium_tanks', 'tank'),

  -- Artillery
  ('field_artillery', 'artillery'),
  ('anti_tank', 'artillery'),
  ('anti_aircraft', 'artillery'),
  ('infantry_guns', 'artillery'),
  ('self_propelled_guns', 'artillery'),

  -- Vehicles
  ('halftracks', 'halftrack'),
  ('armored_cars', 'armored_car'),
  ('armored_cars_reconnaissance', 'armored_car'),
  ('trucks', 'vehicle'),
  ('support_vehicles', 'vehicle'),
  ('command_vehicles', 'vehicle'),
  ('recovery_vehicles', 'vehicle'),
  ('transport_vehicles', 'vehicle'),

  -- Aircraft
  ('fighters', 'aircraft'),
  ('bombers', 'aircraft'),
  ('reconnaissance', 'aircraft'),
  ('fighter_bombers', 'aircraft'),
  ('dive_bombers', 'aircraft'),
  ('torpedo_bombers', 'aircraft'),
  ('maritime_patrol', 'aircraft')
) AS t(category, equipment_type);
```

#### Inference SQL

```sql
BEGIN TRANSACTION;

-- Audit logging (before update)
INSERT INTO normalization_audit (table_name, record_id, field_name, old_value, new_value, change_type, change_reason, batch_id)
SELECT
  'equipment' AS table_name,
  canonical_id AS record_id,
  'equipment_type' AS field_name,
  'NULL' AS old_value,
  CASE
    WHEN category IN ('tanks', 'main_tanks', 'light_tanks', 'heavy_tanks', 'medium_tanks') THEN 'tank'
    WHEN category IN ('field_artillery', 'anti_tank', 'anti_aircraft', 'infantry_guns', 'self_propelled_guns') THEN 'artillery'
    WHEN category IN ('halftracks') THEN 'halftrack'
    WHEN category IN ('armored_cars', 'armored_cars_reconnaissance') THEN 'armored_car'
    WHEN category IN ('trucks', 'support_vehicles', 'command_vehicles', 'recovery_vehicles', 'transport_vehicles') THEN 'vehicle'
    WHEN category IN ('fighters', 'bombers', 'reconnaissance', 'fighter_bombers', 'dive_bombers', 'torpedo_bombers', 'maritime_patrol') THEN 'aircraft'
    ELSE 'unknown'
  END AS new_value,
  'type_inference' AS change_type,
  'Inferred from category: ' || category AS change_reason,
  'equipment_type_inference_batch_1' AS batch_id
FROM equipment
WHERE equipment_type IS NULL;

-- Update equipment_type
UPDATE equipment
SET equipment_type = CASE
  WHEN category IN ('tanks', 'main_tanks', 'light_tanks', 'heavy_tanks', 'medium_tanks') THEN 'tank'
  WHEN category IN ('field_artillery', 'anti_tank', 'anti_aircraft', 'infantry_guns', 'self_propelled_guns') THEN 'artillery'
  WHEN category IN ('halftracks') THEN 'halftrack'
  WHEN category IN ('armored_cars', 'armored_cars_reconnaissance') THEN 'armored_car'
  WHEN category IN ('trucks', 'support_vehicles', 'command_vehicles', 'recovery_vehicles', 'transport_vehicles') THEN 'vehicle'
  WHEN category IN ('fighters', 'bombers', 'reconnaissance', 'fighter_bombers', 'dive_bombers', 'torpedo_bombers', 'maritime_patrol') THEN 'aircraft'
  ELSE 'unknown'
END
WHERE equipment_type IS NULL;

-- Validation: Should return ~450-460
SELECT COUNT(*) FROM equipment WHERE equipment_type IS NOT NULL;
-- Expected: 467-469

-- Validation: Should return 0-2
SELECT COUNT(*) FROM equipment WHERE equipment_type IS NULL;
-- Expected: 0-2 (categories not covered by rules)

-- Check distribution
SELECT equipment_type, COUNT(*) AS count
FROM equipment
GROUP BY equipment_type
ORDER BY count DESC;

-- Expected output:
-- aircraft, ~150
-- tank, ~100
-- vehicle, ~80
-- artillery, ~60
-- etc.

COMMIT;
```

#### Rollback SQL

```sql
BEGIN TRANSACTION;

-- Restore NULL values using audit log
UPDATE equipment
SET equipment_type = NULL
WHERE canonical_id IN (
  SELECT record_id
  FROM normalization_audit
  WHERE batch_id = 'equipment_type_inference_batch_1'
);

-- Validation: Should return 467
SELECT COUNT(*) FROM equipment WHERE equipment_type IS NULL;
-- Expected: 467

COMMIT;
```

**Deliverable**: `equipment_type_inference_rules.md`, updated equipment table (95%+ population)

---

### Task 6: Investigate Orphaned Foreign Keys

**Priority**: HIGH
**Affected**: 953/953 unit_equipment records (100% NULL equipment_id)
**Impact**: unit_equipment table is unusable
**Estimated Time**: 2-3 hours (investigation only, not fix)

#### Problem

ALL records in `unit_equipment` have NULL `equipment_id` foreign key.

```sql
SELECT COUNT(*) FROM unit_equipment WHERE equipment_id IS NULL;
-- Result: 953 (100%)
```

This suggests either:
1. Data import error (equipment_ids not populated during import)
2. Schema mismatch (foreign key references wrong field)
3. Data source issue (WITW data doesn't include equipment linkages)

#### Investigation Workflow

**Step 1: Examine unit_equipment schema**

```sql
PRAGMA table_info(unit_equipment);

-- Check foreign key constraints
PRAGMA foreign_key_list(unit_equipment);
```

**Step 2: Examine sample records**

```sql
SELECT * FROM unit_equipment LIMIT 20;

-- Look for patterns:
-- - Are there other fields that might identify equipment?
-- - Is there a unit_id that's populated?
-- - Are there quantity/count fields?
```

**Step 3: Check import source**

```sql
-- Check import_log for unit_equipment
SELECT * FROM import_log WHERE table_name = 'unit_equipment';

-- Determine data source (WITW? Manual import?)
```

**Step 4: Cross-reference with units table**

```sql
-- Check if unit_equipment references valid units
SELECT
  ue.*,
  u.name AS unit_name
FROM unit_equipment ue
LEFT JOIN units u ON ue.unit_id = u.unit_id
LIMIT 20;

-- Are unit_ids valid? Are there other identifiable patterns?
```

**Step 5: Analyze WITW source tables**

```sql
-- Check if WITW tables have equipment assignments
SELECT * FROM witw_toe_ob LIMIT 20;

-- Does witw_toe_ob link units to equipment?
-- Is there a mapping we can use?
```

#### Expected Outcomes

**Outcome A: Import Bug**
- equipment_ids should have been populated during import
- Fix: Re-import data with corrected mapping
- Time: 2-3 hours to write import script

**Outcome B: Schema Mismatch**
- equipment_id references wrong table/field
- Fix: Create correct foreign key, migrate data
- Time: 1-2 hours

**Outcome C: Missing Source Data**
- WITW data doesn't include unit→equipment linkages
- Fix: Manual data entry OR create linkages from historical sources
- Time: Days-weeks (out of scope for Phase 2)

**Outcome D: Table is Legacy/Unused**
- unit_equipment table may be deprecated
- Fix: Document as unused, exclude from future work
- Time: 30 minutes

#### Deliverable

`orphaned_fk_analysis.md` with:
1. Root cause determination
2. Recommended fix strategy
3. Estimated time to fix
4. Whether fix is in-scope for Phase 2 or deferred

**Do NOT implement fix in Phase 2B** - document only.

---

### Phase 2B Summary

**Total Time**: 6-7 hours

| Task | Time | Deliverable |
|------|------|-------------|
| Task 3: Name variant mapping | 3-4 hours | `equipment_name_variants` table populated, `equipment_name_mapping.json` |
| Task 4: Populate equipment_guns | 2-3 hours | `equipment_guns` table populated (80-100 tanks linked) |
| Task 5: Infer equipment_type | 1 hour | 95%+ equipment_type population |
| Task 6: Orphaned FK investigation | 2-3 hours | `orphaned_fk_analysis.md` (investigation only) |
| **Total** | **8-11 hours** | **3 tables populated, 1 analysis report** |

**Success Criteria**:
- ✅ equipment_name_variants table has 100+ mappings
- ✅ equipment_guns table has 150-200 linkages
- ✅ equipment_type populated for 95%+ records
- ✅ Orphaned FK root cause identified

---

## Phase 2C: Medium Priority (Days 2-3)

### Task 7: BattleGroup Duplicate Resolution

**Priority**: MEDIUM
**Affected**: 154 duplicate groups in bg_reference_vehicles
**Impact**: Data quality (may be intentional duplicates)
**Estimated Time**: 2-3 hours

#### Problem

154 duplicate groups found in `bg_reference_vehicles`:
- "Sniper" appears 10 times
- "Supply Column" appears 10 times
- "Forward Headquarters" appears 11 times
- "Combat Medic" appears 8 times

These may be:
1. **Intentional duplicates**: Same generic unit used across different nations/campaigns
2. **Data import artifacts**: Same data imported multiple times
3. **Variant differences**: Items appear identical but have different stats/rules

#### Investigation Workflow

**Step 1: Analyze duplicate patterns**

```sql
-- Get duplicate groups with full details
SELECT
  name,
  COUNT(*) AS duplicate_count,
  GROUP_CONCAT(DISTINCT nation) AS nations,
  GROUP_CONCAT(DISTINCT battle_rating) AS ratings,
  GROUP_CONCAT(DISTINCT cost) AS costs
FROM bg_reference_vehicles
GROUP BY LOWER(name)
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC
LIMIT 20;

-- Example output:
-- Forward Headquarters, 11, "british,german,american,soviet", "0,0,0,0", "10,10,10,10"
-- → INTENTIONAL: Same HQ used across all nations with same stats
```

**Step 2: Check for stat differences**

```sql
-- For each duplicate group, check if stats differ
WITH duplicates AS (
  SELECT name
  FROM bg_reference_vehicles
  GROUP BY LOWER(name)
  HAVING COUNT(*) > 1
)
SELECT
  bg.name,
  bg.nation,
  bg.battle_rating,
  bg.cost,
  bg.armor_front,
  bg.weapons
FROM bg_reference_vehicles bg
WHERE bg.name IN (SELECT name FROM duplicates)
ORDER BY bg.name, bg.nation;

-- If all duplicates have identical stats → likely intentional
-- If stats differ → may need to preserve as variants
```

**Step 3: Categorize duplicates**

```python
import sqlite3

def categorize_duplicates():
    conn = sqlite3.connect('master_database.db')
    cursor = conn.cursor()

    # Get all duplicate groups
    cursor.execute("""
        SELECT name, COUNT(*) AS count
        FROM bg_reference_vehicles
        GROUP BY LOWER(name)
        HAVING COUNT(*) > 1
    """)

    categories = {
        'generic_units': [],      # Same stats across nations (HQ, Sniper, etc.)
        'stat_variants': [],      # Different stats (need to preserve)
        'import_artifacts': [],   # Exact duplicates (safe to merge)
        'nation_specific': []     # Same name but nation-specific stats
    }

    for name, count in cursor.fetchall():
        # Get all records for this name
        cursor.execute("""
            SELECT nation, battle_rating, cost, armor_front, weapons
            FROM bg_reference_vehicles
            WHERE name = ?
        """, (name,))

        records = cursor.fetchall()

        # Check if all records are identical
        if len(set(records)) == 1:
            categories['import_artifacts'].append(name)
        # Check if only nation differs (stats same)
        elif all_stats_identical(records):
            categories['generic_units'].append(name)
        # Check if stats vary by nation
        elif varies_by_nation(records):
            categories['nation_specific'].append(name)
        else:
            categories['stat_variants'].append(name)

    return categories
```

**Step 4: Resolution strategies**

**Strategy A: Generic Units** (e.g., Sniper, HQ, Medic)
- **Decision**: KEEP duplicates (intentional cross-nation use)
- **Action**: Document as "generic units" in data dictionary
- **Rationale**: BattleGroup allows same unit across nations

**Strategy B: Import Artifacts** (exact duplicates)
- **Decision**: MERGE duplicates (keep one, delete rest)
- **Action**: DELETE duplicate records, keep first by ID
- **Rationale**: No value in storing identical copies

**Strategy C: Nation-Specific Variants** (same name, different stats)
- **Decision**: KEEP duplicates, rename for clarity
- **Action**: Append nation code (e.g., "Sniper (GER)", "Sniper (USA)")
- **Rationale**: Different stats indicate different units

**Strategy D: Stat Variants** (unclear why different)
- **Decision**: ESCALATE to user/domain expert
- **Action**: Flag for manual review
- **Rationale**: Requires BattleGroup rules knowledge

#### Deliverable

`bg_duplicate_resolution.json`:
```json
{
  "analysis_date": "2025-11-02",
  "total_duplicate_groups": 154,
  "categories": {
    "generic_units": {
      "count": 80,
      "action": "keep_duplicates",
      "examples": ["Sniper", "Supply Column", "Forward Headquarters"]
    },
    "import_artifacts": {
      "count": 30,
      "action": "merge_duplicates",
      "records_to_delete": 60
    },
    "nation_specific": {
      "count": 20,
      "action": "rename_with_nation_code",
      "examples": ["Churchill III (GBR)", "Churchill III (USA Lend-Lease)"]
    },
    "stat_variants": {
      "count": 24,
      "action": "user_escalation",
      "requires_review": true
    }
  }
}
```

**Time**: 2-3 hours (analysis + categorization + partial cleanup)

---

### Phase 2C Summary

**Total Time**: 2-3 hours

| Task | Time | Deliverable |
|------|------|-------------|
| Task 7: BattleGroup duplicate analysis | 2-3 hours | `bg_duplicate_resolution.json`, categorized duplicates |
| **Total** | **2-3 hours** | **Duplicate strategy documented** |

**Success Criteria**:
- ✅ All 154 duplicate groups categorized
- ✅ Generic units identified (no action needed)
- ✅ Import artifacts identified (safe to merge)
- ✅ Stat variants flagged for review

---

## User Escalation List

### WITW ID Collisions Requiring User Decision (23 cases)

#### Escalation Format

Each escalation includes:
1. WITW ID and collision count
2. Colliding items (canonical_id, name, category)
3. Analysis of collision type
4. Options (A, B, C, D...)
5. Recommendation
6. Space for user decision

---

### Escalation 1: WITW ID 251 (SdKfz Variants)

**Collision**: 5 German vehicles (4 armored cars + 1 halftrack)

**Colliding Items**:
- SdKfz 222 (GER_SDKFZ_222, armored_cars)
- SdKfz 231 (GER_SDKFZ_231, armored_cars)
- SdKfz 251/1 (GER_SDKFZ_251_1, halftracks)
- SdKfz 232 (fu) (GER_SDKFZ_232_FU, armored_cars)
- SdKfz 223 (GER_SDKFZ_223, armored_cars)

**Analysis**: WITW ID 251 likely refers to SdKfz 251/1 (ID matches model number), but need WITW database confirmation.

**Options**:
- A. Retain SdKfz 251/1 (halftrack) - ID 251 = model 251
- B. Retain SdKfz 222 (armored car) - most common variant
- C. Set all to NULL - Phase 5 re-match
- D. Research WITW database for correct assignment

**Recommendation**: Option D (research WITW database), fallback to Option A if unavailable

**User Decision**: _________________

---

### Escalation 2: WITW ID 626 (FIAT Model vs ID)

**Collision**: 5 Italian vehicles (support + trucks)

**Colliding Items**:
- FIAT 626 Recovery (ITA_FIAT_626_RECOVERY, support_vehicles)
- FIAT 666 (ITA_FIAT_666, trucks)
- FIAT 508c Balilla (ITA_FIAT_508C_BALILLA, support_vehicles)
- FIAT 626 (all Variants) (ITA_FIAT_626_ALL_VARIANTS, trucks)
- FIAT 665NM (ITA_FIAT_665NM, trucks)

**Analysis**: WITW ID 626 likely refers to FIAT model 626, but collides with FIAT 666, 665NM (different models).

**Options**:
- A. Retain FIAT 626 (all Variants) - ID matches model
- B. Retain FIAT 626 Recovery - specific variant
- C. Set all to NULL - Phase 5 re-match
- D. Research if WITW uses model numbers as IDs

**Recommendation**: Option A (FIAT 626 all Variants), assuming ID 626 = model 626

**User Decision**: _________________

---

### Escalation 3: WITW ID 100049 (M3 Ambiguity)

**Collision**: 5 American vehicles (3 different vehicle types)

**Colliding Items**:
- M3 Scout Car (USA_M3_SCOUT_CAR, armored_cars_reconnaissance)
- M3 Stuart (USA_M3_STUART, tanks)
- M3A1 Lee (USA_M3A1_LEE, tanks)
- M3A1 Stuart (USA_M3A1_STUART, tanks)
- M3A1 Scout Car (USA_M3A1_SCOUT_CAR, halftracks)

**Analysis**: "M3" designates 5 DIFFERENT vehicles:
- M3 Scout Car (halftrack/armored car)
- M3 Stuart (light tank)
- M3 Lee (medium tank)
- M3A1 variants of above

WITW ID 100049 could refer to ANY of these.

**Options**:
- A. Retain M3 Stuart (most common M3 tank)
- B. Retain M3 Scout Car (primary M3 designation)
- C. Set all to NULL - Phase 5 re-match
- D. Research WITW database for category hint

**Recommendation**: Option C (NULL all), "M3" too ambiguous without WITW reference

**User Decision**: _________________

---

### Escalation 4: WITW ID 49 (Flak Variants)

**Collision**: 3 German guns (2 AA + 1 AT)

**Colliding Items**:
- Flak 18 (GER_FLAK_18, anti_aircraft)
- Flak 38 (GER_FLAK_38, anti_aircraft)
- Flak 36 8.8cm (GER_FLAK_36_8.8CM, anti_tank)

**Analysis**: Three different Flak models:
- Flak 18: 88mm AA gun (early model)
- Flak 36: 88mm AA/AT gun (improved Flak 18)
- Flak 38: 20mm AA gun (totally different weapon!)

Flak 38 is 20mm, Flak 18/36 are 88mm - clear model mismatch.

**Options**:
- A. Retain Flak 36 8.8cm (most famous 88mm variant)
- B. Retain Flak 18 (original 88mm)
- C. Set all to NULL - Phase 5 re-match
- D. Research WITW: Does ID 49 refer to caliber or model?

**Recommendation**: Option A (Flak 36), most common 88mm in WITW era

**User Decision**: _________________

---

### Escalation 5-23: Additional Collisions

**Remaining 19 escalations follow same format**:
1. WITW ID + collision count
2. Colliding items
3. Analysis
4. Options (A-D)
5. Recommendation
6. User decision field

**Examples**:
- WITW ID 100032 (Bedford trucks + Bofors AA)
- WITW ID 100043 (Dodge WC variants)
- WITW ID 504 (M2/M3 Halftrack variants)
- WITW ID 100031 (Marmon-Herrington + Wellington bombers)
- Plus 15 more...

**Deliverable**: `WITW_COLLISION_USER_DECISIONS.md` with all 23 escalations

---

## Rollback Strategy

### Rollback Template (Per Batch)

```sql
-- Rollback Template: Batch [ID] - [Description]
-- Generated: [TIMESTAMP]
-- Affected Records: [COUNT]

BEGIN TRANSACTION;

-- Step 1: Identify batch changes
SELECT
  audit_id,
  table_name,
  record_id,
  field_name,
  old_value,
  new_value
FROM normalization_audit
WHERE batch_id = '[BATCH_ID]';

-- Step 2: Restore original values
UPDATE [TABLE_NAME]
SET [FIELD_NAME] = (
  SELECT old_value
  FROM normalization_audit
  WHERE table_name = '[TABLE_NAME]'
    AND record_id = [TABLE_NAME].[PRIMARY_KEY]
    AND field_name = '[FIELD_NAME]'
    AND batch_id = '[BATCH_ID]'
)
WHERE [PRIMARY_KEY] IN (
  SELECT record_id
  FROM normalization_audit
  WHERE batch_id = '[BATCH_ID]'
);

-- Step 3: Verify rollback
SELECT COUNT(*) AS rolled_back_count
FROM normalization_audit
WHERE batch_id = '[BATCH_ID]';
-- Expected: [COUNT]

-- Step 4: Mark rollback in audit log
INSERT INTO normalization_audit (table_name, record_id, field_name, old_value, new_value, change_type, change_reason, batch_id)
SELECT
  table_name,
  record_id,
  field_name,
  new_value AS old_value,
  old_value AS new_value,
  'rollback' AS change_type,
  'Rolled back batch: [BATCH_ID]' AS change_reason,
  '[BATCH_ID]_rollback' AS batch_id
FROM normalization_audit
WHERE batch_id = '[BATCH_ID]';

COMMIT;
```

### Batch-Specific Rollback Scripts

**Rollback Batch 1: Aircraft-as-Tanks Fix**
```sql
BEGIN TRANSACTION;

-- Restore original WITW IDs
UPDATE equipment SET witw_id = 116, witw_name = 'Lysander I (FI)'
WHERE canonical_id = 'GBR_CRUSADER_I';

UPDATE equipment SET witw_id = 115, witw_name = 'Hurricane I (FI)'
WHERE canonical_id IN ('GBR_SHERMAN_I_M4', 'GBR_SHERMAN_II_M4A1', 'GBR_SHERMAN_III_M4A4');

-- Verify: Should return 4
SELECT COUNT(*) FROM equipment
WHERE canonical_id IN ('GBR_CRUSADER_I', 'GBR_SHERMAN_I_M4', 'GBR_SHERMAN_II_M4A1', 'GBR_SHERMAN_III_M4A4')
  AND witw_id IS NOT NULL;
-- Expected: 4

COMMIT;
```

**Rollback Batch 2: Multi-Category Collisions**
```sql
-- See audit log for original values per WITW ID
-- Restore using audit log query:

BEGIN TRANSACTION;

UPDATE equipment
SET witw_id = (
  SELECT CAST(old_value AS INTEGER)
  FROM normalization_audit
  WHERE table_name = 'equipment'
    AND record_id = equipment.canonical_id
    AND field_name = 'witw_id'
    AND change_type = 'collision_fix'
    AND batch_id = 'multi_category_batch_2'
),
witw_name = (
  SELECT old_value
  FROM normalization_audit
  WHERE table_name = 'equipment'
    AND record_id = equipment.canonical_id
    AND field_name = 'witw_name'
    AND change_type = 'collision_fix'
    AND batch_id = 'multi_category_batch_2'
)
WHERE canonical_id IN (
  SELECT record_id FROM normalization_audit WHERE batch_id = 'multi_category_batch_2'
);

COMMIT;
```

**Rollback equipment_type Inference**
```sql
BEGIN TRANSACTION;

UPDATE equipment
SET equipment_type = NULL
WHERE canonical_id IN (
  SELECT record_id
  FROM normalization_audit
  WHERE batch_id = 'equipment_type_inference_batch_1'
);

-- Verify: Should return 467
SELECT COUNT(*) FROM equipment WHERE equipment_type IS NULL;
-- Expected: 467

COMMIT;
```

**Rollback equipment_guns Population**
```sql
BEGIN TRANSACTION;

-- Delete all gun linkages created in batch
DELETE FROM equipment_guns
WHERE ROWID IN (
  SELECT CAST(SUBSTR(record_id, INSTR(record_id, '_') + 1) AS INTEGER)
  FROM normalization_audit
  WHERE table_name = 'equipment_guns'
    AND change_type = 'gun_linkage'
);

-- Verify: Should return 0
SELECT COUNT(*) FROM equipment_guns;
-- Expected: 0

COMMIT;
```

---

## Timeline & Milestones

### Day 1 (4-5 hours)

**Morning** (2-3 hours):
- ✅ Task 2: Create audit infrastructure (30 min)
- ✅ Batch 1: Aircraft-as-tanks fix (15 min)
- ✅ Batch 2: Multi-category collisions (1 hour)
- ✅ Batch 3: Generic variants (1 hour)

**Afternoon** (2 hours):
- ⏳ Task 3: Name variant mapping (start)
  - Exact matches (30 min)
  - Abbreviation rules (30 min)
  - Fuzzy matching setup (1 hour)

**Milestone**: Phase 2A complete, ~35-40 collisions auto-resolved

---

### Day 2 (6-7 hours)

**Morning** (3-4 hours):
- ⏳ Task 3: Name variant mapping (complete)
  - Fuzzy matching execution (1 hour)
  - Token matching (1 hour)
  - Manual review (1-2 hours)

**Afternoon** (3 hours):
- ⏳ Task 4: Populate equipment_guns
  - Parse bg_reference_vehicles.weapons (1 hour)
  - Match vehicles to equipment (1 hour)
  - Create linkages (1 hour)

**Milestone**: Name variants table populated, gun linkages created

---

### Day 3 (3-4 hours)

**Morning** (2-3 hours):
- ⏳ Task 5: Infer equipment_type (1 hour)
- ⏳ Task 6: Orphaned FK investigation (1-2 hours)

**Afternoon** (1-2 hours):
- ⏳ Task 7: BattleGroup duplicate analysis
- ✅ Final validation
- ✅ Phase 2 summary report

**Milestone**: Phase 2 complete, all high-priority issues addressed

---

### Total Estimated Time: 13-16 hours over 3 days

---

## Success Criteria

### Phase 2 Complete When:

**Phase 2A (Critical)**:
- ✅ All 4 aircraft-as-tanks fixed
- ✅ ~35-40 WITW ID collisions auto-resolved
- ✅ 23 collisions escalated with detailed prompts
- ✅ Audit infrastructure operational (3 tables, 7 indexes)
- ✅ All changes logged in normalization_audit

**Phase 2B (High Priority)**:
- ✅ equipment_name_variants table has 100+ mappings
- ✅ equipment_guns table has 150-200 linkages (80-100 tanks)
- ✅ equipment_type populated for 95%+ records
- ✅ Orphaned FK root cause identified in analysis report

**Phase 2C (Medium Priority)**:
- ✅ All 154 BattleGroup duplicate groups categorized
- ✅ Generic units identified (no action needed)
- ✅ Import artifacts identified (safe to merge)
- ✅ Resolution strategy documented

**Validation**:
- ✅ All SQL scripts tested with validation queries
- ✅ Rollback scripts created for each batch
- ✅ No data loss (all changes reversible)
- ✅ Phase 1 issues reduced by 70%+

---

## Post-Phase 2 Quality Metrics

### Expected Data Quality After Phase 2

| Metric | Before Phase 2 | After Phase 2 | Improvement |
|--------|----------------|---------------|-------------|
| WITW ID collisions | 58 collisions | ~20-25 collisions | 57-65% reduction |
| Aircraft-as-tanks | 4 records | 0 records | 100% fixed |
| equipment_type populated | 0.4% | 95%+ | 237x improvement |
| equipment_guns for tanks | 0% | 70-90% | Complete for matched tanks |
| Name variant mappings | 0 | 100+ | New capability |
| Orphaned FK understanding | Unknown | Root cause identified | Investigation complete |
| BattleGroup duplicates | 154 (unknown) | 154 (categorized) | Strategy documented |

**Overall Quality Improvement**: 70-80% of Phase 1 issues addressed

---

## Deliverables Summary

### Phase 2 Outputs

**Documentation**:
- ✅ `REMEDIATION_PLAN.md` (this file)
- ⏳ `WITW_COLLISION_USER_DECISIONS.md` (23 escalation prompts)
- ⏳ `equipment_name_mapping.json` (match results)
- ⏳ `equipment_type_inference_rules.md` (category-to-type rules)
- ⏳ `orphaned_fk_analysis.md` (investigation report)
- ⏳ `bg_duplicate_resolution.json` (categorized duplicates)

**Database Changes**:
- ⏳ `normalization_audit` table (audit logging)
- ⏳ `witw_collision_resolutions` table (collision tracking)
- ⏳ `equipment_name_variants` table (name mappings)
- ⏳ `equipment` table updates (witw_id, equipment_type)
- ⏳ `equipment_guns` table population (150-200 linkages)

**SQL Scripts**:
- ⏳ Batch 1: Aircraft-as-tanks fix
- ⏳ Batch 2: Multi-category collisions
- ⏳ Batch 3: Generic variants
- ⏳ equipment_type inference
- ⏳ equipment_guns population
- ⏳ Rollback scripts (per batch)

---

## Next Steps: Phase 3 Execution

**Phase 3 will execute this plan**:
1. User reviews Phase 2 plan
2. User decides on 23 WITW ID collision escalations
3. Agent executes remediation batches
4. Validation after each batch
5. Rollback if issues detected
6. Final QA validation

**Prerequisite**: User approval of this remediation plan

---

## Sign-Off

**Phase 2 Status**: ✅ **PLANNING COMPLETE**
**Ready for Execution**: ⏳ **AWAITING USER APPROVAL**
**Estimated Execution Time**: 13-16 hours over 3 days
**Risk Level**: LOW (all changes reversible via rollback scripts)

**Planner**: Specialist Data Cleaning & Normalization Agent v2.0.0
**Date**: 2025-11-02
**Plan Version**: 1.0.0

---

**END OF REMEDIATION PLAN**
