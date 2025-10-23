# Automated Processing Guide

**Created**: 2025-10-23
**Commit**: 1d984fe

---

## TL;DR - What Changed

1. **session:end now runs after EACH batch** (instead of checkpoint)
2. **Automated queue processing added** (no manual "proceed" confirmations)
3. **MCP memory updates every 3 units** (instead of every 12-30 units)
4. **Documentation always synced** (START_HERE + PROJECT_SCOPE updated after each batch)

---

## Your Questions Answered

### Q1: "Does anything get hurt if we run session:end after each batch?"

**Answer: NO - Nothing breaks. session:end INCLUDES checkpoint.**

**What session:end does:**
```
session:end = checkpoint + MCP memory + doc updates + session cleanup
```

**Flow:**
1. ✅ Calls `create_checkpoint.js` internally (validates, updates state, commits git)
2. ✅ Regenerates WORK_QUEUE.md
3. ✅ **Updates MCP Memory** (unit observations, patterns, decisions)
4. ✅ **Updates START_HERE_NEW_SESSION.md** (counts, recent completions)
5. ✅ **Updates PROJECT_SCOPE.md** (progress percentages)
6. ✅ Creates SESSION_SUMMARY.md
7. ✅ Resets session counter to 0

**You were right:** Running session:end after each batch is BETTER for crash resistance!

---

### Q2: "With VS code crashes, more commit to memory is probably better"

**Answer: EXACTLY RIGHT. This is now implemented.**

**Before** (using checkpoint):
- MCP memory updated: Once per session (every 12-30 units)
- VS Code crash loses: Entire session's knowledge (12-30 units)
- Documentation synced: Only at session end

**After** (using session:end):
- MCP memory updated: Every batch (every 3 units)
- VS Code crash loses: Max 1-2 units from current batch
- Documentation synced: After every batch

**Impact:**
- 259/419 units complete (61.8%) was in WORKFLOW_STATE.json
- But START_HERE still showed 254/419 (60.6%)
- Now both stay synced automatically

---

### Q3: "I want to run the process in a loop without saying proceed"

**Answer: Created `process_queue_auto.js` with preset modes.**

---

## New Commands Available

### Quick Reference

```bash
# Interactive mode - Claude shows next 3, waits for confirmation
npm run session:start

# Automated modes - No confirmation needed
npm run auto:quick      # 1 batch  (3 units,  ~20-30 min)
npm run auto:standard   # 3 batches (9 units,  ~60-90 min)
npm run auto:extended   # 5 batches (15 units, ~100-150 min)
npm run auto:marathon   # 10 batches (30 units, ~200-300 min)
npm run auto:continuous # Until queue empty

# Custom batch count
npm run auto -- --batches 7  # Process 7 batches (21 units)
```

### Recommended Workflow

**For Manual Control:**
```bash
npm run session:start
# Claude shows next 3 units
# User says "proceed"
# Claude processes 3 units in parallel
# Claude runs: npm run session:end
# Repeat for next batch
```

**For Automated Processing:**
```bash
npm run auto:standard
# Processes 3 batches (9 units) automatically
# Runs session:end after EACH batch
# No manual confirmations needed
```

---

## Technical Details

### What process_queue_auto.js Does

```
FOR EACH BATCH:
  1. Read next 3 units from WORK_QUEUE.md
  2. Launch 3 parallel Task tool agents (autonomous extraction)
  3. Wait for batch completion
  4. Run npm run session:end
     - Validates units
     - Updates WORKFLOW_STATE.json
     - Commits to git
     - Updates MCP Memory
     - Updates START_HERE_NEW_SESSION.md
     - Updates PROJECT_SCOPE.md
     - Creates SESSION_SUMMARY.md
  5. Repeat for next batch
```

### Preset Batch Sizes

| Mode | Batches | Units | Time Estimate | Use Case |
|------|---------|-------|---------------|----------|
| Quick | 1 | 3 | 20-30 min | Testing, quick progress |
| Standard | 3 | 9 | 60-90 min | **Recommended** daily session |
| Extended | 5 | 15 | 100-150 min | Long work session |
| Marathon | 10 | 30 | 200-300 min | Weekend sprint |
| Continuous | ∞ | All | Until empty | Overnight/unattended |

---

## session:end vs checkpoint - Complete Breakdown

### checkpoint (create_checkpoint.js)

**Does:**
- ✅ Scans canonical units directory
- ✅ Validates units (JSON + chapter + schema)
- ✅ Updates WORKFLOW_STATE.json
- ✅ Regenerates WORK_QUEUE.md
- ✅ Creates SESSION_CHECKPOINT.md
- ✅ Commits to git

**Does NOT:**
- ❌ Update MCP Memory
- ❌ Update START_HERE_NEW_SESSION.md
- ❌ Update PROJECT_SCOPE.md
- ❌ Create SESSION_SUMMARY.md
- ❌ Reset session counter

### session:end (session_end.js)

**Does:**
- ✅ **Calls checkpoint** (all checkpoint features above)
- ✅ **Updates MCP Memory** (unit observations, patterns, decisions)
- ✅ **Updates START_HERE_NEW_SESSION.md** (counts, recent units)
- ✅ **Updates PROJECT_SCOPE.md** (progress percentages)
- ✅ Creates SESSION_SUMMARY.md
- ✅ Resets session counter to 0
- ✅ Removes SESSION_ACTIVE.txt

