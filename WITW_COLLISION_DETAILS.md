# WITW ID Collision Detailed Analysis

**Generated**: 2025-11-02
**Database**: master_database.db
**Total Collisions**: 58
**Total Affected Records**: 169 (36% of equipment table)

---

## Collision Severity Classification

### CRITICAL (Multi-Category Collisions)
**Definition**: Same WITW ID assigned to items from different categories (e.g., tanks + aircraft)

**Count**: 12 collisions affecting 52 records

**Impact**: SEVERE - Would cause wrong item types in WITW scenario exports

---

### HIGH (Same Category, Different Variants)
**Definition**: Same WITW ID assigned to multiple variants of same equipment type

**Count**: 28 collisions affecting 78 records

**Impact**: MODERATE - Would cause variant confusion in scenarios

---

### MEDIUM (Generic Equipment Collisions)
**Definition**: Same WITW ID assigned to generic support vehicles/trucks

**Count**: 18 collisions affecting 39 records

**Impact**: LOW - Generic vehicles may be interchangeable

---

## Top 10 Worst Collisions (By Record Count)

### 1. WITW ID 115 (11 records) - CRITICAL
**Categories**: Fighters (8) + Tanks (3) + Field Artillery (1)

**Collision Type**: Multi-category (CRITICAL)

**Affected Items**:
```
AIRCRAFT (8 items):
  - GBR_HURRICANE_MK1              (Hurricane Mk1)               [fighters]
  - GBR_HAWKER_HURRICANE_MK_I      (Hawker Hurricane Mk I)       [fighters]
  - GBR_HAWKER_HURRICANE_MK_II     (Hawker Hurricane Mk II)      [fighters]
  - GBR_HAWKER_HURRICANE_MK_IIC    (Hawker Hurricane Mk IIC)     [fighters]
  - GBR_HAWKER_HURRICANE_MK_IID    (Hawker Hurricane Mk IID)     [fighters]
  - GBR_HURRICANE_MK2              (Hurricane Mk2)               [fighters]
  - GBR_HURRICANE_RECON            (Hurricane Recon)             [reconnaissance]

TANKS (3 items - DATA CORRUPTION):
  - GBR_SHERMAN_I_M4               (Sherman I (M4))              [tanks]
  - GBR_SHERMAN_II_M4A1            (Sherman II (M4A1))           [tanks]
  - GBR_SHERMAN_III_M4A4           (Sherman III (M4A4))          [tanks]

ARTILLERY (1 item):
  - GER_SFH_18_15CM                (Sfh 18 15cm)                 [field_artillery]
```

**Recommended Resolution**:
1. Retain: GBR_HAWKER_HURRICANE_MK_I (primary variant)
2. Set NULL: All other Hurricanes (Phase 5 will re-assign unique IDs)
3. Set NULL: All 3 Sherman tanks (corrupted - should NOT have aircraft ID)
4. Set NULL: German artillery (wrong ID)

**Escalation**: NO - Clear semantic mismatch (aircraft vs tanks vs artillery)

---

### 2. WITW ID 110 (8 records) - CRITICAL
**Categories**: Bombers (7) + Field Artillery (1)

**Collision Type**: Multi-category (CRITICAL)

**Affected Items**:
```
AIRCRAFT (7 items):
  - GBR_BLENHEIM_MK1               (Blenheim Mk1)                [bombers]
  - GBR_BLENHEIM_MK_I              (Blenheim Mk I)               [bombers]
  - GBR_BLENHEIM_MK4               (Blenheim Mk4)                [bombers]
  - GBR_BRISTOL_BLENHEIM_RECCE     (Bristol Blenheim (recce))    [reconnaissance]
  - GBR_BRISTOL_BLENHEIM_MK_I      (Bristol Blenheim Mk I)       [bombers]
  - GBR_BRISTOL_BLENHEIM_MK_IV     (Bristol Blenheim Mk IV)      [bombers]
  - GBR_BLENHEIM_MK5               (Blenheim Mk5)                [bombers]

ARTILLERY (1 item):
  - GER_10.5CM_LEFH_18             (10.5cm Lefh 18)              [field_artillery]
```

