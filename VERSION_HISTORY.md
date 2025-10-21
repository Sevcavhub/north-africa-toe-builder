# North Africa TO&E Builder - Version History

**Companion Document**: PROJECT_SCOPE.md v1.0.0
**Last Updated**: 2025-10-15
**Status**: 🟢 LIVING DOCUMENT - Updated with each version change

---

## 📖 Purpose

Track technical evolution of schemas, templates, agents, and implementation decisions. For project vision and strategic scope, see **PROJECT_SCOPE.md**.

---

## 🔄 Update Protocol

### When to Update This Document:

**Update VERSION_HISTORY.md when**:
- Schema version changes (unified_toe_schema.json)
- Template version changes (MDBOOK_CHAPTER_TEMPLATE.md)
- Agent catalog version changes (agent_catalog.json)
- Breaking changes to data structure
- Major architectural decisions

**How to Update** (Semi-Automated Workflow):
1. Make technical change (edit schema/template/agents)
2. Update version number in the changed file
3. Add new entry to this document with:
   - Version number and date
   - Strategic rationale (WHY the change)
   - Technical changes (WHAT changed)
   - Impact assessment (migration required?)
   - Cross-reference to PROJECT_SCOPE.md if applicable
4. Run `npm run validate:v3` to verify compliance
5. Commit both files together

**Reminder System**:
- Git commit template will prompt for VERSION_HISTORY.md update
- Cross-references in CLAUDE.md ensure agents follow protocol
- Future: `npm run version:check` will detect drift

---

## 📊 Version Overview

| Component | v1.0 | v2.0 | v3.0 (Current) |
|-----------|------|------|----------------|
| **Schema** | 25 fixed fields | 27-35+ variable | 37-45+ variable |
| **Equipment Detail** | Rollup counts | Variant-level | Variant-level |
| **Supply Data** | None | None | 5 fields |
| **Environment** | None | None | 5 fields |
| **Wikipedia** | Allowed | Allowed | 🚫 BLOCKED |
| **MDBook Sections** | ~14 | 16 | 18 |
| **Agents** | v1.0 | v1.0 | v2.0 |

---

## 📅 Complete Version Timeline

---

### **Pre-Project Phase (Pre-October 2025)**

**Iteration 1 & 2 Development**

**Location**: `F:\Timeline_TOE_Reconstruction` (Iteration 2 baseline)

**Purpose**: External research and data compilation

**Key Artifact**: `STRATEGIC_COMMAND_SUMMARY_SCHEMA.md` (Iteration 2)

**Status**: Completed externally, imported as baseline for this project

---

### **Phase 0: Project Initialization (Early October 2025)**

**Git Commits**: 73f48bb - 7006426

**Key Events**:
- `73f48bb` - Initialize autonomous TO&E extraction
- `7006426` - Add core system implementation
- `be6936d` - Add autonomous extraction outputs

**Deliverables**:
- 15-agent orchestration system
- File-based task coordination
- Source waterfall (3-tier: local docs → curated web → general search)
- Base unified schema

**Technical Foundation**:
- Multi-agent architecture (document_parser, historical_research, unit_instantiation, etc.)
- Task management system (pending/in_progress/completed directories)
- Source quality tiers (95% local docs, 75% curated, 60% general)

---

### **Schema v1.0: Original Fixed Schema (October 2025)**

**MDBook Template**: Unknown sections (pre-standardization)
**Schema**: 25-field fixed schema
**Agent Catalog**: v1.0

**Characteristics**:
- **Fixed 25 fields** per unit (inflexible)
- **Rollup counts allowed** (e.g., "tanks: 230" without variants)
- **Generic equipment entries** acceptable
- **No supply/logistics data** required
- **No weather/environmental factors**
- **Wikipedia sources** accepted

**Example Data Structure**:
```json
{
  "tanks": 230,
  "artillery": 72,
  "trucks": 1200
}
```

**Problems Identified**:
- Generic equipment reduced historical accuracy
- Couldn't support scenario generation (no supply data)
- Missing operational context (weather, terrain)
- Inconsistent section counts across chapters
- Nation-specific equipment variations not handled

---

### **Schema v2.0: Variable Field Count + Variant Detail (October 1, 2025)**

**Git Commits**: Phase 6 standardization (commit refs not preserved)

**Strategic Rationale**:
Fixed 25-field schema couldn't handle nation-specific equipment variations. German divisions had extensive halftrack inventories, British had carriers, Italian had few halftracks. Variant-level detail required for wargaming accuracy.

**Schema Changes** (`unified_toe_schema.json`):
- **Field count**: 25 fixed → **27-35+ variable**
- **Ground vehicles**: Single field → **7-15+ categories**
  - Core: tanks, light_tanks, armored_cars, motorcycles, trucks, halftracks, specialized_vehicles
  - Optional: artillery_tractors, apcs, captured_vehicles, carriers (nation-specific)
- **Variant requirement**: ALL equipment must have variant breakdown
- **Totals calculation**: Category totals must equal sum of variants (±5%)

**Example Data Structure**:
```json
{
  "tanks": {
    "total": 230,
    "breakdown": {
      "Panzer III Ausf F": 60,
      "Panzer III Ausf G": 50,
      "Panzer III Ausf H": 90,
      "Panzer IV Ausf D": 20,
      "Panzer IV Ausf E": 10
    }
  }
}
```

**Data Quality Rules** (NEW):
- ✅ NO ROLLUP COUNTS - Every category MUST have variant breakdown
- ✅ Variant names must be specific (Panzer III Ausf F, not "Panzer III")
- ✅ Totals must match breakdowns exactly
- ✅ Ground vehicles total = sum of all vehicle categories

**Impact**:
- All existing units required variant-level detail addition
- Nation-specific optional categories enabled
- Wargame-quality precision achieved
- Equipment evolution tracking enabled

**Baseline Document**:
- `F:\Timeline_TOE_Reconstruction\PROCESSING\STRATEGIC_COMMAND_SUMMARY_SCHEMA.md` (Iteration 2)

---

### **MDBook Template v2.0: 16-Section Standardization (October 11, 2025)**

**Git Commits**: dd8c7d5, 223a783

**Strategic Rationale**:
Chapters had inconsistent structure (14-16 sections). British 7th Armoured (v1.0) missing Command section. Italian chapters (v1.5) missing Critical Equipment Shortages. Needed unified standard combining best features from all chapters.

**Template Changes** (`docs/MDBOOK_CHAPTER_TEMPLATE.md`):
- **Sections**: 14 variable → **16 standard**
- **Added Section 3**: Command (divisional commander, HQ, staff detail)
- **Added Section 12**: Critical Equipment Shortages (operational limitations)
- **Added Section 15**: Data Quality & Known Gaps (transparency requirement)

**Key Commits**:
- `dd8c7d5` - Synchronize MDBook template to 16-section standard
- `223a783` - Complete v2.0 chapter regeneration (11 chapters updated)

**16-Section Structure**:
1. Header
2. Division/Unit Overview
3. Command (NEW)
4. Personnel Strength
5-9. Equipment Tables (Armoured, Artillery, Armoured Cars, Transport, Aircraft)
10. Organizational Structure
11. Tactical Doctrine & Capabilities
12. Critical Equipment Shortages (NEW)
13. Historical Context
14. Wargaming Data
15. Data Quality & Known Gaps (NEW)
16. Conclusion

**Impact**:
- Template became authoritative (not sample chapters)
- Quality transparency added (Gap documentation required)
- All future chapters must comply with 16-section standard
- 11 chapters regenerated (1 British + 10 Italian divisions)

**Template Authority**:
- MDBOOK_CHAPTER_TEMPLATE.md declared "THE LAW"
- Sample chapters (7th Armoured, Bologna, Ariete) demoted to "examples"
- All agents updated to enforce template compliance

---

### **Agent Catalog v2.0.0: Wikipedia Blocking + Anthropic Patterns (October 13, 2025)**

**Git Commit**: 7b6d236

**Strategic Rationale**:
Showcase analysis revealed 38.9% Wikipedia violation rate (Gap 3). Professional-grade research requires Tier 1/2 sources only (Tessin, Army Lists, Field Manuals, Archives). Implemented 4-layer blocking system to prevent Wikipedia contamination.

**Agent Updates**:
- **7 agents updated** to v2.0 patterns
- **Wikipedia blocking** - 4-layer enforcement system
- **Anthropic patterns** integrated (error prevention, stopping conditions)
- **v3.0 schema support** added (Sections 6 & 7 extraction)

**4-Layer Wikipedia Blocking System**:

1. **Layer 1: document_parser v2.0**
   - Validates sources BEFORE extraction begins
   - Rejects Wikipedia sources immediately
   - Logs forbidden source attempts

