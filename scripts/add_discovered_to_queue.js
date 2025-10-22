#!/usr/bin/env node

/**
 * Add Discovered Units to Queue - Phase 2
 *
 * Reads DISCOVERED_UNITS.md and adds approved units to work queue.
 * Does NOT modify seed file - adds to queue directly for processing.
 *
 * Workflow:
 * 1. Read DISCOVERED_UNITS.md
 * 2. Find units marked with [x] for addition
 * 3. Append to WORK_QUEUE.md in appropriate position
 * 4. Mark units as added in DISCOVERED_UNITS.md
 *
 * Usage: node scripts/add_discovered_to_queue.js
 */

const fs = require('fs').promises;
const path = require('path');
const naming = require('./lib/naming_standard');

const PROJECT_ROOT = path.join(__dirname, '..');
const DISCOVERIES_PATH = path.join(PROJECT_ROOT, 'DISCOVERED_UNITS.md');
const QUEUE_PATH = path.join(PROJECT_ROOT, 'WORK_QUEUE.md');
const SEED_PATH = path.join(PROJECT_ROOT, 'projects/north_africa_seed_units_COMPLETE.json');

async function parseDiscoveriesFile() {
    try {
        const content = await fs.readFile(DISCOVERIES_PATH, 'utf-8');

        // Find units with [x] checkbox (approved for addition)
        const approved = [];
        const sections = content.split('###');

        for (const section of sections) {
            // Look for checked boxes
            if (!section.includes('[x] Add to queue') && !section.includes('[X] Add to queue')) {
                continue;
            }

            // Extract unit details from section
            const lines = section.split('\n');
            const titleMatch = lines[0].match(/^(.+?)\s+-\s+(.+?)$/);

            if (!titleMatch) continue;

            const designation = titleMatch[1].trim();
            const quarter = titleMatch[2].trim();

            // Extract fields
            const nation = extractField(section, 'Nation');
            const type = extractField(section, 'Type');
            const source = extractField(section, 'Source');
            const confidence = extractField(section, 'Confidence');
            const reason = extractField(section, 'Reason');

            if (nation && designation) {
                approved.push({
                    nation: naming.normalizeNation(nation.toLowerCase()),
                    quarter: naming.normalizeQuarter(quarter),
                    designation,
                    type: type || 'unknown',
                    source,
                    confidence: confidence || 'medium',
                    reason
                });
            }
        }

        return approved;
    } catch (error) {
        if (error.code === 'ENOENT') {
            console.log('📝 No DISCOVERED_UNITS.md file found');
            console.log('   Run: node scripts/collect_discoveries.js first\n');
            return [];
        }
        throw error;
    }
}

function extractField(section, fieldName) {
    const match = section.match(new RegExp(`\\*\\*${fieldName}\\*\\*:\\s*(.+?)$`, 'm'));
    return match ? match[1].trim() : null;
}

async function addToSeedFile(units) {
    console.log('📋 Adding discoveries to seed file...');

    try {
        const seedData = JSON.parse(await fs.readFile(SEED_PATH, 'utf-8'));
        let added = 0;

        for (const unit of units) {
            // Determine nation key
            const nationKey = Object.keys(naming.NATION_MAP).find(
                key => naming.NATION_MAP[key] === unit.nation
            );

            if (!nationKey) {
                console.warn(`   ⚠️  Unknown nation: ${unit.nation} for ${unit.designation}`);
                continue;
            }

            // Get or create nation array
            if (!seedData[nationKey]) {
                seedData[nationKey] = [];
            }

            // Check if unit already exists
            const existing = seedData[nationKey].find(u => u.designation === unit.designation);

            if (existing) {
                // Add quarter if not already present
                if (!existing.quarters) {
                    existing.quarters = [];
                }

                if (!existing.quarters.includes(unit.quarter)) {
                    existing.quarters.push(unit.quarter);
                    existing.quarters.sort();
                    added++;
                    console.log(`   ✅ Added quarter ${unit.quarter} to ${unit.designation}`);
                } else {
                    console.log(`   ⏭️  ${unit.designation} already has ${unit.quarter}`);
                }
            } else {
                // Add new unit
                const newUnit = {
                    designation: unit.designation,
                    type: unit.type,
                    quarters: [unit.quarter],
                    source: unit.source || 'discovered',
                    confidence: parseFloat(unit.confidence) || 75,
                    battles: []
                };

                seedData[nationKey].push(newUnit);
                added++;
                console.log(`   ✅ Added new unit: ${unit.designation} (${unit.quarter})`);
            }
        }

        // Recalculate totals
        let totalUnits = 0;
        let totalUnitQuarters = 0;

        for (const [key, value] of Object.entries(seedData)) {
            if (key.endsWith('_units') && Array.isArray(value)) {
                totalUnits += value.length;
                totalUnitQuarters += value.reduce((sum, u) => sum + (u.quarters?.length || 0), 0);
            }
        }

        seedData.total_units = totalUnits;
        seedData.total_unit_quarters = totalUnitQuarters;

        // Save seed file
        await fs.writeFile(SEED_PATH, JSON.stringify(seedData, null, 2));

        console.log(`   ✅ Added ${added} units/quarters to seed file`);
        console.log(`   📊 New totals: ${totalUnits} units, ${totalUnitQuarters} unit-quarters\n`);

        return { added, totalUnits, totalUnitQuarters };
    } catch (error) {
        console.error('❌ Failed to update seed file:', error.message);
        throw error;
    }
}

