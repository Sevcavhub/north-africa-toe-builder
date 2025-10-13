# Data Quality Standards

## Overview

This project maintains **rigorous quality standards** to ensure historical accuracy and research credibility. All units must meet minimum thresholds before publication.

---

## Minimum Requirements

### Publication Thresholds

**Mandatory Requirements**:
- ✅ **Confidence Score**: ≥ 75%
- ✅ **Schema Compliance**: 100% (must pass validation)
- ✅ **Template Compliance**: All 16 required sections
- ✅ **Source Citations**: Minimum 2 sources for critical facts
- ✅ **Gap Documentation**: All gaps explicitly documented

**Units failing any requirement** are flagged for additional research before publication.

---

## Confidence Scoring

### Scoring Rubric

**90-100%: Excellent**
- Data from Tier 1 primary sources (Tessin, Army Lists, Field Manuals)
- Multiple sources corroborate all critical facts
- Equipment variants verified
- Commander details verified (name, rank, appointment date)
- Minimal gaps (< 5% of data points)

**80-89%: Good**
- Mix of Tier 1 and Tier 2 sources
- Core facts verified from primary sources
- Most equipment variants identified
- Some minor gaps (5-10% of data points)
- Estimation clearly flagged

**75-79%: Acceptable**
- Primarily Tier 2 sources with some Tier 1
- Critical facts verified
- Equipment categories known, some variant gaps
- Moderate gaps (10-15% of data points)
- Estimation used for non-critical data

**70-74%: Below Threshold**
- Heavy reliance on Tier 2/3 sources
- Some critical facts unverified
- Equipment approximated
- Significant gaps (15-20%)
- **Requires additional research**

**Below 70%: Insufficient**
- Too many gaps and uncertainties
- Critical facts missing
- **Not published**

### Confidence Factors

**Positive Factors** (increase confidence):
- Tier 1 primary sources
- Multiple corroborating sources
- Contemporary documents (war diaries)
- Precise equipment variant identification
- Commander details verified
- Unit participation in battles confirmed

**Negative Factors** (decrease confidence):
- Single source for critical facts
- Conflicting source information
- Estimated data points
- Generic equipment categories (no variants)
- Missing commanders or dates
- Gaps in organizational structure

---

## Schema Validation

### Critical Validation Rules

**Equipment Validation**:
1. `tanks.total = tanks.heavy + tanks.medium + tanks.light` (exact match required)
2. `artillery_total ≥ field + anti_tank + anti_aircraft` (minimum)
3. `ground_vehicles_total ≥ tanks + trucks + motorcycles` (minimum)
4. Category totals = sum of all variants (exact)

**Personnel Validation**:
1. `total_personnel ≈ officers + ncos + enlisted` (±5% tolerance)
2. Percentage calculations sum to 100% (±0.5% rounding)
3. Personnel realistic for unit type:
   - Division: 10,000-20,000
   - Brigade: 3,000-6,000
   - Regiment: 1,000-3,000

**Organizational Validation**:
1. Parent unit exists (division has corps, regiment has division)
2. Commander appointed date ≤ quarter end date
3. Subordinate units listed with commanders
4. Headquarters location documented

**Historical Validation**:
1. No anachronisms (equipment existed in quarter)
2. Commander verified from 2+ sources
3. Unit designation historically accurate
4. Battle participation cross-checked

### Validation Process

**Automated Checks**:
- JSON schema validation (structure)
- Mathematical validation (totals)
- Field presence validation (required fields)

**Manual Checks**:
- Historical accuracy (anachronisms)
- Source quality assessment
- Cross-reference verification
- Gap documentation review

---

## Template Compliance

### 16 Required Sections

All MDBook chapters must include:

1. ✅ **Header** (unit, nation, quarter, location)
2. ✅ **Division/Unit Overview** (2-3 paragraphs)
3. ✅ **Command** (commander, HQ, staff)
4. ✅ **Personnel Strength** (table with percentages)
5. ✅ **Armoured Strength** (variant breakdown tables)
6. ✅ **Artillery Strength** (variant breakdown + detail sections)
7. ✅ **Armoured Cars** (separate section, NOT in transport)
8. ✅ **Transport & Vehicles** (NO tanks/armored cars)
9. ✅ **Organizational Structure** (subordinate units)
10. ✅ **Supply Status** (fuel, ammo, food, water)
11. ✅ **Tactical Doctrine** (role, capabilities)
12. ✅ **Critical Equipment Shortages** (Priority 1/2/3)
13. ✅ **Historical Context** (quarter-specific events)
14. ✅ **Wargaming Data** (morale, experience, scenarios)
15. ✅ **Data Quality & Known Gaps** (confidence, sources, gaps)
16. ✅ **Conclusion** (assessment + data source footer)

### Variant Detail Requirements

**CRITICAL**: Every variant in summary tables must have a detail section

**Example** (Artillery):
```markdown
## Artillery Strength

| Type | Total | Operational |
|------|-------|-------------|
| **Field Artillery** | **96** | **96** |
| ↳ Ordnance QF 25-pounder | 72 | 72 |
| ↳ QF 4.5-inch Howitzer | 24 | 24 |

### Ordnance QF 25-pounder - 72 guns

**REQUIRED**: Detail section for every variant

**Specifications**: ...
**Combat Performance**: ...
```

**Compliance Check**:
- Count variants in table
- Count detail sections
- Numbers must match

---

## Source Citation Standards

### Minimum Citation Requirements

**Critical Facts** (require 2+ sources):
- Unit commander name
- Unit designation and nickname
- Parent unit
- Major equipment types
- Participation in major battles

**Important Facts** (require 1+ source):
- Personnel strength
- Equipment variant breakdown
- Subordinate unit commanders
- Headquarters location
- Supply status

**Supplementary Facts** (can be estimated):
- Exact operational percentages
- Minor equipment counts
- Individual weapon counts
- Vehicle distribution

### Citation Format

**In JSON**:
```json
{
  "commander": {
    "name": "Major-General Sir Michael O'Moore Creagh",
    "rank": "Major-General",
    "source": "British Army List Q2 1941, page 45"
  }
}
```

**In MDBook Chapter**:
```markdown
**Data Sources**:
- British Army List Q2 1941 (commander, organization)
- British Armoured Formations 1940 (equipment)
- desertrats.org.uk (historical context)
```

---

## Gap Documentation

### Required Gap Documentation

**In MDBook Chapter - Section 15: Data Quality & Known Gaps**

Must include:
- **Confidence Score**: Percentage with tier description
- **Data Sources**: List of sources used
- **Known Gaps**: Categorized by severity
  - **Important**: Core TO&E gaps
  - **Moderate**: Refinement needed
  - **Low Priority**: Supplementary details
- **Research Notes**: Methodology and assumptions
- **Gap Resolution Priority**: Color-coded priorities
- **Future Improvements**: Areas for refinement

**Example**:
```markdown
## Data Quality & Known Gaps

**Confidence Score**: 85% (High confidence - Tier 1 primary sources)

### Known Data Gaps

**Important Gaps**:
- 7th Armoured Brigade commander name not confirmed

**Moderate Gaps**:
- Exact A9 vs A10 cruiser distribution in 6th RTR

**Low Priority**:
- WITW game IDs not available for most vehicles
```

### Gap Categories

**Important Gaps** (Priority 1):
- Missing commanders
- Unknown unit designations
- Major equipment categories missing
- Organizational structure unclear

**Moderate Gaps** (Priority 2):
- Equipment variant distribution uncertain
- Personnel strength estimated
- Minor subordinate unit details missing

**Low Priority Gaps** (Priority 3):
- Wargaming IDs unavailable
- Exact operational percentages
- Individual weapon counts
- Minor equipment details

---

## Cross-Referencing Standards

### Multi-Source Verification

**Process**:
1. **Locate fact in Source A**
2. **Verify in Source B** (different source, ideally different tier)
3. **If conflict**: Document both values, explain resolution
4. **If agreement**: Note corroboration in metadata

