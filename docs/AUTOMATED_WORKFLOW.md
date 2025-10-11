# Automated Agent Workflow - Let the Agents Do the Work

This guide shows how to have your Phase 1 agents automatically extract and verify data from your source documents.

**Key Point:** YOU don't extract data - the AGENTS do it automatically!

---

## Overview

1. **You**: Tell the system which document and what to extract
2. **System**: Automatically loads the document and creates agent task
3. **document_parser agent**: Extracts all facts with citations
4. **historical_research agent**: Cross-references against additional sources
5. **You**: Get verified facts ready for Phase 2

---

## Quick Start: Extract German 21st Panzer Division

### Step 1: Find the Source Document

```bash
cd D:\north-africa-toe-builder

# Search for where 21st Panzer is mentioned
npm run search "21.*Panzer" -- --type german
```

**Output shows:**
```
Found in: Tessin Band 08
File: D:\north-africa-toe-builder\Resource Documents\tessin...\Band 08_hocr_searchtext.txt.gz
```

### Step 2: Prepare Task for document_parser Agent

```bash
# Let the system automatically extract and create the task
npm run prepare parse \
  --source "D:\north-africa-toe-builder\Resource Documents\tessin-georg-verbande-und-truppen-der-deutschen-wehrmacht-und-waffen-ss\Tessin, Georg - Verbände und Truppen der deutschen Wehrmacht und Waffen-SS - Band 08_hocr_searchtext.txt.gz" \
  --type "Tessin Band 08" \
  --nation Germany \
  --quarter 1941-Q2 \
  --search "21.*Panzer" \
  --context 100
```

**What happens automatically:**
1. ✓ System decompresses the .gz file
2. ✓ System searches for "21.*Panzer"
3. ✓ System extracts 100 lines of context around matches
4. ✓ System creates task file: `tasks/pending/task_xxx_parser_germany.json`
5. ✓ Ready for agent to process!

**Output:**
```
Preparing source: Band 08_hocr_searchtext.txt.gz
Document type: Tessin Band 08
Nation: Germany, Quarter: 1941-Q2
Extracting gzipped file...
Searching for: "21.*Panzer"
Found 3 relevant section(s)

✓ Task created: task_1728499200_parser_germany
✓ Task file: tasks/pending/task_1728499200_parser_germany.json
✓ Content length: 8542 characters
✓ Extracted sections for: "21.*Panzer"

Next steps:
1. Terminal 2: npm run agent document_parser
2. VS Code Window 2: Process the task in Claude Code chat
3. Agent will output: outputs/task_1728499200_parser_germany_output.json
```

### Step 3: Start document_parser Agent (Terminal 2)

```bash
# Terminal 2 - Start the agent
npm run agent document_parser
```

**What happens:**
```
Agent document_parser watching for tasks...
Found task: task_1728499200_parser_germany
Processing...
```

### Step 4: Agent Does All the Extraction Work (VS Code Window 2)

The agent runner will show you the full enhanced prompt in your Claude Code chat:

```
New task detected:

<role>You are an expert military historian specializing in WWII Table of Organization & Equipment (TO&E) analysis.</role>

<context>
<document_type>Tessin Band 08</document_type>
<nation>Germany</nation>
<time_period>1941-Q2</time_period>
<source_content>
--- Section 1 (lines 2458-2558) ---
21. Panzer-Division

Aufstellung: Februar 1941 in Nordafrika durch Umbenennung der 5. leichten Division

Kommandeur: Generalmajor Johann von Ravenstein (5.2.1941 - 29.11.1941)

Gliederung Mai 1941:
- Panzer-Regiment 5
  - I. Abteilung (Panzer III und IV)
  - II. Abteilung (Panzer II und III)
...
[Full extracted content automatically provided]
...
</source_content>
</context>

<task>
Extract ALL factual information about Germany military forces in 1941-Q2...
</task>

[Full enhanced prompt with examples and instructions]
```

