# MDBook Chapter Template - TO&E Unit Documentation

**Version:** 3.1
**Updated:** 2025-10-15
**Purpose:** Standard format for all MDBook chapters generated from TO&E JSON files (Ground Forces)

---

## Overview

This template defines the standard structure for military unit chapters in the North Africa TO&E MDBook. All chapters must follow this format to ensure consistency and readability.

---

## Required Sections (18 Total)

### 1. Header

```markdown
# [Unit Designation]

**[Nation] Forces • [Quarter] • [Theater/Location]**

---
```

**Example:**
```markdown
# 7th Armoured Division "Desert Rats"

**British Empire Forces • 1940 Q2 (April-June) • Western Desert, Egypt**

---
```

### 2. Division/Unit Overview

Brief 2-3 paragraph narrative introduction covering:
- Unit history and formation
- Nickname/insignia (if applicable)
- Strategic role
- Commander information (overview - detailed info in Command section)

### 3. Command Section

```markdown
## Command

**Divisional Commander**: [Name]
**Rank**: [Rank]
**Appointed**: [Date]
**Service**: [Background]

**Headquarters**: [Location]
**Parent Formation**: [Higher HQ]

**Division Staff**: [Number] personnel
- Officers: [Number]
- NCOs: [Number]
- Enlisted: [Number]
```

### 4. Personnel Strength

```markdown
## Personnel Strength

| Category | Count | Percentage |
|----------|-------|------------|
| **Total Personnel** | **[Total]** | 100% |
| Officers | [Count] | [%] |
| NCOs | [Count] | [%] |
| Other Ranks | [Count] | [%] |
```

---

## 5-8. Equipment Tables with Variant Breakdowns

**Sections 5-8 cover: Armoured Strength, Artillery Strength, Armoured Cars, Infantry Weapons, Transport & Vehicles**

### CRITICAL FORMAT REQUIREMENT

**ALL equipment tables MUST use variant breakdown format:**

### Tank Summary Table

```markdown
## Armoured Strength

### Summary

[Narrative context about tank strength]

| Category | Total | Operational | Readiness |
|----------|-------|-------------|-----------|
| **All Tanks** | **[Total]** | **[Operational]** | **[%]** |
| **Medium Tanks (Cruisers)** | **[Total]** | **[Operational]** | **[%]** |
| ↳ [Variant 1] | [Count] | [Operational] | [%] |
| ↳ [Variant 2] | [Count] | [Operational] | [%] |
| ↳ [Variant 3] | [Count] | [Operational] | [%] |
| **Light Tanks** | **[Total]** | **[Operational]** | **[%]** |
| ↳ [Variant 1] | [Count] | [Operational] | [%] |
| **Heavy Tanks** | **[Total]** | **[Operational]** | **[%]** |
| ↳ [Variant 1] | [Count] | [Operational] | [%] |
```

**ACTUAL EXAMPLE (British 7th Armoured):**

```markdown
| Category | Total | Operational | Readiness |
|----------|-------|-------------|-----------|
| **All Tanks** | **228** | **220** | **96.5%** |
| **Medium Tanks (Cruisers)** | **69** | **66** | **95.7%** |
| ↳ A13 Mk II (Cruiser Mk IV) | 44 | 42 | 95.5% |
| ↳ A10 Cruiser Mk II | 10 | 10 | 100% |
| ↳ A9 Cruiser Mk I | 9 | 8 | 88.9% |
| ↳ Matilda II (Infantry Tank) | 6 | 6 | 100% |
| **Light Tanks** | **159** | **152** | **95.6%** |
| ↳ Light Tank Mk VI | 159 | 152 | 95.6% |
| **Heavy Tanks** | **0** | **0** | **N/A** |
```

### Artillery Summary Table

