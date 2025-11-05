/**
 * Update Seed File with Full Official Names + Aliases
 *
 * This script:
 * 1. Scans all completed unit files to extract official designations
 * 2. Maps abbreviated seed names to full official names found by agents
 * 3. Updates seed file with full names as primary + aliases array
 */

const fs = require('fs');
const path = require('path');

// Load seed file
const seedPath = 'projects/north_africa_seed_units_COMPLETE.json';
const seed = JSON.parse(fs.readFileSync(seedPath, 'utf-8'));

// Load completed units
const state = JSON.parse(fs.readFileSync('WORKFLOW_STATE.json', 'utf-8'));
const completedSet = new Set(state.completed);

// Nation mapping (seed uses usa_units, files use american)
const nationMap = {
    german_units: 'german',
    italian_units: 'italian',
    british_units: 'british',
    usa_units: 'american',
    french_units: 'french'
};

// Track official names found by agents
const nameMapping = {};

console.log('=== SCANNING COMPLETED UNITS FOR OFFICIAL NAMES ===\n');

// Scan all completed unit files
state.completed.forEach(unitId => {
    const filename = `${unitId}_toe.json`;
    const filepath = path.join('data/output/units', filename);

    if (!fs.existsSync(filepath)) {
        console.log('⚠️  File not found:', filename);
        return;
    }

    try {
        const unit = JSON.parse(fs.readFileSync(filepath, 'utf-8'));
        const officialName = unit.unit_designation;
        const nation = unit.nation;
        const quarter = unit.quarter;

        // Create key for mapping
        const key = `${nation}_${quarter}`;
        if (!nameMapping[key]) {
            nameMapping[key] = {};
        }

        // Normalize for comparison
        const normalized = officialName.toLowerCase()
            .replace(/[^a-z0-9]+/g, '_')
            .replace(/^_+|_+$/g, '');

        nameMapping[key][normalized] = {
            officialName,
            filename,
            unitId
        };
    } catch (error) {
        console.log('❌ Error reading:', filename, error.message);
    }
});

console.log('Scanned', state.completed.length, 'completed units\n');

// Now update seed file
let updatesCount = 0;
let newAliasesCount = 0;

console.log('=== UPDATING SEED FILE ===\n');

for (const [seedKey, nationName] of Object.entries(nationMap)) {
    if (!seed[seedKey]) continue;

    const units = seed[seedKey];

    units.forEach(unit => {
        const originalDesignation = unit.designation;
        let foundOfficialName = null;
        const foundAliases = new Set();

        // Check each quarter this unit appears in
        unit.quarters.forEach(quarter => {
            const normalizedQuarter = quarter.toLowerCase().replace(/-/g, '');
            const key = `${nationName}_${normalizedQuarter}`;

            if (!nameMapping[key]) return;

            // Try to find matching unit in completed files
            const seedNormalized = originalDesignation.toLowerCase()
                .replace(/[^a-z0-9]+/g, '_')
                .replace(/^_+|_+$/g, '');

            // Look for exact match first
            if (nameMapping[key][seedNormalized]) {
                const match = nameMapping[key][seedNormalized];
                if (!foundOfficialName) {
                    foundOfficialName = match.officialName;
                }
                if (match.officialName !== originalDesignation) {
                    foundAliases.add(match.officialName);
                }
            } else {
                // Look for partial matches (fuzzy)
                for (const [normalized, data] of Object.entries(nameMapping[key])) {
                    if (normalized.includes(seedNormalized) || seedNormalized.includes(normalized)) {
                        if (!foundOfficialName) {
                            foundOfficialName = data.officialName;
                        }
                        if (data.officialName !== originalDesignation) {
                            foundAliases.add(data.officialName);
                        }
                    }
                }
            }
        });

        // Update unit if we found official name or aliases
        if (foundOfficialName && foundOfficialName !== originalDesignation) {
            console.log(`\n📝 ${seedKey} - ${originalDesignation}`);
            console.log(`   → Official: ${foundOfficialName}`);

            unit.designation_abbreviated = originalDesignation;
            unit.designation = foundOfficialName;
            updatesCount++;
        }

        if (foundAliases.size > 0) {
            // Always include original designation as an alias
            foundAliases.add(originalDesignation);

            unit.aliases = Array.from(foundAliases).sort();
            newAliasesCount++;

            console.log(`   Aliases: [${unit.aliases.join(', ')}]`);
        } else if (!unit.aliases) {
            // No variants found, but keep original as alias
            unit.aliases = [originalDesignation];
        }
    });
}

// Add metadata about update
seed.alias_system_version = "1.0.0";
seed.last_alias_update = new Date().toISOString();
seed.alias_update_notes = [
    "Added full official names as primary designations",
    "Original abbreviated names moved to designation_abbreviated field",
    "All naming variants stored in aliases array",
    `Updated ${updatesCount} units with official names`,
    `Added aliases to ${newAliasesCount} units`
];

// Save updated seed file
const backupPath = seedPath.replace('.json', '_backup_' + Date.now() + '.json');
fs.copyFileSync(seedPath, backupPath);
console.log(`\n✅ Backup created: ${backupPath}`);

fs.writeFileSync(seedPath, JSON.stringify(seed, null, 2));
console.log(`✅ Updated seed file: ${seedPath}`);

console.log(`\n=== SUMMARY ===`);
console.log(`Units updated with official names: ${updatesCount}`);
console.log(`Units with aliases added: ${newAliasesCount}`);
console.log(`Backup: ${backupPath}`);
