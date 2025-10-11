# Intelligent Orchestrator - Complete Guide

**Fully automated TO&E builder for the North African Campaign (1940-1943)**

---

## 🎯 What is the Intelligent Orchestrator?

The Intelligent Orchestrator is a **fully automated system** that:

1. **Discovers all units** automatically by scanning sources
2. **Creates all tasks** for 15 agents across 6 phases
3. **Monitors progress** with live dashboard
4. **Handles reviews** - pauses for human approval at critical points
5. **Advances phases** automatically when complete
6. **Documents sources** for every fact extracted
7. **Manages the entire workflow** from raw sources to finished TO&E

**You don't manually create tasks** - the orchestrator does everything!

---

## 🚀 Quick Start

### Step 1: Start Agent Terminals

**Before starting the orchestrator, open agent terminals:**

1. **Window 2:** `npm run agent document_parser` (Phase 1)
2. **Window 3:** `npm run agent historical_research` (Phase 1)

*(Add Phase 2-6 agents as needed - see SETUP_AGENTS.md)*

### Step 2: Start Orchestrator

**In your main terminal (Window 1):**

```bash
npm run orchestrate
```

That's it! The orchestrator now:
- ✓ Loads North Africa Campaign project
- ✓ Scans sources to discover all units
- ✓ Creates extraction tasks for Phase 1
- ✓ Monitors agent progress
- ✓ Pauses for your review at checkpoints
- ✓ Advances through all 6 phases

---

## 📊 What You'll See

### Initial Startup

```
================================================================================
  🎯 Intelligent TO&E Orchestrator
================================================================================

📋 Project: North Africa Campaign TO&E Builder
📍 Theater: North Africa
📅 Period: 1940-Q2 to 1943-Q2
🌍 Nations: Italy, Germany, Britain, France, USA, Commonwealth
📊 Levels: corps → division → regiment → battalion → company → platoon → squad

🔍 Discovering units in North Africa...

  Scanning Germany sources...
  Scanning Italy sources...
  Scanning Britain sources...
  Scanning USA sources...
  Scanning France sources...

✓ Discovered 150 units across all nations and quarters

  Germany: 45 units
  Italy: 38 units
  Britain: 52 units
  USA: 8 units
  France: 7 units

================================================================================
  📖 PHASE 1: Source Extraction
================================================================================

Creating extraction tasks for all discovered units...

✓ Created 150 extraction tasks

📊 Tasks pending: 150

⏳ Waiting for agents to process tasks...
   (Start agents in separate terminals with: npm run agent <agent_name>)

📊 Progress: [████░░░░░░] 42/150 (28%)
   ⏳ Pending: 108 | ⚙️  Processing: 12 | ✓ Done: 30 | ✗ Failed: 0
```

### Review Checkpoint Triggered

```
================================================================================
  ⏸️  REVIEW REQUIRED: LOW CONFIDENCE
================================================================================

  15 units with confidence < 75%

  Details:
    1. {"unit": "Ariete Division", "quarter": "1940-Q3", "confidence": 68, ...}
    2. {"unit": "Trieste Division", "quarter": "1941-Q1", "confidence": 72, ...}
    ...

  [A]pprove | [R]eview Details | [M]odify | [S]kip | [Q]uit:
```

**Your options:**
- **A** (Approve): Accept and continue
- **R** (Review Details): See full data for flagged items
- **M** (Modify): Pause to manually correct data in tasks/review/
- **S** (Skip): Continue without addressing issues
- **Q** (Quit): Stop orchestration

### Phase Complete

```
================================================================================
  ✅ PHASE 1 COMPLETE
================================================================================

  📊 Summary:
     Total units: 150
     Avg confidence: 87%
     Sources used: 23
     Review flags: 8

  Proceed to next phase? [Y/n]:
```

---

## 🔄 The 6 Phases

### **Phase 1: Source Extraction** (Current Implementation)

**What happens automatically:**
1. Orchestrator scans primary sources (Tessin, British Army Lists, Field Manuals)
2. Discovers all units matching patterns (e.g., ".*Panzer.*Division", ".*Armoured.*Division")
3. Creates `document_parser` task for each unit
4. Agents extract facts from sources
5. Creates `historical_research` task to verify facts
6. Agents verify with additional sources

**Outputs:**
- `outputs/{nation}/{quarter}/raw_facts.json` (per unit)
- `outputs/{nation}/{quarter}/verified_facts.json` (per unit)