```markdown
## Artillery Strength

| Type | Total | Operational | Caliber |
|------|-------|-------------|---------|
| **Field Artillery** | **[Total]** | **[Operational]** | - |
| ↳ [Variant 1] | [Count] | [Operational] | [Caliber] |
| ↳ [Variant 2] | [Count] | [Operational] | [Caliber] |
| **Anti-Tank** | **[Total]** | **[Operational]** | - |
| ↳ [Variant 1] | [Count] | [Operational] | [Caliber] |
| **Anti-Aircraft** | **[Total]** | **[Operational]** | - |
| ↳ [Variant 1] | [Count] | [Operational] | [Caliber] |
| **Total Artillery** | **[Grand Total]** | **[Operational]** | - |

### [Variant 1 Name] - [Count] guns

**EVERY variant listed in the table MUST have a detail section**

**Specifications**:
- **Caliber**: [Size]
- **Range**: [Distance]
- **Projectile Weight**: [Weight]
- **Rate of Fire**: [Rounds per minute]

**Combat Performance**: [Description of effectiveness, role, strengths/weaknesses]

---

### [Variant 2 Name] - [Count] guns

[Repeat for EVERY variant in all categories: field artillery, AT, AA]
```

**ACTUAL EXAMPLE (British 7th Armoured):**

```markdown
| Type | Total | Operational | Caliber |
|------|-------|-------------|---------|
| **Field Artillery** | **96** | **96** | - |
| ↳ Ordnance QF 25-pounder | 72 | 72 | 87.6mm |
| ↳ QF 4.5-inch Howitzer | 24 | 24 | 114mm |
| **Anti-Tank** | **48** | **48** | - |
| ↳ Ordnance QF 2-pounder | 48 | 48 | 40mm |
| **Anti-Aircraft** | **36** | **36** | - |
| ↳ Bofors 40mm | 36 | 36 | 40mm |
| **Total Artillery** | **180** | **180** | - |
```

### Aircraft Summary Table

```markdown
## Air Strength

| Type | Total | Operational | Role |
|------|-------|-------------|------|
| **Fighters** | **[Total]** | **[Operational]** | - |
| ↳ [Variant 1] | [Count] | [Operational] | [Role] |
| ↳ [Variant 2] | [Count] | [Operational] | [Role] |
| **Bombers** | **[Total]** | **[Operational]** | - |
| ↳ [Variant 1] | [Count] | [Operational] | [Role] |
| **Reconnaissance** | **[Total]** | **[Operational]** | - |
| ↳ [Variant 1] | [Count] | [Operational] | [Role] |
| **Total Aircraft** | **[Grand Total]** | **[Operational]** | - |
```

### Armored Cars Table

**CRITICAL: Armored cars get their own section, NOT in Transport & Vehicles**

```markdown
## Armoured Cars

| Type | Count | Role | Unit |
|------|-------|------|------|
| **Total Armoured Cars** | **[Total]** | - | - |
| ↳ [Variant 1] | [Count] | [Role] | [Unit] |
| ↳ [Variant 2] | [Count] | [Role] | [Unit] |

### [Variant 1 Name] - [Count] vehicles

**EVERY armored car variant MUST have a detail section**

**Armament**:
- [Primary weapon]
- [Secondary weapon]

**Armor**: [Thickness] maximum
**Crew**: [Number]
**Speed**: [km/h]

**Combat Record**: [Historical usage, effectiveness, notable actions]

---

### [Variant 2 Name] - [Count] vehicles

[Repeat for EVERY armored car variant]
```

### Vehicle Summary Table

**CRITICAL RULES:**
- **DO NOT include Tanks** (they have their own section)
- **DO NOT include Armored Cars** (they have their own section)
- **ONLY include**: Trucks, Motorcycles, Support Vehicles, Halftracks
- **EVERY variant MUST have a detail section**

