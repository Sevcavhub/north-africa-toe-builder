# North Africa TO&E Builder - Complete Project Scope

**Version**: 1.4.0
**Last Updated**: 2025-10-31 (Phase 9B Scope Added - BattleGroup book generation system)
**Status**: 🟢 LIVING DOCUMENT - Subject to updates

<!-- AUTO-UPDATED: START - Progress Stats -->
**Current Phase**: Phase 9B (BattleGroup Implementation) 🔄 IN PROGRESS - Step 1 starting
**Completed Phases**: Phase 1-8 (100%) ✅ | Phase 9A (WITW) ✅ 369 scenarios
**Overall Progress**: Extraction complete, WITW scenarios enhanced, BattleGroup system in development
<!-- AUTO-UPDATED: END - Progress Stats -->

**Architecture**: v4.0 (Canonical Output Locations)
**Scope**: COMPLETE - ALL 117 units that fought in North Africa battles (1940-1943)

---

## 🔧 System Restoration (October 23, 2025)

**Status**: ✅ COMPLETE - All 12 tasks (100%)
**Duration**: 1 day (multiple sessions due to VS Code crashes)
**Root Cause**: Workflow drift from Oct 18-23 baseline due to MCP memory gap

### What Was Fixed:

**Phase 1: Critical Fixes** (4 tasks)
- ✅ **MCP Memory Integration**: Created 6 retroactive entities for Oct 18-23 knowledge gap
- ✅ **Work Queue Ordering**: Fixed to echelon-first globally (divisions before corps)
- ✅ **Combat Criteria**: Added `combat_evidence` validation to `discovered_units` schema
- ✅ **Validator Compliance**: Added 92 lines for v3.0.0/v3.1.0 validation (supply/weather/tier/combat)
- ✅ **Count Sync**: Automatic validation-based counting (JSON + chapter + validation pass)

**Phase 2: Documentation** (2 tasks)
- ✅ **Consolidated Docs**: Merged START_HERE + Ken Prompt (629 lines removed)
- ✅ **CLAUDE.md Rewrite**: 872 → 243 lines (72% reduction), clear hierarchy

**Phase 3: Workflow Enforcement** (2 tasks)
- ✅ **Session Start**: Added CRITICAL RULES section to `session_start.js`
- ✅ **Pre-Flight Validation**: Created `validate_session_readiness.js` (environment checks)

**Phase 4: Version History** (2 tasks)
- ✅ **VERSION_HISTORY.md**: Documented schema v3.1.0 features (140 lines)
- ✅ **PROJECT_SCOPE.md**: Updated progress 28.1% → 60.6% (254/419)

**Phase 5: Testing** (2 tasks)
- ✅ **End-to-End Test**: Verified complete workflow functional
- ✅ **Validation Errors**: Fixed 2 critical errors → **0 failures (254 files, 173 passed)**

**Impact**: All workflow drift issues resolved, system ready for Phase 6 continuation

**Git Commits**:
- `65c835e` - Phase 1 restoration (MCP memory, work queue, combat criteria, validator, count sync)
- `5598f65` - Phase 2.1 (documentation consolidation)
- `e06b37a` - Phase 2.2 (CLAUDE.md rewrite)
- `ff5b333` - Phase 2 complete
- `bc465c0` - Phases 3-5 complete (workflow enforcement, version history, testing)
- `fb31013` - Documentation synchronization (unit counts)

---

## 🎯 Project Vision

Build a **comprehensive North Africa Campaign TO&E database (1940-1943)** specifically designed for **wargame scenario and campaign generation**.

This is NOT just a static historical database - it's a **game-ready scenario generation system** with:
- Complete unit TO&E data (variant-level equipment detail)
- Supply/logistics modeling (fuel reserves, ammo stocks, operational radius)
- Weather/environmental factors (seasonal impacts on operations)
- Air-ground integration (complete air support assignments)
- Multi-format export (MDBook, wargaming scenarios, SQL database)

---

## 📊 Complete Project Scope

### Total Units Across All Phases:

| Component | Unit Count | Status |
|-----------|-----------|--------|
| **Ground Forces** | 117 units (402 unit-quarters) | ✅ **402 complete (100%)** - Phase 6 **COMPLETE** |
| **Air Force Units** | 23 quarterly theater summaries | ✅ **23 complete (100%)** - Phase 7 **COMPLETE** |
| **Cross-Linking** | 18 army-level units | ✅ **18 complete (100%)** - Phase 8 **OBE (done in Phase 7)** |
| **Battle Scenarios** | 12+ | Planned - Phase 9 |
| **Campaign System** | 1 complete | Planned - Phase 10 |
| **TOTAL** | **425 units + 23 air summaries** | **✅ Phases 1-8 COMPLETE (100%)** - Ready for Phase 9 Scenarios |
| **COMPLETE SEED** | ✅ Generated Oct 15, 2025 | ALL combat units from 8 major battles |

### Scope Definition (Complete Battle-Participating Units):

**User's Rule**: "Identify ALL the units that fought in North Africa battles, not just italians, or one year or one quarter but ALL units"

**Complete Seed Generated**: October 15, 2025
- File: `projects/north_africa_seed_units_COMPLETE.json`
- **117 unique units** across 5 nations
- **419 unit-quarters** (quarter-by-quarter expansion) - *Updated Oct 23: XXX Corps 1941-Q2 and XXII Corps 1940-Q3 removed via data quality corrections*
- **Verified against 8 major battles**: Operation Compass, Tobruk, Crusader, Gazala, El Alamein (1st & 2nd), Torch, Tunisia Campaign

**Applied Criteria**:
- ✅ Unit participated in documented North Africa battles (offensive OR defensive)
- ✅ Includes mobile, garrison, and static divisions that saw combat
- ✅ Includes divisions destroyed early (Sirte, Marmarica, Cirene, Sabratha - Operation Compass)
- ✅ Includes corps, armies, brigades, specialized formations
- ✅ All Commonwealth allies (Polish, Czech, Greek units)
- ❌ No administrative-only units

**Complete Seed Breakdown by Nation**:
- **German**: 12 units (60 unit-quarters)
- **Italian**: 31 units (156 unit-quarters) - largest nation
- **British/Commonwealth**: 31 units (162 unit-quarters) - largest unit-quarter count
- **American**: 8 units (23 unit-quarters)
- **French**: 7 units (19 unit-quarters)

**Current Completion**: ✅ **402/402 (100%)** - *Updated Oct 27, 2025* - **PHASE 6 COMPLETE**
- Completed: 402 unit-quarters (all valid units extracted and validated)
- Remaining: 0 unit-quarters
- Data quality corrections: 9 unit-quarters researched and confirmed as destroyed/invalid/not-in-theater (removed from scope)
- Final seed total: 411 → 402 unit-quarters (all valid units accounted for)
- Validation: 402 units pass schema v3.1.0

### Scope Clarifications:

**Ground Forces (117 units, 419 unit-quarters)**:
- Theater → Corps → Division → Regiment → Battalion → Company → Platoon → Squad
- All organizational levels with complete SCM detail
- Equipment: Ground vehicles, artillery, support weapons
- Aircraft section: Shows **air support AVAILABLE** to ground forces (not organic aircraft)
- **Expanded from 36 to 117 units** (225% increase) based on comprehensive battle research

**Air Force Units (~100-135 units)**:
- Separate organizational structure (Geschwader → Gruppe → Staffel, etc.)
- Luftwaffe: ~30-40 units (JG 27, StG 2, etc.)
- RAF/Commonwealth: ~40-50 units (Desert Air Force squadrons)
- USAAF: ~10-15 units (9th/12th Air Force groups)
- Regia Aeronautica: ~20-30 units (5ª Squadra Aerea stormi)
- Complete TO&E: Pilots, ground crew, aircraft, ordnance, fuel bowsers
- First pass of seed will be major battles only
---

## 🗓️ Phased Approach

### **Phase 1-4: Database Infrastructure** (COMPLETE ✅)

**Goal**: Establish foundational database architecture and import baseline data

**Status**: ✅ COMPLETE (October 14-18, 2025)

**Work Completed**:
- ✅ SQLite master database created (11 tables)
- ✅ WITW baseline imported (469 equipment items)
- ✅ OnWar AFV data imported (213 vehicles)
- ✅ WWIITANKS imported (612 AFVs + 343 guns)
- ✅ Ammunition data imported (162 types)
- ✅ Penetration data imported (1,296 values)
- ✅ WITW units imported (144 units)

**Database Schema**:
- Core: equipment, guns, ammunition, penetration_data
- Assignments: units, unit_equipment
- Metadata: match_reviews, import_log
- Sources: afv_data (OnWar), wwiitanks_afv_data, wwiitanks_gun_data

**Files Created**:
- `database/master_database.db` - SQLite database
- `scripts/import_witw_baseline.js` - WITW import
- `scripts/import_guns.js` - Guns import
- `scripts/import_units.js` - Units import

**Time Spent**: ~4 hours

---

### **Phase 5: Equipment Matching & Database Integration** (✅ COMPLETE - 100%)

**Goal**: Link WITW baseline equipment to detailed specifications from OnWar and WWIITANKS databases

**Status**: 469/469 complete (100%) - **ALL EQUIPMENT MATCHED** ✅

**Strategic Rationale**:
Historical sources (Tessin, Army Lists, Field Manuals) provide equipment **QUANTITIES** but lack detailed **SPECIFICATIONS**. Wargame scenarios need WITW equipment IDs. MDBook chapters need variant specifications (armor values, gun penetration, performance data). Integration of three data sources provides comprehensive equipment database while preserving historical accuracy for counts.

**Data Sources Integration**:
| Source | Type | Count | Purpose |
|--------|------|-------|---------|
| **WITW Baseline** | Canonical IDs | 469 items | Source of truth for scenario exports |
| **OnWar** | AFV specs | 213 vehicles | Production data, basic specifications |
| **WWIITANKS** | AFV + Gun specs | 612 AFVs, 343 guns | Detailed armor, penetration, ammunition |

