# Schema Transformation Plan - Unify All 75 Units

**Date:** 2025-10-12
**Scope:** Transform ALL 75 unit JSON files to unified schema standard
**Status:** PROPOSED - Awaiting approval

---

## Problem Statement

We have **75 unit JSON files** created across multiple autonomous sessions with **inconsistent schemas**:

### Current State (Discovered Issues)

```
Total JSON files: 75
Validated by script: 69
Not yet validated: 6 (possibly different naming or location)

Schema inconsistencies found:
- 5 units using nested structure (unit_identification.*)
- 1 unit using old commander structure (commander_name vs commander.name)
- Multiple units with partial unified schema compliance
- Unknown number with inconsistent field naming
```

### Why This Matters

**Problem:** Units created in different sessions may have:
- Different field names (`commander_name` vs `commander.name`)
- Different nesting levels (top-level vs `unit_identification.*`)
- Missing required fields (`organization_level`, `validation`)
- Inconsistent data structures across the codebase

**Impact:**
- Code that works for one unit format breaks for another
- Database extraction scripts need dual-path logic
- Future agents don't know which format to expect
- Manual inspection required to know which schema a unit uses

**Goal:** **ONE unified schema standard** for all 75 units

---

## Proposed Approach

### Option 1: Enhanced Batch Script (RECOMMENDED)

**Create:** `scripts/unify-all-schemas.js`

**What it does:**
1. Scans ALL JSON files (not just validation failures)
2. For each unit:
   - Detects current schema structure
   - Transforms to unified schema
   - Validates after transformation
   - Creates backup before modification
3. Generates transformation report
4. Re-runs validation to confirm 100% compliance

**Advantages:**
- Fast (runs in seconds)
- Deterministic (same transformation logic for all units)
- Auditable (full before/after report)
- Automated (no manual intervention)

**Disadvantages:**
- Script-based (not AI-driven, fixed rules)
- May miss edge cases

### Option 2: AI Agent Transformation (ALTERNATIVE)

**Create:** New agent `schema_transformer` in agent_catalog.json

**What it does:**
1. Reads each JSON file
2. Uses AI to understand current structure
3. Intelligently maps fields to unified schema
4. Handles edge cases and ambiguities
5. Validates output

**Advantages:**
- Intelligent (can handle complex transformations)
- Adaptive (can deal with unexpected structures)
- Documents reasoning for each transformation

**Disadvantages:**
- Slower (75 AI calls)
- Uses API tokens
- Non-deterministic (AI may transform differently each time)
- Harder to audit

---

## Recommended Solution: Option 1 (Enhanced Script)

### Implementation Plan

**Phase 1: Discovery (5 minutes)**
```bash
node scripts/discover-schema-variations.js
```
- Scans all 75 JSON files
- Catalogs which structures are used
- Reports field name variations
- Identifies missing required fields

**Phase 2: Unified Transformation (10 minutes)**
```bash
node scripts/unify-all-schemas.js [--dry-run]
```

Transforms ALL units to unified schema:

**Transformations Applied:**

1. **Structure Normalization**
   ```javascript
   // BEFORE (nested)
   {
     "unit_identification": {
       "nation": "italian",
       "quarter": "1941-Q2",
       "unit_designation": "132ª Ariete"
     }
   }

   // AFTER (unified)
   {
     "nation": "italian",
     "quarter": "1941-Q2",
     "unit_designation": "132ª Ariete"
   }
   ```

2. **Commander Structure**
   ```javascript
   // BEFORE (flat)
   {
     "command": {
       "commander_name": "Ettore Baldassarre",
       "commander_rank": "Generale di Divisione"
     }
   }

   // AFTER (nested object)
   {
     "command": {
       "commander": {
         "name": "Ettore Baldassarre",
         "rank": "Generale di Divisione"
       }
     }
   }
   ```

