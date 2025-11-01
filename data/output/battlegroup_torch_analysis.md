# Battlegroup Torch Extraction Analysis

## Issue Identified

The **Battlegroup Torch Mission.pdf** is a **scenario/mission supplement**, NOT a datacard or army list book. It contains:

- Special rules for North African operations (Combined Operations, Mobile Warfare, Desert Dust Cloud)
- Terrain generation rules for Tunisia vs. open desert
- Specific scenarios (Ridgeline Assault, etc.)
- Historical context for Operation Torch (November 1942)

**IT DOES NOT contain comprehensive vehicle/gun datacards.**

## Source File Quality

Both the PDF and TXT files are heavily corrupted from OCR processing:
- Text extraction yields garbled characters
- Table structures are destroyed
- No clean vehicle/gun data tables exist

## Operation Torch Equipment Coverage

Operation Torch (November 1942) forces are already covered in existing Battlegroup datacard extractions:

### American Forces (Operation Torch participants)
**Already extracted in:** `battlegroup_us_vehicles.json`
- M5 Stuart (1942-1945)
- M4 Sherman (1942-1945)
- M3 Grant/Lee (if extracted)
- M3 Stuart (if extracted)
- M3 Halftrack
- Various support vehicles

### British Forces (Operation Torch participants)
**Already extracted in:** `battlegroup_british_vehicles.json` (1,303 lines)
- Crusader variants
- Valentine
- Matilda II
- M4 Sherman (British service)
- Various cruiser tanks
- Support vehicles

### Free French Forces (Operation Torch participants)
**Already extracted in:** `battlegroup_french_polish_romanian_hungarian_complete.json`
- R-35
- H-39
- S-35
- Char B1
- Various support equipment

### Vichy French Forces (Operation Torch defenders)
**Same as Free French** - used same equipment

### German Forces (rushed reinforcements)
**Already extracted in:** `battlegroup_early_german_vehicles.json` (866 lines)
- Panzer III variants (Ausf F, G, H, J, L, M, N)
- Panzer IV variants (Ausf D, E, F1, F2, G)
- StuG III variants
- Various support vehicles

## Recommendation

**The equipment data for Operation Torch is already extracted from the main Battlegroup datacard books.**

### Option 1: Compile Torch-Specific Subset (Recommended)
Create a filtered subset from existing extractions containing only equipment relevant to Operation Torch timeline (1942):
- Filter by `year_range` containing "1942"
- Filter by nations: american, british, french, german, italian
- Create `battlegroup_torch_1942_vehicles.json` and `battlegroup_torch_1942_guns.json`

### Option 2: Manual Data Entry
If Torch Mission book contains unique variants or special rules not in datacards:
- Manually transcribe from PDF pages
- Cross-reference with existing extractions to avoid duplicates

### Option 3: Wait for Better Source
Request a higher-quality scan or digital source of the Torch Mission book if unit data is critical.

## Database Integration

The project database (`master_database.db`) currently has:
- **261 vehicles** in extraction log
- **47 guns** in extraction log
- Tables: `units`, `extraction_log`, `source_citations`, `equipment_variants`, `individual_positions`

**Note:** The `bg_reference_vehicles` and `bg_reference_guns` tables mentioned in the task **do not exist** in the current database schema.

## Next Steps

1. **Clarify Objective**: Does user want:
   - A) All Torch-timeline equipment (compiled from existing extractions) ✅ DOABLE
   - B) New extraction from corrupted Torch PDF ❌ NOT FEASIBLE
   - C) Specific Torch scenarios/special rules ✅ DOABLE (text extraction possible)

2. **Recommended Action**: Create Torch-filtered compilation from existing high-quality extractions

3. **Alternative**: Extract special rules and scenarios from Torch Mission book (these ARE unique and valuable)
