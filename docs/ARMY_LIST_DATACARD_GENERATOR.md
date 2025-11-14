# Army List Datacard Generator

**Created**: November 14, 2025
**Purpose**: Generate BattleGroup V5.5 datacards from army lists (OSJones Builder format or plain text)

---

## Overview

This tool generates datacards for equipment found in army lists, using our **bg_builder_vehicles** (602 vehicles) and **bg_builder_weapons** (239 weapons) tables. Perfect for:

1. **Creating datacards from OSJones Builder armies** - Use the equipment from any force you build
2. **Scenario-specific datacards** - Generate cards only for units in a specific scenario
3. **Quick reference sheets** - Make datacards for commonly-used equipment

---

## Usage

### Method 1: From Text File

Create a text file with equipment names (one per line):

```
Panzer III Ausf F
Panzer IV Ausf D
Matilda II
Crusader I
88mm FlaK 36
```

Then run:
```bash
python scripts/battlegroup/book/generate_datacards_from_army_list.py \
  --input my_army.txt \
  --output datacards/
```

### Method 2: From Command Line

```bash
python scripts/battlegroup/book/generate_datacards_from_army_list.py \
  --equipment "Panzer III Ausf F,Panzer IV Ausf D,Matilda II" \
  --output datacards/
```

### Method 3: From OSJones Builder (Manual Extraction)

Since OSJones Builder doesn't have a direct export:

1. Go to https://osjones.github.io/BattlegroupBuilder/
2. Build your army
3. Manually copy equipment names to a text file
4. Run the generator with `--input`

---

## Equipment Name Matching

The tool uses **fuzzy matching** to find equipment in the database:

### Exact Matches (Best)
- `Panzer III Ausf F` → finds `Panzer III Ausf F`
- `Matilda II` → finds `Matilda II`
- `Crusader I` → finds `Crusader I`

### Fuzzy Matches (Good)
- `Panzer III` → finds `Panzer III Ausf F` (first alphabetical match)
- `Sherman` → finds `M4 Sherman (A1,A2,A3)` (first match)
- `88mm` → finds `8.8cm FlaK 36` (German notation)

### Not Found
- Equipment not in bg_builder tables will be skipped
- Check spelling/variant names if equipment isn't found

---

## Database Tables Used

**bg_builder_vehicles** (602 vehicles)
- Complete vehicle data from OSJones Builder
- Includes: armor, movement, weapons, special rules
- Columns: `id`, `name`, `movement_off_road`, `movement_road`, `armor_front/side/rear`, `weapon_1_id` through `weapon_5_id`

**bg_builder_weapons** (239 weapons)
- Weapon specifications for vehicles and towed guns
- Includes: HE effects, AP penetration at ranges
- Columns: `weapon_id`, `weapon_name`, `he_type`, `he_effect`, `ap_strength_0` through `ap_strength_70`

**bg_builder_vehicle_costs** (703 entries)
- Points costs and BR values by force/experience
- Columns: `vehicle_id`, `force_name`, `cost_regular/veteran/elite`, `br_regular/veteran/elite`

---

## Output Format

Generates **V5.5 format datacards** organized by category:

```
output_directory/
├── tanks.md                    # AFVs, tanks
├── guns_and_artillery.md       # Towed guns, artillery
├── vehicles.md                 # Transports, trucks
└── other_equipment.md          # Misc equipment
```

Each markdown file includes:
- **V5.5 CSS styling** (nation-specific colors)
- **3-column grid layout** (3 datacards per row)
- **Complete datacard data**:
  - Armor values (front/side/rear)
  - Armament table (weapon, HE, AP, HE Range)
  - Movement (off-road, road)
  - Special rules
  - Points cost and BR (if available)

---

## Examples

### Example 1: North Africa DAK Force

**Input** (`dak_force.txt`):
```
Panzer III Ausf G
Panzer III Ausf H
Panzer IV Ausf D
Panzer IV Ausf F1
SdKfz 231 (8-rad)
SdKfz 222
50mm PaK 38
88mm FlaK 36
```

**Command**:
```bash
python scripts/battlegroup/book/generate_datacards_from_army_list.py \
  --input dak_force.txt \
  --output books/tobruk/player_aids/
```

