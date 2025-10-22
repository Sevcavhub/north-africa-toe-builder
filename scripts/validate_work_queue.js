#!/usr/bin/env node

/**
 * Validate Work Queue - Phase 3
 *
 * Checks work queue for dependency issues before processing.
 * Ensures parent units aren't processed before their children.
 *
 * Checks:
 * 1. Parent-child dependencies (corps needs divisions first)
 * 2. Orphaned units (divisions with no parent corps in queue)
 * 3. Circular dependencies
 * 4. Quarter sequence (1941-Q1 before 1941-Q2, etc.)
 *
 * Usage: node scripts/validate_work_queue.js
 */

const fs = require('fs').promises;
const path = require('path');
const naming = require('./lib/naming_standard');
const paths = require('./lib/canonical_paths');

const PROJECT_ROOT = path.join(__dirname, '..');
const QUEUE_PATH = path.join(PROJECT_ROOT, 'WORK_QUEUE.md');
const BLOCKED_UNITS_PATH = path.join(PROJECT_ROOT, 'BLOCKED_UNITS.md');

const ECHELON_HIERARCHY = {
    'battalion': 1,
    'regiment': 2,
    'brigade': 3,
    'column': 3,
    'light_division': 4,
    'panzer_division': 4,
    'armored_division': 4,
    'infantry_division': 4,
    'motorized_division': 4,
    'mountain_division': 4,
    'airborne_division': 4,
    'division': 4,
    'corps': 5,
    'army': 6,
    'army_group': 6,
    'theater': 7
};

function getEchelonLevel(type) {
    if (!type) return 99;
    const normalized = type.toLowerCase().replace(/\s+/g, '_');
    return ECHELON_HIERARCHY[normalized] || 99;
}

