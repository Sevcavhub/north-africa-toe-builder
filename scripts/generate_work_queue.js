#!/usr/bin/env node

/**
 * Work Queue Generator
 *
 * Generates WORK_QUEUE.md from seed file with chronological + echelon ordering.
 * Ensures divisions are processed before corps, corps before armies (bottom-up aggregation).
 *
 * Created: October 2025
 * Purpose: Replace dynamic strategy selection with simple sequential TODO list
 */

const fs = require('fs').promises;
const path = require('path');
const naming = require('./lib/naming_standard');
const paths = require('./lib/canonical_paths');
const matching = require('./lib/matching');

// Echelon priority (smallest to largest for bottom-up aggregation)
// GROUND FORCES ECHELONS
const GROUND_ECHELON_PRIORITY = {
    'squad': 0,
    'platoon': 1,
    'company': 2,
    'battalion': 3,
    'regiment': 4,
    'brigade': 5,
    'column': 5,
    'light_division': 6,
    'panzer_division': 6,
    'armored_division': 6,
    'infantry_division': 6,
    'motorized_division': 6,
    'mountain_division': 6,
    'airborne_division': 6,
    'division': 6,
    'corps': 7,
    'army_group': 8,
    'army': 8,
    'theater': 9,
    'unknown': 99
};

// AIR FORCES ECHELONS
const AIR_ECHELON_PRIORITY = {
    // Smallest units (9-12 aircraft)
    'desert_rescue_staffel': 0,
    'long_range_recon_staffel': 0,
    'zerstoerer_staffel': 0,
    'bomber_squadriglia': 0,

    // Squadron-level units (12-18 aircraft)
    'fighter_squadron': 1,
    'bomber_squadron': 1,
    'bomber_fighter_squadron': 1,
    'fighter_bomber_squadron': 1,
    'bomber_transport_squadron': 1,
    'army_cooperation': 1,
    'photographic_reconnaissance': 1,
    'tactical_reconnaissance_antitank': 1,
    'tactical_reconnaissance_army_cooperation': 1,
    'tactical_reconnaissance_fighter': 1,
    'fighter_reconnaissance': 1,
    'reconnaissance_bomber': 1,

    // Gruppe-level units (~30 aircraft)
    'fighter_gruppe': 2,
    'stuka_gruppe': 2,
    'bomber_gruppe': 2,
    'zerstoerer_gruppe': 2,
    'fighter_gruppo': 2,
    'bomber_gruppo': 2,
    'assault_gruppo': 2,
    'long_range_fighter_ground_attack': 2,

    // Wing/Group level (RAF/USAAF formations)
    'fighter_group': 3,
    'fighter_bomber_group': 3,
    'bomber_group_light': 3,
    'bomber_group_medium': 3,
    'bomber_group_heavy': 3,

    // Geschwader/Stormo level (German/Italian large formations)
    'bomber_geschwader': 4,
    'assault_stormo': 4,
    'bomber_stormo': 4,

    // Staff and command units
    'fighter_geschwader_staff': 5,
    'stuka_geschwader_staff': 5,
    'command_staff': 5,

    // Highest command level
    'command_korps': 6,

    'unknown': 99
};

// Parse command-line arguments
function parseArgs() {
    const args = process.argv.slice(2);
    const mode = args.includes('--air-forces') ? 'air' : 'ground';
    return { mode };
}

// Map seed file type to echelon
function getEchelon(type, mode = 'ground') {
    const lower = type.toLowerCase().replace(/\s+/g, '_');
    const priorityMap = mode === 'air' ? AIR_ECHELON_PRIORITY : GROUND_ECHELON_PRIORITY;

    // Check for exact match
    if (priorityMap[lower] !== undefined) {
        return { name: lower, priority: priorityMap[lower] };
    }

    // Check for partial match
    for (const [echelon, priority] of Object.entries(priorityMap)) {
        if (lower.includes(echelon)) {
            return { name: echelon, priority };
        }
    }

    // Default to unknown
    return { name: 'unknown', priority: 99 };
}

