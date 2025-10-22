#!/usr/bin/env node

/**
 * Collect Discoveries - Phase 2
 *
 * Scans completed unit JSON files for discovered_units field.
 * Agents may find units during research that weren't in the seed file.
 *
 * Output: DISCOVERED_UNITS.md with manual review format
 *
 * Usage: node scripts/collect_discoveries.js
 */

const fs = require('fs').promises;
const path = require('path');
const paths = require('./lib/canonical_paths');

const PROJECT_ROOT = path.join(__dirname, '..');
const DISCOVERIES_PATH = path.join(PROJECT_ROOT, 'DISCOVERED_UNITS.md');

async function scanForDiscoveries() {
    const discoveries = [];
    const canonicalUnitsDir = paths.UNITS_DIR;

    try {
        const files = await fs.readdir(canonicalUnitsDir);

        for (const filename of files) {
            if (!filename.endsWith('_toe.json') || filename.startsWith('unit_')) {
                continue;
            }

            const filePath = path.join(canonicalUnitsDir, filename);

            try {
                const content = await fs.readFile(filePath, 'utf-8');
                const unit = JSON.parse(content);

                // Check for discovered_units field
                if (unit.discovered_units && Array.isArray(unit.discovered_units) && unit.discovered_units.length > 0) {
                    for (const discovered of unit.discovered_units) {
                        discoveries.push({
                            foundInFile: filename,
                            discoveredUnit: discovered,
                            discoveryContext: {
                                nation: unit.nation,
                                quarter: unit.quarter,
                                sourceUnit: unit.unit_designation || unit.designation
                            }
                        });
                    }
                }
            } catch (error) {
                console.warn(`⚠️  Could not parse ${filename}:`, error.message);
            }
        }
    } catch (error) {
        console.error('❌ Failed to scan units directory:', error.message);
        return [];
    }

    return discoveries;
}

