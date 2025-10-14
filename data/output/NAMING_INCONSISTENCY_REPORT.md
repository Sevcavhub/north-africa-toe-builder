# Naming Inconsistency Analysis Report

## Problem Summary
Unit filenames have THREE different naming patterns across the codebase, causing matching failures.

## Documented Standard (CLAUDE.md:360)
```
Pattern: {nation}_{quarter}_{unit_designation}_toe.json
Example: german_1941q2_15th_panzer_division_toe.json
```

**Standard specifies:**
- Nation: adjective form (german, italian, british, french, american)
- Quarter: lowercase, no hyphen (1941q2)

## Actual File Patterns Found

### Pattern A (Correct per CLAUDE.md):
- german_1941q1_deutsches_afrikakorps_toe.json
- italian_1941q1_pavia_division_toe.json
- british_1941q1_7th_armoured_division_toe.json

### Pattern B (Wrong - country name):
- germany_1941q1_5_leichte_division_toe.json
- italy_1941-q1_trento_division_toe.json
- britain_1941-q1_5th_indian_division_toe.json

### Pattern C (Wrong - special cases):
- newzealand_1941q1_2nd_nz_division_toe.json (should be british)
- australia_1941q1_9th_australian_division_toe.json (should be british)

### Pattern D (Wrong - hyphen in quarter):
- german_1941-q1_deutsches_afrikakorps_toe.json
- italy_1941-q1_trento_division_toe.json

## Root Causes

### 1. session_start.js (lines 154-159)
```javascript
const nationMap = {
    'german_units': 'germany',   // ❌ WRONG - should be 'german'
    'italian_units': 'italy',    // ❌ WRONG - should be 'italian'
    'british_units': 'britain',  // ❌ WRONG - should be 'british'
    'usa_units': 'usa',          // ⚠️  Should be 'american'?
    'french_units': 'france'     // ❌ WRONG - should be 'french'
};
```

### 2. session_ready.js (lines 118-124) - SAME BUG
```javascript
const nations = {
    'german_units': 'germany',   // ❌ WRONG
    'italian_units': 'italy',    // ❌ WRONG
    'british_units': 'britain',  // ❌ WRONG
    'usa_units': 'usa',
    'french_units': 'france'     // ❌ WRONG
};
```

### 3. Quarter Format Inconsistency
- session_start.js line 166: `quarter.toLowerCase().replace(/-/, '')` → removes hyphen
- But some files still have hyphens (1941-q1)

### 4. Commonwealth Nation Handling
- CLAUDE.md says British includes Commonwealth (Australia, NZ, India, SA, Canada)
- But files use specific nation names (newzealand, australia)
- Should probably all be "british" with designation specifying division origin

## Files That Need Fixing

### Scripts with nation mapping:
1. ✅ session_ready.js (ALREADY FIXED with variation handling)
2. ❌ session_start.js (lines 154-159)
3. ❌ create_checkpoint.js (check for similar mapping)
4. ❌ generate_mdbook_chapters.js (check for similar mapping)
5. ❌ backfill_database.js (check for similar mapping)

### Documentation:
1. ✅ CLAUDE.md already correct
2. ❌ Need to add explicit nation list: german, italian, british, french, american

## Recommended Solution

### Step 1: Define Canonical Standard
Create `scripts/lib/naming_standard.js`:
```javascript
module.exports = {
    // Canonical nation values (adjective form)
    NATIONS: {
        GERMAN: 'german',
        ITALIAN: 'italian',
        BRITISH: 'british',      // Includes all Commonwealth
        AMERICAN: 'american',    // For USA
        FRENCH: 'french'
    },
    
    // Map from seed file keys to canonical nation
    NATION_MAP: {
        'german_units': 'german',
        'italian_units': 'italian',
        'british_units': 'british',
        'usa_units': 'american',
        'french_units': 'french'
    },
    
    // Generate standard filename
    generateFilename(nation, quarter, designation) {
        const cleanNation = this.NATION_MAP[nation] || nation.toLowerCase();
        const cleanQuarter = quarter.toLowerCase().replace(/-/g, '');
        const cleanDesignation = designation
            .toLowerCase()
            .replace(/[^a-z0-9]/g, '_')
            .replace(/_+/g, '_')
            .replace(/^_|_$/g, '');
        return `${cleanNation}_${cleanQuarter}_${cleanDesignation}_toe.json`;
    }
};
```

### Step 2: Update All Scripts
Import and use the standard:
```javascript
const naming = require('./lib/naming_standard');
const filename = naming.generateFilename(nation, quarter, designation);
```

### Step 3: Update CLAUDE.md
Add explicit nation list:
```markdown
## Nation Values (CANONICAL)
ALWAYS use these exact values:
- german (NOT germany)
- italian (NOT italy)
- british (NOT britain - includes ALL Commonwealth: Australia, NZ, India, SA, Canada)
- american (NOT usa)
- french (NOT france)
```

### Step 4: Optional - Rename Existing Files
Create migration script to rename all existing files to canonical format.
OR: Keep existing files, but ensure all NEW files use standard.

## Impact

### If We Fix This:
✅ All scripts will generate consistent filenames
✅ File matching will work reliably
✅ No need for complex variation handling
✅ Clear documentation for future development

### If We Don't Fix This:
❌ Must maintain variation handling in every script
❌ High risk of bugs when adding new scripts
❌ Confusing for developers
❌ May cause data loss if variations missed
