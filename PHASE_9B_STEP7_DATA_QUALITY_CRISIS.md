# Phase 9B Step 7: Critical Data Quality Issues Identified

**Date**: November 2, 2025
**Discovered By**: User observation + Claude analysis
**Severity**: CRITICAL - Affects book datacard generation accuracy

---

## Executive Summary

Investigation into why A10 Cruiser Mk II appeared in "Other Equipment" with missing gun data revealed **systemic WITW integration data corruption** affecting hundreds of equipment items.

### Key Findings

1. **30+ WITW ID Collisions** - Same WITW ID mapped to completely different equipment
2. **Aircraft Tagged as Tanks** - Sherman & Crusader tanks have aircraft witw_names
3. **Missing Equipment Type Fields** - `equipment_type` is null for most items
4. **Name Variance** - Equipment names don't match reference table names exactly
5. **Categorization Logic Gaps** - "Cruiser" not recognized as tank keyword

---

## Issue 1: Categorization Logic Gap

**File**: `scripts/battlegroup/book/generate_book_datacards.py:271`

**Problem**: Tank detection keyword list missing "cruiser"

```python
# Current (BROKEN)
elif any(x in name for x in [' tank', 'panzer', 'sherman', 'matilda',
                              'valentine', 'crusader', 'grant', 'stuart', 'tiger']):
```

**Impact**: A9, A10, A13 Cruiser tanks (British early-war tanks) fall through to "Other Equipment"

**Historical Context**:
- **A9 Cruiser** (1937) - First British cruiser tank, 2pdr gun
- **A10 Cruiser** (1938) - Improved armor over A9, 2pdr gun
- **A13 Cruiser** (1939) - Fast cruiser with Christie suspension, 2pdr gun
- **A15 Crusader** (1941) - Name changed from "Cruiser" to "Crusader"

**Fix**: Add `'cruiser'` to keyword list

---

## Issue 2: Gun Data Lookup Failures

**Root Cause**: Name mismatch between `equipment` table and `bg_reference_vehicles` table

### Example Cases

| Equipment Table | Reference Vehicles Table | Match? |
|-----------------|--------------------------|--------|
| A10 Cruiser Mk II | A10 Cruiser | ❌ No |
| A13 Cruiser Mk2 | A13 Mk I Cruiser | ❌ No |
| A13 Cruiser Mk3 | A13 Mk I Cruiser | ❌ No |

**Impact**: Script can't find gun data → shows "Weapon: None" in datacards

**Gun Data Available** (in `bg_reference_vehicles`):
- **A9 Cruiser**: 2pdr (turret) + MG (coax) + 2x MG (hull)
- **A10 Cruiser**: 2pdr (turret) + MG (coax) + MG (hull)
- **A13 Mk I Cruiser**: 2pdr (turret) + MG (coax)

**Missing**: No linkages in `equipment_guns` table for these tanks

---

## Issue 3: WITW Integration Data Corruption

### Summary Statistics

- **Total WITW ID collisions**: 30+
- **Worst collision**: WITW ID 115 (11 equipment items)
- **Aircraft incorrectly linked to tanks**: 4 cases
- **Equipment with null `equipment_type`**: ~90%+

### Critical Collision Examples

#### WITW ID 115 (11 items - DISASTER)
```
- GBR_HURRICANE_MK1 (fighters)
- GBR_SHERMAN_I_M4 (tanks)  ← TANK WITH FIGHTER ID
- GBR_SHERMAN_II_M4A1 (tanks) ← TANK WITH FIGHTER ID
- GBR_SHERMAN_III_M4A4 (tanks) ← TANK WITH FIGHTER ID
- GER_SFH_18_15CM (field_artillery) ← GERMAN ARTILLERY WITH BRITISH FIGHTER ID
- [6 more aircraft variants]
```

