# Phase 9B Step 3: Points/BR System - Chunked Work Plan

**Goal**: Build points calculator and BR assigner with ±10% accuracy
**Total Estimated Time**: 15-20 hours
**Strategy**: 7 small chunks with git commits + MCP memory updates after each

---

## Chunk 1: Analyze Reference Database Patterns (2-3 hours)

**Deliverable**: `scripts/battlegroup/analysis/points_br_analysis.py`

**Tasks**:
- Query bg_reference_vehicles table (500 vehicles)
- Query bg_reference_guns table (57 guns)
- Analyze points distribution by vehicle type/category
- Analyze BR distribution by unit importance
- Identify correlation: points vs (armor + firepower + mobility)
- Identify correlation: BR vs (unit type + experience level)
- Export patterns to JSON: `analysis_results.json`

**Git Commit**: "feat: Points/BR pattern analysis from 557 reference items"

**MCP Memory**: Store key patterns discovered

**Estimated Tokens**: ~15,000 (read DB, analysis, write code, commit)

---

## Chunk 2: Points Calculator - Base Algorithm (2-3 hours)

**Deliverable**: `scripts/battlegroup/conversion/points_calculator.py` (v1 - base only)

**Tasks**:
- Implement base points formula (armor + gun + movement components)
- Use patterns from Chunk 1 analysis
- Calculate base cost for 20 test vehicles
- Validate against reference database
- Export base formula coefficients to JSON

**Git Commit**: "feat: Points calculator base algorithm (armor+gun+movement)"

**MCP Memory**: Store formula structure and coefficients

**Estimated Tokens**: ~15,000 (algorithm implementation, testing, commit)

---

## Chunk 3: Points Calculator - Modifiers & Special Cases (2-3 hours)

**Deliverable**: `scripts/battlegroup/conversion/points_calculator.py` (v2 - complete)

**Tasks**:
- Add modifiers: special rules, equipment, experience levels
- Handle special cases: self-propelled guns, tank destroyers, recon vehicles
- Implement rounding logic to match official values
- Test on 50 vehicles (diverse types)
- Refine coefficients for ±10% accuracy target

**Git Commit**: "feat: Points calculator modifiers and special cases"

**MCP Memory**: Update with modifier list and special case handling

**Estimated Tokens**: ~18,000 (modifiers, special cases, testing, commit)

---

## Chunk 4: Points Calculator - Full Validation (1-2 hours)

**Deliverable**: Validation report + refined calculator

**Tasks**:
- Test all 500 vehicles from reference database
- Generate accuracy report (percentage within ±10%)
- Identify outliers and adjust formula
- Document remaining gaps (if any)
- Final tuning pass

**Git Commit**: "test: Points calculator validation on 500 vehicles"

**MCP Memory**: Store validation results and accuracy metrics

**Estimated Tokens**: ~12,000 (validation run, analysis, commit)

---

## Chunk 5: BR Assigner - Pattern Analysis (2-3 hours)

**Deliverable**: `scripts/battlegroup/conversion/battle_rating_assigner.py` (v1)

**Tasks**:
- Analyze BR patterns from 557 reference items
- Identify BR rules by unit type (infantry=0, support weapon=1, tank=2-4, etc.)
- Identify experience level effects (Inexperienced/Regular/Veteran/Elite)
- Implement decision tree for BR assignment
- Test on 20 diverse units

**Git Commit**: "feat: Battle Rating assigner with type-based decision tree"

**MCP Memory**: Store BR assignment rules and decision tree

**Estimated Tokens**: ~15,000 (BR analysis, algorithm, testing, commit)

---

## Chunk 6: BR Assigner - Validation & Refinement (2-3 hours)

**Deliverable**: Complete BR assigner with 90%+ accuracy

**Tasks**:
- Test all 557 reference items for BR accuracy
- Calculate exact match percentage (target: 90%+)
- Identify mismatch patterns and refine rules
- Add special cases for unique units
- Document BR assignment logic

**Git Commit**: "test: BR assigner validation on 557 reference items"

**MCP Memory**: Store validation results and refinement notes

**Estimated Tokens**: ~15,000 (validation, refinement, commit)

---

## Chunk 7: Integration & Documentation (2-3 hours)

**Deliverable**: Complete Step 3 documentation + integrated tools

**Tasks**:
- Create unified CLI: `python -m scripts.battlegroup.assign_points_br <equipment_id>`
- Apply to all 469 equipment items in master_database.db
- Generate complete equipment roster with points/BR
- Write PHASE_9B_STEP3_SUMMARY.md (validation results, formulas, examples)
- Update PROJECT_SCOPE.md with Step 3 completion

**Git Commit**: "feat: Phase 9B Step 3 complete - Points/BR system validated"

**MCP Memory**: Store completion status and key metrics

**Estimated Tokens**: ~18,000 (integration, documentation, full commit)

---

## Chunk Execution Strategy

**Per-Chunk Process**:
1. Start with clean todo list for chunk tasks
2. Execute chunk (2-3 hours max)
3. Git commit with detailed message
4. MCP memory update with key results
5. Check remaining token budget
6. **STOP if <30,000 tokens remaining** (safety buffer)
7. Continue to next chunk if tokens available

**Safety Protocol**:
- Never start a chunk with <40,000 tokens remaining
- Commit early and often within chunks
- Store intermediate results in MCP memory
- Can resume from any chunk boundary

**Total Estimated Tokens**: 108,000-126,000 (average ~15,000 per chunk)

**Current Token Budget**: ~139,000 remaining
**Recommendation**: Execute Chunks 1-2 today, then pause and resume next session

---

## Next Session Resume Point

When resuming, check:
1. MCP memory for last completed chunk
2. Git log for last commit
3. This file for next chunk to execute
4. Token budget before starting next chunk

**Quick Resume Commands**:
```bash
# Check last commit
git log -1 --oneline

# Check MCP memory
# (use mcp__memory__search_nodes with query="Phase 9B Step 3")

# Check token budget in session
```
