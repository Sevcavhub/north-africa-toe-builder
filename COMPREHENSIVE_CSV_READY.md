# Comprehensive Gun CSVs Ready for QA

**Date**: November 6, 2025
**Status**: ✅ Exported and ready for your QA/editing
**Estimated Time**: 2.5 hours total

---

## Files Ready

### 1. Canadian Guns ✅
- **File**: `canadian_guns_comprehensive.csv`
- **Guns**: 10 guns with ALL 47 columns
- **Current state**:
  - ✅ Name, caliber, HE dice, AP values (60-100% complete)
  - ❌ HE range bands (0% - need to fill)
  - ❌ HE classification (0% - need to fill)
  - ❌ ROF (0% - need to fill)

### 2. German Guns ✅
- **File**: `german_guns_comprehensive.csv`
- **Guns**: 16 guns with ALL 47 columns
- **Current state**:
  - ✅ Name, caliber, HE dice, AP values (94-100% complete)
  - ❌ HE range bands (0% - need to fill)
  - ❌ HE classification (0% - need to fill)
  - ❌ ROF (0% - need to fill)

### 3. Import Script ✅
- **File**: `scripts/battlegroup/manual_extraction/import_guns_comprehensive.py`
- **Function**: Updates database from edited CSV
- **Features**:
  - Matches by ID (reliable)
  - Updates ALL fields
  - Shows what changed
  - Preserves existing data if no changes

### 4. QA Guide ✅
- **File**: `COMPREHENSIVE_GUN_QA_GUIDE.md`
- **Content**:
  - Column-by-column guide (47 columns)
  - Critical fields to focus on
  - Examples for each nation
  - Common mistakes to avoid
  - Validation checklist

---

## What You Can Do

### Option 1: Full QA + Enrichment (Recommended - 2.5 hours)
1. **QA existing data** - Verify scraped caliber, HE dice, AP values are correct
2. **Fix errors** - Correct any mistakes you find
3. **Fill missing** - Add HE ranges, classification, ROF
4. **Enrich** - Add common names, special rules

### Option 2: Quick Fill Missing Only (1.5 hours)
1. **Skip QA** - Assume scraped data is correct
2. **Fill only**: HE ranges (columns 31-36), classification (column 38), ROF (column 39)
3. **Import** - Update database

### Option 3: Spot QA (2 hours)
1. **QA sample** - Check 3-4 guns per nation in detail
2. **Fill missing** - Add all missing fields
3. **Trust rest** - Assume scraper got remaining guns right

---

## Critical Columns to Fill

**These 8 columns are 0% populated** (must fill):

| Column # | Name | Example | Find in PDF |
|----------|------|---------|-------------|
| 36 | he_0_10 | 3, 6, 9, 15 | HE range row (first value) |
| 31 | he_10_20 | 3, 6, 9, 15 | HE range row (second value) |
| 32 | he_20_30 | 3, 6, 9, 15 | HE range row (third value) |
| 33 | he_30_40 | 3, 6, 9, 15 | HE range row (fourth value) |
| 34 | he_40_50 | 3, 6, 9, 15 | HE range row (fifth value) |
| 35 | he_50_70 | 3, 6, 9 | HE range row (sixth value) |
| 38 | he_shell_classification | v. light, light, medium, heavy | Datacard header |
| 39 | rof | 1, 2, 3, 6, 8, 10 | Datacard stats section |

---

## Quick Start

### 1. Open CSV (Canadian first)
```bash
# Open in Excel or your preferred spreadsheet app
canadian_guns_comprehensive.csv
```

### 2. Reference PDF
- Open: `Resource Documents/Battlegroup Game/Canada's Crucible.pdf`
- Find: Canadian DataCards section
- For each gun, locate the datacard

### 3. Fill Critical Columns
**For each of 10 guns**:
- Check existing data (columns 4, 6, 7, 8-13)
- Fill HE ranges (columns 31-36)
- Fill classification (column 38)
- Fill ROF (column 39)