// Parse quarter to year and quarter number for sorting
function parseQuarter(quarter) {
    const match = quarter.match(/^(\d{4})-Q(\d)$/);
    if (!match) {
        console.warn(`Invalid quarter format: ${quarter}`);
        return { year: 0, q: 0 };
    }
    return { year: parseInt(match[1]), q: parseInt(match[2]) };
}

// Sort quarters chronologically
function compareQuarters(a, b) {
    const aParsed = parseQuarter(a);
    const bParsed = parseQuarter(b);

    if (aParsed.year !== bParsed.year) {
        return aParsed.year - bParsed.year;
    }
    return aParsed.q - bParsed.q;
}

// Load completed units from WORKFLOW_STATE.json
async function loadCompletedUnits() {
    try {
        const statePath = path.join(process.cwd(), 'WORKFLOW_STATE.json');
        const data = await fs.readFile(statePath, 'utf-8');
        const state = JSON.parse(data);
        return new Set(state.completed || []);
    } catch (error) {
        console.warn('⚠️  Could not load WORKFLOW_STATE.json, assuming no units completed');
        return new Set();
    }
}

// Generate unit ID for matching with completed units
function generateUnitId(nation, quarter, designation) {
    const cleanNation = naming.normalizeNation(nation);
    const cleanQuarter = naming.normalizeQuarter(quarter);
    const cleanDesignation = naming.normalizeDesignation(designation);
    return `${cleanNation}_${cleanQuarter}_${cleanDesignation}`;
}

// Expand seed file into individual unit-quarters
function expandSeedToUnitQuarters(seedData, mode = 'ground') {
    const unitQuarters = [];

    // Process each nation
    for (const [nationKey, units] of Object.entries(seedData)) {
        if (!nationKey.endsWith('_units') || !Array.isArray(units)) {
            continue; // Skip metadata fields
        }

        const nation = naming.NATION_MAP[nationKey];
        if (!nation) {
            console.warn(`⚠️  Unknown nation key: ${nationKey}`);
            continue;
        }

        // Process each unit
        for (const unit of units) {
            const echelon = getEchelon(unit.type, mode);

            // Expand quarters
            for (const quarter of unit.quarters) {
                unitQuarters.push({
                    nation,
                    quarter,
                    designation: unit.designation,
                    aliases: unit.aliases || [],  // Include aliases for fuzzy matching
                    type: unit.type,
                    echelon: echelon.name,
                    echelonPriority: echelon.priority,
                    unitId: generateUnitId(nation, quarter, unit.designation),
                    battles: unit.battles || [],
                    confidence: unit.confidence || 0
                });
            }
        }
    }

    return unitQuarters;
}

// Sort unit-quarters by ECHELON first (bottom-up), then chronological
// CRITICAL: Divisions before corps before armies GLOBALLY (not per-quarter)
// This enforces bottom-up aggregation: all divisions complete before ANY corps
function sortUnitQuarters(unitQuarters) {
    return unitQuarters.sort((a, b) => {
        // First by echelon (smallest to largest) - GLOBAL bottom-up
        if (a.echelonPriority !== b.echelonPriority) {
            return a.echelonPriority - b.echelonPriority;
        }

        // Then by quarter (chronological) within each echelon
        const quarterCompare = compareQuarters(a.quarter, b.quarter);
        if (quarterCompare !== 0) return quarterCompare;

        // Then by nation alphabetically
        if (a.nation !== b.nation) {
            return a.nation.localeCompare(b.nation);
        }

        // Finally by designation alphabetically
        return a.designation.localeCompare(b.designation);
    });
}

