# Canadian/German Guns Database Fix - Session Summary

**Date**: November 6, 2025
**Status**: ✅ Fixed - 25 guns re-extracted with correct names
**Time Taken**: ~2 hours
**Action Required**: QA comprehensive CSVs and fill missing HE ranges/ROF/classification

---

## 🚨 Problem Identified

The German and Canadian guns in the database had **incorrect names** that don't match the Battlegroup-Canadas-Crucible source:

### ❌ Wrong Names in Database
- "PzKPfw 38(sf) 2cm"
- "PzKPfw II 2cm"
- "PzKPfw IV 5cm"
- "PzKPfw 38(sf) 3.7cm"
- "PzKPfw II 3.7cm"
- "PzKPfw IV 7.5cm"

### ✅ Correct Names (from Crucible text file)
- "20mmL55"
- "37mmL43 (PaK36)"
- "50mmL60 (PaK38)"
- "75mmL24"
- "75mmL46 (PaK40)"
- "75mmL48"
- "75mmL70"
- "88mmL56 (Flak36)"

**Root Cause**: Previous extraction on November 5 used "manual_screenshot" method which incorrectly extracted vehicle weapon names from armament columns instead of reading from the actual gun tables.

---

## ✅ Fix Applied

### Step 1: Backup and Delete ✅
```bash
# Backed up 26 incorrect guns
python guns_backup_script.py
# Output: guns_backup_before_rescrape.json

# Deleted incorrect data
python delete_guns.py
# - Deleted 26 guns from bg_reference_guns
# - Deleted 26 variants from gun_name_variants
```

### Step 2: Re-scrape with datacard_scraper.py ✅
```bash
python scripts/battlegroup/scrapers/datacard_scraper.py \
    --file "Resource Documents/Battlegroup Game/Battlegroup-Canadas-Crucible.txt"
# Extracted: 11 guns (scraper limitations)
```

**Scraper Output**:
- 0 vehicles, 11 guns extracted
- All guns initially marked as nation="unknown"

### Step 3: Fix Nation Assignments ✅
```python
# Manually assigned correct nations based on gun names
canadian_ids = [47, 48, 49, 50]  # 20mm, 37mmL53, 75mmL40, 105mmL22
german_ids = [51-57]  # 80mm, 120mm, 20mmL55, PaK36, PaK38, 75mmL24, Flak36
```

### Step 4: Manual Addition of Missing Guns ✅
```bash
python add_missing_guns.py
# Added 14 guns the scraper missed
```

**Why Scraper Missed Guns**:
The scraper's regex pattern `r'^(\d+mm\s*L?\d*)\s*(\([^)]+\))?\s+(HE|AP)'` only matches:
- Standard format: `75mmL48    HE      4/4+...`
- With designation: `75mmL46 (PaK40)    HE...`

❌ But it CANNOT match:
- Inch designations: `2"`, `3"`, `4.2"`
- Pounder designations: `6 pdr`, `17 pdr`
- Extra text: `40mmL60 Bofors`
- Subsequent guns in same category (extracts only first)

**Manually Added**:
- **Canadian** (6 guns): 2" Mortar, 3" Mortar, 4.2" Mortar, 40mmL60 Bofors, 6 pdr, 17 pdr
- **German** (8 guns): 37mmL57, 75mmL46 (PaK40), 75mmL48, 75mmL70, 100mmL52 (K18), 105mmL28, 150mmL12 (sIG33), 150mmL30

### Step 5: Export Comprehensive CSVs ✅
```bash
python scripts/battlegroup/manual_extraction/export_guns_comprehensive.py \
    --nation canadian --output canadian_guns_comprehensive_v2.csv
# 10 guns × 47 columns

python scripts/battlegroup/manual_extraction/export_guns_comprehensive.py \
    --nation german --output german_guns_comprehensive_v2.csv
# 15 guns × 47 columns
```

---

## 📊 Current Database State

**Total Guns from Crucible**: 25 guns (10 Canadian + 15 German)

