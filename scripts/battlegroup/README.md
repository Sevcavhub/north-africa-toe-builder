# BattleGroup Book Generation System

This directory contains the complete implementation for generating BattleGroup-format wargaming books for North Africa battles.

## Overview

The BattleGroup system converts our historical database (armor mm, penetration values, equipment counts) into game-ready BattleGroup format with:
- Vehicle/gun datacards (armor letters A-O, penetration 1-15, movement inches, HE dice)
- Points costs and Battle Ratings (reverse-engineered from official lists)
- Army lists with historical restrictions
- Complete battle books (OOB, timelines, scenarios)

## Directory Structure

```
scripts/battlegroup/
├── scrapers/           # Extract reference data from existing BattleGroup materials
│   ├── datacard_scraper.py         # Scrape vehicle/gun profiles from PDFs/text
│   └── army_list_analyzer.py       # Analyze official army lists for patterns
├── conversion/         # Convert our database values to BattleGroup format
│   ├── armor_converter.py          # mm thickness → letter (A-O scale)
│   ├── penetration_converter.py    # mm @ distance → value (1-15 scale)
│   ├── movement_calculator.py      # weight/type → inches (off-road/road)
│   └── he_calculator.py            # caliber → dice/target (e.g., "4/4+")
├── points/             # Game balance mechanics (reverse-engineered)
│   ├── points_calculator.py        # Calculate points costs
│   └── battle_rating_assigner.py   # Assign Battle Rating values
├── generators/         # Output file generators
│   ├── datacard_generator.py       # Create vehicle/gun stat cards
│   ├── force_list_compiler.py      # Create army lists with restrictions
│   ├── oob_formatter.py            # Format historical OOB and timelines
│   └── scenario_generator.py       # Generate playable scenarios
├── templates/          # Output templates
│   ├── datacard_vehicle.txt        # Vehicle datacard template
│   ├── datacard_gun.txt            # Gun profile template
│   ├── force_list.txt              # Army list template
│   ├── scenario_briefing.txt       # Scenario template
│   └── appendix_tables.txt         # Appendix reference tables
└── battlegroup_exporter.py         # Main orchestrator script
```

## Implementation Plan

### Step 1: Reference Database (15-20 hours)
**Goal**: Build database of existing BattleGroup stats for comparison

**Input**: BattleGroup datacards from `Resource Documents/Battlegroup Game/`
- Battlegroup-Kursk.txt (9,946 lines analyzed)
- Battlegroup-DataCards-British.txt
- Avanti Italian Forces.txt
- Additional datacard PDFs

**Process**:
1. Scrape all vehicle profiles (armor letters, movement, weapons, points, BR)
2. Scrape all gun profiles (HE/AP values, penetration scale, range bands)
3. Create SQLite tables: `bg_reference_vehicles`, `bg_reference_guns`
4. Map scraped equipment to our master database (fuzzy matching)

**Output**: Reference database with 200+ vehicles, 150+ guns

### Step 2: Conversion Formulas (20-25 hours)
**Goal**: Develop algorithms to convert our data to BattleGroup format

**Modules**:
1. **Armor Converter**: Analyze scraped armor letters vs known mm values
   - Build conversion table (A=180mm+, K=60-69mm, O=20-29mm, etc.)
   - Handle front/side/rear separately
   - 95% accuracy target vs reference data

2. **Penetration Converter**: Map our penetration database to 1-15 scale
   - Analyze 1,296 penetration data points
   - Apply range band degradation (0-10", 10-20", etc.)
   - Cross-validate with scraped gun profiles

3. **Movement Calculator**: Derive movement from vehicle specs
   - Categorize by type (light/medium/heavy tank, wheeled, halftrack)
   - Use weight/power ratio where available
   - Pattern match against scraped reference data

4. **HE Calculator**: Caliber-based HE effectiveness
   - Pattern analysis from scraped gun profiles
   - Create caliber-based lookup (20-37mm → 2/6+, 75-88mm → 4/4+)
   - Handle special cases (howitzers, rockets)

**Validation**: Compare generated values vs 50+ scraped reference vehicles

### Step 3: Points/BR System (15-20 hours)
**Goal**: Reverse engineer game balance mechanics

