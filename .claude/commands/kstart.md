---
description: Starts Autonomous Orchestrator.
---

You are the GENERAL AGENT receiving a /kstart command.

**STEP 1: Show recommendations**
1. Run: Bash('npm run session:start')
2. The output shows:
   - Quarter completion dashboard
   - Strategy options (chronological, quarterly, specific quarter)
   - 3 recommended units
   - Full autonomous prompt at the end

**STEP 2: Present to user (DO NOT AUTO-LAUNCH YET!)**
Report to user:
- Show the 3 recommended units
- Show the target quarter and completion %
- Ask: "These are the recommended units. Reply with:
  • 'Proceed' → Launch autonomous orchestrator for these 3 units
  • 'Change to [quarter/strategy]' → Adjust selection first
  • 'Use [specific units]' → Custom unit list"

**STEP 3: ONLY AFTER user confirms "Proceed"**
Launch Task tool (subagent_type='general-purpose') with prompt:
"Run autonomous orchestration for North Africa TO&E Builder. Process these 3 units: [unit list]. Use specialized sub-agents for ALL extraction, validation, and chapter generation phases including Phase 6 Seed Reconciliation. Save outputs to canonical locations (data/output/units/ and data/output/chapters/). Run checkpoint after batch completion."

**CRITICAL:**
- DO NOT launch Task tool until user confirms
- DO NOT perform extraction yourself - that's for specialized agents via Task tool
- After launching Task tool, step back and let autonomous orchestrator work