# Misplaced JSON Files Report

## Files in WRONG Location

### 1. Root of data/output (should be in session/units/ folder)

❌ `data/output/1st_Armoured_Division_1941Q4_Research_Report.json`
❌ `data/output/5_leichte_division_1941q1_tessin_extraction.json`
❌ `data/output/ariete_q2_1941_research.json`
❌ `data/output/historical_research_panzer_regiment_5_1941q1_variants.json`

**Issue**: Research/extraction files not in proper session folders

---

### 2. Session Folders Missing units/ Subdirectory

❌ `data/output/autonomous_20251012_101348/italian_1941q4_61_divisione_motorizzata_trento_toe.json`
   → Should be: `data/output/autonomous_20251012_101348/units/italian_1941q4_61_divisione_motorizzata_trento_toe.json`

❌ `data/output/autonomous_20251012_panzerarmee_afrika/german_1942q1_panzerarmee_afrika_toe.json`
   → Should be: `data/output/autonomous_20251012_panzerarmee_afrika/units/german_1942q1_panzerarmee_afrika_toe.json`

❌ `data/output/autonomous_20421012/british_1942q1_8th_army_toe.json`
   → Should be: `data/output/autonomous_20421012/units/british_1942q1_8th_army_toe.json`

❌ `data/output/autonomous_21pz_1941q4/german_1941q4_21_panzer_division_toe.json`
   → Should be: `data/output/autonomous_21pz_1941q4/units/german_1941q4_21_panzer_division_toe.json`

**Issue**: Unit JSON files saved directly to session folder instead of units/ subfolder

---

## Files in CORRECT Location (Archive - Ignore)

### Wikipedia Source Archive (9 files in 1941-q2-showcase/wikipedia_versions/)
✅ These are the Wikipedia source files mentioned - IGNORE as instructed
   - british_1941q2_1st_south_african_infantry_division_toe.json
   - british_1941q2_2nd_new_zealand_division_toe.json
   - british_1941q2_4th_indian_infantry_division_toe.json
   - british_1941q2_5th_indian_infantry_division_toe.json
   - british_1941q2_7th_armoured_division_toe.json
   - german_1941q2_15_panzer_division_toe.json
   - italian_1941q2_132_divisione_corazzata_ariete_toe.json
   - italian_1941q2_25_divisione_di_fanteria_bologna_toe.json
   - italian_1941q2_60_divisione_di_fanteria_sabratha_toe.json

### Special Folders (Intentional)
✅ `data/output/_archived/` - Archive folder with aircraft/battle data
✅ `data/output/1941-q2-showcase/consolidated_units/` - Consolidated showcase units
✅ `data/output/qa_reports/` - QA analysis reports
✅ `orchestration_metadata.json` files - Session metadata (correct location)

---

## Summary

**Total Misplaced**: 8 files
- 4 research/extraction files in root
- 4 unit files missing units/ subfolder

**Recommendation**:
1. Move root research files to appropriate session/research/ folders
2. Create units/ folders and move misplaced unit files
3. Keep Wikipedia archive and special folders as-is