**Equipment Matcher Tool** (`tools/equipment_matcher_v2.py` v2.1):
- Interactive CLI matching workflow
- Type detection (GUN vs AFV vs SOFT_SKIN vs AIRCRAFT)
- Cross-nation matching (captured/lend-lease equipment)
- Research agent integration (automated web search for missing data)
- Match confidence scoring (100% = exact, 85% = partial, 70% = word match)
- Name normalization (handles "H-39" vs "H39" vs "H 39")
- Summary category filtering (auto-excludes "Total Light Tanks")

**Matching Progress by Nation**:
- [x] **French**: 20/20 items → **COMPLETE** (100%)
- [x] **American**: 81/81 items → **COMPLETE** (100%)
- [x] **British**: 196/196 items → **COMPLETE** (99%)
- [x] **German**: 98/98 items → **COMPLETE** (96%)
- [x] **Italian**: 74/74 items → **COMPLETE** (97%)
- **TOTAL**: 469/469 items matched (99% overall success rate)

**Deliverables**:
- ✅ SQLite master database (all 3 sources integrated)
- ✅ Equipment matcher v2.1 (all algorithmic enhancements complete)
- ✅ 469 equipment items matched (99% success rate)
- ✅ 5 missing guns added to database (BL 7.2-inch, leIG 18, 17cm K 18, Obice 100/17, Obice 149/13)
- ✅ 6 aircraft added to database (Lysander III, Hurricane Tac R, Blenheim IV Photo Recon, TBF-1 Avenger)
- ✅ **Enrichment script** (`scripts/enrich_units_with_database.py`) - Add database specs to unit JSONs
- ✅ **Scenario export script** (`scripts/generate_scenario_exports.py`) - WITW CSV with equipment IDs + battle narratives
- ✅ **150 scenarios exported** from existing units (98% success rate)
- ✅ Detail level standards documented (books vs scenarios)

**Critical Integration Scripts Created** ✅:

1. **`scripts/enrich_units_with_database.py`** (✅ COMPLETE)
   - **Purpose**: Add database specifications to unit JSON files
   - **Input**: Unit JSON with counts (from agents: "Panzer III Ausf F": 60)
   - **Output**: Enriched unit JSON with counts + specs (armor, gun, crew, production)
   - **Status**: Created and ready for use
   - **Enables**: MDBook chapter generation with variant specifications

2. **`scripts/generate_scenario_exports.py`** (✅ COMPLETE & TESTED)
   - **Purpose**: Export WITW-format CSV with equipment IDs and battle narratives
   - **Input**: Enriched unit JSON files (existing units with nested variant structure)
   - **Output**: WITW scenario directories (equipment.csv, scenario_metadata.json, README.md)
   - **Status**: Created, tested on 153 units, 150 scenarios successfully exported (98%)
   - **Enables**: Phase 9 scenario generation

3. **`scripts/add_missing_guns.py`** (✅ COMPLETE)
   - **Purpose**: Add 5 guns identified during Phase 5 matching
   - **Status**: Complete - all 5 guns added to database

**Integration with Other Phases**:
- **Phase 6 (Unit Extraction)**: Agents extract counts → Enrichment script adds database specs
- **Phase 9 (Scenarios)**: Enriched units → Scenario export script → WITW CSV with battle narratives
- **Phase 10 (Campaign)**: Equipment transitions tracked via database

**Detail Level Standards** (Critical for Output):

**MDBook Chapters** (Human Readers):
- ✅ Equipment counts (from historical sources)
- ✅ Variant names (specific model designations)
- ✅ Key specifications (main gun, armor, crew)
- ✅ Production context (dates, quantities)
- ✅ Tactical analysis (how used in combat)
- ❌ NO full penetration tables (overwhelming)
- ❌ NO WITW equipment IDs (game-specific)

**WITW Scenarios** (Wargamers):
- ✅ WITW equipment IDs (canonical identifiers)
- ✅ Equipment counts (historical)
- ✅ Operational readiness (ready vs damaged)
- ✅ All vehicles including soft-skin (trucks, halftracks)
- ✅ Battle context (historical situation, date, location)
- ✅ Victory conditions (narrative description)
- ✅ Weather/terrain conditions (operational context)
- ✅ Supply states (fuel days, ammo days, water)
- ✅ Strategic objectives (what each side is trying to achieve)
- ❌ NO detailed equipment production history (not needed for gameplay)
- ❌ NO long-form tactical essays (keep concise for players)

**SQL Database** (Developers/Analysts):
- ✅ EVERYTHING - all data from all sources
- ✅ All penetration tables and ammunition data
- ✅ Complete provenance (sources, confidence levels)
- ✅ Cross-nation transfers (captured, lend-lease)

**Files Created**:
- `tools/equipment_matcher_v2.py` - Interactive matcher (v2.1)
- `tools/equipment_matcher_auto.py` - Enhanced automated matcher
- `tools/apply_research_findings.py` - Apply research to database
- `tools/show_french_results.py` - Query matching results
- `scripts/enrich_units_with_database.py` - Add database specs to units
- `scripts/generate_scenario_exports.py` - Export WITW scenarios
- `scripts/add_missing_guns.py` - Add missing guns to database
- `EQUIPMENT_MATCHING_COMPLETE_ALL_NATIONS.md` - Comprehensive summary (469 items)
- `FRENCH_MATCHING_COMPLETE.md` - French session summary (20 items)
- `BRITISH_MATCHING_COMPLETE.md` - British session summary (196 items)
- `GERMAN_MATCHING_COMPLETE.md` - German session summary (98 items)
- `ITALIAN_MATCHING_COMPLETE.md` - Italian session summary (74 items)
- `PHASE_5_6_INTEGRATION_COMPLETE.md` - Integration scripts summary
- 150 WITW scenario exports in `data/output/scenarios/`

**Time Spent**: ~8-10 hours (automated matching + algorithmic enhancements + script creation)

---

### **Phase 5.5: Database Backfill & Name Normalization** ⏳ **PENDING**

**Goal**: Populate SQLite database with all extracted units and normalize naming variations

**Status**: **NOT STARTED** - Blocking Phase 8-9

**Current Database State** (as of Oct 29, 2025):
- **144 units in database** (Phase 1-4 WITW baseline only)
- **402 ground units extracted** but not in database (64% missing)
- **23 air summaries extracted** but not in database
- **Total gap**: 281 records missing from master_database.db

**Database Tables Status**:
- ✅ `equipment` (469 rows) - WITW baseline complete
- ✅ `guns` (348 rows) - Specifications complete
- ✅ `aircraft` (1,010 rows) - Specifications complete
- ✅ `match_reviews` (959 rows) - Phase 5 matching complete
- ⚠️ `units` (144 rows) - **INCOMPLETE** (should be 425)
- ⚠️ `unit_equipment` - Not populated with extracted units

**Name Normalization Challenge**:

Historical sources use inconsistent naming:
- **Units**: "Deutsches Afrikakorps" vs "Deutsches Afrika-Korps" vs "DAK"
- **Equipment**: "Panzer III Ausf. F" vs "PzKpfw III Ausf F" vs "Pz.Kpfw. III Ausf. F"
- **Aircraft**: "Bf 109E-7/Trop" vs "Messerschmitt Bf 109E-7" vs "Me 109E-7"

**Required Solution**:
1. **Canonical Names Table**: Official standardized names for each entity
2. **Alias Mapping Table**: Links variations → canonical names
3. **Fuzzy Matching Algorithm**: Handles minor spelling/formatting differences
4. **Backfill Script Enhancement**: Use alias resolution during import

**Deliverables**:
- ✅ `scripts/check_database_status.js` - Database status checker (created)
- ⏸️ `database/schema/canonical_names.sql` - Canonical names + aliases tables
- ⏸️ `scripts/lib/name_normalizer.js` - Name resolution library
- ⏸️ `scripts/backfill_ground_units.js` - Import 402 ground units with normalization
- ⏸️ `scripts/backfill_air_summaries.js` - Import 23 air summaries
- ⏸️ `scripts/validate_database_completeness.js` - Verify all units imported

**Timeline**: ~8-12 hours (name mapping design + backfill scripts + testing)

**Prerequisites**: Phase 5 and Phase 6 complete ✅

**Blocks**: Phase 8 (cross-linking), Phase 9 (scenario enrichment)

---

### **Phase 6: Ground Forces Unit Extraction** ✅ **COMPLETE - 100%**

**Goal**: Complete all valid unit-quarters (117 unique units across all quarters)

**Status**: ✅ **402/402 complete (100%)** - **0 unit-quarters remaining** - *Completed Oct 27, 2025*

**Dependencies**: Phase 5 equipment matching provides specifications for MDBook chapters

**COMPLETE SEED GENERATED** (October 15, 2025, updated Oct 23):
- Comprehensive battle research across 8 major operations (1940-1943)
- Identified ALL 117 units that fought in North Africa
- Expanded from incomplete 36-unit seed (215 quarters)
- New seed: 117 units, 419 quarters (+225% units, +95% quarters) - *2 invalid quarters removed Oct 23*
- Verified against authoritative sources (85-95% confidence)

**Completion by Nation** (Updated 2025-10-27):
- **American**: 23/23 (100%) ✅ COMPLETE
- **French**: 19/19 (100%) ✅ COMPLETE
- **German**: 59/59 (100%) ✅ COMPLETE
- **Italian**: 147/147 (100%) ✅ COMPLETE
- **British/Commonwealth**: 154/154 (100%) ✅ COMPLETE

**Deliverables**:
- ✅ **402/402 unit JSON files (complete SCM detail)** → CANONICAL: `data/output/units/` ✅ **COMPLETE**
- ✅ **402/402 MDBook chapters (professional narrative)** → CANONICAL: `data/output/chapters/` ✅ **COMPLETE**
- ⏸️ WITW-format exports (CSV for wargaming) → CANONICAL: `data/output/scenarios/` (pending)
- ⏸️ SQL database schema (ground forces tables) → pending

