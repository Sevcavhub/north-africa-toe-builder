# Phase 9B: BattleGroup Books - Next Steps

**Date**: November 4, 2025
**Status**: ✅ BG Reference Data Repopulation IN PROGRESS - British DataCards OCR/CSV COMPLETE  
**Last Update**: ✅ British DataCards: OCR + CSV templates created (77 vehicles, 15 guns, 6 aircraft) - AWAITING USER DATA ENTRY
**Database Status**: Canada's Crucible 100% | British DataCards templates ready | CSV import pending  
**Current Task**: User fills British DataCards CSVs → Import to DB → Continue remaining DataCards

---

## 🎉 CANADA'S CRUCIBLE EXTRACTION 100% COMPLETE (November 4, 2025)

### ✅ COMPLETED: Full Manual Extraction via Screenshots

**What Was Accomplished**:
- ✅ **41 Python extraction scripts** - Systematic data entry from screenshots
- ✅ **German forces** - 63 vehicles, 16 guns, 2 aircraft, 58 army list units, 9 defences
- ✅ **Canadian forces** - 21 vehicles, 10 guns, 3 aircraft, 47 army list units, 13 defences
- ✅ **4 complete scenarios** - Black Sabbath, Norrey, Surrounded (hierarchical force structures)
- ✅ **3 sample maps** - Scenario battlefield layouts

**Database Tables Populated**:
- `bg_reference_vehicles` (84 vehicles with stats, armor, weapons, movement)
- `bg_reference_guns` (26 guns with HE/AP values, penetration)
- `bg_reference_aircraft` (5 aircraft with role, hits, weaponry)
- `BG_Reference_ArmyList_Examples` (105 units with points, BR, composition)
- `BG_Reference_Defences` (22 defensive structures)
- `BG_Scenario_Army_Lists` (4 scenarios)
- `BG_Scenario_Forces` (8 forces total)
- `BG_Scenario_Units` (54 units with deployment details)
- `BG_Sample_maps` (4 maps)

**Git Commit**: `0aae6c62` - feat(manual-extraction): Complete Canada's Crucible

---

## 🔄 BRITISH DATACARDS EXTRACTION IN PROGRESS (November 4, 2025)

### ✅ OCR + CSV Template Generation COMPLETE

**Approach**: OCR extraction (600 DPI) → CSV templates → User manual entry → Import script

**What Was Accomplished**:
- ✅ **OCR Processing**: All 8 pages of British DataCards PDF processed
- ✅ **CSV Templates Created**: 3 files with 98 total items
  - `british_datacards_ALL_VEHICLES.csv` - 77 vehicles (pages 1-8)
  - `british_datacards_ALL_GUNS.csv` - 15 unique guns (deduplicated)
  - `british_datacards_ALL_AIRCRAFT.csv` - 6 aircraft (page 7)
- ✅ **OCR Reference Files**: 8 text files (`british_datacard_page1-8_OCR.txt`)
- ✅ **Extraction Script**: `create_all_british_csv_templates.py`

**Git Commit**: `c37e672e` - feat(phase9b): British DataCards extraction infrastructure

**Current Status**: ⏳ **AWAITING USER DATA ENTRY**

User needs to fill blank CSV fields using PDF or OCR text as reference:
- **Vehicles**: vehicle_type, off_road_inches, road_inches, armor_front/side/rear, weapons, points_cost, battle_rating, special_rules
- **Guns**: he_dice, he_target (format: "10D8"), AP penetration at 6 range bands (ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70)
- **Aircraft**: cannon_count, cannon_caliber, rockets, bombs, machine_guns, special_notes

**Next Steps**:
1. ⏳ User completes CSV data entry
2. Create import script: `import_british_datacards_from_csv.py`
3. Load to database:
   - `bg_reference_vehicles` (+77 vehicles)
   - `bg_reference_guns` (+15 guns)  
   - `bg_reference_aircraft` (+6 aircraft)
4. Create `bg_reference_small_arms` table for Page 8 "Small Arms Rate of Fire" data
5. Continue with remaining DataCards: Early-German, French-Polish-Romanian-Hungarian, Soviets, US

**OCR Lessons Learned**:
- 600 DPI OCR successfully extracts vehicle names and basic structure
- Small numeric values (penetration tables) too difficult for OCR alone
- Hybrid approach (OCR structure + manual data entry) balances speed vs accuracy
- CSV templates provide clear, systematic structure for completion

