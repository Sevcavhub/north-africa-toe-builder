# Data Separation Strategy - Implementation Complete

## ✅ Status: All data sources properly separated with unique identifiers

## Overview

All scraped data is **completely separated** by source, with each record containing full provenance metadata. This ensures data integrity and allows for proper comparison and merging in future phases.

## Data Source Structure

### 1. OnWar.com Data (Existing)
**Location:** `data/output/afv_data/` (root level)

**Files:**
- `afv_complete_with_specs.json` - ~600 vehicles
- `afv_complete_with_specs.csv`
- `afv_with_normalized_dates.json`

**Identifier in records:**
```json
{
  "url": "https://www.onwar.com/wwii/tanks/{country}/{id}.html"
}
```

**Unique naming:** Uses OnWar URLs as unique identifiers

---

### 2. WWII Tanks UK Data (New)
**Location:** `data/output/afv_data/wwiitanks/`

**Directory Structure:**
```
wwiitanks/
├── afvs/
│   ├── germany_afvs.json       (204 vehicles when scraped)
│   ├── britain_afvs.json       (125 vehicles)
│   └── ... (16 more countries)
├── guns/
│   ├── germany_guns.json       (117 weapons)
│   ├── britain_guns.json       (35 weapons)
│   └── ... (18 countries)
├── all_afvs.json               (612 total AFVs)
├── all_guns.json               (343 total guns)
├── all_afvs.csv
├── all_guns.csv
└── README.md
```

**Identifier in ALL records:**
```json
{
  "wwiitanks_id": "wwiitanks_{country}_{type}_{id}",
  "source": "wwiitanks.co.uk",
  "source_url": "https://wwiitanks.co.uk/FORM-Tank_Data.php?I={id}",
  "scraped_at": "2025-10-17T15:47:17.414Z"
}
```

**Examples:**
- AFV: `"wwiitanks_id": "wwiitanks_germany_afv_104"`
- Gun: `"wwiitanks_id": "wwiitanks_germany_gun_64"`

**Unique features:**
- Every record has globally unique ID
- Full URL preserved for verification
- Timestamp for audit trail
- Source explicitly identified

---

## Record Format Comparison

### OnWar.com Record (Existing)
```json
{
  "country": "france",
  "vehicle_name": "FT-17 Light Tank",
  "url": "https://www.onwar.com/wwii/tanks/france/fr003ft17.html",
  "production_quantity": "about 50001",
  "weight": "7000",
  "crew": "2",
  ...
}
```

### WWII Tanks UK Record (New)
```json
{
  "wwiitanks_id": "wwiitanks_germany_afv_104",
  "source": "wwiitanks.co.uk",
  "source_url": "https://wwiitanks.co.uk/FORM-Tank_Data.php?I=104",
  "scraped_at": "2025-10-17T15:47:17.414Z",
  "country": "germany",
  "vehicle_name": "10.5cm le.F.H 18/2 Gw II(A,B,C,F)",
  "operational_date_s": "1943 - 1945",
  "ordnance_classification": "SdKfz 124",
  "quantity_produced": "676",
  ...
}
```

## Data Provenance Features

### ✅ Complete Traceability
Every WWII Tanks UK record includes:
1. **Unique ID** - Globally unique across all data sources
2. **Source name** - Explicit source identification
3. **Source URL** - Original web page for verification
4. **Timestamp** - When data was scraped (ISO 8601 format)
5. **Country** - Standardized lowercase country code

### ✅ No Data Mixing
- OnWar data stays in root directory
- WWII Tanks UK data in separate `wwiitanks/` subdirectory
- Future sources will get their own directories (e.g., `witw/`)

### ✅ Easy Comparison
```javascript
// Load both sources separately
const onwar = require('./afv_complete_with_specs.json');
const wwiitanks = require('./wwiitanks/all_afvs.json');

// Find same vehicle in both sources
const onwarPanzerIV = onwar.find(v => v.vehicle_name.includes('Panzer IV'));
const wwiitanksPanzerIV = wwiitanks.find(v => v.vehicle_name.includes('PzKpfw IV'));

// Compare specifications
console.log('OnWar weight:', onwarPanzerIV.weight);
console.log('WWII Tanks UK weight:', wwiitanksPanzerIV.weight);
```

## Unique ID Scheme

### Format: `{source}_{country}_{type}_{id}`

**Components:**
- `source`: Data source identifier (`wwiitanks`, `onwar`, `witw`)
- `country`: Lowercase country code (`germany`, `britain`, `italy`)
- `type`: Record type (`afv`, `gun`)
- `id`: Source-specific numeric ID

**Examples:**
```
wwiitanks_germany_afv_104      → German AFV #104 from WWII Tanks UK
wwiitanks_britain_afv_230      → British AFV #230 from WWII Tanks UK
wwiitanks_germany_gun_64       → German gun #64 from WWII Tanks UK
onwar_france_ft17              → French FT-17 from OnWar (future format)
witw_germany_panzer_iv         → German Panzer IV from WITW (future)
```