```markdown
## Transport & Vehicles

| Category | Count | Percentage |
|----------|-------|------------|
| **Total Vehicles** | **[Total]** | 100% |
| **Trucks** | **[Total]** | [%] |
| ↳ [Variant 1] | [Count] | [Capacity] |
| ↳ [Variant 2] | [Count] | [Capacity] |
| ↳ [Variant 3] | [Count] | [Capacity] |
| **Motorcycles** | **[Total]** | [%] |
| ↳ [Variant 1] | [Count] | [Type] |
| ↳ [Variant 2] | [Count] | [Type] |
| **Support Vehicles** | **[Total]** | [%] |
| ↳ [Variant 1] | [Count] | [Type] |
| ↳ [Variant 2] | [Count] | [Type] |
| **Halftracks** | **[Total]** | [%] |
| ↳ [Variant 1] | [Count] | [Type] |

### [Variant 1 Name] - [Count] vehicles

**EVERY vehicle variant MUST have a detail section**

**Specifications**:
- **Type**: [Truck/Motorcycle/Carrier/etc.]
- **Capacity**: [Load capacity or role]
- **Speed**: [km/h] (if applicable)
- **Engine**: [Details] (for motorcycles)

**Role**: [Transport, supply, dispatch, etc.]
**Notes**: [Any special features or usage]

---

### [Variant 2 Name] - [Count] vehicles

[Repeat for EVERY truck, motorcycle, support vehicle, halftrack variant]
```

---

## Formatting Rules

### Category Totals
- **ALWAYS use bold** for category totals (`**Medium Tanks**`, `**Field Artillery**`)
- Category totals show sum of all variants

### Variant Sub-Items
- Use `↳` symbol (Unicode U+21B3) for variant indentation
- **NO bold** for variant items (regular text)
- Variant counts must sum to category total

### Readiness Percentages
- Calculate as: `(Operational / Total) × 100`
- Round to 1 decimal place
- Show as `95.5%` format

### Table Alignment
- Left-align text columns (Category, Type)
- Right-align number columns (Total, Operational)
- Center-align percentage columns (Readiness)

---

### Infantry Weapons Table (CRITICAL - Gap 8 Fix)

**NEW REQUIREMENT for v3.0** - Extract from `top_3_infantry_weapons` in unit JSON

```markdown
## Infantry Weapons

### Top 3 Weapons by Count

| Rank | Weapon | Count | Type | Role |
|------|--------|-------|------|------|
| #1 | [Weapon Name] | [Count] | [Type] | [Role Description] |
| #2 | [Weapon Name] | [Count] | [Type] | [Role Description] |
| #3 | [Weapon Name] | [Count] | [Type] | [Role Description] |

**Analysis**: [Brief paragraph about infantry armament philosophy, strengths, weaknesses]
```

**ACTUAL EXAMPLE (British 7th Armoured, 1940 Q2):**

```markdown
## Infantry Weapons

### Top 3 Weapons by Count

| Rank | Weapon | Count | Type | Role |
|------|--------|-------|------|------|
| #1 | Lee-Enfield No.1 Mk III | 8,420 | Rifle | Primary infantry weapon |
| #2 | Bren Light Machine Gun | 412 | LMG | Squad automatic weapon |
| #3 | Boys Anti-Tank Rifle | 138 | AT Rifle | Infantry anti-tank capability |

**Analysis**: The division's infantry armament follows standard British doctrine with the reliable Lee-Enfield as the backbone. The high Bren count (1 per 20 riflemen) provides excellent squad fire support. Boys AT rifles give infantry companies organic anti-tank capability against light armor, though effectiveness against newer German tanks is limited.
```

---

## Additional Sections

### 9. Supply & Logistics (NEW - v3.0)

**CRITICAL REQUIREMENT** - Extract from `supply_logistics` object in unit JSON

```markdown
## Supply & Logistics

### Logistics Status ([Quarter])

| Resource | Quantity | Status | Notes |
|----------|----------|--------|-------|
| **Operational Radius** | [Distance] km | - | From [Main depot] |
| **Fuel Reserves** | [Days] days | [Status] | At current consumption rate |
| **Ammunition** | [Days] days | [Status] | Combat load basis |
| **Water Supply** | [Liters] L/day/person | [Status] | Desert operations requirement |

**Supply Status**: [Qualitative assessment from supply_status field]

**Operational Context**: [Description of supply constraints, logistics challenges, impact on operations]
```

