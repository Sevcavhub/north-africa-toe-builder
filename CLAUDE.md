# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

---

## 🌟 What Is This Project? (Simple Explanation)

**Imagine building a collection of books about World War 2 tank battles in North Africa...**

**What We're Building**: Professional wargaming scenario books (like official Battlegroup-Kursk.pdf)
- 4 beautiful books: Operation Battleaxe, Operation Crusader, Battle of Gazala, First El Alamein
- Each book has equipment cards showing tanks/guns with pictures and stats
- Historical scenarios you can play out on a tabletop
- Maps, timelines, and stories about what really happened
- Quality good enough to print and sell in stores

**How We Built It** (The 10-Phase Journey):
1. **Phases 1-4**: Built a giant database of WW2 equipment (469 tanks, guns, trucks)
2. **Phase 5**: Matched our equipment to detailed specs (armor thickness, gun power, speed)
3. **Phase 6**: Extracted data on 117 military units (who had what tanks, where they fought)
4. **Phase 7**: Added air force data (planes supporting ground troops)
5. **Phase 8**: Connected everything together (which planes helped which tanks)
6. **Phase 9A**: Created computer game scenarios (WITW format)
7. **Phase 9B** ← **WE ARE HERE**: Creating beautiful printed books (BattleGroup format)
8. **Phases 9C-E**: Will create books for other game systems (Achtung Panzer, Flames of War)
9. **Phase 10**: Campaign system (link multiple battles together)

**Phase 9B - What We're Doing Right Now**:
- Making equipment datacards (like baseball cards but for tanks!)
- Each card shows: picture, armor values, weapon stats, movement speed
- Writing historical scenarios (12 tanks vs 8 tanks with AT guns at Halfaya Pass)
- Creating organization charts (who commanded which units)
- Building 4 complete books ready to print as PDFs

**Quality Standard**: Publication-ready professional books
- Looks like official Battlegroup-Kursk.pdf (see Resource Documents folder)
- Equipment cards match Datacard Examples.png exactly
- Organization charts match OOB Example.png format
- Could actually sell these in a game store

**Current Challenge**: Equipment linkage at 20% (need 100%)
- Can't publish a book with "None" for tank weapons
- Can't show "???" for armor thickness
- Every piece of equipment needs complete data
- Multiple data sources available - need to connect them all

---

## 🎯 Quick Orientation

**Project**: North Africa TO&E Builder (Table of Organization & Equipment)
**Current Phase**: BattleGroup Book Generation (Phase 9B of 10)
**Progress**: 85-90% complete (MVP near ready, polish remaining)
**Schema**: v3.1.0 (tiered extraction, supply/logistics, weather/environment)
**Primary Purpose**: Generate wargaming scenarios with realistic historical data

**Key Documents** (read these for complete context):
- `PROJECT_SCOPE.md` - Complete project vision and phased approach (**LIVING DOCUMENT**)
- `PHASE_9B_NEXT_STEPS.md` - Current phase work breakdown and remaining tasks
- `PHASE_9B_SESSION_SUMMARY.md` - Detailed session history and accomplishments
- `START_HERE_NEW_SESSION.md` - Session workflow and management protocol
- `schemas/unified_toe_schema.json` - Data structure requirements

---

## 📋 Project Progress (All 10 Phases)

### **Completed Phases** ✅

- **Phase 1-4: Database Infrastructure** ✅ **COMPLETE (100%)**
  - SQLite master database (11 tables)
  - WITW baseline (469 equipment items)
  - OnWar AFV data (213 vehicles)
  - WWIITANKS data (612 AFVs + 343 guns + 1,296 penetration values)

- **Phase 5: Equipment Matching** ✅ **COMPLETE (100%)**
  - 469/469 equipment items matched (99% success rate)
  - Three-source integration (WITW + OnWar + WWIITANKS)
  - All nations complete: French (100%), American (100%), British (99%), German (96%), Italian (97%)

- **Phase 6: Ground Forces Extraction** ✅ **COMPLETE (100%)**
  - 402/402 unit-quarters extracted
  - 117 unique units with complete TO&E data
  - All nations complete: British/Commonwealth (154), Italian (147), German (59), American (23), French (19)

