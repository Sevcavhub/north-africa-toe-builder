# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ CRITICAL - READ FIRST

**📋 COMPLETE PROJECT SCOPE**: See **`PROJECT_SCOPE.md`** in root directory

This is the **LIVING DOCUMENT** defining:
- ✅ Complete project vision (313-348 total units: ground + air forces)
- ✅ Phased approach (Database → Equipment Matching → Ground Forces → Air → Scenarios → Campaign)
- ✅ Current status and priorities:
  - Phase 1-4: Database Infrastructure (COMPLETE ✅)
  - Phase 5: Equipment Matching (IN PROGRESS - 4.3%, 20/469 items)
  - Phase 6: Ground Forces Unit Extraction (IN PROGRESS - 28.1%, 118/420 unit-quarters)
- ✅ Success criteria with supply/logistics/weather requirements
- ✅ Schema specifications for ground and air forces
- ✅ Equipment database integration (WITW/OnWar/WWIITANKS)
- ✅ Scenario generation as primary purpose
- ✅ Kickstarter commercial product viability

**🚨 ALL AGENTS AND SESSIONS MUST REFERENCE THIS DOCUMENT 🚨**

**Quick Status Check**:
```bash
# See current scope and phase
cat PROJECT_SCOPE.md | head -50

# Check version and last update
grep -E "Version|Last Updated|Status" PROJECT_SCOPE.md
```

**Why This Matters**:
- **Not just 213 units** - Total scope is 313-348 units (ground + air forces)
- **Phased approach** - Complete Phase 1-6 (Ground Forces) BEFORE starting Phase 7 (Air Forces)
  - Phase 1-4: Database Infrastructure (COMPLETE ✅)
  - Phase 5: Equipment Matching (IN PROGRESS - 4.3%)
  - Phase 6: Ground Forces Unit Extraction (IN PROGRESS - 28.1%)
- **Equipment database integration** - WITW/OnWar/WWIITANKS merge provides specifications (Phase 5)
- **Supply/logistics REQUIRED** - Every unit needs fuel reserves, ammo stocks, operational radius
- **Weather/environment REQUIRED** - Seasonal impacts, terrain effects for scenario generation
- **Scenario-ready output** - Primary purpose is wargame scenario generation, not just static TO&E

**If PROJECT_SCOPE.md conflicts with other documentation, PROJECT_SCOPE.md is authoritative.**

---

## 📖 Version Control & Documentation Standards

**Two Companion Documents Track Project Evolution**:

### PROJECT_SCOPE.md (Strategic)
- **Purpose**: WHAT we're building and WHY (vision, phases, success criteria)
- **Audience**: All team members, stakeholders, future sessions
- **Updates**: When scope, phases, or requirements change
- **Versioning**: Semantic (v1.0.0 → v1.1.0 → v2.0.0)

### VERSION_HISTORY.md (Technical)
- **Purpose**: HOW we built it and WHEN (schema evolution, implementation decisions)
- **Audience**: Developers, agents, technical implementation
- **Updates**: When schema, templates, agents, or architecture change
- **Versioning**: Component-based (Schema v3.0, Template v3.0, Agents v2.0.0)

**Version Control Rules**:

1. **When making schema changes**:
   - Update `schemas/unified_toe_schema.json` with new version
   - Add entry to VERSION_HISTORY.md with technical details
   - Update PROJECT_SCOPE.md if scope implications exist
   - Run validation: `npm run validate:v3`

2. **When modifying MDBook template**:
   - Update `docs/MDBOOK_CHAPTER_TEMPLATE.md` with new version
   - Add entry to VERSION_HISTORY.md documenting section changes
   - Update `scripts/generate_mdbook_chapters.js` if needed

3. **When updating agent catalog**:
   - Update `agents/agent_catalog.json` with new version
   - Document in VERSION_HISTORY.md with rationale
   - Test agents with sample units

