# Final Extraction Plan - Phase 6 Completion

**Generated**: 2025-10-26
**Status**: ✅ VERIFIED - Ready for auto:continuous execution
**Remaining Combat Units**: 3 divisions

---

## 📊 Current State (Verified)

- ✅ **Seed file**: 411 unit-quarters total
- ✅ **Completed**: 372 unit-quarters (90.5%)
- ✅ **Remaining**: 39 unit-quarters
  - **3 combat divisions** (ready for extraction)
  - **34 aggregates** (corps/armies - extract after divisions)
  - **2 discrepancy** (under investigation)

---

## 🎯 Combat Divisions to Extract (Non-Aggregates Only)

### Extraction Order (Chronological + Echelon):

**1. british_1942q4_44th_infantry_division**
- Nation: British
- Quarter: 1942-Q4
- Designation: 44th Infantry Division
- Type: Infantry Division
- Historical Context: Tunisia operations, Second Battle of El Alamein follow-up
- Sources: British Army Lists, 1942 War Diaries

**2. british_1942q4_51st_highland_division**
- Nation: British
- Quarter: 1942-Q4
- Designation: 51st Highland Division (Highland)
- Type: Infantry Division
- Historical Context: El Alamein veteran, pursuit to Tunisia
- Sources: 51st Highland Division War Diary, Operation Supercharge

**3. british_1943q1_44th_infantry_division**
- Nation: British
- Quarter: 1943-Q1
- Designation: 44th Infantry Division
- Type: Infantry Division
- Historical Context: Tunisia Campaign, disbanded January 31, 1943
- Sources: British Army Lists, Tunisia operations records
- **Note**: Last quarter before disbandment

---

## 🚀 Auto:Continuous Execution Plan

### Command to Run:

```bash
/auto-continuous
```

OR via npm:

```bash
npm run auto:continuous
```

### What Will Happen:

1. **Batch 1** (3 units):
   - Launches 3 parallel Task tool agents
   - Each agent extracts 1 division using approved subagents
   - Schema: v3.1.0 (tiered extraction with supply/weather)
   - Automatic checkpoint after completion
   - Estimated time: ~1.5-2 hours total

2. **After Combat Divisions Complete**:
   - Progress: 375/411 (91.2%)
   - Work queue will show 34 aggregates remaining
   - Ready to extract corps and armies (bottom-up aggregation)

3. **Session Management**:
   - Auto:continuous handles checkpoints automatically
   - No manual `session:end` needed
   - Progress saved after each batch

---

## ⚙️ Extraction Workflow (Per Unit)

Each specialized extraction agent will:

1. **Research Phase** (~10-15 mins):
   - Search PDFs for unit TO&E data
   - Identify equipment variants and quantities
   - Document combat participation evidence

2. **Extraction Phase** (~10-15 mins):
   - Extract organizational structure (SCM hierarchy)
   - Extract equipment with variant-level detail
   - Extract supply/logistics data (fuel, ammo, water)
   - Extract weather/environment conditions

3. **Chapter Generation** (~5-10 mins):
   - Professional MDBook chapter
   - Historical context and sources
   - Equipment analysis
   - Tactical employment notes

4. **Validation** (~2-3 mins):
   - Schema v3.1.0 compliance check
   - Tier assignment (1-4 based on completeness)
   - Save to canonical location

**Total per division**: ~30-40 minutes

---

## 📋 After Extraction - Next Steps

### 1. Verify Combat Divisions Complete

```bash
npm run checkpoint
```

Expected output:
- 375/411 units complete (91.2%)
- All 3 divisions pass validation
- Chapters generated

### 2. Begin Aggregate Extraction (34 units)

**Corps** (22 units):
- Aggregate subordinate division data
- Roll up equipment totals
- Command structure
- ~15-20 mins each

**Armies** (12 units):
- Aggregate corps + division data
- Theater-level command
- Strategic supplies
- ~20-25 mins each

**Estimated time for all aggregates**: ~10-12 hours

### 3. Phase 6 Complete

When all 411 units done:
- ✅ Ground forces extraction COMPLETE
- ✅ Ready for Phase 7 (Air Forces)
- ✅ Ready for Phase 8 (Cross-linking)
- ✅ Ready for Phase 9 (Scenario generation)

---

## 🔧 Technical Details

### Approved Subagents:

All extraction uses the specialized extraction subagent:
- **Type**: `general-purpose` (has access to all tools)
- **Prompt**: Detailed unit extraction instructions
- **Tools**: MCP PDF reading, filesystem operations, grep/glob
- **Schema**: v3.1.0 with tiered extraction

### Canonical Output Locations:

- Units: `data/output/units/{canonical_id}_toe.json`
- Chapters: `data/output/chapters/chapter_{canonical_id}.md`

### Validation Requirements:

Each unit must pass:
1. ✅ JSON file exists in canonical location
2. ✅ Chapter file exists in canonical location
3. ✅ Schema v3.1.0 validation (no critical errors)

---

## 📦 Backup Status

**Pre-extraction backup**: ✅ COMPLETE
- Location: `backups/phase1-6_backup_2025-10-26_085050/`
- Size: 3.9 MB compressed
- Contains: 372 completed units + all state files
- Can restore if needed

---

## ✅ Verification Checklist

- [x] Seed file verified (411 unit-quarters)
- [x] WORKFLOW_STATE verified (372 completed, 90.5%)
- [x] Work queue regenerated with canonical IDs
- [x] Remaining units identified (3 combat, 34 aggregates)
- [x] Canonical naming fixed (91 files renamed)
- [x] Complete backup created
- [x] Auto:continuous command ready
- [ ] **Ready to execute** ← YOU ARE HERE

---

## 🚦 Execute When Ready

To begin final combat division extraction:

```bash
/auto-continuous
```

**Expected completion**: 1.5-2 hours for 3 divisions

**Progress after**: 375/411 (91.2%)

**Next**: Aggregate extraction (corps + armies)

---

**✅ SYSTEM VERIFIED - READY FOR FINAL EXTRACTION**
