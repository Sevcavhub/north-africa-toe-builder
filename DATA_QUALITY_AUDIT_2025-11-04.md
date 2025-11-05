# Data Quality Audit - bg_reference_guns Table
**Date**: November 4, 2025
**Status**: PHASE 9B SHOWSTOPPER
**Scope**: Complete audit of reference gun data used for HE/AP conversion formulas

---

## Executive Summary

**CRITICAL FINDING**: The bg_reference_guns table has catastrophic data quality issues affecting 70-100% of entries across all nations. This corrupted reference data invalidates all HE/AP conversion formulas and makes ~99 out of 191 populated equipment items (52%) potentially incorrect.

**Root Cause**: The datacard_scraper.py tool failed to properly extract gun table data from BattleGroup supplement PDFs, resulting in:
- Missing AP penetration values (70-100% missing across nations)
- Missing HE values (22-100% missing across nations)
- Garbage OCR text captured as gun names
- Quantity prefixes embedded in gun names

**Impact**: Cannot generate publication-quality equipment datacards until reference data is corrected.

---

## Detailed Findings by Nation

### German Guns (31 entries)
- **Missing ALL AP values**: 22 of 31 (70%)
- **Missing HE values**: 7 of 31 (22%)
- **Garbage entries**: 2 OCR errors

**Examples of Missing Data**:
```
Gun Name                       | HE    | AP Values (should have 6 range bands)
75mmL46 (PaK40)                | 4/4+  | ALL NULL (should be: -, 8, 8, 7, 6, 5, 4)
75mmL48                        | 4/4+  | ALL NULL
88mmL56 (Flak36)               | 4/3+  | ALL NULL
105mmL28                       | 5/3+  | ALL NULL
150mmL30                       | 7/3+  | ALL NULL
```

**Garbage OCR Entries**:
```
"At the base of the Seelow escarpment collections. In this case, the German 80mm mortar team"
"well covered by 88mm guns on the"
```

### American Guns (10 entries)
- **Missing HE values**: 10 of 10 (100%)
- **Missing AP values**: 10 of 10 (100%)
- **Garbage entries**: 1

**Garbage Entry**:
```
"Upgrade any LVT IV Buffalo with 20mm cannon"
```

### British Guns (9 entries)
- **Missing HE values**: 9 of 9 (100%)
- **Missing AP values**: 9 of 9 (100%)

### Soviet Guns (3 entries)
- **Missing HE values**: 3 of 3 (100%)
- **Missing AP values**: 3 of 3 (100%)
- **Malformed names**: ALL 3 have quantity prefixes

**Malformed Names**:
```
"4 122mm howitzers"              (quantity "4" prefix)
"2-3 4 152mm howitzers"          (double quantity prefix "2-3" and "4")
"4-6 4 203mm howitzers"          (double quantity prefix "4-6" and "4")
```

### Canadian Guns (4 entries)
- **Status**: Not yet audited

---

## Source Data Verification

### What the Data SHOULD Look Like

From user-provided images (Kursk German Gun1.png, Gun2.png), actual BattleGroup supplement tables show:

**Example: 75mmL46 (PaK40) - From Kursk Supplement**
```
Source PDF (Line 3084-3085 of Battlegroup-Kursk.txt):
  75mmL46 (PaK40)    HE      4/4+       3        3        3            3          3        3
                     AP        -        8        8        7            6          5        4
```

**What's in Database**:
```
Database entry:
  name: "75mmL46 (PaK40)"
  he_dice: 4
  he_target: "4+"
  ap_0_10: NULL
  ap_10_20: NULL
  ap_20_30: NULL
  ap_30_40: NULL
  ap_40_50: NULL
  ap_50_70: NULL
```

**Conclusion**: Source PDF text file has complete data, but scraper failed to extract AP values.

---

## Scraper Analysis

### File: scripts/battlegroup/scrapers/datacard_scraper.py

**Function**: `_extract_guns()` (lines 531-657)

**Critical Issues Identified**:

1. **Gun Name Regex Too Restrictive** (line 573)
   ```python
   gun_match = re.match(r'^(\d+mm\s*L?\d*)\s*(\([^)]+\))?\s+(HE|AP)', gun_line, re.IGNORECASE)
   ```
   - Requires gun name to START with caliber+barrel
   - Requires immediate HE or AP after gun designation
   - Many valid gun names don't match this pattern

2. **AP Line Extraction Failing**
   - Logic expects AP line immediately after HE line (line 614: `i += 1`)
   - Pattern `re.findall(r'(\d+|-)', ap_line)` should work
   - But only 9 of 31 German guns have AP data → 71% failure rate

3. **No Validation of Extracted Gun Names**
   - Accepts OCR garbage like "At the base of the Seelow escarpment..."
   - No checks for quantity prefixes ("4 122mm howitzers")
   - No minimum/maximum caliber validation

4. **Table Header Detection Issues**
   - Looks for "WEAPON" + "AMMO" + "HE EFFECT" + "RANGE" (line 543)
   - May be matching headers in different document sections
   - No validation that we're in the actual gun tables section

---

## Impact on Equipment Population

### Affected Equipment Items

**Phase 9B HE/AP Population Results** (from populate_he_ap_values.py):
- Total items: 469
- Items with HE/AP data: 191 (40.7%)
- **Items using corrupted reference data**: ~99 (52% of populated items)

**Breakdown by Method**:
1. **Method 1 (Reference Vehicle)**: 66 items
   - Uses: bg_reference_vehicles → equipment_guns → bg_reference_guns
   - **Corruption risk**: HIGH (depends on bg_reference_guns AP values)

2. **Method 2 (Reference Gun)**: 33 items
   - Uses: Direct lookup in bg_reference_guns
   - **Corruption risk**: CRITICAL (100% dependent on corrupted data)

