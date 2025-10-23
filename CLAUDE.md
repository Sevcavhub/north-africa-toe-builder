# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## 🎯 Quick Orientation

**Project**: North Africa TO&E Builder (Table of Organization & Equipment)
**Current Phase**: Ground Forces Extraction (Phase 6 of 10)
**Progress**: 252/419 unit-quarters complete (60.1%)
**Schema**: v3.1.0 (tiered extraction, supply/logistics, weather/environment)
**Primary Purpose**: Generate wargaming scenarios with realistic historical data

**Key Documents** (read these for complete context):
- `PROJECT_SCOPE.md` - Complete project vision and phased approach (**LIVING DOCUMENT**)
- `START_HERE_NEW_SESSION.md` - Session workflow and management protocol
- `schemas/unified_toe_schema.json` - Data structure requirements
- `RESTORATION_PLAN.md` - Current restoration work (if mid-restoration)

---

## 📋 Current Work (Phase 6: Ground Forces)

**Scope**: 420 unit-quarters (117 unique units, 1940-1943, North Africa only)

**Progress by Phase**:
- Phase 1-4: Database Infrastructure ✅ COMPLETE
- Phase 5: Equipment Matching (20/469 items, 4.3%) ⏸️ Paused
- **Phase 6: Ground Forces** (252/419, 60.1%) ← **YOU ARE HERE**
- Phase 7-10: Air forces, scenarios, campaign (future)

**Work Queue**: Uses `WORK_QUEUE.md` generated from `north_africa_seed_units_COMPLETE.json`
- Sorted echelon-first globally (divisions before corps before armies)
- Then chronological within each echelon
- Enforces strict bottom-up aggregation

---

## 🔄 Session Workflow

**For complete session management, see:** `START_HERE_NEW_SESSION.md` → "Session Management Protocol"

**Quick commands**:
```bash
npm run session:start    # Load progress, show next 3 units
npm run checkpoint       # Validate + commit (auto after 3 units)
npm run session:end      # Save stats, create summary
```

**Work pattern**:
- 3-unit batches (processed in parallel via Task tool)
- Automatic checkpoint after each batch
- NO artificial session limits (user directive Oct 23, 2025)
- ~20-30 minutes per batch with orchestration

---

## ⚠️ Critical Rules (MUST FOLLOW)

### 1. Seed Authority
- **Only extract units in `north_africa_seed_units_COMPLETE.json`**
- Seed file is authoritative (117 units, 420 unit-quarters)
- discovered_units feature requires combat_evidence (NO garrison/reserve units)

### 2. Combat Participation Validation
- discovered_units MUST have documented North Africa combat participation
- MUST include: battle names, dates, operational roles
- MUST EXCLUDE: garrison units, reserves never committed, rear-area units, units stationed elsewhere

### 3. Task Tool Orchestration (MANDATORY)
- You are an **orchestrator**, not an extractor
- Launch 3 specialized sub-agents in parallel using Task tool
- Sub-agents do the extraction work using MCP tools
- Proof required: Show 3 Task tool calls in single message

### 4. Canonical Output Locations (Architecture v4.0)
**ALWAYS use these paths** (NOT session/autonomous folders):
- Units: `data/output/units/[nation]_[quarter]_[unit]_toe.json`
- Chapters: `data/output/chapters/chapter_[nation]_[quarter]_[unit].md`
- Use `scripts/lib/canonical_paths.js` for path operations

### 5. Nation Values (CANONICAL)
**Use exactly these values** (NOT "germany", "italy", "britain", "usa"):
- `german` - German Wehrmacht
- `italian` - Italian Regio Esercito
- `british` - British & Commonwealth (includes Australia, NZ, India, South Africa, Canada, Colonial)
- `american` - US Army
- `french` - Free French forces

### 6. Quarter Format
**Lowercase, no hyphen**: `1941q2` (NOT "1941-Q2", NOT "1941Q2")

### 7. Validation Requirements
**Unit is complete ONLY when ALL 3 pass**:
1. ✅ JSON file exists in canonical location
2. ✅ Chapter file exists in canonical location
3. ✅ Passes schema validation (no critical errors)

Checkpoint automatically validates - failed units not counted.

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

### Equipment Matching Progress

**As of October 23, 2025**:
- [x] French: 20/20 items → **COMPLETE** (100%)
- [ ] American: 81 items → Next
- [ ] German: 98 items → Pending
- [ ] British: 196 items → Pending (largest)
- [ ] Italian: 74 items → Pending

**Total**: 20/469 items matched (4.3% complete)

**Workflow**: Interactive CLI matching (`tools/equipment_matcher_v2.py`) with type detection, name normalization, cross-nation matching for captured/lend-lease equipment, confidence scoring, and automated research for unmatched items.

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

**See START_HERE_NEW_SESSION.md for complete command reference.**

---

## 🔗 Quick Reference Links

| Need | Location |
|------|----------|
| Project scope & phases | `PROJECT_SCOPE.md` |
| Session management | `START_HERE_NEW_SESSION.md` |
| Schema v3.1.0 spec | `schemas/unified_toe_schema.json` |
| Technical history | `VERSION_HISTORY.md` |
| Restoration work | `RESTORATION_PLAN.md` |
| Agent definitions | `agents/agent_catalog.json` |
| Work queue | `WORK_QUEUE.md` |
| Workflow state | `WORKFLOW_STATE.json` |

---

**Ready to start? Run:** `npm run session:start`

**For detailed workflow:** Read `START_HERE_NEW_SESSION.md`

**For restoration context:** Read `RESTORATION_PLAN.md` (if mid-restoration)