**Review triggers:**
- Low confidence (<75%)
- Missing required fields (unit_designation, commander, organization)

---

### **Phase 2: Organization Building**

**What happens automatically:**
1. Orchestrator reads all verified_facts.json files
2. Creates `org_hierarchy` tasks to build org trees
3. Creates `toe_template` tasks to identify unit types
4. Creates `unit_instantiation` tasks to apply templates
5. Agents build complete hierarchy from corps → squad

**Outputs:**
- `outputs/{nation}/{quarter}/org_tree.json`
- `outputs/templates/{unit_type}_template.json`
- `outputs/{nation}/{quarter}/units/{unit_id}.json` (SCM format)

**Review triggers:**
- Org tree inconsistencies
- Missing parent/child relationships
- Template application conflicts

---

### **Phase 3: Equipment Distribution**

**What happens automatically:**
1. Orchestrator analyzes theater-level equipment availability
2. Creates `theater_allocator` tasks for top-down allocation
3. Creates `division_cascader` tasks for cascading to squads
4. Creates `equipment_reconciliation` tasks to verify totals
5. Agents distribute equipment across all levels

**Outputs:**
- `outputs/{nation}/{quarter}/equipment_allocations/`
- `outputs/{nation}/{quarter}/reconciliation_reports/`

**Review triggers:**
- Equipment total mismatches
- Allocation conflicts
- Historical accuracy issues

---

### **Phase 4: Aggregation**

**What happens automatically:**
1. Orchestrator triggers bottom-up aggregation
2. Creates `bottom_up_aggregator` tasks starting from squads
3. Creates `top3_calculator` tasks for weapon rankings
4. Agents aggregate SCM data up through all levels to theater
5. Validates totals match across levels

**Outputs:**
- `outputs/{nation}/{quarter}/aggregated/{level}/`
- `outputs/{nation}/{quarter}/theater_scm.json`
- Top 3 weapons at each level

**Review triggers:**
- Aggregation sum mismatches
- Top 3 calculation errors

---

### **Phase 5: Validation**

**What happens automatically:**
1. Orchestrator runs schema validation on all outputs
2. Creates `schema_validator` tasks for technical validation
3. Creates `historical_accuracy` tasks for content validation
4. Agents check against known historical data
5. Flags errors for correction

**Outputs:**
- `outputs/validation_reports/{validation_id}.json`
- `outputs/accuracy_reports/{unit_id}.json`

**Review triggers:**
- Schema validation failures
- Historical inaccuracies detected
- Confidence degradation

---

### **Phase 6: Output Generation**

**What happens automatically:**
1. Orchestrator prepares final output tasks
2. Creates `book_chapter_generator` tasks for narrative chapters
3. Creates `scenario_exporter` tasks for wargame scenarios
4. Creates `sql_populator` tasks for database generation
5. Agents generate all final deliverables
6. Compiles complete bibliography

**Outputs:**
- `outputs/final/chapters/{nation}/` (markdown chapters with citations)
- `outputs/final/scenarios/` (JSON scenario files)
- `outputs/final/database.sql` (complete SQL database)
- `outputs/final/bibliography.md` (Chicago-style bibliography)

**Review triggers:**
- Bibliography completeness check
- Final quality review

---

## 🎛️ Orchestrator Configuration

All configuration is in **`projects/north_africa_campaign.json`**

### Key Settings

**Scope:**
```json
{
  "theater": "North Africa",
  "time_period": {
    "quarters": ["1940-Q2", ..., "1943-Q2"]
  },
  "nations": {
    "axis": ["Italy", "Germany"],
    "allies": ["Britain", "France", "USA", "Commonwealth"]
  },
  "organizational_levels": ["corps", "division", "regiment", "battalion", "company", "platoon", "squad"]
}
```

**Source Strategy (3-tier waterfall):**
```json
{
  "waterfall_priority": [
    {
      "tier": 1,
      "name": "Local Primary Documents",
      "sources": ["Tessin", "British Army Lists", "US Field Manuals"],
      "confidence_base": 90
    },
    {
      "tier": 2,
      "name": "Curated Web Sources",
      "sources": ["Feldgrau.com", "Niehorster.org", "Asisbiz.com", ...],
      "confidence_base": 75
    },
    {
      "tier": 3,
      "name": "General Web Search",
      "excluded_domains": ["wikipedia.org"],
      "confidence_base": 60,
      "requires_verification": true
    }
  ]
}
```

