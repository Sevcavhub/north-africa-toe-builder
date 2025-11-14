# Phase Architecture Map

**Date Created**: November 5, 2025
**Purpose**: Comprehensive mapping of tools, scripts, agents, schemas, and workflows by phase
**Status**: 🚧 IN PROGRESS - Initial mapping complete, detailed documentation ongoing

---

## 📋 Overview

This document maps the complete data flow through all 10 project phases, showing:
- **Inputs**: What each phase consumes
- **Agents**: Which agents process the data
- **Scripts**: Automation tools used
- **Schemas**: Data validation structures
- **NPM Commands**: Session management and workflow commands
- **Database Tables**: What gets created/populated
- **Outputs**: What each phase produces

---

## 🎯 Quick Reference: Script Inventory

**Total Scripts**: 327 files
- **Phase 1-7 (.js organized)**: 152 scripts (reorganized November 5, 2025)
- **Phase 9B (battlegroup/ .py)**: 93 scripts
- **Phase 9A (scenario_generation/ .py)**: 12 scripts
- **Phase 5.5 (normalization/ .sql)**: ~40 scripts
- **Phase 5.5 (linkage/ .sql)**: ~30 scripts

**Directory Structure** (updated November 5, 2025):
```
scripts/
├── phase_1_4_database/ ────────── Phase 1-4 setup (8 scripts)
│   ├── scrape_onwar_enhanced.js
│   ├── scrape_wwiitanks.js
│   ├── scrape_wwiitanks_enhanced_guns.js
│   ├── scrape_wwiitanks_enhanced_guns_v2.js
│   ├── import_name_variants.js
│   ├── parse_onwar_references.js
│   ├── parse_production_dates.js
│   └── research_production_dates.js
├── phase_6_ground_forces/ ─────── Phase 6 extraction (37 scripts)
│   ├── session_management/ ────── Session workflow (12 scripts)
│   ├── queue/ ─────────────────── Work queue (5 scripts)
│   ├── validation/ ────────────── Schema/source validation (9 scripts)
│   ├── content_generation/ ────── Chapters/TOE (9 scripts)
│   └── unit_management/ ───────── Unit filtering/enrichment (6 scripts)
├── phase_7_air_forces/ ────────── Phase 7 air forces (15 scripts)
│   ├── add_air_sections_to_chapters.js
│   ├── add_air_support_to_armies.js
│   ├── create_focused_air_seed.js
│   ├── generate_american_air_summaries.js
│   └── [11 more air forces scripts]
├── diagnostic/ ────────────────── Analysis tools (38 scripts)
│   ├── analysis/ ──────────────── Data analysis (15 scripts)
│   ├── checks/ ────────────────── Status checks (6 scripts)
│   ├── find/ ──────────────────── Discovery tools (12 scripts)
│   ├── investigation/ ─────────── Deep debugging (6 scripts)
│   └── lists/ ─────────────────── Listing utilities (4 scripts)
├── legacy/ ────────────────────── Migration/testing (19 scripts)
│   ├── migration/ ─────────────── Schema fixes (12 scripts)
│   ├── testing/ ───────────────── Test scripts (7 scripts)
│   └── database_setup/ ────────── Backfill scripts (5 scripts)
├── shared/ ────────────────────── Common utilities (20 scripts)
│   ├── lib/ ───────────────────── Shared libraries (10 modules)
│   ├── git_auto_commit.js
│   ├── memory_mcp_helpers.js
│   ├── search_sources.js
│   └── [17 more shared scripts]
├── battlegroup/ ───────────────── Phase 9B (Python)
│   ├── analysis/
│   ├── book/
│   ├── conversion/
│   ├── database/
│   ├── generators/
│   ├── manual_extraction/
│   ├── points/
│   ├── scrapers/
│   ├── templates/
│   └── validation/
├── scenario_generation/ ──────── Phase 9A (Python)
│   ├── base/
│   ├── converters/
│   ├── game_exporters/
│   └── templates/
├── database/ ─────────────────── Database files
├── linkage/ ──────────────────── Phase 5.5 (equipment linkage)
├── migration/ ────────────────── Phase 5 (data migration)
└── normalization/ ────────────── Phase 5.5 (database normalization)
```

**Reorganization Details** (November 5, 2025):
- Moved 152 .js scripts from flat root to phase-specific folders
- Preserved Git history with `git mv` commands
- Updated 50+ npm commands in package.json
- Fixed 27 PROJECT_ROOT path references
- Updated 14 lib/ require paths
- Deleted 62 empty folders in data/output/
- Commit: 3532a3af

---

## 📊 PHASE 1-4: Database Infrastructure

**Status**: ✅ COMPLETE (October 14-18, 2025)
**Duration**: ~4 hours
**Purpose**: Establish foundational database and import baseline data

### **Inputs**:
- `sources/WITW_EQUIPMENT_BASELINE.json` - 469 equipment items from War in the West game
- `sources/afv_data_onwar_*.json` - OnWar AFV data (213 vehicles)
- `sources/wwiitanks_*.json` - WWIITANKS data (612 AFVs, 343 guns, 162 ammo types, 1,296 penetration values)

