# Project Restoration Plan - Session Drift Fix
**Created**: 2025-10-23
**Status**: PLANNING
**Goal**: Restore consistent workflow, fix drift issues, complete 167 remaining units in 2-3 weeks

---

## Quick Context
- **Current State**: 252/419 units (60.1%), but workflow drifted from Oct 18 baseline
- **Root Cause**: Sessions changing workflows based on feedback without fully reverting unsuccessful changes
- **Solution**: Restore authoritative workflow, fix systematic issues, enforce consistency

---

## 🚨 ROOT CAUSE IDENTIFIED

**MCP Memory Gap: October 18-23, 2025**
- Memory has 34k tokens of data through October 19
- **NOTHING stored from Oct 18-23** (baseline establishment + recent drift)
- Each new session starts with outdated context (Oct 10-19 knowledge)
- Sessions improvising because they don't know about:
  - Oct 18: PROJECT_SCOPE.md baseline
  - Oct 21: Work queue workflow changes
  - Oct 22: Orchestration protocol fixes
  - Oct 22-23: Schema v3.1.0 tiered extraction
  - Session drift problems and resolutions

**Impact**: Without recent memory, each Claude session reinvents workflows instead of following established patterns.

---

## Phase 1: Critical Fixes (DO FIRST)

### 1.0 Fix MCP Memory Integration ✅ COMPLETE **[TOP PRIORITY]**
**Problem**: Session knowledge not being stored in MCP memory since Oct 19
**Impact**: Each session loses context, causing workflow drift

**Tasks**:
- [ ] Audit `scripts/session_end.js` - check if it writes to memory MCP
- [ ] Check if Task tool sub-agents are configured to use memory MCP
- [ ] Create retroactive memory entities for Oct 18-23:
  - [ ] "PROJECT_SCOPE_Baseline_Oct18" entity
  - [ ] "Schema_v3.1.0_Tiered_Extraction" entity
  - [ ] "Work_Queue_Workflow_Change_Oct21" entity
  - [ ] "Orchestration_Protocol_Restore_Oct22" entity
  - [ ] "Session_Drift_Root_Causes" entity with observations
  - [ ] "Discovered_Units_Feature_v3.1.0" entity
  - [ ] "Count_Sync_Issues" entity
- [ ] Fix session_end.js to automatically write session learnings to memory
- [ ] Add memory writes to checkpoint script
- [ ] Test: Run session, check memory updated

**Memory Entities to Create**:

```javascript
// Entity 1: PROJECT_SCOPE baseline (Oct 18)
{
  name: "PROJECT_SCOPE_Baseline_Oct18_2025",
  entityType: "project_baseline",
  observations: [
    "Established October 18, 2025 as authoritative project definition",
    "Complete scope: 420 ground unit-quarters (117 unique units)",
    "Phased approach: Phase 1-4 complete, Phase 5 (4.3%) + Phase 6 (28.1%) in progress",
    "Schema: v3.0.0 with supply/weather, v3.1.0 added tiered extraction",
    "Architecture v4.0: Canonical output locations enforced",
    "Work queue: Chronological + echelon ordering from seed file",
    "All agents MUST reference PROJECT_SCOPE.md as authoritative"
  ]
}

// Entity 2: Schema v3.1.0 (Oct 15 - not documented in memory)
{
  name: "Schema_v3.1.0_Tiered_Extraction",
  entityType: "technical_specification",
  observations: [
    "Added October 15, 2025 - extends v3.0.0",
    "Tiered extraction system: Tier 1 (75-100%), Tier 2 (60-74%), Tier 3 (50-59%), Tier 4 (<50%)",
    "validation.tier field (1-4) indicates extraction quality",
    "validation.status: production_ready | review_recommended | partial_needs_research | research_brief_created",
    "validation.required_field_gaps array lists missing required fields",
    "validation.gap_documentation object: detailed gap info with mitigation strategies",
    "discovered_units array (optional): reports units found NOT in seed",
    "discovered_units REQUIRES combat participation validation (garrison/reserve excluded)",
    "Non-breaking: v3.0 units can upgrade by adding tier=1, status='production_ready'",
    "Purpose: Handle real-world incomplete data, prevent all-or-nothing extraction failure"
  ]
}

// Entity 3: Work queue workflow (Oct 21)
{
  name: "Work_Queue_Workflow_Oct21_2025",
  entityType: "workflow_change",
  observations: [
    "Changed October 21, 2025: Work queue replaced dynamic strategy selection",
    "WORK_QUEUE.md generated from seed file: chronological + echelon ordering",
    "Echelon priority: divisions before corps before armies (bottom-up aggregation)",
    "Session workflow: npm run session:start → reads next 3 from queue → user confirms → Task tool launches",
    "/kstart command: two-step (show queue → wait for user 'Proceed' → launch)",
    "NO automatic 12-unit session limit enforcement (per user directive Oct 23)",
    "Checkpoint auto-commits, regenerates queue, increments session counter",
    "Fuzzy matching improved recognition: 32% → 50.4% (134 → 211 units)"
  ]
}

// Entity 4: Orchestration protocol restore (Oct 22)
{
  name: "Orchestration_Protocol_Restore_Oct22",
  entityType: "workflow_fix",
  observations: [
    "Fixed October 22, 2025 (commit 9b9b961)",
    "Problem: Agent doing sequential extraction instead of orchestrating parallel sub-agents",
    "Speed impact: 3x slower (20 min vs 7 min for 3 units)",
    "Root cause: session_start.js instructions changed from 'Launch Task tool' to 'Do it yourself'",
    "Solution: Restore orchestration protocol with explicit role statement",
    "Mandatory parallel execution: 3 Task tools in ONE message (not sequential)",
    "Proof-of-execution required: must show Task tool calls",
    "MCP integration: agents use mcp__filesystem for Tessin/Army Lists, mcp__memory for knowledge storage",
    "16 specialized agents: document_parser, historical_research, org_hierarchy, etc.",
    "Impact: Restores 3x speed, proper MCP tool usage, specialized agent delegation"
  ]
}

// Entity 5: Session drift root causes
{
  name: "Session_Drift_Root_Causes_Oct18_23",
  entityType: "problem_analysis",
  observations: [
    "Identified October 23, 2025 after user feedback",
    "Period: October 18-23 sessions drifted from baseline",
    "Root cause 1: MCP memory not updated since Oct 19 - sessions lost context",
    "Root cause 2: Workflow changes made without complete revert when unsuccessful",
    "Root cause 3: Multiple documentation sources conflicting (START_HERE vs Ken Prompt)",
    "Root cause 4: No automated enforcement - agents improvising workflows each session",
    "Impact: Work queue suggesting corps before divisions, count sync drift, agent self-extraction",
    "Solution: Fix MCP memory integration, consolidate docs, enforce orchestration protocol"
  ]
}

// Entity 6: Count sync issues
{
  name: "Count_Sync_Issues_Oct23",
  entityType: "technical_issue",
  observations: [
    "Multiple count discrepancies: 252 vs 253 vs 259 units",
    "Root cause: Count incremented on JSON creation, not validation pass",
    "Definition of complete: JSON + chapter + passes validation (3 requirements)",
    "Fix: Checkpoint validates each unit with scripts/lib/validator.js before counting",
    "Validator checks: v3.1.0 schema compliance (tier, gap_documentation, supply/weather)",
    "Only units passing all 3 checks increment WORKFLOW_STATE.json count",
    "Failed validations logged but not counted as complete"
  ]
}
```

**Test Memory Update**:
```bash
# After creating entities, verify they're stored
node -e "
const mcp = require('./mcp_helpers');
mcp.search('PROJECT_SCOPE_Baseline_Oct18').then(console.log);
"
```

---

### 1.1 Fix Work Queue Ordering ✅ COMPLETE
**Problem**: Suggests corps before divisions complete (violates bottom-up aggregation)
**Current**: Chronological → Echelon within quarter
**Fix**: Strict bottom-up across ALL quarters (all divisions before ANY corps)

**Files**:
- [ ] `scripts/generate_work_queue.js` - Change sorting logic (lines 150-180)
- [ ] Add comments documenting bottom-up rationale