**ACTUAL EXAMPLE (German Deutsches Afrikakorps, 1941 Q2):**

```markdown
## Supply & Logistics

### Logistics Status (1941 Q2)

| Resource | Quantity | Status | Notes |
|----------|----------|--------|-------|
| **Operational Radius** | 350 km | Constrained | From Tripoli (1800km) |
| **Fuel Reserves** | 6.5 days | Strained | Vulnerable to interdiction |
| **Ammunition** | 8 days | Adequate | Sufficient for defensive ops |
| **Water Supply** | 4.5 L/day/person | Adequate | Desert operations minimum |

**Supply Status**: Adequate for defensive operations, strained for sustained offensive operations. Primary constraint: fuel delivery from Tripoli over 1800km of vulnerable coastal road.

**Operational Context**: The DAK's operational tempo is directly constrained by fuel availability. Rommel's aggressive tactics frequently operate beyond prudent supply margins. British interdiction of coastal convoys creates periodic crises requiring operational pauses.
```

### 10. Operational Environment (NEW - v3.0)

**CRITICAL REQUIREMENT** - Extract from `weather_environment` object in unit JSON

```markdown
## Operational Environment

### Environmental Conditions ([Quarter])

| Factor | Value | Impact |
|--------|-------|--------|
| **Season** | [Quarter description] | - |
| **Temperature Range** | [Min]°C to [Max]°C | [Heat/cold impact] |
| **Terrain Type** | [Description] | [Mobility/visibility effects] |
| **Storm Frequency** | [Days] days/month | [Operational disruption] |
| **Daylight Hours** | [Hours] hours | [Operational tempo] |

**Environmental Impact**: [Description of how conditions affect operations, equipment performance, personnel endurance]

**Tactical Considerations**: [How weather/terrain influences tactics, timing of operations, equipment choices]
```

**ACTUAL EXAMPLE (North Africa, 1941 Q2 - April-June):**

```markdown
## Operational Environment

### Environmental Conditions (1941 Q2 - April-June)

| Factor | Value | Impact |
|--------|-------|--------|
| **Season** | Spring transitioning to summer | Rising heat stress |
| **Temperature Range** | 18°C to 35°C | High daytime heat, moderate nights |
| **Terrain Type** | Coastal plain and rocky desert | Good tank mobility, limited cover |
| **Storm Frequency** | 2 days/month | Occasional sandstorms (Ghibli winds) |
| **Daylight Hours** | 13.5 hours | Extended operational window |

**Environmental Impact**: Rising temperatures increase water requirements and strain cooling systems on vehicles and aircraft. The terrain favors mobile armored warfare with excellent visibility for reconnaissance. Sandstorms occasionally ground aircraft and reduce visibility to near-zero, halting operations.

**Tactical Considerations**: Long daylight hours enable extended combat operations but also increase exposure to air attack. Lack of natural cover places premium on prepared defensive positions. Heat necessitates dawn/dusk operations to preserve crew effectiveness.
```

### 11. Organizational Structure

List subordinate units with:
- Unit designation
- Commander
- Strength (personnel)
- Composition (regiments/battalions)
- Equipment summary

### 12. Tactical Doctrine & Capabilities

- Role description
- Special capabilities
- Tactical innovations
- Known issues/limitations
- Desert/terrain adaptations (if applicable)

### 13. Critical Equipment Shortages

**REQUIRED SECTION** - Document operational limitations from equipment deficiencies

```markdown
## Critical Equipment Shortages

This section identifies critical equipment shortages that significantly impact unit operational capability during this quarter.

### Priority 1: Critical Shortages (Mission-Limiting)
- **[Equipment Category]**: [Description of shortage]
  - **Required**: [Number/amount needed]
  - **Available**: [Number/amount on hand]
  - **Impact**: [Specific operational limitation]
  - **Mitigation**: [How unit compensates]

### Priority 2: Important Shortages (Capability-Reducing)
- **[Equipment Category]**: [Description]

### Priority 3: Minor Shortages (Performance-Degrading)
- **[Equipment Category]**: [Description]

**Overall Assessment**: [Summary of how shortages affect unit combat effectiveness]
```

