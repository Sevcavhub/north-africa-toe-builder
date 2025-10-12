# STRICT AUTONOMOUS MODE - North Africa TO&E Builder
## Session Continuation Prompt for Ken

**Status:** v2.0 Template Synchronized | Chapter Regeneration Complete/In Progress
**Mission:** Continue autonomous extraction toward 213 total units

---

## 🎯 IMMEDIATE FIRST ACTIONS

1. **Start session with context restoration:**
   ```bash
   npm run session:start
   ```
   This displays:
   - Progress from WORKFLOW_STATE.json (56/213 units complete)
   - Known patterns from previous sessions
   - Workflow decisions (3-3-3 rule, agent limits)
   - Suggested next 3-unit batch

2. **Review workflow state:**
   ```bash
   cat WORKFLOW_STATE.json
   ```
   Shows completed units, in-progress work, last commit

3. **Check current status:**
   ```bash
   cat CURRENT_STATUS.md
   ```

4. **Review priorities:**
   ```bash
   cat GAP_TRACKER.md
   ```

5. **Check if chapter regeneration complete:**
   - Read `CHAPTER_REGENERATION_PROMPT.md` status
   - Verify 11 chapters updated to v2.0 (1 British + 10 Italian)
   - If not complete: finish chapter regeneration first

---

## 📚 REQUIRED READING (in order)

### 1. Project Configuration & Standards ⭐ READ THESE FIRST
- **`docs/MDBOOK_CHAPTER_TEMPLATE.md`** - v2.0 standard (16 sections) ⭐ **THE LAW - AUTHORITATIVE STANDARD**
- **`agents/agent_catalog.json`** - book_chapter_generator agent (synchronized to v2.0)
- **`schemas/unified_toe_schema.json`** - JSON structure requirements

### 2. Current Session State
- **`WORKFLOW_STATE.json`** - ⭐ Live progress tracker (56/213 units complete)
- **`CURRENT_STATUS.md`** - Latest progress, units completed, confidence scores
- **`SESSION_HANDOFF_2025-10-10_STRICT.md`** - Complete workflow instructions
- **`GAP_TRACKER.md`** - Known gaps and research priorities
- **`scripts/MEMORY_SYSTEM.md`** - Cross-session knowledge retention

### 3. Template Synchronization Updates
- **`CHAPTER_REGENERATION_PROMPT.md`** - Chapter upgrade task (completed)
- **Git log:** `git log --oneline -5` to see recent commits

### 4. Example Compliant Chapters (v2.0)
- **`data/output/autonomous_1760133539236/north_africa_book/src/chapter_7th_armoured.md`** (British, 713 lines)
- **`data/output/autonomous_1760155681040/north_africa_book/src/chapter_italy_1941q1_bologna.md`** (Italian, 1000+ lines)
- **`data/output/autonomous_1760155681040/north_africa_book/src/chapter_italy_1940q4_ariete.md`** (Italian armored, 700+ lines)

**These are EXAMPLES demonstrating template compliance, NOT the standard itself. Always follow `MDBOOK_CHAPTER_TEMPLATE.md`.**

---

## 🔄 SESSION MANAGEMENT PROTOCOL

### Session Start (REQUIRED)
Every new session or continuation MUST begin with:
```bash
npm run session:start
```

**This automatically:**
- Reads WORKFLOW_STATE.json to show progress (56/213 units complete)
- Queries memory system for known patterns, decisions, quality issues
- Suggests next 3-unit batch based on completion status
- Creates SESSION_ACTIVE.txt marker for tracking
- Displays recent completions and remaining work

**Memory System Context Restored:**
- **Patterns**: Quality trends discovered (e.g., "80% units have estimated battalion TO&E")
- **Decisions**: Workflow choices made (e.g., "2-3 agents max for stability", "3-3-3 rule")
- **Quality Issues**: Validation failures and data conflicts from previous sessions
- **Session Stats**: Completion rates, durations, performance metrics

### Checkpoint System (AUTOMATIC)
**Autonomous orchestrator automatically creates checkpoints after every 3-unit batch:**

```bash
# Checkpoint automatically runs after each 3-unit batch
npm run checkpoint
```

**Checkpoint does:**
- Scans `data/output/` for completed unit JSON files
- Updates WORKFLOW_STATE.json with current progress
- Creates SESSION_CHECKPOINT.md with recovery instructions
- Commits all changes to git with descriptive message
- Maximum 1 unit lost if crash occurs (<5 min recovery time)

### Session End (REQUIRED)
Always end sessions cleanly with:
```bash
npm run session:end
```

**This automatically:**
- Creates final checkpoint (if uncommitted work exists)
- Stores session statistics to memory system
- Stores patterns/decisions/issues discovered during session
- Generates SESSION_SUMMARY.md with progress report
- Validates no uncommitted changes remain
- Cleans up SESSION_ACTIVE.txt marker

**Session Summary includes:**
- Duration and units completed this session
- Progress percentage (current: 26.3% = 56/213)
- Uncommitted files warning (if any)
- Instructions for resuming next session

### Crash Recovery
If session crashes (VS Code restart, network disconnect, etc.):

