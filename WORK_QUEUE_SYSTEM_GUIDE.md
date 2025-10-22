# Work Queue System - Complete Guide

**Implemented**: October 2025
**Version**: 1.0
**Status**: Production Ready ✅

## Overview

The Work Queue System replaces dynamic strategy selection with a simple, predictable TODO list approach. Units are processed in chronological + echelon order, ensuring bottom-up aggregation (divisions before corps before armies).

## Benefits

✅ **Prevents AI drift/hallucination** - 12-unit sessions keep quality high
✅ **Predictable order** - Always know what's next
✅ **Bottom-up aggregation** - Process divisions before corps
✅ **Discovery system** - Agents report units missing from seed
✅ **Dependency validation** - Catches parent-before-child issues
✅ **Session tracking** - Automatic counter prevents overwork

## Quick Reference

### Start a Session
```bash
npm run session:start
```

Displays:
- Overall progress (244/420 units)
- Session progress (0/12 units)
- Next 3 units to process
- Quarter completion dashboard

### Process Units
Work the next 3 units from WORK_QUEUE.md, then:
```bash
npm run checkpoint
```

This:
- Validates completed units
- Checks MDBook chapters exist
- Increments session counter (+3)
- Regenerates work queue
- Commits to git

### End Session
```bash
npm run session:end
```

This:
- Creates final checkpoint
- Resets session counter to 0
- Updates progress tracking
- Generates session summary

### Discovery Workflow
If agents find units not in seed:
```bash
npm run discover:scan    # Scan for discoveries
# Review DISCOVERED_UNITS.md and mark approved units [x]
npm run discover:add     # Add to queue
```

### Validation
Check for dependency issues:
```bash
npm run queue:validate
# Review BLOCKED_UNITS.md for warnings
```

---

## Phase 1: Work Queue Core

### Components

**1. Work Queue Generator** (`scripts/generate_work_queue.js`)
- Reads seed file (420 unit-quarters)
- Loads completion status from WORKFLOW_STATE.json
- Sorts chronologically (1940-Q2 → 1943-Q2)
- Sorts by echelon (division → corps → army)
- Outputs WORK_QUEUE.md with next 3 units prominent

**2. Session Start** (`scripts/session_start.js`)
- Reads next 3 units from WORK_QUEUE.md
- Checks session counter (blocks if ≥12)
- Displays progress dashboard
- Generates session prompt

**3. Checkpoint** (`scripts/create_checkpoint.js`)
- Scans canonical directory for completed units
- Validates unit JSONs
- Checks MDBook chapters
- Increments session counter
- Regenerates work queue
- Commits to git

**4. Session End** (`scripts/session_end.js`)
- Creates final checkpoint
- Resets session counter to 0
- Updates Memory MCP
- Generates session summary

### Session Limit Enforcement

**12-Unit Limit**: Prevents AI drift/hallucination after processing too many units.

**Flow**:
1. Session starts: `current_session_count = 0`
2. Process 3 units → checkpoint → counter = 3
3. Process 3 units → checkpoint → counter = 6
4. Process 3 units → checkpoint → counter = 9
5. Process 3 units → checkpoint → counter = 12
6. Session start: **BLOCKS** with message to run session:end

**Benefits**:
- Prevents quality degradation
- Forces breaks between batches
- Ensures checkpoints happen
- Maintains consistent quality

---

## Phase 2: Discovery System

### How Discoveries Work

During extraction, agents may find units NOT in the seed file:
- Additional quarters (unit active longer than seed listed)
- Parent units (corps mentioned in division document)
- Sibling units (other divisions under same corps)
- Completely new units (missed in seed creation)

### Agent Reporting

Agents add `discovered_units` array to unit JSON:

```json
{
  "schema_type": "division_toe",
  "schema_version": "3.1.0",
  "nation": "italian",
  "quarter": "1940q3",
  "unit_designation": "Brescia Division",
  ...
  "discovered_units": [
    {
      "designation": "XXI Corpo d'Armata (XXI Corps)",
      "nation": "italian",
      "quarter": "1940q3",
      "type": "corps",
      "source": "Tessin Vol 12, page 245",
      "confidence": 85,
      "reason": "Parent corps for Brescia Division, not in seed file"
    }
  ]
}
```

