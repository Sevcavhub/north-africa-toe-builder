# Phase 9B Step 5: Generator Enhancement - Implementation Plan

**Date**: November 2, 2025
**Phase**: 9B - BattleGroup Book Generation
**Step**: 5 of 7 - Generator Enhancement
**Estimated Duration**: 5-7 hours
**Status**: 🔄 IN PROGRESS - Planning complete

---

## 📋 Executive Summary

**Purpose**: Enhance the baseline generators created in Step 4 into production-ready tools capable of generating complete BattleGroup battle books.

**Foundation**: Step 4 created placeholder/baseline implementations
- Datacard generator (438 lines) - vehicles only
- Army list generator (268 lines) - simplified structure
- Force roster builder (71 lines) - placeholder only
- Campaign tracker (114 lines) - foundation only

**Step 5 Goal**: Transform these into complete, integrated generators ready for Step 6 book generation.

---

## 🎯 Success Criteria (From PROJECT_SCOPE.md)

| # | Criterion | Target | Validation Method |
|---|-----------|--------|-------------------|
| 1 | **Datacard generator handles all equipment types** | Vehicles, guns, defences, fire support | Generate 10+ samples each type |
| 2 | **Force roster builder validates composition** | Points/BR budgets, restrictions | Test 5+ historical forces |
| 3 | **Scenario generator creates playable scenarios** | Victory conditions, deployment, special rules | Generate 3+ test scenarios |
| 4 | **Book structure generator produces complete books** | TOC, chapters, formatting | Generate 1 complete book structure |

---

## 📦 Deliverables Overview

### Part 1: Enhanced Datacard Generator ✅ (Already handles all types via database)
**Current**: Handles vehicles only (template-based)
**Enhancement**: Add gun, defence, fire support templates and generation logic

**Files to Create/Modify**:
- Extend `datacard_generator.py` (+200 lines)
- Create `templates/datacard_gun.txt`
- Create `templates/datacard_defence.txt`
- Create `templates/datacard_fire_support.txt`

**Validation**: Generate datacards for:
- 10 vehicles (Tiger, Sherman, Valentine, Panzer III, etc.)
- 10 guns (88mm, 75mm, 6-pdr, etc.)
- 10 defences (pillboxes, trenches, minefields)
- 10 fire support missions (artillery, air support)

---

### Part 2: Special Rules Database Enhancement
**Current**: 8 generic rules in `bg_special_rules` table
**Enhancement**: Comprehensive catalog with equipment linkage

**Database Changes**:
- Expand `bg_special_rules` to 50+ rules
- Add `equipment_special_rules` junction table
- Link equipment to applicable rules

**Categories to Cover**:
- Tank special rules (HEAT-proof, sloped armor, wide tracks)
- Gun special rules (AP only, HE only, dual-purpose)
- Infantry special rules (assault, scout, engineer)
- Vehicle special rules (open-topped, fast, slow)
- Nation-specific rules

**Validation**: Query 20+ equipment items and verify correct rules assigned

---

### Part 3: Complete Force Roster Builder ⭐ HIGH PRIORITY
**Current**: 71-line placeholder with no logic
**Enhancement**: Full implementation with validation

**Features Required**:
1. **Unit Selection**:
   - Add units from army list
   - Track individual selections
   - Calculate running totals (points/BR)

2. **Budget Management**:
   - Enforce points budget
   - Track BR total (not a budget, just info)
   - Warn when approaching limits

3. **Composition Validation**:
   - HQ requirements (1 per force)
   - Support restrictions (max %, points limits)
   - Rarity enforcement (Unique, Restricted, Limited)

4. **Output Formats**:
   - Text roster for printing
   - JSON for digital use
   - HTML for web display

**Files to Create**:
- Replace `force_roster_builder.py` (500+ lines)
- Create `force_composition_validator.py` (300+ lines)
- Create `templates/force_roster.txt`

**Validation**: Build 5 test forces:
- German Kursk 1943 (500 pts)
- British Crusader 1941 (750 pts)
- American Tunisia 1943 (1000 pts)
- Italian Libya 1941 (500 pts)
- French Bir Hacheim 1942 (600 pts)

---

### Part 4: Scenario Generator ⭐ HIGH PRIORITY
**Current**: Does not exist
**Enhancement**: Create from scratch

**Features Required**:
1. **Scenario Structure**:
   - Title and historical context
   - Date and location
   - Belligerents (attacker/defender)
   - Force selection (points budgets)
   - Map size and terrain
   - Deployment zones
   - Victory conditions
   - Special rules
   - Turn limits

2. **Template System**:
   - Multiple scenario templates (assault, defense, meeting engagement, breakthrough, etc.)
   - Template variables for customization
   - Historical context injection