**Example (British 7th Armoured, 1940 Q2):**
```markdown
## Critical Equipment Shortages

### Priority 1: Critical Shortages
- **Anti-Tank Artillery**: Severe shortage of modern AT guns
  - **Required**: 72 x 2-pounder AT guns per division standard
  - **Available**: 48 (66.7% of requirement)
  - **Impact**: Reduced ability to counter German Panzer III/IV
  - **Mitigation**: Increased reliance on cruiser tanks for AT role

### Priority 2: Important Shortages
- **Infantry Tanks**: Only 6 Matilda II available vs. 50 planned
- **Transport Vehicles**: 15% below establishment strength
```

### 14. Historical Context

- Formation history
- Operational status for the quarter
- Key events during the quarter
- Combat activity
- Equipment status

### 15. Wargaming Data

- Scenario suitability
- Morale rating (1-10)
- Experience level
- Special rules for wargames
- Historical engagements

### 16. Data Quality & Known Gaps

**REQUIRED SECTION** - Transparency about data completeness

**NEW v3.1.0**: Section must include TIER and STATUS information from validation object

```markdown
## Data Quality & Known Gaps

---

### ⭐ EXTRACTION QUALITY

**Tier**: [1-4] ([Tier Name])
**Status**: [production_ready|review_recommended|partial_needs_research|research_brief_created]
**Confidence Score**: [X]% ([Confidence description])

**Tier Definitions**:
- **Tier 1 (75-100%)**: Production Ready - All required fields present
- **Tier 2 (60-74%)**: Review Recommended - Minor documented gaps acceptable
- **Tier 3 (50-59%)**: Partial Needs Research - Substantial data, critical gaps remain
- **Tier 4 (<50%)**: Research Brief Created - Insufficient data for extraction

---

### Data Sources

This unit's TO&E was compiled from:
- **Primary Sources**: [List Tier 1 sources: Tessin, Army Lists, Field Manuals]
- **Secondary Sources**: [List Tier 2/3 sources: Curated web, historical databases]
- **Cross-Referenced**: [Number] sources consulted, [Number] facts verified

### Known Data Gaps

**FOR TIER 2-3 ONLY**: Document each gap from `gap_documentation` object

#### Required Field Gaps

**[Field Name]** (e.g., "Commander Name"):
- **Status**: [unknown|estimated|partial]
- **Reason**: [Why data unavailable]
- **Sources Checked**: [List sources consulted]
- **Confidence Impact**: [-X%]
- **How to Resolve**: [Mitigation strategy]

**[Additional gaps as needed]**

#### Optional Field Gaps

**Important Gaps** (affect core TO&E understanding):
- [Gap 1: e.g., "7th Armoured Brigade commander name not confirmed"]
- [Gap 2: e.g., "Exact distribution of A9 vs A10 cruisers in 6th RTR"]

**Moderate Gaps** (refinements needed):
- [Gap 3: e.g., "Precise strength numbers for some regiments"]

**Low Priority** (supplementary data):
- WITW game IDs not available for most vehicles
- [Other minor gaps]

### Research Notes

- [Note 1: e.g., "Commander O'Moore Creagh confirmed from multiple sources"]
- [Note 2: e.g., "Tank totals verified from British Armoured Formations 1940"]
- [Methodology notes or assumptions made]

### Gap Resolution Priority

- 🔴 **High Priority**: [Gaps affecting historical accuracy]
- 🟡 **Medium Priority**: [Gaps affecting completeness]
- 🟢 **Low Priority**: [Nice-to-have details]

### Future Improvements

When additional sources become available, the following areas would benefit from refinement:
1. [Area 1]
2. [Area 2]
```

**TIER 2 EXAMPLE (Italian XXI Corps 1941-Q2 - 65% confidence)**:

```markdown
## Data Quality & Known Gaps

---

### ⭐ EXTRACTION QUALITY

**Tier**: 2 (Review Recommended)
**Status**: review_recommended
**Confidence Score**: 65% (Acceptable with documented gaps)

**Tier Explanation**: This unit was extracted with Tier 2 quality. The extraction is substantially complete with 1 documented gap in a required field (commander name for interim period). This is acceptable for review and use, with the understanding that one data point is documented as unknown.

---

### Data Sources

This unit's TO&E was compiled from:
- **Primary Sources**: TM E 30-420 (Italian Military Forces handbook, para 50)
- **Secondary Sources**: Lewin (1998) Rommel as Military Commander
- **Cross-Referenced**: 3 sources consulted, subordinate units and organizational structure verified

### Known Data Gaps

#### Required Field Gaps

**Commander Name** (Jan-Jul 1941 interim period):
- **Status**: unknown
- **Reason**: Interim command period between Gen. Carlo Spatocco (departed Dec 20, 1940) and Gen. Enea Navarini (appointed Aug 1, 1941). No sources document acting commander for Jan-Jul 1941.
- **Sources Checked**:
  - ❌ Lewin (1998) Rommel as Military Commander - mentions Gen. Spatocco for earlier period
  - ❌ Nafziger Collection - no OOB file for Q2 1941 informal corps period
  - ❌ TM E 30-420 para 50 - shows organizational structure only, no personnel
- **Confidence Impact**: -10%
- **How to Resolve**: Check Italian War Ministry records (Ufficio Storico) or Gen. Navarini's service file for appointment documentation. Alternately, accept "Acting Commander Unknown (interim period)" if 65% confidence acceptable for use case.

#### Optional Field Gaps

**Low Priority**:
- WITW game IDs not available (awaiting one-time batch mapping)
- Chief of Staff name unknown for informal corps period
```

**FORMATTING RULES**:
- **TIER 1**: Standard gap documentation (optional gaps only)
- **TIER 2**: **MANDATORY** Required Field Gaps section with detailed gap_documentation
- **TIER 3**: Similar to Tier 2 but more gaps, emphasize "Partial Needs Research" status
- **TIER 4**: Would not generate chapter (research brief only)
- Always show tier and status prominently at top
- Categorize gaps by severity (Important/Moderate/Low)
- Be specific about what's missing (not vague "some commanders unknown")
- Note what HAS been verified, not just what's missing
- Include research methodology notes
- Suggest future improvement areas

---

### 17. Conclusion

2-3 paragraph wrap-up covering:
- Unit assessment for the quarter
- Strengths and weaknesses
- Future outlook (if known)
- Historical significance

**Data Source Footer (part of Conclusion):**

```markdown
---

**Data Source**: Autonomous TO&E Extraction System
**Confidence**: [%] ([Source tier description])
**Schema**: unified_toe_schema.json v3.0.0 (Ground Forces)
**Extraction Date**: [YYYY-MM-DD]

---

*For detailed equipment specifications and subordinate unit TO&E files, see:*
- `[subordinate_unit_1_toe.json]`
- `[subordinate_unit_2_toe.json]`
```

---

## Multi-Nation Examples

### German Panzer Division

```markdown
| Category | Total | Operational | Readiness |
|----------|-------|-------------|-----------|
| **All Tanks** | **320** | **305** | **95.3%** |
| **Medium Tanks** | **180** | **170** | **94.4%** |
| ↳ Panzer III Ausf H | 67 | 64 | 95.5% |
| ↳ Panzer III Ausf G | 50 | 47 | 94.0% |
| ↳ Panzer IV Ausf F | 44 | 42 | 95.5% |
| ↳ Panzer IV Ausf E | 19 | 17 | 89.5% |
| **Light Tanks** | **140** | **135** | **96.4%** |
| ↳ Panzer II Ausf C | 85 | 82 | 96.5% |
| ↳ Panzer I Ausf B | 55 | 53 | 96.4% |
```

### Italian Division

