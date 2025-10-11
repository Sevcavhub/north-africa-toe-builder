# STRICT AUTONOMOUS MODE - North Africa TO&E Builder
## Session Continuation Prompt for Ken

**Status:** v2.0 Template Synchronized | Chapter Regeneration Complete/In Progress
**Mission:** Continue autonomous extraction toward 213 total units

---

## 🎯 IMMEDIATE FIRST ACTIONS

1. **Check current status:**
   ```bash
   cat CURRENT_STATUS.md
   ```

2. **Count completed units:**
   ```bash
   find data/output -name "*.json" -path "*/units/*" | wc -l
   ```

3. **Check if chapter regeneration complete:**
   - Read `CHAPTER_REGENERATION_PROMPT.md` status
   - Verify 11 chapters updated to v2.0 (1 British + 10 Italian)
   - If not complete: finish chapter regeneration first

4. **Review priorities:**
   ```bash
   cat GAP_TRACKER.md
   ```

---

## 📚 REQUIRED READING (in order)

### 1. Project Configuration & Standards
- **`docs/MDBOOK_CHAPTER_TEMPLATE.md`** - v2.0 standard (16 sections) ⭐ THE LAW
- **`agents/agent_catalog.json`** - book_chapter_generator agent (synchronized to v2.0)
- **`schemas/unified_toe_schema.json`** - JSON structure requirements

### 2. Current Session State
- **`CURRENT_STATUS.md`** - Latest progress, units completed, confidence scores
- **`SESSION_HANDOFF_2025-10-10_STRICT.md`** - Complete workflow instructions
- **`GAP_TRACKER.md`** - Known gaps and research priorities

### 3. Template Synchronization Updates
- **`CHAPTER_REGENERATION_PROMPT.md`** - Chapter upgrade task (may be complete)
- **Git log:** `git log --oneline -5` to see recent commits

### 4. Reference Baseline
- **`data/output/autonomous_1760133539236/north_africa_book/src/chapter_7th_armoured.md`**
  - 647+ lines, v2.0 compliant (16 sections)
  - Command section included
  - Critical Equipment Shortages documented
  - Data Quality & Known Gaps section complete
  - USE THIS AS GOLD STANDARD

---

## ✅ v2.0 TEMPLATE STANDARD (16 SECTIONS)

Every chapter MUST have:
1. Header (unit designation, nation, quarter, theater)
2. Division/Unit Overview (narrative introduction)
3. **Command** (commander, HQ, staff - REQUIRED)
4. Personnel Strength (table with officers/NCOs/enlisted)
5-8. Equipment Sections (Armoured, Artillery, Armoured Cars, Infantry Weapons, Transport)
   - **Summary tables** with **bold** categories, `↳` variants
   - **Detail sections** for EVERY variant (specs, combat performance, notes)
9. Organizational Structure (subordinate units)
10. Supply Status (fuel, ammunition, food, water, operational radius)
11. Tactical Doctrine & Capabilities (role, innovations, limitations)
12. **Critical Equipment Shortages** (Priority 1/2/3 shortages, impact, mitigation)
13. Historical Context (formation, operations, key events)
14. Wargaming Data (morale, experience, special rules, scenarios)
15. **Data Quality & Known Gaps** (confidence score, sources, gaps by priority)
16. Conclusion (assessment + data source footer)

---

## 🚨 MANDATORY VALIDATION CHECKLIST

After EVERY unit chapter generated:

### Equipment Sections
- [ ] **Artillery**: Summary table + detail section for EVERY variant
  - [ ] Caliber, range, projectile weight, rate of fire documented
  - [ ] Combat performance narrative for each variant
- [ ] **Armored Cars**: SEPARATE section (not in Transport)
  - [ ] Detail section for EVERY variant (armament, armor, crew, speed, combat record)
- [ ] **Transport & Vehicles**: NO tanks or armored cars in this section
  - [ ] Detail section for EVERY truck/motorcycle/carrier variant
- [ ] **Bold** for category totals, `↳` for variant sub-items
- [ ] Operational readiness percentages calculated correctly

### Required Sections
- [ ] Section 3: Command (commander name, rank, HQ, staff)
- [ ] Section 12: Critical Equipment Shortages (realistic priorities)
- [ ] Section 15: Data Quality & Known Gaps (honest assessment)
- [ ] All 16 sections present and correctly numbered

### Quality Standards
- [ ] Confidence score ≥ 75%
- [ ] Minimum 2 sources per critical fact
- [ ] No placeholder text like "TBD" or "[to be completed]"
- [ ] Variant counts sum to category totals
- [ ] No invented/hallucinated data

---

## 🔄 AUTONOMOUS WORKFLOW

### Phase 1: Complete Chapter Regeneration (if not done)
```bash
# Check if regeneration complete
ls -la data/output/autonomous_*/north_africa_book/src/*.md | wc -l
# Should be 11 chapters updated to v2.0

# If not complete: Read and execute CHAPTER_REGENERATION_PROMPT.md
```

