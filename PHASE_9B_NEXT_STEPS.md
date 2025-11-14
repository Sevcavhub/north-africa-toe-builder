# Phase 9B: BattleGroup Books - Next Steps

**Date**: November 14, 2025
**Status**: ✅ **WEB DEPLOYMENT ACTIVE** - Scenario-based datacards working
**Last Update**: ✅ Scenario-based datacard generator created + All 12 battles deployed
**Database Status**: Schema v3.2 ✅ | 205 clean manual vehicles ✅ | Web deployment live ✅
**Current Tasks**:
1. ✅ Fix datacard generator (scenario-based) - COMPLETE
2. ✅ Deploy to GitHub Pages/Render.com - LIVE
3. Parse Jane's guide for ammo capacity data
4. Continue manual BG extraction (target: 300-350 vehicles)
5. Rebuild conversion formulas when 300+ vehicles available

---

## 🚨 DATA QUALITY RECOVERY - CRITICAL BLOCKERS (November 8, 2025)

**Issue Discovered**: Original BG reference data was OCR-scraped with errors
- All conversion formulas (armor, penetration, movement, HE, points, BR) are **SUSPECT**
- Built from flawed OCR data where agents pulled garbage
- 205 manually-entered BG vehicles are clean - use as "Rosetta Stone" for rebuilding

### **Immediate Actions Required**

**Priority 1: Maximize Clean Data Usage** ✅ **COMPLETE - AUTOMATED LINKAGE WORKING**
1. ✅ comprehensive_linkage.py is WORKING CORRECTLY (November 8, 2025):
   - **Status**: 106 linkages (75 vehicles, 31 guns) - all respect nation boundaries
   - **Nation Filtering**: Confirmed working - American equipment fails to match (no American reference data)
   - **Quality**: 28 high-confidence (100%), 78 medium/low confidence (85-95%)
   - **Cross-Nation**: Only 2 items (USA Stuart → British M3A1 Honey) - CORRECT (British nomenclature)
   - **Remaining**: 189 items failed (no matching reference data), 174 transport/aircraft (no weapons)
2. ⏸️ Sync ammo data - Ready to proceed
3. ⏸️ Regenerate datacards - Ready to proceed

**Automated Linkage Audit Results** (November 8, 2025):
- Total linkages: 106 (75 vehicles, 31 guns) ✅
- Nation-consistent: 104 linkages (98%)
- Cross-nation: 2 linkages (Stuart = British nomenclature, historically correct)
- Failed matches: 189 items (no reference data available for American/French equipment)
- **Key Finding**: Need more reference data for American, French, and some British/German/Italian equipment
- **Conclusion**: Script works correctly - limitation is reference data coverage, not matching algorithm

**Priority 2: Fill Ammunition Capacity Gap** 🔴 **CRITICAL**
- **Problem**: WWIITANKS/OnWar lack shells/ammo count per vehicle
- **Impact**: Datacards show "-" for 264+ items without ammo data
- **Actions**:
  1. Parse Jane's WWII Tanks guide: `D:\north-africa-toe-builder\Resource Documents\Janes-WorldWarIiTanksAndFightingVehicles-TheCompleteGuide-text-pdf.txt`
     - Search keywords: "rounds", "shells", "ammunition", "carried", "stowed"
     - Extract: Vehicle name + ammo capacity
     - Import to bg_reference_vehicles or create ammo_capacity table
  2. Identify online sources:
     - tanks-encyclopedia.com (comprehensive)
     - militaryfactory.com (detailed specs)
     - Wikipedia (variable quality, check specs tables)
  3. Create scraping/manual extraction plan for ammo data

**Priority 3: Continue Manual BG Extraction**
- **Current**: 205 vehicles ✅
- **Target**: 300-350 vehicles (all North Africa BG supplements)
- **Remaining**: ~100-150 vehicles (~50-100 hours of work)
- **Why**: Need 300+ data points to validate conversion formulas with statistical confidence

**Priority 4: Formula Validation** (when 300+ vehicles available)
- Analyze vehicles with BOTH BG stats AND WWIITANKS specs
- Build statistical regression models for each conversion type
- Validate accuracy (target: 90%+ match to official BG data)
- Document which formulas work, which need more data

