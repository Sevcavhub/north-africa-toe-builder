# DATABASE LINKAGE PROJECT - INDEX

**Project**: Populate equipment_battlegroup.reference_vehicle_id using exact pattern matching
**Date**: 2025-11-03
**Status**: Analysis Complete - Ready for Execution
**Analyst**: Claude (Database Normalization Agent)

---

## Quick Start

**If you just want to execute Tier 1 (19 items, zero risk)**:
1. Read: [EXECUTE_TIER1.md](EXECUTE_TIER1.md)
2. Execute: `scripts/linkage/tier1_exact_matches.sql`
3. Verify: 2 priority test cases solved (Matilda II, M4 Sherman)

**If you want the full analysis**:
1. Read: [LINKAGE_SUMMARY.txt](LINKAGE_SUMMARY.txt) (quick overview)
2. Read: [LINKAGE_REPORT.md](LINKAGE_REPORT.md) (comprehensive report)
3. Execute when ready

---

## Document Guide

### Core Analysis Documents

#### 1. [LINKAGE_SUMMARY.txt](LINKAGE_SUMMARY.txt) - START HERE
**Purpose**: Quick reference overview
**Audience**: Anyone who wants the key facts
**Contents**:
- Current database state
- Matching results by tier
- Coverage projections
- Architecture issues
- Recommendations

**Read Time**: 2 minutes

---

#### 2. [LINKAGE_REPORT.md](LINKAGE_REPORT.md) - COMPREHENSIVE
**Purpose**: Complete analysis with all details
**Audience**: Technical review, decision-making
**Contents**:
- Executive summary
- Tier 1 exact matches breakdown (19 items)
- Priority test case results (4 cases)
- Tier 2/3 normalization candidates
- Unmatched equipment analysis
- Architecture issues
- Projected outcomes
- Recommendations

**Read Time**: 10-15 minutes

---

#### 3. [LINKAGE_ANALYSIS.md](LINKAGE_ANALYSIS.md) - DISCOVERY PHASE
**Purpose**: Initial discovery and data exploration
**Audience**: Understanding the problem space
**Contents**:
- Database state analysis
- Priority test case initial findings
- Equipment category breakdown
- Matching tier definitions
- Architecture issue identification
- Conservative/optimistic estimates

**Read Time**: 8-12 minutes

---

#### 4. [MATCHING_STRATEGY.md](MATCHING_STRATEGY.md) - TECHNICAL SPECS
**Purpose**: Detailed implementation strategy
**Audience**: Developers implementing Tier 2/3
**Contents**:
- Tier 1 exact match specifications
- Tier 2 normalization rules (Python functions)
- Tier 3 base model matching logic
- Implementation plan with SQL examples
- Safety protocol
- Expected outcomes by tier

**Read Time**: 12-18 minutes

---

### Execution Documents

#### 5. [EXECUTE_TIER1.md](EXECUTE_TIER1.md) - EXECUTION GUIDE
**Purpose**: Step-by-step execution instructions
**Audience**: Whoever runs the SQL script
**Contents**:
- What will happen during execution
- Priority test cases before/after
- Expected database changes
- Execution methods (3 options)
- Validation checks
- Rollback procedure
- Success criteria

**Read Time**: 5-8 minutes

---

#### 6. [scripts/linkage/tier1_exact_matches.sql](scripts/linkage/tier1_exact_matches.sql) - EXECUTABLE SQL
**Purpose**: Actual SQL to execute Tier 1 linkage
**Audience**: Database administrators, automated execution
**Contents**:
- Audit table creation
- Match preview queries
- Transaction with UPDATE statement
- Validation queries
- Rollback script (commented)
- Summary report generation

**Execution Time**: < 1 minute

---

## Priority Test Cases - Current Status

| Test Case | Equipment | Category | Tier 1 Result | Confidence | Next Steps |
|-----------|-----------|----------|---------------|------------|------------|
| #1 | GER_PANZER_III_AUSF_F | tanks | ❌ Not matched | - | Tier 2 normalization |
| #2 | GBR_MATILDA_II | tanks | ✅ **id:290** | **100** | **READY** |
| #3 | USA_M4_SHERMAN | tanks | ✅ **id:203** | **100** | **READY** |
| #4 | GBR_25_POUNDER | field_artillery | ❌ Blocked | - | Add ref_gun_id column |

**Tier 1 Solves**: 2/4 test cases (50%)

---

## Matching Tiers - Overview

### Tier 1: Exact Matches ✅ READY
- **Method**: `LOWER(TRIM(name))` matching with nation validation
- **Results**: 19 items (4.1%)
- **Confidence**: 100
- **Status**: SQL script ready to execute
- **Risk**: Zero (full rollback available)

### Tier 2: Normalization Matches ⏳ ESTIMATED
- **Method**: Punctuation/spacing normalization + reverse order
- **Estimated**: 40-60 items (8.5-12.8%)
- **Confidence**: 90
- **Status**: Requires Python script development
- **Risk**: Low (preview before execution)

### Tier 3: Base Model Matches ⏳ ESTIMATED
- **Method**: Strip variant suffixes, match on base model
- **Estimated**: 20-30 items (4.3-6.4%)
- **Confidence**: 80
- **Status**: Requires variant detection logic
- **Risk**: Medium (manual review recommended)

---

## Architecture Issues

### Issue #1: Missing reference_gun_id Column (CRITICAL)
**Impact**: 110 artillery items (23.5%) cannot be linked
**Solution**: `ALTER TABLE equipment_battlegroup ADD COLUMN reference_gun_id`
**Expected Gain**: +50-70 items (10.7-14.9%)

### Issue #2: Multiple Variant Strategy
**Impact**: 4 items have 2-5 BG variants
**Current**: Using MIN(id) strategy
**Better**: Create variant_preferences table

