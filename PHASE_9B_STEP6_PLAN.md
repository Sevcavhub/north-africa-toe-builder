# Phase 9B Step 6: Book Generation - Implementation Plan

**Date**: November 2, 2025
**Status**: Planning
**Estimated Duration**: 10-15 hours
**Target**: Generate 45 historical scenarios across 4 battle books for MVP

---

## 📋 Executive Summary

**Goal**: Transform the complete generator toolkit from Steps 1-5 into actual book content by generating 45 production-ready historical scenarios across 4 battle books.

**Context**: Steps 1-5 built the complete infrastructure:
- ✅ Reference database (500 vehicles, 57 guns)
- ✅ Conversion formulas (95-100% accuracy)
- ✅ Points/BR calculators (90-100% accuracy)
- ✅ Database enrichment (469/469 items, 100% success)
- ✅ Generator toolkit (7 generators, 8/8 tests passed)
- ✅ Special rules (57 rules, 1,599 linkages, 100% coverage)

**Step 6 Focus**: Content generation - use the tools to create the actual product content.

---

## 🎯 Deliverables

### 1. Pre-Generated Historical Scenarios (45 total)

**MVP Target - 4 Battle Books**:
- **Operation Battleaxe** (June 1941): 8 scenarios
- **Operation Crusader** (Nov-Dec 1941): 12 scenarios
- **Gazala** (May-June 1942): 15 scenarios
- **First El Alamein** (July 1942): 10 scenarios

**Each Scenario Must Include**:
- 2-page format (BattleGroup standard)
- Historical narrative (what happened, why it matters)
- Specific date and location
- Forces: Exact units from Phase 6 unit JSONs
- Terrain: Curated setup (not random)
- Victory conditions (objectives + BR threshold)
- Special rules (from bg_special_rules database)
- Historical outcome notes
- Image placeholders (photos, maps, miniatures)

### 2. Book Generation Workflow

**Automation Pipeline**:
1. Scenario research (identify historical engagements)
2. Unit selection (from Phase 6 JSONs by quarter)
3. Force roster generation (using force_roster_builder.py)
4. Terrain generation (curated templates)
5. Scenario text generation (2-page format)
6. Image placeholder creation
7. MDBook integration
8. PDF generation

### 3. Directory Structure

```
books/
├── battleaxe/
│   ├── book/                    # MDBook source
│   │   ├── src/
│   │   │   ├── SUMMARY.md       # Table of contents
│   │   │   ├── introduction.md
│   │   │   ├── scenarios/
│   │   │   │   ├── scenario_01_fort_capuzzo.md
│   │   │   │   ├── scenario_02_halfaya_pass.md
│   │   │   │   └── ... (8 total)
│   │   │   ├── army_lists/
│   │   │   │   ├── british_1941q2.md
│   │   │   │   └── german_1941q2.md
│   │   │   ├── datacards/       # Equipment datacards
│   │   │   └── appendices/
│   │   └── book.toml            # MDBook config
│   ├── latex/                   # LaTeX source (PDF version)
│   └── images/
│       ├── battles/             # Historical photos
│       ├── miniatures/          # Miniature photos
│       └── maps/                # Deployment maps
├── crusader/                    # Same structure
├── gazala/                      # Same structure
└── first_alamein/               # Same structure
```

### 4. Markdown → PDF Pipeline

**Two Output Formats**:

1. **MDBook → HTML** (web version)
   - Responsive design
   - Searchable
   - Cross-linked
   - Free online access

2. **LaTeX → PDF** (print version)
   - Professional typography
   - Print-ready layout
   - ISBN-ready format
   - Print-on-demand compatible

---

## 🔧 Technical Implementation

### Part 1: Scenario Research Document (2 hours)

**Objective**: Create comprehensive list of all 45 scenarios with historical sources

**File**: `books/scenario_research.md`

**For Each Scenario**:
- Battle name and date
- Historical engagement details
- Primary sources (books, documents)
- Participating units (verified from Phase 6)
- Geographic location
- Scale (patrol/squad/platoon/company/battalion)
- Special characteristics (night attack, desert storm, etc.)

**Research Sources**:
- "The Desert War" trilogy by Alan Moorehead
- Official unit war diaries (if available)
- "Afrika Korps" by Bruce Quarrie
- "The Crucible of War" series by Barrie Pitt
- BattleGroup: Tobruk supplement (once purchased in Step 7)

### Part 2: Directory Structure Setup (1 hour)