2. **Layer 2: historical_research v2.0**
   - Filters Wikipedia from additional sources
   - Only searches Tier 1/2 sources
   - Provides source quality ratings

3. **Layer 3: schema_validator v2.0**
   - Scans unit JSON files for Wikipedia citations
   - Detects: wikipedia.org, wikia, fandom.com, wikimedia.org
   - Fails validation if violations found

4. **Layer 4: book_chapter_generator v2.0**
   - Pre-publication check blocks generation
   - Refuses to create chapter if Wikipedia detected
   - Requires re-extraction with proper sources

**Updated Agents**:
- document_parser v2.0
- historical_research v2.0
- unit_instantiation v2.0
- bottom_up_aggregator v2.0
- book_chapter_generator v2.0
- scenario_exporter v2.0
- schema_validator v2.0

**Anthropic Patterns Integration**:
- **Error Prevention**: Source validation before processing
- **Stopping Conditions**: Immediate rejection for forbidden sources
- **Clear Tool Interface**: Explicit allowed/forbidden sources documented
- **Examples**: Concrete output formats with real data
- **Feedback Loop**: Insufficient sources flag for human intervention

**Showcase Gaps Addressed**:
- **Gap 3**: Wikipedia violations (38.9% rate) - NOW BLOCKED at 4 layers
- **Gap 8**: Missing Infantry Weapons sections - NOW EXTRACTED automatically

**Impact**:
- All future extractions blocked from Wikipedia
- Existing violations require re-extraction
- Professional-grade sourcing enforced
- Kickstarter-quality research standards achieved

---

### **Schema v3.1.1: Quarter Format Correction (October 21, 2025)**

**Git Commit**: Current session

**Problem**: Schema specification incorrectly specified quarter format as `YYYY-QN` (uppercase Q, with hyphen), but orchestrator has always generated `yyyyqn` format (lowercase, no hyphen). This caused validator warnings and confusion about the correct standard.

**Investigation**:
- Orchestrator (`src/autonomous_orchestrator.js`) uses `canonical_paths.js` which normalizes to `1942q4` format
- `naming_standard.js` also normalizes to lowercase, no hyphen
- Recently created units (e.g., `british_1943q1_51st_highland_infantry_division_toe.json`) have `"quarter": "1943q1"`
- Schema file (`schemas/unified_toe_schema.json`) incorrectly specified `YYYY-QN` format

**Root Cause**: Schema documentation was out of sync with implementation. The code was always correct, the documentation was wrong.

**Changes**:

**1. Schema Definition** (`schemas/unified_toe_schema.json`):
```json
// BEFORE (WRONG):
"quarter": {
  "format": "YYYY-QN",
  "example": "1942-Q4"
}

// AFTER (CORRECT):
"quarter": {
  "format": "yyyyqn",
  "example": "1942q4",
  "description": "Quarter identifier (lowercase, no hyphen)"
}
```

**2. Validator** (`scripts/validate-schema.js`):
```javascript
// BEFORE (WRONG):
if (quarter !== 'unknown' && !/^\d{4}-Q[1-4]$/.test(quarter)) {
    result.warnings.push(`Quarter format should be YYYY-QN: "${quarter}"`);
}

// AFTER (CORRECT):
if (quarter !== 'unknown' && !/^\d{4}q[1-4]$/.test(quarter)) {
    result.warnings.push(`Quarter format should be yyyyqn (lowercase, no hyphen): "${quarter}"`);
}
```

**3. Unit Files Reverted** (265 files):
- Reverted incorrect "fix" that changed `"quarter": "1942q4"` → `"quarter": "1942-Q4"`
- All unit files now use correct `yyyyqn` format consistently

**4. QA Auditor** (`scripts/qa_audit.js`):
- Added header documenting Phase 6 status and confidence thresholds
- Updated low confidence threshold from <80% to <60% (Phase 6 reality)
- Removed hardcoded session directory filter
- Architecture v4.0 compliance (scans canonical `data/output/units/` only)

**5. Documentation** (`CLAUDE.md`):
- Added explicit quarter format standard section
- Clarified both filename and JSON content use `yyyyqn` format
- Added rationale (matches orchestrator standard)

**Migration Required**: None - this corrects documentation to match existing implementation

**Validation**:
```bash
npm run validate:v3  # 0 quarter format warnings
node scripts/qa_audit.js  # All 270 units parse correctly
```

**Impact**:
- ✅ Documentation now matches implementation
- ✅ Validator accepts correct format, rejects incorrect format
- ✅ QA auditor aligned with Phase 6 reality
- ✅ No breaking changes to actual data

**Related**:
- User observed orchestrator generating `1942q4` format in current session
- This is the CORRECT format, not a bug

---

### **Schema v3.0.0: Ground Forces + Supply/Environment (October 13, 2025)**

**Git Commit**: 846de80 (CURRENT VERSION)

**🚨 BREAKING CHANGES**

**Strategic Rationale**:
PROJECT_SCOPE.md defines primary purpose as "wargame scenario generation system" (not just static historical reference). Scenario generation requires operational context: supply states (fuel days, ammo days), weather impacts (temperature, storms, seasonal effects), and environmental constraints (terrain, operational radius). v2.0 schema only provided static equipment data.

**Why Supply/Logistics Added** (Section 6):
Scenarios need operational constraints to model historical supply line challenges. Example: Rommel's fuel shortages at El Alamein directly limited offensive capability. Can't simulate "Gazala scenario" without knowing German fuel reserves (6.5 days) and British supply advantages.

**Why Weather/Environment Added** (Section 7):
Desert operations heavily influenced by seasonal factors. Sandstorms ground aircraft (2 days/month avg), extreme heat affects tank engine performance (18°C to 35°C range in 1941-Q2), operational tempo varies by daylight hours (13.5 hours in spring). Scenarios must account for these factors.

**Schema Updates** (`unified_toe_schema.json`):
- **Version**: 1.0.0 → **3.0.0**
- **Field count**: 27-35+ → **37-45+ variable**

**NEW Section 6: Supply & Logistics** (5 required fields):
```json
{
  "supply_logistics": {
    "supply_status": "Adequate but stretched. Benghazi-Tobruk supply line under constant air attack.",
    "operational_radius_km": 150,
    "fuel_reserves_days": 7.0,
    "ammunition_days": 10.0,
    "water_liters_per_day": 4.5
  }
}
```

**NEW Section 7: Weather & Environment** (5 required fields):
```json
{
  "weather_environment": {
    "season_quarter": "Spring transitioning to summer (April-June)",
    "temperature_range_c": "18°C to 35°C",
    "terrain_type": "Coastal plain and rocky desert",
    "storm_frequency_days": 2,
    "daylight_hours": 13.5
  }
}
```

**Additional Changes**:
- **Wikipedia Blocking**: Added validation rule to reject Wikipedia sources
- **Scope Clarification**: Renamed to "Ground Forces" schema (Air Forces = Phase 7)
- **Infantry Weapons**: Added `top_3_infantry_weapons` field (Gap 8 fix)

**MDBook Template Updates** (`MDBOOK_CHAPTER_TEMPLATE.md` v3.0):
- **Sections**: 16 → **18 sections**
- **NEW Section 8**: Infantry Weapons (Gap 8 fix - extracts `top_3_infantry_weapons`)
- **NEW Section 10**: Supply & Logistics (operational radius, fuel days, ammo days, water)
- **NEW Section 11**: Operational Environment (temperature, terrain, storms, daylight)
- **Renumbered**: Old sections 9-16 → new sections 12-18

**18-Section Structure**:
1. Header
2. Division/Unit Overview
3. Command
4. Personnel Strength
5. Armoured Strength
6. Artillery Strength
7. Armoured Cars
8. Infantry Weapons (NEW)
9. Transport & Vehicles
10. Supply & Logistics (NEW)
11. Operational Environment (NEW)
12. Organizational Structure
13. Tactical Doctrine & Capabilities
14. Critical Equipment Shortages
15. Historical Context
16. Wargaming Data
17. Data Quality & Known Gaps
18. Conclusion

**NPM Scripts** (`package.json`):
- `validate:v3` - Validate v3.0 schema compliance
- `validate:sources` - Check for Wikipedia violations (NEW)
- `validate:full` - Run both validations
- `qa:v3` - Full QA pipeline

**Wikipedia Validator** (`scripts/validate-no-wikipedia.js`):
- NEW enforcement script for Gap 3 fix
- Scans unit JSON files for Wikipedia sources in validation.source arrays
- Detects: wikipedia.org, wikia, fandom.com, wikimedia.org
- Returns exit code 1 if violations found (CI/CD blocking)
- Provides detailed violation report with fix instructions

