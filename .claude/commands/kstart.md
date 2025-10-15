---
description: Starts Autonomous Orchestrator.
---

⚠️ **THIS IS A TWO-STEP COMMAND - DO NOT AUTO-EXECUTE BOTH STEPS!** ⚠️

## STEP 1: SHOW RECOMMENDATIONS (Execute immediately)

Run: Bash('npm run session:start')

This will display:
- Quarter completion dashboard
- 3 recommended units
- Target quarter and strategy

## STEP 2: WAIT FOR USER DECISION (DO NOT EXECUTE UNTIL USER RESPONDS!)

After showing recommendations, OUTPUT THIS MESSAGE TO USER:

```
📋 Recommended units for autonomous orchestration:

[List the 3 units here]

Target Quarter: [quarter] ([completion]% complete)

⚠️ BEFORE I LAUNCH THE AUTONOMOUS ORCHESTRATOR, please choose:

• Reply "Proceed" → I will launch Task tool for these 3 units
• Reply "Change to [strategy/quarter]" → I will re-run session:start with different strategy
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

## CRITICAL RULES:
1. /kstart is NOT a single automatic command
2. /kstart means: show recommendations, THEN wait for user decision
3. User must explicitly confirm before Task tool launches
4. DO NOT perform extraction yourself - specialized agents only