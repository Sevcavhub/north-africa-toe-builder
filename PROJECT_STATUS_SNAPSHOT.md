# Project Status Snapshot

**Date**: November 5, 2025
**Purpose**: Quick reference for new session agents - current reality without aspirational claims
**Last Updated By**: Documentation synchronization session

---

## 🎯 Current Phase Reality

**Phase 9B (BattleGroup Book Generation)**: ⏸️ **ON HOLD**

**Not "85% complete" - Currently in DATA QUALITY RECOVERY MODE**

---

## ⚠️ What's Actually Happening (November 2025)

### **The Discovery**
After building all infrastructure and generating initial content, quality review revealed:
- Scraped reference data from BattleGroup supplements/datacards/dispatches contained **errors and inconsistencies**
- All conversion formulas (armor, penetration, movement, HE) were **reverse-engineered FROM this flawed data**
- Therefore: All calculated equipment values are **assumed incorrect**
- Conclusion: **Cannot publish books with uncertain/incorrect equipment stats**

### **Current User Work**
User is manually re-extracting clean reference data:
1. ✅ **Canada's Crucible**: COMPLETE (84 vehicles, 26 guns, 5 aircraft, 105 army units)
   - Provides clean baseline validation dataset
2. ⏳ **British DataCards**: IN PROGRESS (User manually filling CSV templates)
   - 77 vehicles, 15 guns, 6 aircraft
   - OCR completed, data entry ongoing
3. 📋 **Additional Samples**: Reduced scope approach
   - Original plan: Extract ALL 17 supplements comprehensively
   - **New plan**: Just enough samples to validate conversion formulas
   - Full extraction = "nice to have later" (not required for MVP)

### **Database Schema Status**
- Location: `D:\north-africa-toe-builder\database\master_database.db`
- **Schema is evolving**: User discovering changes needed during manual extraction
- **Don't assume schema is frozen**: Check current state before writing queries

---

## ✅ What's Actually Complete

### **Infrastructure** (100% Complete)
- ✅ Database schema with 18 tables
- ✅ Conversion tools (armor, penetration, movement, HE calculators)
- ✅ Book generation framework (MDBook setup)
- ✅ Points/BR calculation system
- ✅ Generator toolkit (7 generators)

### **Book Content** (Non-Equipment Sections Complete)
- ✅ Historical chapters: 12 files, ~24,000 words
- ✅ Equipment special rules: 4 files, 1,543 lines
- ✅ Appendices: 12 files, 7,797 lines (zero placeholders, 181 citations)
- ✅ Tactical templates: 12 templates + 32 platoon/company files
- ✅ Scenarios: 45 historical scenarios with 95%+ parsing success
- ✅ MDBook builds: All 4 books generate HTML (134 files)

### **Phases 1-9A** (100% Complete)
- ✅ Phase 1-4: Database infrastructure (469 equipment items, 3 data sources)
- ✅ Phase 5: Equipment matching (469/469 items matched)
- ✅ Phase 5.5: Database normalization (4,669 → 1,129 unique items)
- ✅ Phase 6: Ground forces extraction (402/402 unit-quarters, 117 unique units)
- ✅ Phase 7: Air forces extraction (23 quarterly summaries, 9 quarters × 4 nations)
- ✅ Phase 8: Cross-linking (integrated during Phase 7)
- ✅ Phase 9A: WITW scenarios (369 scenarios, 91.8% coverage)

---

## ❌ What's Blocked / On Hold

### **Phase 9B Equipment Datacards** ⏸️ ON HOLD
- **Why**: Need clean reference data to validate conversion formulas
- **Can't publish**: Books with "None" weapons, "???" armor, uncertain penetration values
- **When unblocked**: After clean data validates formulas, regenerate all equipment stats

### **Forces/TO&E Tables** ❌ NOT STARTED
- **Status**: 0% complete (deferred)
- **What's needed**: Script to extract from Phase 6 unit JSONs (402 units)
- **Structure**: Corps → Division → Regiment → Battalion → Company hierarchy
- **Not blocking**: Can be added after equipment stats resolved

---

## 📚 Two Book Types (Important Distinction)

### **1. Project Books** (General Historical Books)
- **Purpose**: Summary chapters, appendices, TO&E tables
- **Status**: Can be worked on independently
- **Not blocked**: Don't depend on BattleGroup-specific work

### **2. BattleGroup Books** (Phase 9B Specific)
- **Purpose**: 4 battle books (Battleaxe, Crusader, Gazala, First Alamein)
- **Status**: ⏸️ ON HOLD pending clean reference data
- **Blocked**: Equipment datacards need validated formulas

---

## 🚫 What Agents Should NOT Do