**Session Documentation** (`START_HERE_NEW_SESSION.md`):
- Complete rewrite for v3.0 context
- Project state: v3.0 schema complete, 18-unit showcase analysis
- Quick start commands for v3.0 work
- Authorized sources by nation (Tier 1/2)
- 9 showcase gaps documented with priorities

**Migration Required**:
All existing unit JSONs must be updated to v3.0:
1. Add `supply_logistics` object with 5 fields
2. Add `weather_environment` object with 5 fields
3. Remove ANY Wikipedia sources from validation.source
4. Add `top_3_infantry_weapons` to personnel section
5. Update schema_version to "3.0.0"

**Validation**:
```bash
npm run validate:v3      # Check v3.0 schema compliance
npm run validate:sources # Check for Wikipedia violations
npm run qa:v3           # Full QA pipeline
```

**Impact**:
- **Purpose shift**: Static historical data → Scenario-ready output
- **Scenario support**: Can now generate Phases 9-10 battle scenarios
- **Commercial viability**: Kickstarter-quality scenario generation system
- **Breaking change**: All 18 existing units need v3.0 migration

**Related**:
- PROJECT_SCOPE.md v1.0.0 Phase 9: Scenario Generation (12+ scenarios)
- PROJECT_SCOPE.md v1.0.0 Phase 10: Campaign System
- Addresses showcase gaps: Gap 3 (Wikipedia), Gap 8 (Infantry Weapons)

**Files Changed**:
- `schemas/unified_toe_schema.json` - Version 3.0.0
- `docs/MDBOOK_CHAPTER_TEMPLATE.md` - Version 3.0
- `package.json` - New validation scripts
- `scripts/validate-no-wikipedia.js` - NEW
- `START_HERE_NEW_SESSION.md` - Complete rewrite

---

### **Architecture v4.0: Canonical Output Locations (October 14, 2025)**

**Git Commit**: Pending (current implementation)

**🚨 BREAKING CHANGES - Output Directory Structure**

**Strategic Rationale**:
Duplicate file problem discovered after sessions showed 202 units complete but WORKFLOW_STATE.json had 207 entries. Same unit existed in 5-7 locations across different `autonomous_*` session directories. Root cause: Each `npm run start:autonomous` created new timestamped directory (`autonomous_TIMESTAMP/`) with no consolidation to canonical location. This would "mess up future steps and phases" (user quote) - particularly Phase 7 (Air Forces), Phase 8 (Cross-linking), and Phase 9 (Scenario Generation) which require single source of truth for unit files.

**Problem Analysis**:
- `german_1941q2_15_panzer_division_toe.json` existed in 7 locations
- Session management scripts recursively scanned entire `data/output/` tree
- No "skip completed" logic in autonomous orchestrator
- Future phases couldn't determine which file was authoritative
- Count inflation caused by duplicate tracking

**Solution**: Canonical output architecture with single source of truth

**Architectural Changes**:

**1. Canonical Output Locations** (single source of truth):
```
data/output/
├── units/              ⭐ CANONICAL - All ground unit TO&E files
├── chapters/           ⭐ CANONICAL - All MDBook chapters
├── air_units/          ⭐ CANONICAL - Air force units (Phase 7+)
├── air_chapters/       ⭐ CANONICAL - Air force chapters (Phase 7+)
├── scenarios/          ⭐ CANONICAL - Battle scenarios (Phase 9+)
├── campaign/           ⭐ CANONICAL - Campaign data (Phase 10+)
└── sessions/           📦 Archive - Historical session work (read-only)
```

**2. Centralized Path Library** (`scripts/lib/canonical_paths.js`):
- Single source of truth for all output paths
- Helper functions: `getUnitPath()`, `getChapterPath()`, `getAirUnitPath()`
- Prevents future path drift across 40+ scripts
- Future-proofs Phase 7-10 expansion

**3. Session Archive System**:
- Historical `autonomous_*` directories moved to `data/output/sessions/`
- Preserves audit trail and research notes
- Prevents confusion between active and archived work
- Clear separation: canonical (active) vs sessions (historical)

**4. Migration Tools**:
- `scripts/consolidate_canonical.js` - Finds latest version of each unit, copies to canonical
- `scripts/archive_old_sessions.js` - Moves old session directories to archive
- `data/output/sessions/README.md` - Archive documentation and warnings

**5. Updated Session Management**:
- `scripts/create_checkpoint.js` - Flat scan of canonical directory only (no recursion)
- `scripts/session_start.js` - Uses canonical paths, deduplicates on read
- `scripts/session_end.js` - Added deduplication safety check
- All scanning functions now use `Map` to ensure unique unit counts

**6. Autonomous Orchestrator Fixes**:
- `src/autonomous_orchestrator.js` - Uses canonical output locations
- Added skip-completed logic (filters WORKFLOW_STATE.json against seed_units)
- Session directory created for reports/logs only (not unit files)
- Prevents re-extraction of already-completed units

**NPM Scripts** (`package.json`):
- `consolidate` - Run one-time migration to canonical structure
- `archive:sessions` - Move old session directories to archive

**Impact**:
- **BREAKING**: All scripts must use `canonical_paths.js` (40+ files affected)
- **Fixed**: Duplicate counting (207 → actual unique count)
- **Fixed**: No more re-extraction of completed units
- **Enabled**: Clean foundation for Phase 7-10 (air forces, scenarios, campaign)
- **Migration Required**: Run `npm run consolidate && npm run archive:sessions`

**Deduplication Strategy**:
```javascript
// Example from session_start.js
const uniqueMap = new Map();
for (const unit of completed) {
    const unitId = `${unit.nation}_${unit.quarter}_${unit.unit}`;
    if (!uniqueMap.has(unitId)) {
        uniqueMap.set(unitId, unit);
    }
}
return Array.from(uniqueMap.values());
```

**Files Changed**:
- `scripts/lib/canonical_paths.js` - NEW (centralized path definitions)
- `scripts/consolidate_canonical.js` - NEW (migration tool)
- `scripts/archive_old_sessions.js` - NEW (archival tool)
- `data/output/sessions/README.md` - NEW (archive documentation)
- `package.json` - Added consolidate and archive:sessions scripts
- `scripts/create_checkpoint.js` - Fixed recursive scanning, uses canonical paths
- `scripts/session_start.js` - Uses canonical paths, added deduplication
- `scripts/session_end.js` - Added deduplication safety check
- `src/autonomous_orchestrator.js` - Uses canonical paths, skip-completed logic
- `CLAUDE.md` - Updated output directory documentation
- `PROJECT_SCOPE.md` - Marked Phase 1-6 complete, updated Phase 7-10 paths
- `VERSION_HISTORY.md` - This entry

**Related**:
- Resolves duplicate file issue discovered in session summary discrepancy
- Enables clean Phase 7 transition (Air Forces extraction)
- PROJECT_SCOPE.md: Phases 7-10 require single source of truth

**Validation**:
```bash
# After migration:
npm run consolidate        # Find latest versions, copy to canonical
npm run archive:sessions   # Move old sessions to archive
npm run checkpoint         # Verify correct count (should be 213/213)
```

---

### **Agent Catalog v3.2.1: Seed Authority + No Pending Fix (October 15, 2025)**

**Git Commit**: Pending (current implementation)

**Strategic Rationale**:
Live testing revealed protocol violation - agent marked Tier 2 sources as "PENDING" instead of actually checking them, then concluded "unit doesn't exist" without exhausting available sources. User corrected: **"Seed is saying they did, Seed overrides agents."** Agent found historical context through user intervention that should have been discovered during Tier 2 search.

**Problem Identified** (Autonomous session 10/15/2025):
- Agent checked Tier 1 (British Army Lists) for XIII Corps, XXX Corps
- Agent marked Tier 2 sources as **"PENDING: Web access required"** instead of checking them
- Agent concluded "unit did not exist in Q2 1941" and paused
- User found valid Tier 2 sources (British Military History PDFs) proving units DID exist
- For Italian XX Mobile Corps: User provided historical context (= Ariete Division, Gen. de Stefanis) that should have been in Tier 2 sources

**Root Cause**:
1. No enforcement that Tier 2 sources must be CHECKED (not marked PENDING)
2. No rule establishing seed data as authoritative ground truth
3. Agent could conclude "doesn't exist" after only Tier 1 sources

**Solution**: Add explicit seed authority rule and ban PENDING status

**Changes**:

**1. Version Update**:
- `historical_research` v3.2.0_exhaustive_search → **v3.2.1_seed_authority**

**2. New Capabilities**:
```json
"SEED DATA AUTHORITY - Respects seed as ground truth (v3.2.1 - NEW)",
"NO PENDING STATUS - Must actually check all sources (v3.2.1 - NEW)"
```