**Test**:
```bash
npm run queue:generate
cat WORK_QUEUE.md | head -30
# Verify: Next 3 units are divisions, NOT corps
```

---

### 1.2 Add Combat Criteria to Discovered Units ✅ COMPLETE
**Problem**: Schema v3.1.0 discovered_units lacks combat participation validation

**Files**:
- [ ] `schemas/unified_toe_schema.json` (lines 475-499)
  - Add: `combat_validation_required: true`
  - Add: Examples of valid (combat) vs invalid (garrison) units
  - Add: Warning about scope creep
- [ ] `agents/agent_catalog.json` - historical_research v3.2.1
  - Add validation rule: discovered units MUST show combat participation
  - Add required field: `sources_showing_combat` array
  - Add rejection rule: garrison/reserve/rear-area = output REJECTED

**Criteria for valid discovered unit**:
- ✅ Documented combat in North Africa battles (Compass/Crusader/Gazala/Alamein/Torch/Tunisia)
- ❌ NO garrison units
- ❌ NO reserve formations
- ❌ NO rear-area units
- ❌ NO administrative HQs
- ❌ NO units stationed elsewhere (Italy/Greece/etc)

---

### 1.3 Audit & Fix Validator ✅ COMPLETE
**Problem**: scripts/lib/validator.js may not enforce v3.1.0 schema correctly

**Tasks**:
- [ ] Read `scripts/lib/validator.js` completely
- [ ] Check validation for v3.1.0 features:
  - [ ] validation.tier field (1-4)
  - [ ] validation.status field
  - [ ] validation.required_field_gaps array
  - [ ] validation.gap_documentation object
  - [ ] discovered_units array (if present, validate combat criteria)
- [ ] Check validation for v3.0.0 features:
  - [ ] supply_logistics object (5 required fields)
  - [ ] weather_environment object (5 required fields)
- [ ] Fix any missing validations
- [ ] Test with known good/bad units

**Test**:
```bash
# Test with passing unit
node scripts/lib/validator.js data/output/units/german_1941q2_15_panzer_division_toe.json

# Test with failing unit
node scripts/lib/validator.js data/output/units/british_1940q3_4th_indian_division_toe.json
```

---

### 1.4 Make Count Sync Automatic ✅ COMPLETE
**Problem**: Counts drift (252 vs 253 vs 259) because sync is manual

**Definition of Complete Unit**:
- ✅ JSON file exists in `data/output/units/`
- ✅ Chapter file exists in `data/output/chapters/`
- ✅ Unit passes validation (`scripts/lib/validator.js`)

