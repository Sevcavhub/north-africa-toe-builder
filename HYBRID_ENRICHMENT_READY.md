# Hybrid Enrichment Setup Complete

**Date**: November 6, 2025
**Status**: ✅ Templates and scripts ready for user data entry
**Estimated Time**: 2-3 hours total

---

## What's Ready

### 1. Enrichment CSV Templates ✅

**Canadian guns** (10 guns):
- File: `canadian_guns_enrichment.csv`
- Gun names pre-filled
- 8 columns to fill: HE range bands (6), HE classification, ROF

**German guns** (16 guns):
- File: `german_guns_enrichment.csv`
- Gun names pre-filled
- 8 columns to fill: HE range bands (6), HE classification, ROF

### 2. Import Script ✅

- File: `scripts/battlegroup/manual_extraction/enrich_scraped_guns.py`
- Updates ONLY missing fields (preserves existing data)
- Validates gun name matching
- Generates enrichment report

### 3. Instructions ✅

- File: `ENRICHMENT_INSTRUCTIONS.md`
- Column-by-column guidance
- Example entries
- Quick reference tables
- Common mistakes to avoid

---

## Your Workflow

### Step 1: Fill Canadian Guns (45-60 minutes)

1. Open `canadian_guns_enrichment.csv` in Excel
2. Reference Crucible PDF (Canadian DataCards section)
3. Fill 8 columns for 10 guns:
   - `he_0_10` through `he_50_70` (HE range bands)
   - `he_shell_classification` (v. light, light, medium, heavy, etc.)
   - `rof` (1-10, leave blank if not visible)

**Example row for 25 pdr**:
```csv
25 pdr,3,3,3,3,3,,medium,2
```

### Step 2: Import Canadian Guns (5 minutes)

```bash
python scripts/battlegroup/manual_extraction/enrich_scraped_guns.py \
    --csv canadian_guns_enrichment.csv \
    --nation canadian
```

### Step 3: Fill German Guns (60-90 minutes)

1. Open `german_guns_enrichment.csv` in Excel
2. Reference Crucible PDF (German DataCards section)
3. Fill 8 columns for 16 guns (same process as Canadian)

### Step 4: Import German Guns (5 minutes)

```bash
python scripts/battlegroup/manual_extraction/enrich_scraped_guns.py \
    --csv german_guns_enrichment.csv \
    --nation german
```

### Step 5: Manual Review

**Run audit to verify improvement**:
```bash
python scripts/battlegroup/manual_extraction/audit_scraped_data.py
```

**Expected after enrichment**:
- Canadian guns: HE range bands 100% (was 0%)
- Canadian guns: HE classification 100% (was 0%)
- German guns: HE range bands 100% (was 0%)
- German guns: HE classification 100% (was 0%)

---

## What Gets Updated

### Before Enrichment (Canadian 25 pdr example):
```
name: 25 pdr
caliber_mm: 88
he_dice: 10
he_target: D6
he_0_10: NULL       ← Missing
he_10_20: NULL      ← Missing
he_20_30: NULL      ← Missing
he_30_40: NULL      ← Missing
he_40_50: NULL      ← Missing
he_50_70: NULL      ← Missing
he_shell_classification: NULL  ← Missing
rof: NULL           ← Missing
```

### After Enrichment:
```
name: 25 pdr
caliber_mm: 88
he_dice: 10
he_target: D6
he_0_10: 3          ← ENRICHED
he_10_20: 3         ← ENRICHED
he_20_30: 3         ← ENRICHED
he_30_40: 3         ← ENRICHED
he_40_50: 3         ← ENRICHED
he_50_70: NULL      (no value at this range)
he_shell_classification: medium  ← ENRICHED
rof: 2              ← ENRICHED
```

---

## Quick Reference

### Key Files

| File | Purpose | Status |
|------|---------|--------|
| `canadian_guns_enrichment.csv` | Canadian data entry | ⏳ USER FILLS |
| `german_guns_enrichment.csv` | German data entry | ⏳ USER FILLS |
| `enrich_scraped_guns.py` | Import script | ✅ READY |
| `ENRICHMENT_INSTRUCTIONS.md` | Detailed guidance | ✅ READY |
| `audit_scraped_data.py` | Validation script | ✅ READY |

### Column Definitions

| Column | What It Is | Example Values |
|--------|------------|----------------|
| he_0_10 | HE effectiveness 0-10" | 3, 6, 9, 15, D6 |
| he_10_20 | HE effectiveness 10-20" | 3, 6, 9, 15 |
| he_20_30 | HE effectiveness 20-30" | 3, 6, 9, 15 |
| he_30_40 | HE effectiveness 30-40" | 3, 6, 9, 15 |
| he_40_50 | HE effectiveness 40-50" | 3, 6, 9, 15 |
| he_50_70 | HE effectiveness 50-70" | 3, 6, 9 |
| he_shell_classification | Shell weight class | v. light, light, medium, heavy, bomb, rocket, Cannon |
| rof | Rate of Fire (1-10) | 1, 2, 3, 6, 8, 10 |

### Tips

**Finding HE ranges on datacards**:
- Look for row like: `HE: 3 / 3 / 3 / 3 / 3 / -`
- Each slash-separated value is a range band
- `-` means no effect (leave CSV cell blank)

**Finding HE classification**:
- Usually in datacard header or title
- 37-50mm: "v. light"
- 57-76mm: "light"
- 87-105mm: "medium"
- 114mm+: "heavy"

**Finding ROF**:
- Check datacard stats section
- If not visible, leave blank (OK to skip)

---

## What This Achieves

### Data Completeness Improvement

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Canadian HE ranges | 0% | 100% | +100% |
| Canadian HE class | 0% | 100% | +100% |
| Canadian ROF | 0% | ~80% | +80% |
| German HE ranges | 0% | 100% | +100% |
| German HE class | 0% | 100% | +100% |
| German ROF | 0% | ~80% | +80% |

### Publication Quality

**Before**: Cannot generate datacards (missing critical fields)
**After**: Can generate publication-ready datacards (90%+ complete)

---

## Next Steps After Enrichment

1. ✅ **Manual review** - Verify enriched data looks correct
2. **British aircraft** - Fill british_datacards_ALL_AIRCRAFT.csv (optional)
3. **Phase 9B equipment linkage** - Link 469 WITW items to reference data (currently 20%)
4. **Generate datacards** - Create equipment cards for all 4 books
5. **Publication** - Export final PDFs

---

**Ready to start!** Open the CSVs and begin filling. Reference `ENRICHMENT_INSTRUCTIONS.md` for detailed guidance.

**Estimated time**: 2-3 hours for both Canadian and German enrichment.
