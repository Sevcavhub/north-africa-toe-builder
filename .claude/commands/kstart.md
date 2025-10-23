---
description: Starts Autonomous Orchestrator.
---

⚠️ **THIS IS A TWO-STEP COMMAND - DO NOT AUTO-EXECUTE BOTH STEPS!** ⚠️

## ⚠️ PARAMETER SUPPORT

**SUPPORTED**: /kstart (no parameters - uses WORK_QUEUE.md order)
**NOT SUPPORTED**: /kstart -1940, /kstart -year, /kstart chronological

If user requests year/quarter filtering:
1. Explain that /kstart reads next 3 from WORK_QUEUE.md in pre-determined order
2. WORK_QUEUE.md is already sorted: **ECHELON-FIRST** (Divisions→Corps→Armies), then chronological
3. To focus on specific year/quarter, user should use WORK_QUEUE.md sections directly

## 🔒 CRITICAL: ECHELON ORDERING MUST BE MAINTAINED

**WORK_QUEUE.md enforces BOTTOM-UP ECHELON ORDER (GLOBAL)**:
- ALL Divisions (all quarters) BEFORE ANY Corps
- ALL Corps (all quarters) BEFORE ANY Armies
- Within each echelon: chronological order (1940-Q2 → 1943-Q2)

**When displaying units, you MUST maintain this order**:
✅ CORRECT: Division (1940-Q3) → Division (1941-Q2) → Corps (1940-Q3)
❌ WRONG: Army (1940-Q3) → Corps (1940-Q3) → Division (1940-Q3)

**If user asks to filter by year** (e.g., "show only 1940 units"):
- You MUST still maintain echelon priority within that year
- Example for 1940: Division (1940-Q3) → Division (1940-Q4) → Army (1940-Q3)
- NEVER show: Army → Corps → Division (this breaks bottom-up aggregation)

## STEP 1: SHOW NEXT 3 UNITS (Execute immediately)

Run: Bash('npm run session:start')

This will display:
- Quarter completion dashboard
- **Next 3 units from WORK_QUEUE.md** (ECHELON-FIRST, then chronological)
- Session counter (0/12 units this session)
- Progress summary

## STEP 2: WAIT FOR USER DECISION (DO NOT EXECUTE UNTIL USER RESPONDS!)

After showing next 3 units, OUTPUT THIS MESSAGE TO USER:

```
📋 Next 3 units from WORK_QUEUE.md:

[List the 3 units here]

Session Progress: [X]/12 units this session (max 4 batches of 3)

⚠️ BEFORE I LAUNCH THE AUTONOMOUS ORCHESTRATOR, please choose:

• Reply "Proceed" → I will launch Task tool for these 3 units
• Reply "Skip" → I will skip these units and show next 3 from queue
• Reply "Use [unit list]" → I will use your custom unit selection instead

What would you like to do?
```

## STEP 3: ONLY EXECUTE AFTER USER REPLIES "Proceed"

❌ DO NOT execute this step until user explicitly says "Proceed"
❌ DO NOT assume user wants to proceed
❌ DO NOT launch Task tool automatically

When user says "Proceed", THEN launch Task tool:
- subagent_type='general-purpose'
- Prompt: "Run autonomous orchestration for North Africa TO&E Builder..."

## WORKFLOW (3-3-3-3 Pattern):

1. **Batch 1**: Process 3 units → `npm run checkpoint` (auto-commit) → Session: 3/12
2. **Batch 2**: Process 3 units → `npm run checkpoint` (auto-commit) → Session: 6/12
3. **Batch 3**: Process 3 units → `npm run checkpoint` (auto-commit) → Session: 9/12
4. **Batch 4**: Process 3 units → `npm run checkpoint` (auto-commit) → Session: 12/12
5. **BLOCKED**: Run `npm run session:end` to reset counter and save summary

**CHECKPOINT AUTOMATICALLY**:
- ✅ Updates WORKFLOW_STATE.json
- ✅ Increments session counter (+3)
- ✅ Regenerates WORK_QUEUE.md
- ✅ Commits to git
- ✅ Pushes to GitHub

## CRITICAL RULES:
1. /kstart is NOT a single automatic command
2. /kstart means: show next 3 from WORK_QUEUE.md, THEN wait for user decision
3. User must explicitly confirm before Task tool launches
4. DO NOT perform extraction yourself - specialized agents only
5. Session limit: 12 units max (prevents AI drift/hallucination)
6. **ALWAYS maintain ECHELON-FIRST ordering** (Divisions→Corps→Armies, even when filtering)
7. Parameters like -1940 are NOT supported - explain this to user