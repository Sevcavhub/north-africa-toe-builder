# Cleanup and Reorganization Plan

**Date**: November 5, 2025
**Purpose**: Transform "unorganized clutter" into phase-specific organization
**Status**: 🔴 READY FOR EXECUTION (Awaiting user approval)

---

## 📊 Discovery Summary

**Root Scripts Analyzed**: 152 .js files in `scripts/` directory
**Active Scripts**: 29 (referenced in package.json NPM commands)
**Legacy/Diagnostic Scripts**: 123 (81% of root scripts)
**Empty Folders Found**: 60+ in `data/output/`
**Target**: Phase-specific folder organization

---

## 🎯 Reorganization Strategy

### **Phase-Specific Folders**:
```
scripts/
├── phase_1_4_database/          # Phase 1-4: Database setup
│   └── (1 import script + scraping tools)
├── phase_5_equipment_matching/  # Phase 5: Equipment matching
│   └── (Python tools in tools/ - not affected)
├── phase_5_5_normalization/     # Phase 5.5: Database normalization
│   └── (Already organized in scripts/normalization/ and scripts/linkage/)
├── phase_6_ground_forces/       # Phase 6: Ground forces extraction
│   └── (Session management + queue + validation - 40+ scripts)
├── phase_7_air_forces/          # Phase 7: Air forces extraction
│   └── (15 air-related scripts)
├── phase_9a_witw/               # Phase 9A: WITW scenarios
│   └── (Already organized in scripts/scenario_generation/)
├── phase_9b_battlegroup/        # Phase 9B: BattleGroup books
│   └── (Already organized in scripts/battlegroup/)
├── diagnostic/                  # Diagnostic/analysis tools
│   └── (38 diagnostic scripts - keep for troubleshooting)
├── legacy/                      # Archived scripts (don't delete yet)
│   ├── migration/               # One-time migration scripts (16)
│   ├── testing/                 # Test scripts (3)
│   └── obsolete/                # Truly obsolete (TBD)
└── shared/                      # Shared utilities
    └── (MCP helpers, git, PDF extraction, etc.)
```

---

## 📋 PART 1: Script Categorization (152 Scripts)

### ✅ **PHASE 6: Ground Forces Session Management** (40 scripts - KEEP ACTIVE)

**Session Core** (9 scripts):
```
scripts/phase_6_ground_forces/session_management/
├── session_start.js ───────────────────────── ✅ ACTIVE (npm run session:start)
├── session_end.js ─────────────────────────── ✅ ACTIVE (npm run session:end)
├── process_queue_auto.js ──────────────────── ✅ ACTIVE (npm run auto:continuous)
├── checkpoint_safe.js ─────────────────────── ✅ ACTIVE (npm run checkpoint:safe)
├── create_checkpoint.js ───────────────────── ✅ ACTIVE (npm run checkpoint)
├── resume_paused_unit.js ──────────────────── ✅ ACTIVE (npm run resume)
├── recover_from_crash.js ──────────────────── ✅ ACTIVE (npm run recover)
├── validate_session_readiness.js ──────────── ✅ ACTIVE (npm run session:ready)
└── archive_old_sessions.js ────────────────── ✅ ACTIVE (npm run archive:sessions)
```

**Work Queue Management** (4 scripts):
```
scripts/phase_6_ground_forces/queue/
├── generate_work_queue.js ─────────────────── ✅ ACTIVE (npm run queue:generate)
├── validate_work_queue.js ─────────────────── ✅ ACTIVE (npm run queue:validate)
├── add_discovered_to_queue.js ─────────────── ✅ ACTIVE (npm run discover:add)
└── collect_discoveries.js ─────────────────── ✅ ACTIVE (npm run discover:scan)
```

**Validation & QA** (3 scripts):
```
scripts/phase_6_ground_forces/validation/
├── validate-schema.js ─────────────────────── ✅ ACTIVE (npm run validate:v3)
├── validate-no-wikipedia.js ───────────────── ✅ ACTIVE (npm run validate:sources)
└── qa_audit.js ────────────────────────────── ✅ ACTIVE (via npm run qa:v3)
```