### Issue #3: Unknown Nation Records
**Impact**: 454 bg_reference_vehicles have nation='Unknown'
**Solution**: Parse vehicle names, infer nation, or exclude

---

## Coverage Projections

| Scenario | Items Linked | Percentage | Items NULL | Notes |
|----------|-------------|------------|------------|-------|
| **Tier 1 Only** | 19 | 4.1% | 450 (95.9%) | Ready now |
| **Tier 1 + 2** | 60-80 | 12.8-17.1% | 389-409 | Requires Python |
| **Tier 1 + 2 + 3** | 80-100 | 17.1-21.3% | 369-389 | Requires variant logic |
| **Full (+ ref_gun_id)** | 130-170 | 27.7-36.3% | 299-339 | **Realistic maximum** |

**Unmatchable** (architecture/scope limits): 258 items (55.0%)
- Aircraft: 59 (no BG tables)
- Support vehicles: 89 (limited coverage)
- Artillery without ref_gun_id: 110

---

## Execution Workflow

### This Session (Recommended)

1. **Review** LINKAGE_SUMMARY.txt (2 min)
2. **Review** EXECUTE_TIER1.md (5 min)
3. **Execute** Tier 1 SQL script (< 1 min)
4. **Verify** 19 items linked, 2 test cases solved
5. **Test** BG datacard generation with linked items

**Total Time**: < 10 minutes
**Risk**: Zero
**Gain**: 19 items linked (4.1%)

### Next Session (Follow-Up)

1. **Develop** Tier 2 Python normalization script (1-2 hours)
2. **Preview** Tier 2 matches for approval
3. **Execute** approved Tier 2 matches
4. **Add** reference_gun_id column (architecture fix)
5. **Link** 110 artillery items using bg_reference_guns
6. **Develop** Tier 3 base model matching (2-4 hours)

**Total Time**: 4-8 hours development
**Risk**: Low-Medium (with previews)
**Gain**: +110-150 items (23.5-32.0%)

---

## Files Generated (6 documents)

| File | Type | Purpose | Audience |
|------|------|---------|----------|
| LINKAGE_SUMMARY.txt | Quick Ref | 2-min overview | Everyone |
| LINKAGE_REPORT.md | Report | Comprehensive analysis | Decision makers |
| LINKAGE_ANALYSIS.md | Analysis | Discovery phase findings | Technical review |
| MATCHING_STRATEGY.md | Strategy | Implementation details | Developers |
| EXECUTE_TIER1.md | Guide | Execution instructions | Operators |
| tier1_exact_matches.sql | SQL | Executable script | Database |

Plus this index document (LINKAGE_INDEX.md)

---

## Recommendations

### Immediate (This Session)
1. ✅ **Execute Tier 1 SQL script** - 19 items, zero risk, 2 test cases solved
2. ✅ **Verify results** - Check Matilda II and M4 Sherman datacards
3. ⏳ **Review unmatched items** - Understand Tier 2 potential

### Short Term (Next Session)
1. ⏳ **Develop Tier 2 script** - Python normalization (1-2 hours)
2. ⏳ **Add ref_gun_id column** - Schema migration for artillery
3. ⏳ **Link artillery items** - 110 items via bg_reference_guns

### Long Term (Future Sessions)
1. ⏳ **Develop Tier 3 logic** - Base model variant matching
2. ⏳ **Resolve Unknown nations** - Parse and infer from context
3. ⏳ **Create variant preferences** - Metadata for best variant selection

---

## Success Metrics

**Tier 1 Success** (This Session):
- ✅ 19 items linked (4.1%)
- ✅ 2/4 priority test cases solved
- ✅ Zero data loss
- ✅ Full audit trail

**Full Project Success** (All Tiers):
- ✅ 130-170 items linked (27.7-36.3%)
- ✅ 4/4 priority test cases solved
- ✅ Zero data loss
- ✅ Full audit trail
- ✅ 32-36% coverage (realistic given architecture)

---

## Database State

### Current (Before Execution)
```
equipment: 469 items
equipment_battlegroup:
  - reference_vehicle_id: 0/469 populated (0%)
  - reference_match_confidence: 0/469 set

bg_reference_vehicles: 954 items (499 with nation)
bg_reference_guns: 57 items
```

### After Tier 1 Execution
```
equipment: 469 items
equipment_battlegroup:
  - reference_vehicle_id: 19/469 populated (4.1%)
  - reference_match_confidence: 19/469 set to 100

normalization_audit: 19 records (rollback available)
```

### After Full Implementation (Projected)
```
equipment: 469 items
equipment_battlegroup:
  - reference_vehicle_id: 80-100/469 (17.1-21.3%)
  - reference_gun_id: 50-70/469 (10.7-14.9%)
  - Total linked: 130-170/469 (27.7-36.3%)
  - Confidence scores: 80-100 (tiered)

normalization_audit: 130-170 records (full history)
```

---

## Contact & Questions

**Analysis Performed By**: Claude (Database Normalization Agent)
**Methodology**: agents/database_normalization_agent.json section 4
**Approach**: Exact pattern matching (NOT fuzzy)
**Safety**: Full audit trail, rollback SQL, transaction-based
**Validation**: Pre/post COUNT checks, confidence scoring

**Questions?**
- Review relevant document from list above
- Check LINKAGE_SUMMARY.txt for quick facts
- Consult MATCHING_STRATEGY.md for implementation details

---

**Status**: ✅ Analysis Complete - Ready for Tier 1 Execution

**Next Action**: Execute `scripts/linkage/tier1_exact_matches.sql` or review [EXECUTE_TIER1.md](EXECUTE_TIER1.md) for instructions.

---

*Generated: 2025-11-03*