// Generate markdown work queue
async function generateMarkdown(unitQuarters, completedUnits, mode = 'ground') {
    // Use fuzzy matching instead of exact ID match
    const pending = unitQuarters.filter(uq =>
        !matching.isUnitCompleted(uq.nation, uq.quarter, uq.designation, uq.aliases, completedUnits)
    );
    const completed = unitQuarters.filter(uq =>
        matching.isUnitCompleted(uq.nation, uq.quarter, uq.designation, uq.aliases, completedUnits)
    );

    const totalUnits = unitQuarters.length;
    const completedCount = completed.length;
    const pendingCount = pending.length;
    const progressPct = ((completedCount / totalUnits) * 100).toFixed(1);

    const title = mode === 'air' ? 'North Africa Air Forces Work Queue' : 'North Africa Work Queue';
    const echelonDescription = mode === 'air'
        ? 'Squadrons/Staffeln before Gruppi/Gruppen before Groups/Geschwader'
        : 'Divisions before corps before armies';
    const aggregationDescription = mode === 'air'
        ? 'ALL squadrons/staffeln complete before ANY gruppi/gruppen'
        : 'ALL divisions complete before ANY corps';

    let md = `# ${title}\n\n`;
    md += `**Generated**: ${new Date().toISOString()}\n\n`;
    md += `**Progress**: ${completedCount}/${totalUnits} units complete (${progressPct}%)\n`;
    md += `**Remaining**: ${pendingCount} units\n\n`;
    md += `---\n\n`;
    md += `## ⚙️ How This Queue Works\n\n`;
    md += `1. **Bottom-Up Echelon Order**: ${echelonDescription} (GLOBAL enforcement)\n`;
    md += `2. **Chronological Within Echelon**: Within each echelon, 1940-Q2 → 1943-Q2\n`;
    md += `3. **Bottom-Up Aggregation**: ${aggregationDescription} (strict enforcement)\n`;
    md += `4. **Session Workflow**: /kstart processes next 3 units, no artificial session limit\n`;
    md += `5. **Auto-Update**: Checkpoints mark units complete, queue regenerates as needed\n\n`;
    md += `---\n\n`;

    // Group pending units by quarter
    const byQuarter = {};
    for (const uq of pending) {
        if (!byQuarter[uq.quarter]) {
            byQuarter[uq.quarter] = [];
        }
        byQuarter[uq.quarter].push(uq);
    }

    // Sort quarters
    const quarters = Object.keys(byQuarter).sort(compareQuarters);

    // Show next 3 units prominently
    md += `## 🎯 Next Up (Next Session)\n\n`;
    const next3 = pending.slice(0, 3);
    if (next3.length > 0) {
        for (let i = 0; i < next3.length; i++) {
            const uq = next3[i];
            md += `${i + 1}. **${uq.nation.toUpperCase()}** - ${uq.quarter} - ${uq.designation} _(${uq.echelon})_\n`;
        }
    } else {
        md += `🎉 **ALL UNITS COMPLETE!**\n`;
    }
    md += `\n---\n\n`;

    // Show queue by quarter
    md += `## 📋 Full Queue (Chronological + Echelon Order)\n\n`;

    for (const quarter of quarters) {
        const units = byQuarter[quarter];
        const quarterCompleted = completed.filter(uq => uq.quarter === quarter).length;
        const quarterTotal = quarterCompleted + units.length;

        md += `### ${quarter} (${quarterCompleted}/${quarterTotal} complete)\n\n`;

        // Group by echelon within quarter
        const byEchelon = {};
        for (const uq of units) {
            if (!byEchelon[uq.echelon]) {
                byEchelon[uq.echelon] = [];
            }
            byEchelon[uq.echelon].push(uq);
        }

        // Sort echelons by priority
        const priorityMap = mode === 'air' ? AIR_ECHELON_PRIORITY : GROUND_ECHELON_PRIORITY;
        const echelons = Object.keys(byEchelon).sort((a, b) => {
            const aPriority = priorityMap[a] || 99;
            const bPriority = priorityMap[b] || 99;
            return aPriority - bPriority;
        });

        for (const echelon of echelons) {
            const echelonUnits = byEchelon[echelon];
            md += `**${echelon.toUpperCase()}** (${echelonUnits.length} remaining):\n`;

            for (const uq of echelonUnits) {
                md += `- [ ] ${uq.nation.toUpperCase()} - ${uq.designation}\n`;
            }
            md += `\n`;
        }
    }

    // Add completed units summary
    md += `---\n\n`;
    md += `## ✅ Completed (${completedCount} units)\n\n`;
    md += `<details>\n<summary>Show completed units</summary>\n\n`;

    // Group completed by quarter
    const completedByQuarter = {};
    for (const uq of completed) {
        if (!completedByQuarter[uq.quarter]) {
            completedByQuarter[uq.quarter] = [];
        }
        completedByQuarter[uq.quarter].push(uq);
    }

    const completedQuarters = Object.keys(completedByQuarter).sort(compareQuarters);
    for (const quarter of completedQuarters) {
        const units = completedByQuarter[quarter];
        md += `### ${quarter} (${units.length} complete)\n\n`;

        for (const uq of units) {
            md += `- [x] ${uq.nation.toUpperCase()} - ${uq.designation} _(${uq.echelon})_\n`;
        }
        md += `\n`;
    }

    md += `</details>\n\n`;

    return md;
}