**Script**: `scripts/battlegroup/book/setup_book_structure.py`

**Tasks**:
1. Create all 4 book directories
2. Initialize MDBook config files
3. Create image directory placeholders
4. Set up LaTeX templates
5. Create SUMMARY.md templates for each book

**Validation**: All directories exist, all templates created

### Part 3: Scenario Generation Workflow (3 hours)

**Script**: `scripts/battlegroup/book/scenario_generator_workflow.py`

**Workflow Stages**:

1. **Research Phase**
   - Input: Battle name, date, units involved
   - Output: Historical context markdown

2. **Unit Selection Phase**
   - Query Phase 6 unit JSONs by quarter
   - Filter to units present at battle
   - Extract TO&E data

3. **Force Roster Generation**
   - Use `force_roster_builder.py` from Step 5
   - Create attacker/defender force rosters
   - Calculate points/BR budgets
   - Enforce rarity restrictions

4. **Terrain Setup**
   - Select terrain template (desert open, escarpment, fortified, etc.)
   - Define deployment zones
   - Place objectives

5. **Scenario Assembly**
   - Combine all elements into 2-page markdown
   - Add historical narrative
   - Insert image placeholders
   - Add victory conditions
   - Include special rules

6. **Integration**
   - Save to book/src/scenarios/
   - Update SUMMARY.md
   - Link to army lists
   - Link to datacards

**Output**: Complete scenario markdown file ready for MDBook

### Part 4: Book 1 - Operation Battleaxe (2 hours)

**Battle Context**: June 15-17, 1941 - British offensive to relieve Tobruk

**8 Scenarios**:

1. **Fort Capuzzo Assault** (June 15, dawn)
   - British 4th Armoured Brigade vs German 104th Infantry Regiment
   - Company-level
   - Objective: Capture fort

2. **Halfaya Pass - "Hellfire Pass"** (June 15, morning)
   - British 4th Indian Division vs German 33rd Panzer Regiment + 88mm guns
   - Battalion-level
   - Special: German 88mm ambush

3. **Point 206 Tank Battle** (June 15, midday)
   - British 7th Armoured Division vs German 5th Light Division
   - Tank engagement
   - Open desert terrain

4. **Hafid Ridge** (June 15, afternoon)
   - British infantry vs German Panzergrenadiers
   - Platoon-level
   - Rocky terrain

5. **Counterattack at Capuzzo** (June 16, dawn)
   - German 15th Panzer Division vs British 4th Armoured Brigade
   - Combined arms
   - German counterattack

6. **The Cauldron** (June 16, midday)
   - British surrounded forces vs German Panzer assault
   - Defensive scenario
   - Encirclement mechanics

7. **Withdrawal Under Fire** (June 17, dawn)
   - British 7th Armoured Division retreat vs German pursuit
   - Mobile warfare
   - Fighting withdrawal

8. **Last Stand at Sidi Omar** (June 17, afternoon)
   - British rearguard vs German advance
   - Delaying action
   - Limited forces vs overwhelming odds

**Units Required** (from Phase 6):
- British: 7th Armoured Division, 4th Indian Division (1941-Q2)
- German: 15th Panzer Division, 5th Light Division (1941-Q2)

**Total Output**: 8 scenario files, ~16 pages

### Part 5: Book 2 - Operation Crusader (3 hours)

**Battle Context**: November 18 - December 30, 1941 - Largest desert battle to date

**12 Scenarios**:

1. **Opening Moves - Gabr Saleh** (Nov 18)
2. **Clash at Bir el Gubi** (Nov 19)
3. **Sidi Rezegh Airfield** (Nov 19)
4. **The Corridor to Tobruk** (Nov 21)
5. **Totensonntag - Sunday of the Dead** (Nov 23) - Massive tank battle
6. **Breakout from Tobruk** (Nov 24)
7. **Rommel's Dash to the Wire** (Nov 24-26)
8. **Battle of Sidi Rezegh II** (Nov 27)
9. **Relief of Tobruk** (Nov 28)
10. **Gazala Pursuit** (Dec 5-7)
11. **El Agheila Defensive Line** (Dec 15)
12. **Final Push to Benghazi** (Dec 24)

**Units Required** (from Phase 6):
- British: 7th Armoured Division, 4th Indian Division, 2nd New Zealand Division, 70th Infantry Division (Tobruk) (1941-Q4)
- German: 15th Panzer Division, 21st Panzer Division, 90th Light Division (1941-Q4)
- Italian: Ariete Division, Trieste Division (1941-Q4)