**Example**:
- **Fact**: 7th Armoured Division commander
- **Source A**: British Army List Q2 1941 → "Major-General O'Moore Creagh"
- **Source B**: desertrats.org.uk → "Major-General Sir Michael O'Moore Creagh"
- **Resolution**: Use full name from Source B, note both sources corroborate

### Conflict Resolution

**When sources conflict**:
1. **Tier 1 overrides lower tiers**
2. **More specific source** preferred (divisional history > general OOB)
3. **More recent scholarship** (if equal authority)
4. **Document conflict** in "Known Gaps"

---

## Estimation Standards

### When Estimation is Acceptable

**Acceptable**:
- Personnel strength (using establishment tables)
- Operational percentages (using similar units)
- Minor equipment counts (extrapolated from major categories)
- Subordinate unit strength (proportional allocation)

**NOT Acceptable**:
- Commander names (mark as "Unknown")
- Unit designations (must verify)
- Major equipment types (must verify)
- Battle participation (must verify)

### Estimation Documentation

**Required**:
- `"estimated": true` flag in JSON
- Explanation of estimation method
- Confidence impact noted
- Documentation in "Known Gaps" section

**Example**:
```json
{
  "personnel": {
    "total": 16000,
    "estimated": true,
    "estimation_method": "British infantry division establishment table",
    "confidence_impact": "Reduced confidence by 5%"
  }
}
```

---

## Quality Assurance Process

### Multi-Stage Review

**Stage 1: Automated Validation**
- Schema compliance check
- Mathematical validation
- Required field verification
- Output: Pass/Fail + error report

**Stage 2: Template Compliance**
- 16 required sections present
- Variant detail sections match summary tables
- Formatting standards met
- Output: Compliance score %

**Stage 3: Historical Accuracy**
- Anachronism check (equipment existed in quarter?)
- Commander verification (2+ sources?)
- Battle participation cross-check
- Output: Historical accuracy score

**Stage 4: Manual Review**
- Overall coherence and completeness
- Gap documentation adequate?
- Source quality appropriate?
- Output: Final confidence score

### QA Metrics

**Unit-Level**:
- Confidence score (target: 80%+)
- Schema compliance (target: 100%)
- Template compliance (target: 100%)
- Source count (target: 5+ sources)
- Cross-reference % (target: 80%+ critical facts)

**Project-Level**:
- Units completed / total planned
- Average confidence score
- Schema compliance rate
- Template compliance rate

---

## Continuous Improvement

### Iterative Refinement

1. **Publish at 75%+ confidence**
2. **Document all gaps** in "Known Gaps" section
3. **Prioritize gap filling** (Priority 1 first)
4. **Research additional sources**
5. **Update units** when new data found
6. **Track confidence improvement** over time

### Version Control

**Track changes**:
- Initial extraction date
- Last updated date
- Schema version
- Template version
- Change log (major updates)

**Example**:
```json
{
  "metadata": {
    "extraction_date": "2025-10-10",
    "last_updated": "2025-10-12",
    "schema_version": "1.0.0",
    "template_version": "2.0",
    "confidence_history": [
      {"date": "2025-10-10", "score": 78},
      {"date": "2025-10-12", "score": 85}
    ]
  }
}
```

---

## Quality Checklist

### Before Publishing Unit

- [ ] Confidence score ≥ 75%
- [ ] Schema validation passes (100%)
- [ ] All 16 required sections present
- [ ] Variant detail sections match summary tables
- [ ] Critical facts cited (2+ sources)
- [ ] Commander verified
- [ ] No anachronisms
- [ ] All gaps documented in Section 15
- [ ] Estimation flagged where used
- [ ] Cross-references verified
- [ ] Data source footer included

---

## Further Reading

- [Research Methodology](./research-methodology.md) - Overall process
- [Source Hierarchy](./source-hierarchy.md) - Source quality tiers
- [Validation Process](./validation.md) - Detailed validation rules

---

**Last Updated**: 2025-10-12
**Minimum Standards**: 75% confidence, 100% schema compliance, 16 sections required
**Target Standards**: 80%+ confidence, 5+ sources, 80%+ cross-reference rate
