# Research Methodology

## Overview

This project uses a **systematic, multi-agent approach** to extract and validate Table of Organization & Equipment (TO&E) data from primary historical sources. All data follows rigorous quality standards to ensure historical accuracy and research credibility.

---

## 7-Phase Extraction Workflow

### Phase 1: Source Extraction

**Objective**: Locate and extract raw data from primary source documents

**Process**:
1. Identify unit and quarter from project configuration
2. Search for sources using 3-tier waterfall (see [Source Hierarchy](./source-hierarchy.md))
3. Extract commander, personnel, and equipment data
4. Document source citations and page numbers
5. Flag gaps and uncertainties

**Agents**: `document_parser`, `historical_research`

**Output**: Raw extraction JSON with source citations

---

### Phase 2: Organization Building

**Objective**: Construct hierarchical organizational structure

**Process**:
1. Identify parent unit (corps, army, theater)
2. List subordinate units (brigades, regiments, battalions)
3. Map command relationships
4. Verify organizational changes during quarter
5. Document headquarters locations

**Agents**: `org_hierarchy`, `unit_instantiation`

**Output**: Complete organizational hierarchy

---

### Phase 3: Equipment Distribution

**Objective**: Distribute equipment from division level down to subordinate units

**Process**:
1. Calculate division-level totals
2. Allocate equipment to brigades/regiments
3. Track equipment to specific variants
4. Calculate operational vs. total equipment
5. Validate totals sum correctly

**Agents**: `theater_allocator`, `division_cascader`, `equipment_reconciliation`

**Output**: Equipment distribution at all organizational levels

---

### Phase 4: Aggregation

**Objective**: Roll up equipment and personnel totals from bottom to top

**Process**:
1. Sum equipment from subordinate units
2. Calculate personnel totals
3. Compute "Top 3" infantry weapons
4. Validate parent = sum of children (±5%)
5. Flag discrepancies for review

**Agents**: `bottom_up_aggregator`, `top3_calculator`

**Output**: Validated aggregated totals

---

### Phase 5: Validation

**Objective**: Verify schema compliance and historical accuracy

**Process**:
1. Validate against `unified_toe_schema.json`
2. Check equipment totals (tanks.total = heavy + medium + light)
3. Verify personnel totals (total ≈ officers + ncos + enlisted ±5%)
4. Cross-check commanders against historical records
5. Flag anachronisms (equipment not available in quarter)
6. Calculate confidence score

**Agents**: `schema_validator`, `historical_accuracy`

**Output**: Validation report with pass/fail status

---

### Phase 6: Output Generation

**Objective**: Generate multiple output formats from validated data

**Process**:
1. **MDBook Chapters**: Generate markdown chapters following template v2.0
2. **WITW Scenarios**: Export CSV files for wargaming (when WITW IDs available)
3. **SQL Database**: Generate INSERT statements for relational database
4. **JSON Files**: Save final unit TO&E JSON

**Agents**: `book_chapter_generator`, `scenario_exporter`, `sql_populator`

**Output**: Multi-format deliverables

---

### Phase 7: Quality Assurance

**Objective**: Final review and gap analysis

**Process**:
1. Review all outputs for consistency
2. Cross-check JSON vs. MDBook chapter
3. Verify template compliance (16 required sections)
4. Document known gaps and uncertainties
5. Create QA audit report

**Agents**: `qa_auditor` (orchestrator-workers pattern)

**Output**: QA report with quality metrics

---

## Multi-Agent Architecture

### Agent Types

**Source & Extraction**:
- `document_parser`: Extract data from PDF/text sources
- `historical_research`: Web research for supplementary data

**Structure & Organization**:
- `org_hierarchy`: Build organizational structure
- `toe_template`: Create standardized TO&E structure
- `unit_instantiation`: Instantiate unit from template

**Equipment Distribution**:
- `theater_allocator`: Allocate equipment at theater level
- `division_cascader`: Cascade equipment to subordinate units
- `equipment_reconciliation`: Reconcile discrepancies

**Aggregation & Calculation**:
- `bottom_up_aggregator`: Roll up totals from subordinates
- `top3_calculator`: Calculate top 3 infantry weapons

**Validation**:
- `schema_validator`: Validate JSON schema compliance
- `historical_accuracy`: Verify historical plausibility

**Output Generation**:
- `book_chapter_generator`: Generate MDBook chapters
- `scenario_exporter`: Export wargaming scenarios
- `sql_populator`: Generate SQL database scripts

---

## Data Quality Principles

### 1. No Guessing Policy

**Rule**: If data is not found in sources, mark as "Unknown" or "Estimated"

**Examples**:
- Commander name not found → `"commander": "Unknown (not documented in sources)"`
- Equipment count uncertain → `"estimated": true` flag
- Personnel strength missing → Document in "Known Gaps" section

**Rationale**: Better to acknowledge gaps than hallucinate false data

---

### 2. Due Diligence in Calculations

**Rule**: Calculate all totals from component parts when possible

**Examples**:
- Tank totals = sum(heavy + medium + light) - calculate, don't guess
- Personnel totals = sum(officers + NCOs + enlisted) - verify ±5%
- Equipment operational % = (operational / total) × 100 - calculate precisely

**Rationale**: Calculated totals are more reliable than estimated totals

---

### 3. Source Citation Requirements

**Rule**: Every major fact must cite a source

**Examples**:
- Commander name → British Army List Q2 1941, page 45
- Equipment count → Tessin Vol 3, page 127
- Unit location → War diary entry, 15 June 1941

