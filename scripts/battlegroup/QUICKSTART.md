# BattleGroup Generator Toolkit - Quickstart Guide

**Goal**: Generate your first BattleGroup scenario in 10 minutes

**Prerequisites**:
- Database populated (Phase 1-4 complete)
- Python 3.8+
- Working directory: `D:\north-africa-toe-builder`

---

## 🚀 Quick Demo (5 minutes)

### 1. Generate Equipment Datacard (30 seconds)

```bash
# Generate M4 Sherman datacard
python scripts/battlegroup/generators/datacard_generator.py \
  --equipment "M4 Sherman" \
  --print
```

**Expected Output**:
```
==================================================
M4 SHERMAN
==================================================
Type: Vehicle
Nation: American
Experience: Regular

ARMOR:                 MOVEMENT:
  Front:    K            Off-Road: 9"
  Side:     L            Road:     14"
  Rear:     N
  Turret:   N/A

POINTS: 50
BATTLE RATING: 3-r
==================================================
```

---

### 2. Generate Random Scenario (1 minute)

```bash
# Generate desert patrol clash scenario
python scripts/battlegroup/generators/random_scenario_generator.py \
  --scenario desert_patrol_clash \
  --year 1942 \
  --size company \
  --points-attacker 750 \
  --points-defender 750 \
  --output data/output/scenarios/
```

**Output**: 2-page scenario in `data/output/scenarios/desert_patrol_clash_*.md`

---

### 3. Generate Book Structure (2 minutes)

```bash
# Generate Operation Battleaxe book structure (MDBook format)
python scripts/battlegroup/generators/book_structure_generator.py \
  --battle "battleaxe" \
  --operation "Operation Battleaxe" \
  --dates "June 15-17, 1941" \
  --quarter "1941q2" \
  --attacker "british" \
  --defender "german" \
  --scenarios 8 \
  --format mdbook \
  --output data/output/books/
```

**Output**: Complete book structure in `data/output/books/battleaxe/`

---

### 4. Build the Book (1 minute)

```bash
cd data/output/books/battleaxe
mdbook build
```

**Output**: HTML website in `book/` directory

**View**: Open `book/index.html` in browser

---

## 📚 Common Use Cases

### Use Case 1: Generate Datacards for All German Equipment

```bash
python scripts/battlegroup/generators/datacard_generator.py \
  --nation german \
  --output data/output/battlegroup/datacards/german/
```

**Result**: ~98 German equipment datacards

---

### Use Case 2: Generate Army List for 1941q2 British Forces

```bash
python scripts/battlegroup/generators/army_list_generator.py \
  --nation british \
  --quarter 1941q2 \
  --print
```

**Result**: Complete British army list with equipment organized by category

---

### Use Case 3: Build Force Roster (Interactive)

```bash
python scripts/battlegroup/generators/force_roster_builder_v2.py \
  --interactive
```

**Steps**:
1. Select nation (e.g., german)
2. Select battle (e.g., kursk)
3. Set points budget (e.g., 1000)
4. Add units interactively
5. Validate composition (HQ requirement, support limit, rarity)
6. Export as JSON or text

---

### Use Case 4: Generate All 12 Random Scenario Types

```bash
# Desert Patrol Clash
python scripts/battlegroup/generators/random_scenario_generator.py \
  --scenario desert_patrol_clash --year 1942 --size company --points-attacker 750 --points-defender 750 \
  --output data/output/scenarios/

# Oasis Counter-Attack
python scripts/battlegroup/generators/random_scenario_generator.py \
  --scenario oasis_counter_attack --year 1942 --size company --points-attacker 800 --points-defender 750 \
  --output data/output/scenarios/

# ... (10 more scenario types available)
```

**Available scenario types**:
- desert_patrol_clash
- oasis_counter_attack
- desert_flanking_maneuver
- wadi_crossing
- escarpment_defense
- pass_assault
- supply_convoy_ambush
- airfield_assault
- fortified_box_defense
- coastal_road_defense
- desert_breakthrough
- rearguard_action

