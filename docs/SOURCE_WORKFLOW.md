# Source Document Workflow Guide

## Overview
This guide shows how to use your local documents and web sources with the multi-agent TO&E builder system.

## Your Source Collection

### **PRIMARY SOURCES (95% Confidence)**
1. **British Army Lists (1941-1943)** - Official quarterly unit assignments
2. **Tessin's Wehrmacht Encyclopedia (17 volumes)** - Definitive German units
3. **US Field Manuals** - Official doctrine and TO&E

### **SECONDARY SOURCES (70-90% Confidence)**
4. **Web databases** - Feldgrau, Niehorster, Asisbiz, etc.

---

## Phase 1: Source Extraction Workflow

### Step 1: Choose Your Primary Document

**For German units:**
```
Source: Tessin volumes (Band 01-17)
Location: D:\north-africa-toe-builder\Resource Documents\tessin-georg-verbande-und-truppen-der-deutschen-wehrmacht-und-waffen-ss\
Files: Tessin, Georg - Verbände und Truppen... Band XX_hocr_searchtext.txt.gz
```

**For British units:**
```
Source: British Army Lists (quarterly)
Location: D:\north-africa-toe-builder\Resource Documents\Great Britain Ministery of Defense Books\
Files: armylist[month][year]grea_hocr_searchtext.txt.gz

Available quarters:
- 1941: jan, apr, jul, oct
- 1942: jan, apr, jul, oct
- 1943: jan, apr
```

**For US units:**
```
Source: US Field Manuals
Location: D:\north-africa-toe-builder\Resource Documents\
Files:
- FM7-20_Infantry_Battalion_1942.pdf (infantry)
- FM17-10_Armored_Force_1942.pdf (armor)
- FM101-10_US_Army_Staff_Manual_1941.pdf (organization)
```

### Step 2: Extract Facts (Agent: document_parser)

**Input preparation:**
1. Decompress .gz files if needed:
   ```bash
   gunzip -c "Tessin, Georg - Band 01_hocr_searchtext.txt.gz" > tessin_band_01.txt
   ```

2. Extract relevant sections (or use entire document)

3. Create task for document_parser:
   ```json
   {
     "agent_id": "document_parser",
     "inputs": {
       "source_content": "[paste text from document]",
       "document_type": "Tessin Wehrmacht Encyclopedia",
       "nation": "Germany",
       "quarter": "1941-Q2"
     }
   }
   ```

**What you'll get:**
- `raw_facts.json` - Structured facts with citations and confidence levels

### Step 3: Cross-Reference (Agent: historical_research)

**Input preparation:**
Gather additional sources for the same unit/topic:

**Example for German 15th Panzer Division, 1941-Q2:**

1. **Primary extraction** (already done in Step 2):
   - Tessin Band 03 (Afrika Korps units)

2. **Additional sources** for verification:
   ```
   - Tessin Band 04 (related units)
   - Feldgrau.com: http://feldgrau.com/15pzdiv.html
   - Niehorster.org: North Africa OOB 1941
   - RommelsRiposte.com: 15th Panzer equipment data
   ```

3. **Prepare source content:**

   For **local documents**, extract relevant sections:
   ```json
   {
     "source": "Tessin Band 04, pages 120-125",
     "content": "[paste extracted text about 15th Panzer]"
   }
   ```

   For **web sources**, you can either:
   - Option A: Paste the URL and relevant text
   - Option B: Use WebFetch to retrieve (if accessible)

4. **Create task for historical_research:**
   ```json
   {
     "agent_id": "historical_research",
     "inputs": {
       "raw_facts": "[output from document_parser]",
       "source_list": [
         {
           "source": "Tessin Band 04, pages 120-125",
           "content": "[text about unit organization]"
         },
         {
           "source": "Feldgrau.com - 15th Panzer Division",
           "url": "http://feldgrau.com/15pzdiv.html",
           "content": "[relevant text from website]"
         },
         {
           "source": "Niehorster - Afrika Korps OOB May 1941",
           "content": "[OOB data]"
         }
       ]
     }
   }
   ```

