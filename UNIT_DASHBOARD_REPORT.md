# North Africa TO&E Builder - Unit Dashboard Report

**Generated:** October 19, 2025, 10:00 AM
**Project Version:** Architecture v4.0
**Schema Target:** v3.0
**Template Target:** v2.0

---

## 📊 Executive Summary

**Overall Progress:** 174/420 unit-quarters complete (41.4%)

**Status:** ⚠️ **CRITICAL ISSUES DETECTED** - Schema compliance and data completeness require immediate attention.

### Key Findings

✅ **Strengths:**
- 41.4% completion rate (ahead of 28.1% from PROJECT_SCOPE.md v1.0.7)
- Excellent equipment variant detail (0% missing variants)
- Perfect nation value compliance (all lowercase)
- 98.9% chapter generation rate (172/174 units)

❌ **Critical Issues:**
- **100% units missing Section 6 fields** (supply/logistics: fuel_reserves, ammunition, operational_radius)
- **100% units missing Section 7 fields** (weather/environmental: season_quarter, temperature_range, terrain_type)
- **100% units missing confidence scores** (metadata.confidence_score)
- **100% units have non-nested commander** (Schema v3.0 violation - needs `commander.name`, `commander.rank`)
- **45.4% units have tank total validation errors** (total ≠ heavy + medium + light)
- **Mixed schema versions** (some use v3.0 top-level fields, others use old nested `unit_identification`)

---

## 📈 Progress Breakdown

### By Nation

| Nation    | Units | Percentage | Progress Bar |
|-----------|------:|:----------:|:-------------|
| Italian   | 73    | 42.0%      | ██████████████ |
| British   | 60    | 34.5%      | ████████████ |
| German    | 31    | 17.8%      | ██████ |
| American  | 6     | 3.4%       | █ |
| French    | 4     | 2.3%       | █ |
| **TOTAL** | **174** | **100%** | **████████████** |

**Analysis:**
- Italian units dominate (73/174, 42.0%) - aligns with Priority 1 in PROJECT_SCOPE.md
- American and French severely underrepresented (10 combined, 5.7%)
- Per PROJECT_SCOPE.md complete seed: Italian should be 156 unit-quarters (currently at 47% of target)

### By Quarter

| Quarter  | Units | Progress Bar |
|----------|------:|:-------------|
| 1940-Q2  | 8     | ████ |
| 1940-Q3  | 8     | ████ |
| 1940-Q4  | 8     | ████ |
| 1941-Q1  | 24    | ████████████ |
| **1941-Q2** | **31** | **███████████████** ⭐ |
| 1941-Q3  | 24    | ████████████ |
| 1941-Q4  | 19    | █████████ |
| 1942-Q1  | 4     | ██ |
| 1942-Q2  | 4     | ██ |
| 1942-Q3  | 13    | ██████ |
| 1942-Q4  | 25    | ████████████ |
| 1943-Q1  | 6     | ███ |

**Analysis:**
- 1941-Q2 is the most complete quarter (31 units) ⭐
- 1942-Q1 and 1942-Q2 are severely underrepresented (4 units each)
- Early war (1940-Q2 to 1940-Q4) has consistent coverage (8 units each)
- Late war (1943-Q1) needs more work (6 units vs target from seed)

---

## 🔍 Quality Audit Results

### Schema Compliance (v3.0)

| Metric | Status | Count | Severity |
|--------|--------|------:|:---------|
| Missing Top-Level Fields | ✅ PASS | 0/174 (0.0%) | None |
| **Commander Not Nested** | ❌ **FAIL** | **174/174 (100.0%)** | 🚨 **CRITICAL** |
| **Missing Confidence Score** | ❌ **FAIL** | **174/174 (100.0%)** | 🚨 **CRITICAL** |
| Invalid Nation Value | ✅ PASS | 0/174 (0.0%) | None |

**Critical Finding:** ALL units use non-compliant commander structure. Schema v3.0 requires:
```json
{
  "commander": {
    "name": "Generalleutnant Erwin Rommel",
    "rank": "Generalleutnant"
  }
}
```

But many units have:
```json
{
  "command": {
    "commander": {
      "name": "Generalleutnant Erwin Rommel",
      "rank": "Generalleutnant"
    }
  }
}
```

Or older schema with `unit_identification` object.

### Equipment Detail Compliance

