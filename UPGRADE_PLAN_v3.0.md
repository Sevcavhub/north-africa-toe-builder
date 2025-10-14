# Schema v3.0 Upgrade Plan - 25 Units with Warnings

**Created**: 2025-10-13
**Status**: Ready for Execution
**Target**: Bring all 25 units to full v3.0 compliance

---

## Executive Summary

**Current State**:
- 158 total units
- 133 passing (84.2%)
- 0 critical failures ✅
- 25 warnings (15.8%)

**Goal**: Upgrade 25 units from warnings to full v3.0 compliance
**Expected Outcome**: 158/158 units passing (100%)
**Estimated Effort**: 8-12 hours (automated + manual review)

---

## Warning Categories - Detailed Breakdown

### Category 1: Invalid Schema Types (4 units) - PRIORITY 1 🔴

**Issue**: Using old or incorrect schema_type values
**Fix**: Update to correct schema v3.0 allowed values
**Effort**: LOW (quick fixes)

| File | Current schema_type | Correct Value | Organization Level |
|------|---------------------|---------------|-------------------|
| french_1942q2_1re_brigade_fran_aise_libre_toe.json | "brigade_toe" | corps_toe or regiment_toe | Brigade (non-standard) |
| british_1940q2_western_desert_force_toe.json | "unified_toe" | corps_toe | Corps-level force |
| british_1940q3_7th_armoured_division_toe.json | "unified_toe" | division_toe | Division |
| german_1942q3_panzerarmee_afrika_toe.json | "theater_toe" | theater_scm | Army-level command |

**Additional Issues**:
- Western Desert Force: 0% confidence (needs complete regeneration)
- 7th Armoured Division: 0% confidence (needs complete regeneration)

---

### Category 2: Low Confidence (14 units) - PRIORITY 2 🟡

**Issue**: Confidence scores 65-74% (below 75% threshold)
**Fix**: Enhance with additional sources, verify data, recalculate
**Effort**: MEDIUM (research + validation)

| File | Quarter | Confidence | Action Needed |
|------|---------|------------|---------------|
| german_1941q2_15_panzer_division_toe.json (065701) | 1941-Q2 | 65% | Add Tessin sources, verify tank counts |
| italian_1940q2_63a_divisione_di_fanteria_cirene_toe.json | 1940-Q2 | 68% | TM E 30-420 research, commander ID |
| german_1941q3_21_panzer_division_toe.json | 1941-Q3 | 70% | Fix personnel=0, add Feldgrau sources |
| italian_1940q4_132_divisione_corazzata_ariete_toe.json | 1940-Q4 | 72% | Nafziger Collection (already extracted for 1941-Q4 at 92%) |
| british_1941q2_1st_south_african_infantry_division_toe.json | 1941-Q2 | 72% | British Army Lists, unit war diaries |
| french_1943q1_1re_division_fran_aise_libre_toe.json | 1943-Q1 | 72% | Free French archives, Niehorster |
| italian_1941q3_25th_infantry_division_bologna_toe.json | 1941-Q3 | 72% | Compare with 1941-Q4 version (82%) |
| british_1940q2_4th_indian_infantry_division_toe.json | 1940-Q2 | 72% | British Army Lists, regimental histories |
| british_1941q1_1st_south_african_infantry_division_toe.json | 1941-Q1 | 72% | South African official histories |
| italian_1941q1_55a_divisione_di_fanteria_savona_toe.json (308971) | 1941-Q1 | 72% | **SUPERSEDED** by new version (80%) - DELETE |
| german_1943q1_10_panzer_division_toe.json | 1943-Q1 | 72% | Tessin Band 08, Nafziger |
| german_1942q4_90_leichte_afrika_division_toe.json | 1942-Q4 | 72% | Compare with 1941-Q4 version if available |
| italian_1940q2_62_divisione_di_fanteria_marmarica_toe.json | 1940-Q2 | 72% | TM E 30-420, Italian TO&E |
| italian_1940q2_61_divisione_di_fanteria_sirte_toe.json | 1940-Q2 | 72% | TM E 30-420, Italian TO&E |

**Note**: italian_1941q1_55a_divisione_di_fanteria_savona (72%) is an OLD VERSION. New version (80%) exists in autonomous_1760403072009. DELETE the old one.

---

### Category 3: Unknown Commanders (6 units) - PRIORITY 3 🟠

**Issue**: Commander field = "Unknown"
**Fix**: Research and identify commanders for specific quarters
**Effort**: HIGH (historical research required)

| File | Quarter | Current Confidence | Research Sources |
|------|---------|-------------------|------------------|
| italian_1941q2_101_divisione_motorizzata_trieste_toe.json | 1941-Q2 | 78% | Comando Supremo, Italian archives, Generals.dk |
| italian_1942q2_133rd_littorio_armored_division_toe.json | 1942-Q2 | 85% | Comando Supremo, Nafziger Collection |
| italian_1942q3_133a_divisione_corazzata_littorio_toe.json | 1942-Q3 | 80% | Same as Q2 (likely same commander) |
| italian_1942q4_133a_divisione_corazzata_littorio_toe.json | 1942-Q4 | 85% | Italian official histories |
| italian_1942q4_185a_divisione_paracadutisti_folgore_toe.json | 1942-Q4 | 82% | Folgore paratrooper histories, El Alamein accounts |
| italian_1943q1_131_divisione_corazzata_centauro_toe.json | 1943-Q1 | 76% | Italian armored division histories |

