# Exhaustive Search Protocol v3.2.0

**Human-in-the-Loop Collaboration for Historical Research**

**Version**: Agent Catalog v3.2.0
**Status**: Production Ready
**Date**: October 15, 2025

---

## Overview

The Exhaustive Search Protocol replaces autonomous tier-based extraction (v3.1.0) with a collaborative human-in-the-loop approach. When agents encounter data gaps, they now:

1. ✅ **Exhaust ALL available sources** (Tier 1 → Tier 2 → Tier 3)
2. ⏸️ **PAUSE** and present detailed findings
3. ⏳ **AWAIT your direct instruction** on how to proceed
4. 📋 **Document** exactly which sources were checked and what was found

**Critical Rule**: "I will never accept null or unknown without trying further search options, even if I am doing them."

---

## What Changed from v3.1.0

### v3.1.0 (Autonomous - OLD)
```
1. Check 2-3 sources
2. Find gap (commander unknown)
3. Classify as Tier 2 (60-74% confidence)
4. Create gap documentation
5. Proceed autonomously with extraction ❌
6. User sees completed Tier 2 extraction
```

### v3.2.0 (Exhaustive Search + Human-in-Loop - NEW)
```
1. Check ALL Tier 1 sources (Tessin, Italian War Ministry)
2. Check ALL Tier 2 sources (Comando Supremo, Niehorster, Regio Esercito)
3. Check Tier 3 sources for critical gaps (Italian State Archive, NARA T-821)
4. Compile exhaustive_search_report (6+ sources checked)
5. Identify potential_next_steps ✅
6. PAUSE and present findings to user ⏸️
7. AWAIT user direct instruction ⏳
8. User says: "Check British Intelligence WO 208" or "Accept with null commander"
9. Agent follows your explicit instruction ✅
```

---

## How It Works

### 1. Exhaustive Source Catalog

**New File**: `sources/exhaustive_search_catalog.json`

Comprehensive source catalog for ALL nations with 3-tier search paths:

**Tier 1 (Local - 90%+ confidence)**:
- German: Tessin Wehrmacht Encyclopedia (17 volumes), Field Manuals
- Italian: Italian War Ministry records (if available locally)
- British: Army Lists (quarterly 1941-1943), Field Service Regulations
- American: US Field Manuals, Army Lists

**Tier 2 (Curated Web - 75%+ confidence)**:
- German: Feldgrau.com, Niehorster OOB, Lexikon der Wehrmacht, Axis History Forum
- Italian: Comando Supremo, Regio Esercito online, Niehorster Italian OOB
- British: British Military History, Long Long Trail, Niehorster Commonwealth OOB
- American: US Army CMH, Niehorster US OOB

**Tier 3 (Specialized Archives - 85-95% confidence)**:
- German: Bundesarchiv, NARA German records (T-78, T-312, T-314, T-315)
- Italian: Italian State Archive, Ufficio Storico, NARA Italian records (T-821)
- British: National Archives UK (WO 169, WO 170, WO 175), Australian War Memorial, Archives NZ, India Office Records
- American: NARA US records (RG 407), Army Heritage Center

**Cross-Reference Sources**:
- British Intelligence assessments of Axis forces (WO 208)
- German intelligence on Allied forces
- Regimental histories, contemporary newspapers, academic publications

### 2. Agent Behavior

When the **historical_research v3.2.0** agent encounters a data gap:

**Step 1: EXHAUSTIVE SEARCH**
```
For Italian XXI Corps Q2 1941 commander gap:

✅ Tier 1 local sources:
   - Tessin Vol 12: CHECKED → Found subordinate units, no commander
   - Italian War Ministry records: CHECKED → No local copies available

✅ Tier 2 curated web:
   - Comando Supremo: CHECKED → Unit designation found, commander field blank
   - Regio Esercito online: CHECKED → No Q2 1941 commander data
   - Niehorster Italian OOB: CHECKED → Unit listed, commander field blank

✅ Tier 3 specialized archives (for critical gap):
   - Italian State Archive (online catalog): CHECKED → Catalog entry found, digitized records not available
   - Ufficio Storico: CHECKED → Requires in-person visit or formal request
   - NARA T-821 (Italian records): CHECKED → No Q2 1941 commander records found
   - British Intelligence WO 208: NOT CHECKED (potential next step)

Total sources checked: 8
Result: Commander UNKNOWN after exhaustive search
```

