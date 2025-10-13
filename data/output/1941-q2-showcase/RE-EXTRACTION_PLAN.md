# Re-Extraction Plan: 9 Wikipedia-Affected Divisions

**Date**: 2025-10-13
**Session**: v3.0.0 schema compliance
**Purpose**: Rebuild 9 divisions with proper Tier 1/2 sources (no Wikipedia)

---

## Overview

After removing 26 Wikipedia citations from 9 divisions, we need to **re-extract** these units using only authorized Tier 1/2 sources. This ensures data quality and v3.0 compliance.

**Backup Location**: `data/output/1941-q2-showcase/wikipedia_versions/` (original files preserved)

**Reference**: See `WIKIPEDIA_VIOLATIONS_REFERENCE.md` for trace paths to primary sources

---

## Extraction Priority Order

### Priority 1: High Wikipedia Dependence (5+ citations removed)
1. **🇮🇳 5th Indian Division** - 8 citations removed
2. **🇿🇦 1st South African Division** - 5 citations removed
3. **🇮🇹 Ariete Division** - 4 citations removed

### Priority 2: Medium Dependence (2-3 citations removed)
4. **🇩🇪 15. Panzer-Division** - 2 citations removed
5. **🇮🇳 4th Indian Division** - 2 citations removed
6. **🇮🇹 Sabratha Division** - 2 citations removed

### Priority 3: Low Dependence (1 citation removed)
7. **🇳🇿 2nd New Zealand Division** - 1 citation removed
8. **🇬🇧 7th Armoured Division** - 1 citation removed
9. **🇮🇹 Bologna Division** - 1 citation removed + empty overview fix needed

---

## Authorized Sources by Nation

### British/Commonwealth Units

#### Tier 1 (Primary Sources - 90-95% confidence)
- **British Army Lists** (quarterly) - Officer rosters, unit assignments
  - Location: `Resource Documents/Great Britain Ministery of Defense Books/`
  - Files: `armylistapr1941grea`, `armylistjul1941grea`
- **War Diaries** (WO 169 series) - Daily operational records
  - National Archives reference: WO 169/1100-1150 (7th Armoured)
  - National Archives reference: WO 169/XXX (Indian divisions)
- **Regimental Histories** - Official unit histories

#### Tier 2 (Curated Web - 75-85% confidence)
- **desertrats.org.uk** - 7th Armoured Division OOB and operations
- **Imperial War Museum** - Documents and archives
- **Union Defence Force Archives** (South Africa)
- **South African Military History Society** - Unit compositions

### Indian Units (British Command)

#### Tier 1 (90-95% confidence)
- **Indian Army Lists** (quarterly) - British India Army rosters
- **War Diaries** - Indian division operational records
- **Regimental Histories** - Indian Army regiments

#### Tier 2 (75-85% confidence)
- **Imperial War Museum** - East Africa campaign documents
- **Battle of Keren archives** - 4th & 5th Indian Divisions

### New Zealand Units

#### Tier 1 (90-95% confidence)
- **Official History of New Zealand in the Second World War**
  - Available: New Zealand Electronic Text Collection
- **2NZEF Archives** - New Zealand Expeditionary Force records

#### Tier 2 (75-85% confidence)
- **Auckland War Memorial Museum** - Unit records
- **New Zealand Defence Force Archives**

### German Units

#### Tier 1 (90-95% confidence)
- **Tessin, Georg. Verbände und Truppen der deutschen Wehrmacht 1939-1945**
  - Location: `Resource Documents/tessin-georg-verbande.../`
  - 17 volumes covering all Wehrmacht units
  - **NOTE**: Currently .gz compressed format - needs extraction

#### Tier 2 (75-85% confidence)
- **Feldgrau.com** - Wehrmacht organizational database
- **Lexikon der Wehrmacht** - Unit histories and commanders
- **Bundesarchiv** - German Federal Archives

### Italian Units

#### Tier 1 (90-95% confidence)
- **TM E 30-420: Handbook on Italian Military Forces (1943)**
  - US War Department technical manual
  - Location: `Resource Documents/`
- **Italian Official Military Histories** - Comando Supremo publications

#### Tier 2 (75-85% confidence)
- **Comando Supremo** (comandosupremo.com) - Italian military history database
- **Niehorster WWII OOB** - Italian forces North Africa 1941
- **Tank Encyclopedia** - M13/40, L3/35 specifications (legitimate site, not wiki)

---

## Agent Workflow for Each Division

### Phase 1: Document Parsing
**Agent**: `document_parser` v2.0.0

