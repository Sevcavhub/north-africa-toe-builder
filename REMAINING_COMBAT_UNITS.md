# Remaining Combat Units to Extract

**Generated**: 2025-10-26
**Total Remaining**: 3 divisions (0 brigades)
**Status**: Ready for auto:continuous extraction

---

## 🎯 Combat Units Only (Non-Aggregates)

### 1942-Q4 (2 units)

1. **BRITISH - 44th Infantry Division**
   - Quarter: 1942-Q4
   - Type: Infantry Division
   - Canonical ID: `british_1942q4_44th_infantry_division`
   - Historical Context: North Africa Campaign, Tunisia operations

2. **BRITISH - 51st Highland Division**
   - Quarter: 1942-Q4
   - Type: Infantry Division
   - Canonical ID: `british_1942q4_51st_highland_division`
   - Historical Context: El Alamein, Tunisia operations

### 1943-Q1 (1 unit)

3. **BRITISH - 44th Infantry Division**
   - Quarter: 1943-Q1
   - Type: Infantry Division
   - Canonical ID: `british_1943q1_44th_infantry_division`
   - Historical Context: Tunisia Campaign

---

## 📊 Aggregate Units (Extract After Combat Units)

**Note**: 34 aggregate units (corps and armies) will be extracted AFTER all combat divisions are complete per bottom-up aggregation policy.

- **Corps**: 22 units (1942-Q3 through 1943-Q2)
- **Armies**: 12 units (1942-Q1 through 1943-Q2)

These aggregates roll up data from their subordinate divisions and should only be extracted once all division data is available.

---

## ✅ Extraction Queue for Auto:Continuous

**Priority Order** (Chronological within echelon):
1. british_1942q4_44th_infantry_division
2. british_1942q4_51st_highland_division
3. british_1943q1_44th_infantry_division

**Extraction Method**:
- Use `/auto-continuous` command
- Batch size: All 3 units (single continuous run)
- Estimated time: ~1.5-2 hours (30-40 mins per division)
- Schema: v3.1.0 with tiered extraction
- Agents: Specialized extraction subagents (per approved workflow)

---

## 🔧 Post-Extraction Tasks

After these 3 divisions are complete:

1. ✅ Run checkpoint to verify all 3 units
2. ✅ Progress will be 375/411 (91.2%)
3. ⏭️ Begin aggregate extraction (34 corps/armies)
4. 🎯 Phase 6 complete when all 411 units done

---

## 📝 Verification

- ✅ Verified against seed file: `projects/north_africa_seed_units_COMPLETE.json`
- ✅ Cross-checked with WORKFLOW_STATE.json (372 completed)
- ✅ Remaining count matches: 411 total - 372 complete = 39 pending
  - 3 combat divisions
  - 34 aggregates (corps/armies)
  - 2 possible duplicates (needs investigation)

---

**Ready to run:** `/auto-continuous` with these 3 units
