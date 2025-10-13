# 🚀 NEW SESSION - START HERE

**Project**: North Africa TO&E Builder - **v3.0.0 (Ground Forces)**
**Last Updated**: 2025-10-13
**Status**: Schema v3.0 Complete, Ready for Unit Extraction

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

### 🔨 IN PROGRESS:
- **1941-Q2 Showcase**: 18 units generated, needs Gap 3/5/8 fixes
- **Wikipedia Violations**: 7 chapters (38.9%) need regeneration with Tier 1/2 sources only
- **Infantry Weapons**: Missing from all 18 chapters (data exists, needs extraction)
- **Corps Roll-ups**: 2 British + 2 Italian corps units need extraction

### 📋 NEXT PRIORITIES:

1. **Gap 8 Fix** (CRITICAL): Regenerate all 18 chapters with Infantry Weapons section
2. **Gap 3 Fix** (CRITICAL): Remove Wikipedia from 7 chapters (Bologna, Ariete, 15.Panzer, 1st SA, 4th Indian, 5th Indian, 7th Armoured)
3. **Gap 5 Fix** (HIGH): Fix empty Division Overview sections (Bologna, Trieste)
4. **Gaps 1 & 2** (HIGH): Extract 4 corps units (XIII Corps, WDF, XX Corpo, XXI Corpo)

---

## Key Files to Reference

### Project Documentation:
- `PROJECT_SCOPE.md` - Complete scope (313-348 units, 10 phases)
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
npm run start:autonomous    # RECOMMENDED: Fully autonomous mode
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

### 1. Fix Showcase Gaps (Immediate Priority)

```bash
# Read gap analysis
"Read data/output/1941-q2-showcase/SHOWCASE_GAPS.md"

# Fix Gap 8 (Infantry Weapons)
"Update scripts/generate_mdbook_chapters.js to extract top_3_infantry_weapons"

# Fix Gap 3 (Wikipedia violations)
"Regenerate 7 chapters using only Tier 1/2 sources"

# Fix Gap 5 (Empty sections)
"Fix Bologna and Trieste Division Overview sections"
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
- 213 Ground Forces (Phase 1-6) ← **Current Focus**
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

**Recommended Next Step**: "Review SHOWCASE_GAPS.md and fix Gap 8 (Infantry Weapons extraction)"
