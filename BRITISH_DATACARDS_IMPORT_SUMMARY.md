# British DataCards Import Summary

**Date**: November 5, 2025
**Status**: ✅ VEHICLES COMPLETE (90/90 imported)
**Database**: `database/master_database.db`
**Table**: `bg_reference_vehicles`

---

## 📊 Import Results

### Vehicles Imported

**Total CSV rows processed**: 90
**Duplicates updated**: 10 (Canadian + British multi-nation vehicles)
**New vehicles inserted**: 80 (British-only vehicles)
**Skipped**: 0

**Final database totals**:
- British-only: 80 vehicles
- German: 41 vehicles
- Canadian-only: 13 vehicles
- Multi-Nation (Canadian, British): 10 vehicles
- **Total vehicles**: 144

---

## 🔄 Multi-Nation Vehicles (Canadian + British)

The following 10 vehicles were already in the database from Canada's Crucible extraction and are used by both Canadian and British forces. Their `nation` field was updated from "Canadian" to "Canadian, British":

1. M4 Sherman
2. M4A1 Sherman
3. M4A4 Sherman
4. M4 Sherman Firefly
5. Bren Carrier
6. Loyd Carrier
7. M5 (Half-track)
8. Humber IV
9. M5 Ambulance
10. Armoured Bulldozer

---

## ✅ British-Only Vehicles (80 new)

### Light Tanks
- Vickers IV, VI A, VI B, VI C
- Tetrarch, Tetrarch CS
- M3A1 Honey, M3A2 Honey, M3A3 Honey
- M5A1 Stuart, M5A2 Stuart, M5A3 Stuart
- M24 Chaffee

### Medium Tanks
- Matilda I, Matilda II, Matilda II CS
- A9, A9 CS
- A10
- A13, A13 MkII
- Cromwell IV, V, HQ, ARV
- Centaur IV, Centaur AA, Centaur Bulldozer
- M4A2 Sherman, M4A3 Sherman
- M4 Sherman (76mm), M4 Sherman Dozer, M4 Sherman DD
- Sherman ARV, Sherman Kangaroo

### Heavy Tanks
- Churchill III, IV, V, VI, VII, VIII
- Churchill AVRE, Churchill Crocodile
- Churchill Ark, Churchill ARV, Churchill AVRE Bridge
- Comet

### Tank Destroyers / Self-Propelled Guns
- Challenger
- M10 Wolverine, M10 Achilles
- Archer
- M7 Priest
- Sexton

### Armored Cars / Reconnaissance
- AEC III
- Daimler
- Dingo, Humber Scout Car
- M3 Scout Car, M8 Greyhound
- M5 Recce, M9
- Staghound, Staghound AA
- Guy Lizard Mk1
- Humber Light Recce
- Morris CS9

### Carriers / Transport
- Wasp (Flamethrower carrier)
- Dorchester ACV
- Guy Lizard ACV
- LVT IV Buffalo (20mm)
- LVT IV Buffalo (MG)
- RAM Kangaroo

### Anti-Aircraft
- Crusader AA MkI
- Crusader AA MkII (2x 20mm)
- Crusader AA MkII (3x 20mm)

### Specialist Vehicles
- Valentine Bridgelayer
- M4 Sherman Crab (Flail mine-sweeper)
- M4 Sherman BARV (Beach Armoured Recovery Vehicle)
- Crusader Tractor
- AVRE Fascine

---

## 🗂️ Field Mapping

### CSV to Database Field Mapping

| CSV Column | Database Column | Notes |
|------------|----------------|-------|
| name | name | ✅ Direct mapping |
| nation | nation | ✅ Set to "British" (or "Canadian, British" for duplicates) |
| year_range | year_range | ✅ Direct mapping |
| vehicle_type | vehicle_type | ✅ Direct mapping |
| off_road_inches | off_road_inches | ✅ Direct mapping |
| road_inches | road_inches | ✅ Direct mapping |
| special_movement | special_movement | ✅ Normalized (e.g., "Unrel" → "Unreliable") |
| armor_front | armor_front | ✅ Direct mapping |
| armor_side | armor_side | ✅ Direct mapping |
| armor_rear | armor_rear | ✅ Direct mapping |
| Schürzen_side | armor_side_schurzen | ✅ Direct mapping |
| weapons | weapons | ✅ Direct mapping |
| special_rules | special_rules | ✅ Direct mapping |
| source_file | source_file | ✅ Direct mapping |
| page_number | source_page | ✅ Direct mapping |
| armor_top | notes | ⚠️ Stored in notes (not in schema) |
| mount | notes | ⚠️ Stored in notes (not in schema) |
| ammo | notes | ⚠️ Stored in notes (not in schema) |

### Additional Database Fields (Auto-populated)

- `extraction_confidence`: "High" (manual data entry)
- `extraction_method`: "manual_csv_entry"
- `source_document`: "Battlegroup DataCards - British"
- `extraction_notes`: "Imported from manually-entered CSV (british_datacards_ALL_VEHICLES.csv)"

---

## 🔧 Script Created

**File**: `scripts/battlegroup/manual_extraction/import_british_datacards_vehicles.py`

**Features**:
- CSV field mapping to database schema
- Duplicate detection (by vehicle name)
- Nation field merging for duplicates
- Special_movement normalization (e.g., "Unrel" → "Unreliable")
- Windows-1252 encoding support (handles Schürzen character)
- Stores unmapped CSV fields (mount, ammo, armor_top) in notes field

---

## 📋 Next Steps

### Guns Import (TODO)

**File**: `british_datacards_ALL_GUNS.csv` (15 guns)
**Table**: `bg_reference_guns`

Similar import script needed to import gun data.

### Aircraft Import (TODO)

**File**: `british_datacards_ALL_AIRCRAFT.csv` (6 aircraft)
**Table**: `bg_reference_aircraft`

Similar import script needed to import aircraft data.

---

## ✅ Verification Queries

Check multi-nation vehicles:
```sql
SELECT name, nation FROM bg_reference_vehicles WHERE nation LIKE '%,%';
```

Check British-only vehicles:
```sql
SELECT COUNT(*) FROM bg_reference_vehicles WHERE nation = 'British';
```

Check Churchill variants:
```sql
SELECT name, year_range, vehicle_type FROM bg_reference_vehicles
WHERE name LIKE 'Churchill%' ORDER BY name;
```

---

**Import Complete**: November 5, 2025
**Git Commit**: (Pending - ready for commit)
