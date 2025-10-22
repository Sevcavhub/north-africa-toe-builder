# Orchestrator Analysis - Issues Found (October 21, 2025)

## Summary

Recent changes to fix source prioritization (divisions before corps) appear to have inadvertently created discrepancies between the autonomous orchestrator, session start script, and documentation. The workflow steps (3-3-3, checkpoint, QA, commits, end session) ARE present in the code but are being delivered through DIFFERENT paths than expected.

---

## Key Findings

### 1. **Two Competing Autonomous Workflows Exist**

**Workflow A: `session_start.js` (via `npm run session:start` or `/kstart`)**
- Location: `scripts/session_start.js:480-551`
- Generates prompt that includes:
  - ✅ 3-3-3 rule mentioned (line 493)
  - ✅ Checkpoint instruction (line 496: "After batch complete: Bash('npm run checkpoint')")
  - ✅ Session end (line 498: "When done: Bash('npm run session:end')")
  - ✅ User confirmation required BEFORE launching Task tool
  - ✅ Division-before-corps prioritization (added in last 2 days)
- **Two-step process:**
  1. Show recommendations and wait for user confirmation
  2. ONLY AFTER user says "Proceed" → launch Task tool with 3-unit batch

**Workflow B: `autonomous_orchestrator.js` (via `npm run start:autonomous` or `/krun-Autonomous`)**
- Location: `src/autonomous_orchestrator.js:229-349`
- Generates MUCH MORE DETAILED prompt that includes:
  - ✅ 6-phase workflow (Setup → Document Extraction → Cross-Reference → TO&E Generation → Output Generation → Seed Reconciliation)
  - ✅ Checkpoint after every 3-unit batch (line 270: "**CHECKPOINT: After every 3-unit batch, run: Bash('npm run checkpoint')**")
  - ✅ MCP integration instructions (SQLite, Puppeteer, Memory, Git)
  - ✅ Seed reconciliation (human-in-loop for discrepancies)
  - ✅ Extended thinking, parallel processing (batches of 3)
  - ❌ NO user confirmation step - expects autonomous execution immediately
  - ❌ NO division-before-corps prioritization in prompt (relies on external seed file order)

---

### 2. **Slash Command Confusion**

**Three slash commands exist with different behaviors:**

**`/kstart` (.claude/commands/kstart.md)**
- Runs: `npm run session:start`
- Behavior: TWO-STEP (show recommendations → wait for user → launch Task tool)
- Status: ✅ Working as designed

**`/krun-Autonomous` (.claude/commands/krun-Autonomous.md)**
- Runs: `npm run start:autonomous`
- Behavior: ONE-STEP (immediately display autonomous orchestrator prompt)
- Status: ✅ Working as designed

**`/kend` (.claude/commands/kend.md)**
- Runs: `npm run session:end`
- Status: ✅ Working as designed

**Issue:** Users might expect `/krun-Autonomous` to do the same thing as `/kstart` but it doesn't. They serve different purposes.

---

### 3. **Documentation References Non-Existent Command**

**File:** `STRICT AUTONOMOUS MODE - Ken Prompt.md:13`
- References: `npm run session:ready`
- **Status:** ❌ DOES NOT EXIST in package.json
- **Impact:** Users following this doc will get "script not found" error

**Should be:** `npm run session:start` (which DOES exist)

---

### 4. **Missing Steps in Autonomous Orchestrator Prompt**

The `autonomous_orchestrator.js` prompt (lines 229-349) includes ALL the workflow steps:

✅ **Present:**
- 3-3-3 batching (line 269: "Process units in parallel (batches of 3 maximum)")
- Checkpoint after each batch (line 270: "**CHECKPOINT: After every 3-unit batch**")
- TodoWrite tracking (line 252, 269)
- QA validation (Phase 3: Cross-Reference Validation, lines 276-282)
- Git commits (line 256: "If Git MCP available: Create initial commit")
- Session end implied (Phase 6 deliverables, lines 330-337)