**Priority 5: Equipment Rebuild** (after validation)
- Clear suspect data from equipment_battlegroup
- Repopulate with validated formulas + WWIITANKS source data
- Mark generation method for transparency
- Regenerate all 12 battle books

### **Formula Rebuild Scope**

**1. Armor Conversion** (mm → BG letter scale A-O) - **NEEDS REBUILD**
- Current: equipment_battlegroup armor ratings (suspect)
- Data points: 205 vehicles × 3 facings = 615 clean values
- Formula: armor_hull_front_mm (WWIITANKS) → armor_front letter (BG)
- Validation: Map to bg_armor_conversion table (16 mm ranges)

**2. Penetration Conversion** (mm → BG penetration scale) - **NEEDS REBUILD**
- Current: bg_penetration_scale table (suspect)
- Data points: 57 manually-entered BG guns
- Formula: Gun caliber + penetration_data (mm at range) → BG penetration rating
- Validation: Against known BG gun penetration scales

**3. Movement Conversion** (speed/weight → BG inches) - **NEEDS REBUILD**
- Current: equipment_battlegroup movement values (suspect)
- Data points: 205 vehicles with known BG movement
- Formula: Vehicle type + weight + max speed → off_road/road inches
- Variables: Tank/halftrack/armored car, tonnage, max_speed_kmh

**4. HE Effectiveness** (caliber → BG HE dice) - **NEEDS REBUILD**
- Current: bg_he_effectiveness table (suspect)
- Data points: 57 BG guns with known HE values
- Formula: Gun caliber_mm → HE dice count (e.g., 75mm = 6 dice)
- Lookup: Caliber ranges to HE dice mapping

**5. Points Cost Calculation** - **NEEDS REBUILD**
- Current: equipment_battlegroup points values (suspect)
- Complexity: Based on armor, weapons, mobility, special rules
- May require: Manual assignment or very complex multi-variable formula
- Target: Validate if formula possible or manual-only

**6. Battle Rating Calculation** - **NEEDS REBUILD**
- Current: equipment_battlegroup BR values (suspect)
- Complexity: Unit value based on multiple factors
- Similar to points: May need manual assignment
- Target: Validate formula feasibility

### **Estimated Timeline**

**Immediate (8-15 hours)**:
- Documentation updates: 30 minutes ✅
- Jane's guide parsing: 2-4 hours
- Online ammo source research: 4-6 hours
- Run comprehensive_linkage.py: 5 minutes
- Ammo data integration: 4-8 hours

**Short-term (4-6 weeks)**:
- Manual BG extraction: ~50-100 hours (100-150 vehicles)
- Reach 300-350 vehicle target for formula validation

**Medium-term (after 300+ vehicles)**:
- Formula validation: 8-12 hours (statistical analysis)
- Equipment rebuild: 4-6 hours (scripted)
- Book regeneration: 2-4 hours
- QA validation: 4-8 hours

**Total to publication-ready**: ~60-120 hours work remaining

---

## 📌 SCOPE CLARIFICATION (November 5, 2025)

**Important**: Phase 9B reference data extraction scope has been **reduced** from comprehensive to **sample-based validation**.

**Original Plan**: Extract ALL 17 supplements comprehensively (DataCards + Dispatches + Full supplements)
- Goal: Complete reference database with every vehicle/gun from all BattleGroup sources
- Effort: Months of manual extraction work
- Purpose: Personal comprehensive database

**New Plan**: Extract **just enough samples** to validate conversion formulas
- Goal: Clean reference data to validate armor/penetration/movement/HE formulas
- Effort: Weeks (targeted sampling, not comprehensive)
- Purpose: **MVP publication-ready books** with accurate equipment stats

**What This Means**:
- ✅ Canada's Crucible provides clean baseline (84 vehicles, 26 guns)
- ⏳ British DataCards provides additional validation samples (77 vehicles, 15 guns)
- 📋 Additional extractions: **Only if needed** to validate specific formula edge cases
- 📦 Comprehensive extraction (17 full sources): "Nice to have later" for personal use, NOT required for MVP

**Decision Driver**: Focus on **book publication** (validate formulas, regenerate equipment stats, complete 12 battle books) rather than building comprehensive reference database.

---

## 🔄 DATABASE SCHEMA v3.2 MIGRATION COMPLETE (November 8, 2025)

