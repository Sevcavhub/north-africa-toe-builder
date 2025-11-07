# Scraped Data Quality Audit Report

**Date**: November 6, 2025
**Purpose**: Compare scraped Canadian/German data against British manual entry standards
**Sources**: Canada's Crucible PDF (OCR scraped) vs British DataCards (manual entry)

---

## Executive Summary

### Data Quality Comparison

| Nation | Vehicles | Guns | Method | Overall Quality |
|--------|----------|------|--------|-----------------|
| **British** | 90 | 23 | Manual Entry | ✅ **EXCELLENT** (baseline) |
| **Canadian** | 25 | 10 | PDF Scrape | ⚠️ **INCOMPLETE** (40-60% complete) |
| **German** | 41 | 16 | PDF Scrape | ⚠️ **INCOMPLETE** (60-70% complete) |

### Critical Findings

**🔴 MISSING DATA (ALL Scraped Vehicles & Guns)**:
1. **HE Range Bands** - 0% populated (he_0_10 through he_50_70) for ALL scraped guns
2. **ROF (Rate of Fire)** - 0% populated for ALL scraped guns
3. **HE Shell Classification** - 0% populated for ALL scraped guns
4. **Special Rules** - 0% populated for ALL scraped vehicles

**🟡 PARTIAL DATA**:
- Canadian vehicles: 40% missing armor values, 48% missing weapons
- German vehicles: 37% missing armor values, 37% missing weapons
- Canadian guns: 40% missing basic HE/AP data
- German guns: Better coverage (93%+ HE/AP), but missing range bands

---

## Canadian Data Audit (25 vehicles, 10 guns)

### Vehicles: 25 total

**Completeness**:
- ✅ Movement: 100% (off-road/road inches populated)
- ✅ Vehicle type: 100%
- ❌ Armor: 60% (10 vehicles missing armor entirely)
- ❌ Weapons: 52% (12 vehicles missing weapons)
- ❌ Special rules: 0% (none populated)

**Vehicles Missing Armor & Weapons** (10 soft-skin vehicles):
1. Motorcycle - No armor, no weapons
2. Jeep - No armor, no weapons
3. Bedford MWD - No armor, no weapons
4. Bedford QLT - No armor, no weapons
5. CMP - No armor, no weapons
6. Bedford QLD - No armor, no weapons
7. Scammell Pioneer - No armor, no weapons
8. M1 Wrecker - No armor, no weapons
9. M5 Ambulance - No armor, no weapons
10. Loyd Carrier - No armor, **missing weapons**

**Note**: This is expected for soft-skin vehicles (trucks, jeeps, motorcycles). The issue is that:
- Armor should be "None/None/None" (string) not NULL
- Weapons should be populated (some have MGs, some are unarmed)

### Guns: 10 total

**Completeness**:
- ⚠️ Caliber: 90% (1 missing - 60lb Rocket expected)
- ⚠️ HE dice/target: 60% (4 missing)
- ⚠️ AP basic: 60% (4 missing)
- ❌ HE range bands: 0% (ALL missing)
- ❌ ROF: 0% (ALL missing)
- ❌ HE shell classification: 0% (ALL missing)

**Guns Missing Critical Data**:
1. **17 pdr** - Missing: HE data (AT gun, expected), ROF, HE_class
2. **2 pounder** - Missing: HE data (AT gun, expected), ROF, HE_class
3. **6 pdr** - Missing: HE data (AT gun, expected), ROF, HE_class
4. **PIAT** - Missing: HE data, ROF, HE_class
5. **3" Mortar** - Missing: AP data (mortar, expected), ROF, HE_class
6. **4.5" gun** - Missing: AP data, ROF, HE_class
7. **5.5" medium gun** - Missing: AP data, ROF, HE_class
8. **60lb Rocket** - Missing: Caliber (expected), AP data, ROF, HE_class