❌ **Missing:**
- Explicit "When done: npm run session:end" instruction
- User confirmation step before launching autonomous work
- Division-before-corps prioritization (relies on seed file order)

---

### 5. **Recent Changes That May Have Caused Regression**

**Git history analysis shows:**

**Commit 24d65bb (2 days ago): "feat: Add checkpoint extraction"**
- Modified `scripts/session_start.js`
- Added `scripts/lib/matching.js` for improved unit matching
- **Added division-before-corps prioritization** (lines 256-277 in session_start.js)
- This is GOOD - fixes the source prioritization issue

**Commit 836a61b (2 days ago): "feat: Add checkpoint extraction"**
- Multiple checkpoint commits
- Archive weak source units
- Update seed file with aliases
- **NO changes to autonomous_orchestrator.js**

**Observation:** Division-before-corps prioritization was added to `session_start.js` but NOT to `autonomous_orchestrator.js`. This creates a discrepancy in which units get selected depending on which workflow you use.

---

## Root Cause Analysis

### Why It Feels "Less Autonomous"

**User perception:** "Acting like less autonomous special agents following instructions versus manual things occurring"

**Actual cause:** The TWO-STEP confirmation process in `session_start.js` makes it FEEL more manual:

1. User runs `/kstart` (or `npm run session:start`)
2. System shows 3 recommended units
3. System WAITS for user to say "Proceed"
4. ONLY THEN does it launch the Task tool for autonomous work

This is INTENTIONAL (lines 536-539):
```
1. ✅ CONFIRM these units with user (or allow adjustments)
2. ✅ ONLY AFTER confirmation → Launch Task tool with autonomous orchestrator
3. ✅ Specialized agents do ALL extraction, validation, chapter generation
4. ❌ DO NOT perform extraction yourself as general agent
```

**But:** The `autonomous_orchestrator.js` workflow (via `/krun-Autonomous`) expects IMMEDIATE autonomous execution without confirmation.

**Confusion:** Users might think `/kstart` should be fully autonomous, but it's designed to be semi-autonomous (user confirms batch first).

---

### Why Steps Seem Missing

**User perception:** "Not all steps being completed like they used to; Identify 3-3-3, checkpoints, commit, QA and end session"

**Actual cause:** Steps ARE present in BOTH workflows, but delivered differently:

**`session_start.js` workflow:**
- ✅ Identifies 3-unit batch (lines 614-643)
- ✅ Shows 3-3-3 rule (line 493)
- ✅ Instructs checkpoint (line 496)
- ✅ Instructs session end (line 498)
- ⚠️ QA mentioned indirectly (lines 497, 563)
- ⚠️ Commits happen via checkpoint (not explicit in prompt)

**`autonomous_orchestrator.js` workflow:**
- ✅ Processes all units in project (not just 3)
- ✅ Checkpoints after every 3-unit batch (line 270)
- ✅ QA validation in Phase 3 (lines 276-282)
- ✅ Git commits if MCP available (lines 243, 256, 300)
- ❌ NO explicit "session:end" instruction
- ❌ NO 3-unit batch limit (processes ALL remaining units)

**Discrepancy:** The two workflows have DIFFERENT scopes:
- `session:start` → 3 units per session (manual batch selection)
- `start:autonomous` → ALL remaining units (full autonomous run)

---

## Recommendations

### Option 1: Unify the Workflows (Recommended)

**Goal:** Make both workflows produce the same behavior

**Changes needed:**

1. **Add user confirmation to `autonomous_orchestrator.js`:**
   - Modify prompt to say: "CONFIRM units with user before launching Task tool"
   - Match `session_start.js` two-step approach

2. **Add division-before-corps prioritization to `autonomous_orchestrator.js`:**
   - Use same logic from `session_start.js:256-277`
   - Ensure divisions are processed before corps in all workflows

3. **Add explicit session:end instruction to `autonomous_orchestrator.js`:**
   - Add to Phase 6 deliverables: "Run: npm run session:end when all units complete"