async function regenerateWorkQueue() {
    console.log('🔄 Regenerating work queue...');

    try {
        const { execSync } = require('child_process');
        execSync('node scripts/generate_work_queue.js', {
            cwd: PROJECT_ROOT,
            stdio: 'pipe'
        });

        console.log('   ✅ Work queue regenerated\n');
        return true;
    } catch (error) {
        console.error('❌ Failed to regenerate work queue:', error.message);
        return false;
    }
}

async function markDiscoveriesAsAdded(approvedUnits) {
    console.log('📝 Updating DISCOVERED_UNITS.md...');

    try {
        let content = await fs.readFile(DISCOVERIES_PATH, 'utf-8');

        // Mark approved units as added
        for (const unit of approvedUnits) {
            // Replace [x] Add to queue with status message
            const searchPattern = new RegExp(
                `(### ${unit.designation.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}[\\s\\S]*?\\[x\\] Add to queue)`,
                'gi'
            );

            content = content.replace(
                searchPattern,
                `$1 ✅ ADDED (${new Date().toISOString().split('T')[0]})`
            );
        }

        await fs.writeFile(DISCOVERIES_PATH, content);
        console.log(`   ✅ Marked ${approvedUnits.length} units as added\n`);
    } catch (error) {
        console.warn('⚠️  Could not update DISCOVERED_UNITS.md:', error.message);
    }
}

async function main() {
    console.log('\n🎯 Adding discovered units to queue...\n');

    // Parse discoveries file
    console.log('📖 Reading DISCOVERED_UNITS.md...');
    const approved = await parseDiscoveriesFile();

    if (approved.length === 0) {
        console.log('\n📋 No approved discoveries found\n');
        console.log('   To approve discoveries:');
        console.log('   1. Open DISCOVERED_UNITS.md');
        console.log('   2. Change [ ] to [x] for units to add');
        console.log('   3. Run this script again\n');
        return;
    }

    console.log(`   Found ${approved.length} approved units\n`);

    // Show summary
    console.log('📊 Units to add:\n');
    approved.forEach((u, i) => {
        console.log(`   ${i + 1}. ${u.nation.toUpperCase()} - ${u.designation} (${u.quarter})`);
    });
    console.log('');

    // Add to seed file
    const result = await addToSeedFile(approved);

    // Regenerate work queue
    await regenerateWorkQueue();

    // Mark as added in discoveries file
    await markDiscoveriesAsAdded(approved);

    console.log('✨ Discovery integration complete!\n');
    console.log(`📊 Summary:`);
    console.log(`   - ${approved.length} units processed`);
    console.log(`   - ${result.added} additions made`);
    console.log(`   - New seed totals: ${result.totalUnits} units, ${result.totalUnitQuarters} unit-quarters`);
    console.log(`   - Work queue regenerated`);
    console.log('');
    console.log('🚀 Run `npm run session:start` to process new units\n');
}

// Run
if (require.main === module) {
    main().catch(error => {
        console.error('❌ Failed to add discoveries:', error.message);
        process.exit(1);
    });
}

module.exports = { parseDiscoveriesFile, addToSeedFile };