### Phase 2: Unit Extraction (Batch Processing)
1. **Batch size:** 3-5 units per run
2. **Validate EACH unit** immediately after generation
3. **If validation fails:** STOP, regenerate with corrections, re-validate
4. **After 10 units:** Run QA audit (`npm run validate` or manual review)
5. **Git commit:** After every 10 units
   ```bash
   npm run git:commit "Italian batch 4 - 10 units"
   ```

### Phase 3: Priority Order
1. **Incomplete/in-progress work** (check CURRENT_STATUS.md)
2. **Italian units** (42 unit-quarters remaining)
3. **British/Commonwealth** (include India, Australia, NZ, Canada, South Africa)
4. **German units** (Panzer divisions, infantry divisions)
5. **American units** (1942-1943)
6. **French units** (1940-1941)

---

## 🛑 STOP CONDITIONS

Autonomous session MUST STOP and ask if:
1. **Validation fails** after 2 regeneration attempts
2. **Confidence score < 75%** for any unit
3. **Critical gaps** cannot be resolved (missing commander, no equipment data)
4. **Template violations** detected in generated chapters
5. **Source documents unavailable** for nation/quarter
6. **Agent errors** or tool failures occur
7. **Unclear instructions** or ambiguous requirements

---

## ❌ FORBIDDEN ACTIONS

**DO NOT:**
- ❌ Create manual operations or templates
- ❌ Copy/paste from other chapters
- ❌ Skip sections or use stubs
- ❌ Guess data or hallucinate facts
- ❌ Create chapters without corresponding JSON
- ❌ Use placeholder text like "TBD" or "Unknown"
- ❌ Continue if validation fails
- ❌ Commit invalid/incomplete work

---

## 📊 GIT WORKFLOW

**After every 10 units:**
```bash
npm run git:commit "descriptive batch name"
```

**Commit should include:**
- Unit JSON files
- MDBook chapters
- Any agent/template updates

**DO NOT commit:**
- Temporary files
- Test outputs
- Incomplete work

---

## 🔍 QUALITY ASSURANCE

### Every Unit:
- Self-validate against checklist above
- Check JSON schema compliance
- Verify equipment totals sum correctly
- Confirm all 16 sections present

### Every 10 Units:
- Run schema validator: `npm run validate`
- Review GAP_TRACKER.md for patterns
- Check confidence score distribution
- Verify git commits successful

### Every 50 Units:
- Run QA Auditor orchestrator
- Generate quality report
- Update CURRENT_STATUS.md
- Review and adjust priorities

---

## 🎓 KEY PRINCIPLES

1. **Autonomous does NOT mean unsupervised** - validate everything
2. **Quality over quantity** - 10 perfect units > 50 flawed units
3. **Stop when uncertain** - ask rather than guess
4. **Use v2.0 template** - all new chapters automatically compliant
5. **Be honest about gaps** - Section 15 documents what's unknown
6. **Historical accuracy** - no anachronisms, verify equipment dates
7. **Commonwealth = British** - include all Empire/Commonwealth forces

---

## 📁 KEY FILES & LOCATIONS

### Output Directories:
- **Units JSON:** `data/output/autonomous_*/units/*.json`
- **Chapters:** `data/output/autonomous_*/north_africa_book/src/*.md`
- **Session logs:** `data/output/autonomous_*/logs/`

### Configuration:
- **Project config:** `projects/north_africa_campaign.json`
- **Source catalog:** `sources/sources_catalog.json`
- **Agent catalog:** `agents/agent_catalog.json`

### Documentation:
- **Setup guide:** `docs/AUTONOMOUS_SETUP_GUIDE.md`
- **Workflow guide:** `docs/AUTOMATED_WORKFLOW.md`
- **Source workflow:** `docs/SOURCE_WORKFLOW.md`
- **Git guide:** `docs/GIT_AUTO_COMMIT_GUIDE.md`

---

## 🚀 READY TO START

Confirm you have:
- [ ] Read MDBOOK_CHAPTER_TEMPLATE.md v2.0 completely
- [ ] Checked CURRENT_STATUS.md for latest progress
- [ ] Verified chapter regeneration status
- [ ] Reviewed GAP_TRACKER.md priorities
- [ ] Understood 16-section template requirements
- [ ] Know the validation checklist
- [ ] Understand stop conditions

**Then begin with:**
```bash
# If chapter regeneration incomplete:
# Read and execute: CHAPTER_REGENERATION_PROMPT.md

# If chapter regeneration complete:
npm run start:autonomous
# Process 3-5 units, validate each, commit after 10
```

---

**Template Version:** v2.0 (16 sections)
**Agent Version:** book_chapter_generator (synchronized commit dd8c7d5)
**Last Updated:** 2025-10-11
**Session Owner:** Ken
**GitHub:** https://github.com/Sevcavhub/north-africa-toe-builder

**Remember:** You are extracting historical military data with academic rigor. Every unit matters. Every gap must be documented. Quality is non-negotiable.

---

Ready? 🎯
