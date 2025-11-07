# Import Implementation Plan

**Date**: November 5, 2025
**Purpose**: Step-by-step execution roadmap for British DataCards import completion
**Scope**: Complete British data, prepare for German/Italian/American imports

---

## Current Status (as of November 5, 2025)

### ✅ COMPLETED

**British Vehicles**: DONE
- CSV created: `british_datacards_ALL_VEHICLES.csv` (90 vehicles)
- Import script: `import_british_datacards_vehicles.py` ✅ EXECUTED
- Database: 144 vehicles in `bg_reference_vehicles` (64 Canadian + 80 British)
- Multi-nation support: 10 vehicles flagged as "Canadian, British"

**Database Schema**: UPDATED
- Migration 1-3: HE ranges, gun_name_variants, he_shell_classification ✅ COMPLETE
- Migration 4: ROF, weapon_category, special_rules - PENDING

**Documentation**: COMPLETE
- 8 documentation files created (21KB + 7KB + 9KB + 15KB + 13KB + 18KB + 8KB + TBD)
- Research preserved: weapon systems, edge cases, validation specs, classification, OCR design

### ⏸️ IN PROGRESS

**British Guns**: AWAITING USER DATA ENTRY
- CSV template: `british_datacards_ALL_GUNS_UPDATED.csv` (20 columns, ROF added)
- Import script: `import_british_datacards_guns.py` READY (not executed)
- Status: User filling HE/AP data from British DataCards PDF

**British Aircraft**: NOT STARTED
- CSV template: `british_datacards_ALL_AIRCRAFT.csv` (awaiting user completion)
- Import script: `import_british_datacards_aircraft.py` READY (not executed)

---

## Phase 1: Complete British Import (4-6 hours)

### Step 1.1: User Data Entry (2-3 hours)

**User tasks**:
1. Fill `british_datacards_ALL_GUNS_UPDATED.csv` with HE/AP data from British DataCards PDF
   - 24 guns estimated (based on Canadian = 26 guns)
   - Fields: HE ranges (6 columns), AP ranges (6 columns), ROF, he_shell_classification
   - Edge cases handled: Littlejohn (row 17 cleaned), Flamethrower (D6), AA guns (AP only)

2. Edit row 17 (2 pdr Littlejohn Adaptor):
   - Remove dual values `3(4)` → use single base value `3`
   - Plan: Create two gun records post-import (standard 2 pdr + Littlejohn variant)

3. Fill `british_datacards_ALL_AIRCRAFT.csv` with aircraft weapon data
   - Estimated: 10-15 aircraft types
   - Fields: Same as guns (HE/AP ranges, bombs/rockets)

**Estimated time**: 2-3 hours (similar to vehicles)

### Step 1.2: Database Migration 4 (15 minutes)

**Execute remaining schema changes**:
```sql
-- Add columns to bg_reference_guns
ALTER TABLE bg_reference_guns ADD COLUMN rof INTEGER DEFAULT NULL;
ALTER TABLE bg_reference_guns ADD COLUMN weapon_category TEXT DEFAULT NULL;
ALTER TABLE bg_reference_guns ADD COLUMN category_confidence INTEGER DEFAULT NULL;
ALTER TABLE bg_reference_guns ADD COLUMN gun_role TEXT DEFAULT NULL;
ALTER TABLE bg_reference_guns ADD COLUMN max_range_inches INTEGER DEFAULT NULL;
ALTER TABLE bg_reference_guns ADD COLUMN special_rules TEXT DEFAULT NULL;

-- Add metadata columns
ALTER TABLE bg_reference_guns ADD COLUMN import_date TEXT DEFAULT NULL;
ALTER TABLE bg_reference_guns ADD COLUMN import_source TEXT DEFAULT NULL;
ALTER TABLE bg_reference_guns ADD COLUMN validation_notes TEXT DEFAULT NULL;

-- Same for aircraft table
ALTER TABLE bg_reference_aircraft ADD COLUMN weapon_category TEXT DEFAULT NULL;
ALTER TABLE bg_reference_aircraft ADD COLUMN rof INTEGER DEFAULT NULL;
-- ... (similar columns)
```