**Special Features**:
- Multi-day battles with unit progression
- Commonwealth diversity (British, NZ, Indian, SA)
- Italian forces prominently featured
- Largest scenarios (up to battalion+)

**Total Output**: 12 scenario files, ~24 pages

### Part 6: Book 3 - Gazala (4 hours)

**Battle Context**: May 26 - June 21, 1942 - Rommel's masterpiece, Free French at Bir Hacheim

**15 Scenarios**:

1. **Rommel's Left Hook** (May 26-27) - Opening offensive
2. **The Cauldron Forms** (May 28) - German trapped position
3. **150th Brigade Box** (May 29-June 1) - British defensive box destroyed
4. **Bir Hacheim - Free French Stand** (May 27-June 10) - 14-day siege, 3 scenarios
   - Day 1-3: Initial assault
   - Day 7-10: Continued siege
   - Day 11-14: Breakout
5. **Knightsbridge Box** (June 5-12) - Tank battles around supply base, 2 scenarios
6. **The Gazala Gallop** (June 13-14) - British retreat, 2 scenarios
7. **Tobruk Falls** (June 20-21) - Final assault, 2 scenarios
8. **Mersa Matruh** (June 26-27) - Pursuit into Egypt, 2 scenarios

**Units Required** (from Phase 6):
- British: 1st Armoured Division, 7th Armoured Division, 50th Infantry Division (1942-Q2)
- Free French: 1st Free French Brigade (1942-Q2)
- German: 15th Panzer Division, 21st Panzer Division, 90th Light Division (1942-Q2)
- Italian: Ariete Division, Trieste Division, Littorio Division (1942-Q2)

**Special Features**:
- Free French forces (different army list)
- Box defenses (fortified positions)
- Multi-day siege mechanics
- Largest scenario count (most complex battle)

**Total Output**: 15 scenario files, ~30 pages

### Part 7: Book 4 - First El Alamein (3 hours)

**Battle Context**: July 1-27, 1942 - Defensive stalemate, Rommel stopped

**10 Scenarios**:

1. **Ruweisat Ridge - First Assault** (July 1-3)
2. **Point 63** (July 10) - Australian attack
3. **Tel el Eisa** (July 10-11) - South African assault
4. **Miteirya Ridge** (July 14-15)
5. **Ruweisat Ridge - Second Assault** (July 15-16)
6. **El Mreir Depression** (July 21-22) - Tank battle
7. **Kidney Ridge** (July 22)
8. **Deir el Shein** (July 1) - Indian defense
9. **Alam el Onsol** (July 26-27) - Australian night attack
10. **Stalemate Patrol** (July 27) - No-man's land patrol

**Units Required** (from Phase 6):
- British: 1st Armoured Division, 7th Armoured Division (1942-Q3)
- Australian: 9th Australian Division (1942-Q3)
- South African: 1st South African Division (1942-Q3)
- Indian: 5th Indian Division (1942-Q3)
- New Zealand: 2nd New Zealand Division (1942-Q3)
- German: 15th Panzer Division, 21st Panzer Division, 90th Light Division (1942-Q3)
- Italian: Ariete Division, Littorio Division, Trento Division (1942-Q3)

**Special Features**:
- Commonwealth diversity (British, Australian, NZ, Indian, SA)
- Defensive battles (Axis defending for first time)
- Night attacks
- Attritional warfare

**Total Output**: 10 scenario files, ~20 pages

### Part 8: PDF Generation Pipeline (2 hours)

**Tools Required**:
- MDBook (already used in Step 5)
- Pandoc (Markdown → LaTeX)
- LaTeX distribution (TeX Live or MiKTeX)

**Script**: `scripts/battlegroup/book/generate_pdf.py`

**Pipeline Stages**:

1. **MDBook HTML Generation**
   - `mdbook build books/battleaxe/book`
   - Output: `books/battleaxe/book/book/index.html`
   - Web-ready format

2. **LaTeX Conversion**
   - Pandoc: Markdown → LaTeX
   - Template: Professional book layout
   - Styling: Desert-themed colors

3. **PDF Compilation**
   - `pdflatex` or `xelatex`
   - Multiple passes (for cross-references)
   - Output: Print-ready PDF

4. **Validation**
   - Check all cross-references
   - Verify image placeholders
   - Test print dimensions (US Letter / A4)

**Output**: 4 HTML books + 4 PDF books

---

## 📊 Integration with Existing Systems

