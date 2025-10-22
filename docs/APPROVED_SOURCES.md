# Approved Sources for TO&E Extraction Agents

**Version**: 1.0.0
**Last Updated**: 2025-10-22
**Purpose**: Reference guide for all agents performing source research and data extraction

---

## 🚨 CRITICAL RULES

### ✅ ALLOWED:
- **All sources listed below** (primary and secondary)
- **WebSearch tool** for finding specific information
- **WebFetch tool** for accessing URLs
- **Local document reading** (MCP filesystem tools)

### ❌ PROHIBITED:
- **Wikipedia** (all languages, all domains: *.wikipedia.org)
- **Random blogs or forums** (unless from approved domains below)
- **Social media** (Twitter, Reddit, Facebook, etc.)
- **Guessing or hallucination** - If data unavailable, mark as "Unknown" with low confidence

---

## 📚 PRIMARY SOURCES (90-95% Confidence)

### Local Documents (Best - Use First!)

**German Units:**
- **Tessin Wehrmacht Encyclopedia** (17 volumes, 95% confidence)
  - Location: `Resource Documents/tessin-georg-verbande.../`
  - Coverage: Complete Wehrmacht organization 1939-1945
  - Best for: German unit TO&E, commanders, organizational structure

- **Nafziger Collection** (10,049 OOB/TO&E files, 92% confidence)
  - Location: `Resource Documents/Nafziger Collection/WWII/`
  - Coverage: All nations, 1939-1945, 205 North Africa files
  - Best for: Orders of battle, daily strength returns, TO&E templates
  - **NOTE**: Some OCR errors exist (e.g., "Savona Celere" error - verify with other sources)

**British/Commonwealth Units:**
- **British Army Lists** (Quarterly 1941-1943, 95% confidence)
  - Location: `Resource Documents/Great Britain Ministery of Defense Books/`
  - Coverage: Official quarterly unit assignments, commanders
  - Best for: Commander names, unit assignments, exact dates
  - **PRIMARY SOURCE** - Official government records

- **TM 30-410: Handbook on the British Army** (1942, 90% confidence)
  - Location: `Resource Documents/British_PRIMARY_SOURCES/`
  - Coverage: Complete British Army organization, equipment, tactics
  - Best for: Organizational structure, equipment specs, doctrine

- **Desert Rats: British 8th Army in North Africa 1941-43** (Osprey, 85% confidence)
  - Location: `data/output/pdf_extracts/682349763-Battle-Orders-028-Desert-Rats...`
  - Coverage: 8th Army organization, operations, equipment
  - Best for: North Africa-specific details, artillery, armor tactics

**Italian Units:**
- **US G-2 Order of Battle of the Italian Army** (July 1943, 95% confidence)
  - Location: `Resource Documents/Order-of-battle-of-the-Italian-Army-USA-HQ-G2-July-1943.txt`
  - Coverage: Complete Italian Army units, composition, history
  - Best for: Unit designations, regimental composition, operational history

- **TM E 30-420: Handbook on the Italian Military Forces** (3 August 1943, 90% confidence)
  - Location: `Resource Documents/TME_30_420_Italian_Military_Forces_1943_temp.txt`
  - Coverage: Italian binary division organization FROM MARCH 1, 1940 onward
  - **Contains 1940 TO&E data** - not just 1943!
  - Best for: Standard division structure, equipment allocations, MVSN attachments

**American Units:**
- **FM 101-10: Staff Officers' Field Manual** (1941, 90% confidence)
  - Coverage: US Army organization, staff procedures, unit structures

- **FM 17-10: Armored Force Field Manual** (1942, 90% confidence)
  - Coverage: US armored division organization, tank battalion TO&E

- **FM 7-20: Infantry Battalion** (1942, 90% confidence)
  - Coverage: US infantry battalion organization, weapons, squad structure

**Equipment Reference:**
- **Jane's WW2 Tanks And Fighting Vehicles** (88,257 lines, 90% confidence)
  - Location: `Resource Documents/Janes-ww2-Tanks-And-Fighting-Vehicles.txt`
  - Coverage: All nations AFV specifications, production dates, variants
  - Best for: Production dates, AFV specifications, variant identification

---

## 🌐 APPROVED WEB SOURCES (70-87% Confidence)

### Tier 1 Web Sources (80-87% confidence)

**Feldgrau.net** (87% confidence)
- **URL**: http://feldgrau.com
- **Nation**: Germany
- **Best for**: Wehrmacht organization, Afrika Korps detail, equipment variants
- **Notes**: Some 403 errors - use forum posts and cached content
- **Example**: http://feldgrau.com/15pzdiv.html (15th Panzer Division)

