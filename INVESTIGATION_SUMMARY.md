# File Count Disparity Investigation Summary

**Date**: 2025-10-26
**Investigator**: Claude (Autonomous Agent)
**Issue**: Discrepancy between expected unit count (414), WORKFLOW_STATE count (424), and actual files (428)

---

## 🔍 Root Cause Identified

The file count disparity was caused by **THREE systemic issues**:

### 1. Duplicate Files (28 files)

**Cause**: Extraction agents created multiple files for the same seed unit using different naming conventions.

**Examples**:
- `british_1941q1_1st_south_african_division_toe.json` ✅ Canonical
- `british_1941q1_1st_south_african_infantry_division_toe.json` ❌ Duplicate (added "infantry")

- `german_1941q1_deutsches_afrikakorps_toe.json` ✅ Canonical
- `german_1941q1_deutsches_afrika_korps_toe.json` ❌ Duplicate (space in "afrika korps")

- `italian_1940q2_sabratha_division_toe.json` ✅ Canonical (English)
- `italian_1940q2_60_divisione_di_fanteria_sirte_toe.json` ❌ Duplicate (Italian)

**Impact**: 28 duplicate files across 26 seed units

---

### 2. Orphaned Files (28 files)

**Cause**: Files created for units NOT in the seed file, or using incorrect quarters.

**Categories**:

**A. Units Destroyed in 1940-Q4** (Should NOT exist in 1941-Q1):
- `italian_1941q1_1_divisione_ccnn_23_marzo_toe.json`
- `italian_1941q1_2_divisione_ccnn_28_ottobre_toe.json`
- `italian_1941q1_4_divisione_ccnn_3_gennaio_toe.json`
- `italian_1941q1_1_divisione_libica_toe.json`
- `italian_1941q1_2_divisione_libica_toe.json`

**Note**: These units were already removed from seed file on 2025-10-24. Files are orphaned extractions from before the correction.

**B. German Naming Variant** (6 files):
- `german_*_90_leichte_afrika_division_toe.json` (1941q3, 1941q4, 1942q1, 1942q3, 1942q4)
- Seed expects: "90. leichte Division"
- Files have: "90. leichte Afrika-Division" (added "Afrika")

**C. Italian Naming Variants** (14 files):
- Italian language names instead of canonical English
- `101_divisione_motorizzata_trieste` vs `101st_trieste_division`
- `10_armata` / `10a_armata` vs `10_armata_italian_10th_army`
- `xxi_corpo_d_armata` vs expected with English suffix

**D. Other Issues** (3 files):
- `british_1942q4_46_infantry_division_toe.json` - Missing "th" (should be 46th)
- `french_1942q3_1ere_brigade_francaise_libre_toe.json` - Accent variation
- `british_1941q3_6th_australian_division_2nd_aif_toe.json` - Parenthesis issue

---

### 3. Non-Normalized WORKFLOW_STATE.json Entries

**Cause**: `session:end` script stored filenames as-is, without normalizing to canonical IDs.

**Examples from WORKFLOW_STATE.json**:
```json
"british_1940q4_1_south_african_division",          // Missing "st"
"british_1940q4_1st_south_african_division",        // Correct, but duplicate
"british_1942q1_2nd South African Division",        // HAS SPACES! Not normalized!
```

**Impact**:
- 424 entries in WORKFLOW_STATE.json
- Many duplicates (same unit with different naming)
- Created false "101.9%" completion rate

---

## 📊 Actual Numbers (After Reconciliation)

| Metric | Count | Notes |
|--------|-------|-------|
| **Expected (seed file)** | 414 | Per north_africa_seed_units_COMPLETE.json |
| **Canonical IDs generated** | 411 | 3 units failed to generate canonical IDs (special chars) |
| **Actual files** | 428 | Files in data/output/units/ |
| **Matched to seed** | 372 | Using fuzzy matching |
| **Duplicate files** | 28 | Multiple files for same seed unit |
| **Orphaned files** | 28 | Files not matching ANY seed unit |
| **TRUE completion** | **89.9%** | 372/411 complete |