3. **Balance Calculation**:
   - Asymmetric point allocations (defender +20%, etc.)
   - Objective point values
   - Reinforcement schedules

4. **Integration**:
   - Pull from Phase 6 unit data (future)
   - Use army lists for force generation
   - Apply historical restrictions

**Files to Create**:
- `scenario_generator.py` (600+ lines)
- `templates/scenario_assault.txt`
- `templates/scenario_defense.txt`
- `templates/scenario_meeting_engagement.txt`
- `templates/scenario_breakthrough.txt`

**Validation**: Generate 3 test scenarios:
- Operation Battleaxe assault scenario
- Operation Crusader meeting engagement
- Gazala defensive scenario

---

### Part 5: Book Structure Generator ⭐ HIGH PRIORITY
**Current**: Does not exist
**Enhancement**: Create from scratch

**Features Required**:
1. **Book Structure**:
   - Title page
   - Table of contents (auto-generated)
   - Introduction chapter
   - Historical overview chapter
   - Equipment section (datacards)
   - Army lists section
   - Scenarios section (8-15 scenarios)
   - Appendices (rules, tables, references)

2. **Content Assembly**:
   - Aggregate all components
   - Apply consistent formatting
   - Generate cross-references
   - Create index

3. **Output Formats**:
   - Markdown (for MDBook)
   - HTML (for web)
   - LaTeX/PDF (for print)

4. **Template System**:
   - Book templates by battle
   - Section templates
   - Page layout templates

**Files to Create**:
- `book_structure_generator.py` (700+ lines)
- `templates/book_structure.yaml` (structure definition)
- `templates/book_toc.txt`
- `templates/book_chapter.txt`
- `templates/book_section.txt`

**Validation**: Generate complete book structure for Operation Battleaxe (June 1941)

---

### Part 6: Army List Generator Enhancement
**Current**: 268 lines, simplified structure
**Enhancement**: Add Phase 6 unit integration and restrictions

**Features to Add**:
1. **Historical Restrictions**:
   - Date-based availability (which units in which quarters)
   - Rarity enforcement (Unique: 0-1, Restricted: 0-1, Limited: unlimited)
   - Composition restrictions (max % support, required HQ)

2. **Phase 6 Integration**:
   - Parse unit JSONs from `data/output/units/`
   - Extract equipment compositions
   - Map to BattleGroup equipment database
   - Calculate points/BR from actual unit TO&E

3. **Force Organization**:
   - HQ section (platoon/company/battalion HQ)
   - Infantry section
   - Armor section
   - Artillery section
   - Anti-tank section
   - Reconnaissance section
   - Support section (engineers, transport, etc.)

4. **Output Enhancement**:
   - Detailed unit descriptions
   - Historical notes
   - Tactical suggestions
   - Force building advice

**Files to Modify**:
- Extend `army_list_generator.py` (+300 lines = 568 total)
- Create `phase6_unit_parser.py` (400+ lines)
- Create `templates/force_list_enhanced.txt`

**Validation**: Generate army lists for all 5 nations (german, british, american, italian, french) using Phase 6 data

---

### Part 7: Validation Suite
**Current**: Step 4 validation exists but incomplete
**Enhancement**: Comprehensive end-to-end validation

**Tests Required**:
1. **Datacard Generation**:
   - All equipment types generate correctly
   - All 4 experience levels work
   - Templates render properly

2. **Force Roster Building**:
   - Point budgets enforced
   - Composition rules validated
   - Output formats correct

3. **Scenario Generation**:
   - All templates work
   - Victory conditions balance
   - Special rules apply correctly

4. **Book Structure**:
   - TOC generates correctly
   - Cross-references valid
   - All sections present

5. **Integration**:
   - Phase 6 units parse correctly
   - Equipment mapping works
   - Points/BR calculations accurate

**Files to Create**:
- `validate_step5.py` (500+ lines)
- `test_fixtures/` directory with test data

**Validation**: All tests pass (100% success rate)

---

### Part 8: Completion Report
**Current**: Does not exist
**Enhancement**: Comprehensive documentation

**Contents**:
- Executive summary
- Detailed implementation notes
- Validation results
- Usage examples
- Next steps (Step 6)

**Files to Create**:
- `PHASE_9B_STEP5_SUMMARY.md` (5,000+ words)

---

## 🔧 Technical Architecture

### Data Flow

```
Phase 6 Unit JSONs
    ↓
Unit Parser → Equipment Mapping
    ↓
BattleGroup Database (469 items)
    ↓
    ├→ Datacard Generator → Datacards (vehicles, guns, defences, fire support)
    ├→ Army List Generator → Force Lists (by nation, quarter)
    ├→ Force Roster Builder → Player Rosters (selected forces)
    ├→ Scenario Generator → Playable Scenarios (8-15 per battle)
    └→ Book Structure Generator → Complete Books (45-70 pages)
```

