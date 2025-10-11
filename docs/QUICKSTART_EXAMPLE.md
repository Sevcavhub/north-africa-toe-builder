# Quick Start Example: German 21st Panzer Division (1941-Q2)

This guide walks through a complete end-to-end example of extracting and verifying TO&E data for the German 21st Panzer Division in North Africa, May 1941.

## Prerequisites

1. Sources are in `D:\north-africa-toe-builder\Resource Documents\`
2. File-based orchestration system is set up (see `FILE_BASED_SETUP.md`)
3. 6 VS Code windows open with separate Claude Code sessions

---

## Step 1: Search for Source Material

**Terminal 1 (Orchestrator):**
```bash
cd D:\north-africa-toe-builder
npm run search "21.*Panzer" -- --type german --context 5
```

**What you'll see:**
```
Searching sources for: "21.*Panzer"
Resource directory: D:\north-africa-toe-builder\Resource Documents\

Found results in:
- Tessin Band 03: Afrika formations
- Tessin Band 08: Panzer divisions

[Result 1] Tessin Band 08:1245
21. Panzer-Division
Aufstellung: 1941 in Nordafrika aus der 5. leichten Division
Kommandeur: Generalmajor Johann von Ravenstein (Feb 1941 - Nov 1941)
...
```

**Action:** Copy the relevant excerpts from Tessin for use in document_parser.

---

## Step 2: Extract Facts from Primary Source

**Terminal 2 (document_parser agent):**

Create task file:
```bash
cd D:\north-africa-toe-builder

cat > tasks/pending/task_001_parse_21pz.json << 'EOF'
{
  "task_id": "task_001_parse_21pz",
  "agent_id": "document_parser",
  "inputs": {
    "source_content": "21. Panzer-Division\n\nAufstellung: Februar 1941 in Nordafrika durch Umbenennung der 5. leichten Division\n\nKommandeur: Generalmajor Johann von Ravenstein (5.2.1941 - 29.11.1941)\n\nGliederung Mai 1941:\n- Panzer-Regiment 5\n  - I. Abteilung (Panzer III und IV)\n  - II. Abteilung (Panzer II und III)\n- Schützen-Regiment 104\n  - I. Bataillon\n  - II. Bataillon\n- Artillerie-Regiment 155\n  - I. Abteilung (10,5 cm leFH 18)\n  - II. Abteilung (10,5 cm leFH 18)\n- Panzerjäger-Abteilung 39\n- Aufklärungs-Abteilung 3\n- Pionier-Bataillon 200\n- Nachrichten-Abteilung 200\n\nStärke: ca. 12.500 Mann\n\nPanzerbestand Mai 1941:\n- Panzer II: 45\n- Panzer III (kurz): 71\n- Panzer III (lang): 20\n- Panzer IV (kurz): 20\n- Gesamt: 156 Panzer",
    "document_type": "Tessin Wehrmacht Encyclopedia Band 08",
    "nation": "Germany",
    "quarter": "1941-Q2"
  },
  "created_at": "2025-10-09T14:30:00Z",
  "status": "pending"
}
EOF
```

**Terminal 2 - Start agent runner:**
```bash
npm run agent document_parser
```

**Agent runner output:**
```
Agent document_parser watching for tasks...
Found task: task_001_parse_21pz
Processing...
```

**VS Code Window 2 (document_parser session):**

Claude Code will detect the task and show you the prompt. In the chat, you'll see:

```
New task from agent_runner:

<role>You are an expert military historian specializing in WWII Table of Organization & Equipment (TO&E) analysis.</role>

<context>
<document_type>Tessin Wehrmacht Encyclopedia Band 08</document_type>
<nation>Germany</nation>
<time_period>1941-Q2</time_period>
<source_content>
21. Panzer-Division
[... full source content ...]
</source_content>
</context>