**Analysis**:
- AT guns missing HE is EXPECTED (2 pdr, 6 pdr, 17 pdr, PIAT)
- Artillery missing AP is EXPECTED (3" Mortar, 4.5" gun, 5.5" gun)
- **ALL guns missing HE range bands** - This is the CRITICAL gap
- **ALL guns missing ROF** - Important gameplay stat
- **ALL guns missing HE shell classification** - Important for datacards

---

## German Data Audit (41 vehicles, 16 guns)

### Vehicles: 41 total

**Completeness**:
- ✅ Movement: 100% (off-road/road inches populated)
- ✅ Vehicle type: 100%
- ❌ Armor: 63% (15 vehicles missing armor)
- ❌ Weapons: 63% (15 vehicles missing weapons)
- ❌ Special rules: 0% (none populated)

**Vehicles Missing Armor & Weapons** (15 soft-skin vehicles):
1. Motorcycle
2. Motorcycle and sidecar
3. Staff car
4. Kubelwagen
5. Medium Truck
6. Steyr/Horch Heavy Car
7. Opel Blitz
8. Opel Maultier
9. Heavy Truck
10. 1 tonne SdKfz 10
... (5 more)

**Note**: Same issue as Canadian - soft-skin vehicles need "None/None/None" for armor, and some should have MG weapons.

### Guns: 16 total

**Completeness**:
- ✅ Caliber: 100%
- ✅ HE dice/target: 100%
- ⚠️ AP basic: 94% (1 missing - 75mm leIG18 infantry gun)
- ❌ HE range bands: 0% (ALL missing)
- ❌ ROF: 0% (ALL missing)
- ❌ HE shell classification: 0% (ALL missing)

**All German Guns** (better data quality than Canadian):
1. 37mm PAK35/36 - Missing: ROF, HE_class
2. 50mm PAK38 - Missing: ROF, HE_class
3. 75mm PAK40 - Missing: ROF, HE_class
4. **75mm leIG18** - Missing: AP (infantry gun, expected), ROF, HE_class
5. 88mm FlaK18 - Missing: ROF, HE_class
6. 88mm FlaK36/37 - Missing: ROF, HE_class
7. 88mm FlaK41 - Missing: ROF, HE_class
8. 88mm PaK43 - Missing: ROF, HE_class
9. 88mm PaK43/41 - Missing: ROF, HE_class
10. PaK97/38 - Missing: ROF, HE_class
... (6 more vehicle-mounted guns)

**Analysis**:
- German guns have MUCH better base HE/AP data than Canadian (100% vs 60%)
- Still missing ALL HE range bands (critical gap)
- Still missing ALL ROF values
- Still missing ALL HE shell classifications

---

## British Manual Entry (Baseline Standard)

### Vehicles: 90 total

**Completeness**: ~95%+ across all fields
- Armor values: Letter codes (K, L, N, etc.) or "None/None/None"
- Movement: off-road/road inches populated
- Weapons: Populated with gun names + MG
- Special rules: Populated where applicable
- Vehicle type: All populated

### Guns: 23 total

**Completeness**: ~90-100% across all fields
- Caliber: 100% (NULL only for flamethrower/bombs/rockets - expected)
- HE dice/target: 100%
- **HE range bands (0-10" through 50-70")**: ~95% populated ✅
- **ROF**: 9% (only 2 guns, but field available) ⚠️
- **HE shell classification**: ~95% populated ✅
- AP range bands: 100%

**British Advantages**:
1. Complete HE range data (6 range bands per gun)
2. HE shell classification (v. light, light, medium, heavy, bomb, rocket, Cannon)
3. Common name variants (gun_name_variants table)
4. Import metadata (import_date, import_source)
5. Edge cases handled (Littlejohn dual values, Flamethrower D6, bombs without caliber)

---

## Root Cause Analysis

### Why Scraped Data is Incomplete

**1. PDF Parsing Limitations**:
- OCR from Crucible PDF captured basic stats (HE dice, AP values)
- OCR did NOT capture detailed range bands (probably in table format)
- OCR did NOT capture classification text (may have been separate section)
- OCR did NOT capture ROF values (may have been in separate column)

**2. Soft-Skin Vehicles**:
- Scraper stored NULL for armor/weapons instead of explicit "None/None/None"
- Unarmed vehicles stored NULL instead of "None"
- This is a data quality issue, not missing data

**3. Schema Mismatch**:
- Scraped data populated only: he_dice, he_target, ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70
- Scraped data SKIPPED: he_0_10, he_10_20, he_20_30, he_30_40, he_40_50, he_50_70 (HE range bands)
- Scraped data SKIPPED: rof, he_shell_classification (new fields)

### British Manual Entry Advantages

**Manual process captured**:
1. All 6 HE range bands (he_0_10 through he_50_70)
2. ROF values (where visible on cards)
3. HE shell classification (v. light, light, medium, heavy, etc.)
4. Proper handling of NULL vs "None" for unarmed/unarmored vehicles
5. Edge cases (variable damage D6, dual values, bombs without caliber)

---

## Impact Assessment

### What This Means for Phase 9B Books

**BLOCKER**: Cannot generate publication-quality datacards with current scraped data

**Missing on equipment datacards**:
- HE range values (showing only dice, not actual range effectiveness)
- HE shell classification (required for datacard header)
- ROF values (important gameplay stat)

**Example of incomplete data**:
```
Canadian 25 pdr (current):
  HE: 4 dice, 3+ target
  HE Ranges: ??? (ALL range bands missing)
  ROF: ??? (missing)
  Classification: ??? (missing)

British 25 pdr (manual entry):
  HE: 4 dice, 3+ target
  HE Ranges: 3/3/3/3/3/- (complete range bands) ✅
  ROF: (empty, but field available)
  Classification: medium ✅
```

**Cannot publish Canadian/German datacards until data enriched**.

---

## Recommended Actions

### Immediate (This Session)

**Option 1: Manual Re-Entry** (3-4 hours per nation)
- User manually fills HE range bands, ROF, HE classification from Crucible PDF
- Create `canadian_datacards_GUNS_ENRICHMENT.csv` with missing fields
- Run update script to populate missing data
- Same for German guns

**Option 2: Hybrid Approach** (1-2 hours per nation)
- Keep existing HE dice/AP values (already good)
- Only add missing: HE range bands, ROF, HE classification
- Smaller CSV (only 3 new columns per gun)
- Faster data entry

**Option 3: Re-Scrape with Better Parser** (4-6 hours setup, 30 min execution)
- Enhance PDF scraper to capture HE range tables
- Re-extract Canadian/German guns with complete data
- Requires OCR improvements or manual table parsing

### Long-Term (Future Sessions)

**1. Standardize Soft-Skin Vehicles**
- Run SQL update: NULL → "None/None/None" for armor
- Run SQL update: NULL → "None" or "MG" for weapons (check PDF)
- Estimated: 30 minutes

**2. Validate Special Rules**
- Canadian/German vehicles show 0% special rules populated
- Cross-reference Crucible PDF for: Open-topped, Unreliable, etc.
- Add special_movement/special_rules data
- Estimated: 1-2 hours

**3. Create Data Enrichment Pipeline**
- Script to flag incomplete records
- CSV template generator for missing fields only
- Bulk update script for enrichment
- Estimated: 2-3 hours development

---

## Comparison Tables

### Gun Data Completeness

| Field | British (Manual) | Canadian (Scraped) | German (Scraped) |
|-------|------------------|--------------------| -----------------|
| Caliber | 100% | 90% | 100% |
| HE dice/target | 100% | 60% | 100% |
| **HE range bands** | **95%** | **0%** ❌ | **0%** ❌ |
| AP ranges | 100% | 60% | 94% |
| **ROF** | **9%** | **0%** ❌ | **0%** ❌ |
| **HE shell class** | **95%** | **0%** ❌ | **0%** ❌ |

### Vehicle Data Completeness

| Field | British (Manual) | Canadian (Scraped) | German (Scraped) |
|-------|------------------|--------------------| -----------------|
| Armor | 95% | 60% | 63% |
| Movement | 100% | 100% | 100% |
| Weapons | 95% | 52% | 63% |
| Special rules | 75%+ | 0% ❌ | 0% ❌ |

---

## Decision Point

**Question for User**: How would you like to proceed?

### Option A: Manual Enrichment (Recommended)
- **Effort**: 4-6 hours total (both nations)
- **Quality**: HIGH (same as British)
- **Process**: Fill enrichment CSVs, run update scripts
- **Timeline**: Can complete this session

### Option B: Hybrid Approach
- **Effort**: 2-3 hours total (both nations)
- **Quality**: MEDIUM-HIGH (focused on critical fields only)
- **Process**: Add only HE ranges + classification + ROF
- **Timeline**: Can complete this session

### Option C: Defer to Phase 9B Completion
- **Effort**: 0 hours now
- **Quality**: LOW (use incomplete data for now)
- **Process**: Complete British books first, come back to Canadian/German later
- **Timeline**: Prioritize British book MVP

### Option D: OCR Re-Scrape
- **Effort**: 4-6 hours setup + testing
- **Quality**: MEDIUM (depends on OCR accuracy)
- **Process**: Improve scraper, re-extract data
- **Timeline**: 1-2 sessions

**My Recommendation**: **Option B (Hybrid)** - Focus on critical missing fields (HE ranges, HE classification) for Canadian/German. This gives you complete enough data for datacards (90%+) with minimal time investment (2-3 hours vs 4-6 hours full re-entry).

---

**Files Created**:
- `scripts/battlegroup/manual_extraction/audit_scraped_data.py` - Audit script
- `SCRAPED_DATA_QUALITY_AUDIT.md` - This report

**Next Step**: User decides on enrichment approach
