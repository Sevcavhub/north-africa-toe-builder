# Agent Hallucination Analysis - Task Tool Test

**Date:** 2025-10-15
**Test:** Historical research agent invocation for Italian corps HQ size
**Result:** Agent fabricated data and falsely cited source

---

## The Prompt I Used (Task Tool Test #2)

```
You are the historical_research specialist agent. Research the typical Italian Army corps headquarters staff composition in 1941.

**Task:** Find authoritative sources for Italian corps (Corpo d'Armata) headquarters staff size and composition during 1941 North Africa campaign.

**Required Output (JSON format):**
```json
{
  "research_findings": {
    "typical_corps_hq_staff": {
      "officers": <number>,
      "ncos": <number>,
      "enlisted": <number>,
      "total": <number>
    },
    "sources": [
      "Source 1 with citation",
      "Source 2 with citation"
    ],
    "confidence_score": <0-100>,
    "notes": "Any caveats or uncertainties"
  }
}
```

**Search Strategy:**
1. Check for Italian Army doctrine manuals (1941)
2. Search for historical corps TO&E documents
3. Cross-reference with known Italian corps (XX, XXI, etc.)
4. Use Nafziger Collection if available
5. Web search as fallback

**Confidence Scoring:**
- 90-100%: Primary source document (doctrine manual, official TO&E)
- 75-89%: Secondary source with multiple confirmations (Nafziger, historian accounts)
- 60-74%: Single secondary source or inference from similar units
- <60%: Estimation only

Return your findings as JSON only.
```

---

## What The Agent Returned

```json
{
  "research_findings": {
    "typical_corps_hq_staff": {
      "officers": 60,
      "ncos": 90,
      "enlisted": 150,
      "total": 300,
      "notes": "Estimated based on comparative analysis..."
    },
    "sources": [
      "TME 30-420 'Handbook on Italian Military Forces' (1943) - US War Department Technical Manual - Paragraph 50: Corps Headquarters (comando di corpo d'armata) organizational structure with General Staff sections and headquarters personnel components",
      ...
    ],
    "confidence_score": 65,
    "notes": "MEDIUM-LOW CONFIDENCE - No primary source document found specifying exact Italian corps headquarters personnel strength for 1941..."
  }
}
```

**Key claim:** "Paragraph 50: Corps Headquarters... with headquarters personnel components"

---

## What TME 30-420 Paragraph 50 ACTUALLY Says

```
50. Corps headquarters (comando di corpo d'armata).—
Corps headquarters consists of the following components:

a. General Staff (Stato Maggiore),
   (1) Department of the Chief of the Army General Staff:
       (a) Operations and Intelligence Service.
       (b) Discipline.
       (c) Personnel and Administration.
   (2) Corps artillery headquarters.
   (3) Corps engineer headquarters.
   (4) Intendance:
       (a) Corps Transport Directorate.
       (b) Corps Medical Directorate.
       (c) Corps Commissariat Directorate.
       (d) Corps Veterinary Directorate.
   (5) Military tribunal.

b. Headquarters personnel (quartiere generale):
   (1) Headquarters infantry unit.
   (2) Photography section.
   (3) Staff-car unit (autodrappello).
   (4) Horsed Carabinieri section.
   (5) Aircraft signaling station.
   (6) Survey section.
   (7) Post office.
   (8) Two topographical sections.
   (9) Two mixed Carabinieri sections.
```

**Reality:** Paragraph 50 is a QUALITATIVE organizational chart with ZERO personnel numbers.

---

## The Hallucination

The agent:
1. ✅ Found correct source (TME 30-420)
2. ✅ Found correct paragraph (50)
3. ❌ **FABRICATED** "60 officers, 90 NCOs, 150 enlisted, 300 total"
4. ❌ **FALSELY CLAIMED** paragraph 50 contains "headquarters personnel components" (numbers)
5. ⚠️ Admitted in notes it was "Estimated based on comparative analysis"

**The agent created plausible-sounding numbers and falsely attributed them to a real source.**

---

## Why Did This Happen?

### Problem #1: Prompt Demanded Numbers

My prompt required:
```json
"officers": <number>,
"ncos": <number>,
"enlisted": <number>,
"total": <number>
```

**This created pressure to fill in numbers even if source didn't have them.**

### Problem #2: No Verification Requirements

My prompt said:
- ✅ "Find authoritative sources"
- ❌ No requirement to quote verbatim text
- ❌ No requirement to cite exact page/paragraph with quote
- ❌ No distinction between "source states X" vs "I estimated X from Y"

### Problem #3: JSON-Only Output

"Return your findings as JSON only" meant:
- No space for "I searched TME 30-420 para 50 but it only lists sections, no personnel counts"
- Agent felt compelled to complete the JSON structure
- Estimation happened silently without explicit marking

### Problem #4: Confidence Score Ambiguity

Agent returned 65% confidence BUT:
- Did this mean "65% confident the estimate is accurate"?
- Or "65% confident because no source found, this is a guess"?
- The confidence score obscured the fact that numbers were fabricated

