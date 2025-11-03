# Next Session Handoff - Phase 9B Scenario Regeneration

**Session Date**: November 3, 2025 (Session End)
**Next Session Goal**: Integrate enhanced parser v2, regenerate all 45 scenarios with fixed combined arms validation
**Estimated Time**: 4-6 hours

---

## 🎯 Context Summary (What Happened)

### User Reported Issue
"Scenario 1 of battleaxe; all the work fixed the British forces, however the axis does not comply with combined arms they have nothing but infantry."

### Root Cause Identified
1. **Scenario research document** (`books/scenario_research.md`) was incomplete
   - Axis defensive forces missing AT guns and artillery
   - Example: Fort Capuzzo defenders had only Italian infantry, no 47mm AT guns to counter Matilda IIs
2. **Generator parsing bugs** caused most force descriptions to fail parsing
   - Infantry counting bug: 120 men counted as "120 platoons" instead of 4 platoons
   - Squadron parsing failures with colons/slashes
   - Company/battalion patterns missing

### What Was Fixed
✅ **18 scenarios corrected** in `books/scenario_research.md` (all 4 books)
   - Added Axis AT guns: Italian 47mm, German PAK 38/40, 88mm FlaK
   - Added artillery: Italian 75mm, German 105mm leFH 18
   - Based on Phase 6 unit TO&E data

✅ **Enhanced parser v2 created** (`scripts/battlegroup/book/scenario_force_parser_v2.py`)
   - 12 comprehensive validation rules (WargamingDataCleaner approach)
   - Fixes infantry counting: properly converts men → platoons
   - Handles squadrons, companies, battalions, batteries
   - Test results: 3/3 units parsed correctly for Scenario 1

✅ **Documentation created**
   - `PHASE_9B_SESSION_WORK_NOV3.md` (comprehensive session report - READ THIS)
   - `PHASE_9B_NEXT_STEPS.md` (updated with root cause analysis)

### What's NOT Done Yet
❌ Parser v2 **not integrated** into `scenario_generator_workflow.py` (still using buggy parser v1)
❌ Infantry validator **not fixed** in `force_composition_validator.py`
❌ Scenarios **not regenerated** with corrected parsing (Battleaxe/Crusader have bugs from v1)
❌ Gazala & First Alamein **not regenerated** at all

---

## 🚀 Next Session Tasks (Priority Order)

### **Task 1: Integrate Parser v2** (1-2 hours)

**Goal**: Replace buggy parser v1 with enhanced parser v2 in scenario generator

**Files to modify**:
1. `scripts/battlegroup/book/scenario_generator_workflow.py`

**Steps**:
1. Add import at top:
   ```python
   from scenario_force_parser_v2 import ScenarioForceParserV2, ParsedUnit
   ```

2. Find the `RosterBuilder` class (around line 250)

3. Replace the `_parse_force_description()` method with:
   ```python
   def _parse_force_description(self, description: str, nation: str = "unknown") -> List[ParsedUnit]:
       parser = ScenarioForceParserV2()
       parsed_units = parser.parse_force_description(description, nation)

       # Print validation report if issues found
       if parser.issues:
           print(parser.generate_validation_report())

       return parsed_units
   ```

4. Update `build_roster()` method to accept `ParsedUnit` objects instead of tuples

5. **Test with single scenario FIRST**:
   ```bash
   python scripts/battlegroup/book/scenario_generator_workflow.py --battle battleaxe --scenario 1
   ```

**Success Criteria**:
- Parsing logs show "Parsed 5 units" for Scenario 1 Axis forces (not 0-1 units)
- Axis forces include: Italian infantry, 47mm AT guns, Breda M37 HMGs, German infantry, PAK 38
- No warnings about "Failed to parse"

---

### **Task 2: Fix Infantry Validator** (30 minutes)

**Goal**: Fix platoon counting bug so validator doesn't count raw men as platoons

**File to modify**:
1. `scripts/battlegroup/force_composition_validator.py`

**Find** (around line 122-140):
```python
def count_infantry_platoons(units: List[Dict]) -> int:
    """Count total infantry platoons in force."""
    platoon_count = 0
    for unit in units:
        unit_type = unit.get("type", "")
        if unit_type in ["infantry_platoon", "infantry"]:
            platoon_count += unit.get("count", 0)  # BUG: This is correct now!
    return platoon_count
```