**Input**:
```json
{
  "agent_id": "document_parser",
  "task_id": "parse_[nation]_[unit]_q2_1941",
  "inputs": {
    "nation": "[german|italian|british]",
    "quarter": "1941-Q2",
    "unit_designation": "[Full unit name]",
    "unit_type": "[division|corps]",
    "source_documents": ["[Tier 1 source paths]"],
    "source_tier": "tier_1"
  }
}
```

**Expected Output**:
- Raw unit data extracted from Tier 1 sources
- Commander information with appointment dates
- Brigade/regiment structure
- Equipment holdings (tanks, artillery, vehicles)
- **NO Wikipedia sources in validation.source array**

### Phase 2: Historical Research
**Agent**: `historical_research` v2.0.0

**Input**:
```json
{
  "agent_id": "historical_research",
  "task_id": "research_[nation]_[unit]_q2_1941",
  "inputs": {
    "nation": "[german|italian|british]",
    "quarter": "1941-Q2",
    "unit_designation": "[Full unit name]",
    "parsed_data": "[Output from document_parser]",
    "research_questions": [
      "Operational history Q2 1941",
      "Major engagements this quarter",
      "Supply status and logistics",
      "Combat effectiveness assessment"
    ],
    "allowed_sources": ["tier_1", "tier_2"],
    "forbidden_sources": ["wikipedia", "wikia", "fandom", "military_wiki"]
  }
}
```

**Expected Output**:
- Operational history with specific dates/battles
- Tactical doctrine and capabilities
- Strengths/weaknesses analysis
- Supply and logistics assessment
- **All sources verified as Tier 1/2**

### Phase 3: Validation & Consolidation
**Agent**: `schema_validator` v2.0.0

**Input**:
- Parsed document data
- Historical research data

**Validation Checks**:
1. Schema v3.0.0 compliance (supply_logistics, weather_environment)
2. NO Wikipedia sources in validation.source
3. Confidence score ≥75%
4. All required sections present
5. Equipment totals sum correctly

---

## Detailed Re-Extraction Tasks

### 1. 🇮🇳 5th Indian Division (Priority 1)

**Wikipedia Citations Removed**: 8
- Division organization structure
- Commander Mosley Mayne appointment
- Brigade compositions (9th, 10th, 29th)
- Battle of Keren participation

**Tier 1 Sources to Use**:
- Indian Army Lists Q2 1941
- War Diaries: 5th Indian Division (WO 169 series)
- Battle of Keren after-action reports

**Tier 2 Sources to Use**:
- Imperial War Museum: East African Campaign
- HyperWar: East African Campaign Chapter 9 (already cited)

**Key Data Points**:
- Commander: Major-General Mosley Mayne (April 1941)
- Location: East Africa (Eritrea) - NOT North Africa
- Brigades: 9th, 10th, 29th Indian Infantry Brigades
- Personnel: ~15,843
- Equipment: No tanks (infantry division), 72x 25-pdr artillery

**Current Confidence**: 78% → **Target**: 85%+

---

### 2. 🇿🇦 1st South African Division (Priority 1)

**Wikipedia Citations Removed**: 5
- Division history and commander
- Brigade compositions (1st, 2nd, 5th SA Infantry Brigades)

**Tier 1 Sources to Use**:
- Union Defence Force records
- British Army Lists Q2 1941 (South African units)
- South African Defence Force Archives

**Tier 2 Sources to Use**:
- South African Military History Society
- HyperWar: UK Mediterranean & Middle East Vol.II Appendix VIII (already cited)

**Key Data Points**:
- Commander: Brigadier-General George Brink (Aug 1940 - Mar 1942)
- Location: In transit (arrived Egypt 3 May 1941)
- Marmon-Herrington armoured cars (SA manufacture)
- Personnel: ~18,500
- Training at Mersa Matruh for desert warfare

**Current Confidence**: 72% → **Target**: 85%+

---

### 3. 🇮🇹 Ariete Division (Priority 1)

**Wikipedia Citations Removed**: 4
- Multiple Wikipedia articles (division, commander, M13/40 tank)
- Military Wiki / Fandom

**Tier 1 Sources to Use**:
- TM E 30-420: Handbook on Italian Military Forces
- Italian official histories (if accessible)

**Tier 2 Sources to Use**:
- Comando Supremo database (already cited)
- Tank Encyclopedia - M13/40, L3/35 (already cited)
- Historia Scripta (already cited)
- Niehorster WWII OOB (already cited)

**Key Data Points**:
- Commander: Generale Ettore Baldassarre
- Tank strength: 99x M13/40 medium, 24x L3/35 light (June 1941)
- Major operations: Tobruk assaults, Operation Battleaxe
- Supply issues: Sand filter problems in April

**Current Confidence**: 84% → **Target**: 88%+

**Note**: This division already has good Tier 2 sources, just needs Wikipedia removed

---

### 4. 🇩🇪 15. Panzer-Division (Priority 2)