### 4. Import
```bash
python scripts/battlegroup/manual_extraction/import_guns_comprehensive.py \
    --csv canadian_guns_comprehensive.csv \
    --nation canadian
```

### 5. Repeat for German
Same process, 16 guns instead of 10.

---

## Example: One Gun Start to Finish

**Canadian 25 pdr** (row 4 in CSV):

### Step 1: QA Existing Data
- Column 2 (name): "25 pdr" ✓
- Column 4 (caliber_mm): 88 ✓ (87.6mm rounds to 88)
- Column 6 (he_dice): 10 ✓
- Column 7 (he_target): "D6" ✓
- Columns 8-13 (AP): 6, 6, 5, 4, 3, (blank) ✓

**Result**: All existing data correct, no fixes needed

### Step 2: Find on PDF
- Open Canada's Crucible PDF
- Find 25 pdr datacard
- Note HE range row: `3 / 3 / 3 / 3 / 3 / -`
- Note header: "medium"
- Note stats: ROF 2

### Step 3: Fill Missing Data
- Column 36 (he_0_10): **3**
- Column 31 (he_10_20): **3**
- Column 32 (he_20_30): **3**
- Column 33 (he_30_40): **3**
- Column 34 (he_40_50): **3**
- Column 35 (he_50_70): **(leave blank)** (dash on datacard)
- Column 38 (he_shell_classification): **medium**
- Column 39 (rof): **2**

### Step 4: Save
Save the CSV, move to next gun.

**Repeat 9 more times for Canadian**, then 16 times for German.

---

## Column Order Warning ⚠️

**HE range columns are NOT in sequence!**

When datacard shows: `3 / 3 / 3 / 3 / 3 / -`

Fill in this order:
1. Column **36** (he_0_10) = 3 (FIRST value)
2. Column **31** (he_10_20) = 3 (SECOND value)
3. Column **32** (he_20_30) = 3 (THIRD value)
4. Column **33** (he_30_40) = 3 (FOURTH value)
5. Column **34** (he_40_50) = 3 (FIFTH value)
6. Column **35** (he_50_70) = (blank) (SIXTH value is dash)

**Why**: Database columns were added in different order than logical range sequence.

---

## After Import

### Validation
```bash
# Run audit to verify 100% completion
python scripts/battlegroup/manual_extraction/audit_scraped_data.py
```

**Expected results**:
```
Canadian guns:
  HE range bands: 100% (was 0%)
  HE classification: 100% (was 0%)
  ROF: 80-100% (was 0%)

German guns:
  HE range bands: 100% (was 0%)
  HE classification: 100% (was 0%)
  ROF: 80-100% (was 0%)
```

### If Issues Found
1. Check import output for errors
2. Re-edit CSV to fix
3. Re-run import script
4. Repeat validation

---

## Files Created

| File | Purpose | Size |
|------|---------|------|
| `canadian_guns_comprehensive.csv` | Canadian guns data | 10 rows × 47 cols |
| `german_guns_comprehensive.csv` | German guns data | 16 rows × 47 cols |
| `export_guns_comprehensive.py` | Export script | Used to create CSVs |
| `import_guns_comprehensive.py` | Import script | Updates database |
| `COMPREHENSIVE_GUN_QA_GUIDE.md` | Detailed guide | 11KB |
| `COMPREHENSIVE_CSV_READY.md` | This file | Quick reference |

---

## Next Steps

1. **Now**: Open CSVs and start QA/filling
2. **After Canadian**: Import Canadian, verify results
3. **After German**: Import German, verify results
4. **Then**: British aircraft enrichment OR Phase 9B equipment linkage

---

**Estimated Total Time**: 2.5 hours (60 min Canadian + 90 min German)

**Ready to start!** Open `canadian_guns_comprehensive.csv` and reference `COMPREHENSIVE_GUN_QA_GUIDE.md` for detailed instructions.