**Script**: Create `migrate_guns_migration_4.sql`

**Execution**:
```bash
sqlite3 database/master_database.db < scripts/battlegroup/manual_extraction/migrate_guns_migration_4.sql
```

**Validation**:
```bash
sqlite3 database/master_database.db "PRAGMA table_info(bg_reference_guns);"
# Verify 35+ columns present
```

### Step 1.3: Update Import Scripts (30 minutes)

**Update `import_british_datacards_guns.py`**:
- Integrate flexible parser from `GUN_IMPORT_VALIDATION_SPEC.md`
- Add auto-detection from `WEAPON_CATEGORY_CLASSIFICATION.md`
- Add OCR error correction patterns
- Add validation logging (ERROR/WARNING/INFO levels)

**Key changes**:
```python
# Add at top of script
from datetime import datetime

def parse_numeric_field(value, field_name):
    """Flexible parser accepting numbers, dice, dual values."""
    # (Implementation from GUN_IMPORT_VALIDATION_SPEC.md)
    pass

def auto_detect_weapon_category(gun):
    """Auto-classify weapon type."""
    # (Implementation from WEAPON_CATEGORY_CLASSIFICATION.md)
    pass

# Update main import loop
for row in csv_reader:
    gun = map_csv_row(row)  # 20-column mapping

    # Validate
    errors = validate_critical_fields(gun)
    if errors:
        log_error(f"Row {row_num}: {errors}")
        continue

    # Auto-detect category
    gun['weapon_category'] = auto_detect_weapon_category(gun)
    gun['category_confidence'] = get_classification_confidence(gun)

    # Insert to database
    insert_gun(gun)
```

**Update `import_british_datacards_aircraft.py`**:
- Similar changes to guns script
- Aircraft-specific weapon categories (bomb, rocket, aircraft_cannon)

### Step 1.4: Execute British Guns Import (10 minutes)

**Prerequisites**:
- User completed CSV data entry (Step 1.1)
- Migration 4 executed (Step 1.2)
- Import script updated (Step 1.3)

**Execution**:
```bash
python scripts/battlegroup/manual_extraction/import_british_datacards_guns.py \
    --csv "D:/north-africa-toe-builder/british_datacards_ALL_GUNS_UPDATED.csv" \
    --nation british \
    --validate-only  # Dry run first

# Review validation output
# If OK, run actual import:
python scripts/battlegroup/manual_extraction/import_british_datacards_guns.py \
    --csv "D:/north-africa-toe-builder/british_datacards_ALL_GUNS_UPDATED.csv" \
    --nation british
```

**Expected output**:
```
[*] Processing british_datacards_ALL_GUNS_UPDATED.csv
[+] Loaded 24 rows

Row 1: Ordnance QF 25-pdr
  [+] Valid critical fields
  [+] HE data: 6/4+ with ranges
  [+] AP data: 0-40" ranges
  [INFO] Auto-detected category: field_artillery_light (confidence=85)
  [INFO] Created variant: "25 pdr"

Row 17: 2 pdr (Littlejohn Adaptor)
  [+] Valid critical fields
  [+] AP data: base values only (dual values removed)
  [INFO] Auto-detected category: at_gun (confidence=90)
  [!] RECOMMEND: Create separate gun record for standard 2 pdr

...

Summary:
  Total: 24 guns
  Imported: 24
  Errors: 0
  Warnings: 2 (Littlejohn, Flamethrower)
  Manual review: 2 items flagged
```

**Database validation**:
```bash
sqlite3 database/master_database.db "SELECT COUNT(*) FROM bg_reference_guns WHERE nation LIKE '%british%';"
# Expected: 24 British + 26 Canadian = 50+ total guns
```

