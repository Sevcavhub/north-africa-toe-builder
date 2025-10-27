---
description: End Air Forces session and save progress to git
---

npm run session:end

# Air Forces Session End

This command ends the current air forces extraction session and saves all progress.

## What This Does

1. Runs final checkpoint (validates all air units, updates WORKFLOW_STATE.json, commits)
2. **Updates MCP Memory** with air forces session statistics, patterns, and squadron observations
3. Creates SESSION_SUMMARY.md with comprehensive air forces session report
4. Removes SESSION_ACTIVE.txt marker
5. Prepares environment for next air forces session

## When to Use

- ✅ **After completing air forces batches** (when done for the day)
- ✅ **Before switching to ground forces work**
- ✅ **When reaching 12-unit session limit**
- ❌ **NOT after every batch** (use automatic checkpoint instead)

## Air Forces Progress Saved

Session end will save to MCP memory:
- Number of squadrons/gruppen/gruppi extracted this session
- Aircraft variant discoveries (new types encountered)
- Squadron organizational patterns learned
- Base/airfield locations tracked
- Sortie/claims/losses data patterns
- Any issues or gaps requiring follow-up

## Next Session Continuity

When you run `/air-start` in the next session:
- WORK_QUEUE_AIR.md will reflect current progress
- MCP Memory will provide context from previous air forces sessions
- Next 3 air units will be loaded automatically
- All aircraft variant data preserved