4. **Git commit message format**:
   ```
   feat: Schema v3.0 - Add supply/logistics fields

   - Added Section 6 (5 fields): fuel_reserves, ammo_days, etc.
   - Updated validator agent to enforce new requirements
   - Regenerated 18 showcase units

   See VERSION_HISTORY.md for complete technical details.
   ```

5. **Semi-automated workflow**:
   - Machines detect: Schema changes, template modifications, agent updates
   - Humans document: WHY changes were made, architectural decisions, context
   - Cross-reference: Both documents link to each other for complete picture

**Quick Reference**:
- Read VERSION_HISTORY.md to understand technical evolution
- Read PROJECT_SCOPE.md to understand strategic direction
- Both documents are LIVING and must stay synchronized

---

## Project Overview

Multi-agent orchestration system for building detailed Table of Organization & Equipment (TO&E) data from historical military sources. Creates hierarchical military organization data from Theater level down to individual Squad level with full Strategic Command Summary (SCM) detail at every tier.

## 🚀 OCTOBER 2025: Fully Autonomous Mode (RECOMMENDED)

**Leverages Sonnet 4.5's complete capabilities - Task tool, extended thinking, parallel processing, MCP integrations!**

```bash
npm run start:autonomous
```

This displays instructions for Claude Code to:
- ✅ **Launch specialized sub-agents** using Task tool for document parsing, validation, etc.
- ✅ **Use extended thinking** for complex multi-source document analysis
- ✅ **Process units in parallel** (batches of 3-5 simultaneously)
- ✅ **Read source documents directly** using MCP file access
- ✅ **Write outputs autonomously** - no manual saving
- ✅ **Track progress live** with TodoWrite
- ✅ **Run in background** while you continue working
- ✅ **Uses your Max subscription** - zero API tokens!

**You run ONE command, paste one message to Claude, and watch it work autonomously!**

---

## Alternative: Semi-Manual Mode (Legacy)

If you want more control:

```bash
# Generate prompts for manual processing
npm run start:claude

# Or process interactively one-by-one
npm run start:claude:interactive
```

This creates prompt files that you paste into Claude Code session manually. Less automated but gives you control over each step.

## Other Commands

### Development Commands
```bash
# Run main orchestrator (⚠️ Uses API tokens)
npm start

# Run file-based orchestrator (⚠️ Requires manual JSON entry)
npm run start:file

# Run intelligent orchestrator with project config (⚠️ Uses API tokens)
npm run orchestrate
npm run orchestrate:resume          # Resume existing project

# Run single agent (⚠️ Requires manual JSON entry)
npm run agent                        # Interactive agent runner

# Search source documents
npm run search                       # Search for units in source docs

# Prepare source for agent processing
npm run prepare                      # Prepare source extraction task

# Testing
npm test                            # Run test suite
npm run validate                    # Validate schema compliance
```

### Agent Runner Commands
The agent runner (`src/agent_runner.js`) runs individual agents in separate terminal/VS Code windows:
```bash
node src/agent_runner.js document_parser
node src/agent_runner.js historical_research
node src/agent_runner.js org_hierarchy
# ... (15 total agents)
```

## How Single-Session Mode Works (Recommended)

The **Single-Session Orchestrator** (`src/single_session_orchestrator.js`) is designed to work entirely within Claude Code using your Max subscription:

### Workflow:

1. **Run the orchestrator** to generate all prompts:
   ```bash
   npm run start:claude
   ```

2. **Orchestrator automatically**:
   - Loads your project configuration
   - Searches for source documents using 3-tier waterfall
   - Extracts relevant content for each unit
   - Generates agent prompts with source material included
   - Saves all prompts to `data/output/session_XXXXX/prompts/`
   - Creates a processing guide with step-by-step instructions

3. **You process prompts**:
   - Open `data/output/session_XXXXX/PROCESSING_GUIDE.md`
   - For each prompt:
     - Copy the prompt file content
     - Paste it into this Claude Code chat
     - Claude (AI) automatically processes it and returns JSON
     - Save Claude's JSON response to the specified response file
     - Move to next prompt

4. **No API calls, no manual extraction** - Claude Code AI does all the work using your subscription!

