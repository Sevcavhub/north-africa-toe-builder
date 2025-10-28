# Army & Corps Aggregation Issues Report

**Date**: 2025-10-27
**Scope**: All higher echelon units (armies and corps)
**Total Units Audited**: 41

---

## Executive Summary

**Status Breakdown**:
- ✅ **CORRECT**: 21/41 (51%) - Properly aggregating from subordinates
- ⚠️ **INCORRECT TOTALS**: 11/41 (27%) - Has subordinate data but wrong totals
- ⚠️ **HQ-ONLY**: 7/41 (17%) - Subordinates listed but no strength data
- ℹ️ **NO SUBORDINATES**: 2/41 (5%) - No subordinate units listed

**Units Needing Fixes**: **18 total** (7 HQ-only + 11 incorrect totals)

---

## 1. HQ-ONLY Issues (7 units)

These units list subordinates but have no strength data in subordinate_units array.

### British Units (3)

1. **british_1942q2_eighth_army_8th_army_toe.json**
   - Current: 100,000 personnel, 849 tanks
   - Subordinates: 2 units listed (no strength data)
   - Fix: Read subordinate corps files and aggregate totals

2. **british_1942q3_eighth_army_8th_army_toe.json**
   - Current: 150,000 personnel, 1,029 tanks
   - Subordinates: 2 units listed (no strength data)
   - Fix: Read subordinate corps files and aggregate totals

3. **british_1942q4_eighth_army_8th_army_toe.json**
   - Current: 1,250 personnel, 0 tanks ← **CRITICAL** (HQ-only instead of aggregated)
   - Subordinates: 3 units listed (no strength data)
   - Expected: ~100,000+ personnel, ~336+ tanks
   - Fix: Read subordinate corps files and aggregate totals

### Italian Units (4)

4. **italian_1940q2_10_armata_italian_10th_army_toe.json**
   - Current: 150,000 personnel, 120 tanks
   - Subordinates: 14 units listed (no strength data)
   - Fix: Read subordinate divisions and aggregate totals

5. **italian_1940q3_10_armata_italian_10th_army_toe.json**
   - Current: 150,000 personnel, 600 tanks
   - Subordinates: 5 units listed (no strength data)
   - Fix: Read subordinate divisions and aggregate totals

6. **italian_1940q3_xxii_corpo_d_armata_xxii_corps_toe.json**
   - Current: 14,600 personnel, 0 tanks
   - Subordinates: 9 units listed (no strength data)
   - Fix: Read subordinate divisions and aggregate totals

7. **italian_1941q1_xxii_corpo_d_armata_xxii_corps_toe.json**
   - Current: 25,000 personnel, 65 tanks
   - Subordinates: 6 units listed (no strength data)
   - Fix: Read subordinate divisions and aggregate totals

---

## 2. INCORRECT TOTALS (11 units)

These units have subordinate strength data but totals don't match expected aggregation.

### British Units (3)

1. **british_1941q3_eighth_army_8th_army_toe.json**
   - Current: 82,865 personnel, 302 tanks
   - Expected: 107,865 personnel, 0 tanks (from subordinates)
   - Discrepancy: -25,000 personnel (-23%)
   - Fix: Recalculate from subordinate corps

2. **british_1942q4_first_army_toe.json**
   - Current: 33,450 personnel, 165 tanks
   - Expected: 65,250 personnel, 0 tanks
   - Discrepancy: -31,800 personnel (-49%)
   - Fix: Recalculate from subordinate divisions

3. **british_1943q2_first_army_toe.json**
   - Current: 148,650 personnel, 643 tanks
   - Expected: 226,635 personnel, 960 tanks
   - Discrepancy: -77,985 personnel (-34%), -317 tanks (-33%)
   - Fix: Recalculate from subordinate divisions

### German Units (5)

4. **german_1941q3_panzergruppe_afrika_toe.json**
   - Current: 450 personnel, 0 tanks ← **CRITICAL** (HQ-only placeholder)
   - Expected: 118,500 personnel, 0 tanks
   - Discrepancy: -118,050 personnel (-99.6%)
   - Fix: Recalculate from subordinate divisions

5. **german_1942q1_panzergruppe_afrika_toe.json** (NOTE: File named "panzergruppe" but should be "panzerarmee")
   - Current: 500 personnel, 0 tanks ← **CRITICAL** (HQ-only placeholder)
   - Expected: 118,500 personnel, 0 tanks
   - Discrepancy: -118,000 personnel (-99.6%)
   - Fix: Recalculate from subordinate divisions

6. **german_1942q3_panzerarmee_afrika_toe.json**
   - Current: 96,000 personnel, 320 tanks
   - Expected: 129,500 personnel, 0 tanks
   - Discrepancy: -33,500 personnel (-26%)
   - Fix: Recalculate from subordinate divisions

7. **german_1942q4_panzerarmee_afrika_toe.json**
   - Current: 104,000 personnel, 238 tanks
   - Expected: 153,734 personnel, 441 tanks
   - Discrepancy: -49,734 personnel (-32%), -203 tanks (-46%)
   - Fix: Recalculate from subordinate divisions

8. **german_1943q1_panzerarmee_afrika_toe.json**
   - Current: 78,000 personnel, 240 tanks
   - Expected: 161,720 personnel, 0 tanks
   - Discrepancy: -83,720 personnel (-52%)
   - Fix: Recalculate from subordinate divisions

