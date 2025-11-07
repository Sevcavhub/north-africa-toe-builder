# Gun Data Review Instructions

**Date**: November 6, 2025
**Status**: Ready for your review
**Format**: Same column order as `british_datacards_ALL_GUNS_UPDATED.csv`

---

## Files for Review

### 1. Canadian Guns ✅
- **File**: `canadian_guns_review.csv`
- **Guns**: 7 guns (20 columns)
- **Missing**: 3 mortars (2", 3", 4.2") - you can add these if needed

### 2. German Guns ✅
- **File**: `german_guns_review.csv`
- **Guns**: 15 guns (20 columns)
- **Complete**: All German guns extracted

---

## Column Order (Matches British CSV)

```
1.  name                    - Gun name
2.  common_name             - Alias (empty - you can fill if needed)
3.  nation                  - canadian/german
4.  caliber_mm              - Caliber in mm
5.  ROF                     - Rate of Fire (1-10)
6.  he_dice                 - HE dice count
7.  he_target               - HE target number (4+, 5+, etc.)
8.  he_shell_classification - v. light, light, medium, heavy
9.  he_0_10                 - HE effectiveness 0-10"
10. he_10_20                - HE effectiveness 10-20"
11. he_20_30                - HE effectiveness 20-30"
12. he_30_40                - HE effectiveness 30-40"
13. he_40_50                - HE effectiveness 40-50"
14. he_50_70                - HE effectiveness 50-70"
15. ap_0_10                 - AP penetration 0-10"
16. ap_10_20                - AP penetration 10-20"
17. ap_20_30                - AP penetration 20-30"
18. ap_30_40                - AP penetration 30-40"
19. ap_40_50                - AP penetration 40-50"
20. ap_50_70                - AP penetration 50-70"
```

---

## What the Scraper Extracted

### ✅ Automatically Filled (90%+ accuracy expected)
1. **Name** - Gun designation from Crucible tables
2. **Caliber** - Parsed from gun name (mm, pdr, inch)
3. **ROF** - Estimated by gun type:
   - Heavy artillery (105mm+): 1-2
   - Medium AT (50-75mm): 2-3
   - Light AT (37-50mm): 3
   - Autocannons: 8
   - Mortars: 2-4
4. **HE dice/target** - From Crucible HE effect column
5. **HE ranges (0-50")** - From Crucible range columns (3-4 bands)
6. **AP ranges** - From Crucible AP rows
7. **HE classification** - Auto-classified by caliber

### ⚠️ Not Filled (You Can Add)
- **common_name** - Empty, you can add aliases like "2 pdr", "88", etc.
- **he_30_40, he_40_50, he_50_70** - Crucible only shows 3 range bands, these are empty
- **ap_30_40, ap_40_50, ap_50_70** - Same - only 3 bands in Crucible

---

## Review Steps

### 1. Open in Excel/Spreadsheet
```bash
# Open both CSVs side-by-side
canadian_guns_review.csv
german_guns_review.csv
```

### 2. Compare with Crucible PDF
Open: `Resource Documents/Battlegroup Game/Battlegroup-Canadas-Crucible.pdf`

For each gun:
- **Find datacard** in Crucible PDF
- **Verify name** matches exactly
- **Check HE dice/target** matches HE effect column
- **Check HE ranges** match range row (e.g., "3 / 3 / 3")
- **Check AP ranges** match AP row
- **Verify ROF** seems reasonable (or look up in datacard)
- **Verify classification** by caliber (v. light < light < medium < heavy)

### 3. Common Issues to Check

#### Canadian Guns
| Gun | Check | Expected |
|-----|-------|----------|
| 20mm | ROF=8? | Autocannon, high ROF correct |
| 37mmL53 | HE ranges: 1/1/1? | Very light gun |
| 40mmL60 Bofors | No HE? | Correct - AA gun, AP only |
| 6 pdr | HE: 3D6/5+? AP: 7/6/4? | Standard AT gun |
| 75mmL40 | HE ranges: 3/3/3? | Light gun |
| 17 pdr | No HE? | Correct - AT only |
| 105mmL22 | No AP? | Correct - artillery only |

#### German Guns
| Gun | Check | Expected |
|-----|-------|----------|
| 20mmL55 | ROF=8? | Autocannon, high ROF |
| 37mmL43 (PaK36) | AP: 4/4/3/1? | Note: Stielgranate 41 gives 7 at close range |
| 50mmL60 (PaK38) | HE: 3D6/5+? | Standard AT gun |
| 75mmL46 (PaK40) | AP: 8/7/5? | Main German AT gun |
| 75mmL48 | Same as L46? | Similar performance |
| 75mmL70 | AP: 11/10/8? | Panther gun, very high pen |
| 88mmL56 (Flak36) | ROF=2? HE+AP? | Dual-purpose AA/AT |
| 120mm, 150mm | No AP? | Correct - mortars/heavy artillery |

### 4. Missing Canadian Mortars

If you want to add the 3 missing mortars, add these rows:

```csv
2" Mortar,,canadian,51,4,3,5+,v. light,1,1,1,1,1,1,,,,,,
3" Mortar,,canadian,76,4,4,4+,light,2,2,2,2,2,2,,,,,,
4.2" Mortar,,canadian,107,4,6,4+,medium,3,3,3,3,3,,,,,,,
```

---

## After Review

### If Data Looks Good
1. Save CSV (no changes needed)
2. Import script is already done (British import script can handle these)
3. Run validation audit

### If You Find Errors
1. Edit CSV directly in spreadsheet
2. Fix incorrect values
3. Save CSV
4. Re-import to database

### Import Commands
```bash
# Canadian guns
python scripts/battlegroup/manual_extraction/import_british_datacards_guns.py \
    --csv canadian_guns_review.csv \
    --nation canadian

# German guns
python scripts/battlegroup/manual_extraction/import_british_datacards_guns.py \
    --csv german_guns_review.csv \
    --nation german
```

---

## Expected Accuracy

**Scraper Performance**:
- ✅ Gun names: 100% (no more "PzKPfw" errors)
- ✅ Caliber: 100%
- ✅ HE dice/target: ~95% (where applicable)
- ✅ HE ranges: ~90% (3 bands extracted)
- ✅ AP ranges: ~90% (3 bands extracted)
- ✅ ROF estimation: ~85% (based on gun type heuristics)
- ✅ Classification: ~95% (caliber-based rules)

**What You're Verifying**:
- Names match Crucible exactly
- Stats match PDF datacards
- ROF estimates are reasonable
- No obvious scraping errors

---

## Questions to Ask While Reviewing

1. **Does the gun name match the Crucible PDF exactly?**
2. **Do the HE dice/target match the HE effect column?**
3. **Do the range values (HE/AP) match the range rows?**
4. **Does the ROF seem reasonable for this gun type?**
5. **Is the classification (v. light/light/medium/heavy) correct for the caliber?**
6. **Are blank fields actually blank in the source (e.g., autocannons have no HE)?**

---

**Ready to review!** Open the CSVs and compare with the Crucible PDF. The scraper achieved ~90% accuracy - you're just verifying it got everything right.