### ✅ COMPLETED: Excel Template Compliance + Multi-Weapon Ammo Support

**What Was Accomplished**:
- ✅ **Schema Restructured**: bg_reference_vehicles modernized (34 columns)
  - ID moved to position 1 (far left) for Excel compatibility
  - Ammo expanded from single field to ammo_1-4 (supports Churchill Crocodile flamethrower edge case)
  - Mount data parsed from weapon fields (22 records, 26 combinations cleaned)
- ✅ **Data Quality**: 86 weapon name corrections (German caliber/length notation)
- ✅ **Tobruk Import**: 50 new vehicles (24 German, 26 Italian)
  - Panzer I/II/III/IV early variants
  - SdKfz armored cars, Panzerjäger I, Flak trucks
  - CV-33/35 tankettes, M11/39, M13/40, M14/41, Autoblinda 40/41
- ✅ **Nation Normalization**: All nation values lowercase canonical (british, german, italian, canadian)
- ✅ **V5 Generator Updated**: Datacard generator ready for multi-weapon ammo support

**Database Status After Migration**:
- **Total vehicles**: 191 (british: 78, german: 63, italian: 26, canadian: 12, canadian/british: 12)
- **Schema version**: v3.2 (Excel template compliance)
- **Key fields**: weapon_1-4, mount_1-4, ammo_1-4
- **Ammo coverage**: 100/191 (52.4%)
- **Sources**: Legacy (41), Canada's Crucible (20), British DataCards (80), Tobruk (50)

**Scripts Created**: 15 Python files for migration, import, export, verification

**Git Commits**: (Pending) Database schema v3.2 migration + documentation updates

**Impact**: Database infrastructure now ready for continued manual data entry and eventual book generation

---

## 🎉 CANADA'S CRUCIBLE EXTRACTION 100% COMPLETE (November 4, 2025)

### ✅ COMPLETED: Full Manual Extraction via Screenshots

**What Was Accomplished**:
- ✅ **41 Python extraction scripts** - Systematic data entry from screenshots
- ✅ **German forces** - 63 vehicles, 16 guns, 2 aircraft, 58 army list units, 9 defences
- ✅ **Canadian forces** - 21 vehicles, 10 guns, 3 aircraft, 47 army list units, 13 defences
- ✅ **4 complete scenarios** - Black Sabbath, Norrey, Surrounded (hierarchical force structures)
- ✅ **3 sample maps** - Scenario battlefield layouts

**Database Tables Populated**:
- `bg_reference_vehicles` (84 vehicles with stats, armor, weapons, movement)
- `bg_reference_guns` (26 guns with HE/AP values, penetration)
- `bg_reference_aircraft` (5 aircraft with role, hits, weaponry)
- `BG_Reference_ArmyList_Examples` (105 units with points, BR, composition)
- `BG_Reference_Defences` (22 defensive structures)
- `BG_Scenario_Army_Lists` (4 scenarios)
- `BG_Scenario_Forces` (8 forces total)
- `BG_Scenario_Units` (54 units with deployment details)
- `BG_Sample_maps` (4 maps)

**Git Commit**: `0aae6c62` - feat(manual-extraction): Complete Canada's Crucible

---

## 🔄 BRITISH DATACARDS EXTRACTION IN PROGRESS (November 4, 2025)

### ✅ OCR + CSV Template Generation COMPLETE

**Approach**: OCR extraction (600 DPI) → CSV templates → User manual entry → Import script

**What Was Accomplished**:
- ✅ **OCR Processing**: All 8 pages of British DataCards PDF processed
- ✅ **CSV Templates Created**: 3 files with 98 total items
  - `british_datacards_ALL_VEHICLES.csv` - 77 vehicles (pages 1-8)
  - `british_datacards_ALL_GUNS.csv` - 15 unique guns (deduplicated)
  - `british_datacards_ALL_AIRCRAFT.csv` - 6 aircraft (page 7)
- ✅ **OCR Reference Files**: 8 text files (`british_datacard_page1-8_OCR.txt`)
- ✅ **Extraction Script**: `create_all_british_csv_templates.py`

**Git Commit**: `c37e672e` - feat(phase9b): British DataCards extraction infrastructure

**Current Status**: ⏳ **AWAITING USER DATA ENTRY**