### **Scripts**:
```
scripts/phase_1_4_database/
├── scrape_onwar_enhanced.js ───────── Scrape OnWar AFV data
├── scrape_wwiitanks.js ────────────── Scrape WWIITANKS data
├── scrape_wwiitanks_enhanced_guns.js ─ Scrape gun data
├── scrape_wwiitanks_enhanced_guns_v2.js ─ Enhanced gun scraping
├── import_name_variants.js ────────── Import equipment name variations
├── parse_onwar_references.js ──────── Parse OnWar source references
├── parse_production_dates.js ──────── Parse production date data
└── research_production_dates.js ───── Research production dates

scripts/database/
└── master_database.db ───────────────── SQLite database (18 tables)
```

### **Agents**: None (direct import scripts)

### **Database Tables Created** (11 tables):
1. `equipment` - WITW baseline (469 items)
2. `afv_data` - OnWar AFV data (213 vehicles)
3. `wwiitanks_afv_data` - WWIITANKS AFVs (612 vehicles)
4. `wwiitanks_gun_data` - WWIITANKS guns (343 guns)
5. `guns` - Gun specifications
6. `ammunition` - Ammunition types (162 types)
7. `penetration_data` - Penetration values (1,296 data points)
8. `units` - WITW units (144 units)
9. `unit_equipment` - Equipment assignments
10. `match_reviews` - Equipment matching metadata
11. `import_log` - Import provenance tracking

### **NPM Commands**: None (manual script execution during setup)

### **Outputs**:
- `database/master_database.db` - Populated SQLite database with 11 tables
- Foundation for all subsequent phases

---

## 🔗 PHASE 5: Equipment Matching & Database Integration

**Status**: ✅ COMPLETE (469/469 items matched, 99% success rate)
**Purpose**: Link WITW baseline to detailed specifications from OnWar and WWIITANKS

### **Inputs**:
- `database/master_database.db` - Equipment, AFV, gun tables from Phase 1-4
- User knowledge (interactive matching decisions)

### **Scripts/Tools**:
```
tools/equipment_matcher_v2.py (v2.1)
├── Interactive CLI matching workflow
├── Type detection (GUN, AFV, SOFT_SKIN, AIRCRAFT)
├── Cross-nation matching (captured/lend-lease)
├── Research agent integration
├── Name normalization
└── Match confidence scoring (100%, 85%, 70%)
```

### **Agents**:
- Research agent (automated web search for missing data) - integrated into matcher tool

### **Database Tables Updated**:
- `equipment` - Added `onwar_id` and `wwiitanks_id` foreign keys
- `match_reviews` - Match decisions with confidence scores

### **Matching Progress by Nation**:
- French: 20/20 (100%)
- American: 81/81 (100%)
- British: 196/196 (99%)
- German: 98/98 (96%)
- Italian: 74/74 (97%)

### **NPM Commands**: None (manual tool execution with user interaction)

### **Outputs**:
- 469/469 equipment items linked to OnWar/WWIITANKS specifications
- Complete three-source integration (WITW + OnWar + WWIITANKS)

---

## 🔄 PHASE 5.5: Database Normalization

**Status**: ✅ COMPLETE (November 3-4, 2025)
**Purpose**: Eliminate duplication, establish master naming table, support multi-game/multi-theater architecture

### **Inputs**:
- `database/master_database.db` - 4,669 equipment entries with massive duplication

### **Scripts** (11 normalization scripts, 3,051 lines):
```
scripts/normalization/
├── phase_a_master_consolidation.sql ───── De-duplication, name simplification
├── phase_b_data_quality_cleanup.sql ───── Extract org units, remove duplicates
├── phase_c_name_variant_population.sql ─ Generate name variants (2,234 variants)
├── phase_d_foreign_key_integration.sql ─ Update all foreign keys
└── qa_validation_suite.sql ────────────── 14 comprehensive QA tests

scripts/linkage/
├── tier1_exact_matches.sql ────────────── Exact name matches (19 items, confidence 100)
├── tier2_normalization.py ─────────────── Name variations (20 items, confidence 85-90)
├── tier3_base_model.py ────────────────── Variant stripping (41 items, confidence 80)
├── tier4_artillery_linkage.py ─────────── Artillery cross-reference (16 items, confidence 85-90)
└── execute_all_tiers.sql ──────────────── Comprehensive 4-tier linkage
```

### **Agents**:
- `agents/database_normalization_agent.json` - Guided normalization process
- `agents/name_variant_generator_agent.json` - Generated name variants

### **Database Changes**:
- **Before**: 4,669 rows, massive duplication
- **After**: 1,129 unique items in `equipment_master_new`
- **New Tables**:
  - `equipment_master_new` - 1,129 unique canonical items
  - `equipment_name_variants` - 2,234 name variants with 100% master coverage
  - `normalization_audit` - Audit trail for Tier 1-4 linkages

### **NPM Commands**: None (SQL script execution)

### **Outputs**:
- 8x data duplication eliminated
- Multi-game architecture ready (BattleGroup, Achtung Panzer, Flames of War)
- Multi-theater support (all theaters, not just North Africa)
- Zero data loss (QA validated)

---

## 📦 PHASE 6: Ground Forces Extraction

**Status**: ✅ COMPLETE (402/402 unit-quarters, 100%)
**Duration**: October 2025
**Purpose**: Extract complete TO&E data for 117 unique units across 402 unit-quarters

### **Inputs**:
- `projects/north_africa_seed_units_COMPLETE.json` - 117 units, 402 unit-quarters
- Historical sources (Tessin, Army Lists, Field Manuals, etc.)
- `database/master_database.db` - Equipment specifications

