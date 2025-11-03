# Database Normalization: Start Here for Next Session

**Last Updated**: 2025-11-02
**Current Status**: Phase 2 Complete - Ready for User Decisions & Phase 3 Execution

---

## 🎯 Current Status

### ✅ Completed
- **Phase 1**: Discovery & Analysis (READ-ONLY) - COMPLETE
- **Phase 2**: Prioritization & Planning - COMPLETE
- **Database Backup**: Created (9.1 MB) at `database/master_database.db.backup-20251102-pre-normalization`

### ⏳ Next Steps
- **USER DECISIONS**: 23 WITW ID collisions require manual decisions
- **Phase 3**: Remediation Execution (with user approval)
- **Phase 4**: Validation & Certification

---

## 📋 Quick Summary

### What Was Done

**Phase 1** (Discovery & Analysis):
- Analyzed 42 database tables (~21,000 records)
- Ran 5 detection capabilities (duplicates, normalization, naming, constraints, denormalization)
- Generated 8 comprehensive reports
- **Found**: 58 WITW ID collisions, 4 aircraft-as-tanks, 101 name mismatches, 467 null equipment_types, 112 empty equipment_guns

**Phase 2** (Planning):
- Created detailed remediation plan (13,500+ words)
- Defined 3-phase execution strategy (2A/2B/2C)
- Generated 23 user decision prompts for ambiguous collisions
- Estimated 13-16 hours total remediation time

### Critical Findings

| Issue | Records | Severity | Blocks |
|-------|---------|----------|--------|
| WITW ID collisions | 169 | 🔴 CRITICAL | Phase 10 exports |
| Aircraft-as-tanks | 4 | 🔴 CRITICAL | Data integrity |
| Name mismatches | 101 | 🟡 HIGH | Phase 9B datacards |
| Empty equipment_guns | 112 | 🟡 HIGH | Phase 9B datacards |
| NULL equipment_type | 467 | 🟡 HIGH | Categorization |
| Orphaned FKs | 953 | 🟡 HIGH | unit_equipment |

---

## 📁 Key Files

### Analysis Reports (Phase 1)
- `DATA_QUALITY_BASELINE.md` - Executive summary with metrics
- `constraint_violations.json` - Detailed violation catalog
- `naming_inconsistencies.json` - Name variant analysis
- `duplicate_analysis.json` - Duplicate detection results
- `WITW_COLLISION_DETAILS.md` - Comprehensive collision breakdown
- `PHASE1_DISCOVERY_COMPLETE.md` - Phase 1 summary

### Planning Documents (Phase 2)
- `REMEDIATION_PLAN.md` - Complete execution plan (13,500+ words)
- `WITW_COLLISION_USER_DECISIONS.md` - 23 collisions requiring user decisions

### Agent Specifications
- `agents/database_normalization_agent.json` - Agent capabilities & config
- `agents/AGENT_INSTRUCTIONS_DATABASE_NORMALIZATION.md` - Complete instructions

### Context Documents
- `PHASE_9B_STEP7_DATA_QUALITY_CRISIS.md` - Original issue documentation
- `temp_check_witw_collisions.py` - Collision detection script

### Database
- `database/master_database.db` - Master database (9.1 MB)
- `database/master_database.db.backup-20251102-pre-normalization` - Pre-normalization backup

---

## 🚀 How to Resume Work

### For Next Session (Recommended Path)

**Step 1: Review Current State** (5 minutes)
```bash
# Check git status
git status

# Read this file
# You're already here!

# Review executive summary
cat DATA_QUALITY_BASELINE.md
```

**Step 2: Make User Decisions** (30-60 minutes)
```bash
# Open decision document
code WITW_COLLISION_USER_DECISIONS.md

# Review 23 collision cases
# Choose option A/B/C/D for each
# Document your choices in the file
```

**Step 3: Launch Phase 3 Execution**
```bash
# After user decisions are complete, launch the agent
# The agent will read your decisions and execute remediation

# Command to resume agent:
claude --dangerously-skip-permissions
```

