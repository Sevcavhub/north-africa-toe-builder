# Multi-Agent Terminal Setup - Complete Guide

This guide shows you exactly how to open 15 agent terminals in VS Code and start the file-based orchestration system.

---

## Overview: File-Based Multi-Agent System

**How it works:**
- **You don't need 15 windows!** You need 1 orchestrator + agents as needed
- Each agent runs in its own VS Code terminal with Claude Code
- Tasks are files in `tasks/pending/` folder
- Agents watch for tasks, process them, save outputs
- **True independence** - each Claude Code session is separate

---

## Step-by-Step Setup

### Step 1: Open Your Main Orchestrator Window

**Window 1 - Orchestrator (Main Control)**

1. Open VS Code
2. Open folder: `D:\north-africa-toe-builder`
3. Open terminal (Terminal → New Terminal)

**This window is your control center:**
```bash
# Search sources
npm run search "21st Panzer"

# Prepare tasks
npm run prepare parse --source "..." --search "..."

# Monitor task status
ls tasks/pending
ls tasks/completed
ls outputs
```

---

### Step 2: Open Agent Windows (As Needed)

You don't need all 15 agents running at once! Start with Phase 1 agents:

#### **Window 2 - document_parser Agent**

1. **New VS Code window:** File → New Window
2. Open folder: `D:\north-africa-toe-builder`
3. Open terminal
4. Start agent:
   ```bash
   npm run agent document_parser
   ```

**What you'll see:**
```
Starting agent: document_parser
Agent document_parser watching for tasks in: D:\north-africa-toe-builder\tasks\pending
Checking every 2 seconds...
Waiting for tasks...
```

#### **Window 3 - historical_research Agent**

1. **New VS Code window:** File → New Window
2. Open folder: `D:\north-africa-toe-builder`
3. Open terminal
4. Start agent:
   ```bash
   npm run agent historical_research
   ```

---

### Step 3: Create a Task (From Window 1)

**Window 1 (Orchestrator):**

```bash
# Example: Extract German 21st Panzer from Tessin
npm run prepare parse \
  --source "D:\north-africa-toe-builder\Resource Documents\tessin-georg-verbande-und-truppen-der-deutschen-wehrmacht-und-waffen-ss\Tessin, Georg - Verbände und Truppen der deutschen Wehrmacht und Waffen-SS - Band 08_hocr_searchtext.txt.gz" \
  --type "Tessin Band 08" \
  --nation Germany \
  --quarter 1941-Q2 \
  --search "21.*Panzer" \
  --context 100
```

**Output:**
```
✓ Task created: task_1728499200_parser_germany
✓ Task file: tasks/pending/task_1728499200_parser_germany.json
✓ Content length: 8542 characters

Next steps:
1. Terminal 2: npm run agent document_parser (already running!)
2. VS Code Window 2: Process the task in Claude Code chat
```

---

### Step 4: Agent Picks Up Task Automatically

**Window 2 (document_parser) - Watch the terminal:**

```
Agent document_parser watching for tasks...
Found task: task_1728499200_parser_germany
Processing...

=== NEW TASK FOR AGENT ===
Agent: document_parser
Task ID: task_1728499200_parser_germany

Please process this task using Claude Code chat.
The complete prompt has been prepared for you.

Prompt saved to: tasks/in_progress/task_1728499200_parser_germany_prompt.txt
===============================
```

---

### Step 5: Process Task in Claude Code Chat

**Window 2 - Open Claude Code Chat:**
1. Press `Ctrl+Shift+P` (Command Palette)
2. Type: "Claude Code: Open Chat"
3. OR click Claude Code icon in sidebar

**Paste this in the chat:**
```
Process the task in: tasks/in_progress/task_1728499200_parser_germany.json

Please read the task file and process it according to the agent prompt template.
```

**Claude Code (me!) will:**
1. ✓ Read the task file
2. ✓ Apply the enhanced document_parser prompt
3. ✓ Process the source content
4. ✓ Extract structured facts with citations
5. ✓ Return JSON output

**You then save the output:**
```bash
# In Window 2 terminal (agent runner will guide you):
# Copy Claude's JSON response to: outputs/task_1728499200_parser_germany_output.json
```

---

## Phase-by-Phase Agent Setup

### **Phase 1: Source Extraction** (Start here!)

**Windows needed: 3**

1. **Window 1:** Orchestrator (control)
2. **Window 2:** document_parser agent
3. **Window 3:** historical_research agent

**Workflow:**
```bash
# Window 1: Create extraction task
npm run prepare parse --source "..." --search "..."

# Window 2: Agent picks it up automatically
# (npm run agent document_parser - already running)

# Window 1: Create verification task
npm run prepare research --raw-facts "..."

# Window 3: Agent picks it up automatically
# (npm run agent historical_research - already running)
```