#### WITW ID 116 (Your Example)
```
Equipment Table Entry:
  canonical_id: GBR_CRUSADER_I
  name: "Crusader I"
  category: "tanks"
  witw_id: 116
  witw_name: "Lysander I (FI)"  ← AIRCRAFT NAME FOR A TANK!

Correct Entry:
  canonical_id: GBR_LYSANDER
  name: "Lysander"
  category: "reconnaissance"
  witw_id: 116
  witw_name: "Lysander I (FI)"  ✓ Correct
```

**Result**: Crusader I tank has the WITW ID and name of a Lysander reconnaissance aircraft!

#### WITW ID 110 (8 items)
```
- GBR_BLENHEIM_MK1 (bombers) × 6 variants
- GER_10.5CM_LEFH_18 (field_artillery) ← GERMAN ARTILLERY WITH BRITISH BOMBER ID
```

### Aircraft-as-Tanks Cases

| Tank | WITW ID | WITW Name (WRONG!) | Should Be |
|------|---------|-------------------|-----------|
| Crusader I | 116 | Lysander I (FI) | Crusader tank |
| Sherman I (M4) | 115 | Hurricane I (FI) | Sherman tank |
| Sherman II (M4A1) | 115 | Hurricane I (FI) | Sherman tank |
| Sherman III (M4A4) | 115 | Hurricane I (FI) | Sherman tank |

---

## Issue 4: Missing `equipment_type` Field

**Finding**: ~90%+ of equipment records have `equipment_type = null`

**Impact**: Categorization logic cannot rely on this field

**Example** (A10 Cruiser Mk II):
```json
{
  "canonical_id": "GBR_A10_CRUISER_MK_II",
  "name": "A10 Cruiser Mk II",
  "category": "tanks",
  "equipment_type": null  ← SHOULD BE "tank" or "armored_vehicle"
}
```

**Result**: Script must fall back to name-based keyword matching (which is incomplete)

---

## Issue 5: Category Value Inconsistency

**Finding**: Same equipment type has different category values

**Examples**:
- A10 tanks: `"tanks"` vs `"main_tanks"`
- Crusader tanks: `"tanks"` vs `"main_tanks"`

**Impact**: Even when categorization uses `category` field, it must handle multiple values

---

## Root Cause Analysis

### How Did This Happen?

1. **WITW Baseline Import** (Phase 5)
   - 469 equipment items imported from `WITW_EQUIPMENT_BASELINE.json`
   - Each item has `witw_id` and `witw_name`

2. **Equipment Matching Process** (Phase 5 - INCOMPLETE)
   - Only **20/469 items matched** (4.3% complete)
   - French: 20/20 ✓ COMPLETE
   - American: 0/81 ❌ NOT STARTED
   - German: 0/98 ❌ NOT STARTED
   - British: 0/196 ❌ NOT STARTED (includes Cruisers, Shermans!)
   - Italian: 0/74 ❌ NOT STARTED

3. **Data Import from Multiple Sources**
   - Phase 6 unit JSONs extracted → new equipment discovered
   - Equipment added to database without WITW matching
   - **Result**: `witw_id` and `witw_name` fields auto-assigned incorrectly

4. **No Data Validation**
   - No checks for WITW ID uniqueness
   - No validation of `witw_name` against `category` (aircraft vs tank)
   - No referential integrity checks

---

## Impact Assessment

### Affected Systems

✅ **Phase 6 Ground Forces Extraction** - NOT affected (uses unit JSONs directly)
✅ **Schema v3.1.0 Validation** - NOT affected (validates structure, not content)
❌ **Phase 9B Book Datacard Generation** - CRITICALLY affected
❌ **Future WITW Scenario Exports** - WILL BE affected
❌ **Equipment Database Reliability** - COMPROMISED

### Datacard Generation Impact

**Books Affected**: All 4 (Battleaxe, Crusader, Gazala, Alamein)

**Categories Affected**:
- Tanks → "Other Equipment" (A9, A10, A13 Cruisers)
- Missing gun data → "Weapon: None" (widespread)
- Incorrect WITW references for scenario exports

**User-Facing Issues**:
- Unusable datacards (no weapons, wrong category)
- Cannot generate accurate scenarios
- Historical inaccuracy in published content

