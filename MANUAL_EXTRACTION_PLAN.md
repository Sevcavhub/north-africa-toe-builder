# Manual Extraction Plan - BattleGroup Reference Data
**Date**: November 4, 2025
**Decision**: Manual screenshot extraction (scraper unreliable due to inconsistent PDF table layouts)
**Goal**: 100% accurate reference data for HE/AP conversion formulas

---

## Database Cleanup Strategy

### Option 1: Archive and Start Fresh ⭐ **RECOMMENDED**
```sql
-- Backup existing tables
ALTER TABLE bg_reference_guns RENAME TO bg_reference_guns_scraped_archive;
ALTER TABLE bg_reference_vehicles RENAME TO bg_reference_vehicles_scraped_archive;

-- Create fresh tables
CREATE TABLE bg_reference_guns (same schema);
CREATE TABLE bg_reference_vehicles (same schema);

-- Add audit columns
ALTER TABLE bg_reference_guns ADD COLUMN extraction_method TEXT DEFAULT 'manual_screenshot';
ALTER TABLE bg_reference_guns ADD COLUMN verified_by TEXT;
ALTER TABLE bg_reference_guns ADD COLUMN verification_date TIMESTAMP;
```

**Pros**:
- Keeps historical record of scraper output
- Clean slate for manual entry
- Can compare manual vs scraped data later
- Audit trail for data provenance

---

## Extraction Priority by Theater

### TIER 1: North Africa Equipment (1940-1943) - **CRITICAL PRIORITY**

These are essential for Phase 9B books (Battleaxe, Crusader, Gazala, Alamein):

#### T1-A: Gun Tables
- [ ] **Battlegroup-Kursk.pdf** - German guns (BEST source, user has screenshots)
  - Status: User has Kursk German Gun1.png, Gun2.png
  - Contains: 20mm-210mm German artillery with complete HE/AP data
  - Priority: **IMMEDIATE** (gold standard reference)

- [ ] **Battlegroup-DataCards-British.pdf** - British guns
  - Contains: 2-pdr, 6-pdr, 17-pdr, 25-pdr, 3" mortar, etc.
  - Priority: **HIGH** (needed for British forces)

- [ ] **Battlegroup-DataCards-US.pdf** - American guns
  - Contains: 37mm, 57mm, 75mm, 76mm, 105mm, etc.
  - Priority: **HIGH** (needed for American forces)

- [ ] **Battlegroup-DataCards-Early-German.pdf** - Early war German
  - Contains: Early Panzer III/IV guns, PaK 36, etc.
  - Priority: **HIGH** (1940-1942 equipment)

- [ ] **Battlegroup-DataCards-French-Polish-Romanian-Hungarian.pdf** - French guns
  - Contains: 25mm, 37mm, 47mm, 75mm French artillery
  - Priority: **MEDIUM** (Operation Battleaxe had some captured French equipment)

- [ ] **Battlegroup-Torch-Mission.pdf** - North Africa specific
  - Contains: Theater-specific army lists and equipment
  - Priority: **HIGH** (if readable - OCR quality issues)
  - Note: May have North Africa variants/special rules

#### T1-B: Vehicle/Equipment Tables
- [ ] **Battlegroup-DataCards-British.pdf** - British vehicles
  - Contains: Matilda, Valentine, Crusader, Grant, Sherman, etc.
  - Armor values, movement, special rules
  - Priority: **HIGH**

- [ ] **Battlegroup-DataCards-US.pdf** - American vehicles
  - Contains: Stuart, Grant, Lee, Sherman variants
  - Priority: **HIGH**

- [ ] **Battlegroup-DataCards-Early-German.pdf** - Early German AFVs
  - Contains: Panzer II, III, IV (early variants), SdKfz 221/222/231
  - Priority: **HIGH**

- [ ] **Battlegroup-Kursk.pdf** - German vehicles (mid-war)
  - Contains: Later Panzer III/IV variants, StuG, Marder
  - Priority: **MEDIUM** (some applicable to 1942-1943 North Africa)