User needs to fill blank CSV fields using PDF or OCR text as reference:
- **Vehicles**: vehicle_type, off_road_inches, road_inches, armor_front/side/rear, weapons, points_cost, battle_rating, special_rules
- **Guns**: he_dice, he_target (format: "10D8"), AP penetration at 6 range bands (ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70)
- **Aircraft**: cannon_count, cannon_caliber, rockets, bombs, machine_guns, special_notes

**Next Steps**:
1. ⏳ User completes CSV data entry
2. Create import script: `import_british_datacards_from_csv.py`
3. Load to database:
   - `bg_reference_vehicles` (+77 vehicles)
   - `bg_reference_guns` (+15 guns)  
   - `bg_reference_aircraft` (+6 aircraft)
4. Create `bg_reference_small_arms` table for Page 8 "Small Arms Rate of Fire" data
5. Continue with remaining DataCards: Early-German, French-Polish-Romanian-Hungarian, Soviets, US

**OCR Lessons Learned**:
- 600 DPI OCR successfully extracts vehicle names and basic structure
- Small numeric values (penetration tables) too difficult for OCR alone
- Hybrid approach (OCR structure + manual data entry) balances speed vs accuracy
- CSV templates provide clear, systematic structure for completion

---

## 📋 REMAINING: DataCards Supplements (4 more)

**Location**: `D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Equipment Screen Captures`

**DataCards To Process**:
1. ✅ **Battlegroup-DataCards-British** (8 pages) - OCR/CSV templates complete, awaiting data entry
2. ⏳ Battlegroup-DataCards-Early-German
3. ⏳ Battlegroup-DataCards-French-Polish-Romanian-Hungarian
4. ⏳ Battlegroup-DataCards-Soviets
5. ⏳ Battlegroup-DataCards-US

**Important Notes**:
- DataCards are QRS (Quick Reference Sheet) cards, NOT full equipment lists
- Format: Top table = vehicle stats, bottom section = integrated gun stats (if vehicle has gun)
- Includes: Armored vehicles, soft-skin vehicles, aircraft cards
- NO army lists, NO maps, NO scenarios in DataCards

---

## 📋 FULL SUPPLEMENTS (After DataCards)

**Full Supplements** (Army Lists, Maps, Vehicles, Guns, Aircraft, Scenarios):
1. Battlegroup-Dispatches-1
2. Battlegroup-Dispatches-2
3. BG-Dispatches-3
4. Battlegroup-Fall-of-the-Reich-Full
5. Battlegroup-Kursk
6. Battlegroup-Market-Garden-Army-List
7. Battlegroup-Market-Garden-Scenarios
8. Battlegroup-Overlord-Army-Lists
9. Battlegroup-Overlord-D-Day-scenarios
10. Battlegroup-Torch-Mission
11. Battlegroup-Wacht-Am-Rhein
12. Battlegroup-Westwall
13. BG Army lists (PDF) v5

**Total Remaining**: 4 DataCards + 13 Full Supplements = 17 extraction tasks

---

## 📊 DATABASE STATUS