### Canadian Guns (10 guns)
| ID | Name | Caliber | HE | AP | Notes |
|----|------|---------|----|----|-------|
| 47 | 20mm | 20mm | - | 2/2/1/1/1/- | Autocannon |
| 48 | 37mmL53 | 37mm | 2D6/5+ | 4/4/3/2/1/- | Very Light Gun |
| 49 | 75mmL40 | 75mm | 4D6/4+ | 6/6/5/4/3/- | Light Gun |
| 50 | 105mmL22 | 105mm | 5D6/3+ | - | Medium Gun |
| 58 | 2" Mortar | 51mm | 3D6/5+ | - | Mortar |
| 59 | 3" Mortar | 76mm | 4D6/4+ | - | Mortar |
| 60 | 4.2" Mortar | 107mm | 6D6/4+ | - | Mortar |
| 61 | 40mmL60 Bofors | 40mm | - | 3/3/2/2/1/- | Autocannon |
| 62 | 6 pdr | 57mm | 3D6/5+ | 7/7/6/5/4/- | Very Light Gun |
| 63 | 17 pdr | 76mm | - | 11/11/10/9/8/7 | Light Gun (AT only) |

### German Guns (15 guns)
| ID | Name | Caliber | HE | AP | Notes |
|----|------|---------|----|----|-------|
| 51 | 80mm | 80mm | 4D6/4+ | - | Mortar |
| 52 | 120mm | 120mm | 6D6/4+ | - | Mortar |
| 53 | 20mmL55 | 20mm | - | 2/2/1/1/1/- | Autocannon |
| 54 | 37mmL43 (PaK36) | 37mm | 2D6/5+ | 4(7)*/4(7)*/3/2/1/- | Very Light AT (*Stielgranate 41) |
| 55 | 50mmL60 (PaK38) | 50mm | 3D6/5+ | 5/5/4/3/2/- | Very Light AT |
| 56 | 75mmL24 | 75mm | 4D6/4+ | 4/4/3/2/1/- | Light Gun |
| 57 | 88mmL56 (Flak36) | 88mm | 4D6/3+ | 9/9/8/7/6/5 | Medium Gun (Flak) |
| 64 | 37mmL57 | 37mm | - | 3/3/2/2/1/- | Autocannon |
| 65 | 75mmL46 (PaK40) | 75mm | 4D6/4+ | 8/8/7/6/5/4 | Light AT |
| 66 | 75mmL48 | 75mm | 4D6/4+ | 8/8/7/6/5/4 | Light Gun |
| 67 | 75mmL70 | 75mm | 4D6/4+ | 11/11/10/9/8/7 | Light Gun |
| 68 | 100mmL52 (K18) | 100mm | 5D6/3+ | 10/10/9/8/7/6 | Medium Gun |
| 69 | 105mmL28 | 105mm | 5D6/3+ | - | Medium Gun |
| 70 | 150mmL12 (sIG33) | 150mm | 7D6/3+ | - | Heavy Gun |
| 71 | 150mmL30 | 150mm | 7D6/3+ | - | Heavy Gun |

---

## ⚠️ Missing Data (Need Your QA)

**ALL 25 guns are missing these critical fields** (0% populated):

### 1. HE Range Bands (columns 31-36)
- `he_0_10`, `he_10_20`, `he_20_30`, `he_30_40`, `he_40_50`, `he_50_70`
- **Where to find**: Crucible PDF gun tables show range rows like "3 / 3 / 3 / 3 / 3 / -"
- **⚠️ Column order warning**: Columns are NOT in sequence!
  - Column 36 = he_0_10 (FIRST value)
  - Column 31 = he_10_20 (SECOND value)
  - Column 32 = he_20_30 (THIRD value)
  - Column 33 = he_30_40 (FOURTH value)
  - Column 34 = he_40_50 (FIFTH value)
  - Column 35 = he_50_70 (SIXTH value)

### 2. HE Shell Classification (column 38)
- Values: `v. light`, `light`, `medium`, `heavy`, `bomb`, `rocket`, `Cannon`
- **Guide by caliber**:
  - 20-50mm: "v. light"
  - 57-76mm: "light"
  - 87-105mm: "medium"
  - 114mm+: "heavy"