**Agent prompt**:
```
You are the Database Normalization Agent. Resume work by executing Phase 3: Remediation.

Read these files first:
1. DATABASE_NORMALIZATION_START_HERE.md (this file - you're here)
2. REMEDIATION_PLAN.md (execution plan)
3. WITW_COLLISION_USER_DECISIONS.md (user decisions)

Execute Phase 3 according to REMEDIATION_PLAN.md:
- Phase 3A: Critical fixes (WITW collisions using user decisions)
- Phase 3B: High priority (name variants, equipment_guns, equipment_type)
- Phase 3C: Medium priority (BattleGroup duplicates)

Work autonomously with transaction safety, audit logging, and rollback scripts.
Report back after each phase completes.
```

### Alternative: Quick Fix for Phase 9B Only

If you want to unblock Phase 9B book datacard generation immediately:

**Quick Fix Tasks** (2-3 hours):
1. Fix A10/A13 Cruiser categorization (add 'cruiser' keyword)
2. Manually populate equipment_guns for A9/A10/A13 tanks
3. Resume book datacard generation

**Then do full normalization later**.

See: `scripts/battlegroup/book/generate_book_datacards.py:271` for categorization fix.

---

## 🎯 Phase 3 Execution Plan (When Ready)

### Phase 3A: Critical Fixes (Day 1, 4-5 hours)

**Batch 1**: Aircraft-as-tanks (4 records)
- Auto-fix: Set witw_id=NULL for Crusader I + 3 Shermans
- Time: 15 minutes
- Rollback: SQL provided

**Batch 2**: Multi-category collisions (~25 collisions)
- Auto-resolve using decision tree (semantic + category matching)
- Time: 1-2 hours
- Rollback: SQL per collision

**Batch 3**: User-decided collisions (23 collisions)
- Execute based on user decisions in WITW_COLLISION_USER_DECISIONS.md
- Time: 1-2 hours
- Rollback: SQL per collision

**Batch 4**: Audit infrastructure
- Create normalization_audit table
- Create witw_collision_resolutions table
- Create equipment_name_variants table
- Time: 30 minutes

### Phase 3B: High Priority (Days 1-2, 6-7 hours)

**Task 1**: Name variant mapping (3-4 hours)
- Parse all equipment, bg_reference_vehicles names
- Fuzzy matching (Levenshtein, token-based)
- Populate equipment_name_variants table
- Generate equipment_name_mapping.json

**Task 2**: equipment_guns population (2-3 hours)
- Parse bg_reference_vehicles.weapons JSON
- Match names using variants table
- Create 150-200 equipment_guns linkages
- Focus on tanks first (A9/A10/A13 priority)

**Task 3**: equipment_type inference (1 hour)
- Rules-based UPDATE from category field
- Target: 95%+ population

**Task 4**: Orphaned FK investigation (2-3 hours)
- Analyze why 953/953 unit_equipment have NULL equipment_id
- Generate orphaned_fk_analysis.md with recommendations

### Phase 3C: Medium Priority (Days 2-3, 2-3 hours)

**Task 1**: BattleGroup duplicate analysis
- Review 154 duplicate groups
- Categorize as intentional/error
- Generate bg_duplicate_resolution.json

---

## 🛡️ Safety Features

- ✅ Database backup created (20251102)
- ✅ All changes use BEGIN TRANSACTION / COMMIT
- ✅ Audit logging for every modification
- ✅ Rollback SQL generated per batch
- ✅ Validation queries before COMMIT
- ✅ Batch size: 50-100 records max

---

## 📊 Expected Quality Improvement

| Metric | Before | After Phase 3 | Improvement |
|--------|--------|---------------|-------------|
| WITW ID collisions | 58 | ~20-25 | 57-65% reduction |
| Aircraft-as-tanks | 4 | 0 | 100% fixed |
| equipment_type populated | 0.4% | 95%+ | 237x improvement |
| equipment_guns linkages | 0% | 70-90% | New capability |
| Name variant mapping | 0 | 100+ | Enables lookups |