3. **Method 3 (Formula/Name Parsing)**: 67 items
   - Uses: Caliber extraction + conversion formulas
   - Conversion formulas reverse-engineered from bg_reference_guns
   - **Corruption risk**: HIGH (formulas based on corrupted reference data)

4. **Method 4 (Manual Mapping)**: 66 items
   - Uses: manual_caliber_mapping.json + conversion formulas
   - **Corruption risk**: HIGH (formulas based on corrupted reference data)

**Examples of Potentially Incorrect Data**:
```
Equipment: GBR_CHEVROLET_C30_CMP (Truck, no gun)
  Database shows: HE 7/2+, AP: 11, 11, 10, 9, 8, 7
  Issue: Regex parsed "C30 CMP" as "30cm" = 300mm artillery!

Equipment: Ford F30 CMP (Truck, no gun)
  Similar issue: "F30" parsed as "30cm" = 300mm
```

---

## Recommended Solution

### Hybrid Approach (Manual Entry + Scraper Fix)

**Phase 1: Immediate Manual Entry** (2-3 hours)
1. Manually enter German gun data from Kursk supplement images (31 guns)
2. Clean up 3 garbage OCR entries
3. Validate against source images provided by user

**Phase 2: Scraper Enhancement** (3-4 hours)
1. Fix gun name regex to be more flexible
2. Add validation checks (no quantity prefixes, caliber in range)
3. Improve table boundary detection
4. Add debug logging to show extraction progress
5. Re-run on all available supplement PDFs

**Phase 3: Validation** (1-2 hours)
1. Compare manual entries vs scraper results
2. Validate conversion formulas against clean data
3. Re-run HE/AP population on all 469 items
4. QA check: Ensure trucks don't have 300mm guns!

---

## Available Source Files

**BattleGroup Supplements** (in Resource Documents/Battlegroup Game/):
- Battlegroup-Kursk.pdf + .txt (BEST German data)
- Battlegroup-Torch-Mission.pdf + .txt (North Africa - American/British?)
- Battlegroup-Fall-of-the-Reich.pdf + .txt (late war)
- Battlegroup-Market-Garden.pdf + .txt (1944 Western Europe)
- Multiple datacard PDFs

**Reference Images** (provided by user):
- Kursk German Gun1.png (shows 20mm, 37mm, 50mm, 75mm guns with complete AP data)
- Kursk German Gun2.png (shows 88mm, 105mm, 150mm+ guns with complete AP data)
- Gun Profiles.png (shows table format explanation)

---

## Next Steps

**DECISION REQUIRED**:
User needs to decide on approach:
- **Option A**: Manual entry only (fastest, limited scope)
- **Option B**: Fix scraper only (automated, OCR quality risks)
- **Option C**: Hybrid (recommended - best quality + future-proof)

**Estimated Time to Resolution**:
- Option A: 2-3 hours
- Option B: 4-5 hours
- Option C: 6-9 hours (but most comprehensive)

---

## Appendices

### Appendix A: Complete German Gun Audit

```
Name                                         | Cal | HE    | AP: 0-10 | 10-20 | 20-30 | 30-40 | 40-50 | 50-70
20mm                                         |  20 | NULL  |     2    |   2   |   1   |   1   |   1   | -
20mmL55                                      |  20 | NULL  |     2    |   2   |   1   |   1   |   1   | -
37mmL43 (PaK36)                              |  37 | 2/5+  |     4    |   4   |   3   |   2   |   1   | -
37mmL45                                      |  37 | 2/5+  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
37mmL53                                      |  37 | 2/5+  |     4    |   4   |   3   |   2   |   1   | -
37mmL57                                      |  37 | NULL  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
50mm                                         |  50 | 3/5+  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
50mmL60 (PaK38)                              |  50 | 3/6+  |     5    |   5   |   4   |   3   |   2   | -
75mm (IG18)                                  |  75 | 3/4+  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
75mmL24                                      |  75 | 4/4+  |     4    |   4   |   3   |   2   |   1   | -
75mmL30                                      |  75 | 4/4+  |     5    |   5   |   4   |   3   |   2   | -
75mmL46 (PaK40)                              |  75 | 4/4+  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
75mmL48                                      |  75 | 4/4+  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
75mmL70                                      |  75 | 4/4+  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
80mm                                         |  80 | 4/4+  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
[GARBAGE] At the base of the Seelow...       |  80 | NULL  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
82mm                                         |  82 | 4/4+  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
85mmL54                                      |  85 | 4/3+  |     9    |   9   |   8   |   7   |   6   | -
88mm L56 AA Gun                              |  88 | NULL  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
88mmL56                                      |  88 | 4/3+  |     9    |   9   |   8   |   7   |   6   |   5
88mmL56 (Flak36)                             |  88 | 4/3+  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
[GARBAGE] well covered by 88mm guns...       |  88 | NULL  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
100mmL52 (K18)                               | 100 | 5/3+  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
105mm L28 Howitzer                           | 105 | NULL  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
105mmL28                                     | 105 | 5/3+  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
120mm                                        | 120 | 6/4+  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
150mmL12 (sIG33)                             | 150 | 7/3+  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
150mmL30                                     | 150 | 7/3+  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
170mmL50                                     | 170 | 6/2+  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
203mmL49                                     | 203 | 8/2+  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
210mmL31                                     | 210 | 7/2+  |  NULL    | NULL  | NULL  | NULL  | NULL  | NULL
```

**Summary**:
- Good data: 9 guns (29%)
- Missing AP only: 13 guns (42%)
- Missing HE only: 4 guns (13%)
- Missing both: 3 guns (10%)
- Garbage: 2 entries (6%)

---

**END OF AUDIT**