### Example:
```bash
# Generate all Phase 1 prompts
npm run start:claude

# Open the processing guide
# Follow step-by-step to process each unit
# All work happens in this Claude Code session
```

## Architecture Overview

### Multi-Agent System
16 specialized AI agents organized in 6 categories:
1. **Source & Extraction**: document_parser, historical_research
2. **Structure & Organization**: org_hierarchy, toe_template, unit_instantiation
3. **Equipment Distribution**: theater_allocator, division_cascader, equipment_reconciliation
4. **Aggregation & Calculation**: bottom_up_aggregator, top3_calculator
5. **Validation**: schema_validator, historical_accuracy, seed_reconciliation_validator
6. **Output Generation**: book_chapter_generator, scenario_exporter, sql_populator

### Orchestration Modes
Two operational modes:

**1. API-based (`src/orchestrator.js`)**
- Direct Claude API integration
- Runs all agents automatically in sequence
- 7-phase workflow: Source Extraction → Organization Building → Equipment Distribution → Aggregation → Validation → Seed Reconciliation → Output Generation
- Requires ANTHROPIC_API_KEY in .env

**2. File-based (`src/file_orchestrator.js`)**
- No API calls required
- Each agent runs in separate Claude Code terminal session
- Task coordination via file system (`tasks/pending/`, `tasks/in_progress/`, `tasks/completed/`)
- Enables true multi-agent independence with human review between phases

---

## 🗄️ Equipment Database Architecture (Phase 5)

**As of October 2025**, the project uses a **three-source equipment database** to provide comprehensive specifications beyond what historical documents contain.

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
- Agents extract counts from historical sources
- Database provides specifications for enrichment
- Result: Both historical accuracy (counts) AND detailed specs (combat modeling)

---

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
- **Use Case**: Technical specs for MDBook chapters, penetration modeling for database

---

### Database Schema (master_database.db)

**11 tables in SQLite database**:

**Core Equipment Tables**:
- `equipment` - WITW baseline (469 items) with match links to OnWar/WWIITANKS
- `guns` - 343 guns with full specifications (caliber, penetration, ammunition)
- `ammunition` - 162 ammunition types with characteristics
- `penetration_data` - 1,296 penetration values (gun vs armor at various distances)

**Unit Assignment Tables**:
- `units` - 144 WITW units (divisions, corps, armies)
- `unit_equipment` - Equipment assignments (which units have which equipment)

**Metadata & Provenance Tables**:
- `match_reviews` - Equipment matching decisions with confidence scores
- `import_log` - Data provenance tracking (when imported, by whom, from what source)

**Source Data Tables**:
- `afv_data` - OnWar AFV data (213 vehicles)
- `wwiitanks_afv_data` - WWIITANKS AFV data (612 vehicles)
- `wwiitanks_gun_data` - WWIITANKS gun data (343 guns)

---

### Equipment Matching Workflow (Phase 5)

**Interactive CLI Matching Process**:

```
WITW Baseline (469 items by nation)
  ↓
Equipment Matcher (tools/equipment_matcher_v2.py)
  ├─ Type Detection (GUN vs AFV vs SOFT_SKIN vs AIRCRAFT)
  ├─ Name Normalization (handles "H-39" vs "H39" vs "H 39")
  ├─ Cross-Nation Matching (all 343 guns, 825 AFVs loaded for captured/lend-lease)
  ├─ Match Confidence Scoring (100% = exact, 85% = partial, 70% = word match)
  └─ Research Agent (if no match found - automated web search)
  ↓
Database (match_reviews table)
  ├─ Approved matches (linked to OnWar/WWIITANKS)
  ├─ Rejected matches (no suitable match found)
  └─ Researched items (comprehensive findings from web search)
```

**Matching Progress** (as of October 18, 2025):
- [x] French: 20/20 items → **COMPLETE** (100%)
- [ ] American: 81 items → Next
- [ ] German: 98 items → Pending
- [ ] British: 196 items → Pending (largest)
- [ ] Italian: 74 items → Pending

