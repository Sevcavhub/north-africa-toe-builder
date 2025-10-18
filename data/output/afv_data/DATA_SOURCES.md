# AFV Data Sources Registry

## Overview

This directory contains AFV (Armored Fighting Vehicle) and gun specifications from **multiple independent sources**. Each source is kept **completely separate** to maintain data provenance and allow comparison/validation.

## Data Sources

### 1. OnWar.com (Root Directory)

**Location:** `data/output/afv_data/*.json` (root level files)

**Files:**
- `afv_complete_with_specs.json` - Original scraped data
- `afv_complete_with_specs.csv` - CSV export
- `afv_with_normalized_dates.json` - Processed with normalized dates
- `production_date_gaps.json` - Analysis of missing production dates
- `production_date_research_results.json` - Research to fill gaps

**Source Identifier:** `"source": "onwar.com"`

**URL Pattern:** `https://www.onwar.com/wwii/tanks/{country}/{vehicle_id}.html`

**Coverage:**
- Multiple countries (France, Germany, Britain, Italy, USA, USSR, Japan, etc.)
- Focus on specifications: dimensions, armor, armament, production

**Data Quality:**
- Good production quantities
- Reliable operational dates
- Basic specifications
- Some missing fields

**Record Count:** ~600+ vehicles

**Unique Fields:**
- `formal_designation`
- `production_quantity` (more reliable than other sources)
- `production_period`
- OnWar-specific HTML structure metadata

---

### 2. WWII Tanks UK (wwiitanks.co.uk)

**Location:** `data/output/afv_data/wwiitanks/`

**Directory Structure:**
```
wwiitanks/
├── afvs/
│   ├── germany_afvs.json
│   ├── britain_afvs.json
│   └── ... (18 countries)
├── guns/
│   ├── germany_guns.json
│   ├── britain_guns.json
│   └── ... (18 countries)
├── all_afvs.json
├── all_guns.json
├── all_afvs.csv
├── all_guns.csv
└── README.md
```

**Source Identifier:** `"source": "wwiitanks.co.uk"`

**URL Pattern:**
- AFVs: `https://wwiitanks.co.uk/FORM-Tank_Data.php?I={id}`
- Guns: `https://wwiitanks.co.uk/FORM-Gun_Data.php?I={id}`

**Coverage:**
- **612 AFVs** across 18 countries
- **343 guns** across 18 countries
- Detailed penetration data
- Hit probability tables
- AFV-to-gun relationships

**Data Quality:**
- **Excellent gun specifications** (penetration, ammunition types)
- Detailed armor values (8 zones)
- Performance specs (speed, range, fuel)
- Multiple ammunition types per gun
- Hit probability data by range

**Record Count:**
- 612 AFVs
- 343 guns
- ~2000+ relationships

**Unique Fields:**
- `indicators` (has_photo, has_scale_illustration, etc.)
- `ammunition` array with penetration tables
- `hit_probability_percent` by range
- Gun-to-AFV relationships

---

### 3. WITW (World in the Balance) [Future]

**Location:** `data/output/afv_data/witw/` (to be created)

**Source Identifier:** `"source": "witw_game_data"`

**Coverage:** Game-balanced equipment stats for wargaming

**Purpose:** Strategic-level game data, not historical accuracy

---

## Data Provenance Standards

### Every Record MUST Include:

```json
{
  "source": "onwar.com | wwiitanks.co.uk | witw_game_data",
  "source_url": "https://...",
  "scraped_at": "2025-10-17T15:30:00Z",
  "scraper_version": "1.0.0"
}
```

### Unique ID Convention:

**Format:** `{source}_{country}_{id}`

**Examples:**
- `onwar_germany_panzer_iv_ausf_f`
- `wwiitanks_germany_104` (using their internal ID)
- `witw_germany_panzer_iv`

### Country Code Standardization:

All sources use **lowercase country codes**:
- `germany` (not Germany, german, or Deutschland)
- `britain` (includes Commonwealth)
- `italy` (not Italy or italia)
- `usa` (not United States, US, or american)
- `ussr` (not Russia, Soviet Union)
- `france` (not France)
- `japan` (not Japan)

## Comparison Matrix