### Phase 6 Unit Integration

**Data Source**: `data/output/units/` (402 unit JSONs)

**Query Method**:
```python
def get_units_for_quarter(nation, quarter, battle=None):
    """
    Get all units available for a given quarter
    Optionally filter by battle participation
    """
    # Example: get_units_for_quarter('german', '1941q2', 'Battleaxe')
    # Returns: [15th Panzer Division JSON, 5th Light Division JSON]
```

**Equipment Extraction**:
```python
def get_unit_equipment(unit_json):
    """
    Extract all equipment from unit JSON
    Cross-reference with equipment_battlegroup table
    Return list of equipment with BG stats
    """
```

### Equipment Database Integration

**Data Source**: `database/master_database.db` → `equipment_battlegroup` table

**Query Method**:
```python
def get_equipment_datacard(equipment_name, experience='regular'):
    """
    Generate BattleGroup datacard for equipment
    Uses datacard_generator.py from Step 5
    """
```

### Special Rules Integration

**Data Source**: `database/master_database.db` → `bg_special_rules`, `bg_equipment_special_rules` tables

**Query Method**:
```python
def get_unit_special_rules(equipment_list):
    """
    Get all applicable special rules for unit's equipment
    Returns: List of rule names and descriptions
    """
```

### Army List Integration

**Tool**: `army_list_generator.py` from Step 5

**Usage**:
```python
def generate_army_list(nation, quarter, battle):
    """
    Generate complete army list for nation/quarter
    Filter to equipment available at battle
    Include rarity restrictions
    """
```

---

## ✅ Success Criteria

From PROJECT_SCOPE.md Phase 9B Step 6 requirements:

| Criterion | Target | Validation Method |
|-----------|--------|-------------------|
| **45 scenarios generated** | 45 files | Count scenario markdown files |
| **All scenarios use Phase 6 units** | 100% | Verify unit JSON references |
| **All scenarios include force rosters** | 100% | Check roster sections exist |
| **All scenarios 2-page format** | 100% | Validate markdown structure |
| **MDBook builds successfully** | 4 books | `mdbook build` completes |
| **PDF generation works** | 4 PDFs | LaTeX compilation succeeds |
| **Image placeholders present** | 100% | Check image directory structure |
| **Special rules linked** | 100% | Verify rule references |

**Additional Quality Criteria**:
- Historical accuracy (dates, locations, units verified)
- Narrative quality (readable, engaging)
- Game balance (points/BR budgets reasonable)
- Completeness (all sections present)

---

## 🗂️ File Deliverables

### Scripts (6 new files, ~2,000 lines estimated)

```
scripts/battlegroup/book/
├── setup_book_structure.py          (~300 lines)
├── scenario_generator_workflow.py   (~600 lines)
├── generate_battleaxe_scenarios.py  (~200 lines)
├── generate_crusader_scenarios.py   (~300 lines)
├── generate_gazala_scenarios.py     (~350 lines)
├── generate_alamein_scenarios.py    (~250 lines)
└── generate_pdf.py                  (~200 lines)
```

### Book Content (45 scenarios + infrastructure)

```
books/
├── scenario_research.md              (~2,000 lines - research document)
├── battleaxe/                        (8 scenarios, ~1,600 lines)
├── crusader/                         (12 scenarios, ~2,400 lines)
├── gazala/                           (15 scenarios, ~3,000 lines)
└── first_alamein/                    (10 scenarios, ~2,000 lines)
```

**Total**: ~11,000 lines of scenario content + ~2,000 lines of code

### Documentation

```
PHASE_9B_STEP6_PLAN.md                (this file)
PHASE_9B_STEP6_PROGRESS.md            (tracking document)
PHASE_9B_STEP6_SUMMARY.md             (completion report)
```

---

## 📅 Work Schedule

**Part-by-Part Breakdown** (11 parts, 10-15 hours):

| Part | Task | Duration | Output |
|------|------|----------|--------|
| 1 | Scenario research document | 2 hours | scenario_research.md |
| 2 | Directory structure setup | 1 hour | All directories created |
| 3 | Scenario generation workflow | 3 hours | scenario_generator_workflow.py |
| 4 | Generate Battleaxe scenarios | 2 hours | 8 scenarios |
| 5 | Generate Crusader scenarios | 3 hours | 12 scenarios |
| 6 | Generate Gazala scenarios | 4 hours | 15 scenarios |
| 7 | Generate Alamein scenarios | 3 hours | 10 scenarios |
| 8 | PDF generation pipeline | 2 hours | 4 HTML + 4 PDF books |
| 9 | Validation suite | 1 hour | Validation tests |
| 10 | Integration testing | 1 hour | End-to-end test |
| 11 | Step 6 summary | 1 hour | PHASE_9B_STEP6_SUMMARY.md |

