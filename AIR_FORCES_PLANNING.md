# Air Forces Quarterly Summaries - Project Plan & Status

**Project**: Quarterly theater-wide air forces summaries for North Africa (1940-Q3 to 1943-Q1)
**Current Status**: Phase 1 partially complete - Nafziger extraction working but missing strength data
**Last Updated**: 2025-10-28
**Session Document**: `AIR_SESSION_2025_10_28.md`

---

## Executive Summary

**Goal**: Create 52 quarterly air summaries (4 nations × 13 quarters) showing organizational hierarchy and aggregate strength for scenario generation integration.

**Current Progress**:
- ✅ Automated PDF parser built (`scripts/extract_nafziger_air_pdf.js`)
- ✅ 7 summaries generated from 5 Nafziger PDFs
- ⚠️ **BLOCKER**: 4 out of 7 summaries (57%) lack aircraft strength data
  - German units: Have strength data (170, 5, 20 aircraft)
  - Italian units: Only organizational structure (no counts)
  - British units: Only organizational structure (no counts)

**Critical Decision Needed**: Accept partial data OR pursue online archival sources?

---

## What Has Been Completed

### ✅ Phase 1a: Nafziger PDF Parser (COMPLETE)

**Script**: `scripts/extract_nafziger_air_pdf.js`

**Capabilities**:
- Handles 3 different PDF formats:
  1. **Tabular** (German): Column-aligned with headers
     ```
     Unit                Aircraft       Base           Aircraft
     2.(H)/14            HS126/Bf110    Ain El Gazala   18/13
     ```
  2. **Simple List** (Mixed Axis): Parenthetical format
     ```
     1/JG27 (23/6)
     6° Gruppo (MC202)
     ```
  3. **Hierarchical** (British RAF): Squadron structure without numbers
     ```
     No. 112 Squadron (GAMBUT) - Kittyhawk I
     ```

- Auto-detects nation from unit designation patterns
- Handles missing strength data gracefully (null values, "?" parsing)
- Extracts: unit designations, aircraft types, base locations, strength counts
- Output: v3.1.0_air schema compliance

**Execution**:
```bash
cd D:/north-africa-toe-builder
node scripts/extract_nafziger_air_pdf.js
```

**Output Location**: `data/output/air_summaries/`

### ✅ Phase 1b: Nafziger PDFs Extracted (PARTIAL)

**Successfully Processed** (5 PDFs → 7 JSONs):

| PDF | Date | Nations | Format | Units | Strength Data? |
|-----|------|---------|--------|-------|----------------|
| 941gdmc.pdf | 1941-05 | German | Tabular | 8 | ✅ YES (170 total, 252 operational) |
| 942game.pdf | 1942-01 | German, Italian | List | 28 | ⚠️ Partial (German: 5 aircraft, Italian: none) |
| 942geme.pdf | 1942-05 | German, Italian | Tabular | 34 | ⚠️ Partial (German: 20 aircraft, Italian: "?" values) |
| 942bema.pdf | 1942-05 | British | Hierarchical | 21 | ❌ NO (org structure only) |
| 942bima.pdf | 1942-09 | British | Hierarchical | 37 | ❌ NO (org structure only) |

**Generated Summaries**:
1. `german_1941q2_air_summary.json` - ✅ Tier 1 (90% confidence)
2. `german_1942q1_air_summary.json` - ✅ Tier 1 (90% confidence)
3. `german_1942q2_air_summary.json` - ✅ Tier 1 (90% confidence)
4. `italian_1942q1_air_summary.json` - ⚠️ Tier 2 (70% confidence - no strength)
5. `italian_1942q2_air_summary.json` - ⚠️ Tier 2 (70% confidence - no strength)
6. `british_1942q2_air_summary.json` - ⚠️ Tier 2 (70% confidence - no strength)
7. `british_1942q3_air_summary.json` - ⚠️ Tier 2 (70% confidence - no strength)

**Documentation**: `data/output/air_summaries/EXTRACTION_SUMMARY.md`

### ✅ Phase 1c: Local Primary Source Research (COMPLETE)

**Exhaustively Searched**:

1. ✅ **Nafziger Collection (1,140 PDFs searched)**
   - Pattern: Only 5 PDFs in entire 1941-1942 directory contain air OOBs
   - Result: All air-related PDFs already extracted above
   - Searched: 1939-1940, 1941-1942, 1943-1945 directories
   - Conclusion: No additional Nafziger air OOBs with strength data exist locally

2. ✅ **TME 30-420 (Italian Military Forces 1943)**
   - Location: `Resource Documents/TME_30_420_Italian_Military_Forces_1943_temp.txt`
   - Found: Chapter 7 Air Force, Table 274 (April 1943 theater aggregates)
   - Result: ❌ Too late (April 1943 vs. our 1941-1942 focus)
   - Result: ❌ Theater-wide totals only, no unit-level strength