**Analysis**:
1. Systematic analysis of BattleGroup army lists (Kursk, Torch, etc.)
2. Extract points/BR for 100+ unit types
3. Identify formula components:
   - Base vehicle type (tank: 40, infantry squad: 5)
   - Armor modifier (+5 per armor letter tier)
   - Gun power modifier (+10 for good guns)
   - Special rules bonuses (Elite +5, Unreliable -5)
4. Build points calculator with ±10% tolerance
5. Build BR assigner (pattern-based: medium tank = 5-7 BR)

**Output**: `points_calculator.py`, `battle_rating_assigner.py`

### Step 4: Database Schema (5 hours)
**Goal**: Add BattleGroup-specific tables to master_database.db

**New Tables**:
```sql
-- Reference data (scraped)
CREATE TABLE bg_reference_vehicles (...)
CREATE TABLE bg_reference_guns (...)

-- Lookup tables (conversion)
CREATE TABLE bg_armor_conversion (mm_min, mm_max, letter, description)
CREATE TABLE bg_penetration_scale (mm_1000m, value_1_15, notes)
CREATE TABLE bg_movement_values (vehicle_type, weight_range, off_road, road)
CREATE TABLE bg_he_effectiveness (caliber_range, dice, target_number)
CREATE TABLE bg_special_rules (name, description, effect)

-- Generated stats (per equipment item)
CREATE TABLE equipment_battlegroup (
    equipment_id, armor_front, armor_side, armor_rear,
    off_road_movement, road_movement, points, battle_rating,
    special_rules_json, ammo_capacity, notes
)
```

### Step 5: Generator Tools (20-25 hours)
**Goal**: Build output file generators

**Generators**:
1. **Datacard Generator**: Vehicle/gun stat cards (text format)
   - Read equipment from master database
   - Apply conversions (armor, penetration, movement, HE)
   - Calculate points/BR
   - Format as BattleGroup datacard layout
   - Output: `04_datacards/vehicles/panzer_iii_f.txt`

2. **Force List Compiler**: Army lists with restrictions
   - Pull units from extracted JSONs (Phase 6 data)
   - Filter by quarter (historical availability)
   - Apply force restrictions (minimum infantry %, etc.)
   - Calculate total points/BR
   - Add off-map fire support options
   - Output: `03_army_lists/german_panzer_division.txt`

3. **OOB Formatter**: Historical order of battle
   - Battle timeline (day-by-day events)
   - Unit assignments and attachments
   - Strength reports
   - Output: `01_timeline.md`, `02_oob.md`

4. **Scenario Generator**: Playable scenarios
   - Historical briefing (context, date, location)
   - Force selection (attacker/defender lists)
   - Map setup, terrain, weather
   - Victory conditions and special rules
   - Output: `05_scenarios/scenario_01_meeting_engagement.txt`

### Step 6: Battle Books (15-20 hours)
**Goal**: Generate 12 complete books (one per major battle)

**Battles**:
1. Operation Compass (1940q4-1941q1)
2. Operation Sonnenblume (1941q1)
3. Siege of Tobruk (1941q2)
4. Operation Battleaxe (1941q2)
5. Operation Crusader (1941q4)
6. Gazala (1942q2)
7. First Alamein (1942q3)
8. Alam Halfa (1942q3)
9. Second Alamein (1942q4)
10. Operation Torch (1942q4)
11. Tunisia Campaign (1943q1)
12. Mareth Line (1943q1)

**Book Structure** (per battle):
```
data/output/battlegroup/[battle_name]/
├── 00_introduction.md          # Historical overview
├── 01_timeline.md              # Day-by-day battle events
├── 02_oob.md                   # Complete orders of battle
├── 03_army_lists/              # Force selection
│   ├── german_panzer_division.txt
│   ├── italian_division.txt
│   ├── british_armoured_division.txt
│   └── restrictions.txt
├── 04_datacards/               # Equipment profiles
│   ├── vehicles/               # All vehicle datacards
│   ├── guns/                   # All gun datacards
│   └── aircraft/               # Aircraft support profiles
├── 05_scenarios/               # 7+ playable scenarios
│   ├── scenario_01_meeting_engagement.txt
│   ├── scenario_02_attack_defence.txt
│   └── [...]
├── 06_appendices/              # Reference tables
│   ├── armor_penetration_table.txt
│   ├── special_rules_reference.txt
│   ├── terrain_rules.txt
│   ├── weather_rules.txt
│   └── fire_support_tables.txt
└── battlegroup_[battle_name]_COMPLETE.pdf
```

