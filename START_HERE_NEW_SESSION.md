# 🚀 NEW SESSION - START HERE

<!-- AUTO-UPDATED: START - Session Metadata -->
**Project**: North Africa TO&E Builder - **v3.0.0 (Ground Forces)**
**Last Updated**: 2025-10-23 06:45
**Status**: Schema v3.0 Complete, 252/419 units (60.1%)
<!-- AUTO-UPDATED: END - Session Metadata -->

---

## Quick Start Commands

### If You Want to Continue v3.0 Work:

```
"Review PROJECT_SCOPE.md and continue with v3.0 schema implementation"
```

### If You're Starting New Unit Extraction:

```
"Run autonomous orchestrator for [nation] [quarter] units"
```

### If You're Reviewing Showcase Quality:

```
"Read data/output/1941-q2-showcase/SHOWCASE_GAPS.md and prioritize fixes"
```

---

## Current Project State

### ✅ COMPLETED (v3.0 Schema):
- **Schema v3.0.0**: Supply/logistics + Weather/environment support
- **Agent Catalog v2.0.0**: All 7 agents updated with Anthropic patterns
- **MDBOOK Template v3.0**: 18-section template with new Supply & Environment sections
- **NPM Scripts**: Added `validate:v3`, `validate:sources`, `qa:v3`
- **Wikipedia Blocking**: 4-layer protection (parser → research → validator → publisher)

<!-- AUTO-UPDATED: START - Recently Completed -->
### ✅ RECENTLY COMPLETED (Last Session):
- **Session Date**: 2025-10-23
- **Units Completed**: 252 unit-quarters (0 → 252)
- **Session Duration**: 37 minutes
- **Completion Rate**: 60.1% of total project
- **Recent Work**:
  - italian_1942q4_101_divisione_motorizzata_trieste
  - italian_1942q4_102_divisione_motorizzata_trento
  - italian_1942q4_132_ariete_division
  - italian_1942q4_133a_divisione_corazzata_littorio
  - italian_1942q4_185a_divisione_paracadutisti_folgore
  - italian_1942q4_185_divisione_paracadutisti_folgore
  - italian_1942q4_xxi_corps
  - italian_1942q4_xx_mobile_corps
  - italian_1943q1_131_divisione_corazzata_centauro
<!-- AUTO-UPDATED: END - Recently Completed -->

<!-- AUTO-UPDATED: START - Progress Stats -->
### 🔨 IN PROGRESS:
- **Ground Forces Extraction**: 252/419 unit-quarters (60.1%)
  - 167 unit-quarters remaining to complete Phase 1-6
  - 117 unique units total
  - Target: All 117 combat units across all quarters (1940-1943)
<!-- AUTO-UPDATED: END - Progress Stats -->

### 📋 NEXT PRIORITIES:

1. **Gap 1** (HIGH): Extract British Corps units (XIII Corps, Western Desert Force)
2. **Gap 2** (HIGH): Extract Italian Corps units (XX Corpo d'Armata, XXI Corpo d'Armata)
3. **Gap 4** (MEDIUM): Apply Ariete narrative standard to all chapters
4. **Complete Showcase**: Upgrade remaining 8 divisions to v3.0.0 (50th Infantry, 9th Australian, 5. leichte, Pavia, Brescia, Trento, Savona, DAK)

---

## Key Files to Reference

### Project Documentation:
- `PROJECT_SCOPE.md` - Complete scope (313-348 units, 10 phases) - **READ FIRST**
- `VERSION_HISTORY.md` - Technical version history (schema evolution, implementation decisions) - **NEW**
- `docs/project_context.md` - Architecture and design decisions
- `CLAUDE.md` - Project instructions for Claude Code

### Schema & Templates:
- `schemas/unified_toe_schema.json` - **v3.0.0** (Ground Forces)
- `docs/MDBOOK_CHAPTER_TEMPLATE.md` - **v3.0** (18 sections)
- `agents/agent_catalog.json` - **v2.0.0** (Anthropic patterns)

### Showcase Analysis:
- `data/output/1941-q2-showcase/SHOWCASE_GAPS.md` - 9 gaps identified
- `data/output/1941-q2-showcase/README_FINAL.md` - Showcase summary

### Session Management:
- Run `npm run session:start` to create new work session
- Run `npm run session:end` to checkpoint progress
- Run `npm run checkpoint` for mid-session saves