### Step 1.5: Execute British Aircraft Import (10 minutes)

**Same process as guns**:
```bash
python scripts/battlegroup/manual_extraction/import_british_datacards_aircraft.py \
    --csv "D:/north-africa-toe-builder/british_datacards_ALL_AIRCRAFT.csv" \
    --nation british
```

### Step 1.6: Create Gun Variants (30 minutes)

**Littlejohn Adaptor** (manual SQL):
```sql
-- Verify existing 2 pdr record
SELECT id, name, ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70
FROM bg_reference_guns
WHERE name LIKE '%2 pdr%' AND nation LIKE '%british%';

-- Create Littlejohn variant (if needed)
INSERT INTO bg_reference_guns (
    name, common_name, nation, caliber_mm, rof,
    ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70,
    weapon_category, import_date, import_source
)
SELECT
    '2 pdr (Littlejohn Adaptor)',
    '2 pdr Littlejohn',
    nation,
    caliber_mm,
    rof,
    4, 4, 3, 2, 1, NULL,  -- Enhanced AP values
    'at_gun',
    datetime('now'),
    'Manual variant creation from british_datacards'
FROM bg_reference_guns
WHERE name = '2 pdr' AND nation LIKE '%british%';

-- Create gun_name_variants
INSERT INTO gun_name_variants (gun_id, variant_name, variant_source, is_official)
SELECT id, 'Littlejohn', 'British DataCards', 1
FROM bg_reference_guns
WHERE name = '2 pdr (Littlejohn Adaptor)';
```

**Tetrarch vehicle variant** (link to Littlejohn gun):
```sql
-- Find Tetrarch vehicle
SELECT id, name, weapons FROM bg_reference_vehicles WHERE name LIKE '%Tetrarch%';

-- Duplicate Tetrarch with Littlejohn gun
INSERT INTO bg_reference_vehicles (
    name, nation, vehicle_type, crew, points_cost, battle_rating,
    movement_slow, movement_fast, armor_front, armor_side, armor_rear, armor_top,
    weapons, special_rules, import_date, import_source
)
SELECT
    name || ' (Littlejohn)',
    nation,
    vehicle_type,
    crew,
    points_cost + 5,  -- Slight points increase for upgraded gun
    battle_rating,
    movement_slow,
    movement_fast,
    armor_front,
    armor_side,
    armor_rear,
    armor_top,
    '2 pdr (Littlejohn Adaptor)',  -- Updated weapon
    special_rules,
    datetime('now'),
    'Manual variant creation'
FROM bg_reference_vehicles
WHERE name = 'Tetrarch' AND nation LIKE '%british%';
```

### Step 1.7: Validation & QA (30 minutes)

**Database integrity checks**:
```bash
# Count totals
sqlite3 database/master_database.db "SELECT nation, COUNT(*) FROM bg_reference_vehicles GROUP BY nation;"
sqlite3 database/master_database.db "SELECT nation, COUNT(*) FROM bg_reference_guns GROUP BY nation;"

# Check for NULL critical fields
sqlite3 database/master_database.db "SELECT name FROM bg_reference_guns WHERE caliber_mm IS NULL;"
sqlite3 database/master_database.db "SELECT name FROM bg_reference_vehicles WHERE armor_front IS NULL;"

# Verify gun variants
sqlite3 database/master_database.db "SELECT COUNT(*) FROM gun_name_variants;"

# Check weapon_category population
sqlite3 database/master_database.db "SELECT weapon_category, COUNT(*) FROM bg_reference_guns GROUP BY weapon_category;"
```

**Expected totals**:
- Vehicles: 144+ (64 Canadian + 80 British + variants)
- Guns: 50+ (26 Canadian + 24 British)
- Aircraft: 10-15 British
- gun_name_variants: 50+ entries