---

## 🛠️ Tool Reference

### Datacard Generator

**Purpose**: Generate BattleGroup-formatted equipment datacards

**Options**:
- `--equipment "Name"`: Single equipment item
- `--nation german|british|american|italian`: All equipment for nation
- `--type vehicle|gun|defence|fire_support`: Filter by type
- `--experience regular|veteran|inexperienced|elite`: Experience level
- `--print`: Print to console
- `--output path/`: Save to directory

**Examples**:
```bash
# Single vehicle (veteran)
python scripts/battlegroup/generators/datacard_generator.py \
  --equipment "Tiger I" --experience veteran --print

# All American equipment
python scripts/battlegroup/generators/datacard_generator.py \
  --nation american --output datacards/american/

# All guns
python scripts/battlegroup/generators/datacard_generator.py \
  --type gun --output datacards/guns/
```

---

### Force Roster Builder

**Purpose**: Build force rosters with composition validation

**Options**:
- `--interactive`: Interactive mode (recommended for beginners)
- `--nation german|british|american|italian`: Force nation
- `--battle battlename`: Battle context
- `--points N`: Points budget
- `--load file.json`: Load existing roster
- `--validate`: Validate only (with --load)

**Examples**:
```bash
# Interactive mode (easiest)
python scripts/battlegroup/generators/force_roster_builder_v2.py --interactive

# Programmatic mode
python scripts/battlegroup/generators/force_roster_builder_v2.py \
  --nation german --battle kursk --points 1000

# Load and validate existing roster
python scripts/battlegroup/generators/force_roster_builder_v2.py \
  --load my_roster.json --validate
```

---

### Random Scenario Generator

**Purpose**: Generate random scenarios with North Africa terrain

**Options**:
- `--scenario TYPE`: Scenario template (12 types available)
- `--year 1940|1941|1942|1943`: Campaign year
- `--size platoon|company|battalion`: Battle size
- `--points-attacker N`: Attacker points budget
- `--points-defender N`: Defender points budget
- `--output path/`: Output directory

**Examples**:
```bash
# Company-level desert patrol clash (1942)
python scripts/battlegroup/generators/random_scenario_generator.py \
  --scenario desert_patrol_clash \
  --year 1942 \
  --size company \
  --points-attacker 750 \
  --points-defender 750 \
  --output data/output/scenarios/

# Battalion-level oasis attack (1943)
python scripts/battlegroup/generators/random_scenario_generator.py \
  --scenario oasis_counter_attack \
  --year 1943 \
  --size battalion \
  --points-attacker 1200 \
  --points-defender 1000 \
  --output data/output/scenarios/
```

---

### Book Structure Generator

**Purpose**: Generate complete book structures (MDBook or LaTeX)

**Options**:
- `--battle battlename`: Battle identifier (required)
- `--operation "Full Name"`: Operation name (required)
- `--dates "Date Range"`: Battle dates (required)
- `--quarter YYYYQN`: Quarter (e.g., 1941q2) (required)
- `--attacker nation`: Attacking nation (required)
- `--defender nation`: Defending nation (required)
- `--scenarios N`: Number of scenarios (required)
- `--format mdbook|latex|all`: Output format (required)
- `--output path/`: Output directory (required)
- `--location "Place"`: Battle location (optional)

**Examples**:
```bash
# MDBook format
python scripts/battlegroup/generators/book_structure_generator.py \
  --battle "battleaxe" \
  --operation "Operation Battleaxe" \
  --dates "June 15-17, 1941" \
  --quarter "1941q2" \
  --location "Halfaya Pass, Libya-Egypt Border" \
  --attacker "british" \
  --defender "german" \
  --scenarios 8 \
  --format mdbook \
  --output data/output/books/

# LaTeX format (print-ready PDF)
python scripts/battlegroup/generators/book_structure_generator.py \
  --battle "crusader" \
  --operation "Operation Crusader" \
  --dates "November 18 - December 30, 1941" \
  --quarter "1941q4" \
  --attacker "british" \
  --defender "german" \
  --scenarios 12 \
  --format latex \
  --output data/output/books/

# Both formats
python scripts/battlegroup/generators/book_structure_generator.py \
  --battle "gazala" \
  --operation "Battle of Gazala" \
  --dates "May 26 - June 21, 1942" \
  --quarter "1942q2" \
  --attacker "german" \
  --defender "british" \
  --scenarios 15 \
  --format all \
  --output data/output/books/
```