---

## ✅ Fixes Applied

### 1. Reconciled WORKFLOW_STATE.json
- **Created**: 2025-10-26
- **Action**: Ran `scripts/reconcile_workflow_state.js`
- **Result**:
  - Removed all duplicates
  - Normalized all entries to canonical IDs
  - Backed up old version to `WORKFLOW_STATE.json.backup`
  - Updated completion: 424 → 372 (TRUE count)
  - Updated percentage: 101.9% → 89.9%

### 2. Generated Detailed Report
- **Location**: `data/output/qa_reports/reconciliation_report.json`
- **Contents**:
  - Full list of duplicates (26 units, 28 files)
  - Full list of orphaned files (28 files)
  - File-to-seed mapping (for all 428 files)
  - Seed-to-files mapping (shows duplicates clearly)

---

## 🔧 Required Next Steps

### Immediate Actions

**1. Delete Orphaned Files** (28 files)
- Units destroyed in 1940-Q4 (5 files) - confirmed should not exist
- German "Afrika-Division" naming variants (6 files) - duplicates
- Italian naming variants (14 files) - duplicates
- Other naming issues (3 files) - need individual review

**2. Delete Duplicate Files** (28 files)
- Keep canonical English version
- Delete all variants (Italian names, spacing issues, extra words)

**3. Investigate Seed File Issues**
- Why do only 411 canonical IDs generate from 414 expected?
- Likely: 3 units have special characters that break normalization
- Need to identify and fix these

**4. Fix Session:End Script**
- Update `scripts/session_end.js` to store canonical IDs only
- Use `naming_standard.normalizeDesignation()` before storing
- Prevent future duplicates

**5. Enforce Canonical Paths in Extraction Agents**
- Update agent prompts to require use of `canonical_paths.js`
- Pass pre-normalized designations from seed file
- Add validation step before creating files

---

## 📋 Detailed File Lists

### Duplicate Files to Delete (28 files)

Keep the first file (canonical), delete the second:

```
british_1941q1_1st_south_african_infantry_division_toe.json (keep: _1st_south_african_division)
british_1941q2_1st_south_african_infantry_division_toe.json (keep: _1st_south_african_division)
british_1941q2_5th_indian_infantry_division_toe.json (keep: _5th_indian_division)
british_1942q4_x_corps_toe.json (keep: _xxx_corps)
german_1941q1_deutsches_afrika_korps_toe.json (keep: _deutsches_afrikakorps, no space)
german_1941q2_deutsches_afrikakorps_dak_toe.json (keep: _deutsches_afrikakorps)
german_1942q1_panzerarmee_afrika_toe.json (keep: _panzergruppe_afrika)
italian_1940q2_60_sabratha_division_toe.json (keep: _sabratha_division without number)
italian_1940q2_61_divisione_di_fanteria_sirte_toe.json (keep: _sirte_division)
italian_1940q2_62_divisione_di_fanteria_marmarica_toe.json (keep: _marmarica_division)
... (18 more - see reconciliation_report.json for complete list)
```

### Orphaned Files to Delete or Review (28 files)

**DELETE - Destroyed units (5 files)**:
```
italian_1941q1_1_divisione_ccnn_23_marzo_toe.json
italian_1941q1_2_divisione_ccnn_28_ottobre_toe.json
italian_1941q1_4_divisione_ccnn_3_gennaio_toe.json
italian_1941q1_1_divisione_libica_toe.json
italian_1941q1_2_divisione_libica_toe.json
```

**DELETE - German naming duplicates (6 files)**:
```
german_1941q3_90_leichte_afrika_division_toe.json
german_1941q4_90_leichte_afrika_division_toe.json
german_1942q1_90_leichte_afrika_division_toe.json
german_1942q3_90_leichte_afrika_division_toe.json
german_1942q3_164_leichte_afrika_division_toe.json
german_1942q4_90_leichte_afrika_division_toe.json
```