### Discovery Workflow

```
1. Agent extracts unit
   ↓
2. Finds reference to unit not in seed
   ↓
3. Adds to discovered_units array
   ↓
4. Checkpoint runs (no action on discoveries yet)
   ↓
5. User runs: npm run discover:scan
   ↓
6. DISCOVERED_UNITS.md generated with all discoveries
   ↓
7. User reviews and marks approved units [x]
   ↓
8. User runs: npm run discover:add
   ↓
9. Approved units added to seed file
   ↓
10. Work queue regenerated
   ↓
11. Next session processes new units
```

### Components

**1. Collect Discoveries** (`scripts/collect_discoveries.js`)
- Scans all completed unit JSONs
- Finds units with `discovered_units` field
- Groups by type (additional quarter, hierarchy, new unit)
- Generates DISCOVERED_UNITS.md for manual review

**2. Add to Queue** (`scripts/add_discovered_to_queue.js`)
- Reads DISCOVERED_UNITS.md
- Finds units marked `[x] Add to queue`
- Adds to seed file (or adds quarter to existing unit)
- Regenerates work queue
- Marks discoveries as added

### Quality Standards

**Good Discovery**:
```json
{
  "designation": "XXI Corpo d'Armata",
  "nation": "italian",
  "quarters": ["1940q3", "1940q4"],
  "type": "corps",
  "source": "Tessin Vol 12, page 245",
  "confidence": 90,
  "reason": "Parent corps active in additional quarters"
}
```

**Bad Discovery**:
```json
{
  "designation": "Unknown unit",
  "nation": "italian",
  "quarter": "1940q3",
  "type": "division",
  "source": "somewhere",
  "confidence": 30,
  "reason": "not sure"
}
```

---

## Phase 3: Validation & Safety

### Dependency Checking

The validator checks for:

**1. Parent Before Child**
- Corps scheduled for extraction before divisions complete
- Army scheduled before corps complete
- **Action**: Skip parent or process children first

**2. Orphaned Units**
- Divisions with no parent corps in queue or completed
- **Note**: May be intentional (independent divisions)
- **Action**: Verify historical accuracy or add parent

**3. Missing Prerequisites** (future)
- Units requiring specific equipment/personnel not yet available
- **Action**: Process prerequisites first

### Validation Workflow

```bash
npm run queue:validate
```

Output: BLOCKED_UNITS.md with detailed issues and recommendations.

**Example Issue**:
```markdown
### italian_1941q2_xxi_corps (corps)

**Problem**: Scheduled for extraction but has incomplete children

**Incomplete children**:
- Brescia Division
- Pavia Division
- Trieste Division

**Action**: Process children first, or skip this unit until next session
```

### Components

**Validate Work Queue** (`scripts/validate_work_queue.js`)
- Parses WORK_QUEUE.md
- Gets completed units from canonical directory
- Checks parent-child relationships
- Identifies orphaned units
- Generates BLOCKED_UNITS.md

---

## Phase 4: Polish & Integration

### NPM Scripts

All queue commands are available via `npm run`:

```bash
# Session management
npm run session:start          # Start new session
npm run session:end            # End session, reset counter
npm run checkpoint             # Save progress

# Queue management
npm run queue:generate         # Regenerate work queue
npm run queue:validate         # Check dependencies

# Discovery workflow
npm run discover:scan          # Scan for discoveries
npm run discover:add           # Add approved discoveries

# Validation
npm run validate:queue         # Alias for queue:validate
```

### Auto-Regeneration

Work queue automatically regenerates:
- After every checkpoint (updates completion status)
- After adding discovered units (new units in queue)
- Can be manually triggered: `npm run queue:generate`

### Session Analytics

Session counter tracked in WORKFLOW_STATE.json:
- Starts at 0 each session
- Increments by batch size on checkpoint
- Blocks session:start when ≥12
- Resets to 0 on session:end