**Issue**: The old parser was passing raw men counts. Parser v2 already converts men → platoons, so this function should work correctly now. **Just verify it's summing `count` field correctly.**

**Test**:
```bash
python scripts/battlegroup/force_composition_validator.py --points 700 --year 1941 --infantry 4
```

Expected output: Should show infantry requirements for 700 pts in 1941 (min: 0, max: 0 platoons)

---

### **Task 3: Regenerate All 45 Scenarios** (2-3 hours)

**Goal**: Regenerate all scenarios with parser v2 and corrected research data

**Commands** (run in order):
```bash
cd D:/north-africa-toe-builder

# Step 1: Test single scenario first
python scripts/battlegroup/book/scenario_generator_workflow.py --battle battleaxe --scenario 1

# Step 2: If test passes, regenerate Battleaxe
python scripts/battlegroup/book/scenario_generator_workflow.py --battle battleaxe --all

# Step 3: Regenerate Crusader
python scripts/battlegroup/book/scenario_generator_workflow.py --battle crusader --all

# Step 4: Regenerate Gazala
python scripts/battlegroup/book/scenario_generator_workflow.py --battle gazala --all

# Step 5: Regenerate First Alamein
python scripts/battlegroup/book/scenario_generator_workflow.py --battle first_alamein --all
```

**Watch for**:
- Parsing logs: Should show "Parsed X units" with high success rate
- Validation reports: Should show valid or warnings only (not errors)
- Force diversity: Both sides should have 2+ unit types
- Infantry counts: Should be reasonable (1-10 platoons, not 120 platoons)

**Success Criteria**:
- All 45 scenarios generate without critical errors
- Scenario 1 Axis forces show: Italian infantry, 47mm AT guns, Breda M37 HMGs
- Validation reports show 0 combined arms violations for both sides
- Infantry platoon counts accurate (not raw men counts)

---

### **Task 4: Validation & Commit** (1 hour)

**Goal**: Verify all scenarios correct, commit regenerated content

**Validation steps**:
1. Check Scenario 1 markdown file:
   ```bash
   cat books/battleaxe/book/src/scenarios/scenario_01.md
   ```
   - Should show Axis forces with AT guns and artillery

2. Run validation suite (if available):
   ```bash
   python scripts/battlegroup/book/validate_all_scenarios.py
   ```

3. Check validation statistics:
   - 0 combined arms violations (both British and Axis)
   - 0 critical parsing errors
   - Infantry platoon counts reasonable

**Git commits**:
```bash
# Commit integrated parser
git add scripts/battlegroup/book/scenario_generator_workflow.py
git add scripts/battlegroup/force_composition_validator.py
git commit -m "feat(phase9b): Integrate enhanced parser v2 into scenario generator

- Replace buggy parser v1 with parser v2
- Fix infantry platoon counting in validator
- Enables proper combined arms validation for both sides
- Prepares for clean scenario regeneration"

# Commit regenerated scenarios
git add books/*/book/src/scenarios/*.md
git commit -m "feat(phase9b): Regenerate all 45 scenarios with combined arms fixes

All scenarios now comply with BattleGroup combined arms requirements:
- British forces: Infantry + tanks/AT guns + artillery
- Axis forces: Infantry + AT guns + artillery (NOW CORRECT)

Fixed scenarios:
- Battleaxe: 8 scenarios (Axis now have 47mm AT guns, PAK 38)
- Crusader: 12 scenarios (Axis combined arms complete)
- Gazala: 15 scenarios (German/Italian combined forces)
- First Alamein: 10 scenarios (PAK 40, 88mm FlaK 36)

Parser v2 achievements:
- 100% success rate on test scenarios
- Proper infantry organization (men -> platoons)
- Comprehensive validation rules
- Zero critical parsing errors"
```

---

## 📁 Key Files to Reference

**MUST READ FIRST**:
- `PHASE_9B_SESSION_WORK_NOV3.md` - Complete session report (READ THIS!)
- `PHASE_9B_NEXT_STEPS.md` - Current priorities and timeline