**Content Generation** (9 scripts - REVIEW NEEDED):
```
scripts/phase_6_ground_forces/content_generation/
├── generate_mdbook_chapters.js ────────────── Keep? (chapter generation)
├── generate_single_chapter.js ─────────────── Keep? (single chapter)
├── generate_missing_chapters.js ───────────── Keep? (missing chapters)
├── generate_31_missing_chapters.js ────────── Legacy? (specific batch)
├── generate_toe_diagram.js ────────────────── Keep? (diagram generation)
├── generate_reextraction_batch.js ─────────── Keep? (reextraction batches)
├── generate_complete_seed.js ──────────────── Legacy? (seed generation complete)
├── consolidate_canonical.js ───────────────── ✅ ACTIVE (npm run consolidate)
└── generate_final_expansion_summaries.js ──── Legacy? (expansion summaries)
```

**Seed/Unit Management** (6 scripts - REVIEW NEEDED):
```
scripts/phase_6_ground_forces/unit_management/
├── filter_battle_units.js ─────────────────── Keep? (filter units)
├── enrich_units_with_database.js ──────────── Keep? (database enrichment)
├── backup_all_units.js ────────────────────── Keep? (unit backups)
├── cross_reference_seed.js ────────────────── Keep? (seed cross-reference)
├── update_seed_with_aliases.js ────────────── Legacy? (alias updates)
└── canonical_master_matcher.js ────────────── Keep? (matching system)
```

**Validation Tools** (9 scripts - REVIEW NEEDED):
```
scripts/phase_6_ground_forces/validation/
├── validate_4_units.js ────────────────────── Diagnostic?
├── validate_army_aggregation.js ───────────── Diagnostic?
├── validate_seed_against_authoritative.js ─── Diagnostic?
├── validate_seed_phase1.js ────────────────── Legacy?
├── validate_work_queue.js ─────────────────── ✅ ACTIVE
├── validate_no_wikipedia.js ───────────────── ✅ ACTIVE (duplicate?)
├── validate-no-wikipedia.js ───────────────── ✅ ACTIVE
├── validate-schema.js ─────────────────────── ✅ ACTIVE
└── final_status_check.js ──────────────────── Keep? (final check)
```

### ✈️ **PHASE 7: Air Forces** (15 scripts - MOVE)

```
scripts/phase_7_air_forces/
├── add_air_sections_to_chapters.js
├── add_air_support_to_armies.js
├── add_american_air_support_sections.js
├── add_final_air_support_sections.js
├── add_new_air_support_sections.js
├── create_focused_air_seed.js
├── create_hybrid_air_summaries.js
├── create_ultra_focused_air_seed.js
├── extract_nafziger_air_pdf.js
├── generate_american_air_summaries.js
├── generate_expansion_air_summaries.js
├── generate_quarterly_air_overviews.js
├── generate_work_queue_air.js
├── regenerate_air_summaries_with_wikipedia.js
└── search_nafziger_air_1941.js
```

### 🗄️ **PHASE 1-4: Database Setup** (8 scripts - MOVE TO LEGACY)

**Import Scripts** (1 active):
```
scripts/phase_1_4_database/
└── import_name_variants.js ────────────────── Keep? (Phase 5.5 related)
```

**Scraping Scripts** (7 - mostly one-time use):
```
scripts/legacy/database_setup/
├── scrape_onwar_enhanced.js ───────────────── Legacy (one-time Phase 1-4)
├── scrape_wwiitanks.js ────────────────────── ✅ ACTIVE (npm run scrape:wwiitanks)
├── scrape_wwiitanks_enhanced_guns.js ──────── Legacy (superseded by v2)
├── scrape_wwiitanks_enhanced_guns_v2.js ───── ✅ ACTIVE (npm run scrape:guns:enhanced)
├── scrape_wwiitanks_pagination_test.js ────── ✅ ACTIVE (test - keep?)
├── scrape_wwiitanks_test.js ───────────────── ✅ ACTIVE (test - keep?)
└── scrape_wwiitanks_test_guns.js ──────────── ✅ ACTIVE (test - keep?)
```

### 🔍 **DIAGNOSTIC/ANALYSIS TOOLS** (38 scripts - MOVE)