**Architecture v4.0 + Complete Seed**:
- ✅ Canonical output locations implemented (`data/output/units/`, `data/output/chapters/`)
- ✅ Complete seed generated with all combat units
- ✅ Master Unit Directory rebuilt (419 unit-quarters)
- ✅ Validation-based count sync implemented (JSON + chapter + validation = complete)
- ✅ Skip-completed logic working with new seed

**Phase 6 Status**: ✅ **COMPLETE** - All 402 valid unit-quarters extracted and validated
**Note**: 9 unit-quarters from original 411 total were researched and confirmed as destroyed/invalid/not-in-theater

---

### **Phase 7: Air Force Extraction** ✅ **COMPLETE - 100%** (Design Divergence)

**Goal**: Extract air force data for scenario generation (all nations)

**Status**: **23 quarterly summaries complete (100%)** - *Updated Oct 29, 2025*
- **23 quarterly air summaries** → `data/output/air_summaries/` (aggregate strength data)
- **Covers 9 quarters** (1941-Q1 through 1943-Q1)
- **4 nations**: German (7), British (7), Italian (7), American (2)
- Average confidence: 70% weighted by aircraft count
- **18 Army-level ground units** updated with air_support sections

**⚠️ DESIGN DIVERGENCE FROM ORIGINAL PLAN:**

**Originally Planned**: ~100-135 per-unit JSONs with detailed TO&E (pilots, ground crew, aircraft, ordnance) + individual MDBook chapters for each Gruppe/Squadron/Stormo

**Actually Implemented**: 23 quarterly theater-wide summaries with aggregate data (total fighters/bombers/recon by nation per quarter)

**Rationale**:
- Scenario generation requires **aggregate air support availability**, not organic unit detail
- Historical sources provide theater-level strength data, not individual unit TO&Es
- Summary approach is **functionally complete** for Phase 9 scenario generation
- Detailed per-unit extraction would require extensive archival research (~60-80 hours) with limited value-add

**What This Means for Phase 8-10**:
- Phase 8: Cross-linking uses quarterly summaries, not individual air unit IDs
- Phase 9: Scenarios use aggregate air support data (e.g., "170 German aircraft available")
- Phase 10: Campaign tracking uses quarterly strength transitions

**If Detailed Air Units Needed Later**: Can be extracted post-MVP as "Phase 11: Detailed Air Forces"

**Organizational Structures**:

**Luftwaffe** (Fliegerführer Afrika):
```
Fliegerkorps X
  └─ Jagdgeschwader 27 (Fighter Wing)
      ├─ Stab/JG 27 (Wing Staff)
      ├─ I./JG 27 (1st Group - 35 Bf 109)
      │   ├─ 1. Staffel (12 aircraft)
      │   ├─ 2. Staffel (12 aircraft)
      │   └─ 3. Staffel (11 aircraft)
      └─ II./JG 27, III./JG 27 (additional groups)
```

**RAF Desert Air Force**:
```
No. 204 Group
  └─ No. 274 Squadron RAF
      ├─ A Flight (Hurricanes)
      ├─ B Flight (Hurricanes)
      └─ Ground crew, maintenance
```

**USAAF** (1942-1943):
```
9th Air Force
  └─ 57th Fighter Group
      ├─ 64th Fighter Squadron (P-40)
      ├─ 65th Fighter Squadron (P-40)
      └─ 66th Fighter Squadron (P-40)
```

**Deliverables**:
- ~100-135 air unit JSON files → CANONICAL: `data/output/air_units/`
- Air forces MDBook chapters → CANONICAL: `data/output/air_chapters/`
- Air unit WITW exports (specialized format) → CANONICAL: `data/output/scenarios/air_units/`
- SQL air forces tables

**Timeline**: ~60-80 hours of autonomous processing

**Prerequisites**: Phase 1-6 complete (all 213 ground units)

---

### **Phase 8: Cross-Linking & Integration** ✅ **OBE (ACCOMPLISHED DURING PHASE 7)**

**Original Goal**: Connect ground and air units with assignment data

**Status**: ✅ **COMPLETE** - Integration accomplished naturally during Phase 7 extraction

**What Actually Happened**:

Due to the **Phase 7 design pivot** (quarterly theater summaries instead of per-unit JSONs), air-ground integration was accomplished **during extraction** rather than as a separate phase.

**Integration Approach**:
- **Army/Theater level units** (18 units) include `air_support` sections with:
  - Direct references to quarterly air summary files
  - Aggregate theater air strength data
  - Air command structure (Desert Air Force, Twelfth Air Force, etc.)
  - Serviceability rates and operational aircraft counts

**Example** (American II Corps 1942-Q4):
```json
"air_support": {
  "air_summary_reference": "american_1942q4",
  "theater_air_command": {
    "designation": "Twelfth Air Force",
    "commander": "Major General James H. Doolittle"
  },
  "aggregate_strength": {
    "total_aircraft": 500,
    "operational_aircraft": 400
  },
  "data_source": {
    "summary_file": "american_1942q4_air_summary.json"
  }
}
```

**Doctrinal Rationale**:
- Air forces commanded at **theater/army level** (historically accurate)
- Divisions/corps receive air support through parent formations
- Quarterly summaries provide theater-wide context for scenario generation
- No need for detailed unit-level cross-linking

**Deliverables** (Already Complete):
- ✅ 18/18 army-level units include air support references
- ✅ 23 quarterly air summaries link to corresponding ground formations
- ✅ Theater air strength integrated at appropriate command echelon
- ✅ Ready for Phase 9 scenario generation

**Timeline**: 0 hours (work already complete)

**Phase 8 is OBE** - Original plan superseded by Phase 7 integration approach

---

### **Phase 9: Scenario Generation** ⏳ **Phase 9A COMPLETE, 9B-9E IN PROGRESS**

**Goal**: Create multi-game scenario exports (WITW, BattleGroup, Achtung Panzer, Flames of War)

**Status**: Phase 9A complete (WITW enhanced), Phase 9B next (BattleGroup implementation)

---

#### **Phase 9A: WITW Enhancement + Architecture** ✅ **COMPLETE (October 29, 2025)**

**Deliverables**:
- ✅ Pluggable scenario generation architecture (`scripts/scenario_generation/`)
- ✅ Base `ScenarioExporter` class with game-agnostic functionality
- ✅ Enhanced WITW exporter with supply/weather/air support integration
- ✅ 369 WITW scenarios exported (91.8% of 402 units)
- ✅ 98% supply data coverage, 83% weather data coverage
- ✅ Validation report: `docs/PHASE_9A_VALIDATION_REPORT.md`

**Time Spent**: ~10 hours

**Key Achievement**: Established multi-game export framework with Schema v3.0 and Phase 8 cross-linking integration

---

#### **Phase 9B: BattleGroup Book Generation** 🔄 **IN PROGRESS**

**Goal**: Generate complete BattleGroup-format books for North Africa battles (matching Battlegroup-Kursk style)

**Approach**: Hybrid historical accuracy + game balance adjustments

**Status**: Step 1 starting (Datacard scraping & reference database creation)

**Deliverables**:

1. **Reference Database** (Step 1):
   - Scraped datacard database from existing BattleGroup PDFs/text files
   - ~200+ vehicle profiles (armor letters, movement, weapons, points, BR)
   - ~150+ gun profiles (HE/AP values, penetration scale, range bands)
   - Cross-reference mapping to our master database

2. **Conversion Formula Suite** (Step 2):
   - `armor_converter.py`: mm thickness → letter rating (A-O scale)
   - `penetration_converter.py`: mm @ distance → value (1-15 scale)
   - `movement_calculator.py`: weight/type → inches (off-road/road)
   - `he_calculator.py`: caliber → dice/target number (e.g., "4/4+")
   - Validation: 95%+ accuracy vs scraped reference data

3. **Game Balance System** (Step 3):
   - `points_calculator.py`: Reverse-engineered points cost algorithm
   - `battle_rating_assigner.py`: BR value assignment (pattern-based)
   - Analysis of official BattleGroup army lists (±10% tolerance target)

4. **Database Schema Extensions** (Step 4):
   - 11 new SQLite tables for BattleGroup-specific data
   - `bg_reference_vehicles`, `bg_reference_guns` (scraped data)
   - `bg_armor_conversion`, `bg_penetration_scale` (lookup tables)
   - `equipment_battlegroup` (generated stats for all 469 equipment items)

5. **Generator Tools** (Step 5):
   - `datacard_generator.py`: Vehicle/gun stat cards (text format)
   - `force_list_compiler.py`: Army lists with historical restrictions
   - `oob_formatter.py`: Historical order of battle timelines
   - `scenario_generator.py`: Playable scenarios with victory conditions

6. **Complete Battle Books** (Step 6 - 12 books):
   - Operation Compass (1940q4-1941q1)
   - Operation Sonnenblume (1941q1)
   - Siege of Tobruk (1941q2)
   - Operation Battleaxe (1941q2)
   - Operation Crusader (1941q4)
   - Gazala (1942q2)
   - First Alamein (1942q3)
   - Alam Halfa (1942q3)
   - Second Alamein (1942q4)
   - Operation Torch (1942q4)
   - Tunisia Campaign (1943q1)
   - Mareth Line (1943q1)