### Step 7: Validation (10 hours)
**Goal**: Ensure accuracy and playability

**Validation Steps**:
1. Cross-check generated stats vs official BattleGroup books
2. Verify points/BR totals for historical forces
3. Playtest 3-5 scenarios for balance
4. Review with BattleGroup community (if possible)
5. Iterate on balance adjustments

## Data Flow

```
Master Database (master_database.db)
  ├── equipment (469 items with WITW IDs)
  ├── wwiitanks_afv_data (612 vehicles with armor mm)
  ├── wwiitanks_gun_data (343 guns with penetration mm)
  └── penetration_data (1,296 penetration values)
                    ↓
        Conversion Layer (Step 2)
  ├── armor_converter.py (mm → A-O letters)
  ├── penetration_converter.py (mm → 1-15 scale)
  ├── movement_calculator.py (weight → inches)
  └── he_calculator.py (caliber → dice/target)
                    ↓
        Game Balance Layer (Step 3)
  ├── points_calculator.py (calculate cost)
  └── battle_rating_assigner.py (assign BR)
                    ↓
        Generator Layer (Step 5)
  ├── datacard_generator.py
  ├── force_list_compiler.py
  ├── oob_formatter.py
  └── scenario_generator.py
                    ↓
        Output (Step 6)
  12 complete BattleGroup books
  84+ playable scenarios
  469 equipment datacards
```

## Success Criteria

- [ ] Reference database: 200+ vehicles, 150+ guns scraped and mapped
- [ ] Conversion formulas: 95%+ accuracy vs official BattleGroup stats
- [ ] Points calculator: ±10% accuracy vs official army lists
- [ ] All 469 equipment items have BattleGroup stats generated
- [ ] 12 complete battle books (84+ scenarios total)
- [ ] Datacards match official format layout
- [ ] Force lists enforce historical restrictions
- [ ] Scenarios playtested and balanced

## Dependencies

**Phase 9A** (Complete ✅):
- Base scenario generation architecture
- ScenarioExporter base class
- Canonical output paths

**Master Database** (Complete ✅):
- 469 equipment items (WITW baseline)
- 612 AFV specifications (WWIITANKS)
- 343 gun specifications (WWIITANKS)
- 1,296 penetration data points
- 402 ground unit JSONs (Phase 6)
- 23 air summaries (Phase 7)

**Research** (Complete ✅):
- Comprehensive BattleGroup mechanics analysis
- Conversion formula documentation
- Points/BR system patterns identified

## Timeline

Total: **100-125 hours** across 7 steps

Current status: **Step 1 starting** (Datacard scraping)

## Usage

Once complete, generate a BattleGroup book for a battle:

```bash
# Generate complete book for Operation Crusader
python scripts/battlegroup/battlegroup_exporter.py \
  --battle "operation_crusader_1941q4" \
  --output data/output/battlegroup/

# Generate just datacards for German equipment
python scripts/battlegroup/generators/datacard_generator.py \
  --nation german \
  --quarter 1941q4 \
  --output data/output/battlegroup/operation_crusader_1941q4/04_datacards/
```

## Notes

- **Approach**: Hybrid historical accuracy + game balance adjustments
- **Format**: Text-based datacards (PDF generation optional future enhancement)
- **Validation**: All stats cross-checked against official BattleGroup books
- **Commercial Value**: Second major export format (WITW + BattleGroup) for Kickstarter product

## Related Documentation

- `PROJECT_SCOPE.md` - Phase 9B complete specification
- `docs/BATTLEGROUP_RESEARCH_REPORT.md` - Comprehensive game mechanics analysis
- `Resource Documents/Battlegroup Game/` - Source materials for reference database
- `data/output/scenarios/` - WITW scenarios (Phase 9A complete)

---

**Phase 9B Status**: Step 1 starting (October 31, 2025)
**Next Action**: Build datacard scraper to extract reference data