### **Scripts** (Session Management System):
```
scripts/phase_6_ground_forces/

session_management/ (12 scripts)
├── session_start.js ─────────────────── Initialize extraction session
├── session_end.js ───────────────────── End session with summary
├── validate_session_readiness.js ───── Pre-flight validation
├── process_queue_auto.js ────────────── Automated extraction
│   ├── --quick ─────────────────────── Fast mode
│   ├── --standard ──────────────────── Standard mode
│   ├── --extended ──────────────────── Extended mode
│   ├── --marathon ──────────────────── Marathon mode
│   └── --continuous ────────────────── Continuous mode
├── resume_paused_unit.js ────────────── Resume interrupted units
├── create_checkpoint.js ─────────────── Save progress checkpoint
├── checkpoint_safe.js ───────────────── Safe checkpoint with validation
├── recover_from_crash.js ────────────── Crash recovery
├── archive_old_sessions.js ──────────── Archive completed sessions
├── rebuild_workflow_state.js ────────── Rebuild workflow state
├── reconcile_workflow_state.js ──────── Reconcile workflow state
└── update_restoration_progress.js ───── Update restoration progress

queue/ (5 scripts)
├── generate_work_queue.js ───────────── Create unit queue
├── validate_work_queue.js ───────────── Validate queue structure
├── add_discovered_to_queue.js ───────── Add discovered units
├── collect_discoveries.js ───────────── Collect discovered units
└── create_extraction_plan.js ────────── Create extraction plan

validation/ (9 scripts)
├── validate-schema.js ──────────────── Schema v3.0.0/v3.1.0 validation
├── validate-no-wikipedia.js ─────────── Wikipedia blocking (4 layers)
├── validate_no_wikipedia.js ─────────── Wikipedia validation
├── qa_audit.js ──────────────────────── QA audit validation
├── validate_4_units.js ──────────────── Validate 4 units
├── validate_army_aggregation.js ─────── Validate army aggregation
├── validate_seed_against_authoritative.js ─ Validate seed against authoritative
├── validate_seed_phase1.js ──────────── Validate seed phase 1
└── final_status_check.js ────────────── Final status check

content_generation/ (9 scripts)
├── generate_mdbook_chapters.js ──────── Generate MDBook chapters
├── generate_single_chapter.js ───────── Generate single chapter
├── generate_missing_chapters.js ─────── Generate missing chapters
├── generate_31_missing_chapters.js ──── Generate 31 missing chapters
├── generate_toe_diagram.js ──────────── Generate TOE diagram
├── generate_reextraction_batch.js ───── Generate reextraction batch
├── generate_complete_seed.js ────────── Generate complete seed
├── consolidate_canonical.js ─────────── Consolidate canonical data
└── generate_final_expansion_summaries.js ─ Generate final expansion summaries

unit_management/ (6 scripts)
├── filter_battle_units.js ───────────── Filter battle units
├── enrich_units_with_database.js ────── Enrich units with database
├── backup_all_units.js ──────────────── Backup all units
├── cross_reference_seed.js ──────────── Cross reference seed
├── update_seed_with_aliases.js ──────── Update seed with aliases
└── canonical_master_matcher.js ──────── Canonical master matcher
```

### **Agents** (7 specialized agents):
```
agents/agent_catalog.json:
├── ground_unit_extractor ───────────── Extract unit TO&E data
├── research_specialist ─────────────── Web research for missing data
├── qa_auditor ──────────────────────── Quality assurance validation
├── chapter_summarizer ──────────────── Generate summary chapters
├── publisher ───────────────────────── Publish units/chapters
├── scenario_generator ──────────────── Generate battle scenarios
└── discovery_validator ─────────────── Validate discovered units
```

### **Schema**:
- `schemas/unified_toe_schema.json` (v3.0.0 → v3.1.0)
  - Required: unit metadata, organizational structure, equipment lists
  - Optional: supply/logistics (5 fields), weather/environment (5 fields)
  - Tiered extraction: Tier 1-4 (75-100% → <50% complete)
  - Validation: `combat_evidence` required for discovered units

### **NPM Commands** (Phase 6 Workflow):
```bash
npm run session:start          # Initialize session
npm run queue:generate         # Generate work queue
npm run auto:continuous        # Run continuous extraction
npm run checkpoint             # Save progress
npm run validate:v3            # Validate schema v3.0.0/v3.1.0
npm run validate:sources       # Validate no Wikipedia usage
npm run qa:v3                  # Full QA validation
npm run session:end            # End session with summary
```

**Slash Commands** (Phase 6):
```
/kstart                        # Start ground forces session (calls session:start)
/auto-continuous               # Run continuous ground extraction (calls auto:continuous)
/kend                          # End ground forces session (calls session:end)
```

### **Database Tables Updated**:
- `units` - 117 unique units
- Equipment assignments tracked via unit JSONs (not in database)

### **Outputs**:
- `data/output/units/*.json` - 402 unit JSONs with complete TO&E data
- `data/output/chapters/*.md` - MDBook summary chapters
- `data/output/scenarios/witw/*.csv` - WITW scenario CSVs (optional)