- **Phase 7: Air Forces Extraction** ✅ **COMPLETE (100%)**
  - 23 quarterly theater-wide summaries
  - 9 quarters (1941-Q1 through 1943-Q1)
  - 4 nations (German, British, Italian, American)

- **Phase 8: Cross-Linking & Integration** ✅ **COMPLETE (OBE)**
  - Integration accomplished during Phase 7
  - 18 army-level units include air support references
  - Theater air strength integrated at appropriate command echelon

- **Phase 9A: WITW Enhancement** ✅ **COMPLETE (100%)**
  - 369 WITW scenarios exported (91.8% of 402 units)
  - Pluggable scenario generation architecture
  - Supply/weather/air support integration

### **Current Phase** 🎯

- **Phase 9B: BattleGroup Book Generation** 🎯 **85-90% COMPLETE** ← **YOU ARE HERE**
  - Foundation & Tools (Steps 1-5): **100% COMPLETE** ✅
  - Book Content (Step 7): **85-90% COMPLETE**
    - ✅ Equipment datacards: V4 format complete, database linkage started (20%)
    - ✅ Historical chapters: 100% (12 files, ~24,000 words)
    - ✅ Equipment special rules: 100% (4 files, 1,543 lines)
    - ✅ Appendices: 100% (12 files, 7,797 lines, zero placeholders)
    - ✅ Tactical templates: 100% (12 templates + 32 files)
    - ✅ Scenarios: 100% (45 scenarios with 95%+ parsing success)
    - ❌ Forces/TO&E tables: 0% (CRITICAL BLOCKER - needs script)
  - **Remaining**: 4-7 hours to core MVP

### **Future Phases** 📋

- **Phase 9C: Achtung Panzer** 📋 PLANNED (pending rulebook PDFs)
- **Phase 9D: Flames of War** 📋 PLANNED (pending rulebook PDFs)
- **Phase 9E: Documentation & QA** 📋 PLANNED
- **Phase 10: Campaign System** 📋 PLANNED (30-40 hours estimated)

---

## 📊 Phase 9B Current Work (BattleGroup Books)

**Scope**: Generate 4 professional-quality books for BattleGroup wargame system
- Operation Battleaxe (1941-Q2)
- Operation Crusader (1941-Q4)
- Battle of Gazala (1942-Q2)
- First El Alamein (1942-Q3)

**Quality Standard**: **Publication-ready** (match Battlegroup-Kursk.pdf quality)
- Equipment datacards match `Resource Documents/Battlegroup Game/Datacard Examples.png`
- OOB sections match `Resource Documents/Battlegroup Game/OOB Example.png`
- Professional layout, zero placeholders, comprehensive citations
- Print-ready PDFs (2-5 MB each, A4 landscape)

**Current Status** (as of November 3, 2025):
- **Content Created**: 171+ files, 28,983+ lines
- **Equipment Database Linkage**: 96/469 items (20.5% coverage) - **NEEDS 100%**
- **Conversion Formula Accuracy**: 97-100% (exceptional validation)
- **Books Generated**: All 4 MDBook HTML builds complete (134 HTML files)
- **Scenarios**: 45 historical scenarios with combined arms validation

**CRITICAL BOTTLENECK**: Equipment Linkage at 20%
- **Current**: 96/469 items have complete data (armor, weapons, penetration)
- **Required**: 469/469 items (100% coverage) for publication quality
- **Why It Matters**: Can't publish with "None" weapons or "???" armor values
- **Available Sources**: bg_reference_vehicles (500), bg_reference_guns (57), WWIITANKS (612 AFVs + 343 guns)
- **Strategy**: Reverse-engineer from multiple complementary data sources

**Database Linkage System** (Created Nov 3, 2025):
- **Tier 1 (Exact)**: 19 items - Direct name matches, confidence 100
- **Tier 2 (Normalized)**: 2 items - Name variations, confidence 85-90
- **Tier 3 (Base Model)**: 10 items - Variant stripping, confidence 80
- **Tier 4 (Artillery)**: 16 items - Artillery-specific matching, confidence 85-90
- **Session Additions**: +47 new tank linkages (Stuart, Sherman, Crusader, etc.)
- **Total**: 96 items linked (vehicles 80, guns 16)