### **Absolutely Do NOT**:
1. ❌ Work on Phase 9B book generation (equipment datacards blocked)
2. ❌ Run conversion formula scripts (need validation against clean data first)
3. ❌ Create new databases (master_database.db already exists)
4. ❌ Create duplicate folder structures (check existing patterns first)
5. ❌ Assume documentation is 100% accurate (it had contradictions - now being fixed)
6. ❌ Assume Phase 9B is "85-90% complete" (it's ON HOLD in recovery mode)

### **Why This Matters**:
Previous agents with partial/contradictory documentation awareness:
- Created duplicate databases
- Worked on wrong tasks
- Built on flawed reference data
- Left clutter from abandoned approaches
- Wasted tokens on incorrect assumptions

---

## ✅ What Agents CAN Do

### **Safe to Work On**:
1. ✅ Documentation updates (keep these 4 files in sync with timestamps)
2. ✅ Infrastructure improvements (non-Phase 9B)
3. ✅ Project Books (non-BattleGroup books) if requested
4. ✅ Validation/QA tasks
5. ✅ Schema exploration (to understand current state)
6. ✅ Script creation for Forces/TO&E tables (when requested)

### **Before Creating Anything New**:
1. Search for existing patterns (`*.db` files, folder structures)
2. Check recent git commits (what was done, where files were placed)
3. Read existing similar files (follow their pattern)
4. Verify with user if unsure

---

## 📊 Database Reality Check

### **Current Database**
- **Location**: `D:\north-africa-toe-builder\database\master_database.db`
- **Tables**: 18 tables (not 11 - expanded during Phase 9B)
- **Reference Data Quality**: Being rebuilt with clean manual extraction
- **Schema State**: Evolving (user discovering needed changes)

### **Key Tables**
- `equipment` - 469 WITW baseline items
- `equipment_battlegroup` - BattleGroup stats (need regeneration after formula validation)
- `bg_reference_vehicles` - Reference vehicles (being repopulated with clean data)
- `bg_reference_guns` - Reference guns (being repopulated with clean data)
- `units` - 117 unique units from Phase 6
- `wwiitanks_afv_data` - 612 AFVs with detailed specs
- `wwiitanks_gun_data` - 343 guns with penetration tables

### **Data Quality Status**
- Phase 1-7 data: ✅ Reliable (historical extraction from primary sources)
- Phase 9B reference data: ⏸️ Being rebuilt (scraped data had errors)
- Phase 9B calculated stats: ⚠️ Assumed incorrect (need regeneration)

---

## 📁 File Structure (Where Things Actually Are)

### **Documentation** (Root Directory)
- `PROJECT_SCOPE.md` - Complete project vision (UPDATED 2025-11-05)
- `START_HERE_NEW_SESSION.md` - Session workflow (UPDATED 2025-11-05)
- `PHASE_9B_SESSION_SUMMARY.md` - Session history (UPDATED 2025-11-05)
- `PHASE_9B_NEXT_STEPS.md` - Current tasks (UPDATED 2025-11-05)
- `CLAUDE.md` - Agent instructions with New Thread Protocol (UPDATED 2025-11-05)

### **Database**
- `database/master_database.db` - Single SQLite database (don't create duplicates!)

### **Phase 6 Unit Data** (Source for Forces/TO&E tables)
- `data/output/units/*.json` - 402 unit JSONs with complete TO&E data

### **BattleGroup Books** (Phase 9B)
- `books/battleaxe/book/src/` - Battleaxe book content
- `books/crusader/book/src/` - Crusader book content
- `books/gazala/book/src/` - Gazala book content
- `books/first_alamein/book/src/` - First Alamein book content

### **Scripts**
- `scripts/battlegroup/conversion/` - Conversion formula tools
- `scripts/battlegroup/book/` - Book generation scripts
- `scripts/battlegroup/manual_extraction/` - Manual extraction scripts (Canada's Crucible)

---

## 🔄 Recovery Timeline

**No fixed timeline** - depends on:
1. User completing British DataCards CSV filling (in progress)
2. Whether additional sample extractions needed for formula validation
3. Formula validation complexity
4. Equipment stat regeneration effort

**Don't promise timelines to user** - this is a quality recovery effort, not a feature sprint.

---

## 💡 Quick Start for New Agents

### **First 5 Minutes**:
1. Read this snapshot (you're doing it!)
2. Read `PROJECT_SCOPE.md` section on "Data Quality Discovery & Recovery Plan"
3. Read `START_HERE_NEW_SESSION.md` "CURRENT STATUS: Phase 9B ON HOLD" section
4. Understand: We're in RECOVERY MODE, not "finishing the last 10%"

### **Ask User**:
- "What would you like to work on today?"
- "Is there anything specific you need help with while Phase 9B is on hold?"
- "Should I help with Project Books, documentation, or something else?"

### **Don't Assume**:
- Phase 9B is nearly done (it's on hold)
- Equipment stats are correct (they're assumed incorrect)
- Schema is frozen (it's evolving)
- All documentation agrees (it had contradictions - we just fixed them)

---

## 📝 Session Management

### **During Your Session**:
- Update relevant .md files with progress
- Add timestamps to all updates (YYYY-MM-DD or "November 5, 2025")
- Keep PROJECT_SCOPE.md, PHASE_9B_SESSION_SUMMARY.md, PHASE_9B_NEXT_STEPS.md in sync

### **Before Committing**:
- Verify no contradictions between documentation files
- Check that status claims are realistic (not aspirational)
- Ensure timestamps are current

---

**Remember**: This project has solid foundations (Phases 1-8 complete, infrastructure built, content created). We're not starting over - we're just validating and correcting equipment stats before publication. The work is good; it just needs clean reference data to finish properly.

**Updated**: November 5, 2025 - Documentation synchronization complete
