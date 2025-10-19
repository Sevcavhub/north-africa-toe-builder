# Battlegroup Wargame Integration

## Overview

This document describes the integration of **Battlegroup** (WWII tabletop wargame system) with our North Africa TO&E project, enabling automatic scenario generation from historical unit data.

---

## What is Battlegroup?

**Battlegroup** is a 15mm/20mm scale WWII miniatures wargame system that emphasizes:
- Historical accuracy with theatre-specific supplements
- Battle Rating system (attrition-based victory conditions)
- Combined-arms tactics (infantry, armor, artillery, air support)
- Detailed vehicle/gun statistics

**Key Features**:
- Points-based force selection (100-2000+ points)
- Four game sizes: Squad, Platoon, Company, Battalion
- Morale system with unit experience levels (Inexperienced, Regular, Veteran, Elite)
- Scenario-driven gameplay with historical contexts

---

## Project Goals

**Primary Goal**: Generate playable Battlegroup scenarios directly from our historical TO&E database

**Why Battlegroup?**
1. ✅ Matches our data granularity (individual vehicles, squad-level detail)
2. ✅ Historical focus aligns with our primary sources (Tessin, Army Lists, Field Manuals)
3. ✅ Database integration possible (our equipment DB has all needed specs)
4. ✅ Scenario format works for North Africa campaign (1940-1943)
5. ✅ Commercial viability (wargamers buy scenario books)

---

## Completed Work (October 19, 2025)

### 1. PDF Text Extraction

**File**: `sources/battlegroup_rules_extracted.txt`
- **Source**: Battlegroup Rules.pdf (66 pages, 7.93 MB)
- **Extracted**: 219,289 characters of full text
- **Method**: Node.js script using `pdf2json` library
- **Script**: `scripts/extract_battlegroup_pdf.js`

**Analysis Data**: `sources/battlegroup_rules_analysis.json`
- Keyword frequency analysis (game mechanics, unit stats)
- Section identification
- Metadata (pages, file size, extraction timestamp)

### 2. Game Mechanics Analysis

**Comprehensive Guide**: `sources/BATTLEGROUP_SCENARIO_GUIDE.md`

**Key Findings**:

**Core Mechanic - Battle Rating (BR) System**:
- Each unit has BR value (0-5) + experience level (i/r/v/e)
- Players draw numbered counters (1-5) when units destroyed, rallied, etc.
- When total counters ≥ total BR, battlegroup breaks (loses)
- **Perfect for historical accuracy**: Important units (HQ, heavy tanks) have high BR

**Unit Statistics Required**:
```
Infantry:
- Rate of Fire (ROF): Shots per turn
- Morale: Quality level
- Movement: Inches per turn
- Special Rules: AT grenades, engineer, etc.

Vehicles:
- Armor: Front/Side/Rear values (1-16 or A-L)
- Penetration: Gun effectiveness (1-15+)
- Rate of Fire: Shots per turn
- Movement: Speed in inches
- Special Rules: Radio, smoke, etc.

Artillery/Guns:
- HE Size: Very Light, Light, Medium, Heavy
- Penetration: Same as vehicles
- Range: Direct fire and indirect (via spotter)
```

**Game Sizes**:
| Size | Points | Table (20mm) | Typical Forces |
|------|--------|--------------|----------------|
| Squad | 250 | 6' x 4' | 1-2 tanks, 1-2 infantry squads |
| Platoon | 500 | 6' x 6' | 3-5 tanks, 2-4 squads, 1-2 guns |
| Company | 1000 | 6' x 8' | 8-12 tanks, 5-8 squads, artillery |
| Battalion | 1500+ | 6' x 10'+ | 15+ tanks, 10+ squads, full support |

### 3. Historical TO&E Mapping

**Database Integration**:

Our existing `master_database.db` already contains ALL data needed:

**WWIITANKS Gun Data** → Battlegroup Penetration:
```
Conversion Formula:
Penetration @ 500m (mm) → BG Pen Value

Example:
50mm KwK 38 L/42 (Panzer III):
- WWIITANKS: 61mm @ 500m
- Battlegroup: Pen 6
```

**WWIITANKS Armor Data** → Battlegroup Armor Value:
```
Conversion Formula:
Armor thickness (mm) → BG Armor Value

Example:
Panzer III Ausf F (1941):
- Front: 50mm → Armor 7
- Side: 30mm → Armor 5
- Rear: 21mm → Armor 3
```