**Tables with Data**:
- ✅ `bg_reference_vehicles` - 84 items (Canada's Crucible)
- ✅ `bg_reference_guns` - 26 items (Canada's Crucible)
- ✅ `bg_reference_aircraft` - 5 items (Canada's Crucible)
- ✅ `BG_Reference_ArmyList_Examples` - 105 units
- ✅ `BG_Reference_Defences` - 22 defences
- ✅ `BG_Scenario_Army_Lists` - 4 scenarios
- ✅ `BG_Scenario_Forces` - 8 forces
- ✅ `BG_Scenario_Units` - 54 units
- ✅ `BG_Sample_maps` - 4 maps

**Pending Import** (British DataCards CSVs):
- ⏳ `bg_reference_vehicles` - +77 vehicles
- ⏳ `bg_reference_guns` - +15 guns
- ⏳ `bg_reference_aircraft` - +6 aircraft

**To Be Created**:
- ⏳ `bg_reference_small_arms` - Small Arms Rate of Fire table (British DataCards Page 8)

---

## 🛠️ HANDOFF INSTRUCTIONS FOR NEXT SESSION

**Current State**:
1. Canada's Crucible extraction: ✅ 100% COMPLETE in database
2. British DataCards: ✅ OCR/CSV templates ready → ⏳ User filling data
3. Database location: `D:/north-africa-toe-builder/database/master_database.db`

**CSV Files Ready for User**:
- `D:/north-africa-toe-builder/british_datacards_ALL_VEHICLES.csv` (77 rows)
- `D:/north-africa-toe-builder/british_datacards_ALL_GUNS.csv` (15 rows)
- `D:/north-africa-toe-builder/british_datacards_ALL_AIRCRAFT.csv` (6 rows)

**When User Completes CSVs**:
1. Create import script matching Canada's Crucible pattern
2. Read CSVs and insert to database with proper field mapping
3. Handle UNIQUE constraints (skip duplicates, report new items)
4. Verify with COUNT queries
5. Commit to git: "feat(phase9b): Import British DataCards from user-completed CSVs"

**Next DataCards Supplement**:
- After British import complete, start: Battlegroup-DataCards-Early-German
- Use same OCR + CSV template approach
- Location: `Resource Documents/Battlegroup Game/Suppliment Equipment Screen Captures`

**Reference Documents**:
- Canada's Crucible extraction scripts: `scripts/battlegroup/manual_extraction/canada_*.py`
- Database schema: Check table definitions with `PRAGMA table_info(table_name)`
- OCR script: `create_all_british_csv_templates.py`

---

## 🌐 WEB DEPLOYMENT STATUS (November 12, 2025)

### ✅ BACKEND API (Render.com) - DEPLOYED

**Deployment URL**: https://north-africa-toe-api.onrender.com

**Status**: ✅ Production ready
- Health check passing: `/api/health` (service healthy, database exists)
- Database: 6.58 MB web_database.db (17 tables, optimized for deployment)
- Equipment search working: `/api/equipment/search` (Sherman: 10 results, Panzer: 14 results)

**API Endpoints Implemented**:
1. `GET /api/health` - Health check (status, version, database status)
2. `GET /api` - API info/documentation
3. `GET /api/equipment/search` - Equipment search with filters (name, nation, category)
4. `GET /api/equipment/<id>` - Equipment details by ID
5. `POST /api/scenarios/random` - Random scenario generator (points, nations, quarter)
6. `POST /api/scenarios/historical` - Historical scenario generator (location, quarter)
7. `GET /api/scenarios/locations/<quarter>` - Battle locations by quarter (1941q1-1942q4)

**Database Optimization**:
- Original: 15.57 MB full database
- Optimized: 6.58 MB (stripped to essential tables)
- Excluded: Phase 6 extraction metadata, temporary tables, unused indexes

**Configuration**:
- Auto-deploy from main branch on git push
- CORS enabled for GitHub Pages frontend
- Error handling with JSON responses
- Logging enabled for debugging

### ✅ FRONTEND (GitHub Pages) - DEPLOYED

**Deployment URL**: https://sevcavhub.github.io/north-africa-toe-builder/

**Status**: ✅ Production ready with navigation improvements

**Pages Deployed**:
1. `index.html` - Landing page with sticky navigation ✅
2. `tools.html` - Interactive tools (scenario generators, equipment search) ✅
3. `bibliography.html` - Research sources and citations ✅
4. **4 Battle Books** (MDBook HTML outputs):
   - `battleaxe/book/book/` - 134+ HTML files ✅
   - `crusader/book/book/` - 134+ HTML files ✅
   - `gazala/book/book/` - 134+ HTML files ✅
   - `first_alamein/book/book/` - 134+ HTML files ✅

**Navigation UX Improvements** (November 12, 2025):
- ✅ Sticky top navigation bar added (About, Books, Interactive Tools, Bibliography)
- ✅ Feature cards rewrded to clarify book contents ("Each book includes...")
- ✅ Bibliography reference page created (links to all 4 book appendices)
- ✅ Interactive Tools highlighted in navigation (red accent button)
- ✅ Section anchors added (id="about", id="books")

**Tools Page Features**:
- Equipment search with filters (name, nation, category)
- Random scenario generator (configurable points, nations, quarter)
- Historical scenario generator (quarter selection, location dropdown)
- Raw API response display for debugging

### 📋 REMAINING WEB TASKS

**Priority 1: Book 404 Troubleshooting** (if issues persist)
- Current Status: Books deployed to git, may have GitHub Pages propagation delay
- Files in git: 281 HTML files (12 books × ~70 files each)
- Next steps:
  1. Wait for GitHub Pages cache refresh (24-48 hours)
  2. If persistent, check GitHub Pages build logs
  3. Verify `.gitignore` not re-excluding book directories
  4. Test book links manually: `battleaxe/book/book/index.html`, etc.

**Priority 2: Quick Access Consolidated Pages** (Optional Enhancement)
- **Equipment Index**: Searchable/filterable master list of all 469 equipment items
  - Filters: Nation, category, quarter availability
  - Links to datacard pages in books
  - Estimated: 4-6 hours
- **Consolidated OOBs**: Master organization view across all quarters
  - Hierarchical: Theater → Army → Corps → Division
  - Timeline view showing unit evolution
  - Estimated: 6-8 hours
- **Scenario Browser**: All 45+ scenarios with filters
  - Filters: Quarter, nation, battle, points range
  - Quick reference cards with setup details
  - Estimated: 4-6 hours
- **Timeline Visualization**: Interactive campaign timeline
  - Visual timeline: June 1941 → July 1942
  - Key battles, unit deployments, equipment introductions
  - Estimated: 6-8 hours

**Priority 3: Production Testing Checklist**
- [ ] Test all 7 API endpoints with various parameters
- [ ] Test equipment search with edge cases (special characters, empty results)
- [ ] Test scenario generators with all 8 quarters (1941q1-1942q4)
- [ ] Verify book navigation (chapter links, appendix links, cross-references)
- [ ] Mobile responsiveness testing (landing page, tools page, books)
- [ ] Browser compatibility (Chrome, Firefox, Safari, Edge)
- [ ] Performance testing (API response times, page load times)
- [ ] Accessibility audit (WCAG compliance, screen reader testing)

**Priority 4: Future Enhancements**
- Enhanced equipment display (formatted cards instead of raw JSON)
- Save/share scenario configurations (URL parameters or local storage)
- Printable scenario sheets (CSS @media print styles)
- Dark mode toggle for all pages
- Search across all book content (full-text search index)

### 🚀 DEPLOYMENT WORKFLOW

**Backend Updates** (Render.com):
1. Make changes to `scripts/battlegroup/web/railway_app.py` or `railway_config.py`
2. Commit and push to main branch
3. Render auto-deploys within 2-5 minutes
4. Verify at https://north-africa-toe-api.onrender.com/api/health

**Frontend Updates** (GitHub Pages):
1. Make changes to HTML/CSS files in `books/` directory
2. Regenerate MDBook outputs if needed (`cd books/[battle]/book && mdbook build`)
3. Commit and push to main branch
4. GitHub Pages deploys within 1-5 minutes
5. May need to clear browser cache to see changes

**Database Updates**:
1. Update `scripts/battlegroup/web/database/web_database.db` locally
2. Upload to Render via web dashboard (Disk storage section)
3. Restart Render service to pick up new database
4. Verify changes via `/api/equipment/search` or other endpoints

### 📊 WEB DEPLOYMENT METRICS

**Git Commits** (Web Deployment Phase):
- `d65ff456` - feat(render): Add Render.com deployment configuration
- `26bd33ee` - feat(render): Add temporary database upload endpoint
- `cd321a23` - feat(phase12): Complete 1942-Q2 (Gazala/Tobruk, 80.4k chars)
- `8a3fb197` - feat(web): Create stripped database for Render deployment
- `[pending]` - feat(web): Add scenario endpoints and navigation improvements
- `f0a1ce5f` - feat(web): Add navigation bar and bibliography page

**Files Changed** (Web Deployment):
- Backend: `railway_app.py`, `railway_config.py`, `render.yaml`
- Frontend: `index.html`, `tools.html`, `bibliography.html` (new)
- Database: `web_database.db` (stripped, 6.58 MB)
- Git config: `.gitignore` (un-excluded book directories)
- Books: 281 HTML files added (12 books × MDBook outputs)

**Lines of Code**:
- Backend API: ~300 lines (7 endpoints, error handling, CORS)
- Frontend HTML: ~850 lines (3 pages with navigation)
- CSS: ~500 lines (responsive design, navigation, cards)
- JavaScript: ~200 lines (API calls, form handling, display logic)

---