**Book Structure Per Battle**:
```
data/output/battlegroup/[battle_name]/
├── 00_introduction.md (historical overview)
├── 01_timeline.md (day-by-day battle events)
├── 02_oob.md (complete orders of battle)
├── 03_army_lists/ (force selection with points/BR)
│   ├── german_panzer_division.txt
│   ├── italian_division.txt
│   ├── british_armoured_division.txt
│   ├── american_armored_division.txt
│   └── restrictions.txt
├── 04_datacards/
│   ├── vehicles/ (all vehicle profiles)
│   ├── guns/ (all gun profiles)
│   └── aircraft/ (aircraft support profiles)
├── 05_scenarios/ (7+ playable scenarios)
│   ├── scenario_01_meeting_engagement.txt
│   ├── scenario_02_attack_defence.txt
│   ├── scenario_03_breakthrough.txt
│   └── [...]
├── 06_appendices/
│   ├── armor_penetration_table.txt
│   ├── special_rules_reference.txt
│   ├── terrain_rules.txt (desert-specific)
│   ├── weather_rules.txt
│   └── fire_support_tables.txt
└── battlegroup_[battle_name]_COMPLETE.pdf
```

**Key Features**:
- **Points System**: Reverse-engineered from official lists (base cost + modifiers)
- **Battle Rating**: Pattern-based assignment (company: 35-45, battalion: 60-80)
- **Movement Values**: Derived from weight/power ratio (light tanks: 12-14", medium: 8-10")
- **Armor Ratings**: Letter-based (A-O scale) converted from our mm values
- **Penetration Scale**: 1-15 values mapped from our penetration database
- **HE Effectiveness**: Caliber-based (20-37mm: 2/6+, 75-88mm: 4/4+, etc.)
- **Special Rules**: Doctrinal assignment (Unreliable, Elite, Scout, Engineer, etc.)
- **Scenarios**: 7+ per battle with victory conditions and special rules

**Project Structure**:
```
scripts/battlegroup/
├── scrapers/
│   ├── datacard_scraper.py (extract from PDFs/text)
│   └── army_list_analyzer.py (analyze official lists)
├── conversion/
│   ├── armor_converter.py
│   ├── penetration_converter.py
│   ├── movement_calculator.py
│   └── he_calculator.py
├── points/
│   ├── points_calculator.py
│   └── battle_rating_assigner.py
├── generators/
│   ├── datacard_generator.py
│   ├── force_list_compiler.py
│   ├── oob_formatter.py
│   └── scenario_generator.py
├── templates/
│   ├── datacard_vehicle.txt
│   ├── datacard_gun.txt
│   ├── force_list.txt
│   ├── scenario_briefing.txt
│   └── appendix_tables.txt
└── battlegroup_exporter.py (main orchestrator)
```

**Timeline**: 100-125 hours total
| Step | Task | Hours |
|------|------|-------|
| 1 | Datacard scraping & reference DB | 15-20 |
| 2 | Conversion formula development | 20-25 |
| 3 | Points/BR reverse engineering | 15-20 |
| 4 | Database schema extensions | 5 |
| 5 | Generator tools | 20-25 |
| 6 | Battle book assembly (12 books) | 15-20 |
| 7 | Validation & testing | 10 |

**Success Criteria**:
- [ ] Reference database: 200+ vehicle profiles, 150+ gun profiles scraped
- [ ] Conversion formulas: 95%+ accuracy vs official BattleGroup stats
- [ ] Points calculator: ±10% accuracy vs official army lists
- [ ] All 469 equipment items have BattleGroup stats generated
- [ ] 12 complete battle books (84+ scenarios total)
- [ ] Datacards match official format layout
- [ ] Force lists enforce historical restrictions
- [ ] Scenarios playtested and balanced

**Prerequisites**:
- ✅ Base architecture complete (Phase 9A)
- ✅ BattleGroup research complete (comprehensive analysis document)
- ✅ Conversion formulas documented (armor, penetration, movement, HE)
- ✅ Master database has 402 ground units + 469 equipment items
- ✅ 23 air summaries for aircraft integration

---

#### **Phase 9C: Achtung Panzer Implementation** 📋 **PLANNED**

**Goal**: Generate Achtung Panzer operational/tactical scenarios

**Prerequisites**: Achtung Panzer rulebook PDFs (user will provide)

**Timeline**: ~30-40 hours (research + implementation)

---

#### **Phase 9D: Flames of War Implementation** 📋 **PLANNED**

**Goal**: Generate Flames of War 15mm miniatures scenarios

**Prerequisites**: Flames of War rulebook PDFs (user will provide)

**Timeline**: ~30-40 hours (research + implementation)

---

#### **Phase 9E: Documentation & QA** 📋 **PLANNED**

**Goal**: Complete user documentation and scenario catalog

**Timeline**: ~8-12 hours

---

**Phase 9 Total Scenarios**:
- WITW: 369 scenarios ✅
- BattleGroup: 12 scenarios 📋
- Achtung Panzer: 12 scenarios 📋
- Flames of War: 12 scenarios 📋
- **Total**: 405 scenarios across 4 game systems

**Phase 9 Planned Battles** (12 major operations):
1. Operation Battleaxe (June 1941)
2. Operation Crusader (November 1941)
3. Gazala (May-June 1942)
4. First El Alamein (July 1942)
5. Alam Halfa (August-September 1942)
6. Second El Alamein (October-November 1942)
7. Operation Torch (November 1942)
8. Tunisia Campaign (December 1942 - May 1943)
9. Plus 4+ additional operations

---

### **Phase 10: Campaign System**

**Goal**: Complete campaign framework for 1940-1943

**Status**: Awaits completion of Phases 1-9

**Campaign Elements**:
- Quarterly transitions (how units evolved Q to Q)
- Supply line modeling (Tripoli → Benghazi → Tobruk routes)
- Weather patterns (seasonal impacts by quarter)
- Unit evolution tracking (equipment upgrades, reorganizations)
- Airfield data (Luftwaffe/RAF base locations and capacity)

**Deliverables**:
- Campaign framework (complete 1940-1943 timeline)
- Supply route data (historical port capacities, distances)
- Weather database (seasonal conditions by month/quarter)
- Unit transition tracking (formation, reorganization, dissolution)

**Timeline**: ~30-40 hours

---

## 📋 Complete Data Schema

### Ground Forces Schema (Phases 1-6)

**Version**: 3.0 (Updated 2025-10-13)

**Based on**: `F:\Timeline_TOE_Reconstruction\PROCESSING\STRATEGIC_COMMAND_SUMMARY_SCHEMA.md` (Iteration 2)

#### Section 1: COMMAND (2 fields)
- `supreme_commander` - Full rank and name
- `headquarters_location` - Geographic location with operational context

#### Section 2: PERSONNEL (3 fields)
- `total_strength` - Complete theater strength
- `total_infantry_strength` - Infantry personnel only
- `top_3_weapons` - Three most numerous infantry weapons with counts

#### Section 3: GROUND VEHICLES (27+ fields - VARIABLE)
**Core**: `ground_vehicles_total` - Rollup sum

**Standard Categories** (with variant breakdowns - NO ROLLUPS):
- `tanks` - Medium/heavy tanks (Panzer III/IV, M13/40, Sherman, Crusader, etc.)
- `light_tanks` - Light tanks and tankettes (Panzer I/II, L3/35, Stuart, etc.)
- `armored_cars` - Reconnaissance armored cars (SdKfz 222, AB41, Daimler, M8, etc.)
- `motorcycles` - Military motorcycles (BMW R75, Zündapp KS750, BSA M20, etc.)
- `trucks` - Transport trucks (Opel Blitz, Bedford, CMP, GMC, FIAT, etc.)
- `halftracks` - Halftrack carriers (SdKfz 251, Universal Carrier, M3, etc.)
- `specialized_vehicles` - Recovery, engineering, SPGs

**Optional Nation-Specific**:
- `artillery_tractors` - If separate from halftracks (SdKfz 7, SdKfz 11)
- `apcs` - If separate from halftracks
- `captured_vehicles` - If significant numbers
- `carriers` - British Universal/Bren carriers (if separate)

**CRITICAL RULE**: Every category MUST have variant-level breakdown. NO rollup counts.

#### Section 4: ARTILLERY (4 fields)
- `artillery_total` - Rollup sum
- `field_artillery` - Howitzers, guns (10.5cm leFH, 25-pdr, M1 105mm, etc.) WITH VARIANTS
- `anti_tank` - Towed AT guns (PaK 36/38/40, 6-pdr, 57mm, etc.) WITH VARIANTS
- `anti_aircraft` - AA guns (FlaK 18/36, Bofors, 90mm, etc.) WITH VARIANTS

#### Section 5: AIRCRAFT (4 fields) - AIR SUPPORT AVAILABLE
**IMPORTANT**: This shows air support ASSIGNED to ground forces, NOT organic aircraft.

- `aircraft_total` - Rollup sum
- `fighters` - Fighter aircraft (Bf 109, Spitfire, P-40, Hurricane, etc.) WITH VARIANTS
- `bombers` - Bombers and dive bombers (Ju 87 Stuka, Ju 88, Wellington, B-25, etc.) WITH VARIANTS
- `reconnaissance` - Reconnaissance aircraft (Bf 110, Lysander, P-38, etc.) WITH VARIANTS

**After Phase 8**: Will include `assigned_units` array with cross-links to air force unit IDs.

#### Section 6: SUPPLY/LOGISTICS (5 fields) - CRITICAL FOR SCENARIOS
- `supply_status` - Qualitative assessment with operational context
- `operational_radius` - Distance from main supply depot (kilometers)
- `fuel_reserves` - Days at current consumption rate
- `ammunition` - Days of combat supply
- `water` - Liters per day capacity (critical for desert operations)

#### Section 7: WEATHER/ENVIRONMENT (5+ fields) - NEW FOR SCENARIOS
- `season_quarter` - Which quarter and seasonal conditions
- `temperature_range` - Daily min/max temperatures (Celsius)
- `terrain_type` - Primary terrain (sand, rocky desert, coastal plain, etc.)
- `storm_frequency` - Sandstorms, Ghibli winds (days per month)
- `daylight_hours` - Average daylight hours (affects operational tempo)

---

### Air Forces Schema (Phase 7)

**Version**: 1.0 (For future implementation)

**Different from ground forces** - separate organizational structure.