**These are troubleshooting tools - keep but organize**:
```
scripts/diagnostic/
├── analysis/
│   ├── analyze_british_coverage.js
│   ├── analyze_combat_participation.js
│   ├── analyze_match_quality.js
│   ├── analyze_non_matching_units.js
│   ├── analyze_out_of_scope_origins.js
│   ├── analyze_remaining_seed_units.js
│   ├── analyze_remaining_units.js
│   ├── analyze_sources_comprehensive.js
│   ├── analyze_unit_locations.js
│   └── analyze_unmatched_equipment.js
├── checks/
│   ├── check_1942_missing.js
│   ├── check_database_status.js
│   ├── check_na_enrichment.js
│   ├── check_queue_matching.js
│   ├── check_seed_issues.js
│   └── check_untracked_files.js
├── find/
│   ├── find_duplicates.js
│   ├── find_missing_1941.js
│   ├── find_missing_chapters.js
│   ├── find_missing_coverage.js
│   ├── find_missing_units.js
│   ├── find_non_matching_units.js
│   ├── find_noncanonical_files.js
│   ├── find_orphaned_files.js
│   ├── find_out_of_scope_units.js
│   ├── find_real_duplicates.js
│   └── find_truly_missing_1941.js
├── investigation/
│   ├── investigate_extra_files.js
│   ├── investigate_missing_sources.js
│   ├── investigate_unmatched_units.js
│   ├── identify_43_out_of_scope.js
│   ├── debug_unit_matching.js
│   ├── deep_reconciliation_analysis.js
│   └── diagnose_state_mismatch.js
└── lists/
    ├── list_1940q3_missing.js
    ├── list_1941q1_missing.js
    ├── list_incomplete_units.js
    ├── list_wikipedia_and_no_source_units.js
    ├── show_incomplete_by_unit_name.js
    ├── show_incomplete_units.js
    └── show_seed_by_quarter.js
```

### 🔧 **MIGRATION/FIX SCRIPTS** (16 scripts - MOVE TO LEGACY)

**These are one-time migration scripts - archive but don't delete**:
```
scripts/legacy/migration/
├── batch_fix_conclusions.js ───────────────── One-time fix
├── batch_research_production_dates.js ─────── One-time fix
├── fix_4th_indian_schema.js ───────────────── One-time fix
├── fix_alias_matches.js ───────────────────── One-time fix
├── fix_army_corps_aggregation.js ──────────── One-time fix
├── fix_canonical_naming.js ────────────────── One-time fix
├── fix_confidence_field.js ────────────────── One-time fix
├── fix_quarter_format.js ──────────────────── One-time fix
├── fix_session_start_workflow.js ──────────── One-time fix
├── fix-schema-mismatches.js ───────────────── One-time fix
├── migrate_filenames.js ───────────────────── One-time migration
├── migrate_to_schema_v310.js ──────────────── One-time migration (Phase 6)
├── rebuild_workflow_state.js ──────────────── One-time fix
├── reconcile_workflow_state.js ────────────── One-time fix
├── revert_quarter_format.js ───────────────── One-time fix
└── update_restoration_progress.js ─────────── One-time fix (October 23, 2025)
```

### 🧪 **TEST SCRIPTS** (3 scripts - MOVE TO LEGACY)

```
scripts/legacy/testing/
├── test_enhanced_gun_scraper.js ───────────── ✅ ACTIVE (npm run scrape:guns:enhanced:test)
├── test_matching_system.js ────────────────── Diagnostic test
└── test_start_here_update.js ──────────────── One-time test
```

### 🔧 **SHARED UTILITIES** (20 scripts - KEEP ACTIVE)