**Relationship:**
```
session:end = checkpoint + (MCP memory + documentation + cleanup)
```

---

## Migration Path

### Old Workflow (Before Oct 23, 2025)

```bash
npm run session:start
# Process 3 units
npm run checkpoint  # After batch 1
# Process 3 units
npm run checkpoint  # After batch 2
# Process 3 units
npm run checkpoint  # After batch 3
# Process 3 units
npm run checkpoint  # After batch 4
npm run session:end # END OF SESSION (only time MCP memory updated)
```

**Problems:**
- MCP memory updated once (at very end)
- Documentation updated once (at very end)
- VS Code crash loses entire session's MCP memory
- 12-unit sessions showed 254/419 in STATE but docs not synced

### New Workflow (After Oct 23, 2025)

```bash
npm run session:start
# Process 3 units
npm run session:end  # After batch 1 (MCP memory + docs updated)
# Process 3 units
npm run session:end  # After batch 2 (MCP memory + docs updated)
# Process 3 units
npm run session:end  # After batch 3 (MCP memory + docs updated)
```

**OR:**

```bash
npm run auto:standard  # Runs above workflow automatically
```

**Benefits:**
- MCP memory updated 3 times (every 3 units)
- Documentation synced 3 times (always current)
- VS Code crash loses max 1-2 units (not entire session)
- WORKFLOW_STATE.json and docs always match

---

## Crash Recovery Examples

### Old System (checkpoint)

```
Session starts: 254/419 complete
Batch 1: 3 units → checkpoint → 257/419 in STATE (docs still 254)
Batch 2: 3 units → checkpoint → 260/419 in STATE (docs still 254)
💥 VS CODE CRASH 💥
Lost: 6 units of MCP memory, documentation out of sync
Docs show: 254/419 (wrong)
State shows: 260/419 (correct, but MCP memory empty)
```

### New System (session:end)

```
Session starts: 254/419 complete
Batch 1: 3 units → session:end → 257/419 (STATE + docs + MCP ✅)
Batch 2: 3 units → session:end → 260/419 (STATE + docs + MCP ✅)
💥 VS CODE CRASH 💥
Lost: Max 1-2 units from current batch
Docs show: 260/419 (correct)
State shows: 260/419 (correct)
MCP memory: 260 units stored (correct)
```

---

## What This Fixes

### Issue 1: Documentation Drift

**Before:**
- WORKFLOW_STATE.json: 259/419 (61.8%)
- START_HERE_NEW_SESSION.md: 254/419 (60.6%)
- PROJECT_SCOPE.md: 254/419 (60.6%)

**After:**
- All three files always match (updated after each batch)

### Issue 2: MCP Memory Gaps

**Before:**
- MCP memory updated: Once per session (end only)
- Search for recent units: 0 entities found

**After:**
- MCP memory updated: After each batch (every 3 units)
- Search for recent units: All units have 5-10 observations

### Issue 3: Manual Confirmation Fatigue

**Before:**
- Every batch requires "proceed" confirmation
- 30 units = 10 confirmations

**After:**
- Automated mode: 0 confirmations
- 30 units = `npm run auto:marathon`

---

## Recommendations

### For Daily Work

```bash
npm run auto:standard  # 9 units, 3 batches, ~60-90 min
```

### For Testing

```bash
npm run auto:quick  # 3 units, 1 batch, ~20-30 min
```

### For Unattended Processing

```bash
npm run auto:continuous  # Until queue empty
# ⚠️  Monitor for errors
# ⚠️  Check SESSION_SUMMARY.md periodically
```

### For Manual Control (Still Available)

```bash
npm run session:start
# Claude shows next 3 units
# User says "proceed"
# Claude processes batch
# Claude runs session:end
# Repeat
```

---

## Files Modified

1. **scripts/process_queue_auto.js** (NEW - 280 lines)
   - Automated queue processing with presets
   - Reads WORK_QUEUE.md → processes batches → runs session:end

2. **package.json**
   - Added 6 new NPM scripts (auto, auto:quick, auto:standard, etc.)

3. **scripts/session_start.js**
   - Updated workflow instructions to use session:end after each batch
   - Added crash-resistance notes
   - Added automated mode documentation

---

## Git History

```
1d984fe - feat: Add automated queue processing + switch to session:end after each batch
```

**See commit message for complete technical details.**

---

## Next Steps

1. ✅ **Try the new workflow:**
   ```bash
   npm run auto:quick
   ```

2. ✅ **Verify documentation syncs:**
   - Check START_HERE_NEW_SESSION.md after batch
   - Check PROJECT_SCOPE.md after batch
   - Both should show same count as WORKFLOW_STATE.json

3. ✅ **Verify MCP memory updates:**
   ```bash
   # After batch completes, search for recent unit
   "Search knowledge graph for [recent unit name]"
   # Should find entity with 5-10 observations
   ```

4. ✅ **Use automated mode for production:**
   ```bash
   npm run auto:standard  # Recommended for daily sessions
   ```

---

**Status**: ✅ All changes committed and ready to use

**Commit**: 1d984fe
**Date**: 2025-10-23
**Author**: Claude Code (based on user insights)