---

## v3.0 Schema Changes (BREAKING)

### Section 6: Supply & Logistics (NEW)
**5 required fields** for scenario generation:
- `supply_status` (string - qualitative assessment)
- `operational_radius_km` (integer, 50-1000)
- `fuel_reserves_days` (number, 0-30)
- `ammunition_days` (number, 0-30)
- `water_liters_per_day` (number, 3-10)

### Section 7: Weather & Environment (NEW)
**5 required fields** for seasonal modeling:
- `season_quarter` (string, "YYYY-QN")
- `temperature_range_c` (object with min/max)
- `terrain_type` (string)
- `storm_frequency_days` (integer, 0-15)
- `daylight_hours` (number, 10-15)

### Wikipedia Blocking (ENFORCED)
- NO Wikipedia sources allowed in `validation.source` array
- 4-layer blocking: parser → research → validator → publisher
- All agents use Anthropic patterns (error prevention, stopping conditions)

---

## NPM Commands (v3.0)

### Validation:
```bash
npm run validate:v3         # Validate v3.0 schema compliance
npm run validate:sources    # Check for Wikipedia violations
npm run validate:full       # Run both validations
npm run qa:v3              # Full QA pipeline (validation + audit)
```

### Orchestration:
```bash
    # RECOMMENDED: Fully autonomous mode
npm run start:claude        # Generate prompts for manual processing
npm run orchestrate         # API-based orchestration (uses tokens)
```

### Session Management:
```bash
npm run session:start       # Start new work session
npm run session:end         # End session with checkpoint
npm run checkpoint          # Mid-session checkpoint
```

### Git Workflow:
```bash
npm run git:commit          # Auto-commit with standardized message
npm run git:push           # Commit and push
```

---

## 🔄 Session Management Protocol

### Starting a Session

**Always start with:**
```bash
npm run session:start
```

**This automatically:**
- Loads WORKFLOW_STATE.json with current progress (252/419 units)
- Queries Memory MCP for project knowledge
- Displays next 3 suggested units from WORK_QUEUE.md
- Shows recent completions and patterns
- Creates SESSION_ACTIVE.txt marker

### Checkpoint System (Automatic)

**Checkpoints run automatically after every 3-unit batch completion.**

```bash
npm run checkpoint
```

**What checkpoint does:**
1. Scans canonical directories for completed units (JSON + chapter files)
2. Validates each unit (schema v3.1.0 compliance)
3. Only counts units meeting ALL 3 requirements:
   - ✅ JSON file exists
   - ✅ Chapter file exists
   - ✅ Passes validation (no critical errors)
4. Updates WORKFLOW_STATE.json with validated count only
5. Regenerates WORK_QUEUE.md with latest progress
6. Creates SESSION_CHECKPOINT.md with recovery info
7. Commits to git with descriptive message

**Maximum data loss in crash: 1-2 units** (<5 min recovery time)

### Crash Recovery Procedure

If session crashes (VS Code restart, network disconnect, etc.):

**Step 1: Check last checkpoint**
```bash
cat SESSION_CHECKPOINT.md
cat WORKFLOW_STATE.json
```

**Step 2: Review what was completed**
- SESSION_CHECKPOINT.md shows last successful commit
- Maximum 1-2 units lost (current batch only)
- RESTORATION_PLAN.md exists for mid-restoration crashes

**Step 3: Resume work**
```bash
npm run session:start
# Continue with next batch - all context loaded automatically
```

**Step 4: Manual checkpoint if needed**
```bash
npm run checkpoint "crash_recovery"
```

### Ending a Session

**Always end sessions cleanly:**
```bash
npm run session:end
```

**Session end automatically:**
1. Creates final checkpoint (if uncommitted work exists)
2. Stores session statistics to Memory MCP
3. Stores patterns/decisions/issues discovered
4. Generates SESSION_SUMMARY.md with progress report
5. Validates no uncommitted changes remain
6. Cleans up SESSION_ACTIVE.txt marker
7. Resets session counter for next session

**Session summary includes:**
- Duration and units completed this session
- Progress percentage (current: 60.1% = 252/419)
- Uncommitted files warning (if any)
- Instructions for resuming next session

### Work Pattern (Proven Stable)

**3-Unit Batches:**
- Process units in groups of 3
- Automatic checkpoint after each batch
- Parallel Task tool execution (3 agents simultaneously)
- ~20-30 minutes per batch (with orchestration)

