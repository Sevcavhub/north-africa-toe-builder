# North Africa TO&E Multi-Agent Builder - Project Context

## Project Goal
Build a multi-agent orchestration system that creates complete Table of Organization & Equipment (TO&E) data from Theater level down to individual Squad level, with full Strategic Command Summary (SCM) schema detail at every organizational tier.

## What We're Building

### Data Structure Hierarchy
```
Theater SCM (Summary totals only)
  ↓
Corps TO&E (Full SCM detail)
  ↓
Division TO&E (Full SCM detail)
  ↓
Regiment TO&E (Full SCM detail)
  ↓
Battalion TO&E (Full SCM detail)
  ↓
Company TO&E (Full SCM detail)
  ↓
Platoon TO&E (Full SCM detail)
  ↓
Squad TO&E (Full SCM detail + individual soldier positions)
```

### Key Requirements
1. **Every organizational level** has complete SCM-level equipment detail
2. **Bottom-up aggregation**: Squad totals → Platoon → Company → ... → Theater
3. **Validation at every level**: Math must work at each tier
4. **Individual positions**: Squad level has every soldier with weapon/equipment
5. **Multi-format output**: MDBook chapters, wargaming scenarios, SQL database

## Agent Architecture

### 15 Specialist Agents Organized in 6 Categories

#### 1. Source & Extraction (2 agents)
- **document_parser**: Parse PDFs and extract facts with citations
- **historical_research**: Cross-reference multiple sources, identify conflicts

#### 2. Structure & Organization (3 agents)
- **org_hierarchy**: Build Theater → Squad organizational tree
- **toe_template**: Create standard unit templates (reusable)
- **unit_instantiation**: Create specific units from templates

#### 3. Equipment Distribution (3 agents)
- **theater_allocator**: Distribute theater totals across divisions
- **division_cascader**: Cascade division equipment down to squad level
- **equipment_reconciliation**: Verify all totals match at every level

#### 4. Aggregation & Calculation (2 agents)
- **bottom_up_aggregator**: Aggregate squad → platoon → company → ... → theater
- **top3_calculator**: Calculate top 3 weapons at each level

#### 5. Validation (2 agents)
- **schema_validator**: Validate against unified TO&E schema
- **historical_accuracy**: Verify against historical sources

#### 6. Output & Generation (3 agents)
- **book_chapter_generator**: Generate MDBook markdown chapters
- **scenario_exporter**: Export wargaming scenarios (WITW, TOAW, etc.)
- **sql_populator**: Generate SQL INSERT statements

### Master Orchestrator Workflow

**Phase 1: Source Extraction**
- Parse source documents
- Extract and verify facts
- Build citation database

**Phase 2: Organization Building**
- Build organizational hierarchy
- Create unit templates
- Instantiate all units (Theater → Squad)

**Phase 3: Equipment Distribution**
- Allocate theater equipment to divisions
- Cascade division equipment down through hierarchy
- Reconcile totals at all levels

**Phase 4: Aggregation**
- Aggregate squad data upward
- Calculate summary statistics
- Generate theater SCM

**Phase 5: Validation**
- Schema compliance checks
- Historical accuracy verification
- Math validation (parent = sum of children)

**Phase 6: Output Generation**
- Generate MDBook chapters
- Export wargaming scenarios
- Create SQL database scripts

## Example Data: Italian 10th Army (1940-Q2)

### Theater Level
- **Personnel**: 200,000 total
- **Tanks**: 170 (72 M11/39, 98 L3/35)
- **Artillery**: 876 pieces
- **Top 3 Weapons**: 166,152 Carcano M1891, 13,846 Breda M30, 180 47mm AT

### Corps Level (XXI Corpo d'Armata)
- **Personnel**: 35,000
- **Commander**: Generale di Corpo d'Armata Lorenzo Dalmazzo
- **Divisions**: 4 (Sirte, Sabratha, Cirene, Catanzaro)

### Division Level (Sirte Division)
- **Type**: Colonial Infantry Division (Libyan)
- **Personnel**: 8,000 (200 Italian officers, 7,800 Libyan askaris)
- **Regiments**: 2 infantry + 1 artillery

### Squad Level (Rifle Squad)
- **Personnel**: 13 men
  - 1 Caporale (Squad Leader): Carcano M1891 + Beretta M1934 pistol
  - 1 Soldato Scelto (Assistant): Carcano M1891
  - 1 Soldato (LMG Gunner): Breda M30 + 600 rounds
  - 2 Soldato (LMG team): Carcano M1891 + carry LMG ammo
  - 8 Soldato (Riflemen): Carcano M1891 each
- **Weapons**: 12 Carcano M1891, 1 Breda M30, 1 Beretta M1934
- **Ammunition**: 1,584 rifle rounds, 600 LMG rounds, 26 hand grenades

## Equipment Aggregation Example

```
Squad: 12 Carcano + 1 Breda
  ↓ ×4 squads
Platoon: 48 Carcano + 4 Breda (+ 4 HQ weapons = 52 total)
  ↓ ×3 platoons
Company: 156 Carcano + 12 Breda (+ 9 HQ weapons = 165 total)
  ↓ ×4 companies
Battalion: 650 Carcano + 36 Breda
  ↓ ×3 battalions
Regiment: 2,000 Carcano + 108 Breda
  ↓ ×2 regiments + division troops
Division: 7,200 Carcano + 240 Breda
  ↓ ×4 divisions
Corps: 28,000 Carcano + 840 Breda
  ↓ ×3 corps
Theater: 166,152 Carcano + 13,846 Breda
```