**Step 2: COMPILE FINDINGS**
```json
{
  "exhaustive_search_report": {
    "search_complete": true,
    "tier1_sources_checked": [
      {"source": "Tessin Vol 12", "status": "CHECKED", "result": "Found subordinate units, missing commander"},
      {"source": "Italian War Ministry records", "status": "CHECKED", "result": "No local copies available"}
    ],
    "tier2_sources_checked": [
      {"source": "Comando Supremo", "status": "CHECKED", "result": "Found unit designation, no commander info"},
      {"source": "Niehorster OOB", "status": "CHECKED", "result": "Unit listed, commander field blank"},
      {"source": "Regio Esercito online", "status": "CHECKED", "result": "No Q2 1941 commander data"}
    ],
    "tier3_sources_checked": [
      {"source": "Italian State Archive", "status": "CHECKED", "result": "Catalog entry found, digitized records not available"},
      {"source": "Ufficio Storico", "status": "CHECKED", "result": "Requires in-person visit"},
      {"source": "NARA T-821", "status": "CHECKED", "result": "No Q2 1941 commander records"}
    ],
    "critical_gaps_identified": [
      {
        "field": "commander",
        "status": "UNKNOWN after exhaustive search",
        "sources_tried": 8,
        "reason": "Interim command period Jan-Jul 1941, formal command structure not established",
        "potential_next_steps": [
          "Request access to Italian Military Historical Office archives (Ufficio Storico)",
          "Check Gen. Navarini's service file at Italian State Archive (requires in-person visit)",
          "Review British Intelligence assessments of Italian command structure (National Archives UK WO 208)",
          "Search Italian contemporary newspapers (Corriere della Sera, La Stampa) for command announcements",
          "Check German liaison reports to OKW for Italian command structure Q2 1941"
        ]
      }
    ],
    "data_summary": {
      "fields_verified": ["subordinate_units", "organization_level", "quarter"],
      "fields_estimated": ["equipment_totals", "personnel_strength"],
      "fields_unknown": ["commander"],
      "overall_confidence": 65,
      "extraction_quality_assessment": "Substantial data exists (subordinate units verified, structure documented), but critical gap (commander) remains after checking 8 sources across 3 tiers."
    }
  }
}
```

**Step 3: PAUSE AND REPORT**
```json
{
  "awaiting_user_guidance": {
    "status": "PAUSED",
    "reason": "Exhaustive search complete, gaps identified, awaiting user decision",
    "question_for_user": "Commander for Italian XXI Corps Q2 1941 unknown after checking:
- Tier 1: Tessin, Italian War Ministry (not available locally)
- Tier 2: Comando Supremo, Niehorster, Regio Esercito online
- Tier 3: Italian State Archive (catalog only), Ufficio Storico (requires visit), NARA T-821

Potential next steps:
1. Request Italian Military Historical Office archives access
2. Check Gen. Navarini's service file (requires in-person visit to Italian State Archive)
3. Review British Intelligence WO 208 assessments
4. Search Italian contemporary newspapers for command announcements
5. Check German liaison reports for Italian command structure

How would you like to proceed?",
    "user_options_context": "You can:
- Instruct me to pursue specific research avenues (e.g., 'Check British Intelligence WO 208')
- Accept extraction with commander = null and document the gap
- Mark unit for future research when archive access available
- Provide commander information if you have it from other sources"
  }
}
```

**Step 4: AWAIT YOUR GUIDANCE**

Agent stops and waits for your instruction.

---

## How to Use the System

### When Agent Pauses

You'll see output like this:

```
================================================================================
⏸️  AGENT PAUSED - AWAITING USER GUIDANCE
================================================================================

📋 Unit: italian XXI Corps (1941-Q2)

❓ Reason: Exhaustive search complete, gaps identified, awaiting user decision

🔍 EXHAUSTIVE SEARCH COMPLETED:
   • Tier 1 sources checked: 2
   • Tier 2 sources checked: 3
   • Tier 3 sources checked: 3

📊 DATA SUMMARY:
   ✅ Verified: subordinate_units, organization_level, quarter
   📐 Estimated: equipment_totals, personnel_strength
   ❌ Unknown: commander
   🎯 Overall confidence: 65%

⚠️  CRITICAL GAPS IDENTIFIED:

   Field: commander
   Status: UNKNOWN after exhaustive search
   Sources tried: 8
   Reason: Interim command period Jan-Jul 1941, formal command structure not established

   💡 Potential next steps:
      1. Request access to Italian Military Historical Office archives (Ufficio Storico)
      2. Check Gen. Navarini's service file at Italian State Archive (requires in-person visit)
      3. Review British Intelligence assessments (National Archives UK WO 208)
      4. Search Italian contemporary newspapers for command announcements
      5. Check German liaison reports

--------------------------------------------------------------------------------
❓ QUESTION FOR USER:
--------------------------------------------------------------------------------
Commander for Italian XXI Corps Q2 1941 unknown after checking:
- Tier 1: Tessin, Italian War Ministry (not available locally)
- Tier 2: Comando Supremo, Niehorster, Regio Esercito online
- Tier 3: Italian State Archive (catalog only), NARA T-821

Potential next steps:
1. Request Italian Military Historical Office archives access
2. Check Gen. Navarini's service file (requires in-person visit)
3. Review British Intelligence WO 208 assessments
4. Search Italian contemporary newspapers
5. Check German liaison reports

How would you like to proceed?

--------------------------------------------------------------------------------
💬 CONTEXT:
--------------------------------------------------------------------------------
You can:
- Instruct me to pursue specific research avenues (e.g., 'Check British Intelligence WO 208')
- Accept extraction with commander = null and document the gap
- Mark unit for future research when archive access available
- Provide commander information if you have it from other sources

================================================================================
⏳ Unit saved to: data/paused_units.json
📝 You can provide guidance by:
   1. Running: npm run resume -- [unit_id]
   2. Providing direct instruction when prompted
================================================================================
```

### Commands Available

**List all paused units:**
```bash
npm run resume:list
```

**Resume a paused unit (interactive):**
```bash
npm run resume
```

This will:
1. Show all paused units
2. Ask which one to resume
3. Show detailed pause information
4. Prompt for your instruction

**Resume specific unit by ID:**
```bash
npm run resume -- italian_1941q2_XXI_Corps
```

### Providing Instructions

When prompted, you can provide direct instructions like:

**Example 1: Pursue specific research avenue**
```
Your instruction: Check British Intelligence WO 208 for Italian XXI Corps commander Q2 1941
```

**Example 2: Accept with documented gap**
```
Your instruction: Accept extraction with commander = null. Document this as formal interim period Q2 1941 where command structure was not established. Add note that Gen. Navarini likely temporary commander but unconfirmed.
```

**Example 3: Provide information you have**
```
Your instruction: Use Generale di Corpo d'Armata Lorenzo Dalmazzo as commander. Found in Regio Esercito records dated April 1941.
```

**Example 4: Mark for future research**
```
Your instruction: Mark this unit for future research. Commander requires in-person visit to Italian State Archive or formal Ufficio Storico request. For now, proceed with commander = null and document the gap with all 8 sources checked.
```

**Example 5: Request deeper archive search**
```
Your instruction: Before accepting null, also check:
1. British WO 208 intelligence summaries April-June 1941
2. German OKW liaison reports on Italian forces
3. Contemporary Italian newspapers (Corriere della Sera April-June 1941)
Then report back findings.
```

---

## File Locations

**Exhaustive Search Catalog**:
```
sources/exhaustive_search_catalog.json
```

**Paused Units**:
```
data/paused_units.json
```