**DELETE - Italian naming duplicates (14 files)**:
```
italian_1940q2_10_armata_toe.json
italian_1940q3_10a_armata_toe.json
italian_1940q3_10_armata_toe.json
italian_1941q1_xxi_corpo_d_armata_toe.json
italian_1941q2_60_divisione_di_fanteria_sabratha_toe.json
italian_1941q3_101_divisione_motorizzata_trieste_toe.json
italian_1941q4_101_divisione_motorizzata_trieste_toe.json
italian_1941q4_divisione_motorizzata_trieste_toe.json
italian_1941q4_xx_corps_toe.json
italian_1942q3_101_divisione_motorizzata_trieste_toe.json
italian_1942q4_101_divisione_motorizzata_trieste_toe.json
... (3 more)
```

**REVIEW - Potential issues (3 files)**:
```
british_1940q4_1_south_african_division_toe.json (missing "st")
british_1941q3_6th_australian_division_2nd_aif_toe.json (parenthesis issue?)
british_1942q4_46_infantry_division_toe.json (missing "th")
french_1942q3_1ere_brigade_francaise_libre_toe.json (accent variation)
french_1943q1_division_de_marche_du_maroc_toe.json (naming issue)
```

---

## 🎯 Long-Term Solutions

### 1. Enforce Canonical Naming Standard

**Create**: `scripts/lib/unit_file_manager.js`
- Single function to create unit files
- Takes: nation, quarter, seed_designation
- Returns: canonical filename using naming_standard.js
- Used by ALL extraction agents

### 2. Add File Validation Hook

**Create**: Pre-commit hook to validate filenames
- Check all `*_toe.json` files match canonical naming
- Reject commits with non-canonical filenames
- Prevent future drift

### 3. Update Agent Prompts

**Modify**: Agent catalog and extraction prompts
- Explicitly require use of `canonical_paths.js`
- Provide pre-normalized designation from seed
- Add example code showing correct usage

### 4. Add Reconciliation to Checkpoint

**Modify**: `scripts/checkpoint.js`
- Run reconciliation after validation
- Warn if duplicates or orphans detected
- Prevent marking units complete if naming issues exist

---

## 📈 Impact on Project Progress

**Before Investigation**:
- Reported: 424/416 complete (101.9%) ❌ WRONG
- Actual files: 428
- Confusion about "extra" units

**After Reconciliation**:
- Actual: 372/411 complete (89.9%) ✅ CORRECT
- Clear understanding of remaining work
- Path forward to fix issues

**Remaining Work**:
- 39 units to complete (411 - 372)
- Plus: Fix 3 units that failed to generate canonical IDs
- Plus: Clean up 56 duplicate/orphaned files

---

## 📝 Recommendations

### Priority 1: Clean Up (Immediate)
1. ✅ Reconcile WORKFLOW_STATE.json (DONE)
2. ⏳ Delete 56 duplicate/orphaned files (script ready to create)
3. ⏳ Investigate 3 units failing to generate canonical IDs

### Priority 2: Prevent Recurrence (This Session)
1. ⏳ Update session:end to store canonical IDs
2. ⏳ Update agent prompts to enforce canonical_paths.js
3. ⏳ Add filename validation to checkpoint

### Priority 3: Complete Extraction (Ongoing)
1. ⏳ Continue processing 39 remaining units
2. ⏳ Regenerate work queue after cleanup
3. ⏳ Validate all files with QA pipeline

---

**Investigation completed**: 2025-10-26T14:30:00Z
**Tools used**: reconcile_workflow_state.js, investigate_extra_files.js
**Reports generated**: reconciliation_report.json
**Status**: ROOT CAUSE IDENTIFIED, FIXES IN PROGRESS
