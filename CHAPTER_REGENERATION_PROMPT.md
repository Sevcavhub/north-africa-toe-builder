# Chapter Regeneration to v2.0 Standard - Autonomous Task

**Status:** Ready for autonomous execution
**Priority:** High - Required before new unit extraction
**Estimated Time:** 30-45 minutes

---

## Context

The MDBook template and book_chapter_generator agent have been synchronized to **v2.0 standard (16 sections)**. Existing chapters were created under older standards and need updating to match.

**What Changed:**
- Template updated: `docs/MDBOOK_CHAPTER_TEMPLATE.md` (committed: dd8c7d5)
- Agent updated: `agents/agent_catalog.json` book_chapter_generator
- All future chapters will automatically use v2.0
- Existing chapters need manual regeneration

---

## Chapters Requiring Updates

### Group A: 7th Armoured Division (British) - v1.0 → v2.0

**File:** `data/output/autonomous_1760133539236/north_africa_book/src/chapter_7th_armoured.md`

**Current Status:** 14 sections (v1.0 baseline)
**Missing Sections:**
- **Section 3: Command** (was not required when originally created)
  - Commander: Major-General Michael O'Moore Creagh
  - HQ location and staff details from JSON
- **Section 15: Data Quality & Known Gaps** (QA requirement added later)
  - Confidence score: 85%
  - Source tier information
  - Known gaps by priority

**Action Required:** Add sections 3 and 15, renumber existing sections appropriately

---

### Group B: Italian Divisions - v1.5 → v2.0

**Files to Update:**
1. `data/output/autonomous_1760155681040/north_africa_book/src/chapter_italy_1940q4_ariete.md`
2. `data/output/autonomous_1760155681040/north_africa_book/src/chapter_italy_1940q4_trento.md`
3. `data/output/autonomous_1760155681040/north_africa_book/src/chapter_italy_1940q4_savona.md`
4. `data/output/autonomous_1760155681040/north_africa_book/src/chapter_italy_1940q3_pavia.md`
5. `data/output/autonomous_1760155681040/north_africa_book/src/chapter_italy_1941q1_bologna.md`
6. `data/output/autonomous_1760155681040/north_africa_book/src/chapter_italy_1942q1_littorio.md`
7. `data/output/autonomous_1760155681040/north_africa_book/src/chapter_italy_1942q2_littorio.md`
8. `data/output/autonomous_1760155681040/north_africa_book/src/chapter_italy_1942q3_littorio.md`
9. `data/output/autonomous_1760155681040/north_africa_book/src/chapter_italy_1942q3_folgore.md`
10. `data/output/autonomous_1760155681040/north_africa_book/src/chapter_trieste_1941q2.md`

**Current Status:** 15 sections (v1.5 - has Command + Data Quality)
**Missing Section:**
- **Section 12: Critical Equipment Shortages** (operational reality section from 7th Armoured)
  - Identify mission-limiting equipment deficiencies
  - Priority 1: Critical shortages (with required/available/impact/mitigation)
  - Priority 2: Important shortages
  - Priority 3: Minor shortages
  - Overall assessment

**Action Required:** Insert section 12 between "Tactical Doctrine" and "Historical Context", renumber remaining sections

---

## Step-by-Step Execution Plan

### Phase 1: Read and Understand Template
1. Read `docs/MDBOOK_CHAPTER_TEMPLATE.md` completely - **THIS IS THE AUTHORITATIVE STANDARD**
2. Note the 16-section structure
3. Understand Critical Equipment Shortages format (lines 333-372)
4. Understand Data Quality & Known Gaps format (lines 390-447)
5. **Reference chapters (7th Armoured, Bologna, Ariete) are EXAMPLES only, not standards**

### Phase 2: Process 7th Armoured Division
1. Read existing chapter: `data/output/autonomous_1760133539236/north_africa_book/src/chapter_7th_armoured.md`
2. Read corresponding JSON (if available) for commander/confidence data
3. **Add Section 3: Command** after Division Overview
   - Extract commander info from existing overview text
   - Add HQ location, staff structure
   - Format per template lines 44-61
4. **Add Section 15: Data Quality & Known Gaps**
   - Confidence score: 85% (from metadata)
   - List sources used
   - Document known gaps (brigade commanders, exact equipment distributions)
   - Format per template lines 390-447
5. **Renumber** existing sections 3-14 to become 5-16
6. **Validate** all 16 sections present
7. **Save** updated chapter

