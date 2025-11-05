# Session Summary: Data Quality Audit & Manual Extraction Setup
**Date**: November 4, 2025
**Duration**: ~2 hours
**Focus**: PHASE 9B SHOWSTOPPER - Corrupted reference data discovery and resolution plan

---

## What We Discovered

### Critical Finding: Corrupted Reference Data

**Impact**: ~99 of 191 equipment items (52%) have potentially incorrect HE/AP weapon stats

**Data Quality by Nation**:
- **German**: 70% missing AP, 22% missing HE, 2 garbage OCR entries
- **American**: 100% missing HE and AP
- **British**: 100% missing HE and AP
- **Soviet**: 100% missing HE and AP, ALL 3 names have quantity prefixes

**Examples of Corruption**:
1. **Missing Data**: `75mmL46 (PaK40)` has HE 4/4+ but NULL for all AP values (should be: -, 8, 8, 7, 6, 5, 4)
2. **Garbage OCR**: "At the base of the Seelow escarpment collections. In this case, the German 80mm mortar team"
3. **Your Discovery**: Transport trucks showing 300mm artillery (regex bug: "C30 CMP" → "30cm")

**Root Cause**: The `datacard_scraper.py` failed to properly extract gun table data from PDFs due to:
- Inconsistent table layouts across supplements
- OCR quality variations
- Table boundary detection issues
- Gun name regex too restrictive

### User's Decision: Manual Entry

**Rationale**:
- PDF table layouts are inconsistent across supplements
- No two datasets are spaced the same
- Manual is the only guarantee of accuracy
- User has excellent screenshot sources (Kursk German Gun1.png, Gun2.png)

---

## What We Created

### 1. Documentation Files

#### `DATA_QUALITY_AUDIT_2025-11-04.md`
Comprehensive audit report with:
- Nation-by-nation data quality breakdown
- Source verification (what SHOULD be vs what IS)
- Scraper code analysis showing specific bugs
- Impact assessment on 191 populated items
- Complete German gun audit table
- **Location**: `D:\north-africa-toe-builder\DATA_QUALITY_AUDIT_2025-11-04.md`

#### `MANUAL_EXTRACTION_PLAN.md`
Complete manual extraction strategy with:
- Database cleanup strategy (archive & start fresh)
- Extraction priority by theater (3 tiers)
- Workflow for guns, vehicles, army lists
- Session-by-session extraction schedule (9 sessions, 14-20 hours)
- Available source files organized by priority
- **Location**: `D:\north-africa-toe-builder\MANUAL_EXTRACTION_PLAN.md`

### 2. Database Migration Scripts

#### `archive_scraped_tables.sql`
Archives corrupted tables with audit trail:
- Renames `bg_reference_guns` → `bg_reference_guns_scraped_archive`
- Renames `bg_reference_vehicles` → `bg_reference_vehicles_scraped_archive`
- Creates `extraction_audit` table for tracking
- Records archive action with timestamp and notes
- **Location**: `D:\north-africa-toe-builder\scripts\battlegroup\database\archive_scraped_tables.sql`

#### `create_manual_extraction_tables.sql`
Creates fresh tables with audit fields:
- New `bg_reference_guns` table with manual extraction columns
- New `bg_reference_vehicles` table with manual extraction columns
- Added audit fields: `extraction_method`, `verified_by`, `verification_date`, `screenshot_file`
- Creates indexes for efficient querying
- **Location**: `D:\north-africa-toe-builder\scripts\battlegroup\database\create_manual_extraction_tables.sql`

#### `clear_corrupted_linkages.sql`
Clears bad HE/AP data from equipment:
- Clears all HE/AP values from `equipment_battlegroup`
- Clears `reference_gun_id` linkages
- Clears `reference_vehicle_id` linkages
- Records cleanup actions in audit log
- **Location**: `D:\north-africa-toe-builder\scripts\battlegroup\database\clear_corrupted_linkages.sql`

#### `execute_migration.py`
Master migration script that orchestrates all three steps:
- Creates timestamped database backup first (safety!)
- Executes archive → create → clear in sequence
- Verifies tables exist before migration
- Prints comprehensive summary after completion
- Rollback on errors
- **Location**: `D:\north-africa-toe-builder\scripts\battlegroup\database\execute_migration.py`
- **Usage**: `python scripts/battlegroup/database/execute_migration.py`