**Agent Prompt**:
```
agents/agent_catalog.json → historical_research v3.2.0
```

**Pause/Resume Handler**:
```
src/pause_resume_handler.js
scripts/resume_paused_unit.js
```

---

## Benefits

1. **Exhaustive Research**: ALL available sources checked before accepting null/unknown
2. **Transparency**: You see exactly which sources were tried and what was found/not found
3. **Collaboration**: Agent reports findings and awaits your guidance
4. **Flexibility**: You can direct agent to pursue specific research avenues
5. **Quality**: No more "quick classification" - comprehensive search required
6. **Control**: You make final decision on how to proceed

---

## Integration with Orchestrator

The autonomous orchestrator (v4.0+) will:

1. Run agent extraction as normal
2. Detect `awaiting_user_guidance` status
3. Save paused unit to `data/paused_units.json`
4. Present pause information to you
5. STOP orchestration and await your guidance
6. Resume when you provide instruction via `npm run resume`

**Orchestrator Changes Required** (Pending):
- Detect pause signal in agent response
- Call `PauseResumeHandler.isPaused(response)`
- Save paused unit with `PauseResumeHandler.savePausedUnit(pauseInfo)`
- Present to user with `PauseResumeHandler.presentToUser(pauseInfo)`
- Exit orchestration loop
- Resume when user runs `npm run resume`

---

## Validation

To test the exhaustive search protocol:

1. Agent MUST check sources from `sources/exhaustive_search_catalog.json`
2. Agent MUST try ALL Tier 1 sources first
3. Agent MUST try Tier 3 for critical gaps (commander, unit existence)
4. Agent output MUST include `exhaustive_search_report`
5. Agent output MUST include `awaiting_user_guidance`
6. Agent MUST PAUSE (not proceed autonomously)
7. Agent MUST present `potential_next_steps` for each gap

---

## Related Documentation

- **VERSION_HISTORY.md**: Agent Catalog v3.2.0 entry (complete technical details)
- **agents/agent_catalog.json**: historical_research v3.2.0 prompt template
- **sources/exhaustive_search_catalog.json**: Comprehensive source catalog
- **PROJECT_SCOPE.md**: Project vision and phased approach

---

## Example Workflow

```
1. Run orchestrator: npm run start:autonomous

2. Agent processes Italian XXI Corps Q2 1941

3. Agent checks:
   ✅ Tier 1: Tessin, Italian War Ministry (2 sources)
   ✅ Tier 2: Comando Supremo, Niehorster, Regio Esercito (3 sources)
   ✅ Tier 3: Italian Archive, Ufficio Storico, NARA (3 sources)

4. Agent finds gap: Commander unknown after 8 sources

5. Agent PAUSES:
   ⏸️  AGENT PAUSED - AWAITING USER GUIDANCE
   📋 Unit: italian XXI Corps (1941-Q2)
   🔍 Exhaustive search complete (8 sources checked)
   ❌ Gap: commander (unknown after exhaustive search)
   💡 Potential next steps: [5 research options listed]

6. Orchestrator saves to data/paused_units.json

7. You review findings:
   npm run resume:list

8. You provide guidance:
   npm run resume
   > Your instruction: Check British Intelligence WO 208 for commander info

9. Agent resumes with your guidance

10. Agent checks WO 208, finds commander reference

11. Extraction completes with verified commander data
```

---

## Future Enhancements

**Planned for next iterations**:

1. **Automated archive requests**: Agent can draft formal requests to archives (Ufficio Storico, National Archives)
2. **Collaborative research notes**: Build persistent knowledge base of what sources were tried for which units
3. **Smart suggestions**: Based on similar units, agent suggests most likely productive sources
4. **Multi-agent collaboration**: Research agent can consult document_parser agent for deeper source analysis
5. **Progress tracking**: Dashboard showing paused units, research in progress, completion timeline

---

**Version**: v3.2.0
**Status**: Production Ready
**Last Updated**: October 15, 2025

---

*For questions or issues with the exhaustive search protocol, see VERSION_HISTORY.md Agent Catalog v3.2.0 entry.*