3. ✅ **US G2 Italian OOB 1943**
   - Location: `Resource Documents/Order-of-battle-of-the-Italian-Army-USA-HQ-G2-July-1943.txt`
   - Searched: "Regia Aeronautica", "Stormo", "Gruppo", "aviation"
   - Result: ❌ Army only, no air force data

4. ✅ **British Army Lists (28 quarterly files, 1941-1943)**
   - Location: `Resource Documents/Great Britain Ministery of Defense Books/`
   - Searched: July 1942 list for "Squadron", "RAF", "aircraft"
   - Result: ❌ Army only, no RAF Air Force Lists present

5. ⏸️ **Tessin Vol 12 (German Wehrmacht)** - IN PROGRESS
   - Location: `Resource Documents/tessin-georg-verbande-und-truppen-der-deutschen-wehrmacht-und-waffen-ss/Band 12`
   - Status: Search started but not completed (VS Code crashes)
   - Expected: Might have Luftwaffe Fliegerführer Afrika strength returns

**Conclusion**: Local primary sources provide organizational structure but lack critical aircraft strength numbers for Italian/British units.

---

## Critical Blocker: Missing Strength Data

### Problem Statement

**4 out of 7 summaries (57%) lack aircraft strength numbers**

| What We Have | What We Need |
|--------------|--------------|
| ✅ Squadron/Gruppo designations | ❌ Total aircraft counts |
| ✅ Aircraft types (Spitfire, MC.202, etc.) | ❌ Operational aircraft counts |
| ✅ Base locations (Gambut, Benghazi, etc.) | ❌ Serviceability rates |
| ✅ Organizational hierarchy (Wing → Squadron) | ❌ Unit establishment strengths |

### Why This Matters

