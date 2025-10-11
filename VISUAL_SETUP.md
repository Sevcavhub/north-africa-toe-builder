# Visual Multi-Agent Setup Guide

Visual guide showing exactly what your screen should look like.

---

## 🎯 The Setup You Need

**Important:** You don't need all 15 agents running at once! Start with 3 windows:

```
┌─────────────────────────────────────────────────────────────────┐
│  VS Code Window 1: ORCHESTRATOR (Main Control)                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Terminal                                                   │  │
│  │  D:\north-africa-toe-builder> npm run search "21st Panzer" │  │
│  │  D:\north-africa-toe-builder> npm run prepare parse ...    │  │
│  │  D:\north-africa-toe-builder> ls tasks/pending            │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  VS Code Window 2: DOCUMENT_PARSER AGENT                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Terminal                                                   │  │
│  │  D:\north-africa-toe-builder> npm run agent document_parser│  │
│  │  Agent document_parser watching for tasks...               │  │
│  │  Waiting for tasks...                                       │  │
│  │  Found task: task_123_parser_germany                        │  │
│  │  Processing...                                              │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Claude Code Chat (Sidebar)                                │  │
│  │  > Process task: tasks/in_progress/task_123...             │  │
│  │  [Agent extracts facts automatically]                       │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  VS Code Window 3: HISTORICAL_RESEARCH AGENT                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Terminal                                                   │  │
│  │  D:\north-africa-toe-builder> npm run agent historical_res │  │
│  │  Agent historical_research watching for tasks...           │  │
│  │  Waiting for tasks...                                       │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Claude Code Chat (Sidebar)                                │  │
│  │  [Ready for verification tasks]                             │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Exact Setup Steps

### Step 1: Main Orchestrator Window (Already Open)

**This is your current VS Code window:**

1. ✓ Already in: `D:\north-africa-toe-builder`
2. Open terminal if not open: `Terminal → New Terminal`
3. This is **Window 1 - your control center**

**What you do here:**
- Create tasks
- Search sources
- Monitor progress

---

### Step 2: Open document_parser Agent Window

1. **Open new VS Code window:**
   - Click: `File → New Window`
   - OR press: `Ctrl+Shift+N`

2. **Open project folder:**
   - Click: `File → Open Folder...`
   - Navigate to: `D:\north-africa-toe-builder`
   - Click: `Select Folder`

3. **Open terminal:**
   - Click: `Terminal → New Terminal`
   - OR press: `` Ctrl+` ``

4. **Start the agent:**
   ```bash
   npm run agent document_parser
   ```

5. **You should see:**
   ```
   Starting agent: document_parser
   Agent configuration loaded: document_parser
   Agent document_parser watching for tasks in: D:\north-africa-toe-builder\tasks\pending
   Checking every 2 seconds...
   Waiting for tasks...
   ```

6. ✓ **Keep this window open!** Agent is now watching for tasks.

---

### Step 3: Open historical_research Agent Window

1. **Open ANOTHER new VS Code window:**
   - Click: `File → New Window`
   - OR press: `Ctrl+Shift+N`

2. **Open project folder:**
   - Click: `File → Open Folder...`
   - Navigate to: `D:\north-africa-toe-builder`
   - Click: `Select Folder`

3. **Open terminal:**
   - Click: `Terminal → New Terminal`

4. **Start the agent:**
   ```bash
   npm run agent historical_research
   ```

5. **You should see:**
   ```
   Starting agent: historical_research
   Agent configuration loaded: historical_research
   Agent historical_research watching for tasks in: D:\north-africa-toe-builder\tasks\pending
   Checking every 2 seconds...
   Waiting for tasks...
   ```

6. ✓ **Keep this window open!** Agent is now watching for tasks.

---

### Step 4: Arrange Your Windows

**Recommended layout:**

**Monitor 1 (or left side):**
- Window 1: Orchestrator (full screen or top half)

**Monitor 2 (or right side):**
- Window 2: document_parser (top half)
- Window 3: historical_research (bottom half)

**OR if you have one monitor:**
- Window 1: Left side (orchestrator)
- Window 2 & 3: Right side, split vertically

---

## 🚀 Test It Out!

### Step 1: Create a Task (Window 1)

**In your Orchestrator window, paste this:**

```bash
npm run prepare parse \
  --source "D:\north-africa-toe-builder\Resource Documents\tessin-georg-verbande-und-truppen-der-deutschen-wehrmacht-und-waffen-ss\Tessin, Georg - Verbände und Truppen der deutschen Wehrmacht und Waffen-SS - Band 08_hocr_searchtext.txt.gz" \
  --type "Tessin Band 08" \
  --nation Germany \
  --quarter 1941-Q2 \
  --search "21.*Panzer" \
  --context 100
```

**Press Enter. You should see:**
```
Preparing source: Band 08_hocr_searchtext.txt.gz
Extracting gzipped file...
Searching for: "21.*Panzer"
Found 3 relevant section(s)

✓ Task created: task_1728499200_parser_germany
✓ Task file: tasks/pending/task_1728499200_parser_germany.json
✓ Content length: 8542 characters

Next steps:
1. Terminal 2: npm run agent document_parser (already running!)
2. VS Code Window 2: Process the task in Claude Code chat
```

### Step 2: Watch Window 2 (document_parser)

**Switch to Window 2 - document_parser agent**

**Within 2 seconds, you should see:**
```
Waiting for tasks...
Found task: task_1728499200_parser_germany
Processing task for agent: document_parser

=== NEW TASK FOR AGENT ===
Agent: document_parser
Task ID: task_1728499200_parser_germany

The task file has been moved to in_progress.
Please process this task using Claude Code chat.

Prompt saved to: tasks/in_progress/task_1728499200_parser_germany_prompt.txt

Copy this prompt to Claude Code chat to process the task.
===============================
```