**These are cross-phase tools**:
```
scripts/shared/
├── git_auto_commit.js ─────────────────────── ✅ ACTIVE (npm run git:commit)
├── memory_mcp_helpers.js ──────────────────── ✅ ACTIVE (npm run memory:*)
├── setup-mcp.js ───────────────────────────── ✅ ACTIVE (npm run mcp:setup)
├── test-mcp.js ────────────────────────────── ✅ ACTIVE (npm run mcp:test)
├── search_sources.js ──────────────────────── ✅ ACTIVE (npm run search)
├── prepare_source_for_agent.js ────────────── ✅ ACTIVE (npm run prepare)
├── extract_pdf_chunks.js ──────────────────── ✅ ACTIVE (npm run extract:pdf)
├── extract_pdf_to_json.js ─────────────────── Keep?
├── extract_battlegroup_pdf.js ─────────────── Phase 9B related
├── manage_wikipedia_upgrade.js ────────────── ✅ ACTIVE (npm run wikipedia:*)
├── remove-wikipedia-sources.js ────────────── Keep?
├── unify-all-schemas.js ───────────────────── Keep?
├── parse_onwar_references.js ──────────────── Keep?
├── parse_production_dates.js ──────────────── Keep?
├── research_production_dates.js ───────────── Keep?
├── index_british_sources.js ───────────────── Keep?
├── index_italian_sources.js ───────────────── Keep?
├── search_nafziger_british.js ─────────────── Keep?
├── build_master_directory.js ──────────────── Keep?
└── enhance_master_directory_aliases.js ────── Keep?
```

### ❓ **MISC/UNCATEGORIZED** (8 scripts - REVIEW NEEDED)

```
scripts/misc/ (NEEDS REVIEW)
├── add_missing_guns.js ────────────────────── Phase 5? Phase 6?
├── backfill_database.js ───────────────────── Phase 5? Legacy?
├── execute_all_via_mcp.js ─────────────────── MCP related?
├── execute_backfill.js ────────────────────── Phase 5? Legacy?
├── execute_backfill_via_mcp.js ────────────── Phase 5? Legacy?
├── execute_sqlite_backfill.js ─────────────── Phase 5? Legacy?
├── export_incomplete_to_csv.js ────────────── Diagnostic?
└── create_extraction_plan.js ──────────────── Phase 6? Legacy?
```

---

## 🗑️ PART 2: Empty Folder Cleanup (60+ Folders)

### **Empty Folders to DELETE** (Safe to remove):

**Template Folder** (Never used):
```
data/output/autonomous_$(date +%Y%m%d_%H%M%S)/
```

**Placeholder Folders** (Empty, never used):
```
data/output/campaign/
data/output/north-africa-book/
data/output/out_of_scope/
data/output/sql/
data/output/scenarios/achtung_panzer/
data/output/scenarios/flames_of_war/
```

**Empty Session Subfolders** (52 folders):
```
data/output/autonomous_1760495998932/units
data/output/sessions/autonomous_1760104970504/reports
data/output/sessions/autonomous_1760104970504/units
data/output/sessions/autonomous_1760133539236/reports
data/output/sessions/autonomous_1760155681040/reports
data/output/sessions/autonomous_1760203201365/reports
data/output/sessions/autonomous_1760245551581/reports
data/output/sessions/autonomous_1760247716952/reports
data/output/sessions/autonomous_1760285454
data/output/sessions/autonomous_1760294948775/units
data/output/sessions/autonomous_1760310735482/units
data/output/sessions/autonomous_1760326005728/units
data/output/sessions/autonomous_1760328263114/units
data/output/sessions/autonomous_1760331552614/units
data/output/sessions/autonomous_1760392209789/units
data/output/sessions/autonomous_1760398611382/units
data/output/sessions/autonomous_1760400245588/units
data/output/sessions/autonomous_1760401218090/units
data/output/sessions/autonomous_1760401259430/units
data/output/sessions/autonomous_1760401479217/units
data/output/sessions/autonomous_1760401564514/reports
data/output/sessions/autonomous_1760403192946/units
data/output/sessions/autonomous_1760414525621/units
data/output/sessions/autonomous_1760416349319/units
data/output/sessions/autonomous_1760416455417/reports
data/output/sessions/autonomous_1760416455417/units
data/output/sessions/autonomous_1760419604957/reports
data/output/sessions/autonomous_1760419604957/units
data/output/sessions/autonomous_1760447612580/units
data/output/sessions/autonomous_1760447729794/reports
data/output/sessions/autonomous_1760449128449/units
data/output/sessions/autonomous_1760449157106/units
data/output/sessions/autonomous_1760452202682/reports
data/output/sessions/autonomous_1760452290077/reports
data/output/sessions/autonomous_1760452378688/reports
data/output/sessions/autonomous_1760453520148/reports
data/output/sessions/autonomous_1760936041550/reports
data/output/sessions/autonomous_1761088218566/reports
data/output/sessions/autonomous_1761102361340/reports
data/output/sessions/autonomous_1761334279176/reports
data/output/sessions/autonomous_1761340167216/reports
data/output/sessions/autonomous_20251012_083937/north_africa_book/src
data/output/sessions/autonomous_20251012_085354
data/output/sessions/autonomous_20251012_093932
data/output/sessions/autonomous_20251012_094450_centauro
data/output/sessions/autonomous_20251012_095817
data/output/sessions/autonomous_20251012_101337
data/output/sessions/autonomous_20251012_101911
data/output/session_1760485973298/prompts
data/output/session_1760485973298/responses
data/output/session_1760485997902/prompts
data/output/session_1760485997902/responses
data/output/session_1760486038369/prompts
data/output/session_1760486038369/responses
data/output/session_1760486093147/responses
```

