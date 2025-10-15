# Orchestrator Audit - October 15, 2025

## Summary

**CRITICAL FINDING:** 3 out of 5 orchestrators are MISSING Phase 6 Seed Reconciliation!

---

## NPM Commands & Files Audit

### ✅ ALL NPM SCRIPTS HAVE VALID .JS FILES (except test)

| NPM Command | JavaScript File | File Exists | Has Phase 6 | Status |
|-------------|----------------|-------------|-------------|--------|
| `npm start` | `src/orchestrator.js` | ✅ | ✅ | **ACTIVE** - API-based |
| `npm run start:autonomous` | `src/autonomous_orchestrator.js` | ✅ | ✅ | **ACTIVE** - No API (used by /kstart) |
| `npm run start:file` | `src/file_orchestrator.js` | ✅ | ❌ | **OBSOLETE?** |
| `npm run start:claude` | `src/single_session_orchestrator.js` | ✅ | ❌ | **OBSOLETE?** |
| `npm run start:claude:interactive` | `src/single_session_orchestrator.js` | ✅ | ❌ | **OBSOLETE?** |
| `npm run orchestrate` | `src/intelligent_orchestrator.js` | ✅ | ❌ | **OBSOLETE?** |
| `npm run orchestrate:resume` | `src/intelligent_orchestrator.js` | ✅ | ❌ | **OBSOLETE?** |
| `npm run agent` | `src/agent_runner.js` | ✅ | N/A | Helper |
| `npm run test` | `test/run-tests.js` | ❌ | N/A | **MISSING FILE!** |
| `npm run session:start` | `scripts/session_start.js` | ✅ | N/A | **ACTIVE** |
| `npm run session:end` | `scripts/session_end.js` | ✅ | N/A | **ACTIVE** |

---

## Detailed Analysis

### 1. **src/orchestrator.js** ✅ COMPLETE
- **Purpose:** API-based orchestrator with full 7-phase workflow
- **Requires:** ANTHROPIC_API_KEY environment variable
- **Has Phase 6:** ✅ YES (executePhase6_SeedReconciliation)
- **Status:** **KEEP** - Most complete orchestrator
- **Used By:** `npm start`

### 2. **src/autonomous_orchestrator.js** ✅ COMPLETE (just fixed)
- **Purpose:** No-API orchestrator using Claude Code subscription
- **Requires:** Nothing (uses Claude Code Task tool)
- **Has Phase 6:** ✅ YES (just added in this session)
- **Status:** **KEEP** - Primary workflow for /kstart
- **Used By:** `npm run start:autonomous`, `/kstart`, `/krun-Autonomous`

### 3. **src/file_orchestrator.js** ❌ INCOMPLETE
- **Purpose:** File-based multi-agent coordination (separate terminals)
- **Requires:** Each agent in separate Claude Code terminal
- **Has Phase 6:** ❌ NO
- **Phases:** Only has Phase 1 & 2 implemented (source extraction, org building)
- **Status:** **OBSOLETE** - Experimental approach, incomplete
- **Used By:** `npm run start:file`
- **Recommendation:** **DELETE** or archive

### 4. **src/single_session_orchestrator.js** ❌ INCOMPLETE
- **Purpose:** Generates prompts to files, user pastes them manually
- **Requires:** Manual prompt/response workflow
- **Has Phase 6:** ❌ NO
- **Phases:** Only Phase 1 (document_parser prompts)
- **Status:** **OBSOLETE** - Superseded by autonomous_orchestrator
- **Used By:** `npm run start:claude`, `npm run start:claude:interactive`
- **Recommendation:** **DELETE** or archive

### 5. **src/intelligent_orchestrator.js** ❌ INCOMPLETE
- **Purpose:** Fully automated with file-based task coordination
- **Requires:** Separate agent terminals + interactive prompts
- **Has Phase 6:** ❌ NO
- **Phases:** Partial implementation (Phase 1 complete, others TODO)
- **Status:** **OBSOLETE** - Experimental approach, incomplete
- **Used By:** `npm run orchestrate`, `npm run orchestrate:resume`
- **Recommendation:** **DELETE** or archive

---

## Current Workflow (What Actually Works)

### ✅ **WORKING WORKFLOW:** /kstart → session:start → autonomous_orchestrator

```
User runs: /kstart
    ↓
npm run session:start (gets 3 recommended units)
    ↓
User pastes autonomous prompt
    ↓
General agent launches Task tool
    ↓
Task tool runs autonomous_orchestrator.js prompt
    ↓
Sub-agent processes 3 units through ALL 6 phases:
  - Phase 1: Setup & Planning
  - Phase 2: Document Extraction
  - Phase 3: Cross-Reference Validation
  - Phase 4: TO&E Generation
  - Phase 5: Output Generation
  - Phase 6: Seed Reconciliation ✅ (CRITICAL - Human-in-loop checkpoint)
    ↓
Units saved to canonical locations
Checkpoint created
Pattern database updated
```

