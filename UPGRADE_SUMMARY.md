# Schema v3.0 Upgrade - Quick Reference

**Goal**: Fix 25 units with warnings → Achieve 100% validation pass rate

---

## 📊 Current State

```
Total Units:        158
✅ Passing:         133 (84.2%)
⚠️  Warnings:       25 (15.8%)
❌ Critical Fails:  0 (0.0%)
```

## 🎯 Target State

```
Total Units:        158
✅ Passing:         158 (100%) ← +25 units
⚠️  Warnings:       0 (0.0%)   ← -25 warnings
❌ Critical Fails:  0 (0.0%)
```

---

## 🔧 Fix Categories

### 🔴 Priority 1: Critical Fixes (7 units + 1 deletion)
**Time**: 2-3 hours | **Effort**: LOW

| Issue | Count | Action |
|-------|-------|--------|
| Invalid schema_type | 4 | Change to correct value |
| 0% confidence | 2 | Full regeneration required |
| Data quality errors | 3 | Fix calculations/values |
| Superseded file | 1 | DELETE old version |

### 🟡 Priority 2: Low Confidence (13 units)
**Time**: 4-6 hours | **Effort**: MEDIUM

| Nation | Count | Current | Target | Method |
|--------|-------|---------|--------|--------|
| German | 3 | 65-72% | 78%+ | Add Tessin sources |
| Italian | 5 | 68-72% | 78%+ | TM E 30-420 + Nafziger |
| British | 4 | 72% | 78%+ | Army Lists + war diaries |
| French | 1 | 72% | 78%+ | Free French archives |

### 🟠 Priority 3: Unknown Commanders (6 units)
**Time**: 2-3 hours | **Effort**: HIGH

| Division | Quarters | Research Sources |
|----------|----------|------------------|
| Littorio | 3 (Q2, Q3, Q4) | Comando Supremo, Italian archives |
| Folgore | 1 (Q4) | El Alamein histories |
| Trieste | 1 (Q2) | Compare with Q4 version |
| Centauro | 1 (Q1) | Italian armored histories |

---

## 📋 25 Units to Fix - Complete List

### Phase 1: Quick Fixes (8 units)

**Schema Type Fixes** (4 units):
1. ❌ `french_1942q2_1re_brigade_fran_aise_libre_toe.json` - brigade_toe → corps_toe
2. ❌ `british_1940q2_western_desert_force_toe.json` - unified_toe → corps_toe (+ regenerate, 0% conf)
3. ❌ `british_1940q3_7th_armoured_division_toe.json` - unified_toe → division_toe (+ regenerate, 0% conf)
4. ❌ `german_1942q3_panzerarmee_afrika_toe.json` - theater_toe → theater_scm

**Data Quality Fixes** (3 units):
5. ❌ `german_1941q3_21_panzer_division_toe.json` - Fix org_level "Division" → "division", add personnel (0)
6. ❌ `german_1941q2_15_panzer_division_toe.json` (203201) - Fix personnel mismatch (15000 vs 14000)

**Cleanup** (1 unit):
7. 🗑️ `italian_1941q1_55a_divisione_di_fanteria_savona_toe.json` (308971) - DELETE (superseded by 80% version)

---

### Phase 2: Low Confidence (13 units)

**Batch 1 - German** (3 units):
8. ⚠️ `german_1941q2_15_panzer_division_toe.json` (065701) - 65% → 78%+
9. ⚠️ `german_1941q3_21_panzer_division_toe.json` - 70% → 78%+ (after Phase 1)
10. ⚠️ `german_1943q1_10_panzer_division_toe.json` - 72% → 78%+

**Batch 2 - Italian** (5 units):
11. ⚠️ `italian_1940q2_63a_divisione_di_fanteria_cirene_toe.json` - 68% → 78%+
12. ⚠️ `italian_1940q4_132_divisione_corazzata_ariete_toe.json` - 72% → 78%+
13. ⚠️ `italian_1941q3_25th_infantry_division_bologna_toe.json` - 72% → 78%+
14. ⚠️ `italian_1940q2_62_divisione_di_fanteria_marmarica_toe.json` - 72% → 78%+
15. ⚠️ `italian_1940q2_61_divisione_di_fanteria_sirte_toe.json` - 72% → 78%+

**Batch 3 - British/Commonwealth** (4 units):
16. ⚠️ `british_1941q2_1st_south_african_infantry_division_toe.json` - 72% → 78%+
17. ⚠️ `british_1940q2_4th_indian_infantry_division_toe.json` - 72% → 78%+
18. ⚠️ `british_1941q1_1st_south_african_infantry_division_toe.json` - 72% → 78%+
19. ⚠️ `german_1942q4_90_leichte_afrika_division_toe.json` - 72% → 78%+

**Batch 4 - French** (1 unit):
20. ⚠️ `french_1943q1_1re_division_fran_aise_libre_toe.json` - 72% → 78%+

---

### Phase 3: Commander Research (6 units)