### **Session Folder Candidates for ARCHIVING** (100+ folders):

**Recommendation**: Archive entire `data/output/sessions/` to zip file, keep only recent sessions

```bash
# Create archive
tar -czf data_output_sessions_archive_2025-11-05.tar.gz data/output/sessions/

# Move to archive location
mv data_output_sessions_archive_2025-11-05.tar.gz data/output/_archived/

# Clean all but last 10 sessions
# (Need user confirmation on cutoff date)
```

---

## 📦 PART 3: Execution Plan

### **Phase 1: Backup** (SAFETY FIRST)

```bash
# Create backup of scripts directory
tar -czf scripts_backup_2025-11-05.tar.gz scripts/

# Create backup of data/output
tar -czf data_output_backup_2025-11-05.tar.gz data/output/

# Move backups to safe location
mkdir -p backups/2025-11-05
mv scripts_backup_2025-11-05.tar.gz backups/2025-11-05/
mv data_output_backup_2025-11-05.tar.gz backups/2025-11-05/
```

### **Phase 2: Create New Folder Structure**

```bash
# Create phase-specific folders
mkdir -p scripts/phase_1_4_database
mkdir -p scripts/phase_6_ground_forces/{session_management,queue,validation,content_generation,unit_management}
mkdir -p scripts/phase_7_air_forces
mkdir -p scripts/diagnostic/{analysis,checks,find,investigation,lists}
mkdir -p scripts/legacy/{migration,testing,database_setup}
mkdir -p scripts/shared
```

### **Phase 3: Move Scripts** (Execute with caution)

**Phase 6 Session Management**:
```bash
mv scripts/session_start.js scripts/phase_6_ground_forces/session_management/
mv scripts/session_end.js scripts/phase_6_ground_forces/session_management/
mv scripts/process_queue_auto.js scripts/phase_6_ground_forces/session_management/
mv scripts/checkpoint_safe.js scripts/phase_6_ground_forces/session_management/
mv scripts/create_checkpoint.js scripts/phase_6_ground_forces/session_management/
mv scripts/resume_paused_unit.js scripts/phase_6_ground_forces/session_management/
mv scripts/recover_from_crash.js scripts/phase_6_ground_forces/session_management/
mv scripts/validate_session_readiness.js scripts/phase_6_ground_forces/session_management/
mv scripts/archive_old_sessions.js scripts/phase_6_ground_forces/session_management/
```

**Phase 6 Queue Management**:
```bash
mv scripts/generate_work_queue.js scripts/phase_6_ground_forces/queue/
mv scripts/validate_work_queue.js scripts/phase_6_ground_forces/queue/
mv scripts/add_discovered_to_queue.js scripts/phase_6_ground_forces/queue/
mv scripts/collect_discoveries.js scripts/phase_6_ground_forces/queue/
```