#### Core Fields:
- `unit_designation` - Full air unit name (e.g., "I./Jagdgeschwader 27")
- `unit_type` - Fighter Gruppe, Bomber Staffel, etc.
- `parent_formation` - Parent wing/group
- `nation` - Germany, Britain, USA, Italy
- `quarter` - Which quarter
- `assigned_to_ground` - Which ground formation supported

#### Command:
- `commander` - Gruppe Kommandeur, Squadron CO, etc.
- `base` - Airfield location

#### Personnel:
- `pilots` - Aircrew count
- `ground_crew` - Maintenance personnel
- `mechanics` - Specialized mechanics
- `armorers` - Ordnance handlers
- `signals` - Radio/communications
- `total` - Total personnel

#### Aircraft:
- `total` - Total aircraft on strength
- `operational` - Combat-ready aircraft
- `variants` - Specific aircraft variants with counts

#### Ordnance:
- `ammunition` - Gun ammunition (rounds)
- `cannon_shells` - Cannon ammunition
- `fuel_liters` - Aviation fuel stocks
- `bombs` - Bomb stocks by type
- `drop_tanks` - External fuel tanks

#### Ground Support Vehicles:
- `fuel_bowsers` - Fuel tankers
- `bomb_dollies` - Ordnance transport
- `trucks` - General transport
- `staff_cars` - Command vehicles

#### Supply:
- `fuel_reserves_days` - Days of aviation fuel
- `ammunition_reserves_days` - Days of ammunition
- `sortie_rate_per_day` - Average sorties per aircraft per day
- `operational_radius_km` - Maximum combat radius

#### Operations History:
- Array of combat operations with dates, sorties, claims, losses

---

## 🎮 Three Primary Outputs (All Units)

### 1. MDBook - Professional Military History Publication

**Purpose**: Human-readable historical reference and analysis

**Structure**:
```
north_africa_campaign_book/
├── SUMMARY.md (Unit Index - all 313-348 units)
├── Quarter Overviews (13 quarters 1940-Q2 through 1943-Q2)
│   ├── Strategic situation
│   ├── Major operations
│   ├── Weather/environmental conditions
│   └── Supply line status
├── Ground Forces Chapters (213 chapters)
│   ├── Division Overview
│   ├── Command Structure
│   ├── Equipment Tables (Ground Vehicles, Artillery)
│   ├── Aircraft Section (Available Air Support)
│   ├── Supply & Logistics (NEW - fuel, ammo, water, operational radius)
│   ├── Operational Environment (NEW - weather, terrain, seasonal impacts)
│   ├── Tactical Doctrine
│   ├── Historical Context
│   ├── Sources & Bibliography
│   └── Data Quality & Known Gaps
├── Air Forces Chapters (~100-135 chapters - Phase 7)
│   ├── Unit Overview
│   ├── Command Structure
│   ├── Personnel (pilots, ground crew)
│   ├── Aircraft & Ordnance
│   ├── Ground Support Equipment
│   ├── Operations History
│   ├── Assignment to Ground Units
│   └── Sources & Data Quality
├── Methodology Documentation
├── Complete Bibliography (Chicago style)
└── Appendices (Glossary, Abbreviations, Maps)
```

**Quality Standards**:
- Minimum 80% confidence per unit
- Tier 1/2 sources only (NO Wikipedia)
- ALL equipment variants detailed (NO rollup counts)
- Complete source citations for every data point
- Cross-references between ground and air units (Phase 8+)

---

### 2. Wargaming Scenarios - Multi-Format (PRIMARY PURPOSE)

**Purpose**: Game-ready scenario data for multiple wargaming systems

**Directory Structure**:
```
scenarios/
├── unit_exports/
│   ├── witw_format/               # War in the West CSV
│   │   ├── ground_units/
│   │   │   ├── germany_1941q2_deutsches_afrikakorps.csv
│   │   │   ├── britain_1941q2_western_desert_force.csv
│   │   │   └── ... (213 ground units)
│   │   └── air_units/             # Phase 7
│   │       ├── luftwaffe_1941q2_i_jg27.csv
│   │       ├── raf_1941q2_274_sqn.csv
│   │       └── ... (~100-135 air units)
│   ├── toaw_format/               # The Operational Art of War
│   │   └── ... (similar structure)
│   └── generic_json/              # Universal scenario format
│       ├── ground_units/
│       └── air_units/
│
├── battle_scenarios/              # Historical operations (Phase 9)
│   ├── operation_battleaxe_1941q2/
│   │   ├── oob_ground.json        # Ground order of battle
│   │   ├── oob_air.json           # Air order of battle (Phase 8+)
│   │   ├── supply_state.json      # Fuel, ammo, water at battle start
│   │   ├── weather.json           # Environmental conditions June 1941
│   │   ├── air_support.json       # Available aircraft, sortie rates
│   │   ├── map_data.json          # Terrain, positions
│   │   └── victory_conditions.json
│   ├── operation_crusader_1941q4/
│   ├── gazala_1942q2/
│   ├── el_alamein_1942q3/
│   └── ... (12+ major operations)
│
└── campaign_data/                 # Campaign system (Phase 10)
    ├── quarterly_transitions/     # How units evolved Q to Q
    ├── supply_routes/             # Tripoli → Benghazi → Tobruk
    ├── airfield_data/             # Luftwaffe/RAF base locations
    └── weather_patterns/          # Seasonal impacts by quarter
```

**Critical Scenario Elements**:
- **Operational state**: Fuel days, ammo days, water reserves at scenario start
- **Weather conditions**: Temperature, visibility, storm probability
- **Supply line status**: Benghazi operational? Tobruk besieged? Distance from Tripoli
- **Aircraft availability**: Fighters, bombers, recon with operational counts and sortie rates
- **Unit readiness**: Percentage operational tanks, artillery, vehicles
- **Air-ground coordination**: Which Luftwaffe/RAF units assigned to which ground formations

**Export Formats**:
1. **WITW CSV**: War in the West compatible format
2. **TOAW**: The Operational Art of War format
3. **Generic JSON**: Modding support for HoI4, Decisive Campaigns, etc.
4. **Custom**: Extensible for additional wargame systems

---

### 3. SQL Database - Queryable Campaign Database

**Purpose**: Complex queries, analysis, scenario generation

**Database Schema**:
```sql
-- Core TO&E tables
CREATE TABLE units (
    unit_id VARCHAR PRIMARY KEY,
    unit_designation VARCHAR,
    nation VARCHAR,
    quarter VARCHAR,
    unit_type VARCHAR,  -- ground or air
    organizational_level VARCHAR,  -- division, gruppe, etc.
    total_strength INTEGER
);

CREATE TABLE personnel (...);
CREATE TABLE ground_vehicles (...);
CREATE TABLE artillery (...);
CREATE TABLE aircraft (...);

-- Logistics tables (NEW - Phase 1-6)
CREATE TABLE supply_state (
    unit_id VARCHAR REFERENCES units,
    supply_status TEXT,
    operational_radius_km INTEGER,
    fuel_reserves_days DECIMAL,
    ammunition_days DECIMAL,
    water_liters_per_day INTEGER
);

-- Environmental tables (NEW - Phase 1-6)
CREATE TABLE weather_conditions (
    quarter VARCHAR,
    month VARCHAR,
    temperature_min_c INTEGER,
    temperature_max_c INTEGER,
    terrain_type VARCHAR,
    storm_frequency_days INTEGER,
    daylight_hours DECIMAL
);

-- Air support tables (Phase 7-8)
CREATE TABLE air_units (
    unit_id VARCHAR PRIMARY KEY,
    unit_designation VARCHAR,
    nation VARCHAR,
    quarter VARCHAR,
    unit_type VARCHAR,  -- fighter, bomber, recon
    pilots INTEGER,
    ground_crew INTEGER,
    aircraft_total INTEGER,
    aircraft_operational INTEGER
);

CREATE TABLE air_ground_assignments (
    air_unit_id VARCHAR REFERENCES air_units,
    ground_unit_id VARCHAR REFERENCES units,
    quarter VARCHAR,
    sortie_rate DECIMAL,
    assignment_start DATE,
    assignment_end DATE
);

-- Scenario support tables (Phase 9-10)
CREATE TABLE battle_scenarios (
    scenario_id VARCHAR PRIMARY KEY,
    scenario_name VARCHAR,
    battle_date DATE,
    quarter VARCHAR,
    location VARCHAR,
    weather_id VARCHAR,
    victory_conditions TEXT
);

CREATE TABLE scenario_oob (
    scenario_id VARCHAR REFERENCES battle_scenarios,
    unit_id VARCHAR REFERENCES units,
    fuel_reserves_days DECIMAL,
    ammo_reserves_days DECIMAL,
    operational_percentage DECIMAL
);

CREATE TABLE campaign_transitions (
    unit_id VARCHAR REFERENCES units,
    from_quarter VARCHAR,
    to_quarter VARCHAR,
    changes TEXT,  -- JSON of equipment changes, reorganizations
    disbanded BOOLEAN,
    formed_new BOOLEAN
);

CREATE TABLE supply_routes (
    route_id VARCHAR PRIMARY KEY,
    from_port VARCHAR,
    to_location VARCHAR,
    distance_km INTEGER,
    operational BOOLEAN,
    capacity_tons_per_day INTEGER,
    quarter VARCHAR
);

CREATE TABLE airfields (
    airfield_id VARCHAR PRIMARY KEY,
    name VARCHAR,
    location VARCHAR,
    nation VARCHAR,
    quarter VARCHAR,
    capacity_aircraft INTEGER,
    runway_length_m INTEGER,
    fuel_storage_liters INTEGER
);
```

