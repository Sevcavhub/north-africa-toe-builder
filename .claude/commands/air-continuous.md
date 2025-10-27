---
description: Run continuous AIR FORCES extraction until queue is empty (NO STOPPING)
---

node scripts/session_start.js --air-forces

# CONTINUOUS MODE - AIR FORCES - DO NOT STOP UNTIL COMPLETE

**CRITICAL**: This command runs autonomous AIR FORCES extraction in continuous mode. You MUST continue processing until WORK_QUEUE_AIR.md is completely empty or you encounter an actual error.

## What This Does

Launches air forces extraction which processes WORK_QUEUE_AIR.md in batches of 3 squadrons/gruppen/gruppi until ALL remaining air units are complete.

## Strict Rules for Claude

When this command is active:

1. ✅ **MUST CONTINUE**: Process batches of 3 air units continuously
2. ❌ **DO NOT** run `npm run session:end` yourself - handle checkpoints only
3. ❌ **DO NOT** ask "would you like me to continue?"
4. ❌ **DO NOT** stop after a "good number" of units
5. ❌ **DO NOT** worry about token usage in continuous mode
6. ✅ **ONLY STOP IF**:
   - WORK_QUEUE_AIR.md is empty (no air units remaining)
   - Critical error blocks progress (file system issues, schema validation failures, etc.)
   - User explicitly tells you to stop

## How It Works

1. Script shows you the next 3 air units from WORK_QUEUE_AIR.md (ECHELON-FIRST order)
2. You launch 3 parallel Task tool agents (one per squadron/gruppe/gruppo)
3. Agents extract using air_forces_agent_catalog.json specialized agents
4. Script verifies completion and runs checkpoint automatically
5. Script immediately loads next batch from WORK_QUEUE_AIR.md
6. REPEAT until queue is empty

## Expected Behavior

```
Batch 1 (3 air units) → extraction → checkpoint → Batch 2 (3 air units) → extraction → checkpoint → ... → Queue Empty
```

**NO PAUSING BETWEEN BATCHES**

## AIR FORCE SCHEMA COMPLIANCE

**MANDATORY - Aircraft Variant Specificity**:
- ✅ "Messerschmitt Bf 109E-7/Trop" with full specs
- ❌ "Bf 109" (REJECTED - too generic)
- ✅ "Supermarine Spitfire Mk Vb/Trop"
- ❌ "Spitfire" (REJECTED - no variant)
- ✅ "Fiat CR.42 Falco Serie II"
- ❌ "CR.42" (REJECTED - no series designation)

**Aircraft Entry Requirements**:
- Full manufacturer name (Messerschmitt, Hawker, Macchi, etc.)
- Complete model designation (Bf 109E-7, Hurricane Mk IIB, MC.202, etc.)
- Variant/Series suffix (Ausf, Mk, Serie, /Trop, etc.)
- WITW ID from _airgroup.csv database
- Squadron strength (operational + damaged + reserve = total)

**Echelon-First Ordering**:
- Staffeln/Squadrons first (9-18 aircraft)
- Then Gruppen/Gruppi (27-40 aircraft)
- Then Groups/Geschwader/Wings (50-80 aircraft)
- Then Command units (Fliegerkorps, DAF HQ, etc.)

## Canonical Paths (Air Forces - Phase 7)

**ALWAYS use these paths**:
- JSON: `data/output/air_units/[nation]_[quarter]_[unit]_toe.json`
- Chapters: `data/output/air_chapters/chapter_[nation]_[quarter]_[unit].md`

**Nation values** (CANONICAL):
- `german` - Luftwaffe
- `italian` - Regia Aeronautica
- `british` - RAF & Commonwealth (includes RAAF, RNZAF, SAAF, etc.)
- `american` - USAAF

**Examples**:
- `german_1941q2_jg27_3_staffel_toe.json`
- `british_1942q1_no_112_squadron_raf_toe.json`
- `italian_1941q3_150_gruppo_autonomo_ct_toe.json`

## Designed For

- Overnight unattended runs
- Processing 20-60+ air squadrons/gruppen in one session
- Crash-resistant (checkpoint after each batch saves progress)
- Phase 7 air forces completion (761 unit-quarters total)

## What User Expects

User ran this command expecting you to continue until WORK_QUEUE_AIR.md is empty. Don't stop early.

## Progress Tracking

Total air forces scope: **761 unit-quarters** (142 unique squadrons/gruppen/gruppi)
- Luftwaffe: 28 units
- Regia Aeronautica: 29 units
- RAF/Commonwealth: 62 squadrons
- USAAF: 23 groups

Monitor WORKFLOW_STATE.json for current progress.