**What you'll get:**
- `verified_facts.json` - Facts with verification status (VERIFIED/CONFIRMED/DISPUTED/UNVERIFIED)
- `conflicts.json` - List of contradictions between sources with resolutions

---

## Recommended Source Combinations by Nation

### **For German Afrika Korps Units:**

**PRIMARY:**
1. Tessin volumes (search for unit number/name)
   - Band 03: Afrika formations
   - Band 05-10: Individual divisions

**SECONDARY (verification):**
2. Feldgrau.com (organization details)
3. RommelsRiposte.com (equipment specifics)
4. Niehorster.org (OOB structure)

**Example workflow:**
```
1. Extract from Tessin Band 03 (15th Panzer Division)
   → raw_facts.json

2. Cross-reference with:
   - Tessin Band 07 (15.Panzer-Division full history)
   - Feldgrau.com (organization charts)
   - RommelsRiposte.com (Panzer III/IV allocations)
   → verified_facts.json
```

### **For British 8th Army Units:**

**PRIMARY:**
1. British Army Lists (quarter-specific)
   - Jan 1941: armylistjan1941grea
   - Jul 1942: armylistjul1942grea
   - etc.

2. TM 30-410 (organizational doctrine)

**SECONDARY (verification):**
3. Desert Rats book (8th Army specific)
4. Niehorster.org (OOB verification)

**Example workflow:**
```
1. Extract from British Army List Oct 1941
   → Find 7th Armoured Division commanders and units
   → raw_facts.json

2. Cross-reference with:
   - TM 30-410 (standard British division TO&E)
   - Desert Rats book (7th Armoured specific details)
   - Niehorster (OOB structure verification)
   → verified_facts.json
```

### **For US Army Units:**

**PRIMARY:**
1. US Field Manuals (doctrinal TO&E)
   - FM 7-20: Infantry battalions
   - FM 17-10: Armored divisions
   - FM 101-10: General organization

**SECONDARY (verification):**
2. Niehorster.org (actual unit deployments)
3. Historical unit records (if available)

**Example workflow:**
```
1. Extract from FM 17-10 (standard armored division TO&E)
   → raw_facts.json

2. Cross-reference with:
   - FM 101-10 (personnel allocations)
   - Niehorster (1st Armored Division actual strength)
   → verified_facts.json
```

---

## Source Quality Guidelines

### **Use for DEFINITIVE DATA (95%+ confidence):**
- Commander names → British Army Lists, Tessin
- Unit designations → British Army Lists, Tessin
- Official TO&E → Field Manuals
- Quarterly assignments → British Army Lists

### **Use for VERIFICATION (80-90% confidence):**
- Equipment counts → Field Manuals, Feldgrau
- Organizational structure → TM 30-410, Niehorster
- Tactical doctrine → Field Manuals

### **Use for SUPPLEMENTARY INFO (70-80% confidence):**
- Equipment variants → Feldgrau, RommelsRiposte
- Operational context → Desert Rats, ErwinRommel.info
- Desert modifications → RommelsRiposte

---

## Conflict Resolution Rules

When sources disagree:

**Priority order:**
1. **Official primary documents** (Army Lists, Tessin, Field Manuals)
2. **Contemporary manuals** (TM 30-410, US FMs)
3. **Academic references** (Osprey books, scholarly works)
4. **Research databases** (Niehorster, Feldgrau)
5. **Specialized sites** (RommelsRiposte, ErwinRommel.info)

**Example:**
```
Fact: Commander of 15th Panzer Division, May 1941

Source 1 (Tessin Band 03): "Generalmajor Heinrich von Prittwitz und Gaffron"
Source 2 (Feldgrau.com): "General von Prittwitz"
Source 3 (RommelsRiposte): "von Prittwitz"

Resolution:
- Tessin (95% confidence) has full name and exact rank
- Other sources confirm but less specific
- VERIFIED: Use Tessin's complete data
- Confidence: 98% (primary source + 2 confirmations)
```