**Total**: 20/469 items matched (4.3% complete)

---

### Unit Enrichment Workflow (Phase 6 Integration)

**How Equipment Data Flows**:

```
Step 1: Historical Source Extraction (Agents)
  Tessin Vol 12: "60x Panzer III Ausf F, 20x Panzer IV Ausf D"
  ↓
  document_parser → historical_research → unit_instantiation
  ↓
  Unit JSON (COUNTS ONLY):
  {
    "tanks": {
      "Panzer III Ausf F": 60,
      "Panzer IV Ausf D": 20
    }
  }

Step 2: Database Enrichment (Post-Processing)
  scripts/enrich_units_with_database.js
  ↓
  Query database for each variant
  ↓
  Enriched Unit JSON (COUNTS + SPECS):
  {
    "tanks": {
      "Panzer III Ausf F": {
        "count": 60,                        // from Tessin
        "witw_id": "GER_PANZER_III_AUSF_F", // from WITW baseline
        "armament": "50mm KwK 38 L/42",     // from WWIITANKS
        "armor_mm": {
          "front": 50,
          "side": 30,
          "rear": 21
        },                                   // from WWIITANKS
        "crew": 5,                           // from OnWar
        "production": "435 units (1940-1941)" // from OnWar
      }
    }
  }

Step 3: Output Generation
  ├─ MDBook Chapters (uses enriched units for variant specs)
  ├─ WITW Scenarios (uses witw_id for game export)
  └─ SQL Database (complete data for custom queries)
```

---

### Detail Level Standards (Critical for Output)

**MDBook Chapters** (Human Readers):
- ✅ Equipment counts (from historical sources)
- ✅ Variant names (specific model designations)
- ✅ Key specifications (main gun, armor, crew)
- ✅ Production context (dates, quantities)
- ✅ Tactical analysis (how equipment was used in combat)
- ❌ NO full penetration tables (1,296 values - overwhelming for readers)
- ❌ NO WITW equipment IDs (game-specific identifiers)

**WITW Scenarios** (Wargamers):
- ✅ WITW equipment IDs (canonical identifiers for game import)
- ✅ Equipment counts (historical)
- ✅ Operational readiness (ready vs damaged percentages)
- ✅ All vehicles including soft-skin (trucks, halftracks - critical for logistics)
- ✅ **Battle context** (historical situation, date, location)
- ✅ **Victory conditions** (narrative description of objectives for each side)
- ✅ **Weather/terrain conditions** (operational context affecting gameplay)
- ✅ **Supply states** (fuel days, ammo days, water reserves at scenario start)
- ✅ **Strategic objectives** (what each side is trying to achieve - concise narrative)
- ❌ NO detailed equipment production history essays (overwhelming for players)
- ❌ NO long-form tactical analysis (keep concise for quick player reference)

**SQL Database** (Developers/Analysts):
- ✅ EVERYTHING - all data from all sources
- ✅ All 1,296 penetration data points
- ✅ All 162 ammunition types with characteristics
- ✅ Complete provenance (sources, confidence levels, import timestamps)
- ✅ Cross-nation equipment transfers (captured equipment, lend-lease)

**Rationale**:
- **Books** = Understanding historical formations (narrative focus)
- **Scenarios** = Playing the game with historical accuracy (gameplay + battle context)
- **Database** = Source of truth for everything (complete data for custom queries)

---

### Scripts & Tools for Equipment Database

**Import Scripts** (Phase 1-4 - COMPLETE):
- `scripts/import_witw_baseline.js` - Import WITW baseline (469 items)
- `scripts/import_guns.js` - Import WWIITANKS guns (343 guns + ammunition + penetration)
- `scripts/import_units.js` - Import WITW units (144 units)

**Matching Tools** (Phase 5 - IN PROGRESS):
- `tools/equipment_matcher_v2.py` - Interactive equipment matching (v2.1)
- `tools/apply_research_findings.py` - Apply research results to database
- `tools/show_french_results.py` - Query French equipment matching results