**Agent responds with structured JSON** (automatically saved to outputs/):

```json
[
  {
    "fact_id": "cmd_001",
    "fact_type": "command",
    "data": {
      "unit": "21. Panzer-Division",
      "commander": "Johann von Ravenstein",
      "rank": "Generalmajor",
      "start_date": "1941-02-05",
      "end_date": "1941-11-29"
    },
    "source_citation": "Tessin Band 08, 21. Panzer-Division entry, lines 2458-2558",
    "confidence": 95,
    "extraction_notes": "Explicitly stated with exact dates"
  },
  ... [more facts automatically extracted]
]
```

**System automatically saves:**
- `outputs/task_1728499200_parser_germany_output.json` ✓
- Task moved to `tasks/completed/` ✓

---

### Step 5: Prepare Cross-Reference Task (Automated)

```bash
# Terminal 1 - Automatically prepare verification task
npm run prepare research \
  --raw-facts "outputs/task_1728499200_parser_germany_output.json" \
  --add-source "D:\north-africa-toe-builder\Resource Documents\tessin-georg-verbande-und-truppen-der-deutschen-wehrmacht-und-waffen-ss\Tessin, Georg - Verbände und Truppen der deutschen Wehrmacht und Waffen-SS - Band 03_hocr_searchtext.txt.gz:21.*Panzer"
```

**What happens automatically:**
1. ✓ System loads your raw_facts.json from document_parser
2. ✓ System decompresses Tessin Band 03
3. ✓ System searches for "21.*Panzer" in Band 03
4. ✓ System extracts relevant sections (10k chars max per source)
5. ✓ System creates research task with all sources combined
6. ✓ Ready for historical_research agent!

**Output:**
```
✓ Research task created: task_1728499300_research
✓ Cross-referencing 1 additional sources

Next steps:
1. Terminal 3: npm run agent historical_research
2. VS Code Window 3: Process the task in Claude Code chat
```

### Step 6: Start historical_research Agent (Terminal 3)

```bash
# Terminal 3
npm run agent historical_research
```

**Agent automatically:**
- ✓ Reads your raw_facts from Step 4
- ✓ Compares against Tessin Band 03 sections
- ✓ Identifies VERIFIED/CONFIRMED/DISPUTED facts
- ✓ Resolves conflicts
- ✓ Updates confidence levels
- ✓ Outputs `verified_facts.json`

---

## Complete Example: Italian Sirte Division (1940-Q2)

### Extract from British Army Lists (PRIMARY SOURCE)

```bash
# Step 1: Find which quarterly list to use
npm run search "Sirte" -- --type british

# Step 2: Prepare extraction task
npm run prepare parse \
  --source "D:\north-africa-toe-builder\Resource Documents\Great Britain Ministery of Defense Books\armylistjun1940grea_hocr_searchtext.txt.gz" \
  --type "British Army List June 1940" \
  --nation Italy \
  --quarter 1940-Q2 \
  --search "Sirte.*Division" \
  --context 150

# Step 3: Start agent (Terminal 2)
npm run agent document_parser

# Step 4: Agent automatically extracts facts in VS Code Window 2

# Step 5: Cross-reference with TM 30-410
npm run prepare research \
  --raw-facts "outputs/task_xxx_output.json" \
  --add-source "D:\north-africa-toe-builder\Resource Documents\British_PRIMARY_SOURCES\TM30-410_text.txt:Italian.*division"

# Step 6: Start research agent (Terminal 3)
npm run agent historical_research

# Done! verified_facts.json ready for Phase 2
```

---

## Commands Reference

### Search Sources
```bash
# Find where a unit is mentioned
npm run search "unit name" -- --type <nation> --context 5 --max 20

Options:
  --type      british | german | us | all
  --context   Lines of context around matches
  --max       Maximum results to show
```