### 3. ROF - Rate of Fire (column 39)
- Scale: 1-10
- **Guide by weapon type**:
  - Heavy AT/Field Artillery (88mm+): 1-2
  - Medium AT (57-75mm): 2-3
  - Light AT/Mortars: 3-5
  - Autocannons: 6-10

---

## 📁 Files Ready for QA

### 1. Canadian Guns CSV ✅
- **File**: `canadian_guns_comprehensive_v2.csv`
- **Guns**: 10 guns × 47 columns
- **Status**:
  - ✅ Name, caliber, HE dice/target, AP values (90-100%)
  - ❌ HE range bands (0%)
  - ❌ HE classification (0%)
  - ❌ ROF (0%)

### 2. German Guns CSV ✅
- **File**: `german_guns_comprehensive_v2.csv`
- **Guns**: 15 guns × 47 columns
- **Status**:
  - ✅ Name, caliber, HE dice/target, AP values (95-100%)
  - ❌ HE range bands (0%)
  - ❌ HE classification (0%)
  - ❌ ROF (0%)

### 3. QA Guide ✅
- **File**: `COMPREHENSIVE_GUN_QA_GUIDE.md`
- **Contains**:
  - Column-by-column guide (all 47 columns)
  - HE range column order warning
  - Classification by caliber guide
  - ROF by weapon type guide
  - Common mistakes to avoid

### 4. Import Script ✅
- **File**: `scripts/battlegroup/manual_extraction/import_guns_comprehensive.py`
- **Usage**:
```bash
# After filling CSVs
python scripts/battlegroup/manual_extraction/import_guns_comprehensive.py \
    --csv canadian_guns_comprehensive_v2.csv \
    --nation canadian

python scripts/battlegroup/manual_extraction/import_guns_comprehensive.py \
    --csv german_guns_comprehensive_v2.csv \
    --nation german
```

---

## 🔧 datacard_scraper.py Issues Documented

**Limitations Found**:
1. Regex requires "mm" - misses inch (") and pounder (pdr) designations
2. Can't handle extra text between designation and HE/AP (e.g., "Bofors")
3. Only extracts first gun per category section
4. Nation detection fails when multiple nations in same file

**Recommendation**: Continue using manual extraction process for Crucible. The text file has consistent format but variations the scraper can't handle.

---

## ✅ Validation After Import

```bash
# Run audit after import
python scripts/battlegroup/manual_extraction/audit_scraped_data.py
```

**Expected**:
```
Canadian guns: HE ranges 100%, classification 100%, ROF 80-100%
German guns: HE ranges 100%, classification 100%, ROF 80-100%
```

---

## ⏱️ Time Estimate

**Your QA Work**:
- Canadian: ~60 minutes (10 guns)
- German: ~90 minutes (15 guns)
- **Total: ~2.5 hours**

**What to Do**:
1. Open CSV in Excel/spreadsheet
2. Reference Crucible PDF gun tables
3. Fill HE range bands (columns 31-36) - WATCH COLUMN ORDER!
4. Fill HE classification (column 38) - use caliber guide
5. Fill ROF (column 39) - use weapon type guide
6. Save CSV
7. Run import script
8. Run validation audit

---

## 📋 Files Created This Session

| File | Purpose | Status |
|------|---------|--------|
| `guns_backup_before_rescrape.json` | Backup of 26 incorrect guns | ✅ Complete |
| `canadian_guns_comprehensive_v2.csv` | 10 Canadian guns for QA | ✅ Ready for user |
| `german_guns_comprehensive_v2.csv` | 15 German guns for QA | ✅ Ready for user |
| `add_missing_guns.py` | Script to add 14 missing guns | ✅ Complete |
| `GUNS_DATABASE_FIX_CANADIAN_GERMAN.md` | This summary | ✅ Complete |

---

**Status**: ✅ **READY FOR YOUR QA**

Open the CSVs, reference the Crucible PDF, and fill in the missing HE ranges/classification/ROF data. The British guns are already complete (imported earlier), so these are the last two nations to finish!