**Output Structure** (per unit):
```
data/output/units/
└── {nation}_{quarter}_{unit_name}.json
    ├── unit_metadata (name, nation, quarter, echelon, etc.)
    ├── organizational_structure (corps → division → regiment → battalion → company → platoon → squad)
    ├── equipment_list (tanks, guns, vehicles with quantities)
    ├── supply_logistics (fuel, ammo, water, operational radius, supply status)
    ├── weather_environment (terrain, temperature, seasonal impacts, environmental challenges)
    ├── combat_history (battles, engagements)
    └── validation (completeness tier, required_field_gaps)
```

---

## ✈️ PHASE 7: Air Forces Extraction

**Status**: ✅ COMPLETE (23 quarterly theater summaries, 100%)
**Duration**: October 2025
**Purpose**: Theater-wide air force summaries (not squadron-level detail)

### **Inputs**:
- Historical sources (Luftwaffe, RAF, USAAF, Regia Aeronautica records)
- Quarterly time slices (1941-Q1 through 1943-Q1, 9 quarters)

### **Scripts** (Air Forces Session Management):
```
scripts/phase_7_air_forces/ (15 scripts)
├── add_air_sections_to_chapters.js ──── Add air sections to MDBook chapters
├── add_air_support_to_armies.js ─────── Add air support to army units
├── add_american_air_support_sections.js ─ American air support integration
├── add_final_air_support_sections.js ─── Final air support integration
├── add_new_air_support_sections.js ──── New air support sections
├── create_focused_air_seed.js ───────── Create focused air seed
├── create_hybrid_air_summaries.js ───── Create hybrid air summaries
├── create_ultra_focused_air_seed.js ─── Create ultra focused air seed
├── extract_nafziger_air_pdf.js ──────── Extract Nafziger air force PDFs
├── generate_american_air_summaries.js ─ Generate American air summaries
├── generate_expansion_air_summaries.js ─ Generate expansion air summaries
├── generate_quarterly_air_overviews.js ─ Generate quarterly air overviews
├── generate_work_queue_air.js ───────── Generate air force work queue
├── regenerate_air_summaries_with_wikipedia.js ─ Regenerate with Wikipedia
└── search_nafziger_air_1941.js ──────── Search Nafziger 1941 air data

Note: Uses scripts/phase_6_ground_forces/session_management/session_start.js --air-forces
Note: Uses scripts/phase_6_ground_forces/session_management/session_end.js
```

### **Agents**:
```
agents/air_forces_agent_catalog.json:
├── air_unit_extractor ──────────────── Extract theater-wide summaries
├── research_specialist ─────────────── Web research
├── publisher ───────────────────────── Publish summaries
└── discovery_validator ─────────────── Validate discovered units
```

### **Schema**:
- `schemas/air_force_schema.json`
  - Theater-wide summaries (not squadron-level)
  - Aircraft types, quantities, operational status
  - Command structure (Geschwader/Gruppe level)

### **NPM Commands** (Phase 7 Workflow):
```bash
npm run air:start              # Start air forces session
npm run queue:generate:air     # Generate air force queue
npm run air:end                # End air forces session
```

**Slash Commands** (Phase 7):
```
/air-start                     # Start Air Forces extraction session (Phase 7)
/air-continuous                # Run continuous AIR FORCES extraction until queue is empty
/air-end                       # End Air Forces session and save progress to git
```

### **Database Tables**: None created (summaries stored as JSON/MD files)

### **Outputs**:
- `data/output/air_summaries/*.json` - 23 quarterly theater summaries
  - 9 quarters (1941-Q1 → 1943-Q1)
  - 4 nations (German, British, Italian, American)
- `data/output/air_chapters/*.md` - MDBook air force chapters

**Output Structure** (per quarter/nation):
```
data/output/air_summaries/
└── {nation}_{quarter}_air_summary.json
    ├── quarter
    ├── nation
    ├── theater_strength (total aircraft, operational aircraft)
    ├── command_structure (Geschwader/Group level)
    ├── aircraft_types (fighters, bombers, reconnaissance)
    └── operational_context
```

---

## 🔗 PHASE 8: Cross-Linking & Integration

**Status**: ✅ COMPLETE (OBE - Overtaken By Events, integrated during Phase 7)
**Purpose**: Link ground forces with available air support

### **Implementation**:
Integrated during Phase 7 extraction. 18 army-level units include air support references in their unit JSONs.

### **Scripts**: None (handled within Phase 7 workflow)

### **Agents**: None (integrated into Phase 7 agents)

### **Database Tables**: None

### **Outputs**: Air support references embedded in army-level unit JSONs

---

## 🎮 PHASE 9A: WITW Enhancement (Scenario Generation)

**Status**: ✅ COMPLETE (369 WITW scenarios, 91.8% of 402 units)
**Purpose**: Generate War in the West (WITW) game scenarios with pluggable architecture

### **Inputs**:
- `data/output/units/*.json` - 402 unit JSONs from Phase 6
- `database/master_database.db` - Equipment specifications with WITW IDs

### **Scripts** (Python, Pluggable Architecture):
```
scripts/scenario_generation/
├── base/
│   ├── scenario_base.py ──────────────── Base scenario class
│   └── unit_processor.py ─────────────── Process unit JSONs
├── converters/
│   ├── witw_converter.py ─────────────── WITW-specific conversion
│   └── equipment_mapper.py ───────────── Map to WITW equipment IDs
├── game_exporters/
│   ├── witw_exporter.py ──────────────── Export WITW CSV format
│   └── base_exporter.py ──────────────── Base exporter class
└── templates/
    └── witw_scenario_template.csv ───── WITW CSV template

Main scripts:
├── generate_witw_scenarios.py ────────── Generate all WITW scenarios
├── validate_witw_scenarios.py ────────── Validate scenario outputs
└── export_to_witw.py ─────────────────── Export to WITW game format
```