**Niehorster.org** (82% confidence)
- **URL**: http://niehorster.org
- **Nations**: All
- **Best for**: Organizational hierarchy, strength data, command relationships
- **Notes**: SSL certificate issues - use cached content if needed
- **Coverage**: WWII Organizations & Orders of Battle for all theaters

**WW2 Tanks (wwiitanks.co.uk)** (82% confidence)
- **URL**: https://wwiitanks.co.uk
- **Nations**: All
- **Best for**: AFV production dates, variants, armament specifications
- **Coverage**: Comprehensive WWII tank database, operational history

**Asisbiz.com** (80% confidence)
- **URL**: http://asisbiz.com
- **Best for**: Aircraft variants, squadron assignments, aircraft specs
- **Coverage**: Aircraft and aviation research

**OnWar.com - Tanks** (80% confidence)
- **URL**: https://www.onwar.com/wwii/tanks/index.html
- **Nations**: All (213 vehicles: Germany 69, USSR 48, USA 24, UK 24, Italy 12)
- **Best for**: AFV specifications, production dates, armor protection, mobility data
- **Notes**: Uses 75 primary/secondary references - good for cross-referencing

### Tier 2 Web Sources (70-75% confidence)

**RommelsRiposte.com** (75% confidence)
- **URL**: http://rommelsriposte.com
- **Best for**: Afrika Korps equipment, tank allocations, desert modifications
- **Coverage**: Afrika Korps specialist site

**ErwinRommel.info** (70% confidence)
- **URL**: http://erwinrommel.info
- **Best for**: German command structure, Panzer Army Africa organization
- **Coverage**: Leadership changes, operational timeline

---

## 📋 SOURCE PRIORITY BY TASK

### Commander Verification (Use in order):
1. British Army Lists (95%)
2. Tessin Complete (95%)
3. Nafziger Collection (92%)
4. TM 30-410 (90%)
5. Niehorster (82%)

### German Units:
1. Tessin Complete (95%)
2. Nafziger Collection (92%)
3. Feldgrau (87%)
4. Niehorster (82%)
5. RommelsRiposte (75%)

### British/Commonwealth Units:
1. British Army Lists (95%)
2. Nafziger Collection (92%)
3. TM 30-410 (90%)
4. Desert Rats (85%)
5. Niehorster (82%)

### Italian Units:
1. US G-2 Italian OOB 1943 (95%)
2. Nafziger Collection (92%)
3. **TM E 30-420 (90%)** ← Contains 1940 TO&E!
4. Niehorster (82%)

### American Units:
1. FM 101-10 (90%)
2. FM 17-10 (90%)
3. FM 7-20 (90%)
4. Nafziger Collection (92%)
5. Niehorster (82%)

### Equipment Specifications:
1. Jane's WW2 Tanks (90%)
2. Feldgrau (87% for German)
3. WW2 Tanks UK (82%)
4. OnWar Tanks (80%)
5. TM 30-410 (90% for British)

### North Africa OOB:
1. Nafziger Collection (92%)
2. British Army Lists (95%)
3. Tessin Complete (95%)
4. US G-2 Italian OOB (95%)
5. Desert Rats (85%)

---

## 🔍 RESEARCH WORKFLOW

### Step 1: Exhaust Local Documents FIRST
- Search Tessin (German)
- Search British Army Lists (British/Commonwealth)
- Search Nafziger Collection (All nations)
- Search US G-2 / TM E 30-420 (Italian)
- Search Field Manuals (US)

### Step 2: If Data Missing, Use Approved Web Sources
- Start with highest confidence (Feldgrau 87%, Niehorster 82%)
- Cross-reference with at least 2 sources for critical facts
- Document all sources used with URLs and access dates

### Step 3: Mark Gaps Transparently
- If data unavailable after exhausting sources: Mark "Unknown"
- Document which sources were checked
- Set confidence appropriately (e.g., 40% for unknown commander)
- **NEVER guess or hallucinate data**

---

## ⚠️ KNOWN SOURCE ISSUES

### Nafziger Collection:
- **Savona Division** (Sept 1941): Lists as "Celere Division" with cavalry regiments
  - **ERROR**: Savona was 55th Infantry Division (15th/16th Regiments)
  - **Cause**: Likely OCR error confusing SAVONA with SAVOIA (1st Celere Cavalry)
  - **Action**: Verify Nafziger data with US G-2 or TM E 30-420 for Italian units

### Feldgrau.net:
- Some pages return 403 errors
- Use cached content or forum posts as fallback

### Niehorster.org:
- SSL certificate issues may occur
- Content is reliable when accessible

---

## 📊 CONFIDENCE SCORING GUIDELINES

**95% confidence**: Primary official documents with exact match
- Example: British Army List shows "Maj-Gen W.H.E. Gott" commanding 7th Armoured