**Wikipedia Citations Removed**: 2
- Wikipedia: 15th Panzer Division (Wehrmacht)
- Military Wiki: 15th Panzer Division

**Tier 1 Sources to Use**:
- **Tessin, Georg. Verbände und Truppen der deutschen Wehrmacht 1939-1945**
  - Volume covering Panzer divisions
  - **CRITICAL**: Extract .gz files first
  - Location: `Resource Documents/tessin-georg-verbande.../`

**Tier 2 Sources to Use**:
- Feldgrau.com: 15. Panzer-Division
- Lexikon der Wehrmacht
- Osprey Men-at-Arms #53: Rommel's Desert Army (already cited)

**Key Data Points**:
- Commanders (Q2 1941):
  - Gen. von Prittwitz (KIA 10 April)
  - Col. von Herff (acting 10 April - 16 June)
  - Gen. Neumann-Silkow (16 June onwards)
- Tank strength: 155 tanks (109 medium, 46 light)
- Part of Deutsches Afrikakorps
- Operation Battleaxe defensive operations

**Current Confidence**: 65% → **Target**: 85%+

**NOTE**: This is HIGH priority because current confidence is only 65% (below 75% minimum)

---

### 5. 🇮🇳 4th Indian Division (Priority 2)

**Wikipedia Citations Removed**: 2
- Brigade composition
- 11th Indian Infantry Brigade assignments

**Tier 1 Sources to Use**:
- British Army Lists April 1941 (already cited)
- War diaries: 4th Indian Division

**Tier 2 Sources to Use**:
- stefanov.no-ip.org/MagWeb article (already cited)
- Imperial War Museum

**Key Data Points**:
- Commander: Major-General Frank Messervy (April 1941)
- Brigades: 5th, 7th, 11th Indian Infantry Brigades
- Operation Battleaxe participation (partial division)
- Recent deployment from Battle of Keren

**Current Confidence**: 75% → **Target**: 85%+

---

### 6. 🇮🇹 Sabratha Division (Priority 2)

**Wikipedia Citations Removed**: 2
- Military Wiki - 60th Infantry Division Sabratha

**Tier 1 Sources to Use**:
- TM E 30-420: Handbook on Italian Military Forces

**Tier 2 Sources to Use**:
- Comando Supremo (multiple sources already cited)
- Niehorster WWII OOB (already cited)

**Key Data Points**:
- Full designation: 60ª Divisione di fanteria "Sabratha"
- Colonial division (North Africa deployment)
- Equipment: Infantry division, limited mechanization

**Current Confidence**: 82% → **Target**: 88%+

---

### 7. 🇳🇿 2nd New Zealand Division (Priority 3)

**Wikipedia Citations Removed**: 1
- Military Wiki - 2nd New Zealand Division

**Tier 1 Sources to Use**:
- Official History of New Zealand in the Second World War
- New Zealand Electronic Text Collection

**Tier 2 Sources to Use**:
- Auckland War Memorial Museum archives
- 2NZEF historical records

**Key Data Points**:
- Commander: Major-General Bernard Freyberg VC
- Brigades: 4th, 5th, 6th NZ Infantry Brigades
- Operation Battleaxe participation
- Elite Commonwealth division

**Current Confidence**: 85% → **Target**: 90%+

---

### 8. 🇬🇧 7th Armoured Division (Priority 3)

**Wikipedia Citations Removed**: 1
- Operation Battleaxe order of battle (Wikipedia)

**Tier 1 Sources to Use**:
- British Army Lists April 1941 (already cited)
- War Diaries WO 169/1100-1150 (already cited)
- Operation Battleaxe After-Action Reports (already cited)

**Tier 2 Sources to Use**:
- desertrats.org.uk (already cited)

**Key Data Points**:
- Commander: Major-General Michael O'Moore Creagh
- Tank strength: 190 tanks (100 Matilda II, 90 cruisers)
- Operation Battleaxe: 48% tank losses
- "Desert Rats" nickname

**Current Confidence**: 82% → **Target**: 88%+

**NOTE**: This division already has excellent Tier 1/2 sources, minimal re-work needed

---

### 9. 🇮🇹 Bologna Division (Priority 3)

**Wikipedia Citations Removed**: 1
- Wikipedia: 25th Infantry Division Bologna

**Tier 1 Sources to Use**:
- TM E 30-420 (already cited)
- Order-of-battle of the Italian Army, USA HQ G-2 July 1943 (already cited)

**Tier 2 Sources to Use**:
- Comando Supremo: Mario Marghinotti biographical entry (already cited)