**Points Cost Estimation**:
Since we don't have official Battlegroup North Africa supplement, we use relative power formula:
```
Tank Points = Base + Armor Bonus + Gun Bonus + Special Rules

Example: Panzer III Ausf F
- Base (Medium tank): 100pts
- Armor (Front 7): +20pts
- Gun (Pen 6): +20pts
- Special (Radio, Smoke): +15pts
- **Total: ~155pts**
```

**BR Value Assignment**:
Based on unit importance and historical context:
```
North Africa Experience Levels:

German 1940-1941: Veteran/Elite (v/e)
German 1942-1943: Veteran (v)
Italian 1940-1942: Regular/Inexperienced (r/i)
British 1940-1941: Regular (r)
British 1941-1942 (Desert Rats): Veteran/Elite (v/e)
American 1942-1943: Inexperienced → Regular (i → r/v)
```

### 4. Scenario Format Documentation

**Complete Example Scenario**:
"Battle of Halfaya Pass" (Operation Battleaxe, June 15, 1941)

Includes:
- ✅ Historical context (2-3 paragraphs)
- ✅ Force lists with points and BR values
- ✅ Deployment map and zones
- ✅ Victory conditions (primary + secondary objectives)
- ✅ Special rules (historical doctrine, terrain effects)
- ✅ Designer notes (balance, variations, historical accuracy)
- ✅ Player briefings (separate for each commander)

**Template Structure**:
```markdown
# Battle Title
## Operation Name, Date

### Historical Context
[Strategic situation, forces involved, objectives]

### Forces
[Points-based force lists with BR totals]

### Table Setup
[Terrain, objectives, map]

### Deployment
[Starting positions, reinforcement schedule]

### Victory Conditions
[Primary: BR break, Secondary: objectives, special goals]

### Special Rules
[Historical constraints, weather, doctrine rules]

### Briefings
[Separate narrative for each player]
```

---

## Database Schema

### Proposed: `battlegroup_stats.db`

```sql
-- Core vehicle statistics for Battlegroup scenarios
CREATE TABLE bg_vehicles (
    vehicle_id TEXT PRIMARY KEY,
    name TEXT,
    nation TEXT,
    front_armor INTEGER,
    side_armor INTEGER,
    rear_armor INTEGER,
    gun_pen INTEGER,
    he_size TEXT,
    rof INTEGER,
    movement INTEGER,
    points_cost INTEGER,
    br_value INTEGER,
    experience TEXT,
    special_rules TEXT,
    source TEXT
);

-- Gun/AT weapon statistics
CREATE TABLE bg_guns (
    gun_id TEXT PRIMARY KEY,
    name TEXT,
    caliber TEXT,
    pen INTEGER,
    he_size TEXT,
    range INTEGER,
    rof INTEGER,
    points_cost INTEGER,
    br_value INTEGER,
    special_rules TEXT
);

-- Infantry unit templates
CREATE TABLE bg_infantry (
    unit_id TEXT PRIMARY KEY,
    name TEXT,
    nation TEXT,
    size INTEGER,
    equipment TEXT,
    rof INTEGER,
    morale INTEGER,
    points_cost INTEGER,
    br_value INTEGER,
    experience TEXT,
    special_rules TEXT
);

-- Special rules definitions
CREATE TABLE bg_special_rules (
    rule_id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    points_modifier INTEGER,
    applies_to TEXT
);

-- Link to our master database
CREATE TABLE bg_equipment_mapping (
    bg_equipment_id TEXT,
    master_db_equipment_id TEXT,
    conversion_notes TEXT,
    PRIMARY KEY (bg_equipment_id, master_db_equipment_id)
);
```

---

## Next Steps (Implementation)

### Phase 1: Database Creation

**Create `battlegroup_stats.db`**:
```bash
node scripts/create_battlegroup_database.js
```

**Import Sample Data**:
- 20-30 North Africa vehicles (Panzer II/III/IV, Matilda, Crusader, M3/M4, etc.)
- 15-20 guns (50mm PaK 38, 88mm FlaK, 25-pdr, 2-pdr, etc.)
- 10-15 infantry types (German rifle squad, British section, Italian squad, etc.)

### Phase 2: Scenario Generator Script

**Create `scripts/generate_battlegroup_scenario.js`**:

```javascript
Inputs:
- Unit TO&E JSON (from our Phase 6 output)
- Scenario size (squad/platoon/company/battalion)
- Historical battle context (date, location, operations)

Process:
1. Load TO&E JSON
2. Query battlegroup_stats.db for equipment stats
3. Calculate points costs and BR values
4. Scale forces to scenario size
5. Generate opposing force (historical enemy)
6. Create scenario narrative
7. Apply special rules (doctrine, weather, terrain)

Outputs:
- Markdown scenario file (print-ready)
- JSON scenario data (for future digital tools)
- Force roster sheets (player handouts)
```

