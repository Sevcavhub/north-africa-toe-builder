# MDBook Chapter Template - TO&E Unit Documentation

**Version:** 2.0
**Updated:** 2025-10-10
**Purpose:** Standard format for all MDBook chapters generated from TO&E JSON files

---

## Overview

This template defines the standard structure for military unit chapters in the North Africa TO&E MDBook. All chapters must follow this format to ensure consistency and readability.

---

## Required Sections

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
- Commander information

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

## 5. Equipment Tables with Variant Breakdowns

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

## Additional Sections

### 6. Organizational Structure

List subordinate units with:
- Unit designation
- Commander
- Strength (personnel)
- Composition (regiments/battalions)
- Equipment summary

### 7. Supply Status

```markdown
## Supply Status ([Quarter])

| Resource | Days of Supply | Status |
|----------|---------------|--------|
| **Fuel** | [Days] | [Assessment] |
| **Ammunition** | [Days] | [Assessment] |
| **Food** | [Days] | [Assessment] |
| **Water** | [Liters/day/man] | [Assessment] |

**Operational Radius**: [Distance] from [Base]
**Supply Base**: [Location]
**Assessment**: [Overall status description]
```

### 8. Tactical Doctrine & Capabilities

- Role description
- Special capabilities
- Tactical innovations
- Known issues/limitations
- Desert/terrain adaptations (if applicable)

### 9. Historical Context

- Formation history
- Operational status for the quarter
- Key events during the quarter
- Combat activity
- Equipment status

### 10. Wargaming Data

- Scenario suitability
- Morale rating (1-10)
- Experience level
- Special rules for wargames
- Historical engagements

### 11. Data Quality & Known Gaps

**REQUIRED SECTION** - Transparency about data completeness

```markdown
## Data Quality & Known Gaps

**Confidence Score**: [X]% ([High/Medium/Acceptable] confidence - [Source tier description])

### Data Sources

This unit's TO&E was compiled from:
- **Primary Sources**: [List Tier 1 sources: Tessin, Army Lists, Field Manuals]
- **Secondary Sources**: [List Tier 2/3 sources: Curated web, historical databases]
- **Cross-Referenced**: [Number] sources consulted, [Number] facts verified

### Known Data Gaps

The following information could not be confirmed from available sources:

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

**FORMATTING RULES**:
- Always show confidence score prominently
- Categorize gaps by severity (Important/Moderate/Low)
- Be specific about what's missing (not vague "some commanders unknown")
- Note what HAS been verified, not just what's missing
- Include research methodology notes
- Suggest future improvement areas

---

### 12. Conclusion

2-3 paragraph wrap-up covering:
- Unit assessment for the quarter
- Strengths and weaknesses
- Future outlook (if known)
- Historical significance

### 13. Data Source Footer

```markdown
---

**Data Source**: Autonomous TO&E Extraction System
**Confidence**: [%] ([Source tier description])
**Schema**: unified_toe_schema.json v1.0.0
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
- [ ] All required sections present
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

**Template Version:** 2.0
**Author:** Claude Code Autonomous Orchestrator
**Date:** 2025-10-10
**Status:** PRODUCTION STANDARD - All chapters must comply