Without strength numbers, summaries are:
- ❌ Insufficient for scenario generation (can't balance forces)
- ❌ Incomplete for historical accuracy
- ❌ Unable to show theater-wide aggregate strength
- ❌ Can't calculate serviceability rates or readiness

**User Requirement**: "Strength data is going to need to be known eventually"

---

## Next Steps: Decision Point

### Option A: Accept Partial Data (Lower Quality)

**Pros**:
- Move forward immediately
- Use what we have (German data complete, Italian/British structure-only)
- Mark Italian/British summaries as Tier 3 "research_brief_created"

**Cons**:
- 57% of summaries incomplete
- Can't fulfill user's stated need for strength data
- Scenario generation will lack balance data

### Option B: Pursue Online Archival Sources (Historical Accuracy)

**Recommended Approach**: Exhaust reputable online archives for strength data

**Tier 1 Sources** (Official Archives - 90-95% confidence):

1. **Air Force Historical Research Agency (AFHRA)**
   - URL: https://www.afhra.af.mil/
   - Coverage: USAAF, RAF (lend-lease), Axis intelligence reports
   - Access: Free digital collections
   - Search: "Western Desert Air Force", "North Africa", "Regia Aeronautica"
   - Expected yield: RAF strength returns, USAAF intel reports

2. **UK National Archives - AIR Series**
   - URL: https://discovery.nationalarchives.gov.uk/
   - Series AIR 27: Squadron Operations Record Books (ORBs)
   - Series AIR 24: Commands/Groups Operations Record Books
   - Access: Some free digital, some require £3.50/document
   - Search: Specific squadrons (No. 112, No. 250, etc.)
   - Expected yield: Monthly strength returns in ORBs

3. **RAF Museum Research Portal**
   - URL: https://www.rafmuseum.org.uk/research/
   - Coverage: RAF squadron histories, operational records
   - Access: Some digitized, some require research request
   - Expected yield: Squadron establishment data

**Tier 2 Sources** (Curated Research - 75-85% confidence):

4. **Desert Air Force Research**
   - URL: desertairforce.org.uk (if exists)
   - Coverage: RAF Middle East, WDAF squadron histories
   - Access: Free online database
   - Expected yield: Squadron strength data from enthusiast research

5. **Italian Aviation Historical Sites**
   - Various forums and research sites
   - Coverage: Regia Aeronautica OOBs, squadron histories
   - Confidence: 70-80% (varies by source)

**Estimated Time**: 3-5 hours for online source research

**Pros**:
- Historically accurate, complete data
- Tier 1 (90%+) confidence ratings
- Fulfills user requirement for strength data

**Cons**:
- Requires online research time
- UK Archives may require document purchases (~£10-15 total)

---

## Remaining Work (After Decision)

### Phase 2: Data Completion

**If Strength Data Found**:
1. Regenerate 4 Italian/British summaries with complete strength data
2. Update confidence to Tier 1 (90%)
3. Update `EXTRACTION_SUMMARY.md`

**Current Work**:
- Aggregate existing 3 detailed air unit JSONs into summaries
- Create hybrid summaries (Nafziger snapshots + detailed aggregations)

### Phase 3: Integration (4 hours)

**Tasks**:
1. Add `air_support` sections to Army-level JSONs
   - Schema: Brief summary with aggregate strength, organizational hierarchy
   - Example: "Air support: RAF WDAF (21 squadrons, ~250 aircraft operational)"

2. Regenerate Army-level MDBook chapters with air narrative sections
   - Add "Air Support" section after ground forces breakdown
   - Narrative: 2-3 paragraphs describing air assets available

3. Create quarterly theater overview chapters
   - Multi-nation air forces snapshot per quarter
   - Shows Axis vs. Allied air strength comparisons

### Phase 4: Documentation (30 min)

**Updates**:
- `WORK_QUEUE_AIR.md` - Update status or archive
- `VERSION_HISTORY.md` - Document air forces summaries addition
- `PROJECT_SCOPE.md` - Update Phase 7 progress
- `README.md` - Add air summaries to project overview

---

## File Manifest

### Scripts Created
- `scripts/extract_nafziger_air_pdf.js` - Automated PDF parser (3 formats)
- `scripts/filter_north_africa_air.py` - (Mentioned in git status, not detailed)
- `scripts/find_air_strength_pdfs.py` - (Mentioned in git status, not detailed)
- `scripts/search_nafziger_air_1941.js` - (Mentioned in git status, not detailed)
- `scripts/regenerate_air_summaries_with_wikipedia.js` - (Mentioned in git status, not detailed)

### Data Files
- `data/output/air_summaries/*.json` - 7 quarterly summaries
- `data/output/air_summaries/EXTRACTION_SUMMARY.md` - Extraction documentation

### Session Documents
- `AIR_SESSION_2025_10_28.md` - Current session research findings
- `AIR_FORCES_PLANNING.md` - This file (project plan & status)
- `AIR_FORCES_COMPLETION_REPORT.md` - (In git status, needs review)
- `AIR_FORCES_SEARCH_REPORT.md` - (In git status, needs review)
- `ONLINE_SOURCES_FINDINGS.md` - (In git status, needs review)

### Schema
- `schemas/unified_toe_schema.json` - v3.1.0_air support (already exists)

---

## Quick Start for Next Session

### If Continuing Online Source Research:

```bash
# 1. Search AFHRA digital collections
#    URL: https://www.afhra.af.mil/
#    Search: "Western Desert Air Force" + date range 1941-1942

# 2. Search UK National Archives
#    URL: https://discovery.nationalarchives.gov.uk/
#    Search AIR 27 series: "Squadron No. 112" or specific squadron numbers
#    Download available digital ORBs

# 3. Extract strength data from found documents
#    Add to notes or temporary data files

# 4. Regenerate summaries with complete data
node scripts/extract_nafziger_air_pdf.js
# (Update script or create new aggregation script)
```

### If Accepting Partial Data:

```bash
# 1. Update summaries to Tier 3 for incomplete data
# Edit italian_1942q1_air_summary.json:
#   "tier": "partial_needs_research"
#   "confidence": 60

# 2. Move to integration phase
# Add air_support sections to Army JSONs
# Regenerate MDBook chapters

# 3. Mark as "best available" and document gaps
```

---

## Known Issues

1. **Encoding**: Degree symbols (°) display as "�" in some outputs (e.g., "50� Stormo")
2. **Coverage Gaps**: Only 4 quarters covered (1941-Q2, 1942-Q1, Q2, Q3) out of 52 needed
3. **Mixed Quality**: German data complete, Italian/British partial
4. **No WITW Cross-Reference**: Unit IDs not yet linked to WITW airgroup database (4,097 groups)

---

## User Directives

- **Priority**: Local primary sources FIRST, online sources ONLY if needed
- **Quality**: "Strength data is going to need to be known eventually"
- **Sources**: Approved reputable online sources (AFHRA, RAF Museum, UK Archives, Desert AF Research)
- **NOT Required**: Expensive books (Christopher Shores $200 Air War series)

---

## Session Handoff Checklist

**Before Ending Session**:
- [ ] Complete Tessin Vol 12 search (if not done)
- [ ] Document decision on online sources vs. partial data
- [ ] Update MCP memory with current status
- [ ] Commit planning documents to git
- [ ] Create session summary

**For Next Session**:
- [ ] Review `AIR_FORCES_PLANNING.md` (this file)
- [ ] Review `AIR_SESSION_2025_10_28.md` for research details
- [ ] Check todo list status
- [ ] Execute chosen approach (online sources OR integration)

---

**Last Updated**: 2025-10-28 (Session interrupted by VS Code crashes)
**Next Action**: Complete Tessin search, then DECISION POINT