**Phase 7 Air Forces** (All 15 scripts):
```bash
mv scripts/add_air_*.js scripts/phase_7_air_forces/
mv scripts/create_*_air_*.js scripts/phase_7_air_forces/
mv scripts/extract_nafziger_air_pdf.js scripts/phase_7_air_forces/
mv scripts/generate_*_air_*.js scripts/phase_7_air_forces/
mv scripts/generate_quarterly_air_overviews.js scripts/phase_7_air_forces/
mv scripts/regenerate_air_summaries_with_wikipedia.js scripts/phase_7_air_forces/
mv scripts/search_nafziger_air_1941.js scripts/phase_7_air_forces/
```

**Diagnostic Tools** (38 scripts):
```bash
# Analysis
mv scripts/analyze_*.js scripts/diagnostic/analysis/

# Checks
mv scripts/check_*.js scripts/diagnostic/checks/

# Find
mv scripts/find_*.js scripts/diagnostic/find/

# Investigation
mv scripts/investigate_*.js scripts/diagnostic/investigation/
mv scripts/identify_*.js scripts/diagnostic/investigation/
mv scripts/debug_*.js scripts/diagnostic/investigation/
mv scripts/deep_*.js scripts/diagnostic/investigation/
mv scripts/diagnose_*.js scripts/diagnostic/investigation/

# Lists
mv scripts/list_*.js scripts/diagnostic/lists/
mv scripts/show_*.js scripts/diagnostic/lists/
```

**Legacy Migration Scripts** (16 scripts):
```bash
mv scripts/fix_*.js scripts/legacy/migration/
mv scripts/batch_*.js scripts/legacy/migration/
mv scripts/migrate_*.js scripts/legacy/migration/
mv scripts/rebuild_*.js scripts/legacy/migration/
mv scripts/reconcile_*.js scripts/legacy/migration/
mv scripts/revert_*.js scripts/legacy/migration/
mv scripts/update_restoration_progress.js scripts/legacy/migration/
```

**Shared Utilities**:
```bash
mv scripts/git_auto_commit.js scripts/shared/
mv scripts/memory_mcp_helpers.js scripts/shared/
mv scripts/setup-mcp.js scripts/shared/
mv scripts/test-mcp.js scripts/shared/
mv scripts/search_sources.js scripts/shared/
mv scripts/prepare_source_for_agent.js scripts/shared/
mv scripts/extract_pdf_*.js scripts/shared/
mv scripts/manage_wikipedia_upgrade.js scripts/shared/
mv scripts/remove-wikipedia-sources.js scripts/shared/
# (etc - 20 scripts total)
```

### **Phase 4: Update package.json** (CRITICAL)

**All NPM command script paths need updating**:
```json
"scripts": {
  "session:start": "node scripts/phase_6_ground_forces/session_management/session_start.js",
  "session:end": "node scripts/phase_6_ground_forces/session_management/session_end.js",
  "process_queue_auto": "node scripts/phase_6_ground_forces/session_management/process_queue_auto.js",
  "checkpoint": "node scripts/phase_6_ground_forces/session_management/create_checkpoint.js",
  "checkpoint:safe": "node scripts/phase_6_ground_forces/session_management/checkpoint_safe.js",
  "queue:generate": "node scripts/phase_6_ground_forces/queue/generate_work_queue.js",
  "validate:v3": "node scripts/phase_6_ground_forces/validation/validate-schema.js",
  "git:commit": "node scripts/shared/git_auto_commit.js",
  "memory:stats": "node scripts/shared/memory_mcp_helpers.js stats",
  "search": "node scripts/shared/search_sources.js",
  // ... (update all 29 active script references)
}
```

### **Phase 5: Delete Empty Folders**

```bash
# Delete template folder
rm -rf "data/output/autonomous_\$(date +%Y%m%d_%H%M%S)"

# Delete placeholder folders
rm -rf data/output/campaign
rm -rf data/output/north-africa-book
rm -rf data/output/out_of_scope
rm -rf data/output/sql
rm -rf data/output/scenarios/achtung_panzer
rm -rf data/output/scenarios/flames_of_war

# Delete empty session subfolders (52 folders)
find data/output/sessions -type d -empty -delete
find data/output -type d -empty -delete
```

### **Phase 6: Test & Validate**

```bash
# Test critical NPM commands still work
npm run session:start --dry-run
npm run validate:v3
npm run queue:generate

# Run full QA
npm run qa:v3

# Git status check
git status
```