**Output**:
- `books/tobruk/player_aids/tanks.md` - Panzer III/IV datacards
- `books/tobruk/player_aids/guns_and_artillery.md` - PaK 38, FlaK 36
- `books/tobruk/player_aids/vehicles.md` - SdKfz vehicles

### Example 2: British Armoured Division

**Input** (`british_armor.txt`):
```
Crusader I
Crusader II
Crusader III
Matilda II
Valentine II
Grant
Stuart
25-pdr
6-pdr
2-pdr
```

**Command**:
```bash
python scripts/battlegroup/book/generate_datacards_from_army_list.py \
  --input british_armor.txt \
  --output books/crusader/player_aids/
```

### Example 3: Quick Test

**Command**:
```bash
python scripts/battlegroup/book/generate_datacards_from_army_list.py \
  --equipment "Panzer III,Matilda II,Sherman" \
  --output test/
```

---

## Supported Input Formats

The parser recognizes multiple formats:

```
# Plain names (recommended)
Panzer III Ausf F
Matilda II

# With quantities (quantity ignored for datacards)
3x Panzer III Ausf F
2x Matilda II

# Scenario format (parses equipment name only)
- 3x Panzer III Ausf F (veteran) - 150 pts, BR: 2

# Comma-separated (splits on commas)
Panzer III, Matilda II, Crusader I

# Mixed formats (all parsed correctly)
3x Panzer III
Matilda II (veteran)
- 2x Crusader I - 120 pts
```

---

## Troubleshooting

### Equipment Not Found

**Problem**: `[X] Not found in database`

**Solutions**:
1. Check exact name in database:
   ```bash
   python -c "
   import sqlite3
   conn = sqlite3.connect('database/master_database.db')
   cursor = conn.cursor()
   cursor.execute('SELECT name FROM bg_builder_vehicles WHERE name LIKE \"%Sherman%\"')
   for row in cursor.fetchall():
       print(row[0])
   "
   ```

2. Try fuzzy name: `Sherman` instead of `M4 Sherman (A1,A2,A3)`

3. Check bg_builder_weapons table for towed guns:
   ```bash
   python -c "
   import sqlite3
   conn = sqlite3.connect('database/master_database.db')
   cursor = conn.cursor()
   cursor.execute('SELECT weapon_name FROM bg_builder_weapons WHERE weapon_name LIKE \"%88%\"')
   for row in cursor.fetchall():
       print(row[0])
   "
   ```

### Parsing Issues

**Problem**: Equipment names split incorrectly (e.g., parentheses in names)

**Solutions**:
- Use exact names from database (check with SQL above)
- Avoid comma-separated format for complex names
- Use one equipment per line in text file

### Missing Weapon Data

**Problem**: Datacard shows `-` for weapons

**Cause**: Vehicle in bg_builder_vehicles but weapon_1_id through weapon_5_id not linked

**Solutions**:
- Check weapon linkage in database
- Some vehicles may not have weapons (transports, trucks)

### Nation Color Wrong

**Problem**: Datacard uses wrong nation colors

**Cause**: Name-based nation inference (checks for keywords like "Panzer", "Matilda", "Sherman")

**Solutions**:
- Script infers nation from name patterns
- Italian vehicles may be misclassified if name doesn't have Italian keywords
- Check `infer_nation_from_name()` function for keyword list

---

## Advanced: Generating Army Lists for Scenarios

**Coming Soon**: Reverse process to generate OSJones Builder-style army lists from our scenario markdown files.

**Planned Features**:
1. Parse scenario `## FORCES` sections
2. Look up equipment in bg_builder tables
3. Calculate points costs and BR
4. Generate formatted army list HTML/PDF
5. Export to OSJones Builder format (if API available)

**Script Location**: `scripts/battlegroup/book/generate_army_lists_from_scenarios.py` (to be created)

---

## Database Schema Reference

### bg_builder_vehicles
```sql
CREATE TABLE bg_builder_vehicles (
    id INTEGER PRIMARY KEY,
    name TEXT,
    movement_off_road TEXT,      -- e.g., "10"
    movement_road TEXT,           -- e.g., "18"
    armor_front TEXT,             -- e.g., "E" (BG letter scale)
    armor_side TEXT,              -- e.g., "C"
    armor_rear TEXT,              -- e.g., "B"
    weapon_1_id INTEGER,          -- FK to bg_builder_weapons
    weapon_2_id INTEGER,
    weapon_3_id INTEGER,
    weapon_4_id INTEGER,
    weapon_5_id INTEGER,
    special_rules TEXT,           -- Comma-separated special rules
    nation TEXT,
    -- ... other columns
);
```