**Example Queries**:
```sql
-- What was German fuel state before Operation Battleaxe?
SELECT unit_designation, fuel_reserves_days, ammunition_days, operational_radius_km
FROM units u
JOIN supply_state s ON u.unit_id = s.unit_id
WHERE nation = 'Germany' AND quarter = '1941-Q2' AND unit_designation LIKE '%Afrika%';

-- How many operational Bf 109s available June 1941?
SELECT SUM(aircraft_operational) as operational_109s
FROM air_units
WHERE nation = 'Germany' AND quarter = '1941-Q2' AND unit_designation LIKE '%JG%';

-- What air units supported Deutsches Afrikakorps during Battleaxe?
SELECT a.unit_designation, a.unit_type, a.aircraft_operational, aga.sortie_rate
FROM air_units a
JOIN air_ground_assignments aga ON a.unit_id = aga.air_unit_id
WHERE aga.ground_unit_id = 'germany_1941q2_deutsches_afrikakorps';

-- Weather conditions during Operation Crusader?
SELECT * FROM weather_conditions
WHERE quarter = '1941-Q4' AND month = 'November';

-- Supply route capacity during Q2 1941?
SELECT * FROM supply_routes
WHERE quarter = '1941-Q2' AND operational = TRUE;
```

---

## ✅ Success Criteria

### Data Completeness (All 313-348 Units Must Have):

1. ✅ **Complete ground vehicle TO&E** (variant-level, NO rollups)
2. ✅ **Complete artillery breakdown** (field/AT/AA with variants)
3. ✅ **Complete aircraft data** (fighters/bombers/recon with variants)
4. ✅ **Complete logistics data** (supply status, fuel, ammo, water, operational radius)
5. ✅ **Environmental factors** (weather, terrain, seasonal impacts)
6. ✅ **Bottom-up aggregation validation** (parent = sum of children ±5%)
7. ✅ **Minimum 80% confidence** with Tier 1/2 sources only

### Output Quality:

8. ✅ **MDBook generates for all units** (professional quality, complete template)
9. ✅ **WITW scenarios export correctly** (CSV format validated)
10. ✅ **SQL database populated** with complete schema
11. ✅ **12+ battle scenarios** with OOB + supply + weather data
12. ✅ **Campaign transitions** documented quarter-to-quarter

### Scenario-Specific Requirements (Critical):

13. ✅ **Every ground unit has operational radius** (supply line constraints)
14. ✅ **Every ground unit has fuel/ammo reserves** (days at current consumption)
15. ✅ **Every quarter has weather data** (temperature, visibility, storms)
16. ✅ **Major battles have environmental conditions** documented
17. ✅ **Aircraft availability tracked** with operational counts
18. ✅ **Air-ground assignments** documented (which air units supported which ground)

### Quality Standards:

19. ✅ **NO Wikipedia sources** (Tier 1/2 only: Tessin, Army Lists, Field Manuals, Museums)
20. ✅ **ALL equipment variants detailed** (Sherman M4 vs M4A1, Panzer III Ausf F vs G)
21. ✅ **Complete source citations** (page numbers, archive references)
22. ✅ **Data quality sections** in all MDBook chapters (confidence scores, known gaps)

---

## 🚀 Current Status & Immediate Priorities

### Overall Progress (Updated 2025-10-27):
- **Ground Units**: ✅ **402/402 complete (100%)** - **PHASE 6 COMPLETE** 🎉
- **Complete Seed**: ✅ Generated with ALL 117 combat units (402 valid quarters after all corrections)
- **Air Force Units**: **68/~100-135 (~51-68%)** - **PHASE 7 IN PROGRESS**
- **Overall**: ✅ **100% Ground Forces** (402/402) + **~51-68% Air Forces** (68 extracted)

### Current Phase: Phase 6 (Ground Forces) - ✅ **COMPLETE** (100%)

**Complete Seed Generated** (October 15, 2025, updated Oct 23) ✅:
- ✅ Comprehensive battle research across 8 major operations
- ✅ Identified ALL 117 units that fought in North Africa (not just 36)
- ✅ 419 unit-quarters expanded from period ranges (2 invalid quarters removed Oct 23)
- ✅ Verified against authoritative sources (85-95% confidence)
- ✅ Master Unit Directory rebuilt with complete scope
- ✅ Validation-based count sync implemented (254/419 complete)

**Critical Discovery** (October 15, 2025):
- Original seed had only 36/117 units (31% of actual combat units) ❌
- Missing: Early war Italian divisions destroyed in Operation Compass
- Missing: Corps and army formations (XX Mobile Corps, 10th Army, etc.)
- Missing: Commonwealth allies (Polish, Czech, Greek units)
- Missing: Tunisia campaign units (1942q4-1943q2)
- **Fixed**: Complete seed now has ALL 117 units identified through systematic battle research ✅

**Immediate Priorities**:

1. ✅ **Phase 6: Ground Forces** - **COMPLETE** (402/402 units)
   - All valid unit-quarters extracted and validated
   - 9 units researched and confirmed destroyed/invalid (removed from scope)

2. **Priority 1: Complete Air Forces Extraction** (Phase 7 to 100%):
   - Current: 68/~100-135 complete (~51-68%)
   - Remaining: ~32-67 air units
   - **Target**: 15-30 hours autonomous processing

3. **Priority 2: Phase 8 Cross-Linking** (Air-Ground Integration):
   - Update ground units with `assigned_units` arrays in aircraft sections
   - Generate `data/output/campaign/air_ground_assignments/` tables
   - Cross-reference air units with 402 ground formations
   - **Target**: 20-30 hours (as stated in Phase 8 description)

---

## 🎮 Kickstarter Commercial Product Definition

**"North Africa 1940-1943: The Complete Wargamer's Database"**

### Product Description:

The most comprehensive North Africa Campaign database ever created for historical wargaming, featuring:

**Core Content**:
- ✅ 313-348 complete unit TO&Es (ground + air forces)
- ✅ Variant-level equipment detail (NO generic "tanks: 50" - every variant specified)
- ✅ Supply/logistics modeling (fuel reserves, ammo stocks, operational radius)
- ✅ Weather/environmental factors (seasonal impacts on operations)
- ✅ Complete air-ground integration (which Luftwaffe/RAF units supported which formations)

**Scenarios & Campaigns**:
- ✅ 12+ historical battle scenarios (Battleaxe, Crusader, Gazala, El Alamein, etc.)
- ✅ Complete 1940-1943 campaign system (quarterly progression)
- ✅ Supply line modeling (Tripoli → Benghazi → Tobruk routes)
- ✅ Air operations modeling (sortie rates, base locations)

**Formats & Compatibility**:
- ✅ Professional 500+ page MDBook publication
- ✅ WITW-compatible scenario exports (CSV)
- ✅ SQL database (queryable for custom scenarios)
- ✅ JSON exports (modding support for HoI4, Decisive Campaigns, etc.)

**Quality Guarantee**:
- ✅ 80%+ confidence (professional-grade research)
- ✅ Tier 1/2 sources only (Tessin, Army Lists, Field Manuals, Archives)
- ✅ Complete source citations (Chicago style bibliography)
- ✅ Transparent data quality (confidence scores, known gaps documented)

### Target Audience:
- **Primary**: Historical wargamers (WITW, TOAW, board games)
- **Secondary**: Game developers (scenario packs, commercial mods)
- **Tertiary**: Military historians, researchers, educators

### Unique Selling Points:
1. **Most comprehensive**: 313-348 units across ALL nations and organizational levels
2. **Scenario-ready**: Supply states, weather conditions, air support assignments
3. **Multi-format**: Works with multiple wargaming systems
4. **Professionally sourced**: Tier 1/2 sources only, complete citations
5. **Complete air-ground integration**: First database to model air support comprehensively

**Kickstarter Viability**: ✅ HIGHLY VIABLE

This scope is achievable, professionally valuable, and commercially marketable.

---

## 📚 Related Documentation

### Core Project Files:
- **`PROJECT_SCOPE.md`** (this file) - Complete project vision and phased approach
- **`VERSION_HISTORY.md`** - Technical version history and schema evolution (NEW)
- **`CLAUDE.md`** - Agent instructions and project overview
- **`docs/project_context.md`** - Technical architecture and design decisions
- **`SESSION_SUMMARY.md`** - Current session status and handoff

### Schema & Standards:
- **`schemas/unified_toe_schema.json`** - Ground forces data structure (v3.0 planned)
- **`docs/MDBOOK_CHAPTER_TEMPLATE.md`** - MDBook chapter template (v2.0)
- **`F:\Timeline_TOE_Reconstruction\PROCESSING\STRATEGIC_COMMAND_SUMMARY_SCHEMA.md`** - Iteration 2 baseline

### Agent Configuration:
- **`agents/agent_catalog.json`** - All 16 agent definitions
- **`src/orchestrator.js`** - Main orchestration engine
- **`src/single_session_orchestrator.js`** - Claude Code autonomous mode

### Progress Tracking:
- **`data/output/1941-q2-showcase/SHOWCASE_GAPS.md`** - Current issues identified
- **`data/output/autonomous_XXXXX/GAP_TRACKER.md`** - Data quality tracking
- **`WORKFLOW_STATE.json`** - Autonomous extraction progress

---

## 🔄 Version History

### v1.0.0 (2025-10-13) - Initial Comprehensive Scope Definition
- Defined complete project vision (ground + air forces + scenarios + campaign)
- Total scope: 313-348 units across all phases
- Established phased approach (Ground → Air → Integration → Scenarios → Campaign)
- Added supply/logistics requirements (fuel, ammo, water, operational radius)
- Added weather/environmental requirements (seasonal impacts, terrain effects)
- Clarified aircraft section purpose (air support AVAILABLE to ground units)
- Separated air force units (Phase 7 - own organizational structure)
- Defined scenario generation as primary purpose
- Established Kickstarter commercial product viability
- Created living document for ongoing updates

