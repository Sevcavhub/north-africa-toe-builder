#!/usr/bin/env node

/**
 * Backfill Database - Populate SQLite with missing units
 *
 * Safely reads existing JSON files and inserts missing units into database.
 * Does NOT modify any workflow scripts or state files.
 *
 * Usage: node scripts/backfill_database.js
 */

const fs = require('fs').promises;
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..');
const DATABASE_PATH = path.join(PROJECT_ROOT, 'database/master_database.db');

async function main() {
    console.log('\n' + '═'.repeat(80));
    console.log('  📊 DATABASE BACKFILL - Populating Missing Units');
    console.log('═'.repeat(80));
    console.log('');

    // Step 1: Load WORKFLOW_STATE.json to see what should be in database
    console.log('📋 Loading workflow state...');
    const statePath = path.join(PROJECT_ROOT, 'WORKFLOW_STATE.json');
    const state = JSON.parse(await fs.readFile(statePath, 'utf-8'));
    console.log(`   Found ${state.completed.length} completed units in WORKFLOW_STATE.json\n`);

    // Step 2: Scan for all JSON files
    console.log('🔍 Scanning for unit JSON files...');
    const unitFiles = await scanForUnitFiles();
    console.log(`   Found ${unitFiles.length} unit JSON files\n`);

    // Step 3: Read each JSON file and prepare for database
    console.log('📦 Loading unit data from JSON files...');
    const units = [];
    let loadErrors = 0;

    for (const filePath of unitFiles) {
        try {
            const jsonData = await fs.readFile(filePath, 'utf-8');
            const unit = JSON.parse(jsonData);

            // Extract key fields for database
            const dbRecord = extractDatabaseFields(unit, filePath);
            if (dbRecord) {
                units.push(dbRecord);
            }
        } catch (error) {
            console.log(`   ⚠️  Failed to load ${path.basename(filePath)}: ${error.message}`);
            loadErrors++;
        }
    }

    console.log(`   Loaded ${units.length} units successfully`);
    if (loadErrors > 0) {
        console.log(`   ⚠️  ${loadErrors} files could not be loaded\n`);
    } else {
        console.log('');
    }

    // Step 4: Display what will be inserted
    console.log('═'.repeat(80));
    console.log('  UNITS TO INSERT');
    console.log('═'.repeat(80));
    console.log('');

    const byNation = {};
    for (const unit of units) {
        const nation = unit.nation || 'unknown';
        if (!byNation[nation]) byNation[nation] = [];
        byNation[nation].push(unit);
    }

    for (const [nation, nationUnits] of Object.entries(byNation).sort()) {
        console.log(`${nation}: ${nationUnits.length} units`);
    }

    console.log('');
    console.log(`Total units to process: ${units.length}`);
    console.log('');

    // Step 5: Generate SQL INSERT statements
    console.log('═'.repeat(80));
    console.log('  SQL INSERT STATEMENTS (Copy to SQLite MCP)');
    console.log('═'.repeat(80));
    console.log('');
    console.log('-- Note: Use SQLite MCP write_query tool to execute these');
    console.log('');

    for (let i = 0; i < units.length; i++) {
        const unit = units[i];
        const sql = generateInsertSQL(unit);
        console.log(`-- Unit ${i + 1}/${units.length}: ${unit.nation} ${unit.unit_designation} (${unit.quarter})`);
        console.log(sql);
        console.log('');
    }

    console.log('═'.repeat(80));
    console.log('  BACKFILL COMPLETE');
    console.log('═'.repeat(80));
    console.log('');
    console.log('📌 NEXT STEPS:');
    console.log('   1. Copy the SQL INSERT statements above');
    console.log('   2. Use Claude Code with SQLite MCP to execute them');
    console.log('   3. Or run: node scripts/backfill_database_execute.js');
    console.log('');
    console.log(`💾 Database location: ${DATABASE_PATH}`);
    console.log('');

    // Save SQL to file for easy execution
    const sqlFilePath = path.join(PROJECT_ROOT, 'data/backfill_inserts.sql');
    let sqlContent = '-- Database Backfill SQL\n';
    sqlContent += `-- Generated: ${new Date().toISOString()}\n`;
    sqlContent += `-- Units to insert: ${units.length}\n\n`;

    for (let i = 0; i < units.length; i++) {
        const unit = units[i];
        sqlContent += `-- Unit ${i + 1}: ${unit.nation} ${unit.unit_designation} (${unit.quarter})\n`;
        sqlContent += generateInsertSQL(unit) + '\n\n';
    }

    await fs.writeFile(sqlFilePath, sqlContent);
    console.log(`📄 SQL statements saved to: ${sqlFilePath}`);
    console.log('');
}

/**
 * Scan canonical Architecture v4.0 directories for unit JSON files
 * - Ground units: data/output/units/
 * - Air summaries: data/output/air_summaries/
 */