**Recommended Resolution**:
1. Retain: GBR_BRISTOL_BLENHEIM_MK_IV (primary variant)
2. Set NULL: All other Blenheims (Phase 5 re-match)
3. Set NULL: German artillery (wrong ID)

**Escalation**: NO - Clear category mismatch

---

### 3. WITW ID 100032 (7 records) - HIGH
**Categories**: Trucks (6) + Anti-Aircraft (1)

**Collision Type**: Multi-category (HIGH)

**Affected Items**:
```
TRUCKS (6 items):
  - GBR_BEDFORD_MW                 (Bedford MW)                  [trucks]
  - GBR_BEDFORD_OWL                (Bedford OWL)                 [trucks]
  - GBR_BEDFORD_MW_15CWT           (Bedford MW 15cwt)            [trucks]
  - GBR_BEDFORD_OY_3-TON           (Bedford OY 3-ton)            [trucks]
  - GBR_BEDFORD_MW_MWD             (Bedford MW/MWD)              [trucks]
  - GBR_BEDFORD_OX                 (Bedford OX)                  [trucks]

ANTI-AIRCRAFT (1 item):
  - GBR_BOFORS_40MM                (Bofors 40mm)                 [anti_aircraft]
```

**Recommended Resolution**:
1. Retain: GBR_BEDFORD_MW (most generic)
2. Set NULL: All other Bedford variants (may be same vehicle)
3. Set NULL: Bofors 40mm (wrong category)

**Escalation**: MAYBE - Bedford variants may need domain expert review

---

### 4. WITW ID 100043 (7 records) - HIGH
**Categories**: Command Vehicles (1) + Trucks (6)

**Collision Type**: Same family (HIGH)

**Affected Items**:
```
  - USA_DODGE_COMMAND_CAR          (Dodge Command Car)           [command_vehicles]
  - USA_DODGE_WC-51                (Dodge WC-51)                 [trucks]
  - USA_DODGE_WC-53                (Dodge WC-53)                 [trucks]
  - USA_DODGE_WC-54                (Dodge WC-54)                 [trucks]
  - USA_DODGE_WC-56                (Dodge WC-56)                 [trucks]
  - USA_DODGE_WC54                 (Dodge WC54)                  [trucks]
  - USA_DODGE_WC_SERIES            (Dodge WC Series)             [trucks]
```

**Recommended Resolution**:
1. Retain: USA_DODGE_WC_SERIES (generic - covers all variants)
2. Set NULL: All specific variants (WC-51, WC-53, etc.)

**Escalation**: MAYBE - Dodge WC variants are same vehicle family

---

### 5. WITW ID 251 (5 records) - CRITICAL
**Categories**: Armored Cars (4) + Halftracks (1)

**Collision Type**: Multi-category (CRITICAL)

**Affected Items**:
```
ARMORED CARS (4 items):
  - GER_SDKFZ_222                  (SdKfz 222)                   [armored_cars]
  - GER_SDKFZ_231                  (SdKfz 231)                   [armored_cars]
  - GER_SDKFZ_232_FU               (SdKfz 232 (fu))              [armored_cars]
  - GER_SDKFZ_223                  (SdKfz 223)                   [armored_cars]

HALFTRACKS (1 item):
  - GER_SDKFZ_251_1                (SdKfz 251/1)                 [halftracks]
```

**Recommended Resolution**:
1. Research WITW database: Which SdKfz is actually ID 251?
2. Retain correct item
3. Set NULL for all others

**Escalation**: YES - All items are valid German vehicles, need WITW reference check

---

### 6. WITW ID 626 (5 records) - HIGH
**Categories**: Support Vehicles (2) + Trucks (3)

