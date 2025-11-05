# Phase 9B: BattleGroup Books - Next Steps

**Date**: November 4, 2025
**Status**: ✅ BG Reference Data Repopulation IN PROGRESS - Canada's Crucible COMPLETE
**Last Update**: ✅ Canada's Crucible extraction complete (84 vehicles, 26 guns, 5 aircraft, 105 units, 4 scenarios)
**Database Status**: Manual extraction replacing failed PDF scraper - systematic screenshot-based workflow
**Current Task**: DataCards supplements next (5 supplements, vehicles/guns QRS cards only)

---

## 🎉 CANADA'S CRUCIBLE EXTRACTION 100% COMPLETE (November 4, 2025)

### ✅ COMPLETED: Full Manual Extraction via Screenshots

**What Was Accomplished**:
- ✅ **41 Python extraction scripts** - Systematic data entry from screenshots
- ✅ **German forces** - 63 vehicles, 16 guns, 2 aircraft, 58 army list units, 9 defences
- ✅ **Canadian forces** - 21 vehicles, 10 guns, 3 aircraft, 47 army list units, 13 defences
- ✅ **4 complete scenarios** - Black Sabbath, Norrey, Surrounded (with hierarchical force structures)
- ✅ **3 sample maps** - Scenario battlefield layouts

**Database Tables Populated**:
- `BG_Reference_Vehicles` (84 vehicles with stats, armor, weapons, movement)
- `BG_Reference_Guns` (26 guns with HE/AP values, penetration)
- `BG_Reference_Aircraft` (5 aircraft with role, hits, weaponry)
- `BG_Reference_ArmyList_Examples` (105 units with points, BR, composition)
- `BG_Reference_Defences` (22 defensive structures)
- `BG_Scenario_Army_Lists` (4 scenarios)
- `BG_Scenario_Forces` (8 forces total)
- `BG_Scenario_Units` (54 units with deployment details)
- `BG_Sample_maps` (4 maps)

**Git Commit**:
- `0aae6c62` - feat(manual-extraction): Complete Canada's Crucible BG reference data extraction
- 42 files changed, 8,448 insertions

**Extraction Pattern Established**:
1. Read screenshot PNG file with Read tool
2. User approves with "approve" or "next"
3. Create Python script with data dictionaries matching screenshot
4. Insert into appropriate BG_Reference_* tables
5. Handle UNIQUE constraints (skip duplicates)
6. Verify with COUNT queries and summary output

---

## 📋 NEXT: DataCards Supplements (5 Supplements)

**Location**: `D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Suppliment Equipment Screen Captures`

**Important Notes**:
- DataCards are QRS (Quick Reference Sheet) cards, NOT full equipment lists
- Format: Top table = vehicle stats, bottom section = integrated gun stats (if applicable)
- Includes: Armored vehicles, soft-skin vehicles, aircraft cards
- British8.png has Small Arms Rate of Fire table - create NEW reference table for this
- NO army lists, NO maps, NO scenarios in DataCards supplements

**DataCards To Process** (in order):
1. ✅ Battlegroup-DataCards-British (8 PNG files: Britsh1.png, Britsh2.png, British3-8.png)
2. ⏳ Battlegroup-DataCards-Early-German
3. ⏳ Battlegroup-DataCards-French-Polish-Romanian-Hungarian
4. ⏳ Battlegroup-DataCards-Soviets
5. ⏳ Battlegroup-DataCards-US

**British DataCards Files**:
- Britsh1.png (typo in filename)
- Britsh2.png (typo in filename)
- British3.png
- British4.png
- British5.png
- British6.png
- British7.png
- British8.png (includes Small Arms Rate of Fire table - needs new table creation)

---

## 📋 REMAINING SUPPLEMENTS (After DataCards)

**Full Supplements** (Army Lists, Maps, Vehicles, Guns, Aircraft):
1. Battlegroup-Dispatches-1 (6 extraction types)
2. Battlegroup-Dispatches-2 (6 extraction types)
3. BG-Dispatches-3 (6 extraction types)
4. Battlegroup-Fall-of-the-Reich-Full (6 extraction types)
5. Battlegroup-Kursk (6 extraction types)
6. Battlegroup-Market-Garden-Army-List (6 extraction types)
7. Battlegroup-Market-Garden-Scenarios (6 extraction types)
8. Battlegroup-Overlord-Army-Lists (6 extraction types)
9. Battlegroup-Overlord-D-Day-scenarios (6 extraction types)
10. Battlegroup-Torch-Mission (6 extraction types)
11. Battlegroup-Wacht-Am-Rhein (6 extraction types)
12. Battlegroup-Westwall (6 extraction types)
13. BG Army lists (PDF) v5 (6 extraction types)

**Total Remaining Tasks**: 10 DataCards + 78 Full Supplement = 88 extraction tasks

---

## 🔄 EXTRACTION WORKFLOW (Standard Process)