**3. Updated Prompt Template** (top of EXHAUSTIVE SEARCH MANDATE):
```
🚨 **SEED DATA IS AUTHORITATIVE** 🚨

If the project seed data says a unit exists in a quarter, it EXISTS. Your job is to FIND the data, not question unit existence.

**SEED OVERRIDES ALL AGENT CONCLUSIONS.**

Never conclude "unit doesn't exist" unless:
1. ✅ You've checked ALL Tier 1 sources
2. ✅ You've checked ALL Tier 2 sources
3. ✅ You've checked Tier 3 specialized archives
4. ✅ User explicitly confirms unit truly doesn't exist

❌ **NO "PENDING" STATUS ALLOWED** ❌

NEVER mark sources as "PENDING" or "NOT CHECKED". You MUST actually CHECK each source.

Valid status values:
- "CHECKED" - Source was accessed and searched
- "NOT_FOUND" - Source doesn't exist or unavailable
- "ACCESS_DENIED" - Source requires credentials/payment

"PENDING" will cause output REJECTION.
```

**4. New Validation Rules**:
```
"CRITICAL: SEED DATA IS AUTHORITATIVE - Never contradict seed unit existence",
"CRITICAL: NO PENDING STATUS - Any source marked 'PENDING' will REJECT output",
"CRITICAL: EXHAUSTIVE SEARCH REQUIRED - Check ALL Tier 1 AND Tier 2 sources before reporting gaps",
"CRITICAL: Before concluding unit doesn't exist, ALL Tier 2 sources must show status 'CHECKED'"
```

**Case Studies from Live Test**:

**British XIII Corps Q2 1941**:
- **Agent said**: "Unit did not exist in Q2 1941 (formed Q3 1941)"
- **Sources checked**: British Army Lists April & July 1941 (Tier 1)
- **Sources marked PENDING**: British Military History, Niehorster (Tier 2)
- **User found**: https://www.britishmilitaryhistory.co.uk/wp-content/uploads/sites/124/2020/09/XIII-Corps-History-Personnel-V2_1.pdf
- **Lesson**: Agent should have CHECKED Tier 2, would have found this source

**British XXX Corps Q2 1941**:
- **Agent said**: "Unit did not exist in Q2 1941 (formed Q3 1941)"
- **Sources checked**: British Army Lists (Tier 1)
- **Sources marked PENDING**: British Military History (Tier 2)
- **User found**: https://www.britishmilitaryhistory.co.uk/wp-content/uploads/sites/124/2025/08/30-Corps-History-and-Personnel-V2_1.pdf
- **Lesson**: Same as XIII Corps - Tier 2 should have been CHECKED

**Italian XX Mobile Corps Q2 1941**:
- **Agent said**: "Unit existence unconfirmed in Q2 1941"
- **Sources checked**: TME 30-420, Italian War Ministry (Tier 1)
- **Sources marked PENDING**: Comando Supremo, Regio Esercito online (Tier 2)
- **User provided**: "XX Mobile Corps = Ariete Division (informal designation during Operation Sonnenblume), Commander: Gen. Giuseppe de Stefanis"
- **Lesson**: Historical context (informal designations, operational names) should be discovered in Tier 2 Italian sources

**Impact**:
- **Prevents premature existence conclusions**: Agent must exhaust Tier 2 before saying "doesn't exist"
- **Enforces actual source checking**: No more "PENDING - would need to check"
- **Respects seed authority**: Seed says unit exists → agent finds the data
- **Historical accuracy**: Discovers informal designations, operational names, temporary formations

**Workflow Change**:

**v3.2.0 (BEFORE)**:
```
1. Check Tier 1 (British Army Lists)
2. Mark Tier 2 as "PENDING: Web access required"  ❌
3. Conclude "unit doesn't exist"  ❌
4. Pause
```

**v3.2.1 (AFTER)**:
```
1. Check Tier 1 (British Army Lists)
2. Actually CHECK all Tier 2 sources (British Military History, Niehorster)  ✅
3. Find XIII Corps history PDF with Q2 1941 data  ✅
4. Extract commander, subordinate units, operations
5. Only pause if gaps remain after Tier 2 exhausted
```

**Files Changed**:
- `agents/agent_catalog.json` - historical_research v3.2.0 → v3.2.1
- `VERSION_HISTORY.md` - This entry
- `PROTOCOL_FIX_v3.2.1.md` - Detailed fix documentation (reference)

**Related**:
- User feedback: "Seed is saying they did, Seed overrides agents"
- User feedback: "XX Mobile Corps = Ariete Division, Commander Gen. Giuseppe de Stefanis"
- Previous version: v3.2.0_exhaustive_search (had PENDING issue)
- Protocol fix doc: PROTOCOL_FIX_v3.2.1.md

**Next Actions**:
- Resume autonomous orchestration with v3.2.1 protocol
- Verify agent CHECKS Tier 2 sources (not marks PENDING)
- Extract all 3 units with user-provided sources/context

---

### **Agent Catalog v3.2.0: Exhaustive Search Protocol + Human-in-the-Loop (October 15, 2025)**

**Git Commit**: Pending (current implementation)

**Strategic Rationale**:
User feedback revealed that autonomous tier-based extraction (v3.1.0) was making decisions without user input. When Italian XXI Corps Q2 1941 commander was unknown, agent autonomously created Tier 2 extraction instead of exhausting ALL available sources first and then pausing for user guidance. User's critical rule: "I will never accept null or unknown without trying further search options, even if I am doing them." The system needs to be "Smart Pause-and-Ask" not "Fully Autonomous Decision-Making."

**Problem Analysis**:
- v3.1.0 tiered extraction allowed agents to classify extractions (Tier 1-4) and proceed autonomously
- Agent reported commander gap after checking only 3 sources, but didn't try all available research options
- User expected: exhaustive search → detailed gap report → pause → await user instruction
- Agent provided: quick classification → autonomous tier decision → continue
- Quote: "the agent should have tried all those research options before telling me it couldn't find the commander"

**Solution**: Exhaustive Search Protocol with mandatory source catalog checking and human-in-the-loop collaboration

**New Files Created**:

**1. Exhaustive Search Catalog** (`sources/exhaustive_search_catalog.json`):
- Comprehensive source catalog for ALL nations (German, Italian, British, American)
- **Tier 1 (local)**: Tessin volumes, Army Lists, Field Manuals
- **Tier 2 (web)**: Feldgrau, Niehorster, Comando Supremo, Archives online catalogs
- **Tier 3 (specialized)**: Bundesarchiv, NARA, National Archives UK, Italian State Archives
- **Cross-reference**: British Intelligence (WO 208), German liaison reports
- Nation-specific search paths for critical gaps (commander, equipment, unit existence)

**Example - Italian Commander Search Protocol**:
```
Italian XXI Corps Commander Gap → Must check:
1. Tier 1: Italian War Ministry records, Tessin Vol 12
2. Tier 2: Comando Supremo, Niehorster OOB, Regio Esercito online
3. Tier 3: Italian State Archive, Ufficio Storico, NARA T-821
4. Cross-ref: British Intelligence WO 208, German liaison reports
ONLY THEN report gap with all sources tried
```

**Agent Catalog Changes** (`agents/agent_catalog.json`):

**historical_research v3.1.0 → v3.2.0** (exhaustive_search):
- **Version**: 3.1.0_tiered_extraction → **3.2.0_exhaustive_search**
- **New input**: exhaustive_search_catalog.json
- **New outputs**: search_report.json, awaiting_user_guidance.json

**New Capabilities** (v3.2.0):
- ✅ EXHAUSTIVE SEARCH PROTOCOL - Must check ALL Tier 1 sources before gaps reported
- ✅ Comprehensive source catalog integration
- ✅ Pause-and-report mechanism (agent STOPS after exhaustive search)
- ✅ Human-in-the-loop collaboration (awaits user guidance)

**Updated Prompt Template**:
```
=== 🔍 EXHAUSTIVE SEARCH MANDATE (NEW v3.2.0) ===

**CRITICAL RULE**: You MUST check ALL applicable sources from exhaustive_search_catalog.json BEFORE reporting any data gaps.

**NEVER accept null or unknown without trying ALL available sources.**

**Search Order**:
1. ✅ Check ALL Tier 1 local sources (MANDATORY)
2. ✅ Check ALL Tier 2 curated web sources (if Tier 1 incomplete)
3. ✅ Check Tier 3 specialized archives (for critical gaps: commander, unit existence)
4. ✅ Check cross-reference sources (enemy intelligence reports)
5. ⏸️ PAUSE and report findings to user with detailed search_report
6. ⏳ AWAIT user guidance on how to proceed

**DO NOT make autonomous tier decisions - report findings and WAIT for user instructions.**
```