**After generation**:
```bash
# Build MDBook (HTML website)
cd data/output/books/battleaxe
mdbook build
# Open book/index.html in browser

# Build LaTeX (PDF)
cd data/output/books/
pdflatex battleaxe.tex
# Creates battleaxe.pdf
```

---

### Army List Generator

**Purpose**: Generate historically accurate army lists with Phase 6 integration

**Options**:
- `--nation german|british|american|italian`: Nation (required)
- `--quarter YYYYQN`: Quarter (e.g., 1941q2) (required)
- `--battle battlename`: Battle context (optional)
- `--print`: Print to console
- `--output path/`: Save to directory

**Examples**:
```bash
# British 1941q2 army list
python scripts/battlegroup/generators/army_list_generator.py \
  --nation british \
  --quarter 1941q2 \
  --print

# German 1942q4 army list (save to file)
python scripts/battlegroup/generators/army_list_generator.py \
  --nation german \
  --quarter 1942q4 \
  --output data/output/battlegroup/army_lists/

# American 1942q4 army list for specific battle
python scripts/battlegroup/generators/army_list_generator.py \
  --nation american \
  --quarter 1942q4 \
  --battle torch \
  --print
```

---

### Validation Suite

**Purpose**: Validate all Step 5 components

**Options**: None (runs all tests automatically)

**Examples**:
```bash
# Run comprehensive validation
python scripts/battlegroup/validation/step5_validation_suite.py

# Run quick validation (imports only)
python scripts/battlegroup/validation/quick_validation.py
```

**Expected Output**:
```
✅ Part 1: Datacard Generator - PASS
✅ Part 2: Special Rules Database - PASS (57 rules, 1,599 linkages)
✅ Part 3: Force Roster Builder - PASS
✅ Part 4A: Random Scenario Generator - PASS
✅ Part 4B: Historical Scenario Generator - PASS
✅ Part 5: Book Structure Generator - PASS
✅ Part 6: Army List Generator - PASS
✅ Part 6: Phase6UnitParser - PASS (402 units found)

OVERALL STATUS: [PASS] - All validations successful!
```

---

## 🎯 Quick Workflow: Generate Your First Book

**Time**: ~15 minutes

### Step 1: Generate Book Structure (2 min)

```bash
python scripts/battlegroup/generators/book_structure_generator.py \
  --battle "battleaxe" \
  --operation "Operation Battleaxe" \
  --dates "June 15-17, 1941" \
  --quarter "1941q2" \
  --attacker "british" \
  --defender "german" \
  --scenarios 8 \
  --format mdbook \
  --output data/output/books/
```

### Step 2: Generate Datacards (3 min)

```bash
# British datacards
python scripts/battlegroup/generators/datacard_generator.py \
  --nation british \
  --output data/output/books/battleaxe/src/chapter2/

# German datacards
python scripts/battlegroup/generators/datacard_generator.py \
  --nation german \
  --output data/output/books/battleaxe/src/chapter2/
```

### Step 3: Generate Army Lists (2 min)

```bash
# British 1941q2 army list
python scripts/battlegroup/generators/army_list_generator.py \
  --nation british \
  --quarter 1941q2 \
  --output data/output/books/battleaxe/src/

# German 1941q2 army list
python scripts/battlegroup/generators/army_list_generator.py \
  --nation german \
  --quarter 1941q2 \
  --output data/output/books/battleaxe/src/
```

