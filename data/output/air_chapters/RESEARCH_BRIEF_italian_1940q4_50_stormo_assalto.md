# Research Brief: 50° Stormo Assalto (1940-Q4)

**Date**: 2025-10-28
**Unit**: 50° Stormo Assalto
**Nation**: Italian (Regia Aeronautica)
**Quarter**: 1940-Q4 (Operation Compass)
**Status**: ❌ **TIER 1/2 SOURCE VALIDATION FAILED**

---

## Executive Summary

**EXTRACTION BLOCKED**: Cannot proceed with data extraction for 50° Stormo Assalto (1940-Q4) due to **CRITICAL SOURCE VALIDATION FAILURE**.

**Issue**: Seed data sources (Comando Supremo, Wikipedia 5ª Squadra Aerea) do **NOT meet Tier 1/2 requirements** for air forces extraction per agent catalog validation rules.

---

## Source Validation Analysis

### Sources Listed in Seed Data

From `north_africa_air_units_seed_COMPLETE.json`:
```json
{
  "designation": "50° Stormo Assalto",
  "aircraft_type": "Breda Ba.65 / Caproni Ca.310",
  "type": "assault_stormo",
  "parent_formation": "5ª Squadra Aerea",
  "quarters": ["1940-Q2", "1940-Q3", "1940-Q4"],
  "battles": ["Operation Compass"],
  "locations": ["Sorman"],
  "confidence": 85,
  "notes": "Land attack wing. Part of 5ª Squadra Aerea western sector command at war start",
  "sources": [
    "Comando Supremo",
    "Wikipedia 5ª Squadra Aerea"
  ]
}
```

### Tier 1/2 Validation Requirements

Per `agents/air_forces_agent_catalog.json` (air_document_parser agent):

**✅ ALLOWED Sources (Tier 1/2 ONLY)**:
- Nafziger Collection (air unit OOB documents)
- WITW _airgroup.csv database (4,097 air groups)
- WITW _aircraft.csv database (aircraft specifications)
- **Chris Shores' Air War series** (North Africa volumes) ✅ **PRIMARY SOURCE NEEDED**
- Squadron/Group histories (official unit histories)
- Luftwaffe war diaries (KTB)
- RAF Operations Record Books (ORBs)
- USAAF combat reports
- Asisbiz.com (air unit histories **with citations**)
- Axis History Forum (**ONLY posts with primary source citations**)
- National Archives air combat records
- **Comando Supremo** (❓ **CONDITIONAL - needs verification**)

**❌ FORBIDDEN Sources**:
- **Wikipedia (ANY language)** ❌ ← **SEED DATA USES THIS**
- Wikia/Fandom aviation sites
- Uncited web sources
- Forum posts without citations

### Validation Result

| Source | Status | Issue |
|--------|--------|-------|
| "Comando Supremo" | ❓ **NEEDS VERIFICATION** | Not explicitly listed in Tier 1/2 allowed sources. May be acceptable if it refers to **Italian official records** (explicitly allowed), but seed data doesn't specify which Comando Supremo resource (website vs archives vs official histories). |
| "Wikipedia 5ª Squadra Aerea" | ❌ **FORBIDDEN** | Wikipedia is **explicitly banned** for air forces extraction per agent catalog validation rules. |

**Overall Status**: ❌ **FAILED** - Primary seed source is Wikipedia (forbidden)

---

## Data Available from Seed

### Unit Identification
- **Designation**: 50° Stormo Assalto
- **Type**: assault_stormo (ground attack wing)
- **Parent Formation**: 5ª Squadra Aerea (5th Air Fleet)
- **Base**: Sorman (Libya)
- **Period**: 1940-Q2 through 1940-Q4

### Aircraft Types (REQUIRES VARIANT-LEVEL DETAIL)
Seed data lists:
- Breda Ba.65 (❌ **NOT SPECIFIC** - needs variant: Ba.65bis? Ba.65 A-80?)
- Caproni Ca.310 (❌ **NOT SPECIFIC** - needs variant: Ca.310 Libeccio? Ca.310bis?)

**CRITICAL ISSUE**: Agent catalog requires **NO generic aircraft entries**. All variants must be specific:
- ✅ CORRECT: "Breda Ba.65bis", "Caproni Ca.310 Libeccio"
- ❌ WRONG: "Ba.65", "Ca.310"

### Operations
- **Battle**: Operation Compass (December 1940 - February 1941)
- **Role**: Land attack/ground assault

### Confidence
- Seed confidence: 85% (but based on forbidden Wikipedia source)

---

## Required Research to Proceed

### Priority 1: Tier 1/2 Source Acquisition (MANDATORY)

**Must obtain ONE of the following**:

1. **Christopher Shores - Air War for Yugoslavia, Greece and Crete 1940-41** OR **Shores - Dust Clouds in the Middle East** (1940-1942)
   - Check for 50° Stormo Assalto references during Operation Compass
   - Verify aircraft types, squadriglie composition, operations

2. **Italian Official Records** (Comando Supremo archives - PRIMARY SOURCES)
   - 5ª Squadra Aerea operational records October-December 1940
   - 50° Stormo Assalto war diary (if exists)
   - Aircraft strength returns for Q4 1940

3. **Asisbiz.com** (IF has citations to primary Italian sources)
   - Check for 50° Stormo Assalto unit history page
   - **ONLY acceptable if page cites Comando Supremo archives or Italian official histories**
   - Uncited Asisbiz pages are NOT acceptable

4. **WITW _airgroup.csv Database**
   - Search for "50° Stormo" or "50 Stormo Assalto"
   - If present: Extract aircraft counts, WITW IDs, parent formation
   - Cross-reference with game _aircraft.csv for Ba.65/Ca.310 variants

### Priority 2: Aircraft Variant Resolution (CRITICAL)

**Must identify SPECIFIC variants** for:

1. **Breda Ba.65**
   - Likely variants in North Africa 1940:
     - Ba.65bis (improved model)
     - Ba.65 A-80 (assault variant)
   - Check Shores/Italian records for exact variant designation
   - Need WITW ID for scenario export compatibility

2. **Caproni Ca.310**
   - Likely variants:
     - Ca.310 Libeccio (reconnaissance/light bomber)
     - Ca.310bis (improved model)
   - Verify operational variant in Libya Q4 1940
   - Need WITW ID

### Priority 3: Organizational Structure

**Must determine**:
- Number of gruppi within 50° Stormo
- Squadriglie composition (how many squadriglie per gruppo?)
- Aircraft distribution (how many Ba.65 vs Ca.310?)
- Personnel counts (pilots, ground crew, total)
- Commander (name, rank)

### Priority 4: Operations Data

**For Operation Compass (December 1940)**:
- Sorties flown (total and by mission type)
- Losses (combat and operational)
- Claims (ground targets destroyed)
- Supply status
- Base relocations

---

## Extraction Decision

**STATUS**: ❌ **EXTRACTION BLOCKED**

**Reason**: Source validation failure (Wikipedia forbidden, Comando Supremo not verified)

**Next Steps**:

### Option A: Research and Extract (RECOMMENDED)
1. Acquire Shores' Air War series (Volume 1: 1940-1942)
2. Search for 50° Stormo Assalto references
3. Extract Tier 1 data conforming to agent catalog requirements
4. Resolve aircraft variants to specific models
5. Proceed with full extraction

### Option B: Research Brief Only (CURRENT)
1. Document source validation failure
2. Create this research brief
3. Mark unit as `research_brief_created` (Tier 4)
4. Add to queue for future research when sources available

### Option C: Skip Unit (NOT RECOMMENDED)
1. Remove from seed data
2. Mark as "insufficient sources"
3. ❌ **VIOLATES PROJECT SCOPE** - seed data is authoritative

---

## Recommended Action

**IMMEDIATE**:
1. ✅ Create this research brief (DONE)
2. Generate minimal JSON file with Tier 4 status
3. Generate MDBook chapter documenting source gap

**FUTURE SESSION** (when Shores Air War Vol 1 available):
1. Re-extract with Tier 1/2 sources
2. Resolve aircraft variants
3. Upgrade to Tier 1 (production_ready) or Tier 2 (review_recommended)

---

## Notes

- Italian air units in early war (1940-Q4) have limited English-language documentation
- Shores' Air War series is **THE authoritative source** for Mediterranean air operations
- Christopher Shores specifically covers Italian Regia Aeronautica units in detail
- WITW database may have simplified data but provides variant cross-reference
- Ba.65 and Ca.310 were both obsolescent by 1940 but still in service
- Sorman airfield was in western Libya (Tripolitania), not Cyrenaica combat zone

---

## Tier Assignment

**Current Tier**: 4 - `research_brief_created`

**Why Tier 4**:
- No Tier 1/2 sources accessed
- Aircraft variants not specific
- No operations data
- No personnel data
- Minimal structure information

**Path to Tier 1** (production_ready):
- Acquire Shores Air War Vol 1
- Extract complete aircraft inventory with specific variants
- Document operations during Operation Compass
- Verify organizational structure (gruppi/squadriglie)
- Include WITW IDs for scenario export

---

**Generated**: 2025-10-28
**Agent**: air_forces_extraction_agent
**Next Review**: When Tier 1/2 sources become available