**Rationale**: Enables verification and builds research credibility

---

### 4. Cross-Referencing

**Rule**: Critical facts require minimum 2 sources

**Critical Facts**:
- Unit commander names
- Unit designations and nicknames
- Major equipment types
- Participation in major battles

**Process**:
1. Find fact in Source A
2. Verify in Source B
3. If conflict, document both versions and reasoning for selection

**Rationale**: Reduces errors from single-source mistakes

---

### 5. Quarterly Precision

**Rule**: Data must be specific to the quarter being documented

**Examples**:
- 7th Armoured had 228 tanks in 1940-Q2, but 280 in 1941-Q2 - use correct quarter
- Commander O'Moore Creagh appointed December 1939, relieved June 1941 - verify dates
- Equipment variants change (Panzer III Ausf G in Q1, Ausf H in Q2) - track precisely

**Rationale**: Military units change composition rapidly in wartime

---

## Confidence Scoring

### Scoring Criteria

**90-100%**: High Confidence
- Data from Tier 1 primary sources (Tessin, Army Lists, Field Manuals)
- Multiple sources corroborate
- Minimal gaps or uncertainties

**75-89%**: Medium Confidence
- Data from mix of Tier 1 and Tier 2 sources
- Most facts verified, some gaps
- Estimated data clearly flagged

**60-74%**: Acceptable Confidence
- Data primarily from Tier 2/3 sources
- Some critical facts verified
- Multiple gaps documented

**Below 60%**: Insufficient Confidence
- Too many gaps or uncertainties
- Requires additional research before publishing

### Minimum Threshold

**75% confidence** required for all published units

Units below 75% are flagged for additional research before inclusion in final output.

---

## Validation Rules

### Equipment Validation

1. `tanks.total = tanks.heavy + tanks.medium + tanks.light` (exact)
2. `artillery_total ≥ sum(field + anti_tank + anti_aircraft)` (minimum)
3. `ground_vehicles_total ≥ sum(tanks + trucks + motorcycles + support)` (minimum)
4. Category totals = sum of all variants (exact)

### Personnel Validation

1. `total_personnel ≈ officers + ncos + enlisted` (±5% tolerance)
2. Percentage calculations sum to 100% (±0.5% rounding)
3. Personnel counts realistic for unit type (division: 10,000-20,000)

### Organizational Validation

1. Parent unit total = sum of all child units (±5%)
2. Commander appointed date ≤ quarter end date
3. Subordinate units exist in historical records
4. Headquarters location documented

### Historical Validation

1. No anachronisms (equipment available in quarter)
2. Commander appointments verified from multiple sources
3. Unit participation in battles cross-checked
4. Equipment production dates verified

---

## Handling Conflicts

### Source Conflicts

When sources disagree:

1. **Prioritize primary sources** over secondary
2. **More specific source** wins (e.g., divisional history over general OOB)
3. **More recent scholarship** if sources equally authoritative
4. **Document the conflict** in "Data Quality & Known Gaps" section

**Example**:
- Source A: "15. Panzer had 120 tanks"
- Source B: "15. Panzer had 142 tanks"
- **Resolution**: Use more specific source (divisional war diary > general OOB)
- **Documentation**: "Tank count varies in sources (120-142), used 120 from war diary"

### Estimation When Necessary

When data is unavailable:

1. **Use establishment tables** (authorized strength) with `"estimated": true`
2. **Interpolate from adjacent quarters** if reasonable
3. **Compare to similar units** (e.g., other British infantry divisions)
4. **Document estimation method** in "Known Gaps" section

**Example**:
- Personnel strength not found for 50th Infantry Division Q2 1941
- British infantry division establishment: 15,000-17,000
- Similar divisions (4th Indian, 5th Indian): 16,500 average
- **Estimate**: 16,000 with `"estimated": true`
- **Document**: "Personnel estimated from establishment table, exact strength not documented"

---

## Quality Metrics

### Unit-Level Metrics

- **Confidence Score**: 75-100% (target: 80%+)
- **Schema Compliance**: Pass/Fail (target: 100%)
- **Source Citations**: Count (target: 5+ sources)
- **Cross-Referenced Facts**: % (target: 80%+)
- **Known Gaps**: Count (target: minimize)

### Project-Level Metrics

- **Units Completed**: Count / Total planned
- **Average Confidence**: Mean across all units
- **Schema Compliance Rate**: % units passing validation
- **Template Compliance**: % chapters following template v2.0

---

## Continuous Improvement

### Gap Filling Process

1. **Document all gaps** during initial extraction
2. **Prioritize gaps** (Priority 1: critical, Priority 2: important, Priority 3: nice-to-have)
3. **Research additional sources** for Priority 1 gaps
4. **Update units** when new sources found
5. **Track improvement** in confidence scores over time

### Version Control

All unit files tracked with:
- **Schema version**: unified_toe_schema.json v1.0.0
- **Template version**: MDBOOK_CHAPTER_TEMPLATE.md v2.0
- **Last updated date**
- **Extraction date**
- **Change log** (when updated)

---

## Further Reading

- [Source Hierarchy](./source-hierarchy.md) - 3-tier source prioritization
- [Data Quality Standards](./data-quality.md) - Detailed quality requirements
- [Validation Process](./validation.md) - Schema and historical validation

---

**Last Updated**: 2025-10-12
**Applies To**: All units in project
**Minimum Standards**: 75% confidence, 100% schema compliance, template v2.0 adherence