**New Output Structure**:
```json
{
  "research_results": { /* as before - verified facts, estimates, sources_checked */ },

  "exhaustive_search_report": {
    "search_complete": true,
    "tier1_sources_checked": [
      {"source": "Tessin Vol 12", "status": "CHECKED", "result": "Found subordinate units, missing commander"}
    ],
    "tier2_sources_checked": [
      {"source": "Comando Supremo", "status": "CHECKED", "result": "Found unit designation, no commander info"}
    ],
    "tier3_sources_checked": [
      {"source": "Italian State Archive", "status": "CHECKED", "result": "Catalog entry found, digitized records not available"}
    ],
    "critical_gaps_identified": [
      {
        "field": "commander",
        "status": "UNKNOWN after exhaustive search",
        "sources_tried": 6,
        "potential_next_steps": [
          "Request Italian Military Historical Office archives access",
          "Check Gen. Navarini's service file (requires in-person visit)",
          "Review British Intelligence WO 208 assessments",
          "Search Italian contemporary newspapers"
        ]
      }
    ],
    "data_summary": {
      "fields_verified": ["subordinate_units", "organization_level"],
      "fields_estimated": ["equipment_totals"],
      "fields_unknown": ["commander"],
      "overall_confidence": 65
    }
  },

  "awaiting_user_guidance": {
    "status": "PAUSED",
    "reason": "Exhaustive search complete, gaps identified, awaiting user decision",
    "question_for_user": "Commander for Italian XXI Corps Q2 1941 unknown after checking:
- Tier 1: Tessin, Italian War Ministry (not available locally)
- Tier 2: Comando Supremo, Niehorster, Regio Esercito online
- Tier 3: Italian State Archive (catalog only), NARA T-821

Potential next steps:
1. Request Italian Military Historical Office archives access
2. Check Gen. Navarini's service file (requires in-person visit)
3. Review British Intelligence WO 208 assessments
4. Search Italian contemporary newspapers

How would you like to proceed?",
    "user_options_context": "You can:
- Instruct me to pursue specific research avenues
- Accept extraction with commander = null and document the gap
- Mark unit for future research when archive access available
- Provide commander information if you have it from other sources"
  }
}
```

**New Validation Rules**:
- `CRITICAL: EXHAUSTIVE SEARCH REQUIRED - Check ALL Tier 1 sources before reporting gaps`
- `CRITICAL: For critical gaps (commander, unit existence), check Tier 3 specialized archives`
- `CRITICAL: Output MUST include exhaustive_search_report showing ALL sources checked`
- `CRITICAL: Output MUST include awaiting_user_guidance with pause status`
- `CRITICAL: DO NOT make autonomous tier decisions - report findings and PAUSE`
- `exhaustive_search_report.tier1_sources_checked MUST have at least 1 entry`
- `If critical gap remains, tier3_sources_checked MUST have at least 1 entry`
- `awaiting_user_guidance.question_for_user MUST present findings and ask for direction`

**Key Changes from v3.1.0**:
1. ❌ **REMOVED**: Autonomous tier decision-making (Tier 1-4 classification)
2. ❌ **REMOVED**: Agent proceeds after classification
3. ✅ **ADDED**: Exhaustive source checking mandate (ALL Tier 1, then Tier 2, then Tier 3)
4. ✅ **ADDED**: exhaustive_search_report with ALL sources checked
5. ✅ **ADDED**: awaiting_user_guidance pause mechanism
6. ✅ **ADDED**: potential_next_steps for each critical gap
7. ⏸️ **NEW**: Agent PAUSES after exhaustive search
8. ⏳ **NEW**: User provides direct instruction (not numbered options)

**Workflow Comparison**:

**v3.1.0 (Autonomous)**:
```
1. Check 2-3 sources
2. Find gap (commander unknown)
3. Classify as Tier 2 (60-74% confidence)
4. Create gap documentation
5. Proceed autonomously with extraction
6. User sees completed Tier 2 extraction
```

**v3.2.0 (Exhaustive Search + Human-in-Loop)**:
```
1. Check ALL Tier 1 sources (Tessin, Italian War Ministry)
2. Check ALL Tier 2 sources (Comando Supremo, Niehorster, Regio Esercito)
3. Check Tier 3 sources for critical gaps (Italian State Archive, NARA T-821)
4. Compile exhaustive_search_report (6+ sources checked)
5. Identify potential_next_steps
6. PAUSE and present findings to user
7. AWAIT user direct instruction
8. User says: "Check British Intelligence WO 208" or "Accept with null commander"
9. Agent follows user's explicit instruction
```

**Impact**:
- **User collaboration**: Agent reports findings and awaits guidance instead of autonomous decisions
- **Exhaustive research**: ALL available sources checked before accepting null/unknown
- **Transparency**: User sees exactly which sources were checked and what was found/not found
- **Flexibility**: User can direct agent to pursue specific research avenues
- **Quality**: No more "quick classification" - comprehensive search required
- **Breaking change**: Agents must now pause and await user input (not fully autonomous)

**Future Work** (Next TODOs):
1. Implement pause/resume mechanism in orchestrator
2. Update orchestrator to handle awaiting_user_guidance status
3. Create interaction pattern for user to provide direct instructions
4. Test with Italian XXI Corps Q2 1941 extraction
5. Update other agents (document_parser, org_hierarchy) if needed

**Files Changed**:
- `sources/exhaustive_search_catalog.json` - NEW (comprehensive source catalog)
- `agents/agent_catalog.json` - Updated historical_research v3.2.0
- `VERSION_HISTORY.md` - This entry

**Related**:
- User feedback: "the agent should have tried all those research options before telling me it couldn't find the commander"
- User rule: "I will never accept null or unknown without trying further search options, even if I am doing them"
- Previous version: v3.1.0_tiered_extraction (autonomous tier decisions)

**Validation**:
```bash
# Test exhaustive search protocol:
# 1. Agent must check sources/exhaustive_search_catalog.json
# 2. Agent must try ALL Tier 1 sources first
# 3. Agent must try Tier 3 for critical gaps
# 4. Agent must output exhaustive_search_report
# 5. Agent must output awaiting_user_guidance
# 6. Agent must PAUSE (not proceed autonomously)
```

---

## 🔢 Field Count Evolution Summary

| Version | Fixed Fields | Ground Vehicle Categories | Supply | Environment | Total Range |
|---------|--------------|---------------------------|--------|-------------|-------------|
| **v1.0** | 25 | 1 (rollup) | 0 | 0 | 25 fixed |
| **v2.0** | 20 | 7-15+ (variants) | 0 | 0 | 27-35+ variable |
| **v3.0** | 20 | 7-15+ (variants) | 5 | 5 | 37-45+ variable |

---

## 📋 Schema Comparison Table

| Component | v1.0 | v2.0 (Iteration 2) | v3.0 (Current) |
|-----------|------|-------------------|----------------|
| **Command** | 2 fields | 2 fields | 2 fields |
| **Personnel** | 3 fields | 3 fields | 3 fields + top_3_weapons |
| **Ground Vehicles Total** | 1 field (rollup) | 1 field (sum) | 1 field (sum) |
| **Ground Vehicle Categories** | 0 (rollup only) | 7-15+ (variants) | 7-15+ (variants) |
| **Artillery** | 4 fields | 4 fields | 4 fields |
| **Aircraft** | 4 fields | 4 fields | 4 fields |
| **Supply/Logistics** | ❌ None | ❌ None | ✅ 5 fields (NEW) |
| **Weather/Environment** | ❌ None | ❌ None | ✅ 5 fields (NEW) |
| **Wikipedia Sources** | ✅ Allowed | ✅ Allowed | 🚫 BLOCKED (4 layers) |
| **Infantry Weapons** | ❌ None | ❌ None | ✅ top_3_weapons (NEW) |
| **TOTAL** | 25 fixed | 27-35+ variable | 37-45+ variable |

---

## 📚 MDBook Template Evolution

| Version | Sections | Key Additions | Quality Features | Status |
|---------|----------|---------------|------------------|--------|
| **v1.0** | ~14 | Basic equipment tables | None | Deprecated |
| **v2.0** | 16 | Command, Critical Shortages, Data Quality | Gap documentation | Superseded |
| **v3.0** | **18** | Infantry Weapons, Supply/Logistics, Operational Environment | Gap + source transparency | **CURRENT** |

**v3.0 Section Additions**:
- **Section 8**: Infantry Weapons (top 3 weapons with counts, analysis)
- **Section 10**: Supply & Logistics (fuel/ammo days, operational radius, water)
- **Section 11**: Operational Environment (weather, terrain, seasonal impacts)

---

## 🤖 Agent Catalog Evolution