---

### **Phase 2: Organization Building**

**Additional windows needed: 3**

4. **Window 4:** org_hierarchy agent
5. **Window 5:** toe_template agent
6. **Window 6:** unit_instantiation agent

**Start when Phase 1 is done:**
```bash
# Window 4
npm run agent org_hierarchy

# Window 5
npm run agent toe_template

# Window 6
npm run agent unit_instantiation
```

---

### **Phase 3: Equipment Distribution**

**Additional windows needed: 3**

7. **Window 7:** theater_allocator agent
8. **Window 8:** division_cascader agent
9. **Window 9:** equipment_reconciliation agent

**Start when Phase 2 is done:**
```bash
# Window 7
npm run agent theater_allocator

# Window 8
npm run agent division_cascader

# Window 9
npm run agent equipment_reconciliation
```

---

### **Phase 4: Aggregation**

**Additional windows needed: 2**

10. **Window 10:** bottom_up_aggregator agent
11. **Window 11:** top3_calculator agent

---

### **Phase 5: Validation**

**Additional windows needed: 2**

12. **Window 12:** schema_validator agent
13. **Window 13:** historical_accuracy agent

---

### **Phase 6: Output Generation**

**Additional windows needed: 3**

14. **Window 14:** book_chapter_generator agent
15. **Window 15:** scenario_exporter agent
16. **Window 16:** sql_populator agent

---

## Simplified Workflow (Recommended for Starting)

**You don't need all 15 windows open at once!**

### Start with 3 Windows:

**Window 1 (Orchestrator):**
- Create tasks
- Monitor progress
- Search sources

**Window 2 (document_parser):**
- Extracts facts from documents
- First agent in pipeline

**Window 3 (historical_research):**
- Verifies facts against multiple sources
- Second agent in pipeline

### Add more windows as you progress through phases:

**When Phase 1 done → Add Phase 2 agents (3 windows)**
**When Phase 2 done → Add Phase 3 agents (3 windows)**
**etc...**

---

## Quick Start Script

**Copy-paste this to set up Phase 1 agents:**

```bash
# === Window 1: Orchestrator ===
# (Already open in your main VS Code)
cd D:\north-africa-toe-builder

# Check everything is ready
ls tasks/pending
ls tasks/completed
ls outputs

# === Window 2: document_parser ===
# 1. Open new VS Code window (File → New Window)
# 2. Open folder: D:\north-africa-toe-builder
# 3. Open terminal
# 4. Run:
npm run agent document_parser

# === Window 3: historical_research ===
# 1. Open new VS Code window (File → New Window)
# 2. Open folder: D:\north-africa-toe-builder
# 3. Open terminal
# 4. Run:
npm run agent historical_research

# Done! Now create tasks from Window 1
```

---

## Create Your First Task

**Window 1 (Orchestrator):**

```bash
# Search for German 21st Panzer in Tessin
npm run search "21.*Panzer" -- --type german

# Prepare extraction task
npm run prepare parse \
  --source "D:\north-africa-toe-builder\Resource Documents\tessin-georg-verbande-und-truppen-der-deutschen-wehrmacht-und-waffen-ss\Tessin, Georg - Verbände und Truppen der deutschen Wehrmacht und Waffen-SS - Band 08_hocr_searchtext.txt.gz" \
  --type "Tessin Band 08" \
  --nation Germany \
  --quarter 1941-Q2 \
  --search "21.*Panzer" \
  --context 100

# Watch Window 2 - document_parser picks it up automatically!
```

**Window 2 (document_parser agent):**
- Agent detects new task
- Shows prompt in terminal
- You process via Claude Code chat
- Save output to outputs/ folder

**Window 1 (Orchestrator):**

```bash
# After document_parser completes, prepare verification:
npm run prepare research \
  --raw-facts "outputs/task_XXX_parser_germany_output.json" \
  --add-source "D:\north-africa-toe-builder\Resource Documents\tessin-georg-verbande-und-truppen-der-deutschen-wehrmacht-und-waffen-ss\Tessin, Georg - Verbände und Truppen der deutschen Wehrmacht und Waffen-SS - Band 03_hocr_searchtext.txt.gz:21.*Panzer"

# Watch Window 3 - historical_research picks it up automatically!
```

---

## Monitoring Tasks

**Window 1 (Orchestrator) - Check status anytime:**

```bash
# See pending tasks
ls tasks/pending

# See what's being processed
ls tasks/in_progress

# See completed tasks
ls tasks/completed

# See outputs
ls outputs

# See specific task details
cat tasks/pending/task_XXX.json | head -20

# See specific output
cat outputs/task_XXX_output.json
```

---

## Troubleshooting