---

## How My Manual Work Differed

When I manually estimated 120 personnel:

```json
"staff_strength": {
  "officers": 25,
  "ncos": 35,
  "enlisted": 60,
  "total": 120,
  "note": "Minimal corps staff during informal period. Formal corps headquarters not yet established."
}
```

**What I did right:**
- ✅ Clearly marked as estimate in notes field
- ✅ No false source attribution
- ✅ Contextualized as "minimal/informal" HQ
- ✅ Conservative numbers (120 vs agent's 300)

**What I did wrong:**
- ❌ Didn't use specialized agent (bypassed architecture)
- ❌ No source checking attempt documented
- ❌ No validation of "is 120 reasonable?"

---

## The Fix: Anti-Hallucination Prompt Template

### Version 2.0: Strict Citation Requirements

```
You are the historical_research specialist agent. Research the typical Italian Army corps headquarters staff composition in 1941.

**CRITICAL RULES:**
1. DISTINGUISH between "source states" vs "I estimated"
2. QUOTE verbatim text from sources (with exact page/paragraph)
3. If source gives organizational structure but NO numbers, say "NO PERSONNEL COUNTS FOUND"
4. Use separate JSON fields for "found_data" vs "estimated_data"
5. NEVER attribute estimates to sources

**Required Output:**

```json
{
  "research_findings": {
    "found_in_sources": {
      "organizational_structure": "Description from source",
      "personnel_counts": null OR {actual numbers if found},
      "source_quotes": [
        {
          "source": "TME 30-420 para 50",
          "verbatim_quote": "Exact text from source",
          "interpretation": "What this tells us"
        }
      ]
    },
    "estimates_if_no_data_found": {
      "method": "How estimate was derived",
      "estimated_personnel": {...},
      "confidence": 0-100,
      "caveats": ["Caveat 1", "Caveat 2"]
    },
    "sources_checked": [
      "TME 30-420 - CHECKED, found organizational chart (para 50), NO personnel counts",
      "Nafziger Collection - CHECKED, not available",
      ...
    ]
  }
}
```

**Search Strategy:**
1. Check TME 30-420 for Italian corps structure
2. Search Nafziger Collection for Italian corps TO&E
3. Check Resource Documents for Italian doctrine manuals
4. If NO NUMBERS FOUND, explicitly state this
5. Only estimate if requested, clearly marked as estimate

**Output Requirements:**
- Use "found_in_sources" for actual source data
- Use "estimates_if_no_data_found" for calculations/guesses
- Quote verbatim text with exact citations
- If organizational chart found but no numbers, say "STRUCTURE FOUND, NO COUNTS"
```

---

## Comparison: What Should Have Been Returned

### Correct Output (Anti-Hallucination Format)

```json
{
  "research_findings": {
    "found_in_sources": {
      "organizational_structure": "TME 30-420 para 50 lists sections: General Staff (Operations, Personnel, etc), Corps Artillery HQ, Corps Engineer HQ, Intendance (Transport, Medical, Commissariat, Veterinary), Military Tribunal, plus HQ personnel sections (infantry unit, photography, signals, carabinieri, survey, post office, topographical sections)",
      "personnel_counts": null,
      "source_quotes": [
        {
          "source": "TME 30-420 paragraph 50, page 47",
          "verbatim_quote": "Corps headquarters consists of the following components: a. General Staff (Stato Maggiore)... b. Headquarters personnel (quartiere generale): (1) Headquarters infantry unit. (2) Photography section...",
          "interpretation": "Provides QUALITATIVE organizational chart only. No quantitative personnel counts given."
        }
      ]
    },
    "estimates_if_no_data_found": {
      "method": "Proportional scaling from Division HQ (para 53: 34 officers, 302 enlisted = 336 total) with 2x multiplier for corps-level staff sections",
      "estimated_personnel": {
        "officers": 68,
        "ncos": 100,
        "enlisted": 304,
        "total": 472,
        "note": "ESTIMATE ONLY - based on 2x division HQ baseline"
      },
      "confidence": 40,
      "caveats": [
        "No primary source found for Italian corps HQ personnel counts",
        "TME 30-420 provides structure only, not numbers",
        "Estimate assumes formal corps establishment, not informal Q2 1941 period",
        "XX Corps Q2 1941 was informal/transitional with minimal staff",
        "Recommend: 100-150 personnel for informal period, 300-500 for formal corps"
      ]
    },
    "sources_checked": [
      "TME 30-420 - CHECKED paragraph 50 - organizational structure FOUND, personnel counts NOT FOUND",
      "TME 30-420 - CHECKED paragraph 53 - division HQ: 34 officers, 302 enlisted (used as baseline)",
      "Nafziger Collection - NOT AVAILABLE in Resource Documents for Italian corps 1941",
      "Resource Documents/Order-of-battle Italian Army 1943 - CHECKED, no corps HQ personnel data"
    ]
  }
}
```

**Key differences:**
- ✅ Explicitly states "personnel counts NOT FOUND"
- ✅ Separates source data from estimates
- ✅ Quotes verbatim text
- ✅ Lower confidence (40% vs 65%) reflecting lack of sources
- ✅ Provides range (100-150 informal, 300-500 formal) not false precision

---

## Implementation: Agent Catalog Updates Required

### File: `agents/agent_catalog.json`

**Current historical_research agent prompt (lines ~51-100):**
```json
{
  "agent_id": "historical_research",
  "prompt_template": "Research historical data for {unit}..."
}
```

**Required changes:**

1. **Add anti-hallucination preamble:**
```
CRITICAL: NEVER attribute estimates to sources. If source lacks specific data, return null for that field and explicitly state "NOT FOUND IN SOURCE". Use separate JSON sections for found_data vs estimated_data.
```

2. **Require verbatim quotes:**
```
For each source cited, provide:
- Exact citation (document, paragraph/page, date)
- Verbatim quote (5-10 lines of actual text)
- Your interpretation (what this tells us)
```

3. **Mandate source verification:**
```
Before returning data, verify:
- [ ] Can I quote exact text from source?
- [ ] Does source explicitly state this number/fact?
- [ ] Or am I inferring/estimating from source?
- [ ] Have I marked all estimates clearly?
```

4. **Use structured output format:**
```json
{
  "verified_facts": {
    "fact": "value",
    "source_quote": "verbatim text",
    "citation": "exact location"
  },
  "estimates": {
    "estimate": "value",
    "derivation_method": "how calculated",
    "confidence": 0-100,
    "marked_as_estimate": true
  },
  "sources_checked": ["source 1 - found X", "source 2 - not found"]
}
```

---

## Validation Script Required

Create `scripts/validate_agent_citations.js`:

```javascript
/**
 * Validate Agent Citation Accuracy
 *
 * For any agent output claiming a source:
 * 1. Extract citation (doc, page, paragraph)
 * 2. Read actual source
 * 3. Check if source contains claimed data
 * 4. Flag discrepancies
 */

function validateCitation(agentOutput) {
  const citations = extractCitations(agentOutput);

  for (const citation of citations) {
    const sourceText = readSource(citation.document, citation.location);
    const claimedData = citation.data_claimed;

    if (!sourceText.includes(claimedData)) {
      console.warn(`HALLUCINATION DETECTED: Agent claimed "${claimedData}" from ${citation.document} ${citation.location}, but source does not contain this.`);

      // Suggest correction
      console.log(`Source actually says: "${sourceText.substring(0, 200)}..."`);
    }
  }
}
```

---

## Testing Protocol

### Before deploying agents for real extractions:

**Test 1: Known Source With Data**
```
Prompt: "Find personnel count for Italian Infantry Division HQ from TME 30-420"
Expected: Should find para 53, return 34 officers + 302 enlisted
Verify: Check agent quotes exact numbers from source
```

**Test 2: Known Source WITHOUT Data**
```
Prompt: "Find personnel count for Italian Corps HQ from TME 30-420"
Expected: Should find para 50, return "organizational structure found, NO PERSONNEL COUNTS"
Verify: Agent does NOT fabricate numbers
```

**Test 3: No Source Available**
```
Prompt: "Find personnel count for Italian XX Corps informal HQ Q2 1941"
Expected: Should return "NO PRIMARY SOURCE FOUND" + optional conservative estimate marked clearly
Verify: Agent does NOT claim source exists when it doesn't
```

---

## Lessons Learned

1. **Demanding structured output creates hallucination pressure**
   - If JSON requires `"officers": <number>`, agent fills it even without data
   - Solution: Use nullable fields + separate estimate section

2. **"Return JSON only" removes safety commentary**
   - Agent can't say "I couldn't find this, here's why"
   - Solution: Require "sources_checked" field documenting search

3. **Confidence scores obscure hallucination**
   - 65% confidence doesn't reveal numbers were fabricated
   - Solution: Separate confidence for "source exists" vs "estimate accuracy"

4. **Citation without quotes enables false attribution**
   - "Source: TME 30-420 para 50" sounds authoritative
   - Solution: Require verbatim quote proving source contains claimed data

5. **Proportional thinking misleads**
   - "Division HQ is 336, so corps must be ~300" sounds logical
   - But formal vs informal corps, 1941 vs 1943, etc all matter
   - Solution: Require explicit caveats for all extrapolations

---

## Action Items

- [ ] Update `agents/agent_catalog.json` with anti-hallucination prompts
- [ ] Create `scripts/validate_agent_citations.js` for post-hoc checking
- [ ] Add to session start checklist: "Run agent hallucination tests"
- [ ] Document in CLAUDE.md: "All agent outputs must be citation-validated"
- [ ] Create test suite: `tests/agent_hallucination_tests.json`
- [ ] Train on examples: "Good citation" vs "Hallucination" comparisons

---

**Status:** CRITICAL - Blocks deployment of specialized agents until fixed
**Priority:** HIGH - Affects data quality for all future extractions
**Owner:** Architecture team / Agent design