### Integration Points

1. **Database Layer** (Step 4 complete):
   - `equipment_battlegroup` table (469 items, all enriched)
   - Lookup tables for conversions
   - Special rules catalog

2. **Conversion Layer** (Steps 2-3 complete):
   - Armor, movement, HE, penetration converters
   - Points, BR calculators
   - All validated at 90-100% accuracy

3. **Generation Layer** (Step 5 focus):
   - Enhanced generators (datacards, army lists, rosters)
   - New generators (scenarios, book structure)
   - Template system

4. **Content Layer** (Step 6 future):
   - Historical unit data (Phase 6: 402 units)
   - Battle narratives
   - Scenario details

---

## 📊 Implementation Phases

### Phase A: Foundation Enhancement (1-2 hours)
- Part 1: Datacard generator (all types)
- Part 2: Special rules database expansion

### Phase B: Core Generators (2-3 hours)
- Part 3: Force roster builder (complete implementation)
- Part 4: Scenario generator (from scratch)

### Phase C: Integration (1-2 hours)
- Part 5: Book structure generator (assembly)
- Part 6: Army list generator (Phase 6 integration)

### Phase D: Validation & Documentation (1 hour)
- Part 7: Comprehensive validation suite
- Part 8: Completion report and documentation

**Total Estimated**: 5-7 hours

---

## 🚀 Implementation Order

**Recommended sequence** (based on dependencies):

1. **Part 2: Special Rules** (no dependencies, enables richer datacards)
2. **Part 1: Enhanced Datacards** (uses special rules from Part 2)
3. **Part 6: Army List Enhancement** (enables force building)
4. **Part 3: Force Roster Builder** (uses army lists from Part 6)
5. **Part 4: Scenario Generator** (uses rosters from Part 3)
6. **Part 5: Book Structure Generator** (assembles all previous parts)
7. **Part 7: Validation** (validates all parts)
8. **Part 8: Documentation** (final deliverable)

---

## 📝 Notes

### Scope Decisions

**INCLUDED in Step 5**:
- All generator enhancements
- Template system
- Phase 6 integration architecture
- Validation framework

**DEFERRED to Step 6**:
- Actual content generation (12 battle books)
- Historical narrative writing
- Scenario playtesting
- Professional layout and design

### Dependencies

**From Previous Steps**:
- ✅ Step 4: Database schema (8 tables, 469 items enriched)
- ✅ Steps 2-3: Conversion tools (all validated)
- ✅ Step 1: Reference database (500 vehicles, 57 guns)

**For Next Steps**:
- Step 6: Book Generation (requires all Step 5 generators)
- Step 7: Validation & Polish (requires Step 6 content)

### Quality Standards

**Code Quality**:
- Type hints for all functions
- Docstrings for all classes/methods
- CLI interfaces for all tools
- Error handling with informative messages
- Unicode-safe output (Windows compatibility)

**Output Quality**:
- Professional formatting
- Consistent terminology
- Historical accuracy
- Game balance

**Validation Quality**:
- 95%+ accuracy for calculations
- 100% success for generation
- No crashes or errors

---

## 🎯 Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| **Datacard coverage** | All 4 types (vehicles, guns, defences, fire support) | Generate 40+ datacards |
| **Special rules catalog** | 50+ rules with equipment linkage | Query coverage 80%+ |
| **Force roster validation** | Points/BR/composition rules enforced | Build 5 test forces |
| **Scenario generation** | 3+ templates functional | Generate 3 test scenarios |
| **Book structure** | Complete TOC and sections | Generate 1 book structure |
| **Army list integration** | Phase 6 units parsed and mapped | Generate 5 nation lists |
| **Validation suite** | All tests pass | 100% success rate |
| **Code quality** | Type hints, docstrings, CLI | Manual review |

---

## 🔗 References

**Key Files**:
- `PROJECT_SCOPE.md` - Phase 9B specification
- `PHASE_9B_SESSION_SUMMARY.md` - Overall progress
- `PHASE_9B_STEP4_SUMMARY.md` - Foundation from Step 4
- `schemas/unified_toe_schema.json` - Phase 6 data structure

**Database**:
- `database/master_database.db` - Main database
- `equipment_battlegroup` table - 469 enriched items
- `bg_reference_*` tables - Reference data

**Existing Generators** (Step 4):
- `scripts/battlegroup/generators/datacard_generator.py` (438 lines)
- `scripts/battlegroup/generators/army_list_generator.py` (268 lines)
- `scripts/battlegroup/generators/force_roster_builder.py` (71 lines)
- `scripts/battlegroup/generators/campaign_tracker.py` (114 lines)

---

**Document Version**: 1.0
**Status**: ✅ Planning complete - Ready for implementation
**Next**: Begin Part 2 (Special Rules Database Enhancement)