**Remaining Work to MVP** (4-7 hours):
1. **Equipment Linkage Completion** (HIGH PRIORITY)
   - Expand from 20% to 100% coverage (373 items remaining)
   - Fix weapon performance table population
   - Fix tank categorization logic
   - Create infantry weapon template

2. **Forces/TO&E Tables** (CRITICAL BLOCKER - 3-4 hours)
   - Extract from Phase 6 unit JSONs (402 units)
   - Organizational hierarchy: Corps → Division → Regiment → Battalion → Company
   - Currently BLANK - needs script creation

3. **Production Polish** (1-2 hours)
   - Adapt OOB sections to BattleGroup style
   - Remove attribution text
   - Generate production PDFs (2-5 MB each)

4. **Final Validation** (1 hour)
   - QA suite execution
   - Schema compliance validation
   - Update PROJECT_SCOPE.md

---

## ⚠️ Critical Rules (MUST FOLLOW)

### 1. Publication Quality Standard
- **Every equipment item** must have complete data (armor, weapons, penetration, movement)
- **Zero placeholders** allowed (no "None", "???", "TBD")
- **Professional formatting** matching official BattleGroup books
- **Comprehensive citations** (181 Phase 6 citations, 71 archive references already in appendices)

### 2. Equipment Linkage Requirement
- **100% coverage required** for publication (not 90%, not 95%)
- Use ALL available data sources:
  - `bg_reference_vehicles` (500 vehicles with armor/weapons/movement)
  - `bg_reference_guns` (57 guns with HE/AP penetration)
  - `wwiitanks_afv_data` (612 AFVs with detailed specs)
  - `wwiitanks_gun_data` (343 guns with penetration tables)
  - `penetration_data` (1,296 penetration values)
  - `equipment_battlegroup` (469 items with BattleGroup stats)
- Reverse-engineer missing data from complementary sources
- Confidence scoring: Document match quality (100, 90, 85, 80, 75)

### 3. Data Integrity
- **Seed Authority**: Phase 6 unit JSONs are authoritative for equipment lists
- **Nation Values**: Use canonical values (german, italian, british, american, french)
- **Quarter Format**: Lowercase, no hyphen (1941q2, NOT 1941-Q2)
- **Combat Participation**: Only units with documented North Africa combat

### 4. File Organization (Architecture v4.0)
**Equipment Datacards**:
- Location: `books/[battle]/book/src/chapter2/[category].md`
- Categories: tanks.md, guns_and_artillery.md, vehicles.md, infantry_weapons.md, other_equipment.md
- Format: V4 datacard format (3x2 grid, A4 landscape, locked CSS)

**Forces/TO&E Tables**:
- Location: `books/[battle]/book/src/forces/[unit_type].md`
- Source: Phase 6 unit JSONs (`data/output/units/*.json`)
- Structure: Hierarchical (Corps → Division → Regiment → Battalion)

**OOB Sections**:
- Location: `books/[battle]/book/src/oob/oob_[nation].md`
- Format: Three-column layout matching OOB Example.png
- Content: Army → Corps → Division hierarchy

### 5. Validation Requirements
**Book is complete ONLY when ALL pass**:
1. ✅ Equipment datacards: 100% items linked with complete data
2. ✅ Forces/TO&E tables: All relevant Phase 6 units included
3. ✅ OOB sections: All nations formatted correctly
4. ✅ Scenarios: 45 scenarios validated (combined arms compliance)
5. ✅ Appendices: Zero placeholders, comprehensive citations
6. ✅ Production PDFs: 2-5 MB each, A4 landscape, print-ready

---

## 📐 Schema v3.1.0 Overview

**Tiered Extraction System** (handles incomplete data gracefully):
- **Tier 1** (75-100% complete): `production_ready`
- **Tier 2** (60-74%): `review_recommended`
- **Tier 3** (50-59%): `partial_needs_research`
- **Tier 4** (<50%): `research_brief_created`

**Required Sections** (v3.0.0+):
- `supply_logistics` (5 fields): fuel, ammo, water, operational radius, supply status
- `weather_environment` (5 fields): terrain, temperature range, seasonal impacts, environmental challenges