**Collision Type**: Same nation, different models (HIGH)

**Affected Items**:
```
  - ITA_FIAT_626_RECOVERY          (FIAT 626 Recovery)           [support_vehicles]
  - ITA_FIAT_666                   (FIAT 666)                    [trucks]
  - ITA_FIAT_508C_BALILLA          (FIAT 508c Balilla)           [support_vehicles]
  - ITA_FIAT_626_ALL_VARIANTS      (FIAT 626 (all Variants))     [trucks]
  - ITA_FIAT_665NM                 (FIAT 665NM)                  [trucks]
```

**Recommended Resolution**:
1. Check WITW: Is ID 626 referring to FIAT model 626?
2. Retain: ITA_FIAT_626_ALL_VARIANTS
3. Set NULL: All other FIAT models (different vehicles)

**Escalation**: YES - Need WITW reference (ID 626 might = FIAT 626)

---

### 7. WITW ID 100031 (5 records) - CRITICAL
**Categories**: Armored Cars (1) + Bombers (4)

**Collision Type**: Multi-category (CRITICAL)

**Affected Items**:
```
ARMORED CARS (1 item):
  - GBR_MARMON-HERRINGTON          (Marmon-herrington)           [armored_cars]

BOMBERS (4 items):
  - GBR_BOSTON_MK_III              (Boston Mk III)               [bombers]
  - GBR_WELLINGTON_MK_VIII         (Wellington Mk VIII)          [bombers]
  - GBR_WELLINGTON_MK_X            (Wellington Mk X)             [bombers]
  - GBR_WELLINGTON_MK3             (Wellington Mk3)              [bombers]
```

**Recommended Resolution**:
1. Set NULL: Marmon-Herrington (wrong category)
2. Retain: GBR_WELLINGTON_MK_VIII (primary Wellington variant)
3. Set NULL: All other bombers

**Escalation**: NO - Clear category mismatch

---

### 8. WITW ID 100049 (5 records) - CRITICAL
**Categories**: Armored Cars (1) + Tanks (3) + Halftracks (1)

**Collision Type**: Multi-category (CRITICAL)

**Affected Items**:
```
  - USA_M3_SCOUT_CAR               (M3 Scout Car)                [armored_cars_reconnaissance]
  - USA_M3_STUART                  (M3 Stuart)                   [tanks]
  - USA_M3A1_LEE                   (M3A1 Lee)                    [tanks]
  - USA_M3A1_STUART                (M3A1 Stuart)                 [tanks]
  - USA_M3A1_SCOUT_CAR             (M3A1 Scout Car)              [halftracks]
```

**Recommended Resolution**:
1. Research WITW: Which M3 variant is ID 100049?
2. Likely different M3 vehicles (Scout Car vs Stuart tank vs Lee tank)
3. Set NULL for all, Phase 5 re-match individually

**Escalation**: YES - "M3" is ambiguous (multiple vehicle types)

---

### 9. WITW ID 504 (4 records) - HIGH
**Categories**: Halftracks (3) + Command Vehicles (1)

**Collision Type**: Same family (HIGH)

**Affected Items**:
```
  - USA_M2_HALFTRACK               (M2 Halftrack)                [halftracks]
  - USA_M3_COMMAND_HALFTRACK       (M3 Command Halftrack)        [command_vehicles]
  - USA_M3_HALFTRACK               (M3 Halftrack)                [halftracks]
  - USA_M3A1_HALFTRACK             (M3A1 Halftrack)              [halftracks]
```

**Recommended Resolution**:
1. Retain: USA_M3_HALFTRACK (primary variant)
2. Set NULL: M2, M3A1 (different models)
3. Set NULL or merge: M3 Command (may be variant of M3)

**Escalation**: MAYBE - M2 vs M3 are different vehicles

---

### 10. WITW ID 49 (3 records) - HIGH
**Categories**: Anti-Aircraft (2) + Anti-Tank (1)