### v1.0.1 (2025-10-14) - Architecture v4.0 Update
- **Progress Update**: 202/213 ground units complete (94.8% - was 18/213, 8.5%)
- **Overall Progress**: 64.5% complete (was 5.8%)
- **Architecture v4.0**: Canonical output locations implemented
- **Canonical Paths**: All Phase 7-10 deliverables now reference canonical locations
  - Phase 7: `data/output/air_units/`, `data/output/air_chapters/`
  - Phase 8: `data/output/campaign/air_ground_assignments/`
  - Phase 9-10: `data/output/scenarios/`, `data/output/campaign/`
- **Duplicate Resolution**: Fixed duplicate file counting (207 → 202 unique units)
- **Phase 1-6 Status**: NEARING COMPLETION (11 units remaining)
- **Immediate Priorities**: Architecture v4.0 migration, complete remaining 11 units, prep Phase 7

### v1.0.2 (2025-10-14) - Progress Correction #1
- **CORRECTION**: Actual progress is 153/213 units (71.8%), not 202/213 (94.8%)
- **Reality Check**: 60 units remaining, not 11
- **Root Cause**: Consolidation script found 153 unique units after deduplication
- **Impact**: ~20-30 hours work remaining for Phase 1-6 (not ~3-5 hours)
- **Overall Progress**: 48.9% complete (153 of ~313-348 total units)
- **QA Improvement**: Added priority to improve unit counting validation
- **Lesson Learned**: QA process needs automated cross-checks between WORKFLOW_STATE.json and canonical directory

### v1.0.3 (2025-10-14) - CRITICAL DISCOVERY - Progress Correction #2
- **MAJOR CORRECTION**: Actual progress is 63/213 units (29.6%), NOT 153/213 (71.8%)!
- **Critical Finding**: 90 of the 153 completed units are NOT in current project scope
- **Orphaned Units Breakdown**:
  - 60 Italian units (various quarters/designations)
  - 17 British/Commonwealth units
  - 9 German units
  - 4 French units
- **Reality Check**: 150 units remaining (NOT 60!), ~50-75 hours work (NOT ~20-30 hours)
- **Root Cause**: `projects/north_africa_seed_units.json` was modified at some point, removing 90 units from scope
- **Impact**: Phase 1-6 is only 29.6% complete, overall project ~20.1% complete
- **Architecture v4.0 Success**: Skip-completed logic working correctly (orchestrator shows 150 remaining)
- **QA Failure**: MASSIVE scope mismatch went undetected until orchestrator unit ID matching was debugged
- **Decision Required**: What to do with 90 orphaned units (archive/restore/keep for reference)?
- **See**: `ORPHANED_UNITS_REPORT.md` for complete analysis and recommendations
- **Bug Fix**: Fixed autonomous orchestrator unit ID construction (nation mapping + quarter format + designation normalization)

### v1.0.4 (2025-10-14) - NAMING FIX - Correct Progress is 44.6%
- **FIX**: User correctly identified canonical naming as the issue!
- **Root Cause**: Strict string matching failed on name variations
  - Seed file: "4th Indian Division" → "4th_indian_division"
  - Completed: "4th Indian Infantry Division" → "4th_indian_infantry_division"
  - Strict match failed, fuzzy match succeeds ✅
- **CORRECTED NUMBERS**:
  - Progress: 95/213 (44.6%), NOT 63/213 (29.6%)
  - Remaining: 119 units, NOT 150
  - Orphaned: 58 units, NOT 90
  - Estimated time: ~40-50 hours, NOT ~50-75 hours
- **Fuzzy Matching Logic**: 60% word overlap threshold
  - Filters words >2 characters
  - Counts matching words between seed and completed designations
  - Much more forgiving of naming variations
- **Impact**: Progress aligns with user's week of 12-hour days! ✅
- **Fixed Files**:
  - `src/autonomous_orchestrator.js` - Uses fuzzy matching for skip-completed
  - `scripts/debug_unit_matching.js` - Detects naming mismatches
- **Lesson Learned**: Always use fuzzy matching for unit names (historical designations vary)

### v1.0.5 (2025-10-14) - SCOPE CLARIFICATION - Modified Hybrid Approach
- **CLARIFICATION**: Defined final scope using "Modified Hybrid Approach"
- **User's Rule**: "ALL UNITS THAT WERE ON SOIL IN AFRICA DURING WORLD WAR II between 1941 and 1943's last battle SHALL be included"
- **Location Analysis**: Analyzed all 153 completed units for physical location
  - 151 units IN AFRICA (Libya, Egypt, Tunisia) ✅
  - 2 units NOT in Africa (still in Italy preparing for deployment) ❌
- **Out of Scope Removals**:
  - `italian_1940q4_102_divisione_motorizzata_trento` (Trento, Northern Italy)
  - `italian_1941q2_101_divisione_motorizzata_trieste` (Piacenza, Italy - deploying August 1941)
- **Battle Participation**: 130/151 units have documented combat participation
  - Includes "garrison" divisions that fought defensively (61st Sirte, 62nd Marmarica, 63rd Cirene)
  - 22 units were destroyed/disbanded in combat
  - 12 units have unclear combat data (likely incomplete historical_engagements fields)
- **Scope Refinement**:
  - Total ground units: 211 (down from 213)
  - Completed: 151 (71.6%)
  - Remaining from seed: 60 units
  - Orphaned (not in seed): 56 units (legitimate garrison divisions that fought in battles)
- **Overall Progress**: ~45-48% complete (151 of ~311-346 total units)
- **Analysis Tools Created**:
  - `scripts/filter_battle_units.js` - Battle participation analysis
  - `scripts/analyze_remaining_seed_units.js` - Seed completion tracking
  - `data/output/BATTLE_PARTICIPATION_ANALYSIS.json` - Detailed categorization
  - `data/output/REMAINING_SEED_ANALYSIS.json` - Gap analysis
- **Decision**: Modified Hybrid = Units physically in Africa + participated in battles (offensive or defensive)

### v1.0.6 (2025-10-15) - COMPLETE SEED GENERATED - ALL 117 Combat Units
- **MILESTONE**: Complete North Africa seed generated with ALL units that fought in battles!
- **User's Directive**: "Identify ALL the units that fought in North Africa battles, not just italians, or one year or one quarter but ALL units"
- **Comprehensive Battle Research**: Systematically searched 8 major battles
  - Operation Compass (Dec 1940-Feb 1941)
  - Siege of Tobruk (Apr-Dec 1941)
  - Operation Crusader (Nov-Dec 1941)
  - Battle of Gazala (May-Jun 1942)
  - First/Second El Alamein (1942)
  - Operation Torch (Nov 1942)
  - Tunisia Campaign (Nov 1942-May 1943)
- **Complete Seed**: `projects/north_africa_seed_units_COMPLETE.json`
  - **117 unique units** (up from 36 in incomplete seed)
  - **420 unit-quarters** (up from 215)
  - **+225% increase in units**, **+95% increase in quarters**
  - All verified against authoritative sources (85-95% confidence)
- **Seed Expansion by Nation**:
  - German: 7 → 12 units (+5, +71%)
  - Italian: 10 → 31 units (+21, +210%) - largest expansion
  - British/Commonwealth: 13 → 31 units (+18, +138%)
  - American: 5 → 8 units (+3, +60%)
  - French: 2 → 7 units (+5, +250%)
- **Critical Missing Units Identified**:
  - Early war Italian divisions: Sirte, Marmarica, Cirene, Sabratha (destroyed Operation Compass)
  - Corps formations: XX Mobile Corps, XXI Corps, XXII Corps, X Corps, XIX Corps
  - Commonwealth allies: Polish Carpathian Brigade, Czech 11th Battalion, Greek Brigade
  - Tunisia units: Hermann Göring Division, 10. Panzer, Force L, March divisions
- **Current Completion**: 118/420 (28.1%) - dropped from 44.6% due to scope expansion
  - American: 13/23 (56.5%) - best coverage
  - German: 27/60 (45.0%) - good coverage
  - British: 57/162 (35.2%) - needs work
  - French: 3/19 (15.8%) - significant gap
  - Italian: 18/156 (11.5%) - **CRITICAL GAP**
- **Master Unit Directory Rebuilt**: 420 unit-quarters with complete scope
- **Canonical Matching Updated**: 66 exact + 52 alias = 118 matches
- **Files Generated**:
  - `projects/north_africa_seed_units_COMPLETE.json` - Complete seed
  - `data/canonical/COMPLETE_NORTH_AFRICA_COMBAT_UNITS.json` - Research source
  - `data/canonical/SEED_COMPARISON_REPORT.json` - Old vs new comparison
  - `data/canonical/MASTER_UNIT_DIRECTORY.json` - Updated directory
  - `scripts/generate_complete_seed.js` - Seed generation script
- **MCP Memory Updated**: Milestone, expansion stats, current status, priorities committed
- **Impact**: First historically complete and accurate seed for North Africa ground forces!

### v1.0.7 (2025-10-18) - PHASE 5: Equipment Matching & Database Integration
- **CRITICAL UPDATE**: Documented equipment matching as formal Phase 5 in project scope
- **User Feedback**: "This was a pivot slightly from the project scope" - CONFIRMED and addressed
- **Problem**: Equipment matching/database integration (WITW/OnWar/WWIITANKS merge) was NOT documented in PROJECT_SCOPE.md
- **Solution**: Restructured Phases 1-6 into distinct phases:
  - **Phase 1-4**: Database Infrastructure (COMPLETE ✅)
  - **Phase 5**: Equipment Matching & Database Integration (IN PROGRESS - 4.3%)
  - **Phase 6**: Ground Forces Unit Extraction (IN PROGRESS - 28.1%)
- **Strategic Rationale Clarified**:
  - Historical sources provide QUANTITIES (from Tessin, Army Lists)
  - Equipment databases provide SPECIFICATIONS (from OnWar, WWIITANKS)
  - Integration enables both accurate counts AND detailed specs