### 3. Manual Entry Template Scripts

#### `enter_guns_german.py`
Template for entering German guns from Kursk screenshots:
- Pre-filled with 13 example German guns (20mm-150mm)
- TODO markers for user to add remaining guns from screenshots
- Inserts into `bg_reference_guns` with full audit trail
- Verification summary after insertion
- **Location**: `D:\north-africa-toe-builder\scripts\battlegroup\manual_extraction\enter_guns_german.py`
- **Usage**: `python scripts/battlegroup/manual_extraction/enter_guns_german.py`

**Template Structure** (copy for other nations):
```python
GERMAN_GUNS = [
    (name, caliber_mm, barrel_length, he_dice, he_target,
     ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70, notes),
]
```

User can create similar scripts:
- `enter_guns_british.py`
- `enter_guns_american.py`
- `enter_guns_french.py`
- `enter_vehicles_german.py`
- etc.

---

## What to Do with Current BG Tables

### Recommended: Archive and Start Fresh ⭐

**Execute Migration** (creates backup automatically):
```bash
cd D:\north-africa-toe-builder
python scripts/battlegroup/database/execute_migration.py
```

**What This Does**:
1. Creates timestamped backup: `master_database_backup_YYYYMMDD_HHMMSS.db`
2. Archives old tables: `bg_reference_guns_scraped_archive`, `bg_reference_vehicles_scraped_archive`
3. Creates fresh tables: `bg_reference_guns`, `bg_reference_vehicles` (with audit fields)
4. Clears corrupted HE/AP data from `equipment_battlegroup`
5. Records all actions in `extraction_audit` table

**Benefits**:
- Keeps historical record of scraper output
- Clean slate for manual entry
- Can compare manual vs scraped data later
- Full audit trail for data provenance
- **Database backup created FIRST for safety!**

---

## Extraction Priority (From MANUAL_EXTRACTION_PLAN.md)

### TIER 1: North Africa Equipment (1940-1943) - **CRITICAL PRIORITY**

#### Guns (Required for Phase 9B):
1. ✅ **Battlegroup-Kursk.pdf** - German guns (user has screenshots!)
   - Priority: **IMMEDIATE**
   - Status: Template script created (`enter_guns_german.py`)

2. **Battlegroup-DataCards-British.pdf** - British guns
   - Contains: 2-pdr, 6-pdr, 17-pdr, 25-pdr, 3" mortar, etc.
   - Priority: **HIGH**

3. **Battlegroup-DataCards-US.pdf** - American guns
   - Contains: 37mm, 57mm, 75mm, 76mm, 105mm, etc.
   - Priority: **HIGH**

4. **Battlegroup-DataCards-Early-German.pdf** - Early German
   - Contains: Early Panzer III/IV guns, PaK 36, etc.
   - Priority: **HIGH**

5. **Battlegroup-DataCards-French-Polish-Romanian-Hungarian.pdf** - French guns
   - Contains: 25mm, 37mm, 47mm, 75mm French artillery
   - Priority: **MEDIUM**

#### Vehicles (Required for Phase 9B):
- Same PDFs, vehicle datacard pages
- ~30-40 German, ~30-40 British, ~20-25 American, ~15-20 French AFVs

---

## Next Steps (Immediate)

### Step 1: Execute Database Migration
```bash
cd D:\north-africa-toe-builder
python scripts/battlegroup/database/execute_migration.py
```
- **Time**: 2-3 minutes
- **Output**: Backup created, tables archived, fresh tables ready
- **Verification**: Script prints comprehensive summary

### Step 2: Enter German Guns from Your Screenshots

You mentioned you have `Kursk German Gun1.png` and `Kursk German Gun2.png`.

**Option A: Use Template Script**
1. Open `scripts/battlegroup/manual_extraction/enter_guns_german.py`
2. Fill in gun data from your screenshots (13 examples already filled in)
3. Add remaining guns (17mm, 120mm, 170mm, 203mm, 210mm from Gun2.png)
4. Run: `python scripts/battlegroup/manual_extraction/enter_guns_german.py`

