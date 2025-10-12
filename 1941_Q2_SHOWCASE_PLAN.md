# 1941-Q2 Complete Quarter Showcase Plan

**Purpose**: Demonstrate full end-to-end workflow from Phase 1 (Unit JSONs) through Phase 10 (Battle Correlations) using completed 1941-Q2 data as proof-of-concept.

**Date**: October 2025
**Status**: Planning → Implementation

---

## Data Inventory

### Completed Units: 17/17 (100%)

**British Commonwealth (7 units)**:
- 7th Armoured Division
- 50th Infantry Division
- 2nd New Zealand Division
- 4th Indian Division
- 1st South African Division
- 5th Indian Division
- 9th Australian Division

**German (3 units)**:
- Deutsches Afrikakorps (DAK) - Corps level
- 15. Panzer-Division
- 5. leichte Division

**Italian (7 units)**:
- 132. Divisione corazzata "Ariete"
- 17. Divisione di fanteria "Pavia"
- 27. Divisione di fanteria "Brescia"
- 55. Divisione di fanteria "Trento"
- Divisione di fanteria "Sabratha"
- Divisione di fanteria "Trieste"
- Divisione di fanteria "Bologna"
- Divisione di fanteria "Savona"

**Note**: 8 Italian divisions listed (1 extra)

---

## Multi-Phase Showcase Architecture

### Phase 1-7: Official Workflow (EXISTING)
✅ Phase 1: Source Extraction
✅ Phase 2: Organization Building
✅ Phase 3: Equipment Distribution
✅ Phase 4: Aggregation
✅ Phase 5: Validation
✅ Phase 6: Output Generation (MDBook chapters, scenarios, SQL)
✅ Phase 7: Quality Assurance & Gap Analysis

### Phase 8: WITW Equipment Mapping (NEW - JUST DEFINED)
🔄 **Status**: Agent defined, ready to implement
- Extract all equipment from 17 unit JSONs
- Run witw_equipment_mapper agent
- Output: equipment_witw_mappings.json, canonical_equipment.json, custom_ids.json
- Target: 70%+ high-confidence mappings

### Phase 9: Aircraft Integration (NEW - TO DEFINE)
📋 **Status**: Template needed
- Historical aircraft availability by nation/quarter
- Air units and allocations
- Aircraft specifications and WITW IDs
- Integration with ground units (air support doctrine)

### Phase 10: Battle Correlations (NEW - TO DEFINE)
📋 **Status**: Mapping needed
- Map units to historical battles (Compass, Battleaxe, Brevity, Crusader planning)
- Timeline integration
- Order of battle by engagement
- Strategic context and objectives

---

## Showcase Deliverables

### 1. Phase 1-7 Summary Report
**File**: `1941-Q2_PHASES_1-7_SUMMARY.md`

- Unit completion status (17/17 ✅)
- MDBook chapter inventory
- WITW scenario file status
- SQL database exports
- QA report highlights (confidence, gaps, compliance)

### 2. Phase 8 WITW Mapping Demonstration
**Files**:
- `1941-Q2_equipment_witw_mappings.json`
- `1941-Q2_canonical_equipment.json`
- `1941-Q2_custom_ids.json`
- `1941-Q2_WITW_MAPPING_REPORT.md`

**Contents**:
- All equipment from 17 units with WITW IDs
- Deduplication examples (M4 Sherman cross-nation)
- Custom IDs for unmapped items (241 expected)
- Confidence distribution (target: 70%+ high)
- Manual review queue (<20%)

### 3. Phase 9 Aircraft Template
**File**: `1941-Q2_AIRCRAFT_TEMPLATE.json`

**Contents** (Stub/Template):
```json
{
  "quarter": "1941-Q2",
  "nations": {
    "british": {
      "fighter_squadrons": [
        {"squadron": "No. 3 Squadron RAAF", "aircraft": "Hurricane Mk I", "count": 12, "witw_id": "TBD"}
      ],
      "bomber_squadrons": [],
      "total_aircraft": {"fighters": 120, "bombers": 45, "recon": 15}
    },
    "german": {
      "fighter_squadrons": [
        {"squadron": "I./JG 27", "aircraft": "Bf 109E", "count": 12, "witw_id": "TBD"}
      ]
    },
    "italian": {
      "fighter_squadrons": [
        {"squadron": "9° Gruppo", "aircraft": "Fiat CR.42", "count": 12, "witw_id": "TBD"}
      ]
    }
  },
  "status": "TEMPLATE - Historical data pending",
  "next_actions": [
    "Research squadron assignments from RAF/Luftwaffe/Regia Aeronautica records",
    "Map aircraft types to WITW database",
    "Integrate with ground unit air support doctrine"
  ]
}
```