- **Detail Level Standards Documented** (CRITICAL):
  - **MDBook Chapters**: High-level overview + select detail (NO penetration tables, NO WITW IDs)
  - **WITW Scenarios**: Game-ready with WITW IDs + battle context/victory conditions/supply states (concise narratives, NO production history essays)
  - **SQL Database**: Complete - all data from all sources
- **Equipment Matching Progress**:
  - French: 20/20 items COMPLETE (100%)
  - American: 0/81 items (next priority)
  - German: 0/98 items (pending)
  - British: 0/196 items (pending - largest)
  - Italian: 0/74 items (pending)
  - **Total**: 20/469 items matched (4.3%)
- **Three-Source Integration**:
  - WITW Baseline: 469 canonical equipment items (scenario IDs)
  - OnWar: 213 AFV specifications (production data)
  - WWIITANKS: 612 AFVs + 343 guns (armor, penetration, ammunition)
- **Equipment Matcher v2.1**: Interactive CLI with type detection, cross-nation matching, research agent
- **Database Schema**: 11 tables (equipment, guns, ammunition, penetration_data, match_reviews, etc.)
- **Integration with Workflow**:
  - Phase 6 agents extract counts → Database enrichment adds specs → Chapter generation uses enriched data
  - Scenario exports use WITW IDs from database
  - Campaign tracking uses equipment transitions from database
- **Documentation Updated**:
  - PROJECT_SCOPE.md: Phase 5 added with complete detail level standards
  - EQUIPMENT_MATCHING_SCOPE_ANALYSIS.md: Comprehensive analysis document created
- **Files Created**:
  - `EQUIPMENT_MATCHING_SCOPE_ANALYSIS.md` - Full scope analysis
  - `tools/equipment_matcher_v2.py` - Equipment matcher (v2.1)
  - `FRENCH_MATCHING_COMPLETE.md` - French session summary
  - `FRENCH_RESEARCH_SUMMARY.md` - Research findings
- **Next Actions**: Update CLAUDE.md and VERSION_HISTORY.md with Phase 5 architecture
- **Impact**: First formal documentation of equipment matching phase - scope drift resolved

### v1.0.8 (2025-10-23) - Restoration & Progress Update
- **RESTORATION COMPLETE**: Implemented full restoration plan (RESTORATION_PLAN.md) - 12 tasks across 5 phases
- **Progress Acceleration**: +136 unit-quarters completed since Oct 15 (118 → 254, +115% increase)
- **Data Quality Corrections**: 2 invalid unit-quarters removed (419 total, down from 420)
  - XXX Corps 1941-Q2 (corps formed Sept 9, 1941 in Q3)
  - XXII Corps 1940-Q3 (corps did not exist until November 1940, Q4)
- **Schema v3.1.0 Documented**: Tiered extraction + discovered_units combat validation (VERSION_HISTORY.md)
- **Workflow Enforcement**:
  - Pre-flight validation script (`scripts/validate_session_readiness.js`) - checks environment before session start
  - Session start orchestration requirements (Task tool, MCP tools, canonical paths)
  - Work queue echelon-first sorting (enforces bottom-up aggregation globally)
  - Count sync validation (unit complete = JSON + chapter + validation)
- **Documentation Consolidated**:
  - CLAUDE.md rewritten (872 → 243 lines, 72% reduction)
  - START_HERE_NEW_SESSION.md updated with Session Management Protocol
  - Ken Prompt content merged into START_HERE
- **MCP Memory Integration**: 8 retroactive memory entities created (restored Oct 18-23 baseline knowledge)
- **Validator Enhanced**: Added 92 lines of v3.0.0/v3.1.0 validation logic (supply, weather, tier, combat_evidence)
- **Current Completion**: 254/419 (60.6%) - UP from 118/420 (28.1%) on Oct 18
  - American: improved coverage (priority: German, British, French, Italian remaining)
  - 165 unit-quarters remaining (~66-82 hours autonomous processing)
- **Root Cause Fixed**: MCP memory stub functions replaced with working retroactive entities
- **Session Stability**: 3-unit batches with automatic checkpoints, NO session limits
- **Documentation Updates**:
  - PROJECT_SCOPE.md: Updated progress (v1.0.8), data quality corrections noted
  - VERSION_HISTORY.md: Schema v3.1.0 entry added (tiered extraction + combat validation)
  - CLAUDE.md: Critical Rules section rewritten with 7 enumerated rules
- **Impact**: Workflow drift eliminated, baseline restored, count sync validated, 60.6% completion milestone

### v1.1.0 (2025-10-29) - Phase 7 Complete + Database Backfill Gap Identified
- **Phase 6 & 7 COMPLETE**: All ground forces (402/402) and air forces (23/23 summaries) extraction finished
- **Design Divergence Documented**: Phase 7 implemented as quarterly theater summaries instead of per-unit detail
  - Originally planned: ~100-135 detailed air unit JSONs with organic TO&E
  - Actually delivered: 23 quarterly aggregate summaries (functionally complete for scenarios)
  - Rationale: Scenarios need aggregate availability, not organic detail; detailed extraction deferred to post-MVP
- **Database Backfill Gap Identified**: SQLite master_database.db missing extracted units
  - Current: 144 units (Phase 1-4 WITW baseline only)
  - Expected: 402 ground units + 23 air summaries = 425 total
  - Missing: 258 ground units not in database (64% of extracted data)
  - Impact: Phase 9 scenario enrichment scripts blocked until database backfilled
- **Name Mapping Requirement**: Author/source variations need normalization
  - Example: "Deutsches Afrikakorps" vs "Deutsches Afrika-Korps" vs "DAK"
  - Equipment: "Panzer III Ausf. F" vs "PzKpfw III Ausf F" vs "Pz.Kpfw. III Ausf. F"
  - Solution needed: Canonical name + alias mapping system for fuzzy matching
- **Database Check Script Created**: `scripts/check_database_status.js` for quick status queries
- **Next Priority**: Phase 5.5 - Database backfill with name normalization before Phase 8-9
- **Overall Progress**: 425/425 extraction complete (100%), database integration pending

### v1.4.0 (2025-10-31) - Phase 9B BattleGroup System Scope Defined
- **Phase 9B Comprehensive Plan Added**: Complete BattleGroup book generation system designed
- **User Requirements Captured**: Complete book output (Battlegroup-Kursk style) for North Africa battles
- **Approach Defined**: Hybrid historical accuracy + game balance adjustments
- **7-Step Implementation Plan**:
  1. Datacard scraping (15-20 hours) - Build reference database from existing BG materials
  2. Conversion formulas (20-25 hours) - Armor/penetration/movement/HE converters with 95% accuracy target
  3. Points/BR system (15-20 hours) - Reverse engineer game balance mechanics (±10% tolerance)
  4. Database extensions (5 hours) - 11 new SQLite tables for BattleGroup-specific data
  5. Generator tools (20-25 hours) - Datacards, force lists, OOB, scenarios
  6. Battle books (15-20 hours) - 12 complete books with 7+ scenarios each
  7. Validation (10 hours) - Playtesting and accuracy checks
- **12 Battle Books Planned**: Compass, Sonnenblume, Tobruk, Battleaxe, Crusader, Gazala, First Alamein, Alam Halfa, Second Alamein, Torch, Tunisia, Mareth
- **Book Structure Defined**: 6-section format (intro, timeline, OOB, army lists, datacards, scenarios, appendices)
- **Key Mechanics Documented**:
  - Points System: Reverse-engineered from official lists (base + modifiers)
  - Battle Rating: Pattern-based (company: 35-45 BR, battalion: 60-80 BR)
  - Armor Conversion: mm thickness → letter scale (A-O)
  - Penetration Scale: mm @ distance → 1-15 values
  - Movement: Weight/type → inches (light tanks 12-14", medium 8-10", heavy 6-8")
  - HE Effectiveness: Caliber-based dice/target (20-37mm: 2/6+, 75-88mm: 4/4+)
- **Project Structure Defined**: `scripts/battlegroup/` with 5 subdirectories (scrapers, conversion, points, generators, templates)
- **Success Criteria**: 8 measurable deliverables (200+ vehicles, 150+ guns, 95% accuracy, 469 items, 84+ scenarios)
- **Timeline**: 100-125 hours total across 7 steps
- **Prerequisites Met**: Phase 9A architecture complete, research complete, master database ready (402 units, 469 equipment, 23 air summaries)
- **Next Action**: Begin Step 1 (datacard scraping) to build reference database
- **Commercial Impact**: Second major export format (WITW + BattleGroup), increases product value for Kickstarter
- **Documentation Created**: Comprehensive BattleGroup research report analyzing game mechanics, data requirements, conversion formulas

### Future Updates:
- **v1.5.0** (TBD): [Phase 9B Step 1-3 Complete - Reference database and conversion formulas]
- **v1.6.0** (TBD): [Phase 9B Complete - First BattleGroup books generated]
- **v1.7.0** (TBD): [Phase 9C-9D - Additional game systems]

---

## 📝 Update Procedure for This Living Document

When updating PROJECT_SCOPE.md:

1. **Update version number** (semantic versioning: major.minor.patch)
2. **Update "Last Updated" date** at top of file
3. **Add entry to Version History** section with changes
4. **Update VERSION_HISTORY.md if technical changes** (schema, template, agent modifications)
5. **Update relevant MCP memory** entities/observations if schema changes
6. **Git commit** with descriptive message: `docs: Update PROJECT_SCOPE to v1.1.0 - [changes]`
7. **Announce in session** if major changes affect current work

**Minor updates** (typos, clarifications): Patch version (v1.0.1)
**New sections/requirements**: Minor version (v1.1.0)
**Major scope changes**: Major version (v2.0.0)

---

**END OF PROJECT SCOPE v1.0.7**

**All agents, all sessions, all future work must reference this document.**

**For technical implementation details, see `docs/project_context.md` and `VERSION_HISTORY.md`**
**For current session status, see `SESSION_SUMMARY.md`**
**For agent instructions, see `CLAUDE.md`**