### Prepare Extraction Task
```bash
npm run prepare parse \
  --source "full/path/to/source.txt.gz" \
  --type "Source description" \
  --nation "Germany|Britain|USA|Italy" \
  --quarter "YYYY-QX" \
  --search "search.*regex" \
  --context 100

What it does:
  ✓ Decompresses .gz files automatically
  ✓ Searches for your query
  ✓ Extracts relevant sections (not entire file)
  ✓ Creates agent task ready to process
```

### Prepare Verification Task
```bash
npm run prepare research \
  --raw-facts "outputs/task_xxx_output.json" \
  --add-source "path/to/source2.txt.gz:search term" \
  --add-source "path/to/source3.txt:different search"

What it does:
  ✓ Loads raw facts from document_parser
  ✓ Extracts relevant sections from additional sources
  ✓ Creates research task with all sources combined
```

### Start Agents
```bash
# Terminal 2
npm run agent document_parser

# Terminal 3
npm run agent historical_research

# Terminal 4
npm run agent org_hierarchy

# ... etc for other agents
```

---

## File Locations

**Your source documents:**
```
D:\north-africa-toe-builder\Resource Documents\
├── British_PRIMARY_SOURCES\
├── Great Britain Ministery of Defense Books\
├── tessin-georg-verbande...\
├── FM17-10_Armored_Force_1942.pdf
└── ...
```

**Agent tasks:**
```
tasks\
├── pending\          ← New tasks wait here
├── in_progress\      ← Agents working on these
└── completed\        ← Finished tasks
```

**Agent outputs:**
```
outputs\
├── task_xxx_parser_germany_output.json     ← Raw facts
└── task_yyy_research_output.json           ← Verified facts
```

---

## Typical Workflow

```
1. Search for unit:
   npm run search "unit" --type nation

2. Prepare extraction:
   npm run prepare parse --source "..." --nation X --quarter Y --search "unit"

3. Agent extracts (Terminal 2):
   npm run agent document_parser
   → VS Code Window 2: Agent does extraction
   → Output: raw_facts.json

4. Prepare verification:
   npm run prepare research --raw-facts "..." --add-source "..."

5. Agent verifies (Terminal 3):
   npm run agent historical_research
   → VS Code Window 3: Agent cross-references
   → Output: verified_facts.json

6. Build organization (Phase 2):
   Use verified_facts.json with org_hierarchy, toe_template, unit_instantiation agents
```

---

## Key Benefits

✅ **Agents do ALL extraction work** - not you!
✅ **Automatic decompression** of .gz files
✅ **Smart section extraction** - only relevant content sent to agents
✅ **Consistent JSON output** via enhanced prompts
✅ **Full source citations** with line numbers
✅ **Multi-source verification** automatic
✅ **True agent independence** - each in separate VS Code window

---

## Tips

1. **Start with PRIMARY sources** (Army Lists, Tessin, Field Manuals)
2. **Use specific search terms** to extract just what you need
3. **Adjust --context** if you need more/less surrounding text
4. **Chain tasks** - output of document_parser → input to historical_research
5. **Keep agents running** - they watch for new tasks automatically
6. **Check outputs/** folder for results

---

## Example: Process 5 German Panzer Divisions

```bash
# Search once
npm run search "Panzer.*Division" --type german --max 50 > panzer_locations.txt

# Prepare 5 extraction tasks (these run in parallel!)
for div in "15" "21" "90" "164" "10"; do
  npm run prepare parse \
    --source "tessin_band_08.txt.gz" \
    --type "Tessin Band 08" \
    --nation Germany \
    --quarter 1941-Q2 \
    --search "${div}.*Panzer"
done

# Start agent (processes all 5 tasks one by one)
npm run agent document_parser

# Agents automatically process all 5 divisions!
# Outputs: 5 × raw_facts.json files ready for verification
```

Your agents are now ready to process your entire source collection automatically! 🚀