**Key Data Points**:
- Full designation: 25ª Divisione di Fanteria 'Bologna'
- Commander: Generale Mario Marghinotti (March 1941)
- Binary division: 2 infantry regiments (not 3)
- Semi-motorized (AS-type)
- **CRITICAL**: Division Overview section is EMPTY - needs content

**Current Confidence**: 85% → **Target**: 90%+

**Additional Task**: Fill empty Division Overview section with:
- Formation date and home station
- Deployment to Libya timeline
- Q2 1941 status (rebuilding from Operation Compass losses)
- Participation in Rommel's offensive and Tobruk siege

---

## Execution Plan

### Approach 1: Autonomous Agent Execution (Recommended)
```bash
npm run start:autonomous
```

Then launch 9 parallel agent tasks for each division using Claude Code Task tool:

**Example for 5th Indian Division**:
```
Use Task tool with general-purpose agent:

"Extract 5th Indian Infantry Division TO&E for 1941-Q2 using ONLY Tier 1/2 sources.

FORBIDDEN: Wikipedia, Military Wiki, Fandom, Wikia

REQUIRED TIER 1 SOURCES:
- Indian Army Lists Q2 1941
- War Diaries: 5th Indian Division
- Battle of Keren after-action reports

TIER 2 ALLOWED:
- Imperial War Museum East African Campaign
- HyperWar East African Campaign Chapter 9

EXTRACT:
- Unit identification (designation, type, quarter)
- Command (commander, staff, HQ location)
- Personnel strength (officers, NCOs, enlisted)
- Equipment (artillery, vehicles, small arms)
- Subordinate units (9th, 10th, 29th Brigades)
- Operational history Q2 1941 (East Africa Campaign)
- Tactical doctrine and combat effectiveness
- Supply status

OUTPUT: Complete unit JSON following unified_toe_schema.json v3.0.0

TARGET CONFIDENCE: 85%+

Verify NO Wikipedia sources in validation.source array."
```

### Approach 2: Manual Extraction (Slower but More Control)
```bash
npm run start:claude
```

Generate prompts for each division, process manually one by one.

---

## Success Criteria

### Per Division
- ✅ Schema v3.0.0 compliant
- ✅ Confidence ≥75% (target 85%+)
- ✅ NO Wikipedia sources in validation.source
- ✅ All required sections present and populated
- ✅ Equipment totals validated
- ✅ Operational history specific to Q2 1941

### Overall Project
- ✅ All 9 divisions re-extracted with Tier 1/2 sources
- ✅ Bologna & Trieste Division Overview sections filled
- ✅ All 18 showcase chapters v3.0 compliant
- ✅ 100% pass rate on `npm run validate:sources`
- ✅ Average confidence 82%+ across all divisions

---

## Timeline Estimate

### Parallel Execution (Recommended)
- **Setup**: 15 minutes (agent configuration)
- **Extraction**: 2-3 hours (9 divisions in parallel batches of 3)
- **Validation**: 30 minutes (schema + sources check)
- **Chapter Regeneration**: 10 minutes
- **Total**: ~3-4 hours

### Sequential Execution
- **Per Division**: 20-30 minutes
- **Total**: 3-4.5 hours (9 divisions × 20-30 min)

---

## Post-Extraction Tasks

1. **Validate All Units**:
   ```bash
   npm run validate:v3 data/output/1941-q2-showcase/consolidated_units/*.json
   npm run validate:sources data/output/1941-q2-showcase/consolidated_units/
   ```

2. **Regenerate MDBook Chapters**:
   ```bash
   node scripts/generate_mdbook_chapters.js
   ```

3. **Compare with Wikipedia Versions**:
   ```bash
   # Diff confidence scores
   # Verify data quality improvements
   # Document any data gaps filled
   ```

4. **Update Documentation**:
   - Update `SESSION_SUMMARY.md`
   - Create `RE-EXTRACTION_COMPLETE.md` report
   - Update `SHOWCASE_GAPS.md` with resolved items

---

## Risk Mitigation

### Risk: Tessin Sources Not Accessible (German units)
**Mitigation**:
- Extract .gz compressed files first
- If still inaccessible, use Tier 2 (Feldgrau, Lexikon der Wehrmacht)
- Accept 75% confidence minimum for German units until Tessin accessible

### Risk: Tier 1 Sources Missing Key Data
**Mitigation**:
- Escalate to Tier 2 per source_waterfall.js logic
- Document data gaps in validation.known_gaps
- Flag for future enhancement when better sources available

### Risk: Confidence Scores Below 75%
**Mitigation**:
- Cross-reference multiple Tier 2 sources
- Use interpolation from adjacent quarters (Q1, Q3)
- Document assumptions in validation.assumptions_made

---

**Document Status**: COMPLETE - Ready for execution
**Last Updated**: 2025-10-13
**Next Action**: Execute re-extraction for 9 divisions using agents