async function generateDiscoveriesMarkdown(discoveries) {
    if (discoveries.length === 0) {
        return `# Discovered Units

**Generated**: ${new Date().toISOString()}

**Status**: No discoveries found

All units extracted so far were already in seed file.

---

## About Discoveries

During unit extraction, agents may find references to units that weren't in the original seed file:
- Parent corps/armies mentioned in division documents
- Sibling units in the same formation
- Additional quarters where a unit was active
- Subordinate units (brigades, regiments) worth extracting

When discoveries are found, they appear here for manual review before being added to the work queue.
`;
    }

    // Group by discovery type
    const byType = {
        newUnit: [],
        additionalQuarter: [],
        hierarchy: [],
        other: []
    };

    for (const disc of discoveries) {
        const du = disc.discoveredUnit;
        if (du.reason && du.reason.includes('additional quarter')) {
            byType.additionalQuarter.push(disc);
        } else if (du.reason && du.reason.includes('parent')) {
            byType.hierarchy.push(disc);
        } else if (du.designation && !du.quarters) {
            byType.newUnit.push(disc);
        } else {
            byType.other.push(disc);
        }
    }

    let md = `# Discovered Units

**Generated**: ${new Date().toISOString()}

**Total Discoveries**: ${discoveries.length}

---

## ⚠️ MANUAL REVIEW REQUIRED

These units were discovered during extraction but were NOT in the seed file.
Review each discovery and decide whether to add to work queue.

**Actions**:
1. Review each discovery below
2. Verify unit actually exists (cross-reference with sources)
3. Run: \`node scripts/add_discovered_to_queue.js\` to add approved units

---
`;

    if (byType.additionalQuarter.length > 0) {
        md += `## 📅 Additional Quarters (${byType.additionalQuarter.length})

Existing units found in additional quarters not listed in seed:

`;
        for (const disc of byType.additionalQuarter) {
            const du = disc.discoveredUnit;
            md += `### ${du.designation} - ${du.quarter || du.quarters?.join(', ')}\n\n`;
            md += `- **Found in**: ${disc.foundInFile}\n`;
            md += `- **Nation**: ${du.nation || disc.discoveryContext.nation}\n`;
            md += `- **Type**: ${du.type || 'unknown'}\n`;
            md += `- **Source**: ${du.source || 'Not specified'}\n`;
            md += `- **Confidence**: ${du.confidence || 'Not specified'}\n`;
            md += `- **Reason**: ${du.reason || 'Additional quarter found during extraction'}\n`;
            md += `\n**Decision**: [ ] Add to queue  [ ] Skip (reason: ___________)\n\n`;
            md += `---\n\n`;
        }
    }

    if (byType.hierarchy.length > 0) {
        md += `## 🏛️ Hierarchy Discoveries (${byType.hierarchy.length})

Parent/sibling units mentioned but not in seed:

`;
        for (const disc of byType.hierarchy) {
            const du = disc.discoveredUnit;
            md += `### ${du.designation} - ${du.quarter || du.quarters?.join(', ')}\n\n`;
            md += `- **Found in**: ${disc.foundInFile}\n`;
            md += `- **Nation**: ${du.nation || disc.discoveryContext.nation}\n`;
            md += `- **Type**: ${du.type || 'unknown'}\n`;
            md += `- **Source**: ${du.source || 'Not specified'}\n`;
            md += `- **Confidence**: ${du.confidence || 'Not specified'}\n`;
            md += `- **Reason**: ${du.reason || 'Hierarchy relationship found'}\n`;
            md += `\n**Decision**: [ ] Add to queue  [ ] Skip (reason: ___________)\n\n`;
            md += `---\n\n`;
        }
    }

    if (byType.newUnit.length > 0) {
        md += `## 🆕 New Units (${byType.newUnit.length})

Completely new units not in seed file:

`;
        for (const disc of byType.newUnit) {
            const du = disc.discoveredUnit;
            md += `### ${du.designation} - ${du.quarter || du.quarters?.join(', ')}\n\n`;
            md += `- **Found in**: ${disc.foundInFile}\n`;
            md += `- **Nation**: ${du.nation || disc.discoveryContext.nation}\n`;
            md += `- **Type**: ${du.type || 'unknown'}\n`;
            md += `- **Source**: ${du.source || 'Not specified'}\n`;
            md += `- **Confidence**: ${du.confidence || 'Not specified'}\n`;
            md += `- **Reason**: ${du.reason || 'Unit discovered during research'}\n`;
            md += `\n**Decision**: [ ] Add to queue  [ ] Skip (reason: ___________)\n\n`;
            md += `---\n\n`;
        }
    }

    if (byType.other.length > 0) {
        md += `## 📝 Other Discoveries (${byType.other.length})

Miscellaneous discoveries requiring review:

`;
        for (const disc of byType.other) {
            const du = disc.discoveredUnit;
            md += `### ${du.designation || 'Unknown'} - ${du.quarter || du.quarters?.join(', ') || 'Unknown'}\n\n`;
            md += `- **Found in**: ${disc.foundInFile}\n`;
            md += `- **Nation**: ${du.nation || disc.discoveryContext.nation}\n`;
            md += `- **Type**: ${du.type || 'unknown'}\n`;
            md += `- **Source**: ${du.source || 'Not specified'}\n`;
            md += `- **Confidence**: ${du.confidence || 'Not specified'}\n`;
            md += `- **Reason**: ${du.reason || 'Discovery during extraction'}\n`;
            md += `\n**Decision**: [ ] Add to queue  [ ] Skip (reason: ___________)\n\n`;
            md += `---\n\n`;
        }
    }

    md += `## 📋 Next Steps

After reviewing discoveries:

1. **Verify units exist**: Cross-reference with historical sources
2. **Check seed file**: Confirm unit truly missing (not just naming mismatch)
3. **Add approved units**:
   \`\`\`bash
   node scripts/add_discovered_to_queue.js
   \`\`\`

4. **Update seed file**: Consider regenerating seed if many discoveries
5. **Document reasons**: Note why units were missing (scope change, oversight, etc.)

---

**Note**: Discoveries are NORMAL. Seed file creation is iterative. Agents may find:
- Units in additional quarters beyond initial scope
- Parent formations that should be extracted for completeness
- Subordinate units worth documenting separately

The goal is NOT zero discoveries, but EFFICIENT discovery workflow.
`;

    return md;
}

async function main() {
    console.log('\n🔍 Scanning for discovered units...\n');

    const discoveries = await scanForDiscoveries();

    console.log(`   Found ${discoveries.length} discoveries\n`);

    if (discoveries.length > 0) {
        console.log('📝 Generating DISCOVERED_UNITS.md...');
        const markdown = await generateDiscoveriesMarkdown(discoveries);
        await fs.writeFile(DISCOVERIES_PATH, markdown);
        console.log(`   ✅ Written to ${DISCOVERIES_PATH}\n`);

        console.log('⚠️  **MANUAL REVIEW REQUIRED**\n');
        console.log('   Review DISCOVERED_UNITS.md and decide which units to add to queue.');
        console.log('   Then run: node scripts/add_discovered_to_queue.js\n');
    } else {
        console.log('✅ No discoveries found - all units were in seed file\n');
        const markdown = await generateDiscoveriesMarkdown(discoveries);
        await fs.writeFile(DISCOVERIES_PATH, markdown);
        console.log(`   Generated empty report: ${DISCOVERIES_PATH}\n`);
    }
}

// Run
if (require.main === module) {
    main().catch(error => {
        console.error('❌ Discovery collection failed:', error.message);
        process.exit(1);
    });
}

module.exports = { scanForDiscoveries, generateDiscoveriesMarkdown };
