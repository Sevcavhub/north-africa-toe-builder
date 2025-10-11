# Quick Start - Using Claude Code Subscription (No API Tokens!)

This guide gets you up and running using your Claude Max subscription instead of API tokens.

## 1. Generate Prompts (One Command)

```bash
npm run start:claude
```

This command will:
- Load your North Africa project configuration
- Search for source documents automatically (Tessin, Army Lists, Field Manuals)
- Extract relevant content for each unit
- Generate AI prompts with source material included
- Save everything to `data/output/session_XXXXX/`

**Output:**
```
✅ ALL PROMPTS GENERATED

Total prompts: 47
Location: data/output/session_1234567890/prompts/

📋 INDEX FILE: data/output/session_1234567890/PROMPT_INDEX.json
📖 GUIDE: data/output/session_1234567890/PROCESSING_GUIDE.md
```

## 2. Open the Processing Guide

```bash
# Open the guide in your editor
code data/output/session_XXXXX/PROCESSING_GUIDE.md
```

Or view it in terminal:
```bash
cat data/output/session_XXXXX/PROCESSING_GUIDE.md | less
```

## 3. Process First Prompt

### Step 1: Read the prompt file
```bash
cat data/output/session_XXXXX/prompts/1_parse_Germany_15th_Panzer_Division_prompt.txt
```

### Step 2: Copy the entire prompt

### Step 3: Paste it into this Claude Code chat

You'll see something like:
```
You are an expert military historian specializing in WWII Table of Organization & Equipment (TO&E) analysis.

Task: Extract ALL factual information about Germany military forces in 1941-Q2.

For each fact extracted, provide:
1. The fact itself
2. Source citation (page number, section)
3. Confidence level (0-100)
4. Category (personnel|equipment|organization|command)

... [source document content included] ...

Output format: JSON array of facts
```

### Step 4: Wait for Claude's JSON response

Claude Code (the AI) will automatically process the prompt and return structured JSON like:
```json
[
  {
    "fact_id": "cmd_001",
    "fact_type": "command",
    "data": {
      "unit": "15. Panzer-Division",
      "commander": "Heinrich von Prittwitz und Gaffron",
      "rank": "Generalmajor"
    },
    "source_citation": "Tessin Band 08, 15. Panzer-Division entry, lines 1250-1350",
    "confidence": 95,
    "extraction_notes": "Explicitly stated with exact dates"
  },
  ... more facts ...
]
```

### Step 5: Save Claude's response

```bash
# Method 1: Copy and paste into file
cat > data/output/session_XXXXX/responses/1_parse_Germany_15th_Panzer_Division_response.json <<'EOF'
[paste Claude's JSON here]
EOF

# Method 2: Use your editor
code data/output/session_XXXXX/responses/1_parse_Germany_15th_Panzer_Division_response.json
# Paste Claude's JSON and save
```

### Step 6: Move to next prompt

Repeat steps 1-5 for prompt #2, #3, etc.

## 4. Check Progress

At any time, check how many responses you've saved:

```bash
ls -1 data/output/session_XXXXX/responses/*.json | wc -l
```

Expected: Should match the number of prompts generated.

## 5. Alternative: Interactive Mode

Instead of manually managing files, use interactive mode:

```bash
npm run start:claude:interactive
```

This displays prompts one-by-one in the terminal. After each prompt:
1. Claude Code processes it in chat
2. You save the response
3. Press Enter for the next prompt

## Benefits

✅ **Uses your Claude Max subscription** - no API token consumption
✅ **AI does all extraction** - no manual data entry
✅ **No separate terminals** - everything in one Claude Code session
✅ **Resume anytime** - prompts saved to files, process at your pace
✅ **Full automation** - just paste prompts, Claude does the rest

## Tips

1. **Process in batches**: Do 5-10 units at a time, take breaks
2. **Keep Claude Code open**: Minimize context switching
3. **Verify JSON**: Make sure Claude's response is valid JSON before saving
4. **Use the guide**: The PROCESSING_GUIDE.md has all file paths ready
5. **Check confidence**: Review any facts with confidence < 75%

## Troubleshooting

### "Source not found" errors
- Check that your `Resource Documents` directory path is correct in `projects/north_africa_campaign.json`
- Verify source files exist and are readable

### Claude returns text instead of JSON
- Remind Claude: "Please provide ONLY valid JSON, no explanatory text"
- Or manually extract the JSON from code blocks

### Invalid JSON errors
- Use a JSON validator: `cat response.json | jq .`
- Fix syntax errors and re-save

## Next Steps

After completing all Phase 1 prompts (document_parser):
1. Run Phase 2 to generate historical_research prompts
2. Cross-reference data from multiple sources
3. Continue through all 6 phases

For now, focus on Phase 1 - that's where the bulk of data extraction happens!

## Need Help?

- See `CLAUDE.md` for complete documentation
- See `docs/project_context.md` for project architecture
- See `docs/SOURCE_WORKFLOW.md` for source document details
