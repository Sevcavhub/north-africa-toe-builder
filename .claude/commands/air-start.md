---
description: Start Air Forces extraction session (Phase 7)
---

⚠️ **THIS IS A TWO-STEP COMMAND - DO NOT AUTO-EXECUTE BOTH STEPS!** ⚠️

## ⚠️ PARAMETER SUPPORT

**SUPPORTED**: /air-start (no parameters - uses WORK_QUEUE_AIR.md order)
**NOT SUPPORTED**: /air-start -1941, /air-start -year, /air-start chronological

If user requests year/quarter filtering:
1. Explain that /air-start reads next 3 from WORK_QUEUE_AIR.md in pre-determined order
2. WORK_QUEUE_AIR.md is already sorted: **ECHELON-FIRST** (Staffeln/Squadrons→Gruppen/Gruppi→Groups/Geschwader), then chronological
3. To focus on specific year/quarter, user should use WORK_QUEUE_AIR.md sections directly

## 🔒 CRITICAL: ECHELON ORDERING MUST BE MAINTAINED

**WORK_QUEUE_AIR.md enforces BOTTOM-UP ECHELON ORDER (GLOBAL)**:
- ALL Staffeln/Squadrons (all quarters) BEFORE ANY Gruppen/Gruppi
- ALL Gruppen/Gruppi (all quarters) BEFORE ANY Groups/Geschwader
- Within each echelon: chronological order (1940-Q2 → 1943-Q2)

**When displaying units, you MUST maintain this order**:
✅ CORRECT: Squadron (1940-Q3) → Squadron (1941-Q2) → Gruppe (1940-Q3)
❌ WRONG: Geschwader (1940-Q3) → Gruppe (1940-Q3) → Staffel (1940-Q3)

**If user asks to filter by year** (e.g., "show only 1941 units"):
- You MUST still maintain echelon priority within that year
- Example for 1941: Squadron (1941-Q1) → Squadron (1941-Q2) → Gruppe (1941-Q1)
- NEVER show: Group → Gruppe → Squadron (this breaks bottom-up aggregation)

## STEP 1: SHOW NEXT 3 AIR UNITS (Execute immediately)

Run: Bash('node scripts/session_start.js --air-forces')

This will display:
- Quarter completion dashboard for AIR FORCES
- **Next 3 squadrons/gruppen/gruppi from WORK_QUEUE_AIR.md** (ECHELON-FIRST, then chronological)
- Session counter (0/12 units this session)
- Progress summary (out of 761 total air unit-quarters)

## STEP 2: WAIT FOR USER DECISION (DO NOT EXECUTE UNTIL USER RESPONDS!)

After showing next 3 air units, OUTPUT THIS MESSAGE TO USER:

```
📋 Next 3 air units from WORK_QUEUE_AIR.md:

[List the 3 air units here]

Session Progress: [X]/12 units this session (max 4 batches of 3)

⚠️ BEFORE I LAUNCH THE AIR FORCES ORCHESTRATOR, please choose:

• Reply "Proceed" → I will launch Task tool for these 3 air units
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
- Prompt: "Extract air forces TO&E data for [3 air units]..."

## WORKFLOW (3-3-3-3 Pattern):

1. **Batch 1**: Process 3 air units → `npm run checkpoint` (auto-commit) → Session: 3/12
2. **Batch 2**: Process 3 air units → `npm run checkpoint` (auto-commit) → Session: 6/12
3. **Batch 3**: Process 3 air units → `npm run checkpoint` (auto-commit) → Session: 9/12
4. **Batch 4**: Process 3 air units → `npm run checkpoint` (auto-commit) → Session: 12/12
5. **BLOCKED**: Run `npm run session:end` to reset counter and save summary

**CHECKPOINT AUTOMATICALLY**:
- ✅ Updates WORKFLOW_STATE.json (air forces progress)
- ✅ Increments session counter (+3)
- ✅ Regenerates WORK_QUEUE_AIR.md
- ✅ Commits to git
- ✅ Pushes to GitHub

## AIR FORCE SCHEMA REQUIREMENTS:

**CRITICAL - Aircraft Variant Specificity**:
- ✅ CORRECT: "Messerschmitt Bf 109E-7/Trop"
- ❌ WRONG: "Bf 109", "Messerschmitt Bf 109"
- ✅ CORRECT: "Hawker Hurricane Mk IIB"
- ❌ WRONG: "Hurricane"
- ✅ CORRECT: "Macchi MC.202 Folgore Serie III"
- ❌ WRONG: "MC.202"

**NO GENERIC AIRCRAFT ENTRIES ALLOWED** - Every aircraft variant must have:
- Full manufacturer name
- Complete model designation
- Variant suffix (Ausf, Mk, Serie, etc.)
- Tropical/Desert modifications if applicable

## CRITICAL RULES:
1. /air-start is NOT a single automatic command
2. /air-start means: show next 3 from WORK_QUEUE_AIR.md, THEN wait for user decision
3. User must explicitly confirm before Task tool launches
4. DO NOT perform extraction yourself - specialized AIR agents only
5. Session limit: 12 units max (prevents AI drift/hallucination)
6. **ALWAYS maintain ECHELON-FIRST ordering** (Staffeln→Gruppen→Geschwader, even when filtering)
7. Parameters like -1941 are NOT supported - explain this to user
8. **Aircraft variants MUST be specific** - reject generic entries during validation