- [ ] **Battlegroup-DataCards-French-Polish-Romanian-Hungarian.pdf** - French AFVs
  - Contains: Char B1, Somua S35, Hotchkiss H35/H39, Renault R35
  - Priority: **MEDIUM**

#### T1-C: Army Lists (North Africa specific)
- [ ] **Battlegroup-Torch-Mission.pdf** - Operation Torch army lists
  - American (1st Armored Division, 1st Infantry Division)
  - British (1st Army, 6th Armoured Division)
  - German (Panzer Regiment 190, Hermann Göring Division)
  - Priority: **HIGH** (if readable)

- [ ] **BG Army lists (PDF) v5.pdf** - Generic army lists
  - May contain theater-generic British/German/American lists
  - Priority: **MEDIUM**

---

### TIER 2: Reference/Validation Equipment - **MEDIUM PRIORITY**

These provide validation data and fill gaps:

#### T2-A: Gun Tables
- [ ] **Battlegroup-DataCards-Soviets.pdf** - Soviet guns
  - Priority: **LOW** (not in North Africa, but useful for formula validation)

#### T2-B: Vehicle Tables
- [ ] **Battlegroup-DataCards-Soviets.pdf** - Soviet vehicles
  - Priority: **LOW** (validation only)

- [ ] **Battlegroup-Fall-of-the-Reich-Full.pdf** - Late war equipment
  - Priority: **LOW** (1945 equipment, but may have earlier variants)

---

### TIER 3: Western Europe (Future Phases) - **LOW PRIORITY**

Not needed for Phase 9B, but useful for future work:

- [ ] **Battlegroup-Market-Garden-Army-List.pdf**
- [ ] **Battlegroup-Market-Garden-Scenarios.pdf**
- [ ] **Battlegroup-Overlord-Army-Lists.pdf**
- [ ] **Battlegroup-Overlord-D-Day-scenarios.pdf**
- [ ] **Battlegroup-Wacht-Am-Rhein.pdf**
- [ ] **Battlegroup-Westwall.pdf**
- [ ] **Battlegroup-Canadas-Crucible.pdf**

---

### TIER 4: Rules/Support Documents - **REFERENCE ONLY**

- [ ] **Battlegroup Rules.pdf** - Core rules (reference for stat meanings)
- [ ] **Battlegroup-QRS.pdf** - Quick Reference Sheet
- [ ] **Battlegroup-QRS-4.pdf** - QRS version 4
- [ ] **Battlegroup-Chit-QRS.pdf** - Chit reference
- [ ] **Battlegroup-Dispatches-1/2/3.pdf** - Supplemental rules/scenarios

---

## Extraction Workflow (Per Document)

### For Gun Tables:

**Step 1: Screenshot Capture**
1. Open PDF in viewer (Adobe, browser, etc.)
2. Navigate to gun tables section
3. Screenshot each table page at high resolution
4. Save as: `[document]_guns_page[N].png`
5. Example: `Kursk_guns_page1.png`, `British_DataCards_guns_page1.png`

**Step 2: Manual Data Entry**
1. Create extraction script: `scripts/battlegroup/manual_extraction/enter_guns_[nation].py`
2. Python script with data structure:
```python
guns = [
    {
        "name": "50mmL60 (PaK38)",
        "nation": "german",
        "caliber_mm": 50,
        "barrel_length": "L60",
        "he_dice": 3,
        "he_target": "6+",
        "ap_0_10": 5,
        "ap_10_20": 5,
        "ap_20_30": 4,
        "ap_30_40": 3,
        "ap_40_50": 2,
        "ap_50_70": None,
        "source_file": "Battlegroup-Kursk.pdf",
        "source_page": "23",
        "extraction_method": "manual_screenshot",
        "verified_by": "user",
        "verification_date": "2025-11-04"
    },
    # ... more guns
]
```
3. Script inserts into bg_reference_guns table
4. User reviews screenshot and enters data directly into Python dict
5. Run script to populate database

**Step 3: Verification**
1. Print query of entered guns
2. User visually compares against screenshot
3. Mark any discrepancies
4. Re-enter if needed

### For Vehicle/Equipment Tables:

Same process as guns, but different fields:
```python
vehicles = [
    {
        "name": "Panzer IV Ausf F1",
        "nation": "german",
        "year_range": "1941-1942",
        "vehicle_type": "Medium Tank",
        "off_road_inches": 9,
        "road_inches": 14,
        "armor_front": "K",
        "armor_side": "L",
        "armor_rear": "N",
        "weapons": "75mmL24, MG, MG",
        "points_cost": 76,
        "battle_rating": 4,
        "special_rules": "Smoke Dischargers",
        # ... extraction metadata
    }
]
```

### For Army Lists:

Extract TO&E structures:
```python
army_lists = [
    {
        "list_name": "German Panzer Division, Tunisia 1943",
        "source": "Battlegroup-Torch-Mission.pdf",
        "page": 45,
        "theater": "North Africa",
        "year": "1943",
        "units": [
            {"unit_type": "HQ", "equipment": "Panzer IV Ausf G", "quantity": 2},
            {"unit_type": "Panzer Platoon", "equipment": "Panzer IV Ausf G", "quantity": 5},
            # ... more units
        ]
    }
]
```

---

## Extraction Schedule (Estimated Times)

### Session 1: German Guns (1-2 hours)
- User provides screenshots from Kursk supplement
- Enter 31 German guns from images
- Validate against source
- **Deliverable**: bg_reference_guns with 31 verified German entries

### Session 2: British Guns (1.5-2 hours)
- Screenshot British DataCards gun tables
- Enter ~15-20 British guns
- **Deliverable**: +20 British gun entries

### Session 3: American Guns (1.5-2 hours)
- Screenshot US DataCards gun tables
- Enter ~15-20 American guns
- **Deliverable**: +20 American gun entries

### Session 4: French Guns (1 hour)
- Screenshot French DataCards gun tables
- Enter ~10-15 French guns
- **Deliverable**: +15 French gun entries

### Session 5: German Vehicles (2-3 hours)
- Screenshot Early German + Kursk vehicle datacards
- Enter ~30-40 German AFVs
- **Deliverable**: bg_reference_vehicles with German entries

### Session 6: British Vehicles (2-3 hours)
- Screenshot British DataCards vehicle pages
- Enter ~30-40 British AFVs
- **Deliverable**: +40 British vehicle entries

### Session 7: American Vehicles (1.5-2 hours)
- Screenshot US DataCards vehicle pages
- Enter ~20-25 American AFVs
- **Deliverable**: +25 American vehicle entries

### Session 8: French Vehicles (1 hour)
- Screenshot French DataCards vehicle pages
- Enter ~15-20 French AFVs
- **Deliverable**: +20 French vehicle entries

### Session 9: Validation & QA (2-3 hours)
- Cross-check all entries against screenshots
- Validate conversion formulas with clean data
- Re-run HE/AP population on all 469 equipment items
- **Deliverable**: 100% verified reference data

**Total Estimated Time**: 14-20 hours across 9 sessions

---

## Database Migration Scripts

### Step 1: Archive Old Tables
```sql
-- File: scripts/battlegroup/database/archive_scraped_tables.sql

-- Archive guns
ALTER TABLE bg_reference_guns RENAME TO bg_reference_guns_scraped_archive;

-- Archive vehicles
ALTER TABLE bg_reference_vehicles RENAME TO bg_reference_vehicles_scraped_archive;

-- Record archive metadata
CREATE TABLE extraction_audit (
    id INTEGER PRIMARY KEY,
    table_name TEXT,
    action TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

INSERT INTO extraction_audit (table_name, action, notes)
VALUES ('bg_reference_guns', 'archived', 'Scraped data archived due to 70-100% missing data across nations'),
       ('bg_reference_vehicles', 'archived', 'Scraped data archived to start fresh with manual extraction');
```