### Step 4: Generate Scenarios (5 min)

```bash
# Generate 3 random scenarios for testing
python scripts/battlegroup/generators/random_scenario_generator.py \
  --scenario pass_assault \
  --year 1941 \
  --size company \
  --points-attacker 750 \
  --points-defender 750 \
  --output data/output/books/battleaxe/src/scenarios/

python scripts/battlegroup/generators/random_scenario_generator.py \
  --scenario desert_patrol_clash \
  --year 1941 \
  --size platoon \
  --points-attacker 500 \
  --points-defender 500 \
  --output data/output/books/battleaxe/src/scenarios/

python scripts/battlegroup/generators/random_scenario_generator.py \
  --scenario escarpment_defense \
  --year 1941 \
  --size company \
  --points-attacker 800 \
  --points-defender 700 \
  --output data/output/books/battleaxe/src/scenarios/
```

### Step 5: Build the Book (1 min)

```bash
cd data/output/books/battleaxe
mdbook build
```

### Step 6: View Your Book (1 min)

Open `data/output/books/battleaxe/book/index.html` in your browser

**You now have a complete BattleGroup battle book!** 🎉

---

## 📖 Nation Values (CANONICAL)

**IMPORTANT**: Always use these exact nation values:

- `german` - German Wehrmacht
- `italian` - Italian Regio Esercito
- `british` - British & Commonwealth (includes Australia, NZ, India, South Africa, Canada)
- `american` - US Army
- `french` - Free French forces

**NOT**: "germany", "britain", "usa", "uk", etc.

---

## 📅 Quarter Format (CANONICAL)

**Format**: `YYYYqN` (lowercase 'q', no hyphen)

**Examples**:
- ✅ `1941q2` (correct)
- ❌ `1941-Q2` (wrong - hyphen, uppercase)
- ❌ `1941Q2` (wrong - uppercase)

**Valid quarters**: `1940q4`, `1941q1`, `1941q2`, `1941q3`, `1941q4`, `1942q1`, `1942q2`, `1942q3`, `1942q4`, `1943q1`, `1943q2`

---

## 🐛 Common Issues

### Issue 1: "Equipment not found"

**Problem**: Equipment name doesn't match database
**Solution**: Check exact spelling with:
```bash
sqlite3 database/master_database.db "SELECT name FROM equipment WHERE name LIKE '%Sherman%';"
```

### Issue 2: "No witw_id field" for Phase 6 units

**Problem**: Older unit JSONs lack witw_id enrichment
**Solution**: Run enrichment:
```bash
python scripts/enrich_units_with_database.py
```

### Issue 3: "mdbook: command not found"

**Problem**: MDBook not installed
**Solution**: Install MDBook:
```bash
cargo install mdbook
# OR download from https://github.com/rust-lang/mdBook/releases
```

### Issue 4: Unicode errors on Windows console

**Problem**: Special characters in equipment names
**Solution**: The generators use `safe_print()` to handle this automatically. If you still see errors, redirect output to file:
```bash
python datacard_generator.py --equipment "M4 Sherman" --print > output.txt
```

---

## 📚 Next Steps

### Learn More:
- **Comprehensive Guide**: See `PHASE_9B_STEP5_SUMMARY.md` for detailed documentation
- **Integration Workflows**: See "Integration Guide" section in summary
- **Project Scope**: See `PROJECT_SCOPE.md` for overall vision

### Create Content:
1. **Generate more scenarios**: Use all 12 scenario templates
2. **Create historical scenarios**: Use `historical_scenario_generator.py` framework
3. **Build more books**: Operation Crusader, Gazala, First Alamein
4. **Customize books**: Edit generated markdown files

### Get Help:
- Check `CLAUDE.md` for project instructions
- Review `START_HERE_NEW_SESSION.md` for workflow guidance
- Validate your work: `python scripts/battlegroup/validation/step5_validation_suite.py`

---

**Ready to create BattleGroup scenarios? Start with the Quick Demo above!** 🚀