### Italian Units (3)

9. **italian_1940q4_xxi_corpo_d_armata_xxi_corps_toe.json**
   - Current: 0 personnel, 0 tanks ← **CRITICAL** (empty placeholder)
   - Expected: 34,000 personnel, 0 tanks
   - Fix: Recalculate from subordinate divisions

10. **italian_1940q4_xxii_corpo_d_armata_xxii_corps_toe.json**
    - Current: 0 personnel, 0 tanks ← **CRITICAL** (empty placeholder)
    - Expected: 41,500 personnel, 0 tanks
    - Fix: Recalculate from subordinate divisions

11. **italian_1941q1_xxi_corpo_d_armata_xxi_corps_toe.json**
    - Current: 45,000 personnel, 47 tanks
    - Expected: 32,375 personnel, 0 tanks
    - Discrepancy: +12,625 personnel (+39%) - OVER-COUNTED
    - Fix: Recalculate from subordinate divisions

---

## 3. Units with CORRECT Aggregation (21 units)

These units properly aggregate from their subordinates:

### British Units (5)
- british_1941q4_eighth_army_8th_army_toe.json ✓
- british_1942q1_eighth_army_8th_army_toe.json ✓
- british_1943q1_eighth_army_8th_army_toe.json ✓
- british_1943q1_first_army_toe.json ✓
- british_1943q2_eighth_army_8th_army_toe.json ✓

### German Units (5)
- german_1941q4_panzergruppe_afrika_toe.json ✓
- german_1942q2_panzerarmee_afrika_toe.json ✓
- german_1942q4_5th_panzer_army_toe.json ✓
- german_1943q1_5th_panzer_army_toe.json ✓
- german_1943q2_5th_panzer_army_toe.json ✓

### Italian Units (11)
- italian_1940q4_10_armata_italian_10th_army_toe.json ✓
- italian_1941q1_10_armata_italian_10th_army_toe.json ✓
- italian_1941q2_xxi_corpo_d_armata_xxi_corps_toe.json ✓
- italian_1941q3_xxi_corpo_d_armata_xxi_corps_toe.json ✓
- italian_1941q4_xxi_corpo_d_armata_xxi_corps_toe.json ✓
- italian_1942q1_xxi_corpo_d_armata_xxi_corps_toe.json ✓
- italian_1942q2_xxi_corpo_d_armata_xxi_corps_toe.json ✓
- italian_1942q3_xxi_corpo_d_armata_xxi_corps_toe.json ✓
- italian_1942q4_xxi_corpo_d_armata_xxi_corps_toe.json ✓
- italian_1943q1_first_italian_army_toe.json ✓
- italian_1943q2_first_italian_army_toe.json ✓

---

## 4. Fix Plan

### Automated Fix Script Approach

Create `scripts/fix_army_corps_aggregation.js` to:

1. **Read subordinate unit files** for each problematic army/corps
2. **Sum totals** (personnel, tanks, equipment) from subordinate units
3. **Update army/corps files** with calculated totals
4. **Update subordinate_units array** with correct strength data
5. **Set aggregation_status** to "calculated_from_subordinates"
6. **Preserve all other data** (notes, sources, organizational structure)

### Manual Validation Required

For units with zero or extremely low personnel (450, 500), verify:
- Are these actually HQ-only units historically?
- Or should they aggregate from subordinates?

### Priority Order

**CRITICAL (8 units)** - Fix first:
1. british_1942q4_eighth_army_8th_army_toe.json (1,250 vs ~100,000)
2. german_1941q3_panzergruppe_afrika_toe.json (450 vs 118,500)
3. german_1942q1_panzergruppe_afrika_toe.json (500 vs 118,500)
4. italian_1940q4_xxi_corpo_d_armata_xxi_corps_toe.json (0 vs 34,000)
5. italian_1940q4_xxii_corpo_d_armata_xxii_corps_toe.json (0 vs 41,500)
6. british_1942q4_first_army_toe.json (33,450 vs 65,250)
7. british_1943q2_first_army_toe.json (148,650 vs 226,635)
8. german_1942q4_panzerarmee_afrika_toe.json (104,000 vs 153,734)

**HIGH PRIORITY (10 units)** - Fix next:
- All remaining HQ-ONLY and INCORRECT units

---

## 5. Estimated Effort

- **Script Development**: 2-3 hours
- **Testing & Validation**: 1-2 hours
- **Fixing 18 units**: Automated (minutes)
- **Manual Review**: 1-2 hours
- **Total**: 4-7 hours

---

## 6. Success Criteria

After fixes, ALL 41 units should:
- ✅ Show aggregated totals from subordinates (not HQ-only)
- ✅ Have subordinate_units array with correct strengths
- ✅ Match expected totals within 15% tolerance
- ✅ Have `aggregation_status: "calculated_from_subordinates"`
- ✅ Pass validation checks

---

## Appendix: Subordinate Unit Reference Files

Script will need to read subordinate files from `data/output/units/`:
- Corps subordinates: Division-level units
- Army subordinates: Corps-level units (or divisions if no corps structure)

All subordinate filenames follow pattern: `{nation}_{quarter}_{unit_designation}_toe.json`