---

## Recommended Fix Strategy

### Immediate (Phase 9B Step 7)

1. **Fix Categorization Logic** (Quick Win - 5 min)
   - Add `'cruiser'` to tank keyword list
   - Test with Battleaxe chapter 2

2. **Improve Gun Lookup Fuzzy Matching** (Medium - 30 min)
   - Strip variant suffixes ("Mk II", "Mk2", etc.) before matching
   - Fallback: Try base name without variant

3. **Manually Link A9/A10/A13 Guns** (Quick - 15 min)
   - Populate `equipment_guns` table for these 3 tanks
   - Use data from `bg_reference_vehicles`

### Short-Term (Phase 9B Completion)

4. **Add Equipment Type Inference** (Medium - 1 hour)
   - Auto-populate `equipment_type` from `category`
   - "tanks"/"main_tanks" → "tank"
   - "field_artillery" → "artillery"

5. **Create Data Validation Suite** (Medium - 2 hours)
   - Check WITW ID uniqueness
   - Validate `witw_name` matches `category` semantics
   - Flag aircraft-as-tanks mismatches

### Long-Term (Post-Phase 9B)

6. **Complete Equipment Matching** (Phase 5 Resumption)
   - Match remaining 449/469 WITW items
   - British: 196 items (PRIORITY - includes problem tanks)
   - American: 81 items
   - German: 98 items
   - Italian: 74 items

7. **Database Cleanup & Normalization** (Major - 1 week)
   - De-duplicate equipment entries
   - Fix all WITW ID collisions
   - Establish canonical equipment list
   - Migrate existing unit JSONs to new IDs

8. **Referential Integrity Enforcement** (Medium - 1 day)
   - Add database constraints
   - Unique constraint on `witw_id` (where not null)
   - Check constraint: aircraft categories cannot have tank IDs

---

## Testing & Validation

### Test Case 1: A10 Cruiser Mk II
**Current Output**: "Other Equipment", Weapon: None
**Expected Output**: "Tanks", Weapon: 2pdr

### Test Case 2: Crusader I
**Current WITW Data**: witw_id=116, witw_name="Lysander I (FI)"
**Expected**: witw_id=2012 or unique, witw_name="Crusader I"

### Test Case 3: Sherman I (M4)
**Current WITW Data**: witw_id=115, witw_name="Hurricane I (FI)"
**Expected**: witw_id=unique, witw_name="Sherman I" or "M4"

---

## Files Requiring Changes

### Immediate Fixes (Step 7)
- `scripts/battlegroup/book/generate_book_datacards.py` (categorization + fuzzy matching)

### Short-Term
- `database/master_database.db` (equipment table updates)
- Data validation scripts (new)

### Long-Term
- `tools/equipment_matcher_v2.py` (resume Phase 5 matching)
- All unit JSONs (if canonical IDs change)

---

## Decision Required

**Question**: Should we:

**Option A**: Quick fix for Phase 9B (fix categorization + gun lookup only)
- **Pros**: Unblocks book generation immediately
- **Cons**: Underlying WITW data corruption remains

**Option B**: Full data cleanup before proceeding
- **Pros**: Ensures data integrity for all future work
- **Cons**: Delays Phase 9B completion by 1-2 weeks

**Option C**: Parallel approach
- **Immediate**: Fix categorization + gun lookup (today)
- **Background**: Begin systematic data cleanup (next week)
- **Pros**: Best of both worlds
- **Cons**: More complex project management

---

## Appendix: Complete WITW Collision List

See `temp_check_witw_collisions.py` output for full list of 30+ collisions.

Top 5 worst collisions by item count:
1. WITW ID 115: 11 items (Hurricanes + Shermans + German artillery)
2. WITW ID 110: 8 items (Blenheims + German artillery)
3. WITW ID 100032: 7 items (Bedford trucks + Bofors AA gun)
4. WITW ID 100043: 7 items (Dodge trucks, all variants)
5. WITW ID 251: 5 items (SdKfz halftracks and armored cars)

---

**End of Report**