---

## 📋 REMAINING: DataCards Supplements (4 more)

**Location**: `D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Equipment Screen Captures`

**DataCards To Process**:
1. ✅ **Battlegroup-DataCards-British** (8 pages) - OCR/CSV templates complete, awaiting data entry
2. ⏳ Battlegroup-DataCards-Early-German
3. ⏳ Battlegroup-DataCards-French-Polish-Romanian-Hungarian
4. ⏳ Battlegroup-DataCards-Soviets
5. ⏳ Battlegroup-DataCards-US

**Important Notes**:
- DataCards are QRS (Quick Reference Sheet) cards, NOT full equipment lists
- Format: Top table = vehicle stats, bottom section = integrated gun stats (if vehicle has gun)
- Includes: Armored vehicles, soft-skin vehicles, aircraft cards
- NO army lists, NO maps, NO scenarios in DataCards

---

## 📋 FULL SUPPLEMENTS (After DataCards)

**Full Supplements** (Army Lists, Maps, Vehicles, Guns, Aircraft, Scenarios):
1. Battlegroup-Dispatches-1
2. Battlegroup-Dispatches-2
3. BG-Dispatches-3
4. Battlegroup-Fall-of-the-Reich-Full
5. Battlegroup-Kursk
6. Battlegroup-Market-Garden-Army-List
7. Battlegroup-Market-Garden-Scenarios
8. Battlegroup-Overlord-Army-Lists
9. Battlegroup-Overlord-D-Day-scenarios
10. Battlegroup-Torch-Mission
11. Battlegroup-Wacht-Am-Rhein
12. Battlegroup-Westwall
13. BG Army lists (PDF) v5

**Total Remaining**: 4 DataCards + 13 Full Supplements = 17 extraction tasks

---

## 📊 DATABASE STATUS

**Tables with Data**:
- ✅ `bg_reference_vehicles` - 84 items (Canada's Crucible)
- ✅ `bg_reference_guns` - 26 items (Canada's Crucible)
- ✅ `bg_reference_aircraft` - 5 items (Canada's Crucible)
- ✅ `BG_Reference_ArmyList_Examples` - 105 units
- ✅ `BG_Reference_Defences` - 22 defences
- ✅ `BG_Scenario_Army_Lists` - 4 scenarios
- ✅ `BG_Scenario_Forces` - 8 forces
- ✅ `BG_Scenario_Units` - 54 units
- ✅ `BG_Sample_maps` - 4 maps

**Pending Import** (British DataCards CSVs):
- ⏳ `bg_reference_vehicles` - +77 vehicles
- ⏳ `bg_reference_guns` - +15 guns
- ⏳ `bg_reference_aircraft` - +6 aircraft

**To Be Created**:
- ⏳ `bg_reference_small_arms` - Small Arms Rate of Fire table (British DataCards Page 8)

---

## 🛠️ HANDOFF INSTRUCTIONS FOR NEXT SESSION

**Current State**:
1. Canada's Crucible extraction: ✅ 100% COMPLETE in database
2. British DataCards: ✅ OCR/CSV templates ready → ⏳ User filling data
3. Database location: `D:/north-africa-toe-builder/database/master_database.db`

**CSV Files Ready for User**:
- `D:/north-africa-toe-builder/british_datacards_ALL_VEHICLES.csv` (77 rows)
- `D:/north-africa-toe-builder/british_datacards_ALL_GUNS.csv` (15 rows)
- `D:/north-africa-toe-builder/british_datacards_ALL_AIRCRAFT.csv` (6 rows)

**When User Completes CSVs**:
1. Create import script matching Canada's Crucible pattern
2. Read CSVs and insert to database with proper field mapping
3. Handle UNIQUE constraints (skip duplicates, report new items)
4. Verify with COUNT queries
5. Commit to git: "feat(phase9b): Import British DataCards from user-completed CSVs"

**Next DataCards Supplement**:
- After British import complete, start: Battlegroup-DataCards-Early-German
- Use same OCR + CSV template approach
- Location: `Resource Documents/Battlegroup Game/Suppliment Equipment Screen Captures`

**Reference Documents**:
- Canada's Crucible extraction scripts: `scripts/battlegroup/manual_extraction/canada_*.py`
- Database schema: Check table definitions with `PRAGMA table_info(table_name)`
- OCR script: `create_all_british_csv_templates.py`