**90% confidence**: Official manuals with standard TO&E
- Example: TM E 30-420 shows Italian binary division = 2 regiments, 36 artillery

**85% confidence**: High-quality secondary sources with citations
- Example: Desert Rats book cites specific regimental histories

**80% confidence**: Reputable databases with cross-references
- Example: Feldgrau + Niehorster both confirm 15th Panzer composition

**75% confidence**: Specialized sites with domain expertise
- Example: RommelsRiposte provides Afrika Korps tank allocations

**70% confidence**: Multiple secondary sources agree
- Example: 3 web sources confirm unit was present at battle

**Below 70%**: Insufficient data - mark as "Unknown" with gap documentation

---

## 🎯 AGENT USAGE EXAMPLES

### Example 1: Italian Division 1940-Q3

**Task**: Extract Savona Division TO&E

**Step 1**: Check local documents
```
✓ US G-2 Italian OOB 1943: Found unit designation, regiments, history
✓ TM E 30-420: Found standard Italian binary division structure (1940 TO&E)
✓ Nafziger Collection: Found but has error (lists as Celere - IGNORE)
```

**Step 2**: Check web sources for gaps
```
✓ Feldgrau: Italian division organization standards
✓ Niehorster: 10th Army composition confirmation
```

**Step 3**: Document gaps
```
✗ Commander name: Not found in any source (mark "Unknown", 40% confidence)
✗ Exact location Q3 1940: "Libya" confirmed, sector unknown (60% confidence)
```

**Result**: 70% confidence (acceptable with documented gaps)

### Example 2: German Division 1941-Q2

**Task**: Extract 15th Panzer Division TO&E

**Step 1**: Check local documents
```
✓ Tessin Band 03: Full organization, commander, equipment
✓ Nafziger Collection: Daily strength returns May 1941
```

**Step 2**: Check web sources for equipment details
```
✓ Feldgrau: Panzer III/IV variant breakdown
✓ RommelsRiposte: Desert modifications, actual tank strengths
```

**Step 3**: Cross-reference commander
```
✓ Tessin: "Generalmajor Heinrich von Prittwitz und Gaffron"
✓ Feldgrau: "General von Prittwitz" (confirms)
✓ Niehorster: "von Prittwitz" (confirms)
```

**Result**: 95% confidence (primary source + 2 confirmations)

---

## 📝 SOURCE CITATION FORMAT

Always cite sources in this format:

```json
{
  "type": "primary|secondary|web",
  "title": "Full document title",
  "author": "Author or organization",
  "date": "Publication date or period covered",
  "date_accessed": "YYYY-MM-DD",
  "confidence_level": 85,
  "details": "What specific data was extracted",
  "url": "Full URL or local file path"
}
```

**Example**:
```json
{
  "type": "primary",
  "title": "Technical Manual TME 30-420: Handbook on the Italian Military Forces",
  "author": "US War Department, Military Intelligence Service",
  "date": "3 August 1943",
  "date_accessed": "2025-10-22",
  "confidence_level": 85,
  "details": "Italian binary infantry division organization: 2 infantry regiments, artillery regiment (36 guns: 12x 75mm, 12x 100mm, 12x pack artillery), AT company (8x 47mm guns), AA battery (8x 20mm guns), engineer company, signals company. From March 1, 1940: MVSN legion of 2 battalions attached.",
  "url": "D:\\north-africa-toe-builder\\Resource Documents\\TME_30_420_Italian_Military_Forces_1943_temp.txt"
}
```

---

## 🚀 QUICK REFERENCE CARD

**FOR AGENTS: COPY THIS TO YOUR TASK CONTEXT**

```
APPROVED WEB SOURCES:
✓ Feldgrau.net (87%) - German units
✓ Niehorster.org (82%) - All nations OOB
✓ wwiitanks.co.uk (82%) - AFV specs
✓ OnWar.com/wwii/tanks (80%) - AFV specs
✓ Asisbiz.com (80%) - Aircraft
✓ RommelsRiposte.com (75%) - Afrika Korps
✓ ErwinRommel.info (70%) - German command

PROHIBITED:
✗ Wikipedia (all domains)
✗ Random blogs/forums
✗ Social media
✗ Guessing or hallucination

WORKFLOW:
1. Search local documents FIRST (Tessin, Army Lists, Nafziger, Manuals)
2. Use approved web sources for gaps (minimum 2 sources for critical facts)
3. Mark unknowns transparently (never guess!)
4. Cite all sources with confidence levels
5. Minimum 75% confidence required (70% acceptable with documented gaps)
```

---

**For complete source details, see**: `sources/sources_catalog.json`
**For workflow guidance, see**: `docs/SOURCE_WORKFLOW.md`
**For project scope, see**: `PROJECT_SCOPE.md`
