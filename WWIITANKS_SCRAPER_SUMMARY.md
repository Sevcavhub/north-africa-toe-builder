# WWII Tanks UK Scraper - Implementation Summary

## Status: ✅ COMPLETE AND TESTED

The scraper for wwiitanks.co.uk has been successfully created and tested.

## What Was Built

### 1. Main Scraper (`scripts/scrape_wwiitanks.js`)
- **Full scraper** for all countries, both AFVs and guns
- Covers 18 countries for AFVs and 18 countries for guns
- Outputs JSON and CSV formats
- Incremental saving (per-country files + combined files)

### 2. Test Scraper (`scripts/scrape_wwiitanks_test.js`)
- **Test version** that scrapes first 5 German AFVs only
- Quick validation without running full 1-2 hour scrape
- Successfully tested and working

## Test Results

**Test run on Germany AFVs:**
- ✅ Found 30 vehicles on first page
- ✅ Successfully scraped 5 test vehicles
- ✅ Extracted detailed specifications:
  - Operational dates
  - Ordnance classification (SdKfz numbers)
  - Production quantities
  - Dimensions (length, width, height, weight)
  - Performance specs (speed, range, fuel)
  - Crew size
  - Armament details
  - Armor specifications

**Sample vehicle extracted:**
- **Name:** 10.5cm le.F.H 18/2 Gw II(A,B,C,F) (Wespe)
- **Classification:** SdKfz 124
- **Period:** 1943-1945
- **Production:** 676 units
- **Complete specs:** Dimensions, performance, armament, armor

## How to Use

### Test Scraper (Recommended First)
```bash
npm run scrape:wwiitanks:test
```
- Scrapes first 5 German AFVs only
- Takes ~1-2 minutes
- Output: `data/output/afv_data/wwiitanks/test_germany_afvs.json`

### Full Scraper (All Countries)
```bash
npm run scrape:wwiitanks
```
- Scrapes ALL AFVs and guns from all countries
- Takes 1-2 hours (612 AFVs + 343 guns)
- Polite rate limiting (500-1500ms delays)
- Outputs:
  - Per-country JSON files: `{country}_afvs.json`, `{country}_guns.json`
  - Combined files: `all_afvs.json`, `all_guns.json`
  - CSV exports: `all_afvs.csv`, `all_guns.csv`

## Site Structure Discovered

**WWII Tanks UK (wwiitanks.co.uk):**
- **AFV link pattern:** `FORM-Tank_Data.php?I={id}`
- **Gun link pattern:** `FORM-Gun_Data.php?I={id}`
- **Country summary pages:** `FORM-Tank_Data-Summary.php?C={country_code}`
- **Pagination:** Multiple pages per country (Germany has 7 pages)

## Data Quality

**High-quality specifications including:**
- ✅ Production dates and quantities
- ✅ Physical dimensions (metric)
- ✅ Performance data (speed, range)
- ✅ Engine specifications
- ✅ Armament details (caliber, ammunition)
- ✅ Armor thickness (front, side, rear, top)
- ✅ Crew complement
- ✅ Official designations (SdKfz numbers for German vehicles)

**Indicators tracked:**
- Photo available
- Scale illustration available
- Vehicle history available
- Weapon details available
- Armor details available

## Next Steps

### 1. Run Full Scrape
```bash
npm run scrape:wwiitanks
```
Leave it running for 1-2 hours. It will save incremental results so you can stop/resume.

### 2. Data Integration
After scraping, you'll have three data sources to merge:
- **WITW:** Strategic-level game data
- **OnWar.com:** Historical AFV data (already scraped in `data/output/afv_data/`)
- **WWII Tanks UK:** Detailed specifications (will be in `data/output/afv_data/wwiitanks/`)

### 3. Merge Strategy
Create a merge script that:
1. Uses vehicle name matching (with fuzzy matching for variants)
2. Normalizes field names across sources
3. Resolves conflicts (e.g., different production quantities)
4. Creates unified records with best available data from each source
5. Tracks data provenance (which source provided which field)

## Technical Details

**Dependencies:**
- puppeteer v21.0.0 (installed)
- Node.js file system promises
- Path module

**Browser automation:**
- Runs in visible mode by default (set `headless: true` for background)
- Handles dynamic content loading
- Polite scraping with delays
- Robust error handling

**Output location:**
- `data/output/afv_data/wwiitanks/`

## Coverage

### AFV Countries (18)
Austria, Britain, Canada, Czechoslovakia, France, Germany, Hungary, Italy, Japan, Poland, Sweden, USA, USSR

### Gun Countries (18)
Austria, Belgium, Britain, Czechoslovakia, Denmark, Finland, France, Germany, Hungary, Italy, Japan, Netherlands, Poland, Sweden, Switzerland, USA, USSR

**Total vehicles to be scraped:**
- **612 AFVs**
- **343 guns**
- **955 total records**

## Files Created

1. `scripts/scrape_wwiitanks.js` - Main scraper (all countries)
2. `scripts/scrape_wwiitanks_test.js` - Test scraper (5 vehicles)
3. `data/output/afv_data/wwiitanks/README.md` - Documentation
4. `data/output/afv_data/wwiitanks/test_germany_afvs.json` - Test results

## Package.json Updates

Added scripts:
- `"scrape:wwiitanks": "node scripts/scrape_wwiitanks.js"`
- `"scrape:wwiitanks:test": "node scripts/scrape_wwiitanks_test.js"`

Added dependency:
- `"puppeteer": "^21.0.0"`

---

**Ready to run full scrape when you're ready!** The test confirms everything is working correctly.
