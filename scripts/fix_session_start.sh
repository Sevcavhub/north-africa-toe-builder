#!/bin/bash
# Fix session_start.js with all necessary changes

cd /d/north-africa-toe-builder

# 1. Add validator import after matching import
sed -i "/const matching = require/a const { validateAndRepairState } = require('./lib/state_validator');" scripts/session_start.js

# 2. Replace readWorkflowState function
sed -i '/^async function readWorkflowState/,/^}$/c\
async function readWorkflowState() {\
    try {\
        const data = await fs.readFile(WORKFLOW_STATE_PATH, '\''utf-8'\'');\
        const parsedState = JSON.parse(data);\
        \
        // Validate and auto-repair if needed\
        const { state, repairs } = validateAndRepairState(parsedState, true);\
        \
        // If repairs were made, save the corrected state\
        if (repairs.length > 0) {\
            await fs.writeFile(WORKFLOW_STATE_PATH, JSON.stringify(state, null, 2));\
            console.log('\''✅ WORKFLOW_STATE.json has been auto-repaired and saved\\n'\'');\
        }\
        \
        return state;\
    } catch (error) {\
        return null;\
    }\
}' scripts/session_start.js

# 3. Fix all completed_count || completed.length to just completed.length
sed -i 's/state\.completed_count || state\.completed\.length/state.completed.length/g' scripts/session_start.js

# 4. Fix the totalCompleted line (line ~611)
sed -i 's/state\.completed_count || completed\.length/completed.length/g' scripts/session_start.js

echo "All fixes applied!"