### Phase 3: Process Italian Chapters (10 files)
For each Italian chapter file:
1. Read existing chapter
2. Identify section 11 (Tactical Doctrine & Capabilities)
3. **Insert new Section 12: Critical Equipment Shortages** after section 11
   - Analyze equipment from chapter tables
   - Identify shortages vs. doctrine requirements
   - Create Priority 1/2/3 lists
   - Format per template lines 333-372
   - Example shortages:
     - **Priority 1:** Modern AT guns, tanks vs. German/British equivalents
     - **Priority 2:** Transport vehicles, artillery pieces
     - **Priority 3:** WITW IDs, specific equipment variants
4. **Renumber** sections 12-15 to become 13-16
5. **Validate** all 16 sections present with correct numbers
6. **Save** updated chapter

### Phase 4: Validation
For each updated chapter:
- [ ] Section 1: Header ✓
- [ ] Section 2: Division Overview ✓
- [ ] Section 3: Command ✓
- [ ] Section 4: Personnel Strength ✓
- [ ] Sections 5-8: Equipment (Armoured, Artillery, Armoured Cars, Infantry, Transport) ✓
- [ ] Section 9: Organizational Structure ✓
- [ ] Section 10: Supply Status ✓
- [ ] Section 11: Tactical Doctrine ✓
- [ ] Section 12: Critical Equipment Shortages ✓
- [ ] Section 13: Historical Context ✓
- [ ] Section 14: Wargaming Data ✓
- [ ] Section 15: Data Quality & Known Gaps ✓
- [ ] Section 16: Conclusion with Data Source Footer ✓

### Phase 5: Git Commit
After all chapters updated:
```bash
npm run git:commit "v2.0 chapter regeneration - 11 chapters updated"
```

Commit message should include:
- Number of chapters updated
- Sections added
- v1.0 → v2.0 or v1.5 → v2.0

---

## Quality Standards

### Critical Equipment Shortages Section (Section 12)
- Must identify REALISTIC shortages based on historical context
- Priority 1: Only truly mission-limiting deficiencies
- Include specific numbers (required vs. available)
- Explain operational impact
- Describe how unit compensates
- Use historical sources where possible

### Data Quality & Known Gaps Section (Section 15)
- Be HONEST about data confidence
- List ALL sources consulted
- Categorize gaps by severity (Important/Moderate/Low)
- Be SPECIFIC about what's missing (not vague)
- Note what HAS been verified
- Suggest research improvements

---

## Error Handling

**If chapter file not found:**
- Log warning
- Continue to next chapter
- Report missing files at end

**If section identification unclear:**
- Use section headers (##) to identify sections
- Count from top to bottom
- If ambiguous, read entire chapter first

**If JSON file missing:**
- Use chapter text as source
- Extract info from existing narrative
- Mark confidence as "based on chapter text only"

---

## Expected Output

**11 updated chapter files:**
- 1 x British (7th Armoured) - v1.0 → v2.0 (added 2 sections)
- 10 x Italian - v1.5 → v2.0 (added 1 section)

**All chapters validated against:**
- 16-section template structure
- Format requirements (bold, ↳ symbols, tables)
- Content quality (realistic shortages, honest gaps)

**Git commit created:**
- Descriptive message
- All 11 files staged
- Pushed to GitHub

---

## Success Criteria

- [ ] All 11 chapters have exactly 16 sections
- [ ] Section numbering consistent across all chapters
- [ ] Critical Equipment Shortages are realistic and well-researched
- [ ] Data Quality & Known Gaps are honest and specific
- [ ] All chapters pass quality checklist
- [ ] Git commit successful
- [ ] No chapters left in inconsistent state

---

## Notes for Autonomous Session

- **Use TodoWrite** to track progress through 11 chapters
- **Read template first** before starting updates
- **Process 7th Armoured separately** (different updates than Italian)
- **Be methodical** - update one chapter at a time
- **Validate each** before moving to next
- **Don't guess** - use chapter text and historical knowledge
- **Commit after all 11** are updated, not individually

---

## Next Steps After Completion

After all chapters updated to v2.0:
1. Run QA Auditor validation
2. Verify all chapters pass template compliance
3. Resume normal unit extraction with v2.0 standard
4. All new chapters will automatically use v2.0 (agent updated)

---

**Ready to Execute:** Yes
**Autonomous Session:** Can start immediately
**Estimated Completion:** 30-45 minutes (batch processing)

---

Generated: 2025-10-11
Template Version: v2.0
Agent Version: book_chapter_generator (synchronized dd8c7d5)