**Total**: 10-15 hours (flexible based on scenario complexity)

**Recommended Workflow**:
- Parts 1-3: Infrastructure (setup and tooling)
- Parts 4-7: Content generation (scenarios)
- Parts 8-11: Output and validation

---

## 🎯 Next Steps After This Plan

1. **Review this plan** with user for approval
2. **Begin Part 1**: Scenario research document
3. **Proceed sequentially** through parts 2-11
4. **Use Task tool** to parallelize scenario generation where possible
5. **Checkpoint frequently** (after each book completion)
6. **Document progress** in PHASE_9B_STEP6_PROGRESS.md

---

## 📚 Key Resources

**Generator Tools** (from Step 5):
- `datacard_generator.py` - Equipment datacards
- `army_list_generator.py` - Force lists by nation/quarter
- `force_roster_builder.py` - Force composition validation
- `scenario_generator.py` - Random scenario framework (will extend for historical)
- `historical_scenario_builder.py` - Historical scenario framework (will use)
- `book_structure_generator.py` - MDBook structure automation

**Database Tables**:
- `equipment_battlegroup` - 469 items with BG stats
- `bg_special_rules` - 57 rules
- `bg_equipment_special_rules` - 1,599 linkages
- `bg_reference_vehicles` - 500 reference vehicles
- `bg_reference_guns` - 57 reference guns

**Phase 6 Data**:
- `data/output/units/` - 402 unit JSONs with complete TO&E
- `data/output/chapters/` - 402 historical chapter files
- `north_africa_seed_units_COMPLETE.json` - Canonical unit list

**Historical Sources** (for research):
- "The Desert War" trilogy by Alan Moorehead
- "Afrika Korps" by Bruce Quarrie
- "The Crucible of War" series by Barrie Pitt
- Official unit war diaries (British National Archives)
- BattleGroup: Tobruk supplement (to purchase in Step 7)

---

## ⚠️ Risks and Mitigation

### Risk 1: Historical Research Time

**Risk**: Scenario research takes longer than estimated

**Mitigation**:
- Focus on well-documented battles first
- Use existing BattleGroup scenarios as templates
- Defer less-documented scenarios to future updates
- Prioritize quality over quantity (can reduce to 35-40 if needed)

### Risk 2: Phase 6 Unit Coverage Gaps

**Risk**: Some battles lack complete unit data

**Mitigation**:
- Check Phase 6 coverage before scenario selection
- Use generic "reinforced platoon" for minor gaps
- Document gaps for future research
- Focus on battles with complete unit data

### Risk 3: PDF Generation Technical Issues

**Risk**: LaTeX compilation errors or formatting issues

**Mitigation**:
- Test pipeline early (Part 2)
- Use proven LaTeX templates
- Fallback: HTML-only for MVP, PDF in Step 7
- Consider Pandoc HTML→PDF as alternative

### Risk 4: Scenario Balance

**Risk**: Generated scenarios unbalanced or unplayable

**Mitigation**:
- Use historical force ratios where known
- Cross-reference with BattleGroup official scenarios
- Flag scenarios for playtesting in Step 7
- Include "Designer Notes" for GM adjustments

---

## 🎉 Success Vision

**End State**: 4 complete battle books ready for Step 7 (playtesting and polish)

**Each Book Contains**:
- Introduction with battle overview
- Historical timeline
- 8-15 complete scenarios (2 pages each)
- Army lists for all nations/quarters
- Equipment datacards (referenced, not duplicated)
- Appendices (special rules, terrain notes)
- Image placeholders (for photos/miniatures)

**Format**:
- MDBook HTML version (web-viewable)
- LaTeX PDF version (print-ready)
- Professional layout
- Cross-referenced
- Searchable (HTML version)

**Commercial Readiness**:
- Content complete for MVP
- Ready for Step 7 playtesting
- Foundation for commercial release
- Extensible for Volume 2 (remaining 8 battles)

---

**Document Status**: ✅ COMPLETE - Ready for user review and Part 1 execution

**Estimated Total Time**: 10-15 hours (11 parts)

**Next Action**: User approval → Begin Part 1 (Scenario Research)