**Review Checkpoints:**
```json
{
  "automatic_pause_on": [
    {"trigger": "phase_complete"},
    {"trigger": "low_confidence", "threshold": 75},
    {"trigger": "source_conflict"},
    {"trigger": "validation_failure"},
    {"trigger": "unexpected_error"}
  ]
}
```

---

## 📁 File Structure Created by Orchestrator

```
outputs/
└── north_africa_campaign/
    ├── raw/
    │   ├── Germany/
    │   │   ├── 1941-Q2/
    │   │   │   ├── 21_panzer_division_raw_facts.json
    │   │   │   └── ...
    │   │   └── ...
    │   └── ...
    ├── verified/
    │   ├── Germany/
    │   │   └── 1941-Q2/
    │   │       └── 21_panzer_division_verified_facts.json
    │   └── ...
    ├── org_trees/
    ├── units/
    ├── aggregated/
    └── final/
        ├── chapters/
        ├── scenarios/
        ├── database/
        └── sources/
            └── bibliography.md

tasks/
├── pending/         ← Orchestrator creates tasks here
├── in_progress/     ← Agents move tasks here when processing
├── completed/       ← Agents move tasks here when done
└── failed/          ← Agents move tasks here on error

checkpoints/
└── north_africa_campaign/
    ├── phase_1_checkpoint.json
    ├── phase_2_checkpoint.json
    └── ...
```

---

## ⏸️ Pause and Resume

### Pause Orchestration

**Manual pause:** Press `Ctrl+C` in orchestrator terminal

**Automatic pause:** Orchestrator pauses at review checkpoints

### Resume After Pause

```bash
npm run orchestrate:resume
```

The orchestrator:
- ✓ Loads most recent checkpoint
- ✓ Resumes from last completed phase
- ✓ Continues monitoring tasks
- ✓ Picks up where it left off

---

## 🔍 Source Documentation

**Every fact extracted includes:**

```json
{
  "fact_id": "f_001",
  "fact_type": "personnel",
  "data": {
    "unit_designation": "21st Panzer Division",
    "commander": "Generalleutnant Johann von Ravenstein"
  },
  "source_citation": {
    "source_name": "Tessin Band 08",
    "page": 145,
    "line": 23,
    "confidence": 95,
    "verification_sources": [
      {
        "source_name": "Tessin Band 03",
        "page": 78,
        "confidence": 90
      }
    ]
  }
}
```

**Final bibliography generated automatically** in Chicago Manual of Style format.

---

## 📊 Monitoring Progress

### Live Dashboard (in orchestrator terminal)

```
📊 Progress: [████████░░] 120/150 (80%)
   ⏳ Pending: 20 | ⚙️  Processing: 10 | ✓ Done: 115 | ✗ Failed: 5
```

### Check Task Status (anytime)

```bash
# See pending tasks
ls tasks/pending

# See what's being processed
ls tasks/in_progress

# See completed tasks
ls tasks/completed

# See failed tasks
ls tasks/failed

# Check outputs
ls outputs/north_africa_campaign/verified/Germany/1941-Q2
```

---

## 🛠️ Troubleshooting

### Orchestrator won't start

```bash
# Check project config exists
ls projects/north_africa_campaign.json

# Check required directories exist
mkdir -p tasks/{pending,in_progress,completed,failed}
mkdir -p outputs checkpoints
```

### Agents not picking up tasks

1. **Ensure agents are running** in separate terminals:
   ```bash
   npm run agent document_parser    # Window 2
   npm run agent historical_research # Window 3
   ```

2. **Check task files exist:**
   ```bash
   ls tasks/pending
   ```

3. **Check agent_id matches** in task files

### Task stuck in in_progress

```bash
# Move back to pending to retry
mv tasks/in_progress/task_XXX.json tasks/pending/
```

### Phase won't advance

1. **Check for failed tasks:**
   ```bash
   ls tasks/failed
   ```

2. **Review failure reasons** in task files

3. **Fix and retry:**
   ```bash
   # Edit task if needed, then move back to pending
   mv tasks/failed/task_XXX.json tasks/pending/
   ```

---

## 🎯 Best Practices

### 1. Start Small, Scale Up

**First run:** Start with just Phase 1 agents (document_parser, historical_research)
- Process a few units to verify workflow
- Add Phase 2 agents when ready