async function scanForUnitFiles() {
    const files = [];

    // Scan ground units (Architecture v4.0 canonical location)
    const unitsDir = path.join(PROJECT_ROOT, 'data/output/units');
    try {
        const unitFiles = await fs.readdir(unitsDir);
        for (const file of unitFiles) {
            if (file.endsWith('_toe.json')) {
                files.push(path.join(unitsDir, file));
            }
        }
        console.log(`   Found ${files.length} ground unit files`);
    } catch (error) {
        console.error(`❌ Error scanning units directory: ${error.message}`);
    }

    // Scan air summaries (Architecture v4.0 canonical location)
    const airSummariesDir = path.join(PROJECT_ROOT, 'data/output/air_summaries');
    try {
        const airFiles = await fs.readdir(airSummariesDir);
        const airCount = files.length;
        for (const file of airFiles) {
            if (file.endsWith('.json')) {
                files.push(path.join(airSummariesDir, file));
            }
        }
        console.log(`   Found ${files.length - airCount} air summary files`);
    } catch (error) {
        console.error(`❌ Error scanning air summaries directory: ${error.message}`);
    }

    return files;
}

/**
 * Extract relevant fields from unit JSON for database insertion
 */
function extractDatabaseFields(unit, filePath) {
    if (!unit) return null;

    // Standardize nation name
    let nation = unit.nation || 'unknown';
    nation = standardizeNationName(nation);

    // Calculate tank subtotals
    const tanksHeavy = unit.tanks?.heavy_tanks?.total || 0;
    const tanksMedium = unit.tanks?.medium_tanks?.total || 0;
    const tanksLight = unit.tanks?.light_tanks?.total || 0;

    // Get primary source (first one from validation.source array)
    let primarySource = 'Unknown';
    if (unit.validation?.source && Array.isArray(unit.validation.source) && unit.validation.source.length > 0) {
        primarySource = unit.validation.source[0];
    }

    // Determine source tier from validation data
    let sourceTier = 3; // Default to Tier 3
    if (primarySource.toLowerCase().includes('local json') || primarySource.toLowerCase().includes('tessin')) {
        sourceTier = 1;
    } else if (primarySource.toLowerCase().includes('feldgrau') || primarySource.toLowerCase().includes('niehorster')) {
        sourceTier = 2;
    }

    // Generate unit_id from components
    const unitId = `${nation}_${unit.quarter}_${(unit.unit_designation || 'unknown').toLowerCase().replace(/[^a-z0-9]+/g, '_')}`;

    return {
        unit_id: unitId,
        nation: nation,
        quarter: unit.quarter || 'unknown',
        designation: unit.unit_designation || 'Unknown Unit',
        unit_type: unit.unit_type || null,
        organization_level: unit.organization_level || null,
        commander_name: unit.command?.commander?.name || null,
        commander_rank: unit.command?.commander?.rank || null,
        total_personnel: unit.total_personnel || 0,
        officers: unit.officers || 0,
        ncos: unit.ncos || 0,
        enlisted: unit.enlisted || 0,
        source_file: path.basename(filePath),
        schema_version: unit.schema_version || 'unknown',
        theater: 'north_africa'
    };
}

/**
 * Standardize nation names (fix Germany vs german inconsistency)
 */
function standardizeNationName(nation) {
    const mapping = {
        'germany': 'german',
        'Germany': 'german',
        'britain': 'british',
        'Britain': 'british',
        'italy': 'italian',
        'Italy': 'italian',
        'france': 'french',
        'France': 'french',
        'usa': 'american',
        'USA': 'american',
        'america': 'american',
        'America': 'american',
        'india': 'british',  // India is Commonwealth = British
        'India': 'british',
        'newzealand': 'british',
        'NewZealand': 'british',
        'australia': 'british',
        'Australia': 'british'
    };

    return mapping[nation] || nation.toLowerCase();
}

/**
 * Generate SQL INSERT statement for a unit
 */
function generateInsertSQL(unit) {
    const escape = (str) => {
        if (str === null || str === undefined) return 'NULL';
        if (typeof str === 'number') return str;
        return `'${String(str).replace(/'/g, "''")}'`;
    };

    return `INSERT INTO units (
    unit_id, nation, quarter, designation, unit_type, organization_level,
    commander_name, commander_rank,
    total_personnel, officers, ncos, enlisted,
    source_file, schema_version, theater
) VALUES (
    ${escape(unit.unit_id)}, ${escape(unit.nation)}, ${escape(unit.quarter)},
    ${escape(unit.designation)}, ${escape(unit.unit_type)}, ${escape(unit.organization_level)},
    ${escape(unit.commander_name)}, ${escape(unit.commander_rank)},
    ${unit.total_personnel}, ${unit.officers}, ${unit.ncos}, ${unit.enlisted},
    ${escape(unit.source_file)}, ${escape(unit.schema_version)}, ${escape(unit.theater)}
);`;
}

// Run
main().catch(error => {
    console.error('❌ Backfill failed:', error.message);
    console.error(error.stack);
    process.exit(1);
});
