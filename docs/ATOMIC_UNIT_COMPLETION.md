# Atomic Unit Completion - Architecture v4.1

**Date:** October 14, 2025
**Feature:** Atomic unit+chapter generation
**Status:** ✅ Implemented and tested

---

## Problem

Before v4.1, unit JSON and MDBook chapters were created separately:
- Unit JSON saved by orchestrator/agents
- Chapters generated manually by separate script
- **Result:** Many units had JSON but NO chapters

This violated the "complete unit" concept - we want **unit JSON + chapter together always**.

---

## Solution: Atomic Completion Handler

Created `scripts/lib/unit_completion.js` that provides **one function** to complete a unit:

```javascript
const { completeUnit } = require('./scripts/lib/unit_completion');

const result = await completeUnit(
  unitData,      // Complete validated unit JSON
  'german',      // Nation
  '1941q2',      // Quarter
  '15_panzer_division'  // Designation
);

// Returns:
// {
//   unitPath: 'data/output/units/german_1941q2_15_panzer_division_toe.json',
//   chapterPath: 'data/output/chapters/chapter_german_1941q2_15_panzer_division.md',
//   updated: true  // true if new, false if re-extraction
// }
```

**What it does atomically:**
1. ✅ Save unit JSON to canonical location (`data/output/units/`)
2. ✅ Generate MDBook chapter from that JSON
3. ✅ Save chapter to canonical location (`data/output/chapters/`)
4. ✅ Update `WORKFLOW_STATE.json` completed list
5. ✅ Return paths to both files

**Guarantees:**
- If unit JSON exists, chapter exists
- If chapter exists, unit JSON exists
- Both use canonical paths (Architecture v4.0)
- WORKFLOW_STATE.json stays in sync

---

## Usage in Orchestrators

### Before (v4.0 and earlier):

```javascript
// OLD WAY - Manual, error-prone
const unitPath = paths.getUnitPath(nation, quarter, designation);
await fs.writeFile(unitPath, JSON.stringify(unitData, null, 2));
// Chapter generation: FORGOTTEN OR DONE LATER
// WORKFLOW_STATE.json: UPDATE FORGOTTEN
```

### After (v4.1+):

```javascript
// NEW WAY - Atomic, automatic
const { completeUnit } = require('./scripts/lib/unit_completion');

const result = await completeUnit(unitData, nation, quarter, designation);
// Done! Unit JSON + chapter + WORKFLOW_STATE all updated atomically
```

---

## Integration Points

### 1. Autonomous Orchestrator

**File:** `src/autonomous_orchestrator.js`

**Where to use:**
- After agent returns validated unit JSON
- Replace direct `fs.writeFile()` calls with `completeUnit()`

**Example:**
```javascript
// In Phase 4: TO&E Generation
const unitData = agentOutput.unit_json;  // From historical_research agent

// OLD:
// await fs.writeFile(unitPath, JSON.stringify(unitData, null, 2));

// NEW:
const { completeUnit } = require('../scripts/lib/unit_completion');
const result = await completeUnit(
  unitData,
  unit.nation,
  unit.quarter,
  naming.normalizeDesignation(unit.unit_designation)
);

console.log(`✅ Completed: ${result.unitPath}`);
console.log(`✅ Chapter:   ${result.chapterPath}`);
```

### 2. Intelligent Orchestrator

**File:** `src/intelligent_orchestrator.js`

**Where to use:**
- When processing completed agent tasks
- After schema validation passes

**Example:**
```javascript
// In monitorPhase1() when task completes
const taskOutput = JSON.parse(await fs.readFile(outputPath, 'utf-8'));

if (taskOutput.status === 'success' && taskOutput.unit_json) {
  const { completeUnit } = require('../scripts/lib/unit_completion');

  const result = await completeUnit(
    taskOutput.unit_json,
    task.inputs.nation,
    task.inputs.quarter,
    naming.normalizeDesignation(task.inputs.unit_designation)
  );

  this.taskStats.completed++;
  console.log(`✅ Unit completed: ${result.updated ? 'NEW' : 'UPDATED'}`);
}
```

### 3. Manual Claude Code Sessions

**When you manually create a unit JSON:**

```javascript
// After constructing unitData object manually:
const { completeUnit } = require('./scripts/lib/unit_completion');

await completeUnit(
  unitData,
  'italian',
  '1941q2',
  'xx_corpo_d_armata_motorizzato'
);

// Both files created automatically!
```

### 4. Agent Outputs

**Agents should return unit JSON only:**
- Agents extract/build the unit JSON data
- Agent output includes `unit_json` field
- Orchestrator calls `completeUnit()` with that JSON
- Chapter generation is NOT the agent's job

---

## Chapter Generation Details

**Template:**
The `generateChapterFromData()` function creates an 8-section MDBook chapter:

1. **Header** - Unit name, nation, quarter, type
2. **Overview** - Parent formation, history
3. **Command Structure** - Commander, staff strength
4. **Personnel Summary** - Total, breakdown by category
5. **Tanks & Armored Vehicles** - By type, by model
6. **Artillery** - Field, AT, AA, mortars
7. **Ground Vehicles** - Trucks, cars, motorcycles
8. **Data Quality** - Confidence, sources, notes

**Dynamic:** Only includes sections that have data (e.g., if no tanks, skips tanks section)

**Format:** Clean markdown tables, proper formatting

---

## Testing

**Test suite:** `test_atomic_completion.js` (run once, then deleted)

**Test results:**
```
✅ Creates unit JSON (1,502 bytes)
✅ Creates chapter MD (1,377 bytes)
✅ Updates WORKFLOW_STATE.json
✅ Returns correct paths
✅ Both files exist atomically
```

**Production use:**
- Already used to create test unit (german_1941q2_test_regiment)
- Successfully created and cleaned up
- Ready for XX Corps re-extraction

---

## Migration Path

**Existing units (151 completed):**

Many units have JSON but NO chapters. To backfill:

```bash
# Script to backfill missing chapters
node scripts/generate_missing_chapters.js
```

This will:
1. Scan `data/output/units/*.json`
2. Check if corresponding chapter exists in `data/output/chapters/`
3. Generate missing chapters using `generateChapterFromData()`

**Future units:**
- All new extractions MUST use `completeUnit()`
- No more manual `fs.writeFile()` for units
- Chapter generation is automatic

---

## Benefits

**Before v4.1:**
- ❌ Units and chapters created separately
- ❌ Easy to forget chapter generation
- ❌ WORKFLOW_STATE.json updates manual
- ❌ 151 units, ~50% missing chapters

**After v4.1:**
- ✅ Atomic unit+chapter creation
- ✅ Impossible to forget chapter (automatic)
- ✅ WORKFLOW_STATE.json always in sync
- ✅ Future units: 100% will have chapters

---

## Next Steps

1. ✅ Implement `unit_completion.js` (DONE)
2. ✅ Test atomic completion (DONE)
3. ⏳ Re-extract XX Corps using proper agents
4. ⏳ Compare manual vs agent-generated outputs
5. 🔜 Update orchestrators to use `completeUnit()`
6. 🔜 Backfill missing chapters for existing units

---

**Version:** Architecture v4.1 - Atomic Unit Completion
**Maintainer:** Claude Code Orchestration Team
**Related:** `docs/VERSION_HISTORY.md`, `docs/CANONICAL_PATHS.md`