**Full run:** Open all 15 agent terminals for complete automation

### 2. Monitor Review Checkpoints

**Low confidence (<75%):**
- Usually means source data is incomplete
- Orchestrator will try Tier 2 web sources automatically
- Review and approve if acceptable

**Source conflicts:**
- Different sources disagree on facts
- Review both versions presented
- Choose more authoritative source

### 3. Use Checkpoints

**Save progress frequently:**
- Checkpoints auto-saved at end of each phase
- Can resume anytime with `npm run orchestrate:resume`

### 4. Verify Source Documentation

**Check that agents are citing sources:**
```bash
# Look at a completed output
cat outputs/north_africa_campaign/verified/Germany/1941-Q2/21_panzer_division_verified_facts.json
```

Should include source_citation for every fact!

---

## 📖 Related Documentation

- **SETUP_AGENTS.md** - How to open 15 agent terminals in VS Code
- **VISUAL_SETUP.md** - Visual guide with diagrams
- **AGENT_COMMANDS.md** - Quick command reference
- **AUTOMATED_WORKFLOW.md** - How agents do extraction work
- **SOURCE_WORKFLOW.md** - Source document details

---

## 🎬 Complete Workflow Example

### Initial Setup (One Time)

```bash
# Window 1: Orchestrator terminal (already open)
cd D:\north-africa-toe-builder

# Window 2: document_parser agent
# File → New Window → Open Folder → D:\north-africa-toe-builder
npm run agent document_parser

# Window 3: historical_research agent
# File → New Window → Open Folder → D:\north-africa-toe-builder
npm run agent historical_research
```

### Start Automated Build

```bash
# Window 1: Start orchestrator
npm run orchestrate
```

**Orchestrator runs automatically:**

1. ✓ Scans Tessin, British Army Lists, Field Manuals
2. ✓ Discovers 150 units across all nations and quarters
3. ✓ Creates 150 document_parser tasks
4. ⏳ Agents process extraction tasks
5. ✓ Creates 150 historical_research verification tasks
6. ⏳ Agents verify facts against additional sources
7. ⏸️  **REVIEW CHECKPOINT:** Low confidence on 15 units
   - You: **[A]** Approve and continue
8. ✅ **PHASE 1 COMPLETE**
   - You: **[Y]** Proceed to Phase 2

**Add Phase 2 agents:**

```bash
# Window 4: org_hierarchy
npm run agent org_hierarchy

# Window 5: toe_template
npm run agent toe_template

# Window 6: unit_instantiation
npm run agent unit_instantiation
```

**Orchestrator continues automatically:**

9. ✓ Creates org_hierarchy tasks for all nations
10. ⏳ Agents build organization trees
11. ✓ Creates toe_template tasks
12. ⏳ Agents identify unit types and create templates
13. ✓ Creates unit_instantiation tasks
14. ⏳ Agents apply templates and instantiate units in SCM format
15. ✅ **PHASE 2 COMPLETE**
    - You: **[Y]** Proceed to Phase 3

*...continues through all 6 phases...*

16. ✅ **ALL PHASES COMPLETE!**

**Final outputs:**
- ✓ 150 complete TO&E files (SCM format, all levels)
- ✓ Complete organization trees
- ✓ Equipment allocations and aggregations
- ✓ Validation reports
- ✓ Book chapters with narrative
- ✓ Wargame scenarios
- ✓ SQL database
- ✓ Complete bibliography with citations

---

## 💡 Key Advantages

**Why use the Intelligent Orchestrator?**

1. **Fully Automated** - No manual task creation, orchestrator does everything
2. **True Independence** - 15 separate Claude Code sessions = no context contamination
3. **Zero API Costs** - File-based orchestration, no OpenAI/Anthropic API calls
4. **Source Documentation** - Every fact cited with source, page, confidence level
5. **Quality Control** - Automatic review checkpoints for human oversight
6. **Scalable** - Handles 150+ units across 13 quarters, all nations, all levels
7. **Resumable** - Save checkpoints, resume anytime after interruption
8. **Verifiable** - All intermediate outputs saved for audit trail

---

## 🚀 Ready to Start!

**Start the automated TO&E build now:**

```bash
# Window 1: Start orchestrator
npm run orchestrate

# Windows 2-3: Make sure Phase 1 agents are running
# (Add more agents as phases progress)
```

**Let the orchestrator do the work!** 🎯