**Collision Type**: Multi-category (HIGH)

**Affected Items**:
```
  - GER_FLAK_18                    (Flak 18)                     [anti_aircraft]
  - GER_FLAK_38                    (Flak 38)                     [anti_aircraft]
  - GER_FLAK_36_8.8CM              (Flak 36 8.8cm)               [anti_tank]
```

**Recommended Resolution**:
1. Research WITW: Flak 18/36/38 are different models
2. Likely Flak 36 is primary 88mm (used for both AA and AT)
3. Retain: GER_FLAK_36_8.8CM
4. Set NULL: Flak 18, Flak 38

**Escalation**: YES - All valid German Flak variants, need WITW reference

---

## Resolution Decision Tree

```
For each WITW ID collision:

1. IS IT MULTI-CATEGORY? (aircraft + tanks, trucks + aircraft, etc.)
   YES → CRITICAL
     ├─ Set witw_id = NULL for category mismatch items
     ├─ Retain one item from largest category
     └─ Log: "Multi-category collision resolved"
   NO → Go to step 2

2. IS IT SAME VEHICLE FAMILY? (M3 Scout vs M3 Stuart, Bedford variants, etc.)
   YES → HIGH PRIORITY
     ├─ Research WITW database: Which variant is correct?
     ├─ Retain: Correct variant OR most generic name
     ├─ Set NULL: All other variants
     └─ ESCALATE if ambiguous (e.g., "M3" = Scout Car OR Stuart tank?)
   NO → Go to step 3

3. IS IT DIFFERENT MODELS? (Flak 18 vs Flak 36, FIAT 626 vs FIAT 666, etc.)
   YES → ESCALATE TO USER
     ├─ Cannot determine correct item automatically
     ├─ Need WITW database reference lookup
     └─ Log: "Model collision - user decision required"
   NO → Go to step 4

4. GENERIC COLLISION (Support vehicles, trucks, etc.)
   ├─ Retain: Most generic name OR "all variants"
   ├─ Set NULL: Specific variants
   └─ Log: "Generic collision - retained umbrella item"
```

---

## Resolution Summary Table

| WITW ID | Records | Category Mix | Escalate? | Resolution Strategy |
|---------|---------|--------------|-----------|---------------------|
| 115 | 11 | Fighters + Tanks + Artillery | NO | Set NULL all (aircraft-as-tanks) |
| 110 | 8 | Bombers + Artillery | NO | Set NULL artillery, retain primary bomber |
| 100032 | 7 | Trucks + Anti-Aircraft | MAYBE | Retain Bedford MW, NULL others |
| 100043 | 7 | Command + Trucks | MAYBE | Retain Dodge WC Series |
| 251 | 5 | Armored Cars + Halftracks | YES | Need WITW reference (SdKfz) |
| 626 | 5 | Support + Trucks | YES | Check if 626 = FIAT 626 |
| 100031 | 5 | Armored Cars + Bombers | NO | Set NULL armored car |
| 100049 | 5 | Scout + Tanks + Halftracks | YES | "M3" ambiguous |
| 504 | 4 | Halftracks + Command | MAYBE | M2 vs M3 are different |
| 49 | 3 | Anti-Aircraft + Anti-Tank | YES | Flak variants need check |

**Totals**:
- ✅ **Auto-resolve**: 25 collisions (43%)
- ⚠️ **Escalate to user**: 33 collisions (57%)

---

## Aircraft-as-Tanks Details (CRITICAL)

### Issue: Tanks Inheriting Aircraft WITW Names

**Root Cause**: WITW ID collisions (115, 116) caused tanks to inherit aircraft witw_names during data import

**Affected Tanks**:

```sql
SELECT canonical_id, name, witw_name, witw_id, category
FROM equipment
WHERE category IN ('tanks', 'main_tanks')
  AND (witw_name LIKE '%(FI)%' OR witw_name LIKE '%(LB)%');
```