**Code Files**:
- `scripts/battlegroup/book/scenario_force_parser_v2.py` - Enhanced parser (READY)
- `scripts/battlegroup/book/scenario_generator_workflow.py` - Generator (NEEDS INTEGRATION)
- `scripts/battlegroup/force_composition_validator.py` - Validator (NEEDS VERIFICATION)

**Data Files**:
- `books/scenario_research.md` - Corrected research data (18 scenarios fixed)
- `books/battleaxe/book/src/scenarios/scenario_01.md` - Test this after regeneration

**Testing**:
```bash
# Test parser independently
python scripts/battlegroup/book/scenario_force_parser_v2.py

# Test single scenario after integration
python scripts/battlegroup/book/scenario_generator_workflow.py --battle battleaxe --scenario 1
```

---

## ✅ Success Criteria (How to Know You're Done)

### Minimum Success (MVP)
- [ ] Parser v2 integrated into scenario generator
- [ ] Scenario 1 regenerates with Axis AT guns visible in markdown
- [ ] All 45 scenarios regenerate without critical errors
- [ ] Validation shows 0 combined arms violations (both sides)
- [ ] Infantry platoon counts accurate (not raw men)

### Complete Success
- [ ] All minimum criteria met
- [ ] Parsing logs show 90%+ success rate
- [ ] Validation reports show 0 errors, warnings only
- [ ] Git commits created with regenerated scenarios
- [ ] Documentation updated

---

## 🚨 Potential Issues & Solutions

### Issue: "Failed to parse" warnings persist
**Solution**: Check parser v2 test output, may need additional patterns. Use `generate_validation_report()` to see what's failing.

### Issue: Infantry counts still wrong (120 platoons)
**Solution**: Verify parser v2 is being called (check imports). Parser v2 converts men→platoons correctly.

### Issue: Axis forces still missing AT guns
**Solution**: Check `books/scenario_research.md` - verify the 18 scenario fixes are present (git log should show commit 127bc674).

### Issue: Scenario generation crashes
**Solution**: Start with single scenario (`--scenario 1`), check error logs, ensure all dependencies imported.

---

## 📊 Current Statistics

**Scenario Research Data**:
- ✅ 18/45 scenarios corrected (40%)
- ✅ All 4 books affected
- ✅ Equipment based on Phase 6 unit data

**Parser v2 Status**:
- ✅ 12 validation rules implemented
- ✅ Test results: 100% success on Scenario 1 forces
- ✅ 571 lines of code
- ❌ Not integrated yet

**Regeneration Status**:
- ⚠️ Battleaxe: 8/8 generated (with v1 parser bugs)
- ⚠️ Crusader: 12/12 generated (with v1 parser bugs)
- ❌ Gazala: 0/15 generated
- ❌ First Alamein: 0/10 generated

**After This Session**:
- Should have: 45/45 scenarios with correct parsing ✅
- Should have: 0 combined arms violations ✅
- Should have: Clean git commits ✅

---

## 🎯 One-Sentence Summary

**Integrate parser v2 into scenario generator, fix validator, regenerate all 45 scenarios to resolve Axis combined arms violations.**

---

## 📞 Quick Start Commands

```bash
# 1. Read the full context
cat PHASE_9B_SESSION_WORK_NOV3.md

# 2. Test parser v2 works
python scripts/battlegroup/book/scenario_force_parser_v2.py

# 3. Start integration work
# Edit: scripts/battlegroup/book/scenario_generator_workflow.py
# Add import: from scenario_force_parser_v2 import ScenarioForceParserV2, ParsedUnit

# 4. Test with single scenario
python scripts/battlegroup/book/scenario_generator_workflow.py --battle battleaxe --scenario 1

# 5. If successful, regenerate all
python scripts/battlegroup/book/scenario_generator_workflow.py --battle battleaxe --all
python scripts/battlegroup/book/scenario_generator_workflow.py --battle crusader --all
python scripts/battlegroup/book/scenario_generator_workflow.py --battle gazala --all
python scripts/battlegroup/book/scenario_generator_workflow.py --battle first_alamein --all
```

---

**Good luck! The foundation is solid. 4-6 hours to complete scenario regeneration.**

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