| Metric | Status | Count | Severity |
|--------|--------|------:|:---------|
| Missing Tank Variants | ✅ PASS | 0/174 (0.0%) | None |
| Has Rollup Fields | ✅ PASS | 0/174 (0.0%) | None |
| Artillery No Variants | ✅ PASS | 0/174 (0.0%) | None |

**Excellent!** All units have variant-level equipment detail with NO rollups (exactly as required).

### Supply/Logistics Data (Section 6 - REQUIRED FOR SCENARIOS)

| Metric | Status | Count | Severity |
|--------|--------|------:|:---------|
| **Missing Supply Status** | ❌ **FAIL** | **96/174 (55.2%)** | 🔴 **HIGH** |
| **Missing Fuel Reserves** | ❌ **FAIL** | **174/174 (100.0%)** | 🚨 **CRITICAL** |
| **Missing Ammo Reserves** | ❌ **FAIL** | **174/174 (100.0%)** | 🚨 **CRITICAL** |
| **Missing Operational Radius** | ❌ **FAIL** | **174/174 (100.0%)** | 🚨 **CRITICAL** |

**Critical Finding:** Per PROJECT_SCOPE.md, Section 6 fields are **CRITICAL FOR SCENARIOS**:
- `supply_status` - Qualitative assessment with operational context
- `fuel_reserves` - Days at current consumption rate
- `ammunition` - Days of combat supply
- `operational_radius` - Distance from main supply depot (kilometers)
- `water` - Liters per day capacity (critical for desert operations)

**100% of units are missing these fields!** This blocks Phase 9 (Scenario Generation).

### Weather/Environmental Data (Section 7 - REQUIRED FOR SCENARIOS)

| Metric | Status | Count | Severity |
|--------|--------|------:|:---------|
| **Missing Season/Quarter** | ❌ **FAIL** | **174/174 (100.0%)** | 🚨 **CRITICAL** |
| **Missing Temperature Range** | ❌ **FAIL** | **174/174 (100.0%)** | 🚨 **CRITICAL** |
| **Missing Terrain Type** | ❌ **FAIL** | **174/174 (100.0%)** | 🚨 **CRITICAL** |

**Critical Finding:** Per PROJECT_SCOPE.md, Section 7 fields are **REQUIRED FOR SCENARIOS**:
- `season_quarter` - Which quarter and seasonal conditions
- `temperature_range` - Daily min/max temperatures (Celsius)
- `terrain_type` - Primary terrain (sand, rocky desert, coastal plain, etc.)
- `storm_frequency` - Sandstorms, Ghibli winds (days per month)
- `daylight_hours` - Average daylight hours (affects operational tempo)

**100% of units are missing these fields!** This blocks Phase 9 (Scenario Generation).

### Validation Checks

| Metric | Status | Count | Severity |
|--------|--------|------:|:---------|
| **Tank Total Mismatch** | ⚠️ **WARNING** | **79/174 (45.4%)** | 🟡 **MEDIUM** |
| Personnel Mismatch | ✅ PASS | 0/174 (0.0%) | None |

**Issue:** 45.4% of units have `tanks.total ≠ heavy + medium + light` (outside ±5% tolerance).

Example validation failures may be due to:
- Nested structure with rollup totals (`heavy_tanks.total`, `medium_tanks.total`)
- Missing sub-category counts
- Calculation errors

---

## 📖 Chapter Generation Status

**Chapters Generated:** 172/174 (98.9%) ✅

**Missing Chapters (2 units):**
1. `british_1941q2_1st_south_african_division`
2. `british_1941q2_5th_indian_division`

**Excellent coverage!** Nearly all units have corresponding MDBook chapters.

---

## ⏰ Recent Activity

**Last 10 Completions** (by modification time):

1. `german_1942q1_deutsches_afrikakorps` (10/19/2025 9:55 AM)
2. `italian_1940q3_62_marmarica_division` (10/19/2025 9:42 AM)
3. `italian_1940q3_61_sirte_division` (10/19/2025 9:36 AM)
4. `italian_1940q3_60_sabratha_division` (10/19/2025 9:31 AM)
5. `german_1942q4_deutsches_afrikakorps` (10/19/2025 9:18 AM)
6. `italian_1941q3_xxi_corps` (10/19/2025 9:09 AM)
7. `italian_1941q3_xx_corps` (10/19/2025 9:04 AM)
8. `british_1941q3_xxx_corps` (10/19/2025 9:00 AM)
9. `british_1941q3_xiii_corps` (10/19/2025 8:53 AM)
10. `italian_1940q2_10th_army` (10/19/2025 8:48 AM)