**Enrichment Tools** (Phase 6 - TO BE CREATED):

**🚨 CRITICAL - THESE SCRIPTS MUST BE CREATED BEFORE PHASE 6 CAN USE DATABASE SPECS**:

1. **`scripts/enrich_units_with_database.js`** (REQUIRED)
   - Add database specifications to unit JSON files
   - Input: Unit JSON with counts (from agents)
   - Output: Enriched unit JSON with counts + specs (armor, gun, crew, production)
   - Status: TO BE CREATED after equipment matching complete (469 items)
   - Blocks: MDBook chapter generation with variant specifications

2. **`scripts/generate_scenario_exports.js`** (REQUIRED)
   - Export WITW-format CSV with equipment IDs and battle narratives
   - Input: Enriched unit JSON files
   - Output: WITW scenario CSV (equipment IDs, counts, battle context, victory conditions, supply states)
   - Status: TO BE CREATED after equipment matching complete
   - Blocks: Phase 9 scenario generation

**Without these scripts**:
- Phase 6 unit JSONs will only have counts, no detailed specifications
- MDBook chapters will miss variant specs (armor values, gun penetration, performance)
- Phase 9 scenarios cannot export with WITW equipment IDs
- Battle narratives, victory conditions, supply states won't be included in scenarios

---

### Working with Equipment Database

**Query Equipment Specifications**:
```python
import sqlite3
conn = sqlite3.connect('database/master_database.db')
cursor = conn.cursor()

# Get gun specifications with penetration data
cursor.execute("""
    SELECT e.canonical_id, e.name, g.caliber, g.penetration_100m, g.penetration_500m
    FROM equipment e
    JOIN guns g ON e.wwiitanks_gun_id = g.gun_id
    WHERE e.nation = 'german' AND e.category = 'field_artillery'
""")

# Get AFV armor values
cursor.execute("""
    SELECT e.canonical_id, e.name, a.armor_front_mm, a.armor_side_mm
    FROM equipment e
    JOIN wwiitanks_afv_data a ON e.wwiitanks_afv_id = a.afv_id
    WHERE e.nation = 'german' AND e.category = 'medium_tank'
""")
```

**Run Equipment Matcher**:
```bash
# Match equipment for a nation
python tools/equipment_matcher_v2.py --nation american

# View matching results
python tools/show_french_results.py
```

**Enrich Unit JSON** (future):
```bash
# Add database specs to unit JSON
node scripts/enrich_units_with_database.js \
  --unit germany_1941q2_15_panzer_division_toe.json
```

---

### Data Hierarchy
```
Theater (Summary totals only)
  ↓
Corps (Full SCM detail)
  ↓
Division (Full SCM detail)
  ↓
Regiment (Full SCM detail)
  ↓
Battalion (Full SCM detail)
  ↓
Company (Full SCM detail)
  ↓
Platoon (Full SCM detail)
  ↓
Squad (Full SCM detail + individual soldier positions)
```

### Core Design Principles
1. **Every organizational level has complete SCM-level equipment detail** - no summary-only levels
2. **Bottom-up aggregation**: Squad totals → Platoon → Company → ... → Theater
3. **Validation at every level**: Parent unit total must equal sum of all children (±5%)
4. **Individual positions**: Squad level defines every soldier with specific weapon/equipment
5. **Multi-format output**: MDBook chapters, wargaming scenarios, SQL database

## Key Files

### Core Implementation
- `src/orchestrator.js` - Main API-based orchestration engine with 6-phase workflow
- `src/file_orchestrator.js` - File-based orchestration for multi-terminal agent coordination
- `src/agent_runner.js` - Individual agent runner for file-based mode
- `src/source_waterfall.js` - 3-tier source selection system (local docs → curated web → general search)
- `src/source_scanner.js` - Source document discovery and cataloging

