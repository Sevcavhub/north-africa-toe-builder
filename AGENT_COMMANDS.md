# Agent Command Reference Card

Quick reference for automated agent workflow.

---

## 🔍 Find Sources

```bash
# Search for unit in all sources
npm run search "21st Panzer"

# Search German sources only
npm run search "Rommel" -- --type german

# Search British sources with more context
npm run search "7th Armoured" -- --type british --context 10
```

---

## 📄 Extract Data (document_parser)

```bash
# Prepare extraction task (agents do the work!)
npm run prepare parse \
  --source "D:\north-africa-toe-builder\Resource Documents\tessin...\Band_08.txt.gz" \
  --type "Tessin Band 08" \
  --nation Germany \
  --quarter 1941-Q2 \
  --search "21.*Panzer" \
  --context 100

# Start agent (Terminal 2)
npm run agent document_parser
```

**Agent automatically:**
- ✓ Decompresses .gz files
- ✓ Extracts relevant sections
- ✓ Processes with enhanced prompts
- ✓ Outputs structured JSON with citations

**Result:** `outputs/task_xxx_parser_XXX_output.json`

---

## ✅ Verify Data (historical_research)

```bash
# Prepare verification task
npm run prepare research \
  --raw-facts "outputs/task_xxx_output.json" \
  --add-source "path/to/source2.txt.gz:search term"

# Start agent (Terminal 3)
npm run agent historical_research
```

**Agent automatically:**
- ✓ Cross-references multiple sources
- ✓ Identifies conflicts
- ✓ Updates confidence levels
- ✓ Outputs verified facts

**Result:** `outputs/task_yyy_research_output.json`

---

## 🏗️ Build Organization (Phase 2)

```bash
# Terminal 4: Build org hierarchy
npm run agent org_hierarchy

# Terminal 5: Create templates
npm run agent toe_template

# Terminal 6: Instantiate units
npm run agent unit_instantiation
```

---

## 📊 Quick Examples

### German 21st Panzer Division (1941-Q2)

```bash
# 1. Search
npm run search "21.*Panzer" -- --type german

# 2. Extract from Tessin
npm run prepare parse --source "tessin_band_08.txt.gz" --type "Tessin Band 08" --nation Germany --quarter 1941-Q2 --search "21.*Panzer"

# 3. Agent extracts (Terminal 2)
npm run agent document_parser

# 4. Verify with additional sources
npm run prepare research --raw-facts "outputs/task_xxx_output.json" --add-source "tessin_band_03.txt.gz:21.*Panzer"

# 5. Agent verifies (Terminal 3)
npm run agent historical_research

# Done! verified_facts.json → ready for Phase 2
```

### British 7th Armoured Division (1942-Q3)

```bash
# 1. Search British Army Lists
npm run search "7th.*Armoured" -- --type british

# 2. Extract from July 1942 Army List
npm run prepare parse --source "armylistjul1942grea.txt.gz" --type "British Army List July 1942" --nation Britain --quarter 1942-Q3 --search "7th.*Armoured"

# 3. Agent extracts (Terminal 2)
npm run agent document_parser

# 4. Verify with TM 30-410 and Desert Rats
npm run prepare research --raw-facts "outputs/task_xxx_output.json" --add-source "TM30-410_text.txt:armoured.*division"

# 5. Agent verifies (Terminal 3)
npm run agent historical_research
```

---

## 🚀 Batch Processing

**Process 5 units at once:**
```bash
# Prepare 5 tasks
for unit in "15.*Panzer" "21.*Panzer" "90.*leichte" "164.*Division" "Ariete"; do
  npm run prepare parse --source "source.txt.gz" --type "Source" --nation Germany --quarter 1941-Q2 --search "$unit"
done

# Agent processes all 5 automatically!
npm run agent document_parser
```

---

## 📁 File Locations

```
Resource Documents\          ← Your sources (Tessin, Army Lists, FMs)
tasks\pending\               ← New tasks (agents pick these up)
tasks\completed\             ← Finished tasks
outputs\                     ← Agent outputs (raw_facts, verified_facts)
```

---

## 💡 Remember

1. **Agents do ALL the work** - you just point them to sources!
2. **Use --search** to extract only relevant sections
3. **PRIMARY sources first** (Army Lists, Tessin, Field Manuals)
4. **Verify with 2+ sources** for important facts
5. **Keep agents running** - they watch for new tasks
6. **Each agent in separate VS Code window** = true independence

---

## 📖 Full Documentation

- `AUTOMATED_WORKFLOW.md` - Complete automated workflow guide
- `SOURCE_WORKFLOW.md` - Source document details
- `FILE_BASED_SETUP.md` - Multi-terminal setup
- `sources/sources_catalog.json` - All source metadata

---

## Common Commands

```bash
# Search sources
npm run search "query" -- --type <nation>

# Prepare extraction
npm run prepare parse --source "..." --search "..."

# Prepare verification
npm run prepare research --raw-facts "..." --add-source "..."

# Start agents (separate terminals)
npm run agent document_parser        # Terminal 2
npm run agent historical_research    # Terminal 3
npm run agent org_hierarchy          # Terminal 4
npm run agent toe_template           # Terminal 5
npm run agent unit_instantiation     # Terminal 6

# Check status
ls tasks/pending
ls outputs
```

Ready to process your sources! 🎯