1. **Check last checkpoint:**
   ```bash
   cat SESSION_CHECKPOINT.md
   cat WORKFLOW_STATE.json
   ```

2. **Review what was completed:**
   - WORKFLOW_STATE.json shows last successful commit
   - Maximum 1-2 units lost (current batch only)

3. **Resume work:**
   ```bash
   npm run session:start  # Loads all context
   # Continue with next batch
   ```

4. **If needed, manual checkpoint:**
   ```bash
   npm run checkpoint "crash_recovery"
   ```

### Memory System Commands
View accumulated knowledge across all sessions:

```bash
# View statistics (patterns, decisions, quality issues)
npm run memory:stats

# Export for backup or sharing
npm run memory:export [filepath]

# Clear cache (testing/reset only)
npm run memory:clear
```

**Memory data stored in:** `.memory_cache/` (local fallback) or Memory MCP (when available)

### 3-3-3 Rule (PROVEN STABLE)
- **3 units per batch** - Process in groups of 3
- **3 batches per session** - Maximum 9 units before long break
- **3 hour blocks** - Limit autonomous runs to 3 hours
- **Checkpoints after each batch** - Automatic via orchestrator
- **2-3 agents max** - More agents (4-6) caused crashes

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

### Phase 1: Chapter Regeneration Status
```bash
# Verify all chapters v2.0 compliant (completed)
# 1 British + 10 Italian = 11 chapters updated
```

**Chapter regeneration is COMPLETE.** All existing chapters now v2.0 compliant with 16 sections.

### Phase 2: Unit Extraction (Batch Processing)
1. **Batch size:** 3 units per run (3-3-3 rule)
2. **Validate EACH unit** immediately after generation
3. **If validation fails:** STOP, regenerate with corrections, re-validate
4. **Automatic checkpoint:** After EVERY 3-unit batch (orchestrator handles this)
   - Updates WORKFLOW_STATE.json
   - Creates SESSION_CHECKPOINT.md
   - Commits to git automatically
5. **After 9 units (3 batches):** Take break, run QA audit
   ```bash
   npm run validate
   npm run memory:stats  # Check accumulated knowledge
   ```

### Phase 3: Intelligent Unit Selection

**DO NOT follow rigid nation order. Instead, evaluate:**

1. **Check Current Status:**
   ```bash
   cat CURRENT_STATUS.md
   ```
   - Which nations have units completed?
   - What's the completion percentage per nation?
   - Are there incomplete/in-progress units?

2. **Review Gap Analysis:**
   ```bash
   cat GAP_TRACKER.md
   ```
   - Which units have confidence < 80%?
   - Which nations have critical gaps?
   - Are there pattern problems to address?

3. **Evaluate Source Availability:**
   - Check `sources/sources_catalog.json` for available documents
   - Tier 1 sources (Tessin, Army Lists, Field Manuals) = prioritize
   - Missing sources for nation/quarter = defer or use Tier 2/3

4. **Strategic Decision Criteria:**
   - **Finish what's started**: Complete in-progress work first
   - **Fill gaps**: Units with low confidence need re-extraction
   - **Source-driven**: Process nations with best source availability
   - **Balance**: Don't complete one nation 100% while others at 0%
   - **Historical coherence**: Related units (same corps, same campaign) together

5. **Autonomous Decision:**
   - Read project config: `projects/north_africa_campaign.json`
   - Analyze completion vs total units per nation
   - Select next batch (3-5 units) based on above criteria
   - Document decision in session log

**Example Good Decision:**
```
Status Check:
- Italian: 17/42 units (40% complete, Tier 1 Tessin sources available)
- British: 1/65 units (1.5% complete, Tier 1 Army Lists available)
- German: 0/78 units (0% complete, Tier 1 Tessin sources available)

Decision: Process 5 German units (Panzer divisions 1940-1941)
Rationale: Balance nations (British/Italian both started, German at 0%),
excellent Tier 1 source availability (Tessin), high strategic value (Panzer
divisions critical to North Africa campaign), historical coherence (early-war
Panzers deployed together)
```

**Example Bad Decision:**
```
Decision: Complete all 42 Italian units before touching other nations
Problem: Creates imbalanced dataset, delays British/German extraction,
ignores source availability patterns, no strategic rationale
```

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

**Automatic Checkpoints (RECOMMENDED):**
The autonomous orchestrator automatically commits after every 3-unit batch via:
```bash
npm run checkpoint  # Called automatically by orchestrator
```

**Checkpoint commits include:**
- Unit JSON files
- MDBook chapters
- WORKFLOW_STATE.json updates
- SESSION_CHECKPOINT.md
- Descriptive commit message with batch summary

**Manual checkpoints (if needed):**
```bash
npm run checkpoint "manual_batch_name"
```

**Session end checkpoint (automatic):**
```bash
npm run session:end  # Creates final checkpoint if uncommitted work exists
```

**DO NOT commit:**
- Temporary files
- Test outputs
- Incomplete work
- .memory_cache/ directory (gitignored)

---

## 🔍 QUALITY ASSURANCE

### Every Unit:
- Self-validate against checklist above
- Check JSON schema compliance
- Verify equipment totals sum correctly
- Confirm all 16 sections present