### Configuration & Definitions
- `agents/agent_catalog.json` - All 16 agent definitions with prompts and validation rules
- `schemas/unified_toe_schema.json` - Complete data structure for all organizational levels
- `sources/sources_catalog.json` - Source document catalog with confidence levels
- `projects/north_africa_campaign.json` - Project configuration with units to build

### Project Documentation
- **`PROJECT_SCOPE.md`** - **Complete project vision and phased approach (LIVING DOCUMENT - READ FIRST)**
- `docs/project_context.md` - Technical architecture and design decisions
- `docs/SOURCE_WORKFLOW.md` - How to work with local documents (Tessin, Army Lists, Field Manuals)
- `docs/AUTOMATED_WORKFLOW.md` - Agent automation workflow with examples
- `SESSION_SUMMARY.md` - Current session status and progress

## Working with Agents

### Agent Communication Protocol
All agents use standardized JSON request/response format:
```json
{
  "agent_request": {
    "agent_id": "string",
    "task_id": "uuid",
    "inputs": {},
    "context": {"nation": "italian", "quarter": "1940-Q2"}
  },
  "agent_response": {
    "status": "success|error|partial",
    "outputs": {},
    "metadata": {"confidence": 85, "execution_time_ms": 1234}
  }
}
```

### Agent Prompt Templates
Agent prompts in `agents/agent_catalog.json` use variable substitution:
- Variables: `{nation}`, `{quarter}`, `{unit_designation}`, etc.
- Orchestrator maps input keys to template variables (see `orchestrator.js:516-556`)
- Enhanced prompts provide examples and enforce JSON output format

### File-Based Agent Workflow
1. Create task file in `tasks/pending/`
2. Agent watches for new tasks via `agent_runner.js`
3. Agent processes task and outputs to `outputs/task_xxx_output.json`
4. Move task file to `tasks/completed/` when done

## Source Documents

### Local Primary Sources (95% Confidence)
- **German units**: Tessin Wehrmacht Encyclopedia (17 volumes) in `Resource Documents/tessin-georg-verbande.../`
- **British/Commonwealth units**: British Army Lists (quarterly 1941-1943) in `Resource Documents/Great Britain Ministery of Defense Books/`
- **US units**: US Field Manuals in `Resource Documents/`

### 3-Tier Source Waterfall
Implemented in `src/source_waterfall.js`:
1. **Tier 1** (90% confidence): Local primary documents (Tessin, Army Lists, Field Manuals)
2. **Tier 2** (75% confidence): Curated web sources (Feldgrau, Niehorster, etc.)
3. **Tier 3** (60% confidence): General web search (NO Wikipedia)

System automatically escalates to next tier if data missing or confidence < threshold.

## Data Validation

### Critical Validation Rules
Enforced by `schema_validator` agent:
1. `tanks.total = sum(heavy + medium + light)`
2. `total_personnel ≈ officers + ncos + enlisted (±5%)`
3. `ground_vehicles_total ≥ sum(all vehicle categories)`
4. `artillery_total ≥ sum(field + anti_tank + anti_aircraft)`
5. Parent unit total = sum of all child units (±5%)

### Confidence Scoring
- Required minimum: 75% confidence for all data
- Minimum 2 sources per critical fact (commanders, unit designations)
- Historical accuracy verified by cross-referencing multiple sources
- Conflicts explicitly flagged with resolution reasoning

## Output Formats

### Generated Outputs (in `data/output/`)
1. **Unit JSON files** (`units/`) - Complete TO&E for each organizational level
2. **MDBook chapters** (`chapters/`) - Professional military history narrative with tables
3. **Wargaming scenarios** (`scenarios/`) - WITW CSV format with equipment mappings
4. **SQL database** (`sql/`) - INSERT statements for complete relational database

### Naming Convention
Files follow pattern: `{nation}_{quarter}_{unit_designation}_toe.json`
- Example: `german_1941q2_15th_panzer_division_toe.json`

**CANONICAL NATION VALUES (CRITICAL - USE EXACTLY):**
- `german` (NOT germany) - All German Wehrmacht units
- `italian` (NOT italy) - All Italian Regio Esercito units
- `british` (NOT britain) - All British & Commonwealth units (includes Australia, New Zealand, India, South Africa, Canada, Colonial Forces)
- `american` (NOT usa) - All United States Army units
- `french` (NOT france) - All Free French forces

