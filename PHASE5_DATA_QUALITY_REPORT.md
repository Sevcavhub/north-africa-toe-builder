# Phase 5 Data Quality Audit Report

**Generated**: 2025-10-30T05:56:12.516776

## Executive Summary

This report analyzes the completeness of scraped equipment specification data from OnWar and WWIITANKS sources before importing into master_database.db.

---

## 1. OnWar AFV Data (213 items)

**Source**: `data/output/afv_data/afv_complete_with_specs.json`

### By Nation
| Nation | Count |
|--------|-------|
| france | 6 |
| germany | 69 |
| hungary | 6 |
| italy | 12 |
| japan | 22 |
| romania | 2 |
| uk | 24 |
| usa | 24 |
| ussr | 48 |


### Field Population Rates

**Armor Values**:
- `hull_front`: 85.9% (183/213)
- `hull_side`: 85.9% (183/213)
- `hull_rear`: 82.2% (175/213)
- `turret_front`: 57.3% (122/213)
- `turret_side`: 58.7% (125/213)
- `turret_rear`: 58.2% (124/213)


**Mobility**:
- `speed`: 85.9% (183/213)
- `range`: 66.7% (142/213)
- `fuel_capacity`: 46.9% (100/213)


**Physical Characteristics**:
- `combat_weight`: 68.5% (146/213)
- `crew`: 98.1% (209/213)
- `length_hull`: 53.5% (114/213)
- `width`: 46.5% (99/213)
- `height`: 67.1% (143/213)


**Armament**:
- `primary_armament`: 98.6% (210/213)
- `secondary_armament`: 80.8% (172/213)


### Critical Gaps (90 items)

Items missing critical specification data (armor OR mobility OR <2 physical characteristics):

- **FT-17 Light Tank** (france) - Missing: armor
  - Source: https://www.onwar.com/wwii/tanks/france/fr003ft17.html
- **FCM 36** (france) - Missing: armor, mobility, physical
  - Source: https://www.onwar.com/wwii/tanks/france/fr002fcm36.html
- **PzKpfw 38(t) neuer Art** (germany) - Missing: armor
  - Source: https://www.onwar.com/wwii/tanks/germany/ge050pz38na.html
- **Toldi I** (hungary) - Missing: physical
  - Source: https://www.onwar.com/wwii/tanks/hungary/hu001toldi1.html
- **Toldi IIa** (hungary) - Missing: physical
  - Source: https://www.onwar.com/wwii/tanks/hungary/hu002toldi2a.html
- **Toldi III** (hungary) - Missing: physical
  - Source: https://www.onwar.com/wwii/tanks/hungary/hu003toldi3.html
- **Turan I** (hungary) - Missing: physical
  - Source: https://www.onwar.com/wwii/tanks/hungary/hu004turan1.html
- **Turan II** (hungary) - Missing: physical
  - Source: https://www.onwar.com/wwii/tanks/hungary/hu005turan2.html
- **Zrinyi II** (hungary) - Missing: armor, mobility, physical
  - Source: https://www.onwar.com/wwii/tanks/hungary/hu006zrinyi2.html
- **L3/35 20mm** (italy) - Missing: armor, mobility, physical
  - Source: https://www.onwar.com/wwii/tanks/italy/it003l33520.html
- **L6/40** (italy) - Missing: armor, physical
  - Source: https://www.onwar.com/wwii/tanks/italy/it002l640.html
- **Semovente L40 da 47/32** (italy) - Missing: physical
  - Source: https://www.onwar.com/wwii/tanks/italy/it008sem4732.html
- **M11/39** (italy) - Missing: armor, physical
  - Source: https://www.onwar.com/wwii/tanks/italy/it004m1139.html
- **M13/40** (italy) - Missing: physical
  - Source: https://www.onwar.com/wwii/tanks/italy/it005m1340.html
- **Semovente M40 da 75/18** (italy) - Missing: physical
  - Source: https://www.onwar.com/wwii/tanks/italy/it011sem751840.html
- **Semovente M41M da 90/53** (italy) - Missing: physical
  - Source: https://www.onwar.com/wwii/tanks/italy/it009sem9053.html
- **Carro Commando M41** (italy) - Missing: physical
  - Source: https://www.onwar.com/wwii/tanks/italy/it001ccm41.html
- **M15/42** (italy) - Missing: physical
  - Source: https://www.onwar.com/wwii/tanks/italy/it006m1542.html
- **Semovente M42 da 75/34** (italy) - Missing: armor, physical
  - Source: https://www.onwar.com/wwii/tanks/italy/it012sem753442.html
- **Semovente M43 da 105/25** (italy) - Missing: physical
  - Source: https://www.onwar.com/wwii/tanks/italy/it010sem10525m43.html

*...and 70 more items*


---

## 2. WWIITANKS AFV Data (612 items)

**Source**: `data/output/afv_data/wwiitanks/all_afvs.json`

### By Nation
| Nation | Count |
|--------|-------|
| austria | 1 |
| britain | 125 |
| canada | 38 |
| czechoslovakia | 8 |
| france | 30 |
| germany | 204 |
| hungary | 5 |
| italy | 28 |
| japan | 32 |
| poland | 8 |
| sweden | 11 |
| usa | 51 |
| ussr | 71 |


### Data Indicators
- **Has Armor Details**: 100.0% (612/612)
- **Has Weapon Details**: 74.50980392156863% (456/612)
- **Has Vehicle History**: 100.0% (612/612)

**Note**: WWIITANKS data has unstructured field names and will require parsing scripts to extract armor/gun specifications.

---

## 3. WWIITANKS Gun Data (343 items)

**Source**: `data/output/afv_data/wwiitanks/all_guns_v2.json`

### By Nation
| Nation | Count |
|--------|-------|
| austria | 1 |
| belgium | 1 |
| britain | 35 |
| czechoslovakia | 5 |
| denmark | 3 |
| finland | 1 |
| france | 31 |
| germany | 117 |
| hungary | 3 |
| italy | 26 |
| japan | 15 |
| netherlands | 4 |
| poland | 2 |
| sweden | 9 |
| switzerland | 4 |
| usa | 38 |
| ussr | 48 |


### Data Completeness
- **Has Caliber**: 100.0% (343/343)
- **Has Ammunition Data**: 15.451895043731778% (53/343)
- **Has Vehicle Assignments**: 23.9067055393586% (82/343)

---

## 4. Recommendations

### Immediate Actions
1. **OnWar Data**: Ready for import with 57.74647887323944% usable items
2. **WWIITANKS Parsing**: Requires field extraction scripts for armor/gun specs
3. **Critical Gaps**: 90 OnWar items need manual research or fallback to WWIITANKS

### Data Priority
**High Quality** (import first):
- OnWar AFV data (structured fields, ready to import)
- WWIITANKS gun data (caliber/ammunition present)

**Needs Parsing** (phase 3 work):
- WWIITANKS AFV data (extract from unstructured fields)

### Import Strategy
1. Import OnWar → `afv_data` table (Phase 2-3)
2. Parse WWIITANKS AFV → `wwiitanks_afv_data` table (Phase 3)
3. Import WWIITANKS guns → `wwiitanks_gun_data` table (Phase 3)
4. Populate `equipment` table with hybrid data (Phase 4)

---

**Audit Complete**