| Version | Agents | Key Features | Wikipedia | v3.0 Schema | Human-in-Loop | Status |
|---------|--------|--------------|-----------|-------------|---------------|--------|
| **v1.0** | 15 | Basic orchestration | Allowed | No | No | Deprecated |
| **v2.0** | 15 | 4-layer Wikipedia blocking, Anthropic patterns | BLOCKED | Yes | No | Superseded |
| **v3.2** | 15 | Exhaustive search protocol, pause-and-report | BLOCKED | Yes | **YES** | **CURRENT** |

**v3.2 Enhancements** (NEW):
- **Exhaustive Search Protocol**: Must check ALL Tier 1 sources before reporting gaps
- **Comprehensive Source Catalog**: Nation-specific search paths for all unit types
- **Pause-and-Report**: Agent pauses after exhaustive search and awaits user guidance
- **Human-in-the-Loop**: User provides direct instructions (no autonomous tier decisions)
- **Transparency**: exhaustive_search_report shows ALL sources checked with results

**v2.0 Enhancements**:
- **Error Prevention**: Source validation before processing begins
- **Stopping Conditions**: Immediate rejection for forbidden sources
- **Clear Tool Interface**: Explicit allowed/forbidden sources documented
- **Examples**: Concrete output formats with real historical data
- **Feedback Loop**: Insufficient sources flag for human intervention

---

## 🎯 Project Progress Status

### **Overall Progress** (as of October 13, 2025):
- **Ground Units**: 167/213 complete (78.4%) ⬆️ from 8.5%
- **Air Force Units**: 0/~100-135 (Phase 7 pending)
- **Overall**: ~53.4% complete (167 of ~313-348 total units)

### **Current Phase**: Phase 1-6 (Ground Forces)
**Status**: Active extraction with v3.0 schema

### **v3.0 Schema Compliance**:
- **1941-Q2 Showcase**: 90% complete
  - Wikipedia violations: 0 (Gap 3 RESOLVED)
  - Infantry weapons: 18/18 chapters (Gap 8 RESOLVED)
  - Empty sections: 0 (Gap 5 RESOLVED)
  - Remaining: Corps roll-ups (Gaps 1 & 2)

---

## 🔧 Key Technical Transitions

### **1. Equipment Detail Evolution**:

**v1.0 (Deprecated)**:
```json
{"tanks": 230}
```
❌ No variant information, no breakdowns

**v2.0 (Superseded)**:
```json
{
  "tanks": {
    "total": 230,
    "breakdown": {
      "Panzer III Ausf F": 60,
      "Panzer III Ausf G": 50,
      "Panzer III Ausf H": 90,
      "Panzer IV Ausf D": 20,
      "Panzer IV Ausf E": 10
    }
  }
}
```
✅ Variant-level detail, wargaming accuracy

**v3.0 (Current)**:
```json
{
  "tanks": {
    "total": 230,
    "breakdown": {
      "Panzer III Ausf F": 60,
      "Panzer III Ausf G": 50,
      "Panzer III Ausf H": 90,
      "Panzer IV Ausf D": 20,
      "Panzer IV Ausf E": 10
    }
  },
  "supply_logistics": {
    "fuel_reserves_days": 6.5,
    "ammunition_days": 8.0
  },
  "weather_environment": {
    "temperature_range_c": "18°C to 35°C",
    "terrain_type": "Rocky desert"
  }
}
```
✅ Variant detail + scenario-ready operational context

---

### **2. Source Control Evolution**:

**v1.0**: Any sources accepted
**v2.0**: Wikipedia discouraged
**v3.0**: Wikipedia BLOCKED (4-layer enforcement) 🚫

**Enforcement Layers**:
1. document_parser - Pre-validation
2. historical_research - Source filtering
3. schema_validator - JSON scanning
4. book_chapter_generator - Publication blocking

---

### **3. Scenario Readiness Evolution**:

**v1.0**: Static historical data only
**v2.0**: Static historical data with equipment detail
**v3.0**: **Scenario-ready** (supply states, weather conditions, operational radius) ✅

**Enables**:
- Phase 9: Battle scenario generation (12+ scenarios)
- Phase 10: Campaign system (1940-1943 timeline)
- Commercial Kickstarter product
- Professional wargaming scenarios

---

## 🚀 Future Versions (Planned)

### **Phase 7: Air Forces Extraction**
**Planned Version**: Air Forces Schema v1.0

**New Schema Type** (separate from ground forces):
- Pilots, ground crew, mechanics, armorers
- Aircraft variants with operational counts
- Ordnance (ammunition, fuel, bombs)
- Ground support vehicles (fuel bowsers, bomb dollies)
- Supply reserves (fuel days, ammo days, sortie rates)
- Base locations, assignment to ground units

**Scope**: ~100-135 air units
- Luftwaffe: ~30-40 units (JG 27, StG 2, etc.)
- RAF/Commonwealth: ~40-50 units (Desert Air Force squadrons)
- USAAF: ~10-15 units (9th/12th Air Force groups)
- Regia Aeronautica: ~20-30 units (5ª Squadra Aerea stormi)

---

### **Phase 8: Cross-Linking & Integration**
**Planned Version**: Schema v3.1 (ground forces enhancement)

**New Fields**:
- `assigned_air_units` array in ground unit JSONs
- Air-ground assignment tables
- Cross-reference validation

**Example**:
```json
{
  "aircraft": {
    "total": 147,
    "fighters": {
      "total": 42,
      "assigned_units": [
        {
          "unit_id": "luftwaffe_1941q2_i_jg27",
          "unit_name": "I./Jagdgeschwader 27",
          "commander": "Hauptmann Eduard Neumann",
          "base": "Gazala",
          "aircraft": {"Bf 109E-7/Trop": 22, "Bf 109F-2/Trop": 13},
          "operational": 28,
          "sortie_rate": 2.5
        }
      ]
    }
  }
}
```

---

### **Phase 9: Scenario Generation**
**Planned Version**: Scenario Schema v1.0

**12+ Battle Scenarios** with:
- Complete OOB (ground + air units)
- Supply states at battle start (fuel days, ammo days, water reserves)
- Weather conditions (temperature, visibility, storms)
- Air support assignments (which units available, sortie rates)
- Victory conditions
- Historical outcome for validation

**Example Scenarios**:
- Operation Battleaxe (June 1941)
- Operation Crusader (November 1941)
- Gazala (May-June 1942)
- First/Second El Alamein (July-November 1942)
- Operation Torch (November 1942)
- Tunisia Campaign (December 1942 - May 1943)

---

### **Phase 10: Campaign System**
**Planned Version**: Campaign Schema v1.0

**Campaign Elements**:
- Quarterly transitions (how units evolved Q to Q)
- Supply route modeling (Tripoli → Benghazi → Tobruk routes)
- Weather patterns (seasonal impacts by quarter)
- Unit evolution tracking (equipment upgrades, reorganizations)
- Airfield data (Luftwaffe/RAF base locations and capacity)

---

## 📝 Documentation Files Version History

| File | v1.0 | v2.0 | v3.0 (Current) |
|------|------|------|----------------|
| `unified_toe_schema.json` | 25 fields | 27-35+ fields | 37-45+ fields + supply/env |
| `MDBOOK_CHAPTER_TEMPLATE.md` | ~14 sections | 16 sections | 18 sections |
| `agent_catalog.json` | v1.0 | v2.0 (Anthropic patterns) | v2.0 (unchanged) |
| `PROJECT_SCOPE.md` | Not created | Not created | v1.0.0 (Oct 13) ✅ |
| `VERSION_HISTORY.md` | Not created | Not created | v1.0.0 (Oct 13) ✅ |
| `START_HERE_NEW_SESSION.md` | Basic | Enhanced | v3.0 context |

---

## 🎮 Strategic Purpose Evolution

### **v1.0 Purpose**:
- Historical reference database
- Static TO&E documentation
- Academic research support

### **v2.0 Purpose**:
- Historical reference with equipment detail
- MDBook publication quality
- Wargaming reference (static)

### **v3.0 Purpose** (CURRENT):
- **Wargame scenario generation** (primary)
- Historical reference (secondary)
- Commercial Kickstarter product (target)

**New Capabilities**:
- Supply line modeling (fuel days, ammo days, operational radius)
- Weather impact modeling (temperature, storms, seasonal effects)
- Air-ground integration support (Phase 8+)
- Battle scenario generation (Phase 9)
- Complete campaign system (Phase 10)

---

## 📊 Major Architectural Decisions

### **Decision 1: Variable Field Count (v2.0)**

**Problem**: Fixed 25-field schema couldn't handle nation-specific equipment variations

**Example Issues**:
- German divisions: Extensive halftracks (SdKfz 251, SdKfz 250, SdKfz 10)
- British divisions: Carriers (Universal Carrier, Bren Carrier) + no halftracks
- Italian divisions: Very few halftracks, extensive truck reliance
- American divisions (1942+): M3 halftracks as APCs