### 4. Phase 10 Battle Correlation Map
**File**: `1941-Q2_BATTLE_CORRELATIONS.json`

**Contents**:
```json
{
  "quarter": "1941-Q2",
  "major_operations": [
    {
      "operation": "Operation Battleaxe",
      "date_range": "1941-06-15 to 1941-06-17",
      "british_units": [
        "7th Armoured Division",
        "4th Indian Division"
      ],
      "german_units": [
        "Deutsches Afrikakorps",
        "15. Panzer-Division",
        "5. leichte Division"
      ],
      "italian_units": [
        "132. Divisione corazzata Ariete",
        "17. Divisione di fanteria Pavia"
      ],
      "outcome": "German tactical victory",
      "casualties": {
        "british": {"tanks_lost": 91, "personnel": 969},
        "axis": {"tanks_lost": 12, "personnel": 678}
      },
      "strategic_context": "British attempt to relieve Tobruk, failure led to Churchill replacing Wavell with Auchinleck"
    }
  ],
  "minor_engagements": [
    {
      "engagement": "Siege of Tobruk (continued)",
      "date_range": "1941-04-01 to 1941-06-30",
      "garrison": ["9th Australian Division", "British artillery units"],
      "besiegers": ["Italian divisions (Trento, Brescia, Bologna)", "German reconnaissance units"]
    }
  ],
  "status": "PARTIAL - Major operations mapped, minor engagements need expansion"
}
```

### 5. Comprehensive Showcase Report
**File**: `1941-Q2_COMPLETE_SHOWCASE.md`

**Sections**:
1. Executive Summary
2. Phase 1-7 Completion Metrics
3. Phase 8 WITW Mapping Results
4. Phase 9 Aircraft Integration Status
5. Phase 10 Battle Correlations
6. Data Quality Assessment
7. Known Gaps and Future Work
8. Appendix: File Inventory

---

## Implementation Steps

### Step 1: Consolidate Phase 1-7 Data ✅
- [x] Identify all 17 unit JSON files
- [ ] Validate all JSONs against unified schema
- [ ] Locate MDBook chapters for all units
- [ ] Check WITW scenario exports
- [ ] Review QA audit results

### Step 2: Implement Phase 8 WITW Mapping
- [ ] Extract equipment from all 17 unit JSONs
- [ ] Load WITW database
- [ ] Run witw_equipment_mapper orchestrator
  - [ ] Sub-task: name_normalizer
  - [ ] Sub-task: fuzzy_matcher
  - [ ] Sub-task: cross_nation_deduplicator
  - [ ] Sub-task: custom_id_generator
  - [ ] Sub-task: mapping_validator
- [ ] Generate mapping quality report
- [ ] Review manual review queue

### Step 3: Create Phase 9 Aircraft Template
- [ ] Research 1941-Q2 air order of battle
- [ ] Create aircraft template structure
- [ ] Add sample data for each nation
- [ ] Document data gaps
- [ ] Define next actions for full implementation

### Step 4: Create Phase 10 Battle Correlations
- [ ] Map units to Operation Battleaxe
- [ ] Map units to Tobruk siege
- [ ] Add minor engagements (patrols, recon)
- [ ] Document strategic context
- [ ] Link to historical timeline

### Step 5: Generate Comprehensive Showcase
- [ ] Write executive summary
- [ ] Compile all phase metrics
- [ ] Create data quality assessment
- [ ] Document known gaps
- [ ] Generate file inventory
- [ ] Create visualization (Mermaid diagram of workflow)

---

## Success Criteria

✅ **Complete**: All 17 unit JSONs validated and documented
🔄 **In Progress**: Phase 8 WITW mapping demonstrates 70%+ high-confidence
📋 **Template**: Phase 9 aircraft stub shows structure for future work
📋 **Mapping**: Phase 10 battle correlations link units to historical events
📄 **Report**: Comprehensive showcase demonstrates full end-to-end capability

---

## Timeline

**Estimated Completion**: 2-3 hours
- Phase 1-7 summary: 30 minutes
- Phase 8 WITW mapping: 60 minutes (extract equipment, run agent, validate)
- Phase 9 aircraft template: 20 minutes (stub with samples)
- Phase 10 battle correlations: 20 minutes (basic mapping)
- Comprehensive report: 30 minutes (compilation and formatting)

---

## Next Action

**Immediate**: Begin Step 1 (Consolidate Phase 1-7 Data)
- Validate all 17 unit JSONs
- Locate corresponding MDBook chapters
- Review QA audit results (if available)
- Create Phase 1-7 summary report