3. **Personnel Structure**
   ```javascript
   // BEFORE (nested in personnel_summary)
   {
     "personnel_summary": {
       "total_personnel": 6750,
       "officers": 340
     }
   }

   // AFTER (top-level)
   {
     "total_personnel": 6750,
     "officers": 340
   }
   ```

4. **Equipment Structure**
   ```javascript
   // BEFORE (in equipment_summary)
   {
     "equipment_summary": {
       "tanks": { "total": 123 }
     }
   }

   // AFTER (top-level)
   {
     "tanks": { "total": 123 }
   }
   ```

5. **Validation Structure**
   ```javascript
   // BEFORE (data_quality or metadata)
   {
     "data_quality": {
       "confidence_score": 84,
       "primary_sources": [...]
     }
   }

   // AFTER (validation)
   {
     "validation": {
       "confidence": 84,
       "source": [...],
       "known_gaps": [...]
     }
   }
   ```

**Phase 3: Validation (5 minutes)**
```bash
npm run validate
```
- Re-run validation on all 75 units
- Confirm 100% compliance
- Generate final report

**Phase 4: Database Re-sync (10 minutes)**
```bash
node scripts/resync-database.js
```
- Re-extract data from transformed JSON files
- Update database with corrected structures
- Verify all 63 units match unified schema

---

## Expected Outcomes

### Before Transformation
```
✅ Passed validation: 51/69 (73.9%)
❌ Failed validation: 2/69 (2.9%)
⚠️ Warnings: 16/69 (23.2%)
🔍 Not validated: 6 files

Schema structures:
- Unified schema: ~51 units
- Nested structure: 5 units
- Mixed/hybrid: ~13 units
- Unknown: 6 units
```

### After Transformation
```
✅ Passed validation: 75/75 (100%)
❌ Failed validation: 0/75 (0%)
⚠️ Warnings: 0-5/75 (data quality only, not schema)

Schema structures:
- Unified schema: 75 units ✅
- All other structures: 0 units ✅
```

---

## Safety Measures

1. **Full Backup** - All 75 original files backed up before transformation
2. **Dry-Run Mode** - Test transformation without modifying files
3. **Validation Gating** - Only save if transformation produces valid output
4. **Rollback Plan** - Can restore from backup if issues found
5. **Audit Trail** - Complete report of all transformations applied

---

## Time Estimate

| Phase | Time | Activity |
|-------|------|----------|
| 1. Discovery | 5 min | Scan and catalog structures |
| 2. Script Creation | 30 min | Write unify-all-schemas.js |
| 3. Dry-Run Test | 5 min | Test transformation logic |
| 4. Actual Transformation | 10 min | Apply to all 75 units |
| 5. Validation | 5 min | Verify 100% compliance |
| 6. Database Re-sync | 10 min | Update database |
| **Total** | **~65 minutes** | **Complete standardization** |

---

## Deliverables

1. **scripts/discover-schema-variations.js** - Discovery tool
2. **scripts/unify-all-schemas.js** - Transformation script
3. **data/SCHEMA_TRANSFORMATION_REPORT.md** - Full audit trail
4. **75 transformed JSON files** - All compliant with unified schema
5. **Updated database** - Re-synced with corrected data

---

## Alternative: AI Agent Approach

If you prefer the AI agent approach (Option 2), we would:

1. Create `schema_transformer` agent in agent_catalog.json
2. Run it through orchestrator: `npm run agent -- schema_transformer`
3. Process each unit individually with AI reasoning
4. Generate detailed transformation reports

**Estimated time:** 2-3 hours (75 units × ~2 minutes each)
**Cost:** ~75 API calls

---

## Recommendation

**Proceed with Option 1 (Enhanced Script)** because:
- ✅ Faster (65 minutes vs 2-3 hours)
- ✅ Free (no API costs)
- ✅ Deterministic (consistent transformations)
- ✅ Easier to audit
- ✅ Can run dry-run first to verify logic

**Decision Point:** Should we proceed with automated script transformation, or do you prefer the AI agent approach?