```markdown
| Category | Total | Operational | Readiness |
|----------|-------|-------------|-----------|
| **All Tanks** | **111** | **102** | **91.9%** |
| **Medium Tanks** | **99** | **92** | **92.9%** |
| ↳ M13/40 | 60 | 56 | 93.3% |
| ↳ M11/39 | 39 | 36 | 92.3% |
| **Light Tanks** | **12** | **10** | **83.3%** |
| ↳ L3/35 | 12 | 10 | 83.3% |
```

### American Division

```markdown
| Category | Total | Operational | Readiness |
|----------|-------|-------------|-----------|
| **All Tanks** | **390** | **375** | **96.2%** |
| **Medium Tanks** | **232** | **225** | **97.0%** |
| ↳ M4 Sherman | 108 | 105 | 97.2% |
| ↳ M3 Lee | 124 | 120 | 96.8% |
| **Light Tanks** | **158** | **150** | **94.9%** |
| ↳ M5 Stuart | 92 | 88 | 95.7% |
| ↳ M3 Stuart | 66 | 62 | 93.9% |
```

---

## Quality Checklist

Before publishing any chapter, verify:

- [ ] All equipment tables use variant breakdown format
- [ ] Category totals are **bold**
- [ ] Variant items use `↳` symbol
- [ ] Operational counts provided for all variants
- [ ] Readiness percentages calculated correctly
- [ ] Variant counts sum to category totals
- [ ] WITW IDs included where available
- [ ] All 18 required sections present:
  - [ ] 1. Header
  - [ ] 2. Division/Unit Overview
  - [ ] 3. Command
  - [ ] 4. Personnel Strength
  - [ ] 5-9. Equipment sections (Armoured, Artillery, Armoured Cars, Infantry Weapons, Transport)
  - [ ] 10. Supply & Logistics (NEW v3.0 - extract from supply_logistics object)
  - [ ] 11. Operational Environment (NEW v3.0 - extract from weather_environment object)
  - [ ] 12. Organizational Structure
  - [ ] 13. Tactical Doctrine & Capabilities
  - [ ] 14. Critical Equipment Shortages
  - [ ] 15. Historical Context
  - [ ] 16. Wargaming Data
  - [ ] 17. Data Quality & Known Gaps
  - [ ] 18. Conclusion with Data Source Footer
- [ ] Cross-references to subordinate units included
- [ ] Source citations in footer
- [ ] Confidence score documented

---

## Implementation Notes

### For Autonomous Agents

When generating chapters:
1. Read unit TO&E JSON file
2. Extract all equipment variants from `equipment_variants` table
3. Group variants by category (medium_tank, light_tank, field_artillery, etc.)
4. Calculate category totals (sum of all variants)
5. Calculate readiness percentages per variant
6. Format table with **bold** categories and `↳` variants
7. Follow this template structure exactly

### For Manual Updates

When manually editing chapters:
1. Always maintain variant breakdown format
2. Update operational counts if data changes
3. Recalculate readiness percentages
4. Keep variant counts summing to category totals
5. Maintain bold/non-bold formatting

---

**Template Version:** 3.1
**Author:** Claude Code Autonomous Orchestrator
**Date:** 2025-10-15
**Status:** PRODUCTION STANDARD - All chapters must comply

**v3.1 Changes:**
- Enhanced Section 16: Data Quality & Known Gaps with TIER system
- Added mandatory EXTRACTION QUALITY subsection showing Tier, Status, Confidence
- Added Required Field Gaps documentation for Tier 2-3 extractions
- Included Tier 2 example (Italian XXI Corps) showing gap documentation
- Updated to support schema v3.1.0 tiered extraction system

**v3.0 Changes:**
- Added Section 8: Infantry Weapons (Gap 8 fix)
- Added Section 10: Supply & Logistics (supply_logistics object extraction)
- Added Section 11: Operational Environment (weather_environment object extraction)
- Renumbered sections 9-16 → 12-18
- Updated quality checklist for 18 sections
- Schema updated to v3.0.0 (Ground Forces)