| Feature | OnWar.com | WWII Tanks UK | WITW Game |
|---------|-----------|---------------|-----------|
| **AFV Count** | ~600 | 612 | TBD |
| **Gun Data** | No | 343 guns | TBD |
| **Penetration** | No | ✅ 8 ranges | Game stats |
| **Production Qty** | ✅ Reliable | Sometimes | N/A |
| **Armor Detail** | Basic | ✅ 8 zones | Game stats |
| **Performance** | Basic | ✅ Detailed | Game stats |
| **Relationships** | No | ✅ Gun-to-AFV | N/A |
| **Ammunition Types** | No | ✅ Multiple | N/A |
| **Hit Probability** | No | ✅ By range | Game stats |

## Merge Strategy (Future Phase)

When merging data sources:

### 1. Create Unified Schema
```json
{
  "unified_id": "panzer_iv_ausf_f",
  "sources": {
    "onwar": { ...onwar_data, "confidence": 85 },
    "wwiitanks": { ...wwiitanks_data, "confidence": 90 },
    "witw": { ...witw_data, "confidence": 70 }
  },
  "merged": {
    "name": "PzKpfw IV Ausf F",
    "production_quantity": 462,  // from onwar (more reliable)
    "armor_front_mm": 50,         // from wwiitanks (more detailed)
    "guns": [...],                // from wwiitanks (only source)
    "game_stats": {...}           // from witw
  },
  "conflicts": [
    {
      "field": "weight_tonnes",
      "onwar": 22.0,
      "wwiitanks": 22.3,
      "resolution": "use wwiitanks (more precise)"
    }
  ]
}
```

### 2. Field Priority Rules

```javascript
const fieldPriority = {
  production_quantity: ['onwar', 'wwiitanks', 'witw'],
  armor_thickness: ['wwiitanks', 'onwar', 'witw'],
  gun_penetration: ['wwiitanks'], // only source
  gun_specifications: ['wwiitanks'], // only source
  game_balance: ['witw'], // only source
  operational_dates: ['onwar', 'wwiitanks']
};
```

### 3. Validation Rules

```javascript
// Flag for review if sources differ by >10%
if (Math.abs(source1.weight - source2.weight) / source1.weight > 0.10) {
  flagForManualReview(vehicle, 'weight', [source1, source2]);
}
```

## File Naming Convention

### Source-Specific Files

**OnWar.com:**
- `afv_complete_with_specs.json` (original, keep as-is)
- Files in root directory

**WWII Tanks UK:**
- Directory: `wwiitanks/`
- Files: `{country}_afvs.json`, `{country}_guns.json`
- All files prefixed with directory name for clarity

**WITW:**
- Directory: `witw/`
- Files: `{category}_equipment.json`

### Merged Data (Future)

**Location:** `data/output/afv_data/merged/`

```
merged/
├── unified_afvs.json          # All sources combined
├── unified_guns.json          # Gun data (from wwiitanks only)
├── conflicts.json             # Flagged discrepancies
├── confidence_scores.json     # Quality metrics per field
└── merge_log.json            # Audit trail
```

## Access Patterns

### Query by Source
```javascript
// Get OnWar data only
const onwarData = require('./afv_complete_with_specs.json');

// Get WWII Tanks UK data only
const wwiitanksAFVs = require('./wwiitanks/all_afvs.json');
const wwiitanksGuns = require('./wwiitanks/all_guns.json');
```

### Compare Sources
```javascript
const onwar = require('./afv_complete_with_specs.json');
const wwiitanks = require('./wwiitanks/all_afvs.json');

const comparison = compareVehicle('PzKpfw IV Ausf F', onwar, wwiitanks);
```

### Use Merged Data (Future)
```javascript
const unified = require('./merged/unified_afvs.json');
const vehicle = unified.find(v => v.unified_id === 'panzer_iv_ausf_f');
// Get best-available data from all sources
```

## Data Integrity Rules

1. **Never modify original source files** - Keep raw scraped data intact
2. **Process into new files** - Create `_processed`, `_normalized`, or `_merged` variants
3. **Track provenance** - Every derived file documents its source files
4. **Version control** - Git tracks all changes to source data
5. **Separate outputs** - Each source has its own directory/file namespace

## Current Status

✅ **OnWar.com** - Fully scraped, ~600 vehicles
✅ **WWII Tanks UK** - Scrapers ready, test runs successful
⏸️ **WITW** - Future integration
⏸️ **Merge** - Future phase after all sources complete

## Next Steps

1. ✅ Run full WWII Tanks UK scrape (`npm run scrape:wwiitanks`)
2. ⏸️ Compare overlapping vehicles between sources
3. ⏸️ Document discrepancies and confidence levels
4. ⏸️ Create merge script with field priority rules
5. ⏸️ Generate unified database for TO&E project