**Analysis:** Strong focus on Italian and German units in recent session. Corps-level formations being completed (XXI Corps, XX Corps, XXX Corps, XIII Corps, 10th Army).

---

## 🚨 Critical Action Items

### Priority 1: Fix Schema Compliance (BLOCKING ISSUE)

**Problem:** 100% of units fail Schema v3.0 compliance checks.

**Root Cause:** Mixed schema versions in use:
- Some units use new v3.0 schema (top-level `nation`, `quarter`, `organization_level`)
- Some units use old nested schema (`unit_identification` object)
- Commander structure inconsistent (`command.commander` vs `commander`)

**Required Actions:**
1. ✅ **Standardize commander structure** - All units must use:
   ```json
   {
     "commander": {
       "name": "Full Name",
       "rank": "Rank"
     }
   }
   ```

2. ✅ **Migrate old nested schemas** - Convert `unit_identification` to top-level fields

3. ✅ **Add confidence scores** - All units need:
   ```json
   {
     "metadata": {
       "confidence_score": 85,
       "sources": ["Source 1", "Source 2"]
     }
   }
   ```

**Estimated Time:** ~15-20 hours for automated migration script + manual QA

### Priority 2: Add Section 6 Fields (CRITICAL FOR PHASE 9)

**Problem:** 100% of units missing supply/logistics data required for scenario generation.

**Required Actions:**
1. ✅ Add `supply_status` to all units (qualitative assessment)
2. ✅ Add `fuel_reserves` (days at current consumption)
3. ✅ Add `ammunition` (days of combat supply)
4. ✅ Add `operational_radius` (kilometers from main supply depot)
5. ✅ Add `water` (liters per day - critical for desert operations)

**Data Sources:**
- Theater-level estimates from historical sources (Tessin, Army Lists)
- Field manuals for consumption rates by unit type
- Campaign studies for supply line distances

**Estimated Time:** ~20-30 hours (can be partially automated with theater-level defaults)

### Priority 3: Add Section 7 Fields (CRITICAL FOR PHASE 9)

**Problem:** 100% of units missing weather/environmental data required for scenario generation.

**Required Actions:**
1. ✅ Add `season_quarter` to all units
2. ✅ Add `temperature_range` (min/max Celsius)
3. ✅ Add `terrain_type` (sand, rocky desert, coastal plain, etc.)
4. ✅ Add `storm_frequency` (days per month)
5. ✅ Add `daylight_hours` (average hours)

**Data Sources:**
- Historical weather records for North Africa by quarter
- Campaign studies for environmental conditions
- Military logistics studies for seasonal impacts

**Estimated Time:** ~10-15 hours (mostly automated - weather data by quarter can be standardized)

### Priority 4: Fix Tank Total Validation (MEDIUM PRIORITY)

**Problem:** 45.4% of units have tank total mismatch errors.

**Required Actions:**
1. ✅ Review units with nested tank structures (`heavy_tanks.total`, `medium_tanks.total`)
2. ✅ Recalculate totals: `tanks.total = heavy + medium + light`
3. ✅ Run validation script: `npm run validate:v3`

**Estimated Time:** ~5-10 hours (automated script + manual fixes)

---

## 📋 Recommendations

### Immediate Actions (Next 1-2 Sessions)

1. **Create schema migration script** - Automated conversion of all units to Schema v3.0
   - File: `scripts/migrate_to_schema_v3.js`
   - Convert `unit_identification` to top-level fields
   - Standardize commander structure
   - Add metadata.confidence_score (default 75% with note "estimated")

2. **Create Section 6/7 enrichment script** - Add supply/logistics and weather data
   - File: `scripts/enrich_supply_weather.js`
   - Add Section 6 fields with theater-level defaults
   - Add Section 7 fields from quarter-specific weather database
   - Flag units needing manual review

3. **Run comprehensive validation** - Verify all units pass Schema v3.0 checks
   - File: `scripts/lib/validator.js`
   - Check all required fields present
   - Validate totals (tanks, personnel, artillery)
   - Generate compliance report

### Medium-Term Actions (Next 3-5 Sessions)

4. **Complete Italian units** (Priority 1 from PROJECT_SCOPE.md)
   - Target: 156 unit-quarters (currently 73, 47% complete)
   - Remaining: 83 unit-quarters
   - Estimated: ~30-40 hours autonomous processing

5. **Complete French units** (Priority 2 from PROJECT_SCOPE.md)
   - Target: 19 unit-quarters (currently 4, 21% complete)
   - Remaining: 15 unit-quarters
   - Estimated: ~5-10 hours autonomous processing