async function main() {
    // Parse command-line arguments
    const { mode } = parseArgs();
    const isAirMode = mode === 'air';

    console.log(`🔄 Generating ${isAirMode ? 'AIR FORCES' : 'GROUND FORCES'} work queue from seed file...\n`);

    // Select appropriate seed file
    const seedFileName = isAirMode
        ? 'north_africa_air_units_seed_COMPLETE.json'
        : 'north_africa_seed_units_COMPLETE.json';
    const seedPath = path.join(process.cwd(), 'projects', seedFileName);
    const seedData = JSON.parse(await fs.readFile(seedPath, 'utf-8'));

    console.log(`✅ Loaded seed file: ${seedData.total_units} unique units, ${seedData.total_unit_quarters} unit-quarters\n`);

    // Load completed units
    const completedUnits = await loadCompletedUnits();
    console.log(`✅ Loaded ${completedUnits.size} completed units from WORKFLOW_STATE.json\n`);

    // Expand seed to unit-quarters
    const unitQuarters = expandSeedToUnitQuarters(seedData, mode);
    console.log(`✅ Expanded to ${unitQuarters.length} unit-quarters\n`);

    // Sort by chronological + echelon order
    const sorted = sortUnitQuarters(unitQuarters);
    console.log(`✅ Sorted by ${isAirMode ? 'echelon-first' : 'chronological + echelon'} order (smallest → largest)\n`);

    // Generate markdown
    const markdown = await generateMarkdown(sorted, completedUnits, mode);

    // Write to appropriate output file
    const outputFileName = isAirMode ? 'WORK_QUEUE_AIR.md' : 'WORK_QUEUE.md';
    const queuePath = path.join(process.cwd(), outputFileName);
    await fs.writeFile(queuePath, markdown);

    console.log(`✅ Work queue generated: ${outputFileName}\n`);

    // Show summary (use fuzzy matching like generateMarkdown)
    const pending = sorted.filter(uq =>
        !matching.isUnitCompleted(uq.nation, uq.quarter, uq.designation, uq.aliases, completedUnits)
    );
    const next3 = pending.slice(0, 3);

    console.log('🎯 Next 3 units to process:\n');
    for (let i = 0; i < next3.length; i++) {
        const uq = next3[i];
        console.log(`   ${i + 1}. ${uq.nation.toUpperCase()} - ${uq.quarter} - ${uq.designation} (${uq.echelon})`);
    }
    console.log('');

    const completedCount = completedUnits.size;
    const totalCount = unitQuarters.length;
    const progressPct = ((completedCount / totalCount) * 100).toFixed(1);
    console.log(`📊 Overall Progress: ${completedCount}/${totalCount} (${progressPct}%)\n`);
}

// Run if called directly
if (require.main === module) {
    main().catch(error => {
        console.error('❌ Error generating work queue:', error);
        process.exit(1);
    });
}

module.exports = {
    expandSeedToUnitQuarters,
    sortUnitQuarters,
    generateMarkdown,
    getEchelon,
    parseArgs,
    GROUND_ECHELON_PRIORITY,
    AIR_ECHELON_PRIORITY,
    // Backward compatibility
    ECHELON_PRIORITY: GROUND_ECHELON_PRIORITY
};