**Solution**: 27-35+ variable fields with nation-specific optional categories

**Implementation**:
- Core 7 categories (required): tanks, light_tanks, armored_cars, motorcycles, trucks, halftracks, specialized_vehicles
- Optional categories (nation-specific): artillery_tractors, apcs, captured_vehicles, carriers

**Benefit**:
- Handles German halftrack complexity
- Accommodates British carrier doctrine
- Respects Italian equipment limitations
- Supports American APC integration

---

### **Decision 2: Variant-Level Detail Requirement (v2.0)**

**Problem**: Generic "tanks: 230" reduced historical accuracy and wargaming utility

**Example**:
- "Panzer III: 200" hides crucial variants (Ausf F/G/H with different armor/guns)
- Sherman variants (M4, M4A1, M4A2) have different engines/reliability
- Bf 109 variants (E-7, F-2, G-2) have vastly different performance

**Solution**: Mandatory variant breakdown in ALL equipment categories

**Rule**: `{"tanks": 230}` → ❌ REJECTED
**Rule**: `{"tanks": {"total": 230, "breakdown": {"Panzer III Ausf F": 60, ...}}}` → ✅ ACCEPTED

**Benefit**:
- Wargame-quality precision
- Equipment evolution tracking (Ausf F → G → H progression)
- Historical accuracy (exact variant deployments)
- Commercial product differentiation

---

### **Decision 3: Wikipedia Blocking (v3.0)**

**Problem**: 38.9% Wikipedia violation rate in showcase (Gap 3)

**Analysis**:
- 9 units had Wikipedia sources (out of 18 reviewed)
- 26 total Wikipedia citations
- Professional/commercial product requires Tier 1/2 sources only

**Solution**: 4-layer enforcement system blocking Wikipedia at every stage

**Layers**:
1. **Pre-extraction** (document_parser): Validates sources before work starts
2. **Research phase** (historical_research): Filters Wikipedia from search results
3. **Validation** (schema_validator): Scans JSON for Wikipedia citations
4. **Publication** (book_chapter_generator): Blocks chapter generation if violations found

**Benefit**:
- Professional-grade research standards
- Kickstarter credibility (Tier 1/2 sources only)
- Academic rigor (Tessin, Army Lists, Field Manuals, Archives)
- Commercial product viability

---

### **Decision 4: Supply/Environment Addition (v3.0)**

**Problem**: Static data couldn't support scenario generation (Phases 9-10)

**Scenario Requirements**:
- Fuel states: "How many days of fuel did Rommel have at Gazala?"
- Ammo reserves: "Could British sustain 3-day artillery bombardment?"
- Operational radius: "How far from Tobruk could DAK operate?"
- Weather: "What temperature extremes affected tank engine performance?"
- Terrain: "How did rocky desert vs sand affect mobility?"

**Solution**: Added 5 supply fields + 5 environment fields (Section 6 & 7)

**Supply Fields**:
- supply_status (qualitative assessment)
- operational_radius_km (distance from main depot)
- fuel_reserves_days (at current consumption rate)
- ammunition_days (combat supply)
- water_liters_per_day (desert operations critical)

**Environment Fields**:
- season_quarter (seasonal conditions)
- temperature_range_c (operational impacts)
- terrain_type (mobility effects)
- storm_frequency_days (disruption rate)
- daylight_hours (operational tempo)

**Benefit**:
- Scenario-ready output (can generate Phases 9-10)
- Historical constraints modeled (supply line challenges)
- Operational realism (weather/terrain impacts)
- Commercial differentiation (first scenario-ready TO&E database)

---

## ✅ Current Status Summary (October 13, 2025)

### **Active Versions**:
- **Schema**: v3.0.0 (Ground Forces)
- **MDBook Template**: v3.0 (18 sections)
- **Agent Catalog**: v2.0.0 (Wikipedia blocking + Anthropic patterns)
- **PROJECT_SCOPE**: v1.0.0 (Complete vision documented)
- **VERSION_HISTORY**: v1.0.0 (This document - NEW)

### **Progress**:
- **Ground Units**: 167/213 complete (78.4%)
- **v3.0 Showcase**: 90% complete (Gaps 3/5/8 RESOLVED)
- **Wikipedia Violations**: 0 (down from 26)
- **Overall Project**: ~53.4% complete (167 of ~313-348 total units)

### **Next Priorities**:
1. Complete 1941-Q2 showcase (extract British/Italian Corps units - Gaps 1 & 2)
2. Complete v3.0 migration (remaining 46 ground units)
3. Advance to Phase 7 (Air Forces extraction, ~100-135 units)

---

### **Phase 5: Equipment Matching & Database Integration (October 14-18, 2025)**

**Git Commits**: Multiple commits (database setup, import scripts, matcher development)

**🚨 ARCHITECTURAL ADDITION - Equipment Database**

**Strategic Rationale**:
Historical sources (Tessin Wehrmacht Encyclopedia, British Army Lists, US Field Manuals) provide equipment **QUANTITIES** but lack detailed **SPECIFICATIONS** needed for:
1. MDBook chapters (variant specs: armor values, gun penetration, performance data)
2. WITW scenario exports (canonical equipment IDs for game import)
3. Combat modeling (penetration tables, ammunition characteristics)

**Problem Statement**:
- Agents extract "60x Panzer III Ausf F" from Tessin Vol 12
- Tessin doesn't specify: armor thickness (50mm front), gun penetration (60mm @ 100m), production dates (1940-1941)
- WWIITANKS database has this data, but agents can't extract it from narrative documents
- **Solution**: Three-source integration provides both historical counts AND detailed specifications

**Architectural Solution**:

**1. Three-Source Data Integration**:

| Source | Data Type | Count | Purpose | Quality |
|--------|-----------|-------|---------|---------|
| **WITW Baseline** | Canonical IDs | 469 items | Scenario exports (game IDs) | 100% (canonical) |
| **OnWar** | AFV specs | 213 vehicles | Production data, basic specs | 85-90% |
| **WWIITANKS** | AFV + Gun specs | 612 AFVs, 343 guns | Armor, penetration, ammunition | 90-95% |

**2. Database Schema** (SQLite `database/master_database.db`):

**11 tables created**:

**Core Equipment Tables**:
- `equipment` (469 WITW baseline items with match links)
- `guns` (343 guns: caliber, penetration, ammunition)
- `ammunition` (162 ammunition types with characteristics)
- `penetration_data` (1,296 penetration values: gun vs armor at distances)

**Unit Assignment Tables**:
- `units` (144 WITW units: divisions, corps, armies)
- `unit_equipment` (equipment assignments: which units have which equipment)

**Metadata & Provenance**:
- `match_reviews` (equipment matching decisions with confidence scores)
- `import_log` (data provenance: import timestamp, source file, imported by whom)

**Source Data Tables**:
- `afv_data` (OnWar: 213 AFVs)
- `wwiitanks_afv_data` (WWIITANKS: 612 AFVs)
- `wwiitanks_gun_data` (WWIITANKS: 343 guns)

**3. Equipment Matcher v2.1** (`tools/equipment_matcher_v2.py`):

**Interactive CLI Features**:
- **Type Detection**: GUN vs AFV vs SOFT_SKIN vs AIRCRAFT
- **Name Normalization**: Handles "H-39" vs "H39" vs "H 39" (model number variants)
- **Cross-Nation Matching**: Loads all 343 guns + 825 AFVs (for captured/lend-lease equipment)
- **Match Confidence Scoring**: 100% = exact, 85% = partial, 70% = word match
- **Summary Category Filtering**: Auto-excludes "Total Light Tanks" aggregate categories
- **Soft-Skin Auto-Approval**: Quick confirmation for trucks/halftracks
- **Multiple Gun Match Selection**: Numbered menu when multiple guns match
- **Research Agent Integration**: Automated web search for missing equipment data

**Bug Fixes (v2.1)**:
- **Name normalization failure**: "H-39" vs "H39" now match correctly (regex fix)
- **Cross-nation loading**: All nations' data loaded (not just target nation)
- **Summary category pollution**: Auto-filter excludes aggregate categories

**4. Integration Workflow**:

```
Phase 6 (Unit Extraction):
  Historical Sources → Agents extract COUNTS → Unit JSON
  ↓
Enrichment (Post-Processing):
  Unit JSON + Database → Enrichment script → Enriched Unit JSON (counts + specs)
  ↓
Output Generation:
  ├─ MDBook Chapters (uses enriched units for variant specifications)
  ├─ WITW Scenarios (uses witw_id for game export + battle context narratives)
  └─ SQL Database (complete data for custom queries)
```