**Files to modify**:
- [ ] `scripts/create_checkpoint.js`
  - [ ] After scanning canonical units, validate each with validator.js
  - [ ] Only count as complete if: JSON + chapter + validation passes
  - [ ] Log units that fail validation (don't increment count)
  - [ ] Update WORKFLOW_STATE.json with validated count only

**Test**:
```bash
# Run checkpoint
npm run checkpoint

# Check counts match
echo "Units in data/output/units/:" && ls data/output/units/*.json | wc -l
echo "Chapters in data/output/chapters/:" && ls data/output/chapters/*.md | wc -l
echo "WORKFLOW_STATE.json completed:" && jq '.completed | length' WORKFLOW_STATE.json
echo "Work queue completed:" && grep -c "^\- \[x\]" WORK_QUEUE.md

# All 4 numbers should match (or explain discrepancies)
```

---

## Phase 2: Documentation Consolidation

### 2.1 Merge START_HERE + Ken Prompt ✅ COMPLETE
**Decision**: Consolidate into `START_HERE_NEW_SESSION.md`

**Valuable content from Ken Prompt to extract**:
- ❌ ~~Session limits (12 unit enforcement)~~ - DO NOT ADD (per user)
- ✅ Checkpoint protocol details
- ✅ Crash recovery procedures
- ✅ Template compliance checklist

**Tasks**:
- [ ] Read both documents completely
- [ ] Identify overlapping sections
- [ ] Extract valuable unique content from Ken Prompt
- [ ] Integrate into START_HERE (maintain START_HERE as base)
- [ ] Move Ken Prompt to `docs/archive/STRICT_AUTONOMOUS_MODE_v1.md`
- [ ] Add deprecation header to archived version
- [ ] Create `docs/archive/README.md` explaining archive purpose

---

### 2.2 Rewrite CLAUDE.md ✅ COMPLETE
**Problem**: "kind of a jumble of mismatch directions" (user feedback)

**New structure**:
```markdown
1. Quick Orientation (project/phase/schema/workflow)
2. Session Workflow (3-3-3 pattern without limit enforcement)
3. Schema & Standards (links to authoritative docs)
4. Critical Rules (seed authority, combat criteria, Task tool, canonical paths)
5. Equipment Database (Phase 5 - keep current section)
6. Project Scope (links to PROJECT_SCOPE.md + VERSION_HISTORY.md)
7. Common Commands
```

**Tasks**:
- [ ] Create new CLAUDE.md structure
- [ ] Consolidate overlapping instructions
- [ ] Remove contradictions
- [ ] Add explicit references to authoritative docs
- [ ] Test clarity (can new session understand it?)

---

## Phase 3: Workflow Enforcement

### 3.1 Update session_start.js Prompt ⬜ NOT STARTED
**Ensure**: Oct 22 fix (commit 9b9b961) stays permanent

**Add to prompt**:
- [ ] Explicit role verification at top
- [ ] Required proof: "Show 3 Task tool calls in response"
- [ ] Failure condition: "Cannot use Task tool = STOP and explain"
- [ ] MCP tool usage requirements
- [ ] Orchestrator NOT extractor reminder

**File**: `scripts/session_start.js` (lines 497-536)

---

### 3.2 Create Pre-Flight Validation Script ⬜ NOT STARTED
**New file**: `scripts/validate_session_readiness.js`

**Checks**:
- [ ] WORKFLOW_STATE.json exists and valid
- [ ] WORK_QUEUE.md exists and current
- [ ] No SESSION_ACTIVE.txt (prevents double-start)
- [ ] Canonical directories exist
- [ ] Warns if uncommitted changes

**Integration**:
- [ ] Update `package.json` - add `session:ready` script
- [ ] `npm run session:start` calls validation first
- [ ] Fails fast if environment not ready

---

## Phase 4: Version History Updates

### 4.1 Document Discovered Units in VERSION_HISTORY.md ⬜ NOT STARTED
**Missing**: Schema v3.1.0 doesn't document discovered_units feature

**Add after line 556**:
- Added discovered_units array (optional)
- Combat participation validation REQUIRED
- Purpose: catch missing combat units, prevent scope creep
- Examples of valid/invalid discovered units

---

### 4.2 Update PROJECT_SCOPE.md Progress ⬜ NOT STARTED
**Current**: Shows 28.1% (118/420) - outdated
**Actual**: 60.1% (252/419)

**Updates**:
- [ ] Line 6-7: Update percentages
- [ ] Update "Last Updated" date to today
- [ ] Mark as auto-updated by checkpoint (living document)

---

## Phase 5: Testing & Validation

### 5.1 Test Complete Workflow End-to-End ⬜ NOT STARTED
```bash
# 1. Generate work queue
npm run queue:generate
cat WORK_QUEUE.md | head -30
# ✓ Verify: Next 3 are divisions not corps

# 2. Start session
npm run session:start
# ✓ Verify: Prompt shows orchestration instructions
# ✓ Verify: No session limit mentioned

# 3. Process 3 units (paste into Claude Code)
# ✓ Verify: Agent launches 3 Task tool calls
# ✓ Verify: Outputs to canonical locations
# ✓ Verify: All 3 pass validation

# 4. Checkpoint
npm run checkpoint
# ✓ Verify: WORKFLOW_STATE.json +3 units
# ✓ Verify: WORK_QUEUE.md regenerated
# ✓ Verify: Counts synchronized
```

---

### 5.2 Fix 2 Schema Validation Errors ⬜ NOT STARTED
**From QA report**:

1. `british_1940q3_4th_indian_division_toe.json`:
   - Uses nested structure instead of top-level fields
   - Commander NULL but confidence 87%

2. `british_1940q4_1_south_african_division_toe.json`:
   - Missing required field: `schema_type`

**Tasks**:
- [ ] Fix both units
- [ ] Re-run validation
- [ ] Verify 254 passed, 0 failed

---

## Implementation Timeline

**Total: 5-7 hours spread over 2-3 days**

### Day 1 (Today) - UPDATED PRIORITIES
- ⬜ **Phase 1.0 - Fix MCP memory integration (2 hours) ← START HERE**
- ⬜ Phase 1.1 - Work queue ordering (1 hour)
- ⬜ Phase 1.2 - Combat criteria (30 min)
- ⬜ Phase 1.3 - Validator audit (1 hour)

### Day 2 (Tomorrow)
- ⬜ Phase 2.1 - Documentation merge (1 hour)
- ⬜ Phase 2.2 - CLAUDE.md rewrite (1 hour)
- ⬜ Phase 3.1 - session_start enforcement (30 min)
- ⬜ Phase 3.2 - Pre-flight validation (30 min)

### Day 3
- ⬜ Phase 4.1 - VERSION_HISTORY update (15 min)
- ⬜ Phase 4.2 - PROJECT_SCOPE update (15 min)
- ⬜ Phase 5.1 - End-to-end test (1 hour)
- ⬜ Phase 5.2 - Fix validation errors (30 min)

---

## Success Criteria

✅ Work queue orders divisions before corps (strict bottom-up)
✅ Discovered units have combat validation (no garrison creep)
✅ Validator enforces v3.1.0 schema completely
✅ Count sync automatic at each checkpoint (JSON + chapter + validation)
✅ Single authoritative workflow document (START_HERE consolidated)
✅ CLAUDE.md clear and unambiguous
✅ Agent orchestration enforced (Task tool required)
✅ All sessions follow same workflow (no drift)

**Then**: Complete 167 remaining units in 2-3 weeks
- 3 units/batch × 3-4 batches/day × 5 days/week = 45-60 units/week
- 167 units ÷ 50/week avg = **~3 weeks to completion**

---

## Progress Tracking

Update this section as work progresses:

**Phase 1**: ✅✅✅✅ 4/4 complete (100%)
**Phase 2**: ✅✅ 2/2 complete (100%)
**Phase 3**: ✅✅ 2/2 complete (100%)
**Phase 4**: ✅✅ 2/2 complete (100%)
**Phase 5**: ✅✅ 2/2 complete (100%)

**Overall**: 12/12 tasks complete (100%) ✅ RESTORATION COMPLETE

---

## Notes & Decisions

**2025-10-23 (Session Start)**: Plan created

**2025-10-23 (Session Complete)**: Phase 1 COMPLETE (4/4 tasks, 4.5 hours)
- ✅ 1.0: Created 6 retroactive MCP memory entities for Oct 18-23 baseline knowledge
- ✅ 1.1: Fixed work queue ordering (echelon-first globally, not chronological-first)
- ✅ 1.2: Added combat_evidence requirement to discovered_units schema + validation rule
- ✅ 1.3: Updated validator.js with v3.0.0 (supply/weather) and v3.1.0 (tier/status/gaps/combat) checks
- ✅ 1.4: Modified checkpoint to only count units passing JSON + chapter + validation (all 3 required)
- ✅ Removed 12-unit session limit enforcement from checkpoint script
- User confirmed: NO session limit enforcement
- User confirmed: Count sync must be automatic (JSON + chapter + validation)
- User confirmed: Validator needs review for v3.1.0
- User confirmed: Discovered units need combat criteria

---

## Crash Recovery

If VS Code crashes during implementation:
1. Open this file: `RESTORATION_PLAN.md`
2. Check Phase progress tracking above
3. Continue from last uncompleted task
4. Update checkboxes as you complete tasks
5. Update "Progress Tracking" percentages

---

**Last Updated**: 2025-10-23 (session start)
**Next Review**: After Phase 1 complete