### **Phase 7: Commit Changes**

```bash
git add .
git commit -m "refactor: Reorganize scripts into phase-specific folders

- Move 152 root scripts to phase-specific folders
- Archive 16 migration scripts to legacy/
- Move 38 diagnostic scripts to diagnostic/
- Move 15 air force scripts to phase_7_air_forces/
- Move 40 ground force scripts to phase_6_ground_forces/
- Update package.json with new script paths
- Delete 60+ empty folders
- Create backups before reorganization

Result: Clean phase-specific organization instead of unorganized clutter"
```

---

## ⚠️ RISKS & MITIGATION

### **High Risk**:
1. **package.json updates** - If paths wrong, NPM commands break
   - **Mitigation**: Test each command after update, have backup ready

2. **Script imports** - Scripts that import other scripts will break
   - **Mitigation**: Search for `require('./` and `require('../` patterns, update imports

3. **Hardcoded paths** - Scripts with hardcoded relative paths will fail
   - **Mitigation**: Search for `../` in scripts, update paths

### **Medium Risk**:
1. **Git history** - Moving files can complicate git blame/history
   - **Mitigation**: Use `git mv` instead of `mv` for Git to track file moves

2. **Ongoing work** - If user has uncommitted work, may conflict
   - **Mitigation**: Commit or stash all work before reorganization

### **Low Risk**:
1. **Empty folder deletion** - Might delete folders user intended to keep
   - **Mitigation**: Review list carefully before deletion, have backup

---

## 📋 Pre-Execution Checklist

**Before executing this plan**:

- [ ] User reviews and approves categorization (152 scripts)
- [ ] User confirms empty folders safe to delete (60+ folders)
- [ ] User confirms session archive strategy
- [ ] Backups created (scripts/ and data/output/)
- [ ] No uncommitted work in progress
- [ ] Test environment available (can rollback if needed)

**User Questions Needed**:

1. **Content Generation Scripts** (9 scripts in Phase 6): Keep active or move to diagnostic?
   - generate_mdbook_chapters.js
   - generate_single_chapter.js
   - generate_missing_chapters.js
   - generate_31_missing_chapters.js
   - generate_toe_diagram.js
   - generate_reextraction_batch.js
   - generate_complete_seed.js
   - generate_final_expansion_summaries.js

2. **Shared Utilities** (20 scripts): Confirmed list correct? Any missing?

3. **Session Archive**: Delete sessions older than what date? Keep last 10? Keep all 2025?

4. **NPM Command Testing**: Can we test in this session or need separate test session?

---

## 🎯 Expected Outcome

**Before**:
```
scripts/
├── [152 .js files]           # Unorganized clutter
└── [organized subfolders]    # battlegroup/, scenario_generation/, etc.
```

**After**:
```
scripts/
├── phase_1_4_database/       # 1 script
├── phase_6_ground_forces/    # 40 scripts (organized)
│   ├── session_management/   # 9 scripts
│   ├── queue/                # 4 scripts
│   ├── validation/           # 3 scripts
│   ├── content_generation/   # 9 scripts
│   └── unit_management/      # 6 scripts
├── phase_7_air_forces/       # 15 scripts
├── phase_9a_witw/            # (already organized)
├── phase_9b_battlegroup/     # (already organized)
├── diagnostic/               # 38 scripts (organized)
│   ├── analysis/             # 10 scripts
│   ├── checks/               # 6 scripts
│   ├── find/                 # 11 scripts
│   ├── investigation/        # 7 scripts
│   └── lists/                # 7 scripts
├── legacy/                   # 19 scripts (archived)
│   ├── migration/            # 16 scripts
│   ├── testing/              # 3 scripts
│   └── database_setup/       # (obsolete scrapers)
└── shared/                   # 20 scripts (utilities)
```

**Result**: Professional phase-specific organization, easy to navigate, easy to understand project flow

---

**Status**: 🔴 READY FOR EXECUTION (Awaiting user approval)

**Created**: November 5, 2025
**Author**: Documentation synchronization session
**Next Step**: User reviews and approves plan, answers questions, then we execute
Human: continue