## Technical Implementation

### Technology Stack
- **Language**: JavaScript/Node.js
- **AI**: Claude API (Sonnet 4)
- **Formats**: JSON, Markdown, SQL, CSV
- **Tools**: VS Code, Claude Desktop

### Data Validation Rules
1. `tanks.total = sum(heavy + medium + light)`
2. `total_personnel ≈ officers + ncos + enlisted (±5%)`
3. `ground_vehicles_total ≥ sum(all vehicle categories)`
4. `artillery_total ≥ sum(field + anti_tank + anti_aircraft)`
5. Parent unit total = sum of all child units (±5%)

### Agent Communication Protocol
```json
{
  "agent_request": {
    "agent_id": "string",
    "task_id": "uuid",
    "inputs": {},
    "context": {
      "nation": "italian",
      "quarter": "1940-Q2"
    }
  },
  "agent_response": {
    "status": "success|error|partial",
    "outputs": {},
    "metadata": {
      "confidence": 85,
      "execution_time_ms": 1234
    }
  }
}
```

## Key Design Decisions

### Why Squad-Level Detail?
- **Wargaming accuracy**: Scenarios need individual soldier positions
- **Equipment tracking**: Know exactly where every weapon is
- **Validation**: Can verify totals sum correctly at every level
- **Flexibility**: Can generate scenarios at any organizational level

### Why Full SCM Detail at Every Level?
- **Self-contained units**: Each JSON file is complete
- **Scenario generation**: Can create battles using any level
- **No data loss**: Nothing falls through cracks
- **Easy validation**: Check parent = sum(children) at any level

### Why Multi-Agent vs Monolithic?
- **Specialization**: Each agent focuses on one task
- **Reliability**: Failed agent doesn't break entire system
- **Parallelization**: Can run multiple agents concurrently
- **Maintainability**: Easy to update/improve individual agents
- **Transparency**: Clear audit trail of what each agent did

## Known Challenges & Solutions

### Challenge 1: Data Conflicts
**Problem**: Current comprehensive JSON has 3 different tank totals
**Solution**: Single source of truth at squad/company level, aggregate upward

### Challenge 2: Missing Data
**Problem**: Some commander names unknown, equipment details unclear
**Solution**: Confidence scores + "Unknown" with low confidence flag

### Challenge 3: Template vs Instance
**Problem**: Units deviate from standard TO&E
**Solution**: Templates as base, track deviations explicitly

### Challenge 4: Equipment Not at Squad Level
**Problem**: Artillery, vehicles assigned to battalion/company HQ
**Solution**: Support units separate from rifle squads

## Success Criteria

Project succeeds when:
1. ✓ All organizational levels have complete SCM detail
2. ✓ Squad → Theater aggregation math is perfect (±5%)
3. ✓ Can generate book chapters like German example
4. ✓ Can export wargaming scenarios (WITW format)
5. ✓ Can populate SQL database
6. ✓ Schema validation passes at all levels
7. ✓ Historical accuracy > 85% confidence
8. ✓ System handles multiple nations/quarters

## Files Reference

### Core Files
- `src/orchestrator.js` - Main orchestration engine
- `agents/agent_catalog.json` - All 15 agent definitions
- `schemas/unified_toe_schema.json` - Data structure definition
- `schemas/scm_schema.json` - Strategic Command Summary schema

### Data Files
- `data/sources/1940-Q2_italian.json` - Current comprehensive data
- `templates/italian_rifle_squad_1940.json` - Squad template
- `data/output/chapters/` - Generated MDBook chapters

### Documentation
- `docs/PROJECT_CONTEXT.md` - This file
- `docs/AGENT_GUIDE.md` - How to create new agents
- `docs/SCHEMA_GUIDE.md` - Schema documentation

## Getting Started with Claude IDE

### Initial Prompt
```
I'm building a multi-agent system to create military TO&E data.

Context: I have PROJECT_CONTEXT.md with full background

Current task: [Implement agent framework | Test first agent | etc.]

Please review the context and help me [specific task].
```

### When Resuming
```
Continuing work on North Africa TO&E builder.

Last completed: [Phase/task completed]
Current status: [What's been done]
Next task: [What to do next]

Context available in PROJECT_CONTEXT.md
```

## Development Roadmap

### Phase 1: Foundation (Current)
- [x] Design architecture
- [x] Define agent catalog
- [x] Create schemas
- [ ] Implement orchestrator framework
- [ ] Test first 3 agents

### Phase 2: Core Implementation
- [ ] Implement all 15 agents
- [ ] Build validation system
- [ ] Create test suite
- [ ] Handle error cases

### Phase 3: Data Generation
- [ ] Process Italian 10th Army (1940-Q2)
- [ ] Process British Western Desert Force (1940-Q2)
- [ ] Validate all data
- [ ] Generate outputs

### Phase 4: Scale & Polish
- [ ] Add more quarters (1940-Q3, Q4, etc.)
- [ ] Add more nations (German Afrika Korps)
- [ ] Optimize performance
- [ ] Complete documentation

## Contact & Review Points

Agent will pause for human review at:
- End of each phase
- Any confidence score < 75%
- Conflicting source data
- Validation failures
- Unexpected errors

---

Last Updated: 2025-10-09
Version: 1.0.0