**Quarter Format (CRITICAL - STANDARDIZED OCTOBER 2025):**
- **Filename**: Lowercase, no hyphen: `1941q2` (NOT 1941-Q2, NOT 1941-q2, NOT 1941Q2)
- **JSON Content**: Lowercase, no hyphen: `"quarter": "1941q2"` (NOT "1941-Q2")
- **Rationale**: Matches orchestrator output standard, canonical_paths.js normalization
- **Schema**: `schemas/unified_toe_schema.json` specifies format as `yyyyqn` (lowercase, no hyphen)

**Implementation:**
All scripts MUST use `scripts/lib/naming_standard.js` to generate filenames for consistency.

---

## 📁 Output Directory Architecture (Architecture v4.0)

**CRITICAL**: As of Architecture v4.0 (October 14, 2025), the project uses **canonical output locations** to prevent duplicate files and ensure single source of truth for all phases.

### Canonical Output Structure

```
data/output/
├── units/              ⭐ CANONICAL - All ground unit TO&E files (Phase 1-6)
├── chapters/           ⭐ CANONICAL - All MDBook chapters (Phase 1-6)
├── air_units/          ⭐ CANONICAL - Air force units (Phase 7+, future)
├── air_chapters/       ⭐ CANONICAL - Air force chapters (Phase 7+, future)
├── scenarios/          ⭐ CANONICAL - Battle scenarios (Phase 9+, future)
├── campaign/           ⭐ CANONICAL - Campaign data (Phase 10+, future)
└── sessions/           📦 ARCHIVE - Historical session work (read-only)
```

### ⚠️ CRITICAL RULES

**DO**:
- ✅ ALWAYS use `scripts/lib/canonical_paths.js` for path operations
- ✅ Write unit JSON files to `data/output/units/` ONLY
- ✅ Write MDBook chapters to `data/output/chapters/` ONLY
- ✅ Scan canonical directories for completed units
- ✅ Use `paths.getUnitPath(nation, quarter, unit)` helper functions

**DON'T**:
- ❌ NEVER create new `autonomous_*` or `session_*` directories in `data/output/`
- ❌ NEVER write unit files to session directories
- ❌ NEVER recursively scan `data/output/` for units
- ❌ NEVER hardcode output paths (use canonical_paths.js)

### Using Canonical Paths in Scripts

```javascript
const paths = require('./scripts/lib/canonical_paths');

// ✅ CORRECT: Use canonical paths
const unitPath = paths.getUnitPath('german', '1941q2', '15_panzer_division');
// Returns: data/output/units/german_1941q2_15_panzer_division_toe.json

const chapterPath = paths.getChapterPath('german', '1941q2', '15_panzer_division');
// Returns: data/output/chapters/chapter_german_1941q2_15_panzer_division.md

// ✅ CORRECT: Ensure directories exist
await paths.ensureCanonicalDirectoriesExist();

// ✅ CORRECT: Check if path is canonical
const isCanonical = paths.isCanonicalPath(somePath);
```

```javascript
// ❌ WRONG: Hardcoded paths
const unitPath = 'data/output/autonomous_1760133539236/units/german_1941q2_15_panzer_division_toe.json';

// ❌ WRONG: Creating session directories for unit files
const sessionDir = `data/output/autonomous_${Date.now()}`;
fs.mkdirSync(sessionDir + '/units');
```

### Session Archive System

**Historical session directories** are archived to `data/output/sessions/`:
- Contains old `autonomous_*` and `session_*` directories
- Preserves audit trail and research notes
- **READ-ONLY** - never use for production work
- See `data/output/sessions/README.md` for archive details

**Valid uses of archived sessions**:
- Reviewing historical extraction process
- Checking session-specific reports
- Understanding how a unit was researched
- Audit trail / quality verification