**Italian Divisions** (6 units - all Unknown commanders):
21. 🔍 `italian_1941q2_101_divisione_motorizzata_trieste_toe.json` - Find Q2 commander
22. 🔍 `italian_1942q2_133rd_littorio_armored_division_toe.json` - Research Q2 commander
23. 🔍 `italian_1942q3_133a_divisione_corazzata_littorio_toe.json` - Research Q3 commander
24. 🔍 `italian_1942q4_133a_divisione_corazzata_littorio_toe.json` - Research Q4 commander
25. 🔍 `italian_1942q4_185a_divisione_paracadutisti_folgore_toe.json` - Research Folgore commander
26. 🔍 `italian_1943q1_131_divisione_corazzata_centauro_toe.json` - Research Centauro commander

---

## ⚡ Quick Start Guide

### Option 1: Execute Full Plan (Recommended)
```bash
# Read the detailed plan
cat UPGRADE_PLAN_v3.0.md

# Confirm to begin
# Human: "Begin Phase 1 Quick Fixes"
```

### Option 2: Phase-by-Phase
```bash
# Phase 1 only (2-3 hours)
# Human: "Execute Phase 1 Quick Fixes"

# Then validate
npm run qa:v3

# Proceed to Phase 2 after review
```

### Option 3: Cherry Pick Issues
```bash
# Fix just schema types (30 mins)
# Human: "Fix all invalid schema_type issues"

# Or fix just one unit
# Human: "Regenerate Western Desert Force with proper schema"
```

---

## 📈 Progress Tracking

### Execution Status

**Phase 1: Quick Fixes**
- [ ] 4 schema_type corrections
- [ ] 2 full regenerations (0% confidence)
- [ ] 3 data quality fixes
- [ ] 1 file deletion
- **Progress**: 0/8 complete

**Phase 2: Low Confidence**
- [ ] Batch 1: German (3 units)
- [ ] Batch 2: Italian (5 units)
- [ ] Batch 3: British (4 units)
- [ ] Batch 4: French (1 unit)
- **Progress**: 0/13 complete

**Phase 3: Commander Research**
- [ ] Littorio (3 quarters)
- [ ] Folgore (1 quarter)
- [ ] Trieste (1 quarter)
- [ ] Centauro (1 quarter)
- **Progress**: 0/6 complete

**Overall Progress**: 0/25 units fixed (0%)

---

## 🎯 Expected Results

### Before Upgrade
```
Validation Summary:
  Total:      158 files
  ✅ Passed:  133 (84.2%)
  ❌ Failed:  0 (0.0%)
  ⚠️  Warn:   25 (15.8%)

Issues:
  - 4 invalid schema types
  - 13 low confidence scores
  - 6 unknown commanders
  - 3 data quality errors
```

### After Upgrade
```
Validation Summary:
  Total:      158 files
  ✅ Passed:  158 (100%) ← Perfect!
  ❌ Failed:  0 (0.0%)
  ⚠️  Warn:   0 (0.0%)   ← All fixed!

Quality:
  - All schema types correct
  - All confidence ≥75%
  - Most commanders identified
  - Zero calculation errors
```

---

## 💡 Key Insights

### Why These Units Have Warnings

1. **Schema Type Issues**: Created before v3.0 standardization
2. **Low Confidence**: Extracted with limited source access
3. **Unknown Commanders**: Italian sources less accessible than German/British
4. **Data Errors**: Early extractions before validation tightened

### Why This Matters

- **Publication Quality**: 100% pass rate demonstrates professional standards
- **Data Integrity**: All calculations verified and correct
- **Source Quality**: Enhanced confidence from better sourcing
- **Completeness**: Commander data adds historical value

---

## 📚 Resources

### Documentation
- `UPGRADE_PLAN_v3.0.md` - Detailed execution plan (this summary)
- `schemas/unified_toe_schema.json` - v3.0 schema definition
- `data/SCHEMA_VALIDATION_REPORT.json` - Current validation status

### Commands
```bash
# Validate all units
npm run qa:v3

# Check schema v3.0 only
npm run validate:v3

# Check for Wikipedia sources
npm run validate:sources
```

### Source References
- **German**: Tessin Wehrmacht Encyclopedia (local), Feldgrau.com
- **Italian**: TM E 30-420 (local), Comando Supremo, Nafziger Collection
- **British**: British Army Lists (local), unit war diaries
- **French**: Niehorster.org, Free French archives

---

## ✅ Success Criteria Checklist

### Mandatory (Must Have)
- [ ] All 25 units pass validation (0 warnings)
- [ ] All schema_type values correct
- [ ] All confidence scores ≥75% or documented as unavailable
- [ ] Zero calculation errors
- [ ] Superseded files deleted

### Target (Should Have)
- [ ] 20+ units reach ≥75% confidence
- [ ] 4+ commanders identified
- [ ] All data quality issues resolved
- [ ] Git commits with clear messages

### Stretch (Nice to Have)
- [ ] All 25 units reach ≥78% confidence
- [ ] All 6 commanders identified
- [ ] MDBook chapters regenerated for upgraded units
- [ ] Documentation updated

---

## 🚀 Ready to Start?

**Next Action**: Review `UPGRADE_PLAN_v3.0.md` for detailed execution steps

**Start Command**:
```
"Begin Phase 1 Quick Fixes - execute the 8 unit upgrades"
```

**Estimated Time**: 9-13 hours total (can be done in phases)

**Expected Outcome**: 158/158 units passing (100%) ✅

---

*Upgrade plan created: 2025-10-13*
*Status: Ready for execution*
*Target: 100% validation pass rate*