### Step 2: Create Fresh Tables
```sql
-- File: scripts/battlegroup/database/create_manual_extraction_tables.sql

CREATE TABLE bg_reference_guns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    nation TEXT NOT NULL,
    caliber_mm INTEGER,
    barrel_length TEXT,
    he_dice INTEGER,
    he_target TEXT,
    ap_0_10 INTEGER,
    ap_10_20 INTEGER,
    ap_20_30 INTEGER,
    ap_30_40 INTEGER,
    ap_40_50 INTEGER,
    ap_50_70 INTEGER,
    points_cost INTEGER,
    battle_rating INTEGER,
    source_file TEXT,
    source_page TEXT,
    extraction_confidence TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Manual extraction audit fields
    extraction_method TEXT DEFAULT 'manual_screenshot',
    verified_by TEXT,
    verification_date TIMESTAMP,
    screenshot_file TEXT,

    UNIQUE(name, nation, source_file)
);

CREATE TABLE bg_reference_vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    nation TEXT NOT NULL,
    year_range TEXT,
    vehicle_type TEXT,
    off_road_inches INTEGER,
    road_inches INTEGER,
    special_movement TEXT,
    armor_front TEXT,
    armor_side TEXT,
    armor_rear TEXT,
    weapons TEXT,
    points_cost INTEGER,
    battle_rating INTEGER,
    special_rules TEXT,
    source_file TEXT,
    source_page TEXT,
    extraction_confidence TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Manual extraction audit fields
    extraction_method TEXT DEFAULT 'manual_screenshot',
    verified_by TEXT,
    verification_date TIMESTAMP,
    screenshot_file TEXT,

    UNIQUE(name, nation, year_range, source_file)
);

CREATE INDEX idx_guns_nation ON bg_reference_guns(nation);
CREATE INDEX idx_guns_caliber ON bg_reference_guns(caliber_mm);
CREATE INDEX idx_vehicles_nation ON bg_reference_vehicles(nation);
CREATE INDEX idx_vehicles_type ON bg_reference_vehicles(vehicle_type);
```

### Step 3: Clear Corrupted Equipment Linkages
```sql
-- File: scripts/battlegroup/database/clear_corrupted_linkages.sql

-- Clear HE/AP values that were populated from corrupted data
UPDATE equipment_battlegroup
SET he_value = NULL,
    ap_0_10 = NULL,
    ap_10_20 = NULL,
    ap_20_30 = NULL,
    ap_30_40 = NULL,
    ap_40_50 = NULL,
    ap_50_70 = NULL,
    reference_gun_id = NULL
WHERE reference_gun_id IS NOT NULL
   OR (he_value IS NOT NULL AND equipment_id IN (
       -- Transport vehicles that somehow got gun stats
       SELECT id FROM equipment WHERE category = 'transport'
   ));

-- Clear vehicle linkages (will re-link after manual extraction)
UPDATE equipment_battlegroup
SET reference_vehicle_id = NULL;

-- Record cleanup
INSERT INTO extraction_audit (table_name, action, notes)
VALUES ('equipment_battlegroup', 'cleared_corrupted_data',
        'Cleared HE/AP values and linkages populated from corrupted reference data');
```

---

## Next Steps

### Immediate (This Session):
1. **User Decision**: Approve archive strategy
2. **Execute**: Run archive scripts
3. **Screenshot**: User captures Kursk German gun tables (already has images!)
4. **Enter**: Create and run `enter_guns_german.py` with 31 guns from screenshots

### Session 2-4 (Guns):
5. Screenshot British gun tables → enter data
6. Screenshot American gun tables → enter data
7. Screenshot French gun tables → enter data

### Session 5-8 (Vehicles):
8. Screenshot German vehicle datacards → enter data
9. Screenshot British vehicle datacards → enter data
10. Screenshot American vehicle datacards → enter data
11. Screenshot French vehicle datacards → enter data

### Session 9 (Validation):
12. Re-validate conversion formulas against clean reference data
13. Re-run HE/AP population on all 469 equipment items
14. QA check: No transport trucks with 300mm guns!
15. Update PROJECT_SCOPE.md with completion status

---

**Estimated Timeline**: 2-3 weeks at 1-2 sessions per week, OR 3-4 days intensive work

**Quality Guarantee**: 100% accurate reference data, auditable provenance, publication-ready