**Option B: Send Screenshots, I'll Fill Script**
1. You provide the gun table screenshots
2. I'll read the data from images and complete the Python script
3. You review and run the script

**Estimated Time**: 1-2 hours (depending on method)
**Output**: 31 verified German guns in database

### Step 3: British Guns (Next Session)
1. Screenshot British DataCards gun tables
2. Copy `enter_guns_german.py` → `enter_guns_british.py`
3. Update data structure with British guns
4. Run script

**Estimated Time**: 1.5-2 hours
**Output**: +20 British guns

### Step 4-8: Remaining Nations & Vehicles
Continue same pattern for:
- American guns (1.5-2 hrs)
- French guns (1 hr)
- German vehicles (2-3 hrs)
- British vehicles (2-3 hrs)
- American vehicles (1.5-2 hrs)
- French vehicles (1 hr)

### Step 9: Validation & Re-population
1. Validate all entries against screenshots (2-3 hrs)
2. Re-validate conversion formulas with clean data
3. Re-run HE/AP population on all 469 equipment items
4. QA check: No trucks with 300mm guns!

---

## Estimated Timeline

**Option 1: Intensive (3-4 days)**
- Day 1: Migration + German guns + British guns (4-5 hrs)
- Day 2: American guns + French guns + German vehicles (4-5 hrs)
- Day 3: British vehicles + American vehicles + French vehicles (5-6 hrs)
- Day 4: Validation + re-population + QA (3-4 hrs)
- **Total**: 16-20 hours

**Option 2: Steady (2-3 weeks)**
- 1-2 sessions per week, 2-3 hours per session
- More sustainable, allows for careful verification
- **Total**: Same 16-20 hours, spread over time

---

## Files Created This Session

### Documentation
- ✅ `DATA_QUALITY_AUDIT_2025-11-04.md` - Complete audit report
- ✅ `MANUAL_EXTRACTION_PLAN.md` - Full extraction strategy
- ✅ `SESSION_SUMMARY_2025-11-04_DataQuality.md` - This file

### Database Scripts
- ✅ `scripts/battlegroup/database/archive_scraped_tables.sql`
- ✅ `scripts/battlegroup/database/create_manual_extraction_tables.sql`
- ✅ `scripts/battlegroup/database/clear_corrupted_linkages.sql`
- ✅ `scripts/battlegroup/database/execute_migration.py` (master orchestrator)

### Manual Entry Scripts
- ✅ `scripts/battlegroup/manual_extraction/enter_guns_german.py` (template with 13 examples)

### Directory Structure Created
```
D:\north-africa-toe-builder\
├── DATA_QUALITY_AUDIT_2025-11-04.md
├── MANUAL_EXTRACTION_PLAN.md
├── SESSION_SUMMARY_2025-11-04_DataQuality.md
└── scripts\
    └── battlegroup\
        ├── database\
        │   ├── archive_scraped_tables.sql
        │   ├── create_manual_extraction_tables.sql
        │   ├── clear_corrupted_linkages.sql
        │   └── execute_migration.py
        └── manual_extraction\
            └── enter_guns_german.py
```

---

## Questions for User

1. **Database Migration**: Ready to execute `execute_migration.py`? (creates backup automatically)

2. **German Guns**:
   - Option A: You fill `enter_guns_german.py` from your screenshots?
   - Option B: Share screenshots, I'll complete the script?

3. **Approach Preference**:
   - Intensive (3-4 days)?
   - Steady (2-3 weeks)?

4. **Screenshot Workflow**: Do you want to:
   - Capture all screenshots first, then enter data?
   - OR capture + enter incrementally (one nation at a time)?

---

## Key Takeaways

✅ **Problem Identified**: Corrupted reference data affecting 52% of populated equipment

✅ **Root Cause Found**: Scraper failed due to inconsistent PDF table layouts

✅ **Solution Decided**: Manual screenshot extraction (only guarantee)

✅ **Infrastructure Ready**:
- Database migration scripts created
- Manual entry templates created
- Extraction plan documented
- Audit trail established

✅ **Next Action**: Execute migration, start with German guns

✅ **Timeline**: 16-20 hours total, flexible scheduling

✅ **Quality Guarantee**: 100% accurate, auditable, publication-ready

---

**Status**: Ready to proceed with manual extraction when you are!
