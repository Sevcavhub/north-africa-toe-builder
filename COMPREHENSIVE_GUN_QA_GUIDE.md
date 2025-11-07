# Comprehensive Gun Data QA Guide

**Date**: November 6, 2025
**Task**: Quality check and enrich ALL gun data for Canadian and German guns
**Files**: `canadian_guns_comprehensive.csv` (10 guns), `german_guns_comprehensive.csv` (16 guns)

---

## Overview

You now have comprehensive CSVs with **ALL 47 columns** for each gun. This allows you to:
1. **QA existing data** - Check what the scraper captured
2. **Fix errors** - Correct any mistakes in scraped data
3. **Fill missing fields** - Add HE ranges, ROF, classification
4. **Enrich data** - Add common names, special rules, etc.

---

## Critical Fields to Focus On

### Priority 1: MISSING DATA (Must Fill)

These fields are 0-100% empty and REQUIRED for datacards:

| Column | Current Status | What to Fill | Example |
|--------|----------------|--------------|---------|
| **he_0_10** | 0% | HE effectiveness 0-10" | 3, 6, 9, 15, D6 |
| **he_10_20** | 0% | HE effectiveness 10-20" | 3, 6, 9, 15 |
| **he_20_30** | 0% | HE effectiveness 20-30" | 3, 6, 9, 15 |
| **he_30_40** | 0% | HE effectiveness 30-40" | 3, 6, 9, 15 |
| **he_40_50** | 0% | HE effectiveness 40-50" | 3, 6, 9, 15 |
| **he_50_70** | 0% | HE effectiveness 50-70" | 3, 6, 9 |
| **he_shell_classification** | 0% | Shell weight class | v. light, light, medium, heavy, bomb, rocket, Cannon |
| **rof** | 0% | Rate of Fire (1-10) | 1, 2, 3, 6, 8, 10 |

### Priority 2: EXISTING DATA TO QA

These fields were populated by scraper - verify accuracy:

| Column | Current Status | What to Check |
|--------|----------------|---------------|
| **name** | 100% | Gun name correct? |
| **caliber_mm** | 90% (Canadian), 100% (German) | Caliber value correct? |
| **he_dice** | 60% (Canadian), 100% (German) | HE dice value correct? |
| **he_target** | 60% (Canadian), 100% (German) | HE target correct? (4+, 5+, etc.) |
| **ap_0_10** through **ap_50_70** | 60% (Canadian), 94% (German) | AP range values correct? |

### Priority 3: OPTIONAL ENRICHMENT

These fields can enhance data quality but aren't critical:

| Column | Purpose | Example |
|--------|---------|---------|
| **common_name** | Short alias for vehicles | "25 pdr", "88" |
| **weapon_category** | Auto-classification | at_gun, field_artillery, aa_gun |
| **special_rules** | Game-specific rules | "Indirect fire", "AA capable" |
| **notes** | Additional context | "Also used by South African forces" |

---

## Column-by-Column Guide

### Column Numbers (for Excel navigation)

**Critical columns** (focus here):
- Column 4: **caliber_mm**
- Column 6: **he_dice**
- Column 7: **he_target**
- Columns 8-13: **ap_0_10** through **ap_50_70**
- Columns 31-36: **he_10_20** through **he_0_10** (note order!)
- Column 37: **common_name**
- Column 38: **he_shell_classification**
- Column 39: **rof**

**Metadata columns** (can ignore):
- Columns 1-3: id, name, nation
- Columns 14-30: source tracking, dates, confidence
- Columns 40-47: weapon_category, gun_role, import tracking

### Column Descriptions

#### Core Identification (DO NOT EDIT)
- **id**: Database ID (DO NOT CHANGE)
- **name**: Official gun name (edit if scraped incorrectly)
- **nation**: Nation (canadian, german - lowercase)

#### Specifications (QA THESE)
- **caliber_mm**: Gun caliber in millimeters
  - Check: Does it match PDF datacard?
  - Fix: If wrong, correct it
  - Examples: 37, 50, 75, 88, 105, 140

- **barrel_length**: Barrel length in calibers (usually empty)
  - Leave blank unless you have specific data

#### HE (High Explosive) Data

**he_dice**: Number of HE dice
  - Check: Matches PDF datacard
  - Examples: 1, 2, 3, 4, 5, 10, 15, 20
  - NULL for AT guns with no HE

**he_target**: Target number for HE
  - Format: 2+, 3+, 4+, 5+, 6+, D6
  - Check: Matches PDF datacard
  - NULL for guns with no HE

**he_0_10** through **he_50_70**: HE effectiveness by range
  - ⚠️ **CRITICAL**: These are BLANK (0% populated)
  - Find on PDF: Look for HE range row like `3 / 3 / 3 / 3 / 3 / -`
  - Fill: Each slash-separated value goes in one column
  - Example: `3 / 3 / 3 / 3 / 3 / -` →
    - he_0_10 = 3
    - he_10_20 = 3
    - he_20_30 = 3
    - he_30_40 = 3
    - he_40_50 = 3
    - he_50_70 = (blank - dash means no effect)