### bg_builder_weapons
```sql
CREATE TABLE bg_builder_weapons (
    weapon_id INTEGER PRIMARY KEY,
    weapon_name TEXT,             -- e.g., "7.5cm KwK 40"
    he_type TEXT,                 -- e.g., "HE"
    he_effect TEXT,               -- e.g., "6D6"
    he_strength_0 INTEGER,        -- HE strength at 0-10"
    he_strength_10 INTEGER,       -- HE strength at 10-20"
    he_strength_20 INTEGER,       -- HE strength at 20-30"
    he_strength_30 INTEGER,       -- HE strength at 30-40"
    he_strength_40 INTEGER,       -- HE strength at 40-50"
    he_strength_50 INTEGER,       -- HE strength at 50-70"
    ap_strength_0 INTEGER,        -- AP penetration at 0"
    ap_strength_10 INTEGER,       -- AP penetration at 10"
    ap_strength_20 INTEGER,       -- AP penetration at 20"
    ap_strength_30 INTEGER,       -- AP penetration at 30"
    ap_strength_40 INTEGER,       -- AP penetration at 40"
    ap_strength_50 INTEGER,       -- AP penetration at 50"
    ap_strength_70 INTEGER,       -- AP penetration at 70"
    -- ... other columns
);
```

### bg_builder_vehicle_costs
```sql
CREATE TABLE bg_builder_vehicle_costs (
    id INTEGER PRIMARY KEY,
    vehicle_id INTEGER,           -- FK to bg_builder_vehicles
    vehicle_name TEXT,
    force_name TEXT,              -- e.g., "Tobruk_A5_Deutsches_Afrikakorps"
    cost_regular INTEGER,         -- Points cost for regular crew
    cost_veteran INTEGER,         -- Points cost for veteran crew
    cost_elite INTEGER,           -- Points cost for elite crew
    br_regular INTEGER,           -- Battle rating for regular
    br_veteran INTEGER,           -- Battle rating for veteran
    br_elite INTEGER,             -- Battle rating for elite
    -- ... other columns
);
```

---

## Future Enhancements

### Phase 1: Equipment Lookup Improvements
- [ ] Better fuzzy matching algorithm (Levenshtein distance)
- [ ] Variant consolidation (Panzer III → all Ausf variants)
- [ ] Nation-specific search (restrict by nation)
- [ ] Equipment aliases table (common names → official names)

### Phase 2: OSJones Builder Integration
- [ ] Parse saved army JSON (if export feature added)
- [ ] Direct HTML parsing from print view
- [ ] Browser extension to extract army data

### Phase 3: Army List Generation
- [ ] Generate OSJones-style army lists from scenarios
- [ ] Calculate points/BR totals
- [ ] Format for print (PDF/HTML)
- [ ] Validate force composition (HQ, units, supports)

### Phase 4: Web Integration
- [ ] Add to Render.com API as endpoint
- [ ] Frontend form: paste equipment list → generate datacards
- [ ] Download as PDF option
- [ ] Share/save army lists feature

---

## Related Tools

- `generate_book_datacards_v5_5.py` - Generate datacards from database (all equipment in quarter)
- `generate_book_datacards_from_scenarios.py` - Generate datacards from scenario markdown files
- `generate_datacards_from_army_list.py` - **This tool** - Generate from army lists

**Comparison**:

| Tool | Input | Use Case |
|------|-------|----------|
| v5_5 | Quarter (1942q2) | Generate ALL equipment for a battle/quarter |
| from_scenarios | Scenario markdown | Generate ONLY equipment in scenarios |
| from_army_list | Text list | Generate for CUSTOM army/force list |

---

## Contact & Support

**Issues**: Report bugs/feature requests in project documentation
**Database**: `database/master_database.db` (602 vehicles, 239 weapons)
**Documentation**: This file + inline script help (`--help`)

**Last Updated**: November 14, 2025