### ❌ **BROKEN WORKFLOWS:** (Missing Phase 6)

1. `npm run start:file` → file_orchestrator.js (only Phase 1-2, no Phase 6)
2. `npm run start:claude` → single_session_orchestrator.js (only Phase 1, no Phase 6)
3. `npm run orchestrate` → intelligent_orchestrator.js (partial Phase 1, no Phase 6)

---

## Recommendations

### **IMMEDIATE ACTION REQUIRED:**

1. **Delete obsolete orchestrators:**
   - ❌ Delete `src/file_orchestrator.js` (or move to archive/)
   - ❌ Delete `src/single_session_orchestrator.js` (or move to archive/)
   - ❌ Delete `src/intelligent_orchestrator.js` (or move to archive/)
   - ❌ Remove corresponding npm scripts from package.json

2. **Fix missing test file:**
   - ❌ Create `test/run-tests.js` or remove `npm test` from package.json

3. **Simplify workflow:**
   - Keep only TWO orchestrators:
     - `src/orchestrator.js` (API-based, has Phase 6) ✅
     - `src/autonomous_orchestrator.js` (No API, has Phase 6) ✅
   - Keep session management:
     - `scripts/session_start.js` ✅
     - `scripts/session_end.js` ✅

---

## Cleanup Plan

### **Option A: Delete Obsolete Files**
```bash
# Remove obsolete orchestrators
rm src/file_orchestrator.js
rm src/single_session_orchestrator.js
rm src/intelligent_orchestrator.js

# Remove obsolete npm scripts from package.json
# Delete lines: start:file, start:claude, start:claude:interactive, orchestrate, orchestrate:resume

# Git commit
git add -A
git commit -m "chore: Remove obsolete orchestrators missing Phase 6"
```

### **Option B: Archive for Historical Reference**
```bash
# Create archive directory
mkdir -p archive/obsolete_orchestrators/

# Move obsolete orchestrators
mv src/file_orchestrator.js archive/obsolete_orchestrators/
mv src/single_session_orchestrator.js archive/obsolete_orchestrators/
mv src/intelligent_orchestrator.js archive/obsolete_orchestrators/

# Add README explaining why archived
cat > archive/obsolete_orchestrators/README.md <<EOF
# Obsolete Orchestrators

These orchestrators were experimental approaches that were superseded by
autonomous_orchestrator.js. They are missing Phase 6 Seed Reconciliation
(human-in-loop checkpoint added October 2025).

DO NOT USE these files - they are kept for historical reference only.

Active orchestrators:
- src/orchestrator.js (API-based)
- src/autonomous_orchestrator.js (No API, used by /kstart)
EOF

# Git commit
git add -A
git commit -m "chore: Archive obsolete orchestrators missing Phase 6"
```

---

## Final Simplified Architecture

After cleanup, you'll have:

### **Core Orchestrators (2)**
1. `src/orchestrator.js` - API-based (full 7 phases including Phase 6)
2. `src/autonomous_orchestrator.js` - No-API (full 6 phases including Phase 6)

### **Session Management (2)**
1. `scripts/session_start.js` - Start session, recommend 3 units
2. `scripts/session_end.js` - End session, save checkpoint

### **Slash Commands (3)**
1. `/kstart` → Runs session:start → launches autonomous orchestrator (3 units)
2. `/krun-Autonomous` → Runs start:autonomous → full batch (all remaining units)
3. `/kend` → Runs session:end → saves checkpoint

### **Helper Scripts (all others)**
- Agent runner, validators, checkpoint, memory helpers, etc.

---

## Questions Answered

**Q: Which .js runs when I use /kstart?**
A: `scripts/session_start.js` → generates prompt → general agent launches Task tool → `src/autonomous_orchestrator.js` prompt template executes

**Q: Does it have Phase 6?**
A: YES - `src/autonomous_orchestrator.js` now has Phase 6 Seed Reconciliation (just added in this session)

**Q: What about the other orchestrators?**
A: They are OBSOLETE and MISSING Phase 6. They should be deleted or archived.

**Q: Which npm commands should I use?**
A: Use ONLY:
- `npm run session:start` (via /kstart)
- `npm run session:end` (via /kend)
- `npm run start:autonomous` (via /krun-Autonomous for full batch)

**Q: Should I delete the obsolete files?**
A: YES - Recommend Option B (archive them) for historical reference, but remove npm scripts that reference them.

---

**Generated:** October 15, 2025
**Audit Status:** COMPLETE
**Action Required:** DELETE or ARCHIVE 3 obsolete orchestrators
