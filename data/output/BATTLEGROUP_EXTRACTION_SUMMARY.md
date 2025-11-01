# BattleGroup French/Polish/Romanian/Hungarian Vehicle Extraction

**Extraction Date**: 2025-10-31  
**Source PDF**: `Battlegroup-DataCards-French-Polish-Romanian-Hungarian.pdf`  
**Pages Analyzed**: 6 pages  
**Output Files**:
- Complete data: `battlegroup_french_polish_romanian_hungarian_complete.json`
- Vehicles only: `battlegroup_french_polish_romanian_hungarian_vehicles.json`

---

## Extraction Summary

### Vehicles Extracted: 8 total

#### French Vehicles (7)
1. **R-35** (Renault R-35)
   - Movement: 12" off-road, 16" road
   - Armor: Front 0, Side 0, Rear 0
   - Armament: 37mm L21 turret (9 rounds)

2. **H-35** (Hotchkiss H-35)
   - Movement: 8" off-road, 12" road (1 man turret)
   - Armor: Front M, Side N, Rear N
   - Armament: 37mm L21 turret (10 rounds), MG co-axial

3. **H-39** (Hotchkiss H-39)
   - Movement: 8" off-road, 12" road (1 man turret)
   - Armor: Front M, Side N, Rear N
   - Armament: 37mm L21 turret (10 rounds), MG co-axial

4. **S-35** (Somua S-35)
   - Movement: 9" off-road, 13" road (1 man turret)
   - Armor: Front M, Side N, Rear 0
   - Armament: 47mm L35 turret (6 rounds), MG co-axial

5. **AMC-35** (Automitrailleuse de Combat)
   - Movement: 9" off-road, 13" road
   - Armor: Front M, Side N, Rear 0
   - Armament: 47mm L32 turret (12 rounds), MG co-axial

6. **AMR-35** (Automitrailleuse de Reconnaissance)
   - Movement: 4" off-road, 6" road
   - Armor: Front L, Side N, Rear 0
   - Armament: 47mm L32 turret (11 rounds), 2x MG (co-axial + hull)

7. **AMD-35** (Automitrailleuse de Découverte)
   - Movement: 5" off-road, 7" road
   - Armor: Front L, Side N, Rear 0
   - Armament: 47mm L32 turret (11 rounds), 2x MG (co-axial + hull)

#### Other Vehicles (1)
8. **Tatra** (truck)
   - Movement: 8" off-road, 24" road
   - Armor: Front 0, Side 0, Rear 0
   - Armament: 2x MG (turret + hull)
   - Nation: Unknown (Polish/Romanian/Hungarian)

---

### Aircraft Extracted: 4 total

#### French Aircraft (2)
1. **Breguet 690** - Light Bomber
   - Hits: 4
   - Weaponry: 20mm cannon, 3x MGs, bombs (3x large or 6x small)

2. **MS.406** - Fighter
   - Hits: 3
   - Weaponry: 2x MGs, 20mm cannon

#### Romanian Aircraft (2)
3. **IAR 80** - Fighter
   - Weaponry: 2x MGs

4. **IAR 39** - Bi-plane Fighter
   - Weaponry: 2x MGs, 1x medium bomb

---

## Extraction Notes

### Challenges
- **Poor OCR Quality**: PDF text extraction was difficult due to scanning/OCR issues
- **Limited Coverage**: Only 6 pages in PDF, mostly French vehicles
- **Missing Nations**: Expected Polish/Hungarian vehicles not found (possibly separate PDF or poor OCR)

### Data Quality
- **Confirmed Vehicles**: 7 French tanks/armored cars extracted with complete stats
- **Partial Data**: 1 Tatra truck (nation unclear)
- **Aircraft Bonus**: 4 aircraft profiles also extracted

### Armor Value Key
BattleGroup uses letter codes for armor thickness:
- **0** = Unarmored/minimal
- **L** = Light armor
- **M** = Medium armor
- **N** = Medium-heavy armor
- **O** = Heavy armor

### Next Steps
1. Cross-reference with other BattleGroup PDFs for missing nations
2. Validate vehicle specifications against historical sources
3. Integrate into equipment database if needed for North Africa scenarios

---

## File Locations

**Output Files**:
- `D:\north-africa-toe-builder\data\output\battlegroup_french_polish_romanian_hungarian_complete.json`
- `D:\north-africa-toe-builder\data\output\battlegroup_french_polish_romanian_hungarian_vehicles.json`

**Source Document**:
- `D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Battlegroup-DataCards-French-Polish-Romanian-Hungarian.pdf`

**Extraction Tools**:
- `D:\north-africa-toe-builder\tools\extract_battlegroup_vehicles.py`
- `D:\north-africa-toe-builder\tools\extract_battlegroup_vehicles_v2.py`
- `D:\north-africa-toe-builder\tools\extract_battlegroup_vehicles_v3.py`
- `D:\north-africa-toe-builder\tools\extract_battlegroup_full.py`