**Generate validation report**:
```python
# Create validation_report.py
import sqlite3

conn = sqlite3.connect('database/master_database.db')
cursor = conn.cursor()

print("=== BRITISH DATACARDS IMPORT VALIDATION ===\n")

# Vehicles
cursor.execute("SELECT COUNT(*) FROM bg_reference_vehicles WHERE nation LIKE '%british%'")
print(f"British vehicles: {cursor.fetchone()[0]}")

# Guns
cursor.execute("SELECT COUNT(*) FROM bg_reference_guns WHERE nation LIKE '%british%'")
print(f"British guns: {cursor.fetchone()[0]}")

# Critical field coverage
cursor.execute("SELECT COUNT(*) FROM bg_reference_guns WHERE caliber_mm IS NULL")
print(f"Guns missing caliber: {cursor.fetchone()[0]} (should be 0)")

cursor.execute("SELECT COUNT(*) FROM bg_reference_guns WHERE weapon_category IS NULL")
print(f"Guns missing category: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM bg_reference_guns WHERE weapon_category IS NOT NULL")
print(f"Guns with auto-detected category: {cursor.fetchone()[0]}")

conn.close()
```

---

## Phase 2: Prepare for German Import (1-2 hours)

### Step 2.1: Analyze German DataCards (30 minutes)

**If German PDF available**:
1. Count pages, estimate total vehicles/guns/aircraft
2. Identify unique German-specific edge cases:
   - Schürzen (side skirts) armor modifier
   - Squeeze-bore guns (28/20mm, 42/28mm)
   - Panzerfaust (one-shot, variable range)
   - Nebelwerfer (rocket artillery)
3. Document in `docs/battlegroup/GERMAN_EDGE_CASES.md`

**If German PDF not available**:
- Skip to Step 2.2, proceed with Italian/American

### Step 2.2: Create German CSV Templates (15 minutes)

**Copy British templates**:
```bash
cp british_datacards_ALL_VEHICLES.csv german_datacards_ALL_VEHICLES.csv
cp british_datacards_ALL_GUNS_UPDATED.csv german_datacards_ALL_GUNS.csv
cp british_datacards_ALL_AIRCRAFT.csv german_datacards_ALL_AIRCRAFT.csv

# Clear data rows (keep headers)
# User will fill with German data
```

### Step 2.3: Update Import Scripts for German (30 minutes)

**Minimal changes needed** (nation parameter):
```bash
python scripts/battlegroup/manual_extraction/import_british_datacards_vehicles.py \
    --csv "german_datacards_ALL_VEHICLES.csv" \
    --nation german  # Only change needed
```

**German-specific additions**:
- Add "Schürzen" to special_rules normalization
- Add German gun name variants (PaK, KwK, FlaK abbreviations)
- Add German-specific weapon categories (Panzerfaust, Panzerschreck)

### Step 2.4: Italian & American Templates (30 minutes)

**Same process**:
- Copy CSV templates
- Create nation-specific import commands
- Document nation-specific edge cases

---

## Phase 3: OCR Extraction (Future) (8-12 hours)

### Step 3.1: Install OCR Dependencies

```bash
pip install pdf2image pytesseract pillow opencv-python

# Windows: Download Tesseract installer
# https://github.com/UB-Mannheim/tesseract/wiki

# Add to PATH: C:\Program Files\Tesseract-OCR
```

### Step 3.2: Implement OCR Pipeline

**Create `ocr_extract_datacards.py`**:
- Implement architecture from `OCR_SCRAPER_ARCHITECTURE.md`
- Test on British DataCards PDF (validation against manual CSV)
- Measure accuracy, adjust regex patterns

### Step 3.3: Batch Process All Nations

```bash
python ocr_extract_datacards.py "British DataCards.pdf" british
python ocr_extract_datacards.py "German DataCards.pdf" german
python ocr_extract_datacards.py "Italian DataCards.pdf" italian
python ocr_extract_datacards.py "American DataCards.pdf" american
```