### Step 3: Open Claude Code Chat (Window 2)

**In Window 2 (document_parser):**

1. **Open Claude Code chat:**
   - Press `Ctrl+Shift+P`
   - Type: `Claude Code: Open Chat`
   - Press Enter
   - OR click the Claude Code icon in the sidebar

2. **In the chat, type:**
   ```
   Read the task file at tasks/in_progress/task_1728499200_parser_germany.json and process it according to the document_parser agent prompt.
   ```

3. **I (Claude Code) will automatically:**
   - ✓ Read the task file
   - ✓ Load the source content
   - ✓ Apply the enhanced document_parser prompt
   - ✓ Extract all facts with citations
   - ✓ Output structured JSON

4. **Copy my JSON response and save it:**
   ```bash
   # Create the output file (I'll tell you the exact filename)
   # Save my JSON response to: outputs/task_1728499200_parser_germany_output.json
   ```

### Step 4: Move Task to Completed (Window 2 terminal)

```bash
mv tasks/in_progress/task_1728499200_parser_germany.json tasks/completed/
```

**Done!** ✓ Facts extracted from Tessin Band 08.

---

## 🔄 Workflow Diagram

```
WINDOW 1 (Orchestrator)
    │
    │ npm run prepare parse
    │ → Creates task in tasks/pending/
    │
    ↓
WINDOW 2 (document_parser agent)
    │
    │ Detects task automatically (checks every 2 sec)
    │ Moves to tasks/in_progress/
    │
    │ YOU: Open Claude Code chat
    │ YOU: "Process task in tasks/in_progress/..."
    │
    │ CLAUDE: Reads task, processes with enhanced prompt
    │ CLAUDE: Returns structured JSON with facts
    │
    │ YOU: Save to outputs/task_XXX_output.json
    │ YOU: Move task to tasks/completed/
    │
    ↓
WINDOW 1 (Orchestrator)
    │
    │ npm run prepare research
    │ → Creates verification task with additional sources
    │
    ↓
WINDOW 3 (historical_research agent)
    │
    │ Detects task automatically
    │ YOU: Process in Claude Code chat
    │ CLAUDE: Verifies facts, resolves conflicts
    │ YOU: Save verified_facts.json
    │
    ↓
DONE! Ready for Phase 2
```

---

## ✅ What Success Looks Like

### Window 1 (Orchestrator):
```bash
D:\north-africa-toe-builder> ls tasks/completed
task_1728499200_parser_germany.json
task_1728499300_research.json

D:\north-africa-toe-builder> ls outputs
task_1728499200_parser_germany_output.json      # Raw facts
task_1728499300_research_output.json            # Verified facts
```

### Window 2 (document_parser):
```
Agent document_parser watching for tasks...
Waiting for tasks...
Found task: task_XXX
Processing...
[Task completed via Claude Code chat]
Waiting for tasks...
```

### Window 3 (historical_research):
```
Agent historical_research watching for tasks...
Waiting for tasks...
Found task: task_YYY
Processing...
[Task completed via Claude Code chat]
Waiting for tasks...
```

---

## 🎨 Color Coding Your Windows

**Help identify windows quickly:**

**Window 1 (Orchestrator):** Change terminal color to **Green**
- Terminal settings → Profile → Colors → Foreground: Green

**Window 2 (document_parser):** Change terminal color to **Blue**
- Terminal settings → Profile → Colors → Foreground: Blue

**Window 3 (historical_research):** Change terminal color to **Yellow**
- Terminal settings → Profile → Colors → Foreground: Yellow

---

## 📝 Window Labels

**Add to your VS Code window titles:**

1. Open settings: `Ctrl+,`
2. Search: `window.title`
3. Set custom titles:
   - Window 1: `ORCHESTRATOR - ${rootName}`
   - Window 2: `DOCUMENT_PARSER - ${rootName}`
   - Window 3: `HISTORICAL_RESEARCH - ${rootName}`

---

## 🆘 Quick Troubleshooting

**Agent not detecting tasks?**
```bash
# Check agent is running (you should see "Waiting for tasks...")
# Check task file exists:
ls tasks/pending/task_*.json

# Check agent_id matches:
cat tasks/pending/task_XXX.json | grep agent_id
```

**Claude Code chat not available?**
- Make sure you're in a VS Code window (not terminal app)
- Press `Ctrl+Shift+P` → `Claude Code: Open Chat`
- Or click Claude Code icon in left sidebar

**Task stuck?**
```bash
# Move back to pending:
mv tasks/in_progress/task_XXX.json tasks/pending/

# Agent will pick it up again in 2 seconds
```

---

## 🎯 Quick Start Checklist

- [ ] Window 1: Main VS Code (already open)
- [ ] Window 2: New VS Code → Open folder → Start `npm run agent document_parser`
- [ ] Window 3: New VS Code → Open folder → Start `npm run agent historical_research`
- [ ] Window 1: Create task with `npm run prepare parse`
- [ ] Window 2: Task detected → Process in Claude Code chat
- [ ] Window 1: Create verification task with `npm run prepare research`
- [ ] Window 3: Task detected → Process in Claude Code chat
- [ ] Check `outputs/` folder for results ✓

**You're ready to start extracting!** 🚀

---

## Next: Add More Agents as Needed

**After Phase 1 works, add Phase 2 agents:**

4. **Window 4:** `npm run agent org_hierarchy`
5. **Window 5:** `npm run agent toe_template`
6. **Window 6:** `npm run agent unit_instantiation`

**Same process - each agent in its own VS Code window!**
