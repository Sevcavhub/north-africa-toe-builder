# File-Based Multi-Agent System Setup

## Overview

This system runs multiple **independent** Claude Code sessions (one per agent) communicating via files.

**Benefits:**
✅ No API costs (uses Claude Code subscription)
✅ True agent independence (no context contamination)
✅ Parallel execution capability
✅ Each agent in separate terminal = separate Claude context

## Architecture

```
Terminal 1: Orchestrator (manages workflow)
Terminal 2: Agent "document_parser"
Terminal 3: Agent "historical_research"
Terminal 4: Agent "org_hierarchy"
Terminal 5: Agent "toe_template"
Terminal 6: Agent "unit_instantiation"
```

Communication via shared directories:
- `tasks/pending/` - New tasks waiting
- `tasks/in_progress/` - Currently being worked on
- `tasks/completed/` - Finished tasks
- `outputs/` - Agent outputs

## Setup Instructions

### Step 1: Open Multiple VS Code Windows

1. Open **6 separate VS Code windows**
2. Each window should open the `north-africa-toe-builder` folder
3. Open Claude Code chat in each window

### Step 2: Start Agent Runners (Terminals 2-6)

In each agent terminal, run:

**Terminal 2:**
```bash
cd north-africa-toe-builder
node src/agent_runner.js document_parser
```

**Terminal 3:**
```bash
cd north-africa-toe-builder
node src/agent_runner.js historical_research
```

**Terminal 4:**
```bash
cd north-africa-toe-builder
node src/agent_runner.js org_hierarchy
```

**Terminal 5:**
```bash
cd north-africa-toe-builder
node src/agent_runner.js toe_template
```

**Terminal 6:**
```bash
cd north-africa-toe-builder
node src/agent_runner.js unit_instantiation
```

Each terminal will show:
```
🤖 Agent Runner: <agent_id>
   Watching for tasks...
   Press Ctrl+C to stop

✓ Loaded configuration for <agent_id>
  Role: <description>
  Category: <category>
```

### Step 3: Start Orchestrator (Terminal 1)

In the orchestrator terminal:

```bash
cd north-africa-toe-builder
node src/file_orchestrator.js
```

The orchestrator will:
1. Create task files in `tasks/pending/`
2. Wait for agents to complete them
3. Move workflow through phases

### Step 4: Execute Agent Tasks

When an agent runner picks up a task:

1. **Agent displays the prompt:**
   ```
   ═══════════════════════════════════════════════
   📋 NEW TASK: task_123456789_abc
   ═══════════════════════════════════════════════

   AGENT PROMPT:
   ────────────────────────────────────────────────
   You are a military historian extracting data...

   [Full prompt displayed here]
   ────────────────────────────────────────────────

   📝 Please provide the agent response as JSON:
   ```

2. **In Claude Code chat for that window, ask me:**
   ```
   Execute this agent prompt and provide JSON output:
   [copy the prompt shown in terminal]
   ```

3. **I'll respond with JSON**

4. **Copy my JSON response and paste it in the terminal**

5. **Type `END_JSON` on a new line**

6. **Agent saves output and marks task complete**

## Example Workflow

### Terminal 1 (Orchestrator):
```
🗂️  File-Based Orchestrator initialized

═══════════════════════════════════════════
  TO&E Build: italian 1940-Q2
  Mode: File-Based Multi-Agent (No API)
═══════════════════════════════════════════

📖 PHASE 1: Source Extraction

📝 Created task: document_parser (task_1760055586_abc)
📝 Created task: historical_research (task_1760055587_def)
```

### Terminal 2 (document_parser agent):
```
🤖 Agent Runner: document_parser
   Watching for tasks...

═══════════════════════════════════════════
📋 NEW TASK: task_1760055586_abc
═══════════════════════════════════════════

AGENT PROMPT:
────────────────────────────────────────────
You are a military historian extracting data from military_handbook.

Task: Extract ALL factual information about italian forces in 1940-Q2.
[... rest of prompt ...]
────────────────────────────────────────────

📝 Please provide the agent response as JSON:
   (Paste the complete JSON output below)

Enter response (type END_JSON on a new line when done):
```

### You in Claude Code Chat (Terminal 2):
```
@claude Execute this agent prompt:

You are a military historian extracting data from military_handbook...
[paste full prompt]
```

### I respond:
```json
{
  "facts": [
    {
      "fact_type": "command",
      "data": {
        "unit": "10th Army",
        "commander": "Marshal Rodolfo Graziani"
      },
      "confidence": 95
    }
  ]
}
```

### You copy my JSON and paste in Terminal 2:
```
[paste JSON]
END_JSON
```

### Terminal 2 (document_parser):
```
✓ Task completed successfully!

Watching for next task...
```

## Tips

1. **Keep all terminals visible** - Use VS Code split view or multiple monitors

2. **One window = One agent** - Don't mix agents in same window (prevents context contamination)

3. **Copy prompts carefully** - Make sure you get the full prompt including all context

4. **Paste complete JSON** - Include all braces, formatting

5. **Use `END_JSON`** - This signals the runner you're done

6. **Monitor orchestrator** - Terminal 1 shows overall progress

## Troubleshooting

**Agent not picking up task:**
- Check that agent_id matches exactly
- Verify task file is in `tasks/pending/`
- Restart agent runner

**JSON parse error:**
- Make sure JSON is valid
- Check for missing braces
- Try wrapping in ```json code fence

**Task timeout:**
- Default timeout is 10 minutes
- For long tasks, modify timeout in file_orchestrator.js

**Multiple agents grabbing same task:**
- Should not happen - each watches for their agent_id only
- If it does, check task.agent_id field

## Stopping the System

1. **Complete current tasks first**
2. Press `Ctrl+C` in each agent runner terminal
3. Press `Ctrl+C` in orchestrator terminal

## Next Steps

After testing Phases 1-2:
- Add Phase 3 (Equipment Distribution)
- Add Phase 4 (Aggregation)
- Add Phase 5 (Validation)
- Add Phase 6 (Output Generation)

Each phase follows same pattern:
1. Orchestrator creates tasks
2. Agents watch and execute
3. Results saved to files
4. Next phase begins