**Results**:

| canonical_id | name | witw_name | witw_id | category |
|--------------|------|-----------|---------|----------|
| GBR_CRUSADER_I | Crusader I | Lysander I (FI) | 116 | tanks |
| GBR_SHERMAN_I_M4 | Sherman I (M4) | Hurricane I (FI) | 115 | tanks |
| GBR_SHERMAN_II_M4A1 | Sherman II (M4A1) | Hurricane I (FI) | 115 | tanks |
| GBR_SHERMAN_III_M4A4 | Sherman III (M4A4) | Hurricane I (FI) | 115 | tanks |

**Fix**:
```sql
BEGIN TRANSACTION;

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

COMMIT;
```

**Post-Fix**: Phase 5 equipment matching will re-assign correct WITW IDs

---

## Recommended Phase 2 Actions

### 1. Create Resolution Log Table

```sql
CREATE TABLE witw_collision_resolutions (
  resolution_id INTEGER PRIMARY KEY AUTOINCREMENT,
  witw_id INTEGER NOT NULL,
  collision_count INTEGER NOT NULL,
  resolution_strategy TEXT NOT NULL,
  retained_canonical_id TEXT,
  nulled_canonical_ids TEXT, -- JSON array
  escalated BOOLEAN DEFAULT 0,
  escalation_reason TEXT,
  resolved_at TEXT DEFAULT CURRENT_TIMESTAMP,
  resolved_by TEXT DEFAULT 'normalization_agent_v2.0'
);
```

---

### 2. Generate Resolution Scripts

For each collision:
1. Create SQL UPDATE script (with BEGIN/COMMIT transaction)
2. Create rollback script
3. Log resolution to witw_collision_resolutions table
4. Create audit entries in normalization_audit table

---

### 3. User Escalation List

**Items Requiring User Decision** (33 collisions):

Priority escalations:
- WITW ID 251 (SdKfz variants)
- WITW ID 626 (FIAT model vs ID number)
- WITW ID 100049 (M3 Scout vs M3 Stuart ambiguity)
- WITW ID 49 (Flak 18/36/38 variants)

**Escalation Format**:
```markdown
## WITW ID 251 Collision Decision Required

**Collision**: 5 German vehicles (4 armored cars + 1 halftrack)

**Question**: Which vehicle is the correct WITW ID 251?
- Option A: SdKfz 222 (armored car)
- Option B: SdKfz 231 (armored car)
- Option C: SdKfz 251/1 (halftrack)
- Option D: Set all to NULL (Phase 5 re-match)

**Recommendation**: Check WITW database reference, likely SdKfz 251/1

**User Decision**: _____________
```

---

## Phase 2 Deliverable Preview

**File**: `witw_collision_resolutions.json`

```json
{
  "analysis_date": "2025-11-02",
  "total_collisions": 58,
  "auto_resolved": 25,
  "user_escalated": 33,
  "resolutions": [
    {
      "witw_id": 115,
      "strategy": "aircraft_as_tanks_fix",
      "retained": null,
      "nulled": ["GBR_HURRICANE_MK1", "GBR_SHERMAN_I_M4", ...],
      "reason": "Multi-category collision - critical data corruption"
    },
    {
      "witw_id": 251,
      "strategy": "escalate_to_user",
      "escalation_reason": "Cannot determine correct SdKfz variant",
      "user_decision_pending": true
    }
  ]
}
```

---

## Sign-Off

**Analysis Status**: ✅ **COMPLETE**
**Collision Count**: 58 verified
**Aircraft-as-Tanks**: 4 identified
**Escalation Required**: 33 collisions (57%)

**Recommendation**: Proceed to Phase 2 remediation planning

**Analyst**: Database Normalization Agent v2.0.0
**Date**: 2025-11-02

---

**END OF WITW COLLISION ANALYSIS**