**Research Strategy**:
1. Comando Supremo website (Italian divisions)
2. Generals.dk commander database
3. Axis History Forum archives
4. Italian Army official histories
5. Unit war diaries (if available)

---

### Category 4: Data Quality Issues (3 units) - PRIORITY 1 🔴

**Issue**: Invalid values, calculation errors
**Fix**: Correct data, recalculate fields
**Effort**: LOW (quick fixes)

| File | Issue | Fix |
|------|-------|-----|
| german_1941q3_21_panzer_division_toe.json | organization_level: "Division" | Change to "division" (lowercase) |
| german_1941q3_21_panzer_division_toe.json | total_personnel = 0 | Add personnel data from sources |
| german_1941q2_15_panzer_division_toe.json (203201) | Personnel mismatch: 15000 vs 14000 (6.7%) | Recalculate or adjust total |

---

## Phased Execution Plan

### Phase 1: Quick Fixes (Priority 1 - Highest Impact) ⚡
**Duration**: 2-3 hours
**Units**: 7 (4 schema types + 3 data quality)

**Actions**:
1. Fix schema_type values (4 units):
   - french_1942q2_1re_brigade_fran_aise_libre → corps_toe or regiment_toe
   - british_1940q2_western_desert_force → corps_toe + REGENERATE (0% conf)
   - british_1940q3_7th_armoured_division → division_toe + REGENERATE (0% conf)
   - german_1942q3_panzerarmee_afrika → theater_scm

2. Fix data quality issues (3 units):
   - german_1941q3_21_panzer_division → Fix org_level, add personnel
   - german_1941q2_15_panzer_division (203201) → Fix personnel calculation

3. Delete superseded unit:
   - italian_1941q1_55a_divisione_di_fanteria_savona (308971 folder) → DELETE

**Expected Result**: 7 units upgraded, 1 deleted = 6 net upgrades

---

### Phase 2: Low Confidence Upgrades (Priority 2) 📊
**Duration**: 4-6 hours
**Units**: 13 (after removing superseded Savona)

**Method**: Autonomous extraction with enhanced sourcing

**Batch 1 - German Units (3 units)**:
1. german_1941q2_15_panzer_division (065701) - 65% → 78%+
2. german_1941q3_21_panzer_division - 70% → 78%+ (after Phase 1 fixes)
3. german_1943q1_10_panzer_division - 72% → 78%+

**Batch 2 - Italian Units (5 units)**:
4. italian_1940q2_63a_divisione_di_fanteria_cirene - 68% → 78%+
5. italian_1940q4_132_divisione_corazzata_ariete - 72% → 78%+
6. italian_1941q3_25th_infantry_division_bologna - 72% → 78%+
7. italian_1940q2_62_divisione_di_fanteria_marmarica - 72% → 78%+
8. italian_1940q2_61_divisione_di_fanteria_sirte - 72% → 78%+

**Batch 3 - British/Commonwealth Units (4 units)**:
9. british_1941q2_1st_south_african_infantry_division - 72% → 78%+
10. british_1940q2_4th_indian_infantry_division - 72% → 78%+
11. british_1941q1_1st_south_african_infantry_division - 72% → 78%+
12. german_1942q4_90_leichte_afrika_division - 72% → 78%+

**Batch 4 - French Units (1 unit)**:
13. french_1943q1_1re_division_fran_aise_libre - 72% → 78%+

**Source Enhancement Strategy**:
- German: Tessin Wehrmacht Encyclopedia (Tier 1), Feldgrau.com (Tier 2)
- Italian: TM E 30-420 (Tier 1), Comando Supremo (Tier 2), Nafziger (Tier 1)
- British: British Army Lists (Tier 1), unit war diaries (Tier 1)
- French: Niehorster.org (Tier 2), Free French archives (Tier 2)

**Expected Result**: 13 units upgraded from 65-72% to 78%+ confidence

---

### Phase 3: Commander Research (Priority 3) 🔍
**Duration**: 2-3 hours
**Units**: 6 (all Italian)

**Research Approach**:
1. **Littorio Division** (3 quarters: 1942-Q2, Q3, Q4):
   - Single research effort for all quarters
   - Likely same commander across 6-month period
   - Sources: Comando Supremo, Nafziger, Italian official histories

2. **Folgore Division** (1942-Q4):
   - Famous unit (El Alamein)
   - Well-documented commander
   - Sources: Folgore regimental histories, El Alamein accounts

3. **Trieste Division** (1941-Q2):
   - Compare with 1941-Q4 version (we extracted with commander Piazzoni)
   - Verify if same commander in Q2

4. **Centauro Division** (1943-Q1):
   - Late-war unit
   - Sources: Italian armored division histories