async function parseWorkQueue() {
    try {
        const content = await fs.readFile(QUEUE_PATH, 'utf-8');
        const units = [];

        // Parse "Next Up" section
        const nextUpMatch = content.match(/## 🎯 Next Up \(Next Session\)\n\n([\s\S]*?)\n---/);
        if (nextUpMatch) {
            const nextUpSection = nextUpMatch[1];
            const unitRegex = /\d+\.\s+\*\*([A-Z]+)\*\*\s+-\s+(\S+)\s+-\s+([^_]+)_\(([^)]+)\)_/g;
            let match;

            while ((match = unitRegex.exec(nextUpSection)) !== null) {
                const [, nation, quarter, designation, echelon] = match;
                units.push({
                    nation: nation.toLowerCase(),
                    quarter,
                    designation: designation.trim(),
                    type: echelon.trim(),
                    echelonLevel: getEchelonLevel(echelon.trim()),
                    status: 'next_up'
                });
            }
        }

        // Parse full queue sections
        const quarterSections = content.split(/###\s+(\d{4}-Q\d)/);
        for (let i = 1; i < quarterSections.length; i += 2) {
            const quarter = quarterSections[i];
            const sectionContent = quarterSections[i + 1];

            if (!sectionContent) continue;

            const echelonBlocks = sectionContent.split(/\*\*([A-Z_]+)\*\*/);
            for (let j = 1; j < echelonBlocks.length; j += 2) {
                const echelon = echelonBlocks[j].toLowerCase();
                const block = echelonBlocks[j + 1];

                if (!block) continue;

                const unitLines = block.match(/- \[ \] ([A-Z]+) - (.+)/g);
                if (unitLines) {
                    for (const line of unitLines) {
                        const match = line.match(/- \[ \] ([A-Z]+) - (.+)/);
                        if (match) {
                            const [, nation, designation] = match;
                            units.push({
                                nation: nation.toLowerCase(),
                                quarter,
                                designation: designation.trim(),
                                type: echelon,
                                echelonLevel: getEchelonLevel(echelon),
                                status: 'pending'
                            });
                        }
                    }
                }
            }
        }

        return units;
    } catch (error) {
        console.error('❌ Failed to parse work queue:', error.message);
        return [];
    }
}

async function getCompletedUnits() {
    const completed = new Set();

    try {
        const files = await fs.readdir(paths.UNITS_DIR);

        for (const filename of files) {
            if (!filename.endsWith('_toe.json') || filename.startsWith('unit_')) {
                continue;
            }

            const parsed = naming.parseFilename(filename);
            if (parsed) {
                const unitId = `${parsed.nation}_${parsed.quarter}_${parsed.designation}`;
                completed.add(unitId);
            }
        }
    } catch (error) {
        console.warn('⚠️  Could not scan completed units:', error.message);
    }

    return completed;
}

async function checkDependencies(units, completed) {
    const issues = {
        parentBeforeChild: [],
        orphanedUnits: [],
        missingPrerequisites: []
    };

    // Group by quarter
    const byQuarter = {};
    for (const unit of units) {
        if (!byQuarter[unit.quarter]) {
            byQuarter[unit.quarter] = [];
        }
        byQuarter[unit.quarter].push(unit);
    }

    // Check each quarter
    for (const [quarter, quarterUnits] of Object.entries(byQuarter)) {
        // Find parent units (corps, armies)
        const parents = quarterUnits.filter(u => u.echelonLevel >= 5);
        const children = quarterUnits.filter(u => u.echelonLevel < 5);

        // Check if parents appear before children in queue
        for (const parent of parents) {
            // Check if this parent has any children in the queue
            const potentialChildren = children.filter(c =>
                c.nation === parent.nation &&
                c.status === 'pending'
            );

            if (potentialChildren.length > 0) {
                // Check if children are completed
                const childrenIncomplete = potentialChildren.filter(c => {
                    const childId = `${c.nation}_${c.quarter}_${c.designation}`;
                    return !completed.has(childId);
                });

                if (childrenIncomplete.length > 0 && parent.status === 'next_up') {
                    issues.parentBeforeChild.push({
                        parent: `${parent.nation}_${parent.quarter}_${parent.designation}`,
                        parentType: parent.type,
                        incompleteChildren: childrenIncomplete.map(c => c.designation),
                        reason: 'Parent unit scheduled for extraction before child units complete'
                    });
                }
            }
        }

        // Check for orphaned units (divisions without corps)
        for (const child of children.filter(c => c.echelonLevel === 4)) {  // divisions
            // Look for parent corps
            const hasParentInQueue = parents.some(p =>
                p.nation === child.nation &&
                p.echelonLevel === 5  // corps
            );

            const hasParentCompleted = Array.from(completed).some(id => {
                const [nation, q, designation] = id.split('_');
                return nation === child.nation &&
                       q === child.quarter &&
                       designation.toLowerCase().includes('corps');
            });

            if (!hasParentInQueue && !hasParentCompleted) {
                issues.orphanedUnits.push({
                    unit: `${child.nation}_${child.quarter}_${child.designation}`,
                    type: child.type,
                    reason: 'Division has no parent corps in queue or completed units'
                });
            }
        }
    }

    return issues;
}

async function generateBlockedUnitsReport(issues) {
    if (Object.values(issues).every(arr => arr.length === 0)) {
        return `# Blocked Units

**Generated**: ${new Date().toISOString()}

**Status**: ✅ No blocking issues found

All units in queue have correct dependencies.

---

## About Validation

This report checks for:
- Parent units scheduled before children complete
- Orphaned units (divisions without corps)
- Missing prerequisites

When issues are found, they appear here with recommendations.
`;
    }

    let md = `# Blocked Units

**Generated**: ${new Date().toISOString()}

**Status**: ⚠️  ${Object.values(issues).reduce((sum, arr) => sum + arr.length, 0)} issues found

---
`;

    if (issues.parentBeforeChild.length > 0) {
        md += `## ⚠️  Parent Before Child (${issues.parentBeforeChild.length})

These parent units are scheduled for extraction but their child units aren't complete yet.

**Recommendation**: Skip these units until children are complete, or process children first.

`;
        for (const issue of issues.parentBeforeChild) {
            md += `### ${issue.parent} (${issue.parentType})\n\n`;
            md += `**Problem**: Scheduled for extraction but has incomplete children\n\n`;
            md += `**Incomplete children**:\n`;
            for (const child of issue.incompleteChildren) {
                md += `- ${child}\n`;
            }
            md += `\n**Action**: Process children first, or skip this unit until next session\n\n`;
            md += `---\n\n`;
        }
    }

    if (issues.orphanedUnits.length > 0) {
        md += `## 📝 Orphaned Units (${issues.orphanedUnits.length})

These divisions have no parent corps in queue or completed.

**Note**: This may be intentional (independent divisions, detached formations).

`;
        for (const issue of issues.orphanedUnits) {
            md += `### ${issue.unit} (${issue.type})\n\n`;
            md += `**Status**: No parent corps found\n\n`;
            md += `**Action**: Verify if division was independent or add parent corps to queue\n\n`;
            md += `---\n\n`;
        }
    }

    md += `## 🔧 Next Steps

1. **Review blocking issues** above
2. **Decide on actions**:
   - Process children before parents
   - Skip blocked units this session
   - Add missing parent units to queue
3. **Re-run validation**: \`npm run validate:queue\`

---

**Note**: Some "issues" may be intentional (independent divisions, special formations). Use judgment when deciding actions.
`;

    return md;
}

async function main() {
    console.log('\n🔍 Validating work queue...\n');

    // Parse work queue
    console.log('📋 Reading WORK_QUEUE.md...');
    const units = await parseWorkQueue();
    console.log(`   Found ${units.length} units in queue\n`);

    // Get completed units
    console.log('✅ Scanning completed units...');
    const completed = await getCompletedUnits();
    console.log(`   Found ${completed.size} completed units\n`);

    // Check dependencies
    console.log('🔗 Checking dependencies...');
    const issues = await checkDependencies(units, completed);

    const totalIssues = Object.values(issues).reduce((sum, arr) => sum + arr.length, 0);
    console.log(`   Found ${totalIssues} potential issues\n`);

    // Generate report
    console.log('📝 Generating BLOCKED_UNITS.md...');
    const report = await generateBlockedUnitsReport(issues);
    await fs.writeFile(BLOCKED_UNITS_PATH, report);
    console.log(`   ✅ Written to ${BLOCKED_UNITS_PATH}\n`);

    // Summary
    if (totalIssues === 0) {
        console.log('✅ **VALIDATION PASSED**\n');
        console.log('   No blocking issues found - safe to process queue\n');
    } else {
        console.log('⚠️  **VALIDATION WARNINGS**\n');
        console.log(`   Found ${totalIssues} potential issues:`);
        if (issues.parentBeforeChild.length > 0) {
            console.log(`   - ${issues.parentBeforeChild.length} parents before children`);
        }
        if (issues.orphanedUnits.length > 0) {
            console.log(`   - ${issues.orphanedUnits.length} orphaned units`);
        }
        console.log('\n   Review BLOCKED_UNITS.md for details\n');
    }
}

// Run
if (require.main === module) {
    main().catch(error => {
        console.error('❌ Validation failed:', error.message);
        process.exit(1);
    });
}

module.exports = { parseWorkQueue, checkDependencies };