4. **Fix documentation:**
   - Update `STRICT AUTONOMOUS MODE - Ken Prompt.md` to reference `session:start` instead of non-existent `session:ready`
   - Clarify difference between `/kstart` (3-unit batch) and `/krun-Autonomous` (full run)

---

### Option 2: Keep Workflows Separate (Alternative)

**Goal:** Document the differences clearly so users know which to use

**Changes needed:**

1. **Create clear decision tree:**
   ```
   Use /kstart (session:start) when:
   - You want to process 3 units at a time (incremental progress)
   - You want to confirm unit selection before launching
   - You want manual control over batches

   Use /krun-Autonomous (start:autonomous) when:
   - You want to process ALL remaining units in one session
   - You want zero manual intervention (full autonomous)
   - You want to leverage all MCP capabilities
   ```

2. **Update documentation to explain both workflows**

3. **Still fix `session:ready` reference bug**

4. **Still add division-before-corps to autonomous_orchestrator.js**

---

### Option 3: Deprecate One Workflow (Nuclear Option)

**Goal:** Eliminate confusion by having ONE canonical way to start sessions

**Recommendation:** Keep `session:start` (incremental, user-controlled), deprecate `start:autonomous` (too aggressive for production use)

**Rationale:**
- `session:start` gives user control (safer)
- Division-before-corps prioritization already implemented there
- Matches Ken's 3-3-3 rule (3 units per session)
- Less risk of runaway autonomous extraction

---

## Immediate Fixes Needed (Regardless of Option Chosen)

### 1. Fix Documentation Bug
**File:** `STRICT AUTONOMOUS MODE - Ken Prompt.md`
**Line 13:** Change `npm run session:ready` → `npm run session:start`

### 2. Add Division-Before-Corps to Autonomous Orchestrator
**File:** `src/autonomous_orchestrator.js`
**Add:** Sorting logic from `session_start.js:256-277` to ensure divisions processed before corps

### 3. Clarify Slash Command Differences
**Create:** New doc explaining when to use `/kstart` vs `/krun-Autonomous`

### 4. Add Explicit Session:End to Autonomous Orchestrator
**File:** `src/autonomous_orchestrator.js:300`
**Add:** "If Git MCP available: Final commit with complete summary AND run: npm run session:end"

---

## Testing Recommendations

After fixes applied, test both workflows:

### Test 1: session:start workflow
```bash
npm run session:start
# Should show:
# - Quarter dashboard
# - 3 recommended units (DIVISIONS FIRST)
# - Prompt with 3-3-3 rule, checkpoint, session:end instructions
# - User confirmation required
```

### Test 2: start:autonomous workflow
```bash
npm run start:autonomous
# Should show:
# - Full project prompt
# - Division-before-corps sorting
# - Checkpoint instructions after every 3-unit batch
# - Explicit session:end instruction when complete
```

### Test 3: Crash recovery
```bash
# Start session, process 2 units, force crash
# Check SESSION_CHECKPOINT.md has last successful unit
# Verify WORKFLOW_STATE.json updated
# Resume with npm run session:start
```

---

## Conclusion

**The workflow steps (3-3-3, checkpoint, QA, commits, end session) ARE present in the code**, but they're split across TWO different autonomous workflows with different scopes and behaviors. Recent changes to add division-before-corps prioritization were only applied to ONE workflow, creating the perception that things are "less autonomous" or "missing steps."

**Recommended action:** Implement Option 1 (Unify the Workflows) to ensure consistency across all entry points.

---

**Analysis Date:** October 21, 2025
**Analyzed By:** Claude Code (Sonnet 4.5)
**Git Commits Reviewed:** Last 20 commits (HEAD~20..HEAD)
**Files Analyzed:**
- `scripts/session_start.js`
- `src/autonomous_orchestrator.js`
- `.claude/commands/kstart.md`
- `.claude/commands/krun-Autonomous.md`
- `.claude/commands/kend.md`
- `STRICT AUTONOMOUS MODE - Ken Prompt.md`
- `package.json`