**Invalid uses**:
- ❌ Reading unit TO&E data (use canonical location!)
- ❌ Generating MDBook chapters from archived units
- ❌ Cross-referencing between units (use canonical!)

### Migration Scripts

**One-time migration** (if needed):
```bash
# Consolidate scattered files to canonical locations
npm run consolidate

# Archive old session directories
npm run archive:sessions

# Verify structure
npm run checkpoint
```

These scripts should only be run once during Architecture v4.0 migration.

### Why Canonical Locations?

**Problem**: Before v4.0, each autonomous session created its own timestamped directory. Same unit existed in 5-7 locations, causing:
- Duplicate counting (207 entries for 202 unique units)
- Unclear which file was authoritative
- Future phases (7-10) couldn't determine source of truth
- Re-extraction of already-completed units

**Solution**: Single canonical location for each output type, ensuring:
- Unique files (one version per unit)
- Clear authority (canonical location is source of truth)
- Phase 7-10 readiness (air forces, scenarios, campaign)
- No duplicate work (skip-completed logic)

See `VERSION_HISTORY.md` Architecture v4.0 entry for complete technical details.

---

## Task System

### Task Directory Structure
```
tasks/
├── pending/          # New tasks waiting to be processed
├── in_progress/      # Currently being worked on
├── completed/        # Successfully completed
└── failed/           # Failed with error details
```

### Task File Format
Tasks are JSON files with structure:
```json
{
  "task_id": "task_1760054410179_parse_Germany_15th_Panzer",
  "agent_id": "document_parser",
  "inputs": { ... },
  "dependencies": [],
  "created_at": "2025-10-10T...",
  "status": "pending"
}
```

## Environment Setup

### Required Environment Variables
Create `.env` file with:
```
ANTHROPIC_API_KEY=your_key_here    # Required for API-based orchestration only
```

### Dependencies
```bash
npm install                         # Installs node-fetch, dotenv
```

## Development Guidelines

### When Adding New Agents
1. Define agent in `agents/agent_catalog.json` with:
   - Unique `agent_id`
   - Category assignment
   - Input/output specification
   - Enhanced `prompt_template` with examples
   - Validation rules
2. Add agent case to `agent_runner.js` if needed
3. Update orchestrator workflow phase if applicable
4. Test agent independently before integration

### When Modifying Schema
1. Update `schemas/unified_toe_schema.json`
2. Update validation rules in schema file
3. Test with `npm run validate`
4. Update agent prompts that reference affected fields
5. Regenerate sample data to verify compatibility

### When Adding Source Documents
1. Place documents in `Resource Documents/` directory
2. Update `sources/sources_catalog.json` with metadata
3. Add nation/source mapping to `src/source_waterfall.js:191-207`
4. Test source extraction with `npm run search`

## Special Considerations

### British/Commonwealth Units
Per user's global CLAUDE.md instructions: "British" includes all Commonwealth nations (India, Australia, New Zealand, Canada, South Africa) and Colonial Forces. All British data extraction must include Commonwealth units.

### Data Quality Requirements
- No guessing or hallucination - if data unavailable, mark as "Unknown" with low confidence
- Calculate all totals from bottom-up aggregation when possible
- Use due diligence to verify equipment counts sum correctly at every level
- Preserve original language for unit designations (e.g., "XXI Corpo d'Armata" not "21st Corps")

### Time Period Accuracy
Commanders and equipment allocations change quarterly - always verify data matches specified quarter precisely.

## Project Status

Current implementation status:
- ✅ Architecture designed
- ✅ All 16 agents defined with enhanced prompts (including seed reconciliation validator)
- ✅ Unified schema complete
- ✅ File-based orchestration working
- ✅ Source waterfall system implemented
- ✅ 7-phase workflow with human-in-loop checkpoint
- ⏸️ API-based orchestration in progress
- ⏸️ Web source integration pending

### Active Development Areas
- Processing North Africa campaign units (German, Italian, British 1940-1943)
- Automated source document extraction workflows
- Agent task management and coordination
