# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ CRITICAL - READ FIRST

**📋 COMPLETE PROJECT SCOPE**: See **`PROJECT_SCOPE.md`** in root directory

This is the **LIVING DOCUMENT** defining:
- ✅ Complete project vision (313-348 total units: ground + air forces)
- ✅ Phased approach (Ground → Air → Integration → Scenarios → Campaign)
- ✅ Current status and priorities (Phase 1-6: Ground Forces, 8.5% complete)
- ✅ Success criteria with supply/logistics/weather requirements
- ✅ Schema specifications for ground and air forces
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
- **Phased approach** - Complete ground forces (Phase 1-6) BEFORE starting air extraction (Phase 7)
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
15 specialized AI agents organized in 6 categories:
1. **Source & Extraction**: document_parser, historical_research
2. **Structure & Organization**: org_hierarchy, toe_template, unit_instantiation
3. **Equipment Distribution**: theater_allocator, division_cascader, equipment_reconciliation
4. **Aggregation & Calculation**: bottom_up_aggregator, top3_calculator
5. **Validation**: schema_validator, historical_accuracy
6. **Output Generation**: book_chapter_generator, scenario_exporter, sql_populator

### Orchestration Modes
Two operational modes:

**1. API-based (`src/orchestrator.js`)**
- Direct Claude API integration
- Runs all agents automatically in sequence
- 6-phase workflow: Source Extraction → Organization Building → Equipment Distribution → Aggregation → Validation → Output Generation
- Requires ANTHROPIC_API_KEY in .env

**2. File-based (`src/file_orchestrator.js`)**
- No API calls required
- Each agent runs in separate Claude Code terminal session
- Task coordination via file system (`tasks/pending/`, `tasks/in_progress/`, `tasks/completed/`)
- Enables true multi-agent independence with human review between phases

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
- `agents/agent_catalog.json` - All 15 agent definitions with prompts and validation rules
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

**Quarter Format:**
- Lowercase, no hyphen: `1941q2` (NOT 1941-Q2, NOT 1941-q2, NOT 1941Q2)

**Implementation:**
All scripts MUST use `scripts/lib/naming_standard.js` to generate filenames for consistency.

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
- ✅ All 15 agents defined with enhanced prompts
- ✅ Unified schema complete
- ✅ File-based orchestration working
- ✅ Source waterfall system implemented
- ⏸️ API-based orchestration in progress
- ⏸️ Web source integration pending

### Active Development Areas
- Processing North Africa campaign units (German, Italian, British 1940-1943)
- Automated source document extraction workflows
- Agent task management and coordination
