---
description: Run continuous extraction until queue is empty (NO STOPPING)
---

npm run auto:continuous

# CONTINUOUS MODE - DO NOT STOP UNTIL COMPLETE

**CRITICAL**: This command runs autonomous extraction in continuous mode. You MUST continue processing until the work queue is completely empty or you encounter an actual error.

## What This Does

Launches `npm run auto:continuous` which processes the work queue in batches of 3 units until ALL remaining units are complete.

## Strict Rules for Claude

When this command is active:

1. ✅ **MUST CONTINUE**: Process batches of 3 units continuously
2. ❌ **DO NOT** run `npm run session:end` yourself - the script handles it automatically
3. ❌ **DO NOT** ask "would you like me to continue?"
4. ❌ **DO NOT** stop after a "good number" of units
5. ❌ **DO NOT** worry about token usage in continuous mode
6. ✅ **ONLY STOP IF**:
   - Work queue is empty (no units remaining)
   - Critical error blocks progress (file system issues, etc.)
   - User explicitly tells you to stop

## How It Works

1. Script shows you the next 3 units from WORK_QUEUE.md
2. You launch 3 parallel Task tool agents (one per unit)
3. Script verifies completion and runs session:end automatically
4. Script immediately loads next batch
5. REPEAT until queue is empty

## Expected Behavior

```
Batch 1 (3 units) → extraction → session:end → Batch 2 (3 units) → extraction → session:end → ... → Queue Empty
```

**NO PAUSING BETWEEN BATCHES**

## Designed For

- Overnight unattended runs
- Processing 20-60+ units in one session
- Crash-resistant (session:end after each batch saves progress)

## What User Expects

User ran this command expecting you to continue until the queue is empty. Don't stop early.