### Step 1: Identify Screenshot Category
- Read PNG file with Read tool
- Identify type: Vehicle, Gun, Aircraft, Army List, Map, Scenario, Defence

### Step 2: Create Python Extraction Script
```python
#!/usr/bin/env python3
"""
Extract [Type] from [Supplement] supplement
Populates [Table] table
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
SCREENSHOT_FILE = "D:/north-africa-toe-builder/Resource Documents/.../filename.png"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Data dictionaries matching screenshot
    items = [
        {
            'field1': 'value1',
            'field2': 'value2',
            # ... all fields from screenshot
            'source_supplement': 'Battlegroup-[Name]',
            'source_image_location': SCREENSHOT_FILE,
            'extraction_method': 'manual_screenshot',
            'verified_by': 'claude'
        },
    ]

    # Insert with try/except for UNIQUE constraints
    for item in items:
        try:
            cursor.execute('''INSERT INTO [Table] (...) VALUES (?, ?, ...)''', (...))
            print(f"  [OK] Inserted: {item['name']}")
        except sqlite3.IntegrityError as e:
            print(f"  [SKIP] {item['name']}: {e}")

    conn.commit()

    # Verification queries
    cursor.execute('SELECT COUNT(*) FROM [Table] WHERE ...')
    print(f'Total items: {cursor.fetchone()[0]}')

    conn.close()
```

### Step 3: Execute and Verify
```bash
cd "D:/north-africa-toe-builder"
python scripts/battlegroup/manual_extraction/extract_[name].py
```

### Step 4: Mark Todo Complete
Update todo list when supplement section is 100% complete

---

## 🗄️ DATABASE TABLES REFERENCE

### Vehicles & Equipment
- `BG_Reference_Vehicles` - Armor values, movement, weapons, points, BR, special rules
- `BG_Reference_Guns` - HE dice, AP penetration at ranges, caliber
- `BG_Reference_Aircraft` - Role, hits, weaponry (cannons, bombs, rockets)

### Army Lists
- `BG_Reference_ArmyList_Examples` - Unit name, category, composition, points, BR, transport, rules, upgrades

### Defences & Terrain
- `BG_Reference_Defences` - Name, category, points, BR, special rules
- `BG_Sample_maps` - Map name, image location, scenario title, size

### Scenarios
- `BG_Scenario_Army_Lists` - Scenario name, size, source supplement
- `BG_Scenario_Forces` - Force name, side (Allied/Axis/Neutral), nation, BR total, officers
- `BG_Scenario_Units` - Unit designation, equipment, modifiers, deployment notes

### Organizations (Extracted from Vehicles)
- `BG_Reference_Organizations` - Organizational units (Brigade HQ, Battalion HQ, etc.)

---

## 🎯 SESSION HANDOFF GUIDE

### Quick Start for New Session
1. Check current location in todo list (6 completed, 88 pending)
2. Next task: British DataCards extraction (8 PNG files)
3. Review extraction workflow above
4. Start with Britsh1.png (typo in filename)

### Key Files to Know
- Manual extraction scripts: `scripts/battlegroup/manual_extraction/*.py`
- Screenshots directory: `Resource Documents/Battlegroup Game/Suppliment Equipment Screen Captures/`
- Database: `database/master_database.db`
- Todo list: See TodoWrite tool (94 tasks total)

### Important Context
- PDF scraper failed - manual screenshot extraction is the solution
- Canada's Crucible = proof of concept (100% complete)
- DataCards are different: QRS cards with integrated vehicle+gun data
- British8.png needs NEW table for Small Arms Rate of Fire

### Git Workflow
```bash
# When ready to commit
git add scripts/battlegroup/manual_extraction/
git commit -m "feat(manual-extraction): [Supplement] extraction complete"
git push origin main
```

### Database Schema Reference
See `scripts/battlegroup/database/create_manual_extraction_tables.sql` for full schema

---

## 📊 PROGRESS TRACKING

### Completed (1 supplement, 6 tasks)
- ✅ Battlegroup-Canadas-Crucible (Army Lists, Maps, Vehicles, Guns, Aircraft, Scenarios)

### In Progress (0 supplements)
- None currently

### Pending (18 supplements, 88 tasks)
- ⏳ DataCards supplements (5 supplements, 10 tasks)
- ⏳ Full supplements (13 supplements, 78 tasks)

### Total Extraction Task Count
- **6 completed** + **88 pending** = **94 total extraction tasks**

---

## 🔗 RELATED DOCUMENTS
- `PROJECT_SCOPE.md` - Overall project vision and phases
- `PHASE_9B_SESSION_SUMMARY.md` - Detailed session history
- `CLAUDE.md` - Project instructions for Claude Code
- `START_HERE_NEW_SESSION.md` - Session management protocol

---

**Last Updated**: November 4, 2025 - End of Canada's Crucible extraction session
**Next Session**: British DataCards extraction (8 PNG files)
**Commit**: 0aae6c62 - Manual extraction infrastructure complete