**Optional Features** (v3.1.0+):
- `discovered_units` array (with combat_evidence validation)
- `validation.required_field_gaps` array
- `validation.gap_documentation` object

**See complete schema**: `schemas/unified_toe_schema.json`

---

## 🗄️ Equipment Database Architecture

**As of November 2025**, the project uses a **three-source equipment database** to provide comprehensive specifications beyond what historical documents contain.

### Strategic Rationale

**The Problem**:
- Historical sources (Tessin, Army Lists, Field Manuals) provide equipment **QUANTITIES**
  - Example: "60x Panzer III Ausf F" (from Tessin Vol 12)
- But these sources **DON'T provide detailed specifications**:
  - Armor thickness values
  - Gun penetration tables
  - Production dates and quantities
  - Performance data (speed, range, crew)

**The Solution**:
- **Phase 5 (Equipment Matching)** links WITW baseline to detailed specifications
- **Phase 9B (Database Linkage)** connects equipment to BattleGroup reference data
- Agents extract counts from historical sources
- Database provides specifications for enrichment
- Result: Both historical accuracy (counts) AND detailed specs (combat modeling)

### Three-Source Integration

**Source 1: WITW Baseline** (469 equipment items)
- **Purpose**: Canonical equipment IDs for wargaming scenario exports
- **File**: `sources/WITW_EQUIPMENT_BASELINE.json`
- **Content**: Equipment names, nations, categories, WITW game IDs
- **Authority**: Source of truth for scenario WITW CSV exports
- **Quality**: 100% (canonical game data)

**Source 2: OnWar** (213 AFVs)
- **Purpose**: Production data and basic specifications
- **Files**: `sources/afv_data_onwar_*.json` (by nation)
- **Content**: Production quantities, weights, crew sizes, dimensions
- **Quality**: 85-90% confidence (curated military reference site)
- **Use Case**: Production context for MDBook chapters

**Source 3: WWIITANKS** (612 AFVs + 343 guns)
- **Purpose**: Detailed combat specifications
- **Files**: `sources/wwiitanks_*.json`
- **Content**:
  - Armor values (front, side, rear, turret - all angles)
  - Gun penetration tables (1,296 penetration data points)
  - Ammunition types (162 types with characteristics)
  - Performance data (speed, range, operational radius)
- **Quality**: 90-95% confidence (specialist tank/gun database)
- **Use Case**: Technical specs for MDBook chapters, penetration modeling

**Source 4: BattleGroup Reference Data** (Phase 9B addition)
- **Purpose**: Game-specific stat conversion for BattleGroup format
- **Tables**:
  - `bg_reference_vehicles` - 500 vehicles from official PDFs (armor, movement, weapons, points, BR)
  - `bg_reference_guns` - 57 guns (HE/AP values, penetration scale, range bands)
  - `equipment_battlegroup` - 469 North Africa items enriched with BattleGroup stats
- **Use Case**: Equipment datacards, points/BR calculation, conversion formulas

### Database Schema (master_database.db)