**Manual Research Tasks**:
- Search Comando Supremo website for division pages
- Query Generals.dk database for Italian commanders
- Cross-reference Axis History Forum threads
- Check Italian Army official order of battle documents

**Expected Result**: 6 units upgraded with identified commanders

---

### Phase 4: Validation & Verification ✅
**Duration**: 1 hour

**Actions**:
1. Run `npm run qa:v3` after each phase
2. Verify all 25 units now pass without warnings
3. Check confidence scores all ≥75%
4. Verify commanders identified (or explicitly documented as unavailable)
5. Confirm schema_type values correct
6. Validate personnel calculations

**Success Criteria**:
- 158/158 units passing (100%)
- 0 warnings
- 0 failures
- Average confidence ≥78%

---

## Automation Strategy

### Automated Tasks (Use Task Tool)
- Regenerate units with 0% confidence (Western Desert Force, 7th Armoured)
- Batch process low confidence units with enhanced sourcing
- Auto-fix schema_type values with Edit tool
- Recalculate personnel totals

### Manual Tasks (Human Review Required)
- Commander research (Italian divisions)
- Brigade vs Corps classification decision (French Brigade)
- Cross-reference verification for commanders
- Final QA approval

---

## Tracking & Progress

### Execution Checklist

**Phase 1: Quick Fixes** (7 units + 1 deletion)
- [ ] Fix french_1942q2_1re_brigade_fran_aise_libre schema_type
- [ ] Regenerate british_1940q2_western_desert_force (0% conf)
- [ ] Regenerate british_1940q3_7th_armoured_division (0% conf)
- [ ] Fix german_1942q3_panzerarmee_afrika schema_type
- [ ] Fix german_1941q3_21_panzer_division org_level + personnel
- [ ] Fix german_1941q2_15_panzer_division personnel calculation
- [ ] Delete italian_1941q1_55a_divisione_di_fanteria_savona (old version)

**Phase 2: Low Confidence** (13 units)
- [ ] Batch 1: German units (3)
- [ ] Batch 2: Italian units (5)
- [ ] Batch 3: British/Commonwealth units (4)
- [ ] Batch 4: French units (1)

**Phase 3: Commander Research** (6 units)
- [ ] Research Littorio commanders (3 quarters)
- [ ] Research Folgore commander
- [ ] Research Trieste commander (1941-Q2)
- [ ] Research Centauro commander

**Phase 4: Final Validation**
- [ ] Run npm run qa:v3
- [ ] Verify 158/158 passing
- [ ] Commit all changes
- [ ] Update documentation

---

## Risk Assessment

### Low Risk (Phase 1)
- Schema type fixes: Simple field updates
- Data quality fixes: Straightforward calculations
- File deletions: Superseded versions removed

### Medium Risk (Phase 2)
- Confidence upgrades: Requires quality source research
- May not reach 78%+ if sources unavailable
- Mitigation: Document gaps transparently

### High Risk (Phase 3)
- Commander research: May not find all commanders
- Italian sources less accessible than German/British
- Mitigation: Mark as "Confirmed Unavailable" with research notes

---

## Expected Outcomes

### Quantitative Results
- **Before**: 133/158 passing (84.2%), 25 warnings
- **After**: 158/158 passing (100%), 0 warnings
- **Improvement**: +25 units upgraded (+15.8%)

### Qualitative Improvements
- All units at v3.0 schema standard
- Confidence scores consistently ≥75%
- Commanders identified where possible
- Data quality issues resolved
- Professional publication-ready dataset

---

## Resource Requirements

### Time Estimate
- Phase 1: 2-3 hours
- Phase 2: 4-6 hours
- Phase 3: 2-3 hours
- Phase 4: 1 hour
- **Total**: 9-13 hours

### Tools Required
- Task tool (autonomous extraction)
- Edit tool (quick fixes)
- WebSearch/WebFetch (commander research)
- Validation scripts (qa:v3)

### Source Access
- Tier 1: Tessin, British Army Lists, TM E 30-420 (local)
- Tier 2: Feldgrau, Comando Supremo, Niehorster (web)
- Research: Generals.dk, Axis History Forum (web)

---

## Success Criteria

### Must Have (Required)
✅ All 25 units pass schema validation (no warnings)
✅ All schema_type values correct
✅ All confidence scores documented (target ≥75%)
✅ Zero calculation errors

### Should Have (Target)
✅ 20+ units reach ≥75% confidence
✅ 4+ commanders identified
✅ All data quality issues resolved

### Nice to Have (Stretch)
✅ All 25 units reach ≥78% confidence
✅ All 6 commanders identified
✅ Enhanced sourcing for all units

---

## Next Steps

**Immediate Actions**:
1. Review and approve this plan
2. Run Phase 1 Quick Fixes (2-3 hours)
3. Validate Phase 1 results
4. Proceed to Phase 2 or pause for review

**Command to Execute**:
```bash
# Start upgrade process
# Human confirmation: "Begin Phase 1 Quick Fixes"
```

---

**Plan Status**: ✅ Ready for Execution
**Created**: 2025-10-13
**Estimated Completion**: 1-2 work days
**Expected Success Rate**: 95%+