---

## File Structure

```
north-africa-toe-builder/
├── WORK_QUEUE.md                    # Main work queue
├── DISCOVERED_UNITS.md              # Pending discoveries
├── BLOCKED_UNITS.md                 # Dependency warnings
├── WORKFLOW_STATE.json              # Progress tracking
│
├── scripts/
│   ├── generate_work_queue.js       # Phase 1: Generator
│   ├── session_start.js             # Phase 1: Session start
│   ├── create_checkpoint.js         # Phase 1: Checkpoint
│   ├── session_end.js               # Phase 1: Session end
│   ├── collect_discoveries.js       # Phase 2: Discovery scan
│   ├── add_discovered_to_queue.js   # Phase 2: Add to queue
│   ├── validate_work_queue.js       # Phase 3: Validation
│   └── lib/
│       └── state_validator.js       # Auto-repair state
│
├── docs/
│   └── DISCOVERY_GUIDELINES.md      # Agent discovery guide
│
└── schemas/
    └── unified_toe_schema.json      # Updated with discovered_units
```

---

## Workflow Examples

### Example 1: Standard Session

```bash
# Start session
npm run session:start
# Shows: Next 3 units, session 0/12

# Process units (in Claude Code chat)
# ... agents extract 3 units ...

# Checkpoint
npm run checkpoint
# Session counter: 0 → 3

# Process another batch
# ... agents extract 3 units ...

# Checkpoint
npm run checkpoint
# Session counter: 3 → 6

# Process another batch
# ... agents extract 3 units ...

# Checkpoint
npm run checkpoint
# Session counter: 6 → 9

# Process final batch
# ... agents extract 3 units ...

# Checkpoint
npm run checkpoint
# Session counter: 9 → 12

# Try to start another batch
npm run session:start
# BLOCKED: Session limit reached (12 units)

# End session
npm run session:end
# Session counter reset to 0
```

### Example 2: Discovery Workflow

```bash
# During extraction, agent finds XXI Corps in additional quarters
# Agent adds to discovered_units array in Brescia Division JSON

# After session ends, scan for discoveries
npm run discover:scan
# Output: Found 3 discoveries

# Review DISCOVERED_UNITS.md
# Mark XXI Corps quarters as [x] Add to queue

# Add to queue
npm run discover:add
# Adds XXI Corps to seed file
# Regenerates work queue
# Shows XXI Corps in next available slots
```

### Example 3: Handling Blocked Units

```bash
# Validate queue
npm run queue:validate
# Output: Found 2 issues - parent before child

# Review BLOCKED_UNITS.md
# XXI Corps scheduled but divisions incomplete

# Options:
# 1. Skip XXI Corps this session
# 2. Process divisions first
# 3. Add divisions to queue if missing

# Choose option 2: Process divisions first manually
# (Adjust extraction order in Claude Code)
```

---

## Troubleshooting

### Issue: Session counter won't reset
**Solution**: Run `npm run session:end` to force reset

### Issue: Work queue shows wrong progress
**Solution**: Run `npm run queue:generate` to regenerate

### Issue: Discoveries not appearing
**Check**:
1. Unit JSON has `discovered_units` array
2. Array has proper format (see schema)
3. Confidence ≥60%

### Issue: Validation shows false positives
**Note**: Orphaned units may be intentional (independent divisions).
Review historically and mark as intended if correct.

---

## Future Enhancements

Potential improvements:
- Auto-validation before session start
- Smart queue reordering based on dependencies
- Discovery confidence thresholds
- Session analytics dashboard
- Queue branching (multiple strategies)

---

## Summary

The Work Queue System provides:
✅ Simple, predictable workflow
✅ Prevention of AI drift (12-unit limit)
✅ Bottom-up aggregation (divisions before corps)
✅ Discovery reporting and integration
✅ Dependency validation
✅ Progress tracking and analytics

**Result**: High-quality unit extraction with minimal manual intervention and maximum consistency.

---

**Version**: 1.0 (October 2025)
**Status**: Production Ready
**Tested**: All phases working correctly