**18 tables in SQLite database** (expanded from Phase 5's 11 tables):

**Core Equipment Tables**:
- `equipment` - WITW baseline (469 items) with match links to OnWar/WWIITANKS
- `guns` - 343 guns with full specifications (caliber, penetration, ammunition)
- `ammunition` - 162 ammunition types with characteristics
- `penetration_data` - 1,296 penetration values (gun vs armor at various distances)

**BattleGroup Tables** (Phase 9B additions):
- `equipment_battlegroup` - 469 items with BattleGroup stats (armor, movement, points, BR)
- `bg_reference_vehicles` - 500 reference vehicles from official PDFs
- `bg_reference_guns` - 57 reference guns with HE/AP values
- `bg_armor_conversion` - 16 armor thickness ranges (A-O letter scale)
- `bg_penetration_scale` - 24 gun/caliber penetration mappings
- `bg_movement_values` - 20 vehicle type/weight movement ranges
- `bg_he_effectiveness` - 9 caliber HE effectiveness ranges
- `bg_special_rules` - 57 special rules (1,599 equipment linkages)

**Unit Assignment Tables**:
- `units` - 144 WITW units (divisions, corps, armies)
- `unit_equipment` - Equipment assignments (which units have which equipment)

**Metadata & Provenance Tables**:
- `match_reviews` - Equipment matching decisions with confidence scores
- `import_log` - Data provenance tracking (when imported, by whom, from what source)
- `normalization_audit` - Database linkage audit trail (Tier 1-4 matches)

**Source Data Tables**:
- `afv_data` - OnWar AFV data (213 vehicles)
- `wwiitanks_afv_data` - WWIITANKS AFV data (612 vehicles)
- `wwiitanks_gun_data` - WWIITANKS gun data (343 guns)

### Equipment Linkage Status

**Phase 5 Equipment Matching** (COMPLETE):
- French: 20/20 items → **COMPLETE** (100%)
- American: 81/81 items → **COMPLETE** (100%)
- German: 98/98 items → **COMPLETE** (96%)
- British: 196/196 items → **COMPLETE** (99%)
- Italian: 74/74 items → **COMPLETE** (97%)
- **Total**: 469/469 items matched to OnWar/WWIITANKS (99% success)

**Phase 9B Database Linkage** (IN PROGRESS):
- **Current**: 96/469 items linked to BattleGroup reference data (20.5%)
- **Target**: 469/469 items (100% required for publication)
- **Vehicles**: 80 items linked via `reference_vehicle_id`
- **Guns**: 16 items linked via `reference_gun_id`
- **Confidence Distribution**:
  - Tier 1 (100): 19 items - Exact matches
  - Tier 2 (85-90): 20 items - Normalized matches
  - Tier 3 (80): 41 items - Base model matches
  - Tier 4 (85-90): 16 items - Artillery matches

**Linkage Scripts** (Created Nov 3, 2025):
- `scripts/linkage/tier2_normalization.py` - Name variation matching
- `scripts/linkage/tier3_base_model.py` - Variant stripping logic
- `scripts/linkage/tier4_artillery_linkage.py` - Artillery cross-reference
- `scripts/linkage/tier3_5_stuart_linkage.sql` - Stuart tank variants (10 items)
- `scripts/linkage/tier3_6_common_tanks_linkage.sql` - Common tanks (37 items)
- `scripts/linkage/execute_all_tiers.sql` - Comprehensive 4-tier linkage

---

## 📚 Common Commands

| Command | Purpose |
|---------|---------|
| `npm run session:start` | Start new work session |
| `npm run checkpoint` | Validate + commit progress |
| `npm run session:end` | End session with summary |
| `npm run queue:generate` | Regenerate work queue |
| `npm run qa:v3` | Full QA validation pipeline |
| `npm run validate:v3` | Schema v3.1.0 compliance check |

**Phase 9B Specific Commands**:
```bash
# Generate equipment datacards for all 4 books
python scripts/battlegroup/book/generate_book_datacards.py --all

# Generate datacards for specific battle
python scripts/battlegroup/book/generate_book_datacards.py --battle battleaxe

# Validate scenarios
python scripts/battlegroup/book/validate_all_scenarios.py

# QA final books
python scripts/battlegroup/book/qa_final_books.py

# Build MDBook HTML
cd books/battleaxe/book && mdbook build
cd books/crusader/book && mdbook build
cd books/gazala/book && mdbook build
cd books/first_alamein/book && mdbook build
```

**See START_HERE_NEW_SESSION.md for complete command reference.**

---

## 🔗 Quick Reference Links

| Need | Location |
|------|----------|
| Project scope & phases | `PROJECT_SCOPE.md` |
| Phase 9B next steps | `PHASE_9B_NEXT_STEPS.md` |
| Phase 9B session summary | `PHASE_9B_SESSION_SUMMARY.md` |
| Session management | `START_HERE_NEW_SESSION.md` |
| Schema v3.1.0 spec | `schemas/unified_toe_schema.json` |
| Technical history | `VERSION_HISTORY.md` |
| Agent definitions | `agents/agent_catalog.json` |
| BattleGroup reference | `Resource Documents/Battlegroup Game/` |

---

**Current Priority**: Complete equipment linkage to 100% for publication-ready quality

**Ready to work?** Read `PHASE_9B_NEXT_STEPS.md` for detailed remaining tasks

**For reference**: Official BattleGroup-Kursk.pdf in `Resource Documents/Battlegroup Game/` (use parser agent to read)
