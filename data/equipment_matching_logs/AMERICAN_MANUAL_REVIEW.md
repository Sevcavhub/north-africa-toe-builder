# American Equipment Manual Review
**Date**: October 18, 2025
**Status**: 11 items requiring manual review/resolution

---

## Aircraft Matches Found (9 items)

### ✅ Direct Matches (4 items)

| WITW Baseline | Aircraft Database Match | WITW ID | Confidence |
|---------------|------------------------|---------|------------|
| A-20G Havoc | A-20G-K Havoc | 707 | 90% |
| B-17F Flying Fortress | B-17F Fortress | 717 | 95% |
| C-47 Skytrain | C-47 Skytrain | 730 | 100% (exact) |
| F-4 (P-38 Photo) | F-4 Lightning | 726 | 95% |

### ✅ Variant Matches (4 items)

| WITW Baseline | Aircraft Database Match | WITW ID | Confidence | Notes |
|---------------|------------------------|---------|------------|-------|
| F4F-4 Wildcat | F4F Wildcat | 742 | 90% | Generic variant (F4F covers all) |
| Lockheed P-38F Lightning | P-38F Lightning | 725 | 100% (exact) | Found! |
| SBD-3 Dauntless | SBD Dauntless | 740 | 90% | Generic variant (SBD covers all) |

### ⚠️ Lend-Lease/Cross-Nation (2 items)

| WITW Baseline | Aircraft Database Match | WITW ID | Nation | Confidence | Decision |
|---------------|------------------------|---------|--------|------------|----------|
| B-25C Mitchell (USA) | B-25C Mitchell | 709 | **British** | 100% | **APPROVE** - US aircraft operated by RAF in North Africa |
| Supermarine Spitfire Mk VB (USA) | Spitfire VB (SU) | 408 | **Nation_12** | 90% | **APPROVE** - British aircraft operated by USAAF |

**Rationale**: Both are historically accurate - Americans operated British aircraft and vice versa in North Africa campaign. Database stores by manufacturing nation, not operator.

---

## Aircraft NOT in Database (1 item)

### ❌ Missing from WITW

| WITW Baseline | Status | Decision |
|---------------|--------|----------|
| TBF-1 Avenger | **NOT FOUND** in aircraft database | **SKIP** - Not in WITW game data |

**Searched**: TBF, Avenger, TBF-1, all variants
**Result**: No Avenger variants exist in WITW aircraft CSV (1,006 aircraft total)
**Action**: Mark as SKIPPED with note "Not in WITW aircraft database"

---

## Mortar (1 item)

### ⚠️ Not in Gun Database

| WITW Baseline | Status | Decision |
|---------------|--------|----------|
| M1 81mm Mortar | **NOT FOUND** in guns table (343 guns) | **SKIP** - Mortars not in WWIITANKS database |

**Rationale**: WWIITANKS gun database focuses on towed AT/AA/field guns. Mortars are infantry weapons, not tracked.
**Action**: Mark as SKIPPED with note "Mortars not in gun database (infantry weapons)"

---

## Summary

**Total**: 11 items
**Approve (with WITW ID)**: 9 aircraft
**Skip (not in database)**: 2 items (1 aircraft, 1 mortar)

**Next Step**: Apply these matches to database `match_reviews` table.