### Every 3 Units (After Each Batch):
- Automatic checkpoint runs (`npm run checkpoint`)
- WORKFLOW_STATE.json updated automatically
- Git commit created automatically
- Review SESSION_CHECKPOINT.md for confirmation

### Every 9 Units (After 3 Batches):
- Run schema validator: `npm run validate`
- Check memory statistics: `npm run memory:stats`
- Review GAP_TRACKER.md for patterns
- Check confidence score distribution
- Take break before continuing (3-3-3 rule)

### Every 30 Units:
- Run QA Auditor orchestrator
- Generate quality report
- Update CURRENT_STATUS.md
- Review and adjust priorities
- Consider exporting memory: `npm run memory:export`

---

## 🎓 KEY PRINCIPLES

1. **The TEMPLATE is THE LAW** - `MDBOOK_CHAPTER_TEMPLATE.md` is the authoritative standard, not any chapter file
2. **Orchestration-driven selection** - evaluate status/gaps/sources, don't follow rigid nation order
3. **Autonomous does NOT mean unsupervised** - validate everything
4. **Quality over quantity** - 10 perfect units > 50 flawed units
5. **Stop when uncertain** - ask rather than guess
6. **Use v2.0 template** - all new chapters automatically compliant via book_chapter_generator agent
7. **Be honest about gaps** - Section 15 documents what's unknown
8. **Historical accuracy** - no anachronisms, verify equipment dates
9. **Commonwealth = British** - include all Empire/Commonwealth forces
10. **Document decisions** - explain unit selection rationale in session logs

---

## 📁 KEY FILES & LOCATIONS

### Session Management:
- **`WORKFLOW_STATE.json`** - ⭐ Live progress tracker (updated automatically)
- **`SESSION_CHECKPOINT.md`** - Latest checkpoint with recovery instructions
- **`SESSION_SUMMARY.md`** - Generated at session end
- **`SESSION_ACTIVE.txt`** - Active session marker (created by session:start)
- **`.memory_cache/`** - Local memory storage (patterns, decisions, issues)

### Output Directories:
- **Units JSON:** `data/output/autonomous_*/units/*.json`
- **Chapters:** `data/output/autonomous_*/north_africa_book/src/*.md`
- **Session logs:** `data/output/autonomous_*/logs/`

### Configuration:
- **Project config:** `projects/north_africa_campaign.json`
- **Source catalog:** `sources/sources_catalog.json`
- **Agent catalog:** `agents/agent_catalog.json`

### Documentation:
- **Memory system:** `scripts/MEMORY_SYSTEM.md` ⭐ Cross-session knowledge
- **Setup guide:** `docs/AUTONOMOUS_SETUP_GUIDE.md`
- **Workflow guide:** `docs/AUTOMATED_WORKFLOW.md`
- **Source workflow:** `docs/SOURCE_WORKFLOW.md`
- **Git guide:** `docs/GIT_AUTO_COMMIT_GUIDE.md`

---

## 🚀 READY TO START

Confirm you have:
- [ ] Read MDBOOK_CHAPTER_TEMPLATE.md v2.0 completely
- [ ] Reviewed scripts/MEMORY_SYSTEM.md (checkpoint and memory systems)
- [ ] Checked WORKFLOW_STATE.json for progress (56/213 units)
- [ ] Checked CURRENT_STATUS.md for latest details
- [ ] Verified chapter regeneration status
- [ ] Reviewed GAP_TRACKER.md priorities
- [ ] Understood 16-section template requirements
- [ ] Know the validation checklist
- [ ] Understand stop conditions
- [ ] Understand 3-3-3 rule (3 units, 3 batches, 3 hours)

**Then begin with:**
```bash
# ALWAYS START HERE (loads context from previous sessions)
npm run session:start

# Review the suggested next batch and decide:
# If chapter regeneration incomplete:
# Read and execute: CHAPTER_REGENERATION_PROMPT.md

# If chapter regeneration complete:
npm run start:autonomous
# Process 3 units per batch
# Automatic checkpoint after each batch
# Maximum 9 units (3 batches) before break

# ALWAYS END HERE (stores session knowledge)
npm run session:end
```

---

**Template Version:** v2.0 (16 sections)
**Agent Version:** book_chapter_generator (synchronized commit dd8c7d5)
**Checkpoint System:** v1.0 (automatic checkpoints + memory system)
**Current Progress:** 56/213 units (26.3% complete)
**Last Updated:** 2025-10-11
**Session Owner:** Ken
**GitHub:** https://github.com/Sevcavhub/north-africa-toe-builder

**Remember:** You are extracting historical military data with academic rigor. Every unit matters. Every gap must be documented. Quality is non-negotiable.

**Session Protocol:**
1. **START:** `npm run session:start` (loads all context)
2. **WORK:** Process 3-unit batches (automatic checkpoints)
3. **END:** `npm run session:end` (stores all knowledge)

**Crash Recovery:** Maximum 1 unit lost (<5 min recovery). Check WORKFLOW_STATE.json and SESSION_CHECKPOINT.md to resume.

---

Ready? 🎯