---

## Quick Start Examples

### Example 1: Extract German 21st Panzer Division (1941-Q2)

**Step 1: Find in Tessin**
```bash
# Decompress Tessin Band 08 (Panzer divisions)
gunzip -c "Tessin... Band 08_hocr_searchtext.txt.gz" > tessin_08.txt

# Search for 21st Panzer
grep -A 50 "21.*Panzer" tessin_08.txt
```

**Step 2: Run document_parser**
```
Agent: document_parser
Inputs:
  source_content: [extracted text about 21st Panzer]
  document_type: "Tessin Wehrmacht Encyclopedia"
  nation: "Germany"
  quarter: "1941-Q2"

Output: raw_facts.json
```

**Step 3: Cross-reference**
```
Agent: historical_research
Inputs:
  raw_facts: [from Step 2]
  additional_sources:
    - Feldgrau.com (21st Panzer page)
    - Niehorster (Afrika Korps OOB)
    - RommelsRiposte (tank allocations)

Output: verified_facts.json
```

### Example 2: Extract British 7th Armoured Division (1942-Q3)

**Step 1: Find in Army List**
```bash
# Decompress July 1942 Army List
gunzip -c "armylistjul1942grea_hocr_searchtext.txt.gz" > armylist_1942_jul.txt

# Search for 7th Armoured
grep -A 100 "7th.*Armoured\|Seventh.*Armoured" armylist_1942_jul.txt
```

**Step 2: Run document_parser**
```
Agent: document_parser
Inputs:
  source_content: [extracted Army List entry]
  document_type: "British Army List"
  nation: "Britain"
  quarter: "1942-Q3"

Output: raw_facts.json
```

**Step 3: Cross-reference**
```
Agent: historical_research
Inputs:
  raw_facts: [from Step 2]
  additional_sources:
    - TM 30-410 (British armoured division TO&E)
    - Desert Rats book (7th Armoured details)
    - Niehorster (8th Army OOB July 1942)

Output: verified_facts.json
```

---

## File Management

### Directory Structure:
```
D:\north-africa-toe-builder\
├── sources\
│   ├── sources_catalog.json          ← Source metadata
│   ├── extracted\                    ← Decompressed source files
│   │   ├── tessin_band_01.txt
│   │   ├── tessin_band_02.txt
│   │   ├── armylist_1941_jan.txt
│   │   └── ...
│   └── processed\                    ← Agent outputs
│       ├── raw_facts\
│       │   ├── 15th_panzer_raw.json
│       │   └── 7th_armoured_raw.json
│       └── verified_facts\
│           ├── 15th_panzer_verified.json
│           └── 7th_armoured_verified.json
```

### Naming Convention:
```
{unit_name}_{nation}_{quarter}_{stage}.json

Examples:
- 15th_panzer_ger_1941q2_raw.json
- 7th_armoured_brit_1942q3_verified.json
- 1st_infantry_us_1943q1_raw.json
```

---

## Tips for Success

1. **Start with PRIMARY sources** (Army Lists, Tessin, FMs)
2. **Always cite page numbers** precisely
3. **Extract in context** - include surrounding text for verification
4. **Use at least 2 sources** for critical facts (commanders, unit names)
5. **Mark uncertainties** - better to flag "uncertain" than guess
6. **Preserve original language** - "XXI Corpo d'Armata" not "21st Corps"
7. **Check time periods** carefully - commanders change quarterly!

## Need Help?

- See `sources/sources_catalog.json` for complete source metadata
- See agent prompts in `agents/agent_catalog_enhanced.json` for input formats
- See `FILE_BASED_SETUP.md` for multi-terminal workflow