**NO Session Limits:**
- Continue as long as needed (no 12-unit artificial limit)
- Take breaks between batches to avoid fatigue
- Use session:end when done for the day

---

## Authorized Sources by Nation

### Tier 1 (90-95% Confidence):
- **German**: Tessin Wehrmacht Encyclopedia (17 volumes in `Resource Documents/`)
- **British**: British Army Lists (quarterly 1941-1943 in `Resource Documents/`)
- **Italian**: TM E 30-420 Italian Military Forces handbook
- **American**: US Field Manuals

### Tier 2 (75-85% Confidence):
- **German**: Feldgrau.com, Lexikon der Wehrmacht, Bundesarchiv
- **Italian**: Comando Supremo, Italian Army official histories
- **British**: Unit war diaries, Imperial War Museum, regimental histories
- **American**: NARA records, unit histories

### ❌ FORBIDDEN:
- Wikipedia (ANY language)
- Wikia/Fandom sites
- Unsourced forums
- AI-generated content

---

## Common Workflows

### 1. Complete Showcase (Current Priority)

```bash
# Read gap analysis (updated with resolved gaps)
"Read data/output/1941-q2-showcase/SHOWCASE_GAPS.md"

# Read completion report for v3.0 details
"Read data/output/1941-q2-showcase/RE-EXTRACTION_COMPLETE.md"

# Gap 1 - Extract British Corps
"Extract XIII Corps TO&E for 1941-Q2"
"Extract Western Desert Force TO&E for 1941-Q2"

# Gap 2 - Extract Italian Corps
"Extract XX Corpo d'Armata TO&E for 1941-Q2"
"Extract XXI Corpo d'Armata TO&E for 1941-Q2"
```

### 2. Extract New Units

```bash
# Start autonomous mode
npm run start:autonomous

# Or manual mode
npm run start:claude

# Follow PROCESSING_GUIDE.md in output session directory
```

### 3. Add Corps Units

```bash
# Extract British corps
"Extract XIII Corps TO&E for 1941-Q2"
"Extract Western Desert Force TO&E for 1941-Q2"

# Extract Italian corps
"Extract XX Corpo d'Armata TO&E for 1941-Q2"
"Extract XXI Corpo d'Armata TO&E for 1941-Q2"
```

### 4. Quality Assurance

```bash
# Run full validation
npm run qa:v3

# Check specific unit
npm run validate:v3 data/units/german_1941q2_15th_panzer_division_toe.json
npm run validate:sources data/units/german_1941q2_15th_panzer_division_toe.json
```

---

## Memory Graph Entities (MCP)

If you need context from previous sessions:

```bash
# Search for project entities
"Search knowledge graph for North_Africa_TOE_Builder"
"Search knowledge graph for v3_schema_update"
"Search knowledge graph for 1941_Q2_Showcase"

# Read full graph
"Read entire knowledge graph"
```

---

## Project Goals Reminder

**Primary Purpose**: Generate wargaming scenarios with realistic supply/logistics constraints

**Scope**: 313-348 units total
- **420 unit-quarters** (117 unique units) - Ground Forces (Phase 1-6) ← **Current Focus**
- ~100-135 Air Forces (Phase 7)
- Campaign system (Phase 8-10)

**Quality Standards**:
- Minimum 75% confidence on all data
- Minimum 2 sources per critical fact
- NO Wikipedia sources allowed
- All equipment counts validated bottom-up
- Parent-child totals match (±5%)

---

## Quick Reference

| Need | Command |
|------|---------|
| See project scope | Read `PROJECT_SCOPE.md` |
| See schema | Read `schemas/unified_toe_schema.json` |
| See agents | Read `agents/agent_catalog.json` |
| See showcase gaps | Read `data/output/1941-q2-showcase/SHOWCASE_GAPS.md` |
| Validate v3.0 | `npm run qa:v3` |
| Start autonomous | `npm run start:autonomous` |
| Check memory | Search knowledge graph for "North_Africa_TOE_Builder" |

---

**Ready to continue? Just tell me what you want to work on!** 🚀

**Recommended Next Step**:
1. "Read VERSION_HISTORY.md to understand technical evolution (schema v1.0 → v2.0 → v3.0)"
2. "Read RE-EXTRACTION_COMPLETE.md then extract British/Italian Corps units (Gaps 1 & 2)"
