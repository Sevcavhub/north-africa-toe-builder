# Discovery Guidelines for Agents

**Phase 2 Feature** - October 2025

## Overview

During unit extraction, agents may discover units that were NOT in the original seed file. This is NORMAL and EXPECTED. The discovery system allows agents to report these units for manual review before adding them to the work queue.

## When to Report a Discovery

Report a unit as "discovered" when you find references to:

### 1. Additional Quarters
**Example**: Extracting XXI Corps for 1941-Q2, you find it also existed in 1941-Q3 and 1941-Q4, but seed file only lists 1941-Q2.

```json
{
  "designation": "XXI Corpo d'Armata (XXI Corps)",
  "nation": "italian",
  "quarters": ["1941q3", "1941q4"],
  "type": "corps",
  "source": "Tessin Vol 12, page 342 - mentions XXI Corps active through end of 1941",
  "confidence": 90,
  "reason": "Additional quarters found during extraction - seed file only listed 1941q2"
}
```

### 2. Parent Units
**Example**: Extracting Brescia Division, you find it was part of XXI Corps, but XXI Corps is not in the seed file for that quarter.

```json
{
  "designation": "XXI Corpo d'Armata (XXI Corps)",
  "nation": "italian",
  "quarter": "1940q3",
  "type": "corps",
  "source": "Tessin Vol 12, page 245 - Brescia Division subordinate to XXI Corps",
  "confidence": 85,
  "reason": "Parent corps mentioned in division document but not in seed file for this quarter"
}
```

### 3. Sibling Units
**Example**: Extracting Brescia Division under XXI Corps, you find Pavia Division was also part of XXI Corps, but Pavia is not in seed for this quarter.

```json
{
  "designation": "Pavia Division",
  "nation": "italian",
  "quarter": "1940q3",
  "type": "infantry_division",
  "source": "Tessin Vol 12, page 246 - listed alongside Brescia under XXI Corps",
  "confidence": 90,
  "reason": "Sibling division under same corps, not in seed file for this quarter"
}
```

### 4. Completely New Units
**Example**: Document mentions a unit that doesn't appear in seed file at all.

```json
{
  "designation": "60th Sabratha Division",
  "nation": "italian",
  "quarters": ["1940q3", "1940q4"],
  "type": "infantry_division",
  "source": "Army List October 1940, page 12",
  "confidence": 75,
  "reason": "Division mentioned in source but not in seed file - may be out of geographic scope"
}
```

## When NOT to Report

**DO NOT report:**
- Units already completed (check canonical directory first)
- Units with very low confidence (<60%)
- Temporary formations (battle groups, task forces unless specifically requested)
- Units outside North Africa theater unless clearly relevant
- Minor sub-units (individual companies, platoons unless explicitly in scope)

## How to Report - Add to Unit JSON

Add `discovered_units` array to your output JSON:

```json
{
  "schema_type": "division_toe",
  "schema_version": "3.1.0",
  "nation": "italian",
  "quarter": "1940q3",
  "unit_designation": "Brescia Division",
  ...
  "validation": {
    "source": ["Tessin Vol 12"],
    "confidence": 85,
    ...
  },
  "discovered_units": [
    {
      "designation": "XXI Corpo d'Armata (XXI Corps)",
      "nation": "italian",
      "quarter": "1940q3",
      "type": "corps",
      "source": "Tessin Vol 12, page 245",
      "confidence": 85,
      "reason": "Parent corps for Brescia Division, not in seed file"
    },
    {
      "designation": "Pavia Division",
      "nation": "italian",
      "quarter": "1940q3",
      "type": "infantry_division",
      "source": "Tessin Vol 12, page 246",
      "confidence": 90,
      "reason": "Sibling division under XXI Corps, not in seed file"
    }
  ]
}
```

## Discovery Workflow

1. **Agent extracts unit** → Adds discovered_units to JSON
2. **Checkpoint runs** → No action yet
3. **User runs discovery scan**:
   ```bash
   node scripts/collect_discoveries.js
   ```
4. **Review DISCOVERED_UNITS.md** → Manual verification
5. **Mark approved units** → Change `[ ]` to `[x]`
6. **Add to queue**:
   ```bash
   node scripts/add_discovered_to_queue.js
   ```
7. **Next session** → New units appear in work queue

## Quality Standards

### Good Discovery Report
```json
{
  "designation": "CC.NN. 28 Ottobre Division",
  "nation": "italian",
  "quarters": ["1940q3", "1940q4"],
  "type": "division",
  "source": "Italian Army List September 1940, page 18",
  "confidence": 85,
  "reason": "Blackshirt division active in Libya during this period, not in seed file"
}
```

✅ Clear designation
✅ Specific source with page number
✅ Reasonable confidence
✅ Explains why discovered

### Bad Discovery Report
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

❌ Vague designation
❌ No source details
❌ Too low confidence
❌ Unclear reason

## Confidence Guidelines

- **90-100%**: Found in multiple reliable sources, clearly part of theater
- **75-89%**: Found in one reliable source, likely part of theater
- **60-74%**: Mentioned but unclear if in theater or correct quarter
- **<60%**: Don't report - insufficient evidence

## FAQs

**Q: What if I'm not sure if a unit was in the seed file?**
A: Report it anyway with appropriate confidence. Manual review will catch duplicates.

**Q: Should I report every unit mentioned in the document?**
A: No. Only report units that:
1. Are relevant to North Africa theater
2. Match the scope (usually division-level and above)
3. Have sufficient confidence (≥60%)

**Q: What if I find many discoveries (10+)?**
A: This is fine! It may mean seed file needs regeneration. Report all of them.

**Q: Should I stop extraction to research discovered units?**
A: NO! Just report them and continue with assigned unit. Discoveries will be processed separately.

## Examples from Real Sessions

### Example 1: XXI Corps Additional Quarters
During Brescia Division 1941-Q1 extraction, agent found XXI Corps was active 1940-Q3 through 1941-Q2, but seed only listed 1941-Q1. Agent reported:

```json
"discovered_units": [
  {
    "designation": "XXI Corpo d'Armata (XXI Corps)",
    "nation": "italian",
    "quarters": ["1940q3", "1940q4", "1941q2"],
    "type": "corps",
    "source": "Tessin Vol 12, pages 245-342",
    "confidence": 90,
    "reason": "Corps active in additional quarters beyond seed file scope"
  }
]
```

**Result**: After review, all quarters added to queue. XXI Corps now complete 1940-Q3 through 1941-Q2.

### Example 2: CC.NN. Divisions
During Italian 1940-Q3 extraction, agents found multiple CC.NN. (Blackshirt) divisions not in seed:

```json
"discovered_units": [
  {
    "designation": "1st CC.NN. Division '23 Marzo'",
    "nation": "italian",
    "quarters": ["1940q3", "1940q4"],
    "type": "division",
    "source": "Italian Army List September 1940",
    "confidence": 85,
    "reason": "Blackshirt division active in Libya, not in original seed"
  }
]
```

**Result**: 4 CC.NN. divisions added to queue after verification.

## Summary

✅ **DO** report units you find that aren't in your assignment
✅ **DO** include specific sources and page numbers
✅ **DO** explain why you think unit is missing
✅ **DO** use reasonable confidence levels

❌ **DON'T** stop extraction to research discoveries
❌ **DON'T** report units you're unsure about (<60% confidence)
❌ **DON'T** worry about reporting "too many" - that's useful feedback!

---

**Remember**: Discoveries are NORMAL. Seed files are iterative. Your job is to extract assigned units and report what you find along the way. The discovery system handles the rest!