**Expected time**: 3-6 minutes per nation (vs 2-4 hours manual)

---

## Phase 4: Equipment Linkage (Phase 9B) (4-7 hours)

### Step 4.1: Link WITW Equipment to BattleGroup Reference

**Current**: 96/469 items linked (20.5%)
**Target**: 469/469 items (100%)

**Process**:
1. Run Tier 1-4 linkage scripts (already created)
2. Manual review of unlinked items (373 remaining)
3. Create Tier 5 custom linkage script for edge cases
4. Validate all linkages

**Script**: `scripts/linkage/complete_equipment_linkage.py`

### Step 4.2: Generate Equipment Datacards

**Once linkage complete**:
```bash
python scripts/battlegroup/book/generate_book_datacards.py --all
```

**Output**: 4 books with 100% equipment stats populated

### Step 4.3: Generate Forces/TO&E Tables

**Extract from Phase 6 units**:
```bash
python scripts/battlegroup/book/generate_forces_tables.py --all
```

**Output**: Organizational hierarchy for all 4 battles

---

## Execution Checklist

### British Import (This Session)

- [ ] **User**: Fill british_datacards_ALL_GUNS_UPDATED.csv (2-3 hours)
- [ ] **User**: Edit row 17 (remove dual values)
- [ ] **User**: Fill british_datacards_ALL_AIRCRAFT.csv (1-2 hours)
- [ ] **Agent**: Execute Migration 4 SQL (15 min)
- [ ] **Agent**: Update import_british_datacards_guns.py (30 min)
- [ ] **Agent**: Execute British guns import (10 min)
- [ ] **Agent**: Execute British aircraft import (10 min)
- [ ] **Agent**: Create Littlejohn gun variant (15 min)
- [ ] **Agent**: Create Tetrarch vehicle variant (15 min)
- [ ] **Agent**: Run validation report (15 min)

**Total estimated time**: 4-6 hours (mostly user data entry)

### German/Italian/American (Future Sessions)

- [ ] Analyze nation-specific edge cases (30 min per nation)
- [ ] Create CSV templates (15 min per nation)
- [ ] User data entry (2-4 hours per nation)
- [ ] Execute imports (30 min per nation)
- [ ] Validation (30 min per nation)

**Total per nation**: 3-5 hours

### OCR Automation (Optional Future)

- [ ] Install Tesseract (30 min)
- [ ] Implement OCR pipeline (4-6 hours)
- [ ] Test on British PDF (2 hours)
- [ ] Batch process all nations (20 min)
- [ ] Manual review of flagged items (2-4 hours)

**Total**: 8-12 hours (one-time investment, saves 20-40 hours across all nations)

---

## Success Criteria

### British Import Complete When:
1. ✅ 80+ British vehicles in database
2. ✅ 24+ British guns in database
3. ✅ 10+ British aircraft in database
4. ✅ All gun_name_variants created
5. ✅ All weapon_category fields populated (90%+ coverage)
6. ✅ Zero NULL critical fields (name, nation, caliber)
7. ✅ Validation report shows no errors

### Ready for German Import When:
1. ✅ German CSV templates created
2. ✅ German edge cases documented
3. ✅ Import scripts tested on British data
4. ✅ User ready to begin German data entry

### Ready for Phase 9B Completion When:
1. ✅ All 4 nations imported (British, German, Italian, American)
2. ✅ Equipment linkage 100% complete
3. ✅ Equipment datacards generated with zero "None" values
4. ✅ Forces/TO&E tables populated
5. ✅ All 4 books pass QA validation

---

**Current Priority**: Complete British import (Steps 1.1-1.7)
**Next Session**: Begin German import OR implement OCR pipeline (user decision)
**Estimated Time to Phase 9B MVP**: 15-20 hours (with manual CSV entry) OR 10-15 hours (with OCR automation)