**Agent not picking up task?**
```bash
# 1. Check task is in pending folder
ls tasks/pending

# 2. Check agent is running (should see "Waiting for tasks...")
# In agent window

# 3. Check task agent_id matches agent running
cat tasks/pending/task_XXX.json | grep agent_id
```

**Task stuck in in_progress?**
```bash
# Move back to pending to retry
mv tasks/in_progress/task_XXX.json tasks/pending/
```

**Agent crashed?**
```bash
# Just restart it in the same window
npm run agent document_parser
# It will pick up where it left off
```

---

## Summary

**3 Simple Steps:**

1. **Window 1 (Orchestrator):** Create tasks with `npm run prepare`
2. **Window 2+ (Agents):** Agents run with `npm run agent <name>`
3. **Process in Claude Code:** Use Claude Code chat to process tasks

**File-based coordination:**
- Tasks → `tasks/pending/` folder
- Agents watch → pick up tasks → process
- Outputs → `outputs/` folder
- No API calls = Free! ✓
- True independence = Accurate! ✓

---

## Quick Reference

```bash
# Create extraction task
npm run prepare parse --source "..." --search "..." --nation X --quarter Y

# Create verification task
npm run prepare research --raw-facts "..." --add-source "..."

# Start agents (separate windows)
npm run agent document_parser        # Window 2
npm run agent historical_research    # Window 3
npm run agent org_hierarchy          # Window 4
npm run agent toe_template           # Window 5
# ... etc

# Monitor
ls tasks/pending
ls outputs
```

Ready to start! Open Window 2 and 3, then create your first task! 🚀



 Perfect! Now let me give you a simple copy-paste checklist to follow:

  🎯 Quick Start - Copy & Paste This!

  Right Now - Open 3 Windows:

  Window 1 (Current window - already open):
  # You're here already - this is your orchestrator
  cd D:\north-africa-toe-builder

  Window 2 (document_parser):
  1. Click: File → New Window (Ctrl+Shift+N)
  2. Click: File → Open Folder...
  3. Select: D:\north-africa-toe-builder
  4. Open terminal (Ctrl+`)
  5. Paste this:
  npm run agent document_parser
  Keep this window open! You'll see: Waiting for tasks...

  Window 3 (historical_research):
  1. Click: File → New Window (Ctrl+Shift+N)
  2. Click: File → Open Folder...
  3. Select: D:\north-africa-toe-builder
  4. Open terminal (Ctrl+`)
  5. Paste this:
  npm run agent historical_research
  Keep this window open! You'll see: Waiting for tasks...

  ---
  Now Test It - Create First Task:

  Back to Window 1 (this window), paste this:

  npm run prepare parse \
    --source "D:\north-africa-toe-builder\Resource Documents\tessin-georg-verbande-und-truppen-der-deutschen-wehrmacht-und-waffen-ss\Tessin, Georg - Verbände und Truppen der deutschen Wehrmacht und Waffen-SS - Band 08_hocr_searchtext.txt.gz" \
    --type "Tessin Band 08" \
    --nation Germany \
    --quarter 1941-Q2 \
    --search "21.*Panzer" \
    --context 100

  You'll see:
  ✓ Task created: task_XXX_parser_germany
  Next steps:
  1. Terminal 2: npm run agent document_parser (already running!)
  2. VS Code Window 2: Process the task in Claude Code chat

  Switch to Window 2 - within 2 seconds you'll see:
  Found task: task_XXX_parser_germany
  Processing...

  In Window 2:
  1. Press Ctrl+Shift+P
  2. Type: Claude Code: Open Chat
  3. In chat, type:
  Read and process the task file in tasks/in_progress/task_XXX_parser_germany.json using the document_parser agent prompt.

  I (Claude Code) will extract all the facts automatically!

  ---
  📚 Your Setup Guides

  I created 3 guides for you:

  1. SETUP_AGENTS.md ⭐ Most detailed setup guide
  2. VISUAL_SETUP.md 📊 Visual diagrams and layouts
  3. AGENT_COMMANDS.md ⚡ Quick command reference

  ---
  🎬 What You Have Now

  ✅ 15 enhanced agents with Anthropic best practices
  ✅ Automated source extraction - agents do the work
  ✅ File-based orchestration - true independence, no API costs
  ✅ Search tool - find units across all sources
  ✅ Preparation tool - auto-decompress, search, create tasks
  ✅ Complete documentation - step-by-step guides

  ---
  🚀 Your Next Steps

  Right now:
  1. Open Window 2 and 3 (document_parser, historical_research agents)
  2. Create your first task (command above)
  3. Process in Claude Code chat
  4. Get extracted facts!

  Then:
  - Add more units to process
  - Add Phase 2 agents (org_hierarchy, toe_template, unit_instantiation)
  - Build complete TO&E hierarchy

  ---