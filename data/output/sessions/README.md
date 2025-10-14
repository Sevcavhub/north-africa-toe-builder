# Archived Session Directories

**Created**: 2025-10-14
**Purpose**: Archive of historical autonomous session work
**Status**: READ-ONLY ARCHIVE

---

## ⚠️ **DO NOT USE THESE DIRECTORIES FOR NEW WORK**

These directories contain historical extraction sessions from before Architecture v4.0.

---

## Canonical Locations (ALWAYS USE THESE)

**For ALL new work and file lookups, use canonical locations:**

```
data/output/
├── units/              ⭐ Ground unit TO&E files (213 files - Phase 1-6 COMPLETE)
├── chapters/           ⭐ MDBook chapters (213 files)
├── air_units/          ⭐ Air force units (Phase 7+, future)
├── air_chapters/       ⭐ Air force chapters (Phase 7+, future)
├── scenarios/          ⭐ Battle scenarios (Phase 9+, future)
├── campaign/           ⭐ Campaign data (Phase 10+, future)
└── sessions/           📦 THIS DIRECTORY - Historical archive only
```

**Key Rule**: If you need a unit file, **ALWAYS** use `data/output/units/{filename}`, NEVER use files from `sessions/`.

---

## What's in This Archive?

Session directories contain historical work from autonomous extraction sessions:

- **Session-specific reports**: Progress logs, extraction summaries
- **Research notes**: Historical research interim findings
- **Validation logs**: QA audit results, compliance checks
- **Multiple unit copies**: Same unit may exist here AND in canonical location (use canonical!)
- **Intermediate files**: Work-in-progress data from multi-step processes

---

## Session Directory Naming

### Format: `autonomous_TIMESTAMP` or `session_TIMESTAMP`

Example: `autonomous_1760133539236`
- `autonomous` = autonomous orchestrator session
- `1760133539236` = Unix timestamp (milliseconds since epoch)

Convert timestamp to readable date:
```bash
# On Linux/Mac:
date -d @$(echo "1760133539236" | cut -c1-10)

# In Node.js:
node -e "console.log(new Date(1760133539236).toISOString())"
# Output: 2025-10-10T...
```

---

## Archive Structure

Each session directory may contain:

```
autonomous_TIMESTAMP/
├── units/                      # Unit JSON files (DUPLICATES - use canonical!)
│   ├── german_1941q2_15_panzer_division_toe.json
│   └── ...
├── chapters/                   # MDBook chapters (use canonical!)
├── reports/                    # Session-specific reports
├── research_reports/           # Research notes
├── PROGRESS_DASHBOARD.md       # Session progress
├── EXTRACTION_SUMMARY.md       # What was extracted
└── orchestration_metadata.json # Session metadata
```

---

## Why Sessions Were Archived

**Problem (Before Architecture v4.0)**:
- Each autonomous session created its own timestamped directory
- Same unit extracted multiple times = 5-7 copies across different sessions
- Scattered files caused counting errors (207 entries vs 202 unique units)
- Future phases couldn't determine which file was authoritative

**Solution (Architecture v4.0)**:
- All units consolidated to canonical locations (`data/output/units/`)
- Old session directories archived here for historical reference
- Future sessions use canonical locations (no more duplicates)
- Clear single source of truth for all phases

---

## Using Archived Data

### ✅ **Valid Uses**:
- Reviewing historical extraction process
- Checking session-specific reports
- Understanding how a specific unit was researched
- Audit trail / quality verification

### ❌ **Invalid Uses**:
- Reading unit TO&E data (use canonical location!)
- Generating MDBook chapters from archived units
- Cross-referencing between units (use canonical!)
- Any production workflow

---

## Migration History

**Consolidation**: 2025-10-14
- Script: `scripts/consolidate_canonical.js`
- Process: Found latest version of each unit, copied to canonical location
- Result: 213 unique units in `data/output/units/`

**Archival**: 2025-10-14
- Script: `scripts/archive_old_sessions.js`
- Process: Moved all `autonomous_*` directories to `sessions/`
- Result: Clean output structure, sessions preserved for audit

---

## Verification Commands

```bash
# Count canonical units (should be 213 for Phase 1-6)
ls data/output/units/*.json | wc -l

# Verify no scattered autonomous_* directories remain
ls data/output/autonomous_* 2>/dev/null | wc -l
# Expected: 0

# Count archived sessions
ls data/output/sessions/ | wc -l
# Expected: 15-20 (depending on extraction history)
```

---

## For Developers

When writing new code, **ALWAYS** use `canonical_paths.js`:

```javascript
const paths = require('./scripts/lib/canonical_paths');

// ✅ CORRECT:
const unitPath = paths.getUnitPath('german', '1941q2', '15_panzer_division');
// Returns: data/output/units/german_1941q2_15_panzer_division_toe.json

// ❌ WRONG:
const unitPath = 'data/output/autonomous_1760133539236/units/german_...';
// Never hardcode session directory paths!
```

---

## Related Documentation

- **Architecture v4.0**: See `VERSION_HISTORY.md` for complete architectural changes
- **Canonical paths**: See `scripts/lib/canonical_paths.js` for path definitions
- **Output structure**: See `CLAUDE.md` for complete output directory documentation
- **Phase 7-10**: See `PROJECT_SCOPE.md` for future canonical locations

---

## Archive Maintenance

This archive is **append-only** - sessions are never deleted, only added.

**Disk space**: If sessions grow too large in future:
1. Compress old sessions: `tar -czf sessions_YYYY.tar.gz sessions/autonomous_*`
2. Move compressed archives to long-term storage
3. Keep index for reference

---

**Last Updated**: 2025-10-14
**Archive Location**: `D:\north-africa-toe-builder\data\output\sessions\`
**Canonical Locations**: `data/output/units/`, `data/output/chapters/`, etc.

**Remember**: For ALL production work, use canonical locations! 🎯