**Phase 9B Status**: ✅ UNBLOCKED after Phase 3B completion

---

## 🔍 How to Check Status

### Database Collisions (Current State)
```bash
python temp_check_witw_collisions.py
```

### Equipment Table Stats
```bash
sqlite3 database/master_database.db "SELECT
  COUNT(*) as total,
  COUNT(witw_id) as has_witw_id,
  COUNT(equipment_type) as has_type
FROM equipment;"
```

### BattleGroup Name Mismatches
```bash
sqlite3 database/master_database.db "SELECT COUNT(*)
FROM equipment e
LEFT JOIN bg_reference_vehicles brv ON LOWER(e.name) = LOWER(brv.name)
WHERE e.category IN ('tanks', 'main_tanks') AND brv.name IS NULL;"
```

---

## 📞 Agent Contact Info

**Agent**: Specialist Data Cleaning & Normalization Agent v2.0.0
**Spec File**: `agents/database_normalization_agent.json`
**Instructions**: `agents/AGENT_INSTRUCTIONS_DATABASE_NORMALIZATION.md`
**Architecture**: 5-capability professional data quality enforcement

**Capabilities**:
1. Exact Duplicate Detection
2. Normalization Issue Detection
3. Denormalization Detection
4. Naming Inconsistency Detection
5. Constraint Violation Detection

---

## 🎓 Context for New Users

### What is this project?
North Africa TO&E (Table of Organization & Equipment) Builder - generates wargaming scenarios with historical data.

### What's the database issue?
Equipment data was imported from 4 complementary sources (WITW, OnWar, WWIITANKS, BattleGroup) with:
- Name variations across sources
- WITW ID collisions (same ID for different equipment)
- Missing linkages (equipment → guns)
- Data integrity issues (tanks with aircraft names)

### Why does this matter?
- **Phase 9B** (current): Book datacard generation blocked by missing gun data
- **Phase 10** (future): Scenario exports would be corrupted by WITW collisions

### What's the fix?
Systematic database normalization using professional data cleaning methodologies:
- Fuzzy name matching
- Constraint enforcement
- Relationship linking
- Referential integrity

---

## ✅ Next Session Checklist

Before starting Phase 3:

- [ ] Read this file (DATABASE_NORMALIZATION_START_HERE.md)
- [ ] Review DATA_QUALITY_BASELINE.md (executive summary)
- [ ] Review REMEDIATION_PLAN.md (execution plan)
- [ ] **COMPLETE**: WITW_COLLISION_USER_DECISIONS.md (make 23 decisions)
- [ ] Verify database backup exists (master_database.db.backup-20251102-pre-normalization)
- [ ] Launch agent with Phase 3 prompt (see above)

**Estimated Time**:
- User decisions: 30-60 minutes
- Phase 3A execution: 4-5 hours
- Phase 3B execution: 6-7 hours
- Phase 3C execution: 2-3 hours
- **Total**: 13-16 hours (can spread over 2-3 days)

---

## 📚 Additional Resources

- `PROJECT_SCOPE.md` - Overall project context
- `START_HERE_NEW_SESSION.md` - General session workflow
- `CLAUDE.md` - Project instructions for Claude
- `PHASE_9B_STEP7_DATA_QUALITY_CRISIS.md` - Original problem documentation

---

**Last Session**: 2025-11-02 - Phase 1 & 2 complete (Analysis & Planning)
**Next Session**: User decisions + Phase 3 execution (Remediation)
**Status**: ⏸️ PAUSED - Awaiting user decisions on 23 WITW ID collisions

---

**Questions?** Read `REMEDIATION_PLAN.md` for detailed execution plan or `WITW_COLLISION_USER_DECISIONS.md` for decision guidance.