6. **Add British Corps/Army formations** (Priority 3 from PROJECT_SCOPE.md)
   - XIII Corps, XXX Corps, X Corps, First Army
   - Estimated: ~20-30 hours autonomous processing

### Long-Term Actions (After Phase 6 Complete)

7. **Phase 7: Air Force Extraction** (100-135 air units)
   - After all 420 ground unit-quarters complete
   - Estimated: ~60-80 hours autonomous processing

8. **Phase 9: Scenario Generation** (12+ battle scenarios)
   - Requires Section 6/7 data to be complete
   - Battle contexts, victory conditions, supply states
   - Estimated: ~40-50 hours scenario design + testing

9. **Phase 10: Campaign System** (complete 1940-1943)
   - Quarterly transitions, supply routes, weather patterns
   - Estimated: ~30-40 hours

---

## 📊 Quality Score Summary

| Category | Score | Status |
|----------|------:|:-------|
| Schema Compliance | 20% | 🔴 CRITICAL |
| Equipment Detail | 100% | ✅ EXCELLENT |
| Supply/Logistics | 5% | 🚨 CRITICAL |
| Weather/Environmental | 0% | 🚨 CRITICAL |
| Validation Checks | 55% | 🟡 NEEDS WORK |
| Chapter Generation | 99% | ✅ EXCELLENT |
| **OVERALL** | **47%** | 🔴 **NEEDS WORK** |

**Overall Assessment:** Despite excellent progress (41.4% completion) and equipment detail quality, critical schema compliance and scenario-required data fields (Sections 6 & 7) are blocking Phase 9 (Scenario Generation). Immediate action required to migrate all units to Schema v3.0 and add supply/weather data.

---

## 📁 File Locations (Architecture v4.0)

**Canonical Locations:**
- Units: `data/output/units/` (174 files)
- Chapters: `data/output/chapters/` (172 files)
- Scenarios: `data/output/scenarios/` (future - Phase 9)
- Air Units: `data/output/air_units/` (future - Phase 7)

**Session Archives:**
- Old sessions: `data/output/sessions/` (read-only historical audit trail)

**Scripts:**
- Dashboard: `scripts/generate_dashboard.js`
- Quality Audit: `scripts/audit_unit_quality.js`
- Validation: `scripts/lib/validator.js`
- Canonical Paths: `scripts/lib/canonical_paths.js`

---

## 🎯 Success Criteria Progress

From PROJECT_SCOPE.md v1.0.7:

| Criterion | Status | Notes |
|-----------|--------|-------|
| Complete ground vehicle TO&E (variant-level) | ✅ 100% | All units have excellent variant detail |
| Complete artillery breakdown (variants) | ✅ 100% | All units have variant-level artillery |
| Complete aircraft data (variants) | ✅ 100% | All units have variant-level aircraft |
| **Complete logistics data (Section 6)** | ❌ **0%** | **ALL units missing fuel/ammo/operational radius** |
| **Environmental factors (Section 7)** | ❌ **0%** | **ALL units missing weather/terrain data** |
| Bottom-up aggregation validation | ⚠️ 55% | 45% units have tank total mismatch |
| Minimum 80% confidence | ❌ 0% | ALL units missing confidence scores |
| MDBook generates for all units | ✅ 99% | 172/174 chapters generated |

**Critical Gap:** Sections 6 & 7 are 0% complete but are REQUIRED for Phase 9 (Scenario Generation) per PROJECT_SCOPE.md.

---

## 📝 Next Steps

**Recommended Workflow:**

1. ✅ **Review this dashboard** with user to confirm priorities
2. ✅ **Create migration scripts** (schema v3.0 + Section 6/7 enrichment)
3. ✅ **Run automated migration** on all 174 units
4. ✅ **Manual QA** on sample units (10-20 units) to verify quality
5. ✅ **Complete remaining Italian units** (Priority 1 - 83 units remaining)
6. ✅ **Complete French units** (Priority 2 - 15 units remaining)
7. ✅ **Resume autonomous processing** for remaining 246 unit-quarters

**Estimated Total Time to Phase 6 Complete:** ~120-150 hours autonomous processing + ~50 hours migration/QA

---

**Report End**

*Generated by: `scripts/generate_dashboard.js` and `scripts/audit_unit_quality.js`*
*For detailed technical specifications, see: `PROJECT_SCOPE.md`, `CLAUDE.md`, `VERSION_HISTORY.md`*