**he_shell_classification**: Shell weight class
  - ⚠️ **CRITICAL**: BLANK (0% populated)
  - Values: v. light, light, medium, heavy, bomb, rocket, Cannon
  - Find on PDF: Usually in datacard header
  - Guide by caliber:
    - 20-50mm: "v. light"
    - 57-76mm: "light"
    - 87-105mm: "medium"
    - 114mm+: "heavy"

#### AP (Armor Piercing) Data

**ap_0_10** through **ap_50_70**: AP penetration by range
  - Check: Do values match PDF datacard?
  - Common pattern: Decreases with range (7, 7, 6, 5, 4, 3)
  - NULL: For mortars/artillery with no AP

#### Game Stats

**rof**: Rate of Fire (1-10 scale)
  - ⚠️ **CRITICAL**: BLANK (0% populated)
  - Find on PDF: Check stats section
  - Guide:
    - 1: Heavy guns (17 pdr, 88mm PaK, 5.5" gun)
    - 2: Medium AT guns (6 pdr, 75mm PAK40, 25 pdr)
    - 3: Light AT guns (2 pdr, 37mm PAK)
    - 4-5: Mortars, howitzers
    - 6-8: Light AA guns, HMG
    - 8-10: Autocannon, very high ROF

**points_cost**: Game points (if on datacard)
**battle_rating**: Battle rating value (if on datacard)

#### Enrichment

**common_name**: Short alias
  - Examples: "25 pdr", "88", "2 pdr", "6 pdr"
  - Used by vehicles to reference guns

**weapon_category**: Auto-classification
  - Will be auto-populated later
  - Can leave blank or fill if obvious:
    - at_gun, field_artillery, aa_gun, mortar, tank_gun

**special_rules**: Game-specific rules
  - Examples: "Indirect fire", "AA capable", "One shot"
  - Fill if you see special rules on datacard

---

## Filling Strategy

### Step 1: Open in Excel/Spreadsheet (10 minutes)

1. Open `canadian_guns_comprehensive.csv`
2. Freeze top row (View → Freeze Panes)
3. Widen columns to see full content
4. Note: 47 columns total

### Step 2: QA Existing Data (15-20 minutes per nation)

**Check each gun row**:
1. **Name correct?** (Column 2)
2. **Caliber matches PDF?** (Column 4)
3. **HE dice/target match PDF?** (Columns 6-7)
4. **AP values match PDF?** (Columns 8-13)

**Fix any errors** you find by editing the cell.

### Step 3: Fill Missing HE Ranges (30-40 minutes per nation)

**For each gun**:
1. Find gun on Crucible PDF datacard
2. Locate HE range row (e.g., `3 / 3 / 3 / 3 / 3 / -`)
3. Fill columns 31-36 (he_10_20, he_20_30, he_30_40, he_40_50, he_50_70, he_0_10)
4. ⚠️ **Watch column order**: They're NOT in sequence (31-36 vs 0-70 ranges)

**Correct column mapping**:
- Column 36 (he_0_10) = First value (0-10")
- Column 31 (he_10_20) = Second value (10-20")
- Column 32 (he_20_30) = Third value (20-30")
- Column 33 (he_30_40) = Fourth value (30-40")
- Column 34 (he_40_50) = Fifth value (40-50")
- Column 35 (he_50_70) = Sixth value (50-70")

### Step 4: Fill HE Classification (10 minutes per nation)

**For each gun**:
1. Find datacard header (usually shows classification)
2. Fill column 38 (he_shell_classification)
3. Use exact values: v. light, light, medium, heavy, bomb, rocket, Cannon

### Step 5: Fill ROF (10-15 minutes per nation)

**For each gun**:
1. Check datacard stats section for ROF
2. Fill column 39 (rof)
3. If not visible, use guide above to infer
4. OK to leave blank if uncertain

### Step 6: Optional Enrichment (10 minutes per nation)

- Column 37 (common_name): Add short aliases
- Column 44 (special_rules): Add any special rules from datacard
- Column 19 (notes): Add any observations

---

## Example: Canadian 25 pdr (Full Row QA)

**Existing data** (check these):
- Column 1 (id): 4 ✓ (don't change)
- Column 2 (name): "25 pdr" ✓ (correct)
- Column 3 (nation): "canadian" ✓ (correct)
- Column 4 (caliber_mm): 88 ✓ (correct - 87.6mm rounds to 88)
- Column 6 (he_dice): 10 ✓ (correct)
- Column 7 (he_target): "D6" ✓ (correct)
- Columns 8-13 (AP): 6, 6, 5, 4, 3, (blank) ✓ (correct - artillery has limited AP)

**Missing data** (fill these):
- Column 36 (he_0_10): **3** (from PDF: 3 / 3 / 3 / 3 / 3 / -)
- Column 31 (he_10_20): **3**
- Column 32 (he_20_30): **3**
- Column 33 (he_30_40): **3**
- Column 34 (he_40_50): **3**
- Column 35 (he_50_70): **(blank)** (PDF shows `-` at this range)
- Column 38 (he_shell_classification): **medium** (87.6mm = medium)
- Column 39 (rof): **2** (field artillery, medium ROF)

**Optional enrichment**:
- Column 37 (common_name): "25 pdr"
- Column 44 (special_rules): "Indirect fire"

---

## Example: German 88mm FlaK36/37 (Full Row QA)

**Existing data** (check these):
- Column 2 (name): "88mm FlaK36/37" ✓
- Column 4 (caliber_mm): 88 ✓
- Column 6 (he_dice): 3 ✓
- Column 7 (he_target): "4+" ✓
- Columns 8-13 (AP): 11, 10, 9, 8, 7, 6 ✓ (excellent AT capability)

**Missing data** (fill these):
- Column 36 (he_0_10): **6** (from PDF)
- Column 31 (he_10_20): **6**
- Column 32 (he_20_30): **5**
- Column 33 (he_30_40): **4**
- Column 34 (he_40_50): **3**
- Column 35 (he_50_70): **2**
- Column 38 (he_shell_classification): **medium** (88mm)
- Column 39 (rof): **3** (heavy AA gun)

**Optional enrichment**:
- Column 37 (common_name): "88"
- Column 44 (special_rules): "AA capable, Dual-purpose"

---

## Common Mistakes to Avoid

### Data Entry Errors

1. **Wrong column order for HE ranges**
   - ❌ Filling columns 31-36 sequentially
   - ✅ Column 36 first (he_0_10), then 31-35

2. **Entering "0" instead of blank**
   - ❌ `he_50_70 = 0` (means zero effect, different from no effect)
   - ✅ `he_50_70 = (blank)` (no effect at this range)

3. **Typos in classification**
   - ❌ "lite", "med", "hvy"
   - ✅ "v. light", "light", "medium", "heavy"

4. **Mixing HE and AP data**
   - ❌ Entering AP values in HE range columns
   - ✅ HE ranges in he_* columns, AP ranges already in ap_* columns

5. **Changing ID or nation**
   - ❌ Editing column 1 (id) or column 3 (nation)
   - ✅ Leave these untouched (import script matches by ID)

### QA Errors

1. **Not checking existing data**
   - ❌ Assuming scraper was perfect
   - ✅ Verify caliber, HE dice, AP values against PDF

2. **Skipping guns without HE**
   - ❌ Leaving AT guns blank because they have no HE
   - ✅ Verify this is correct (some AT guns have limited HE)

3. **Guessing instead of checking**
   - ❌ Filling ROF/classification without checking PDF
   - ✅ Reference actual datacard, leave blank if uncertain

---

## Validation Checklist

### Before Import

- [ ] All gun names correct
- [ ] All calibers checked against PDF
- [ ] All HE dice/target checked
- [ ] All AP values checked
- [ ] HE range bands filled (columns 31-36)
- [ ] HE classification filled (column 38)
- [ ] ROF filled where possible (column 39)
- [ ] No "0" values where should be blank
- [ ] ID column unchanged (column 1)
- [ ] Nation column unchanged (column 3)

### After Import

- [ ] Run audit script to verify 100% completion
- [ ] Spot-check 3-4 guns in database
- [ ] Verify HE ranges populated correctly
- [ ] Verify classification populated
- [ ] If errors found, re-edit CSV and re-import

---

## Import Commands

### After filling Canadian CSV:
```bash
python scripts/battlegroup/manual_extraction/import_guns_comprehensive.py \
    --csv canadian_guns_comprehensive.csv \
    --nation canadian
```

### After filling German CSV:
```bash
python scripts/battlegroup/manual_extraction/import_guns_comprehensive.py \
    --csv german_guns_comprehensive.csv \
    --nation german
```

### Validation:
```bash
python scripts/battlegroup/manual_extraction/audit_scraped_data.py
```

---

## Expected Time

**Canadian (10 guns)**:
- QA existing data: 15 min
- Fill HE ranges: 30 min
- Fill classification: 10 min
- Fill ROF: 10 min
- **Total: ~60 minutes**

**German (16 guns)**:
- QA existing data: 20 min
- Fill HE ranges: 45 min
- Fill classification: 15 min
- Fill ROF: 15 min
- **Total: ~90 minutes**

**Grand Total: 2.5 hours** for complete QA and enrichment

---

**Ready to start!** Open the CSV, reference the Crucible PDF, and work through each gun systematically.