### Phase 3: Batch Scenario Generation

**Campaign Books**:

Using our extracted units, generate:

**Operation Battleaxe** (June 1941):
- 6 scenarios (platoon to company size)
- British vs German/Italian
- Linked campaign with carry-over forces

**Operation Crusader** (November 1941):
- 8 scenarios (company to battalion size)
- British relief of Tobruk
- Campaign rules for attrition and replacements

**Gazala** (May 1942):
- 10 scenarios (battalion size)
- Rommel's greatest victory
- Free French forces included

**El Alamein** (October-November 1942):
- 12 scenarios (company to battalion size)
- Montgomery vs Rommel
- Commonwealth forces (Australian, New Zealand, Indian, South African)

**Operation Torch** (November 1942):
- 8 scenarios (platoon to battalion size)
- American debut in North Africa
- US inexperienced units vs Vichy French, then Germans

**Tunisia** (1942-1943):
- 10 scenarios (company to battalion size)
- Final North Africa battles
- British, American, Free French vs German/Italian

**Total**: 54+ scenarios from our TO&E database!

### Phase 4: Commercial Product

**Kickstarter Product Outline**:

**Title**: *Battlegroup: North Africa - The Complete Campaign*

**Contents**:
1. **Hardcover Campaign Book** (200+ pages)
   - Historical overview (1940-1943)
   - 54 scenarios with maps and briefings
   - Campaign rules (linked scenarios, experience, replacements)
   - Designer notes and historical analysis

2. **Army Lists** (North Africa Theatre Supplement)
   - German DAK (1941-1943)
   - Italian forces (1940-1943)
   - British 8th Army (1940-1943)
   - American forces (1942-1943)
   - Free French (1942-1943)

3. **Digital Tools**
   - Scenario generator web app
   - Force roster builder
   - Battle Rating calculator
   - Digital maps and tokens

4. **Physical Components**
   - Custom Battle Rating counters (North Africa themed)
   - Terrain templates (wadis, escarpments, oases)
   - Vehicle/gun data cards (200+ units)

**Target Market**:
- Battlegroup players (existing fanbase)
- WWII miniatures wargamers (general)
- Historical enthusiasts (North Africa campaign)

**Estimated Retail**: $60-80 for complete set

---

## Technical Integration

### Equipment Database Flow

```
Historical Sources (Tessin, Army Lists, Field Manuals)
    ↓
Phase 6: Ground Forces Unit Extraction
    ↓
Unit TO&E JSON (equipment counts)
    ↓
Master Database (equipment specs: WITW/OnWar/WWIITANKS)
    ↓
Conversion Scripts (armor/pen/stats → Battlegroup format)
    ↓
battlegroup_stats.db (Battlegroup-specific data)
    ↓
Scenario Generator Script
    ↓
Markdown Scenario Files (ready to play)
```

### Data Provenance

Every generated scenario tracks:
- Source TO&E unit (which JSON file)
- Equipment database version (master_database.db timestamp)
- Conversion formulas used (armor/pen/points)
- Historical sources cited (Tessin volume, Army List quarter, etc.)
- Generation timestamp

Example:
```json
{
  "scenario": "Battle of Halfaya Pass",
  "generated_at": "2025-10-19T23:00:00Z",
  "source_data": {
    "german_force": "germany_1941q2_15_panzer_division_toe.json",
    "british_force": "british_1941q2_4_armoured_brigade_toe.json"
  },
  "database_version": "master_database_v1.5.db",
  "conversion_rules": "battlegroup_conversion_v1.0",
  "historical_sources": [
    "Tessin Vol 12 (15. Panzer-Division)",
    "British Army List 1941 Q2"
  ]
}
```

---

## Files Created

### Extraction & Analysis

1. **`scripts/extract_battlegroup_pdf.js`**
   - PDF text extraction using pdf2json
   - Keyword analysis
   - Section identification
   - Auto-install dependencies

2. **`sources/battlegroup_rules_extracted.txt`**
   - Full text (219,289 characters)
   - All 66 pages extracted
   - Searchable with Grep tool

3. **`sources/battlegroup_rules_analysis.json`**
   - Metadata (pages, file size, extraction date)
   - Keyword frequency (mechanics, stats)
   - Section markers