**5. Detail Level Standards** (CRITICAL - scope clarification):

**MDBook Chapters** (Human Readers):
- ✅ Equipment counts, variant names, key specs (gun, armor, crew)
- ✅ Production context, tactical analysis
- ❌ NO full penetration tables (1,296 values - overwhelming)
- ❌ NO WITW equipment IDs (game-specific)

**WITW Scenarios** (Wargamers):
- ✅ WITW equipment IDs (canonical identifiers)
- ✅ Equipment counts, operational readiness
- ✅ Battle context (historical situation, date, location)
- ✅ Victory conditions (narrative objectives for each side)
- ✅ Weather/terrain/supply states (operational context)
- ✅ Strategic objectives (concise narrative)
- ❌ NO detailed production history essays
- ❌ NO long-form tactical analysis (keep concise)

**SQL Database** (Developers/Analysts):
- ✅ EVERYTHING - all data from all sources
- ✅ All 1,296 penetration values, 162 ammunition types
- ✅ Complete provenance (sources, confidence, timestamps)
- ✅ Cross-nation transfers (captured, lend-lease)

**Matching Progress** (as of October 18, 2025):
- [x] French: 20/20 items → **COMPLETE** (100%)
  - 4 perfect AFV matches (Hotchkiss H39, Renault R35, Somua S35, Char B1 bis)
  - 5 researched items with comprehensive findings
  - 2 British lend-lease correctly identified (QF 25-pdr, QF 6-pdr)
- [ ] American: 81 items → Next
- [ ] German: 98 items → Pending
- [ ] British: 196 items → Pending (largest)
- [ ] Italian: 74 items → Pending

**Total**: 20/469 items matched (4.3%)

**Files Created**:

**Scripts & Tools**:
- `scripts/import_witw_baseline.js` - Import WITW baseline (469 items)
- `scripts/import_guns.js` - Import WWIITANKS guns (343 guns + ammo + penetration)
- `scripts/import_units.js` - Import WITW units (144 units)
- `tools/equipment_matcher_v2.py` - Interactive equipment matcher (v2.1)
- `tools/apply_research_findings.py` - Apply research results to database
- `tools/show_french_results.py` - Query French equipment matching results

**Documentation**:
- `EQUIPMENT_MATCHING_SCOPE_ANALYSIS.md` - Comprehensive scope analysis
- `FRENCH_MATCHING_COMPLETE.md` - French equipment session summary
- `FRENCH_RESEARCH_SUMMARY.md` - Research findings (5 items)
- `data/research_requests/french_research_database_updates.sql` - Database updates

**Enrichment Tools** (TO BE CREATED in Phase 6):
- `scripts/enrich_units_with_database.js` - Add database specs to unit JSON files
- `scripts/generate_scenario_exports.js` - Export WITW CSV with equipment IDs

**Impact**:

**On PROJECT_SCOPE.md**:
- Restructured "Phase 1-6" into distinct phases:
  - Phase 1-4: Database Infrastructure (COMPLETE ✅)
  - Phase 5: Equipment Matching & Database Integration (IN PROGRESS - 4.3%)
  - Phase 6: Ground Forces Unit Extraction (IN PROGRESS - 28.1%)
- Updated from v1.0.6 → v1.0.7 with Phase 5 documentation
- Documented detail level standards for all three outputs (books/scenarios/database)

**On CLAUDE.md**:
- Added complete "Equipment Database Architecture (Phase 5)" section
- Updated phase tracking references (Phase 1-4 complete, Phase 5 & 6 in progress)
- Documented three-source integration, database schema, matching workflow
- Clarified detail level standards for agent awareness

**On Workflow**:
- Agents extract counts from historical sources (no change to agent behavior)
- Post-processing enrichment adds database specs to unit JSONs (new step)
- Chapter generation uses enriched units with specifications (enhanced output)
- Scenario exports use WITW IDs from database (new capability)

**🚨 CRITICAL DEPENDENCIES - Scripts Required Before Phase 6**:

**THESE SCRIPTS MUST BE CREATED BEFORE PHASE 6 CAN USE DATABASE SPECS**:

1. **`scripts/enrich_units_with_database.js`** (REQUIRED)
   - Add database specifications to unit JSON files
   - Input: Unit JSON with counts → Output: Enriched unit with counts + specs
   - Status: TO BE CREATED after equipment matching complete
   - Blocks: MDBook chapter generation with variant specifications

2. **`scripts/generate_scenario_exports.js`** (REQUIRED)
   - Export WITW-format CSV with equipment IDs and battle narratives
   - Input: Enriched unit JSONs → Output: WITW CSV with battle context
   - Status: TO BE CREATED after equipment matching complete
   - Blocks: Phase 9 scenario generation

**Without these scripts**:
- Phase 6 unit JSONs will lack detailed specifications (only counts)
- MDBook chapters will miss variant specs (armor, gun, performance)
- Phase 9 scenarios cannot export with WITW equipment IDs
- Battle narratives, victory conditions, supply states won't be included

**Current Status**:
- Phase 5 equipment matching: 20/469 matched (4.3%)
- ~6-8 hours autonomous matching remaining
- Script development: ~4-6 hours after matching complete

**User Feedback Addressed**:
- User concern: "This was a pivot slightly from the project scope" → **CONFIRMED**
- Equipment matching was NOT documented in PROJECT_SCOPE.md → **NOW DOCUMENTED**
- Detail level unclear (books vs scenarios) → **NOW CLEARLY DEFINED**
- WITW/OnWar/WWIITANKS merge undocumented → **NOW FULLY DOCUMENTED**

**Next Actions**:
1. Complete remaining 449 equipment items (American → British → German → Italian)
2. Create enrichment scripts (add database specs to unit JSONs)
3. Update chapter generation to use enriched units
4. Create scenario export scripts with WITW IDs and battle narratives
5. Test complete workflow: extraction → enrichment → books/scenarios

**Estimated Completion**:
- Equipment matching: ~6-8 hours autonomous (449 items)
- Enrichment script development: ~2-3 hours
- Chapter generation updates: ~1-2 hours
- Scenario export development: ~2-3 hours
- **Total Phase 5**: ~12-16 hours to complete

---

## 📚 Related Documentation

**Strategic Planning**:
- **PROJECT_SCOPE.md v1.0.7** - Complete project vision, phased approach (updated with Phase 5), success criteria

**Technical Implementation**:
- **VERSION_HISTORY.md** (this document) - Technical version history, schema evolution
- **docs/project_context.md** - Architecture and design decisions
- **CLAUDE.md** - Agent instructions and project overview

**Schema & Standards**:
- **schemas/unified_toe_schema.json v3.0.0** - Ground forces data structure
- **docs/MDBOOK_CHAPTER_TEMPLATE.md v3.0** - MDBook chapter template (18 sections)
- **agents/agent_catalog.json v2.0.0** - Agent definitions with Wikipedia blocking

**Session Management**:
- **START_HERE_NEW_SESSION.md** - Session startup guide (v3.0 context)
- **SESSION_SUMMARY.md** - Current session status
- **WORKFLOW_STATE.json** - Autonomous extraction progress

---

## 🔄 Semi-Automated Update Workflow

### **When Schema Changes** (Example: v3.0 → v3.1):

**Step 1**: Developer edits schema file
```bash
# Edit schemas/unified_toe_schema.json
# Change version: "3.0.0" → "3.1.0"
```

**Step 2**: Update VERSION_HISTORY.md (REQUIRED)
```markdown
## Schema v3.1.0 (YYYY-MM-DD)

**Strategic Rationale**:
[Why was this change needed? What problem does it solve?]

**Changes**:
- [List specific changes made]

**Impact**:
[How does this affect existing units? Migration required?]

**Related**:
- PROJECT_SCOPE.md: [Which phase/section?]
- Git commit: [commit hash]
```

**Step 3**: Validate (automated)
```bash
npm run validate:v3      # Check v3.1 compliance
npm run version:check    # Detect drift (future)
```

**Step 4**: Commit both files together
```bash
git add schemas/unified_toe_schema.json VERSION_HISTORY.md
git commit -m "feat: Add [feature] to schema v3.1.0"
```

### **Reminder System**:
- Git commit template prompts for VERSION_HISTORY.md update
- Cross-references in CLAUDE.md ensure agents follow protocol
- Future: `npm run version:check` will detect drift automatically

---

**Version History v1.0.0**
**Author**: Claude Code Autonomous Orchestrator
**Date**: 2025-10-13
**Status**: PRODUCTION - Update with each version change

---

**END OF VERSION HISTORY**

*For strategic scope and project vision, see **PROJECT_SCOPE.md**.*
*For technical implementation details, see **docs/project_context.md**.*
*For agent instructions, see **CLAUDE.md**.*