<task>
Extract ALL factual information about Germany military forces in 1941-Q2...
</task>
```

**Your response (paste into VS Code chat):**

Acknowledge and provide the extraction in JSON format. The agent prompt will guide you through the exact format needed.

**Example output (save to file):**
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
    "source_citation": "Tessin Band 08, 21. Panzer-Division entry",
    "confidence": 95,
    "extraction_notes": "Explicitly stated with exact dates"
  },
  {
    "fact_id": "org_001",
    "fact_type": "organization",
    "data": {
      "unit": "21. Panzer-Division",
      "formation_date": "1941-02",
      "formed_from": "5. leichte Division (renamed)",
      "theater": "North Africa"
    },
    "source_citation": "Tessin Band 08",
    "confidence": 95,
    "extraction_notes": "Formation history clearly documented"
  },
  {
    "fact_id": "org_002",
    "fact_type": "organization",
    "data": {
      "unit": "21. Panzer-Division",
      "subordinates": [
        "Panzer-Regiment 5",
        "Schützen-Regiment 104",
        "Artillerie-Regiment 155",
        "Panzerjäger-Abteilung 39",
        "Aufklärungs-Abteilung 3",
        "Pionier-Bataillon 200",
        "Nachrichten-Abteilung 200"
      ]
    },
    "source_citation": "Tessin Band 08, Gliederung Mai 1941",
    "confidence": 95,
    "extraction_notes": "Complete organizational structure listed"
  },
  {
    "fact_id": "per_001",
    "fact_type": "personnel",
    "data": {
      "unit": "21. Panzer-Division",
      "total_strength": 12500,
      "strength_qualifier": "approximately"
    },
    "source_citation": "Tessin Band 08, Stärke ca. 12.500 Mann",
    "confidence": 85,
    "extraction_notes": "Approximate figure indicated by 'ca.'"
  },
  {
    "fact_id": "eq_001",
    "fact_type": "equipment",
    "data": {
      "unit": "21. Panzer-Division",
      "date": "1941-05",
      "equipment_type": "tanks",
      "breakdown": [
        {"type": "Panzer II", "count": 45},
        {"type": "Panzer III (short)", "count": 71},
        {"type": "Panzer III (long)", "count": 20},
        {"type": "Panzer IV (short)", "count": 20}
      ],
      "total_tanks": 156
    },
    "source_citation": "Tessin Band 08, Panzerbestand Mai 1941",
    "confidence": 90,
    "extraction_notes": "Specific tank counts with variant details"
  }
]
```

**Save output:**
```bash
# Agent runner will save automatically to:
outputs/task_001_parse_21pz_output.json

# Move task to completed:
mv tasks/in_progress/task_001_parse_21pz.json tasks/completed/
```

---

## Step 3: Cross-Reference with Additional Sources

**Terminal 1 (Orchestrator):**

Search for additional verification sources:
```bash
# Search for 21st Panzer in other sources
npm run search "von Ravenstein" -- --type german
npm run search "Panzer.*Regiment.*5" -- --type german
```

**Gather web sources:**
1. Feldgrau.com: http://feldgrau.com/21pzdiv.html
2. Niehorster.org: Afrika Korps OOB May 1941
3. RommelsRiposte.com: 21st Panzer tank allocations

**Terminal 3 (historical_research agent):**

Create verification task:
```bash
cat > tasks/pending/task_002_verify_21pz.json << 'EOF'
{
  "task_id": "task_002_verify_21pz",
  "agent_id": "historical_research",
  "inputs": {
    "raw_facts": "[paste output from task_001]",
    "source_list": [
      {
        "source": "Tessin Band 03, Afrika formations",
        "content": "21. Panzer-Division (ex-5. leichte Division) - Teil des Deutschen Afrikakorps unter Generalleutnant Erwin Rommel. Kommandeur: Generalmajor von Ravenstein."
      },
      {
        "source": "Feldgrau.com - 21st Panzer Division",
        "url": "http://feldgrau.com/21pzdiv.html",
        "content": "21.Panzer-Division\nFormation: February 1941 in North Africa\nCommander: Generalmajor Johann von Ravenstein\nStrength: Approximately 11,000-13,000 men\nTank Regiment 5 with approximately 150-160 tanks"
      },
      {
        "source": "Niehorster - Afrika Korps May 1941",
        "content": "21st Panzer Division (von Ravenstein)\n- Panzer Regiment 5 (156 tanks total)\n  - Pz II: 45, Pz III: 91, Pz IV: 20\n- Rifle Regiment 104\n- Artillery Regiment 155\n- Division strength: ~12,000"
      }
    ]
  },
  "created_at": "2025-10-09T15:00:00Z",
  "status": "pending"
}
EOF
```

**Terminal 3 - Start agent:**
```bash
npm run agent historical_research
```

**VS Code Window 3 (historical_research session):**

The agent will analyze all facts against additional sources and produce:

```json
[
  {
    "fact_id": "cmd_001",
    "verification_status": "VERIFIED",
    "original_fact": {
      "unit": "21. Panzer-Division",
      "commander": "Johann von Ravenstein",
      "rank": "Generalmajor"
    },
    "verified_fact": {
      "unit": "21. Panzer-Division",
      "commander": "Johann von Ravenstein",
      "rank": "Generalmajor"
    },
    "supporting_sources": [
      {
        "source": "Tessin Band 03",
        "agreement": "exact",
        "excerpt": "Generalmajor von Ravenstein"
      },
      {
        "source": "Feldgrau.com",
        "agreement": "exact",
        "excerpt": "Generalmajor Johann von Ravenstein"
      },
      {
        "source": "Niehorster",
        "agreement": "partial",
        "excerpt": "von Ravenstein (name without rank)"
      }
    ],
    "conflicts": [],
    "updated_confidence": 98,
    "confidence_reasoning": "Commander confirmed by 3 independent sources with consistent name and rank"
  },
  {
    "fact_id": "per_001",
    "verification_status": "CONFIRMED",
    "original_fact": {
      "total_strength": 12500
    },
    "verified_fact": {
      "total_strength": 12000,
      "strength_range": "11000-13000"
    },
    "supporting_sources": [
      {
        "source": "Tessin Band 08",
        "agreement": "exact",
        "excerpt": "ca. 12.500 Mann"
      },
      {
        "source": "Feldgrau.com",
        "agreement": "partial",
        "excerpt": "11,000-13,000 men"
      },
      {
        "source": "Niehorster",
        "agreement": "partial",
        "excerpt": "~12,000"
      }
    ],
    "conflicts": [],
    "updated_confidence": 90,
    "confidence_reasoning": "Strength figures agree within 10% variance - all sources confirm approximately 12,000"
  },
  {
    "fact_id": "eq_001",
    "verification_status": "CONFIRMED",
    "original_fact": {
      "total_tanks": 156,
      "breakdown": [
        {"type": "Panzer II", "count": 45},
        {"type": "Panzer III (short)", "count": 71},
        {"type": "Panzer III (long)", "count": 20},
        {"type": "Panzer IV (short)", "count": 20}
      ]
    },
    "verified_fact": {
      "total_tanks": 156,
      "breakdown": [
        {"type": "Panzer II", "count": 45},
        {"type": "Panzer III", "count": 91, "note": "Variants combined in Niehorster"},
        {"type": "Panzer IV", "count": 20}
      ]
    },
    "supporting_sources": [
      {
        "source": "Tessin Band 08",
        "agreement": "exact",
        "excerpt": "156 Panzer total with full variant breakdown"
      },
      {
        "source": "Feldgrau.com",
        "agreement": "partial",
        "excerpt": "150-160 tanks"
      },
      {
        "source": "Niehorster",
        "agreement": "exact",
        "excerpt": "156 tanks total - Pz II: 45, Pz III: 91, Pz IV: 20"
      }
    ],
    "conflicts": [
      {
        "field": "panzer_iii_variants",
        "conflict": "Tessin shows 71 short + 20 long (91 total), Niehorster shows 91 total without variant split",
        "resolution": "Both sources agree on 91 Panzer III total. Tessin provides additional variant detail which Niehorster doesn't contradict."
      }
    ],
    "updated_confidence": 95,
    "confidence_reasoning": "Tank totals exactly match between Tessin and Niehorster (156 total). Feldgrau confirms range. Variant split from Tessin is additional detail, not contradictory."
  }
]
```

**Output saved to:**
```
outputs/task_002_verify_21pz_output.json
sources/processed/verified_facts/21pz_ger_1941q2_verified.json
```

---

## Step 4: Next Steps - Build Organization

Now that you have **verified facts**, you can proceed to Phase 2:

**Terminal 4 (org_hierarchy agent):**
```bash
# Create organizational hierarchy
cat > tasks/pending/task_003_org_21pz.json
# ... use verified facts to build org tree
```

**Terminal 5 (toe_template agent):**
```bash
# Create templates for German Panzer Division components
```

**Terminal 6 (unit_instantiation agent):**
```bash
# Instantiate specific 21st Panzer units from templates
```

---

## Summary: What You Accomplished

1. ✅ **Searched** 17 volumes of Tessin + Army Lists using `npm run search`
2. ✅ **Extracted** 5 structured facts from Tessin with citations and confidence levels
3. ✅ **Verified** facts against 3 additional sources (Tessin Band 03, Feldgrau, Niehorster)
4. ✅ **Resolved** minor conflicts (variant details)
5. ✅ **Increased** confidence levels from 85-95% → 90-98%
6. ✅ **Produced** `verified_facts.json` ready for Phase 2 (organization building)

---

## Key Takeaways

- **PRIMARY sources** (Tessin, Army Lists) provide base data
- **SECONDARY sources** (web databases) verify and fill gaps
- **Multi-source verification** increases confidence dramatically
- **Agent prompts** ensure consistent, structured output
- **File-based system** maintains true agent independence
- **Commonwealth reminder** embedded in every agent prompt

---

## Quick Reference Commands

```bash
# Search sources
npm run search "query" -- --type german --context 5

# Start agents (in separate terminals)
npm run agent document_parser
npm run agent historical_research
npm run agent org_hierarchy
npm run agent toe_template
npm run agent unit_instantiation

# Check task status
ls tasks/pending/
ls tasks/completed/
ls outputs/

# View agent catalog
cat agents/agent_catalog_enhanced.json | grep "agent_id"

# View source catalog
cat sources/sources_catalog.json
```

Ready to process your first unit!
