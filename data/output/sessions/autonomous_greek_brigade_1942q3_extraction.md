# Greek Brigade (1942-Q3) - Autonomous Extraction Brief

**UNIT**: Greek Brigade
**NATION**: british (Greek forces under British command)
**QUARTER**: 1942q3
**ORGANIZATION_LEVEL**: brigade
**SCHEMA_TYPE**: brigade_toe

---

## HISTORICAL CONTEXT

**Formation History**:
- Formed from Greek Army units evacuated to Egypt after Greece fell to Germany (April 1941)
- Initially organized as 3 infantry battalions under British Middle East Command
- Greek officers, British equipment, British tactical doctrine
- Fought with distinction at El Alamein (July-November 1942)
- Part of multinational Allied coalition in North Africa

**Command (Estimated)**:
- **Commander**: Brigadier Panyotakis (Greek officer under British command - REQUIRES VERIFICATION)
- **Rank**: Brigadier
- **Parent Formation**: British 8th Army (attached to various divisions)

**Personnel Strength (Estimate)**:
- **Total**: ~3,000-4,000 men (standard brigade strength)
- Greek nationals who escaped from Greece
- British supporting personnel (liaison, logistics)

**Equipment**:
- **Rifles**: Lee-Enfield No.1 Mk III (British standard)
- **LMG**: Bren guns
- **Artillery**: British 25-pounder field guns
- **AT Guns**: British 2-pounder/6-pounder
- **Vehicles**: British trucks (Morris, Bedford)
- **NO TANKS** - infantry brigade

**Organization Structure**:
- 3 Infantry Battalions
- Brigade HQ
- Artillery support (attached British guns)
- Support companies (signals, transport, medical)

---

## PRIMARY SOURCES (Tier 2 - LIMITED LOCAL DOCS)

### Tier 1 (Local - Limited)
❌ **No dedicated Greek Brigade documents in local sources**
⚠️ **British Army Lists Q3 1942** - May have references to attached Greek units

### Tier 2 (Curated Web - PRIMARY for this unit)
✅ **Niehorster.org** - Excellent for Allied OOB
✅ **historyofwar.org** - Greek forces in North Africa
✅ **Nafziger Collection** - May have Greek Brigade OOB files
✅ **Imperial War Museum** - British/Allied units documentation
✅ **Hellenic Army General Staff** - Greek military history records

### Tier 3 (Archives - if needed)
- National Archives UK (WO 201 - Middle East operations)
- Imperial War Museum archives
- Greek military archives (Hellenic Army Historical Directorate)

---

## EXTRACTION STRATEGY

**Phase 1: Document Parser**
- Search British Army Lists Q3 1942 for attached Greek units
- Search Niehorster.org for Greek Brigade 1942
- Search historyofwar.org for Greek forces El Alamein
- Extract equipment allocations (British standard TO&E)

**Phase 2: Historical Research**
- Cross-reference commander name (Panyotakis vs other Greek officers)
- Verify personnel strength (~3,000-4,000)
- Confirm equipment types (British lend-lease)
- Document unit actions Q3 1942 (El Alamein preparations)

**Phase 3: Organization Building**
- Structure: Brigade HQ → 3 Battalions → Support companies
- British TO&E patterns for brigade structure
- Greek battalion organization (3-4 companies each)

**Phase 4: Equipment Reconciliation**
- British equipment only (no Greek weapons)
- Standard British brigade allocation:
  - Rifles: ~2,500-3,000
  - Bren guns: ~80-100
  - 25-pounders: 12-24 guns (brigade artillery)
  - 2-pounder AT: 6-12 guns
  - Vehicles: ~200-300 (trucks, carriers)

**Phase 5: Validation**
- Confidence target: ≥75% (acceptable for Tier 2 sources)
- Gap documentation required for:
  - Exact commander name (if not confirmed)
  - Precise equipment quantities
  - Battalion commanders
  - Operational readiness percentages

---

## MDBOOK CHAPTER SPECIAL NOTES

### Section 3: Command
Highlight Greek exile context:
- Greek officers escaped from mainland Greece (April 1941)
- Maintained Greek military traditions under British command
- Fought to liberate homeland

### Section 12: Tactical Doctrine
- British training and tactics
- Greek fighting spirit and motivation
- Infantry-focused (no armor assets)

### Section 15: Historical Context
- Greece fell to Germany April 1941
- Greek forces evacuated to Egypt
- Reorganized as brigade under British Middle East Command
- Q3 1942: Preparation for El Alamein offensive
- Post-Alamein: Fought in Tunisia, Italy, Greece liberation

### Section 16: Data Quality & Known Gaps
**Expected Tier**: 2 (Review Recommended)
**Expected Confidence**: 75-80%

**Known Gaps** (document in chapter):
- Commander name may require verification
- Exact battalion organization (estimated from British patterns)
- Precise equipment quantities (estimated from brigade standard)
- Supply allocations (dependent on British theater logistics)

---

## SUPPLY/LOGISTICS (Section 6 - NEW v3.0)

**Estimate from British theater context**:
- **supply_status**: "Adequate - integrated into British 8th Army logistics"
- **operational_radius_km**: 250 (attached to various divisions)
- **fuel_reserves_days**: 8 (British supply network)
- **ammunition_days**: 12 (British ammunition supply)
- **water_liters_per_day**: 5.0 (desert standard)

---

## WEATHER/ENVIRONMENT (Section 7 - NEW v3.0)

**1942-Q3 (July-September)**:
- **season_quarter**: "1942-Q3 (July-September) - Mid to Late Summer"
- **temperature_range_c**: {"min": 22, "max": 40}
- **terrain_type**: "Coastal plain near El Alamein, rocky desert"
- **storm_frequency_days**: 1 (reduced storms in summer)
- **daylight_hours**: 13.0

---

## OUTPUT PATHS

**Unit JSON**: `D:\north-africa-toe-builder\data\output\units\british_1942q3_greek_brigade_toe.json`

**MDBook Chapter**: `D:\north-africa-toe-builder\data\output\chapters\chapter_british_1942q3_greek_brigade.md`

---

## SUCCESS CRITERIA

✅ Schema-compliant JSON (brigade_toe, v3.1.0)
✅ Confidence ≥ 75%
✅ Tier 2 extraction (review_recommended)
✅ Gap documentation for unverified fields
✅ MDBook chapter with 18 sections (v3.1 template)
✅ Supply/logistics data (Section 6)
✅ Weather/environment data (Section 7)

---

**EXTRACTION DATE**: 2025-10-21
**AGENT VERSION**: Autonomous Orchestrator v4.0