### Documentation

4. **`sources/BATTLEGROUP_SCENARIO_GUIDE.md`** (45KB, comprehensive guide)
   - Game mechanics explained
   - Unit statistics format
   - Scenario structure template
   - Historical TO&E mapping process
   - Conversion formulas (armor, penetration, points)
   - Complete example scenario
   - Database schema proposal
   - Implementation roadmap

5. **`BATTLEGROUP_INTEGRATION_README.md`** (this file)
   - Project overview
   - Completed work summary
   - Next steps
   - Technical integration
   - Commercial product outline

---

## Success Metrics

**Completed (Phase Analysis)**:
- ✅ PDF extraction working (219K characters, 66 pages)
- ✅ Game mechanics documented (Battle Rating system, unit stats, scenarios)
- ✅ Conversion formulas created (armor, pen, points estimation)
- ✅ Example scenario template complete (Halfaya Pass)
- ✅ Database schema designed (battlegroup_stats.db)

**Next Phase (Implementation)**:
- ⏳ Create battlegroup_stats.db database
- ⏳ Import 50+ vehicles/guns from master_database.db
- ⏳ Write scenario generator script
- ⏳ Generate first test scenario (Operation Battleaxe platoon)
- ⏳ Validate points balance (playtest required!)

**Future Phases**:
- ⏸️ Batch generate 54+ scenarios
- ⏸️ Create campaign books (6 operations)
- ⏸️ Develop web-based scenario generator
- ⏸️ Kickstarter campaign for commercial product

---

## Key Insights

### Why This Works

1. **Perfect Data Match**: Our historical TO&E provides exact equipment counts, Battlegroup needs equipment with stats → Master database bridges the gap

2. **Scalability**: One historical unit (e.g., 15th Panzer Division) can generate:
   - 1x Battalion scenario (full division, 1500pts)
   - 3-4x Company scenarios (regimental actions, 1000pts)
   - 8-10x Platoon scenarios (company actions, 500pts)
   - 20+ Squad scenarios (platoon actions, 250pts)
   - **Total: 30-35 scenarios from ONE division's TO&E!**

3. **Historical Accuracy**: Battle Rating system naturally models:
   - German tactical superiority (higher experience levels)
   - Allied numerical/material advantages (more units, easier replacements)
   - Historical outcomes (Germans win tactically, Allies win strategically)

4. **Commercial Viability**:
   - Battlegroup has active player community
   - No official North Africa supplement exists (market gap!)
   - Our database provides unprecedented detail
   - 54+ scenarios = substantial product ($60-80 retail value)

### Challenges & Solutions

**Challenge 1**: No official Battlegroup North Africa supplement
**Solution**: Reverse-engineer from existing supplements + historical data

**Challenge 2**: Points costs estimation without official values
**Solution**: Relative power formula (armor + gun + special rules)

**Challenge 3**: Balance without playtesting
**Solution**: Conservative estimates + designer notes suggesting variations

**Challenge 4**: Scenario variety from limited historical data
**Solution**: Multiple scenario sizes from same TO&E + fictional "what-if" variations

---

## Usage Examples

### Generate Single Scenario

```bash
# From existing TO&E JSON
node scripts/generate_battlegroup_scenario.js \
  --unit germany_1941q2_15_panzer_division_toe.json \
  --opposition british_1941q2_4_armoured_brigade_toe.json \
  --size platoon \
  --battle "Halfaya Pass" \
  --date "1941-06-15" \
  --output scenarios/battleaxe_halfaya_pass.md
```

### Batch Generate Campaign

```bash
# Generate all Operation Battleaxe scenarios
node scripts/generate_battlegroup_campaign.js \
  --operation battleaxe \
  --period 1941q2 \
  --output scenarios/battleaxe/

# Outputs:
# - scenarios/battleaxe/01_halfaya_pass_platoon.md
# - scenarios/battleaxe/02_capuzzo_company.md
# - scenarios/battleaxe/03_hafid_ridge_battalion.md
# - ... (6 scenarios total)
```

### Interactive Scenario Builder

```bash
# Future: Web interface
npm run scenario-builder

# Opens web UI at localhost:3000
# - Select units from database
# - Choose scenario size/type
# - Auto-balance forces
# - Export to PDF/Markdown
```

---

## Contact & Contributions

**Project**: North Africa TO&E Builder
**Integration**: Battlegroup Scenario Generation
**Status**: Phase Analysis Complete, Implementation Pending

**Next Session**: Create battlegroup_stats.db and generator script

---

**End of Document**