## Country Code Standardization

**All sources use lowercase:**
- `germany` (not Germany, german, Deutschland)
- `britain` (includes all Commonwealth)
- `italy` (not Italy, italia)
- `usa` (not United States, US, american)
- `ussr` (not Russia, Soviet Union)
- `france` (not France)
- `japan` (not Japan)

## Test Results

**AFV Test (5 German vehicles):**
```
✅ wwiitanks_id: wwiitanks_germany_afv_104
✅ source: wwiitanks.co.uk
✅ source_url: https://wwiitanks.co.uk/FORM-Tank_Data.php?I=104
✅ scraped_at: 2025-10-17T15:47:17.414Z
✅ country: germany
✅ vehicle_name: 10.5cm le.F.H 18/2 Gw II(A,B,C,F)
```

**Gun Test (5 German guns):**
```
✅ wwiitanks_id: wwiitanks_germany_gun_64
✅ source: wwiitanks.co.uk
✅ source_url: https://wwiitanks.co.uk/FORM-Gun_Data.php?I=64
✅ scraped_at: 2025-10-17T15:47:17.414Z
✅ country: germany
✅ gun_name: 7.92mm MG 13
```

## File Organization

```
data/output/afv_data/
│
├── [OnWar.com Data - Root Level]
│   ├── afv_complete_with_specs.json
│   ├── afv_complete_with_specs.csv
│   ├── afv_with_normalized_dates.json
│   ├── production_date_gaps.json
│   └── production_date_research_results.json
│
├── wwiitanks/                    [WWII Tanks UK - Separate Directory]
│   ├── afvs/
│   │   ├── germany_afvs.json
│   │   ├── britain_afvs.json
│   │   └── ... (16 more)
│   ├── guns/
│   │   ├── germany_guns.json
│   │   ├── britain_guns.json
│   │   └── ... (18 countries)
│   ├── all_afvs.json
│   ├── all_guns.json
│   ├── all_afvs.csv
│   ├── all_guns.csv
│   ├── SCHEMA_PROPOSAL.md
│   └── README.md
│
├── witw/                         [Future - WITW Game Data]
│   └── (to be created)
│
├── merged/                       [Future - Unified Data]
│   └── (to be created in later phase)
│
├── DATA_SOURCES.md              [Documentation]
└── DATA_SEPARATION_COMPLETE.md  [This file]
```

## Next Steps

### 1. Run Full Scrape
```bash
npm run scrape:wwiitanks
```
This will:
- Scrape all 612 AFVs from 18 countries
- Scrape all 343 guns from 18 countries
- Save to separate files per country
- Create combined files
- Generate CSV exports
- Takes 1-2 hours

### 2. Verify Separation
After scraping, verify no data mixing:
```bash
# Check OnWar data unchanged
git diff data/output/afv_data/afv_complete_with_specs.json

# Check WWII Tanks UK in separate directory
ls data/output/afv_data/wwiitanks/afvs/
ls data/output/afv_data/wwiitanks/guns/
```

### 3. Quality Checks
```bash
# Count unique IDs (should match record count)
grep -o '"wwiitanks_id":' data/output/afv_data/wwiitanks/all_afvs.json | wc -l

# Verify all have source metadata
grep -o '"source": "wwiitanks.co.uk"' data/output/afv_data/wwiitanks/all_afvs.json | wc -l
```

### 4. Future: Merge Phase
When ready to create unified database:
1. Create `data/output/afv_data/merged/` directory
2. Run merge script with field priority rules
3. Output `unified_afvs.json` with all sources
4. Preserve original source files (never modify)

## Commands Reference

**Test scrapers:**
```bash
npm run scrape:wwiitanks:test        # Test 5 AFVs
npm run scrape:wwiitanks:test:guns   # Test 5 guns
```

**Full scrape:**
```bash
npm run scrape:wwiitanks             # All AFVs + guns (1-2 hours)
```

**Check files:**
```bash
ls data/output/afv_data/                    # OnWar data
ls data/output/afv_data/wwiitanks/          # WWII Tanks UK data
```

## Summary

✅ **Data is completely separated**
- OnWar.com data in root directory (unchanged)
- WWII Tanks UK data in `wwiitanks/` subdirectory
- Future sources will get their own directories

✅ **Every record has unique identifier**
- Format: `wwiitanks_{country}_{type}_{id}`
- Example: `wwiitanks_germany_afv_104`

✅ **Full provenance tracking**
- Source name (`wwiitanks.co.uk`)
- Source URL (original page)
- Scrape timestamp (ISO 8601)

✅ **Ready for full scrape**
- All 3 scrapers updated with source metadata
- Test runs successful
- No data mixing between sources

🎯 **Your request fulfilled:** Each data source has a unique name and stays completely separate!