### **Agents**: None (direct script execution)

### **Database Tables**: None created (reads equipment table)

### **NPM Commands**: None (Python script execution)

### **Outputs**:
- `data/output/scenarios/witw/*.csv` - 369 WITW scenario CSVs
- Supply/weather/air support integration
- Pluggable architecture ready for future game systems

**WITW CSV Format**:
```
data/output/scenarios/witw/
└── {nation}_{quarter}_{unit_name}_witw.csv
    ├── Unit metadata (name, nation, date)
    ├── Equipment list (WITW IDs, quantities)
    ├── Supply status (fuel, ammo)
    ├── Weather conditions
    └── Air support available
```

---

## 📚 PHASE 9B: BattleGroup Book Generation

**Status**: ⏸️ ON HOLD (Reference data quality recovery)
**Purpose**: Generate 4 professional-quality BattleGroup wargame books

**Target Books**:
1. Operation Battleaxe (1941-Q2)
2. Operation Crusader (1941-Q4)
3. Battle of Gazala (1942-Q2)
4. First El Alamein (1942-Q3)

### **Inputs**:
- `data/output/units/*.json` - 402 unit JSONs from Phase 6
- `database/master_database.db` - Equipment specifications
- `Resource Documents/Battlegroup Game/` - Reference materials (PDFs, datacards)
- BattleGroup supplements (Canada's Crucible, British DataCards, etc.)

### **Scripts** (93 Python scripts):
```
scripts/battlegroup/
├── analysis/
│   └── battlegroup_research.py ────────────── Analyze BattleGroup mechanics
├── book/
│   ├── generate_book_datacards.py ─────────── ✅ PRODUCTION: Uses V5.5 generator (Nov 10 2025)
│   ├── generate_book_datacards_v5_3.py ────── V5.3 format (multi-row armament) [archived]
│   ├── generate_book_datacards_v5_4.py ────── V5.4 format (+ armor modifiers) [archived]
│   ├── generate_book_datacards_v5_5.py ────── ✅ V5.5 MODULE: Silhouettes + armor modifiers (LOCKED)
│   ├── generate_sample_datacards.py ───────── Test datacard generation (uses V5.5)
│   ├── generate_historical_chapters.py ───── Generate historical narratives
│   ├── generate_scenarios.py ──────────────── Generate battle scenarios
│   ├── generate_appendices.py ─────────────── Generate appendices
│   ├── validate_all_scenarios.py ──────────── Validate scenarios
│   └── qa_final_books.py ──────────────────── QA final book output
├── conversion/
│   ├── armor_converter.py ─────────────────── mm thickness → letter (A-O)
│   ├── penetration_converter.py ───────────── mm penetration → value (1-15)
│   ├── movement_calculator.py ─────────────── weight/type → inches
│   ├── he_calculator.py ───────────────────── caliber → HE effect (dice/target)
│   └── lookup_tables/ ─────────────────────── Conversion lookup tables
├── database/
│   ├── populate_bg_tables.py ──────────────── Populate BattleGroup tables
│   ├── update_equipment_battlegroup.py ────── Update equipment_battlegroup table
│   └── equipment_linkage_*.sql ────────────── Equipment linkage scripts
├── generators/
│   ├── datacard_generator.py ──────────────── Generate vehicle/gun datacards
│   ├── force_list_compiler.py ─────────────── Generate army lists
│   ├── oob_formatter.py ───────────────────── Generate OOB sections
│   └── scenario_generator.py ──────────────── Generate playable scenarios
├── manual_extraction/
│   ├── canada_*.py (41 scripts) ───────────── Manual extraction from Canada's Crucible
│   └── create_all_british_csv_templates.py ─ British DataCards OCR/CSV
├── points/
│   ├── points_calculator.py ───────────────── Calculate points cost
│   ├── battle_rating_assigner.py ──────────── Assign BR values
│   ├── defence_calculator.py ──────────────── Calculate defence points
│   └── fire_support_calculator.py ─────────── Calculate fire support costs
├── scrapers/
│   └── scrape_battlegroup_pdfs.py ─────────── Scrape reference data from PDFs
├── templates/
│   └── datacard_template_v4.md ────────────── V4 datacard format template
└── validation/
    └── validate_generators.py ─────────────── Validate generator output
```

### **Agents**: None (direct script execution, OCR-based extraction)

### **Database Tables Created** (8 new tables, 18 total):
```
Phase 9B Tables:
├── equipment_battlegroup ──────────────────── 469 items with BattleGroup stats
├── bg_reference_vehicles ──────────────────── 191 vehicles (schema v3.2 - Nov 8, 2025)
│   └── Schema v3.2: 34 columns (weapon_1-4, mount_1-4, ammo_1-4, Excel template compliant)
├── bg_reference_guns ──────────────────────── 57 reference guns
├── bg_reference_aircraft ──────────────────── Aircraft reference data
├── bg_armor_conversion ────────────────────── 16 armor thickness ranges (A-O)
├── bg_penetration_scale ───────────────────── 24 gun/caliber penetration mappings
├── bg_movement_values ─────────────────────── 20 vehicle type/weight movement ranges
├── bg_he_effectiveness ────────────────────── 9 caliber HE effectiveness ranges
└── bg_special_rules ───────────────────────── 57 special rules (1,599 equipment linkages)

Reference Data Tables (Canada's Crucible extraction):
├── BG_Reference_ArmyList_Examples ─────────── 105 army list units
├── BG_Reference_Defences ──────────────────── 22 defensive structures
├── BG_Scenario_Army_Lists ─────────────────── 4 scenarios
├── BG_Scenario_Forces ─────────────────────── 8 forces
├── BG_Scenario_Units ──────────────────────── 54 units with deployment
└── BG_Sample_maps ─────────────────────────── 4 sample maps
```

### **NPM Commands**: None (Python script execution, MDBook builds)

### **Book Build Commands**:
```bash
# Generate equipment datacards SCENARIO-BASED (November 14, 2025 - CURRENT)
python scripts/battlegroup/book/generate_book_datacards_from_scenarios.py --all
python scripts/battlegroup/book/generate_book_datacards_from_scenarios.py --battle tobruk

# Generate equipment datacards V5.5 (OLD - pulls all quarter equipment)
python scripts/battlegroup/book/generate_book_datacards_v5_5.py --all
python scripts/battlegroup/book/generate_book_datacards_v5_5.py --battle battleaxe

# Validate scenarios
python scripts/battlegroup/book/validate_all_scenarios.py

# QA final books
python scripts/battlegroup/book/qa_final_books.py

# Build MDBook HTML (all 12 battles)
cd books/battleaxe/book && mdbook build
cd books/crusader/book && mdbook build
cd books/gazala/book && mdbook build
cd books/tobruk/book && mdbook build
# ... (8 more battles)
```

### **Outputs** (4 books, 171+ files, 28,983+ lines):
```
books/{battle}/book/src/
├── chapter1/ ──────────────────────────────── Historical overview
│   ├── strategic_situation.md
│   ├── forces_engaged.md
│   └── battle_timeline.md
├── chapter2/ ──────────────────────────────── Equipment datacards
│   ├── tanks.md
│   ├── guns_and_artillery.md
│   ├── vehicles.md
│   ├── infantry_weapons.md
│   └── other_equipment.md
├── chapter3/ ──────────────────────────────── Historical scenarios
│   ├── scenario_01_*.md (45 scenarios total across 4 books)
│   └── [...]
├── forces/ ────────────────────────────────── Forces/TO&E tables (0% - needs script)
├── oob/ ───────────────────────────────────── Order of Battle sections
│   ├── oob_british.md
│   ├── oob_german.md
│   └── oob_italian.md
├── appendices/ ────────────────────────────── Reference appendices (100% complete)
│   ├── appendix_a_weapon_penetration.md (2,006 lines)
│   ├── appendix_b_special_rules.md (3,556 lines)
│   ├── appendix_c_citations.md (2,235 lines)
│   └── [9 more appendices]
└── tactical_templates/ ────────────────────── Tank/artillery templates (100% complete)
    ├── tank_platoons/ (6 templates)
    └── artillery_batteries/ (5 templates)
```

**Content Status**:
- ✅ Infrastructure: Database schema, conversion tools, book generation framework
- ✅ Historical chapters: 12 files, ~24,000 words
- ✅ Equipment special rules: 4 files, 1,543 lines
- ✅ Appendices: 12 files, 7,797 lines (zero placeholders, 181 citations)
- ✅ Tactical templates: 12 templates + 32 platoon/company files
- ✅ Scenarios: 45 scenarios with 95%+ parsing success
- ✅ V5 Datacard Format: LOCKED - Nation-specific colors, multi-row armament, special rules integration
- ⏸️ Equipment datacards: ON HOLD (format ready, need clean reference data for stats)
- ❌ Forces/TO&E tables: 0% (deferred - needs script)

**V5.5 Datacard Format Features** (November 11, 2025 - LOCKED):
- Nation-specific color themes (German, British, Italian, American, French)
- Multi-row armament tables (main gun + secondary weapons)
- Special rules as single italicized header line
- HE range value population (caliber-based)
- Silhouette images from `data/assets/tank_silhouettes/` directory
- Armor modifier display (e.g., "Open-topped") below armor values
- Compact spacing matching official BattleGroup cards
- Documentation: `docs/DATACARD_FORMAT_STANDARD.md`
- **Generator**: `scripts/battlegroup/book/generate_book_datacards_v5_5.py`

**Scenario-Based Datacard Generation** (November 14, 2025 - ✅ FIXED):
- **Problem**: V5.5 generator pulled ALL equipment from quarter, not scenario-specific
- **Solution**: New `generate_book_datacards_from_scenarios.py` script
- **Method**: Parses scenario markdown files to extract equipment names
- **Features**:
  - 4-tier equipment name resolution (exact, normalized, fuzzy, pattern)
  - Manual name mappings (e.g., "25-pdr" → "QF 25-pounder")
  - German gun normalization (88mm → 8.8cm)
  - Generic unit filtering (skips Infantry Platoon, Motorcycle Troops)
- **Results**: Tobruk 50+ items → 13 items (4 tanks matching scenarios exactly)
- **Status**: All 12 battles regenerated with scenario-based datacards (76%+ resolution rate)
- **Format Ready**: V5 datacard generator complete, awaiting validated equipment stats

---

## 🌐 WEB DEPLOYMENT: GitHub Pages + Render.com (November 12-14, 2025)

**Status**: ✅ **LIVE** - Frontend and backend deployed
**Purpose**: Public web access to books, interactive tools, and API endpoints

### **Frontend: GitHub Pages**
**URL**: https://sevcavhub.github.io/north-africa-toe-builder/
**Status**: ✅ Deployed (auto-deploy on git push to main)

**Pages**:
- `index.html` - Landing page with sticky navigation
- `tools.html` - Interactive tools (scenario generators, equipment search)
- `bibliography.html` - Research sources and citations reference page
- **12 Battle Books** - MDBook HTML outputs (134+ files per book)
  - `battleaxe/book/book/`, `crusader/book/book/`, `gazala/book/book/`, `tobruk/book/book/`
  - `first_alamein/book/book/`, `compass/book/book/`, `sonnenblume/book/book/`
  - `alam_halfa/book/book/`, `second_alamein/book/book/`, `torch/book/book/`
  - `tunisia/book/book/`, `mareth/book/book/`

**Features**:
- Sticky top navigation bar (About, Books, Interactive Tools, Bibliography)
- Feature cards with book contents ("Each book includes...")
- Equipment search with filters (name, nation, category)
- Random scenario generator (configurable points, nations, quarter)
- Historical scenario generator (quarter selection, location dropdown)

### **Backend: Render.com API**
**URL**: https://north-africa-toe-api.onrender.com
**Status**: ✅ Production ready
**Database**: 6.58 MB web_database.db (17 tables, optimized for deployment)

**API Endpoints**:
1. `GET /api/health` - Health check (status, version, database status)
2. `GET /api` - API info/documentation
3. `GET /api/equipment/search` - Equipment search with filters (name, nation, category)
4. `GET /api/equipment/<id>` - Equipment details by ID
5. `POST /api/scenarios/random` - Random scenario generator (points, nations, quarter)
6. `POST /api/scenarios/historical` - Historical scenario generator (location, quarter)
7. `GET /api/scenarios/locations/<quarter>` - Battle locations by quarter (1941q1-1942q4)

**Configuration**:
- Auto-deploy from main branch on git push
- CORS enabled for GitHub Pages frontend
- Error handling with JSON responses
- Logging enabled for debugging

### **Scripts**:
```
scripts/battlegroup/web/
├── railway_app.py ──────────────────────── Flask API (7 endpoints)
├── railway_config.py ───────────────────── Configuration
├── render.yaml ─────────────────────────── Render deployment config
└── database/
    └── web_database.db ─────────────────── Stripped database (6.58 MB vs 15.57 MB full)
```

### **Deployment Workflow**:
```bash
# Backend updates (Render.com)
git add scripts/battlegroup/web/railway_app.py
git commit -m "Update API endpoint"
git push origin main  # Auto-deploys within 2-5 minutes

# Frontend updates (GitHub Pages)
git add books/*/book/book/**/*.html index.html
git commit -m "Update books/landing page"
git push origin main  # Deploys within 1-5 minutes

# Database updates
# Upload to Render via web dashboard → Restart service
```

### **Git Commits** (Web Deployment):
- `d65ff456` - feat(render): Add Render.com deployment configuration
- `26bd33ee` - feat(render): Add temporary database upload endpoint
- `8a3fb197` - feat(web): Create stripped database for Render deployment
- `f0a1ce5f` - feat(web): Add navigation bar and bibliography page
- `371b1496` - fix(datacards): Generate equipment cards only from scenario units

---

## 🔄 PHASE 9C-E: Future Game Systems (PLANNED)

**Status**: 📋 PLANNED (pending Phase 9B completion and rulebook PDFs)

### **Phase 9C: Achtung Panzer**
- Pluggable scenario generation architecture ready
- Awaiting Achtung Panzer rulebook PDFs
- Will use scenario_generation/ framework pattern

### **Phase 9D: Flames of War**
- Pluggable scenario generation architecture ready
- Awaiting Flames of War rulebook PDFs
- Will use scenario_generation/ framework pattern

### **Phase 9E: Documentation & QA**
- Comprehensive documentation pass
- Final QA validation across all outputs
- Publication preparation

---

## 🎯 PHASE 10: Campaign System (PLANNED)

**Status**: 📋 PLANNED (30-40 hours estimated)
**Purpose**: Link multiple battles into campaign sequences

**Planned Features**:
- Sequential battle progression
- Unit persistence across battles
- Victory conditions
- Historical campaign paths

---

## 📊 Database Architecture (18 Tables)

### **Core Equipment Tables** (Phase 1-5):
```
equipment ──────────────────────────────────── 469 WITW baseline items
guns ──────────────────────────────────────── 343 gun specifications
ammunition ────────────────────────────────── 162 ammunition types
penetration_data ──────────────────────────── 1,296 penetration values
```

### **Normalization Tables** (Phase 5.5):
```
equipment_master_new ──────────────────────── 1,129 unique canonical items
equipment_name_variants ───────────────────── 2,234 name variants
normalization_audit ───────────────────────── Tier 1-4 linkage audit trail
```

### **Source Data Tables** (Phase 1-4):
```
afv_data ──────────────────────────────────── OnWar AFV data (213 vehicles)
wwiitanks_afv_data ────────────────────────── WWIITANKS AFVs (612 vehicles)
wwiitanks_gun_data ────────────────────────── WWIITANKS guns (343 guns)
```

### **Unit Assignment Tables** (Phase 6):
```
units ─────────────────────────────────────── 117 unique units
unit_equipment ────────────────────────────── Equipment assignments (from unit JSONs)
```

### **BattleGroup Tables** (Phase 9B):
```
equipment_battlegroup ─────────────────────── 469 items with BattleGroup stats
bg_reference_vehicles ─────────────────────── 191 vehicles (schema v3.2 as of Nov 8, 2025)
  ├── 34 columns: weapon_1-4, mount_1-4, ammo_1-4
  ├── Nations: british (78), german (63), italian (26), canadian (12), canadian/british (12)
  ├── Sources: Legacy (41), Canada's Crucible (20), British DataCards (80), Tobruk (50)
  └── Ammo coverage: 100/191 (52.4%)
bg_reference_guns ─────────────────────────── 57 reference guns
bg_reference_aircraft ─────────────────────── Aircraft reference data
bg_armor_conversion ───────────────────────── 16 armor ranges
bg_penetration_scale ──────────────────────── 24 penetration mappings
bg_movement_values ────────────────────────── 20 movement ranges
bg_he_effectiveness ───────────────────────── 9 HE effectiveness ranges
bg_special_rules ──────────────────────────── 57 special rules
```

### **Metadata Tables**:
```
match_reviews ─────────────────────────────── Equipment matching decisions
import_log ────────────────────────────────── Data provenance tracking
```

---

## 🗂️ Data Output Structure

### **Phase 6 Outputs** (Ground Forces):
```
data/output/
├── units/ ────────────────────────────────── 402 unit JSONs
├── chapters/ ─────────────────────────────── MDBook summary chapters
└── scenarios/ ────────────────────────────── Optional WITW CSVs
```

### **Phase 7 Outputs** (Air Forces):
```
data/output/
├── air_summaries/ ────────────────────────── 23 quarterly theater summaries
└── air_chapters/ ─────────────────────────── MDBook air force chapters
```

### **Phase 9A Outputs** (WITW Scenarios):
```
data/output/scenarios/witw/ ──────────────── 369 WITW scenario CSVs
```

### **Phase 9B Outputs** (BattleGroup Books):
```
books/
├── battleaxe/
│   └── book/src/ ─────────────────────────── MDBook source
├── crusader/
│   └── book/src/
├── gazala/
│   └── book/src/
└── first_alamein/
    └── book/src/
```

### **Session Tracking**:
```
data/output/sessions/ ─────────────────────── Autonomous session logs (100+ sessions)
```

### **Archived/Temporary**:
```
data/output/
├── _archived/ ────────────────────────────── Archived data from previous iterations
├── battle_scenarios/ ─────────────────────── Generated battle scenarios (legacy?)
├── companies/ ────────────────────────────── Company-level extractions
├── platoons/ ─────────────────────────────── Platoon-level extractions
├── diagrams/ ─────────────────────────────── Silhouettes and diagrams
└── [various session folders] ─────────────── Session-specific outputs
```

---

## 🧹 Cleanup Candidates (TO BE REVIEWED)

### **Potentially Obsolete Scripts** (needs user review):
```
scripts/
├── [152 .js root files] ──────────────────── Some may be Phase 1-6 legacy, needs audit
├── scrape_wwiitanks*.js ─────────────────── Phase 1-4 scrapers (one-time use?)
└── [various session management scripts] ──── Active or obsolete?
```

### **Potentially Empty/Obsolete Folders** (needs user review):
```
data/output/
├── autonomous_$(date +%Y%m%d_%H%M%S)/ ────── Template folder? (never used)
├── companies/ ────────────────────────────── Empty or used?
├── platoons/ ─────────────────────────────── Empty or used?
├── diagrams/ ─────────────────────────────── Empty or used?
├── battle_scenarios/ ─────────────────────── Legacy or active?
└── [100+ session folders] ────────────────── Can be archived?
```

---

## 📋 Next Steps for Architecture Cleanup

### **1. Audit Script Usage** (User Decision):
- Review 152 root .js files - which are active Phase 6 tools vs obsolete?
- Categorize by phase
- Move to phase-specific folders or archive

### **2. Clean Data Outputs** (User Decision):
- Archive old session folders (100+ sessions in data/output/sessions/)
- Remove empty folders
- Consolidate legacy outputs

### **3. Reorganize into Phase Folders** (Proposed Structure):
```
scripts/
├── phase_1_4_database/
│   └── [database setup scripts]
├── phase_5_equipment_matching/
│   └── [equipment matcher tools]
├── phase_5_5_normalization/
│   └── [normalization + linkage scripts]
├── phase_6_ground_forces/
│   └── [session management + extraction]
├── phase_7_air_forces/
│   └── [air force extraction]
├── phase_9a_witw/
│   └── [WITW scenario generation]
├── phase_9b_battlegroup/
│   └── [current battlegroup/ folder]
└── shared/
    └── [lib/, common utilities]
```

### **4. Document Active vs Obsolete** (This Document):
- Mark each script as ACTIVE, LEGACY, or OBSOLETE
- Create migration plan for phase-specific reorganization
- User approval before major restructuring

---

**Status**: 🚧 Initial mapping complete. Ready for user review and cleanup planning.

**Next Actions**:
1. User reviews script audit findings
2. User identifies empty folders for deletion
3. User approves phase-specific reorganization plan
4. Execute cleanup and reorganization

**Updated**: November 5, 2025
