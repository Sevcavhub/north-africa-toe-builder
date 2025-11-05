/**
 * Phase 5.5 - Phase 2: Import Name Variants to Database
 * Bulk imports equipment name variants from CSV to equipment_name_variants_new table
 */

const Database = require('better-sqlite3');
const fs = require('fs');
const path = require('path');

// Configuration
const DB_PATH = path.join(__dirname, '..', 'database', 'master_database.db');
const CSV_PATH = path.join(__dirname, '..', 'database', 'data', 'equipment_name_variants.csv');

console.log('=' .repeat(80));
console.log('Phase 5.5 - Phase 2: Import Name Variants');
console.log('=' .repeat(80));

// Connect to database
console.log('\nConnecting to database...');
const db = new Database(DB_PATH);
db.pragma('foreign_keys = ON');

// Read CSV file
console.log('Reading CSV file...');
const csvContent = fs.readFileSync(CSV_PATH, 'utf-8');
const lines = csvContent.split('\n').filter(line => line.trim());

console.log(`  Loaded: ${lines.length - 1} variant rows (excluding header)`);

// Parse CSV
console.log('\nParsing CSV data...');
const variants = [];
let parseErrors = 0;

for (let i = 1; i < lines.length; i++) {  // Skip header
    const line = lines[i];

    // Parse CSV (handle quoted fields) - simplified regex
    // Format: master_id,"variant_name",confidence_score,timestamp
    const parts = line.split(',');
    if (parts.length < 4) {
        parseErrors++;
        continue;
    }

    const master_id = parseInt(parts[0], 10);
    const variant_name = parts[1].replace(/^"|"$/g, '');  // Remove quotes
    const confidence_score = parseInt(parts[2], 10);

    // Map confidence score to variant_source and is_official
    let variant_source;
    let is_official;
    if (confidence_score === 100) {
        variant_source = 'programmatic';
        is_official = 0;  // Could be original name, but mark as non-official
    } else if (confidence_score >= 90) {
        variant_source = 'jane';  // Official German names
        is_official = 1;
    } else if (confidence_score >= 85) {
        variant_source = 'programmatic';  // American M-series, British Mark
        is_official = 0;
    } else {
        variant_source = 'programmatic';  // Generic programmatic
        is_official = 0;
    }

    variants.push({
        master_id,
        variant_name: variant_name.trim(),
        variant_source,
        is_official,
    });
}

console.log(`  Parsed: ${variants.length} variants`);
console.log(`  Errors: ${parseErrors}`);

// Validate master_ids exist
console.log('\nValidating master_ids...');
const validMasterIds = new Set();
const masterIdRows = db.prepare('SELECT master_id FROM equipment_master_new').all();
masterIdRows.forEach(row => validMasterIds.add(row.master_id));

console.log(`  Valid master_ids: ${validMasterIds.size}`);

let invalidCount = 0;
const validVariants = variants.filter(v => {
    if (validMasterIds.has(v.master_id)) {
        return true;
    } else {
        invalidCount++;
        return false;
    }
});

if (invalidCount > 0) {
    console.log(`  Warning: ${invalidCount} variants with invalid master_id (will skip)`);
}

console.log(`  Valid variants: ${validVariants.length}`);

// Begin transaction
console.log('\nImporting variants to database...');
const transaction = db.transaction(() => {
    // Clear existing variants (if any)
    const deleteStmt = db.prepare('DELETE FROM equipment_name_variants_new');
    const deleted = deleteStmt.run();
    console.log(`  Cleared: ${deleted.changes} existing variants`);

    // Insert new variants
    const insertStmt = db.prepare(`
        INSERT INTO equipment_name_variants_new (
            master_id,
            variant_name,
            variant_source,
            is_official
        ) VALUES (?, ?, ?, ?)
    `);

    let inserted = 0;
    let duplicates = 0;

    for (const variant of validVariants) {
        try {
            insertStmt.run(
                variant.master_id,
                variant.variant_name,
                variant.variant_source,
                variant.is_official
            );
            inserted++;
        } catch (err) {
            if (err.message.includes('UNIQUE constraint')) {
                duplicates++;
            } else {
                console.log(`  Error inserting variant: ${variant.variant_name} - ${err.message}`);
            }
        }
    }

    console.log(`  Inserted: ${inserted} variants`);
    console.log(`  Duplicates skipped: ${duplicates}`);
});

// Execute transaction
transaction();

// Validation
console.log('\nValidation...');
const counts = db.prepare(`
    SELECT
        COUNT(*) as total_variants,
        COUNT(DISTINCT master_id) as equipment_with_variants,
        SUM(is_official) as official_count
    FROM equipment_name_variants_new
`).get();

console.log(`  Total variants: ${counts.total_variants}`);
console.log(`  Equipment with variants: ${counts.equipment_with_variants}`);
console.log(`  Official variants: ${counts.official_count}`);

// Log to normalization_audit_new
console.log('\nLogging to normalization_audit_new...');
const auditStmt = db.prepare(`
    INSERT INTO normalization_audit_new (
        phase,
        operation,
        table_name,
        record_id,
        before_count,
        after_count,
        reason,
        notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
`);

// Log one master audit entry
const auditEntry = auditStmt.run(
    'Phase 5.5 Phase 2',
    'INSERT',
    'equipment_name_variants_new',
    null,
    0,  // before_count
    counts.total_variants,  // after_count
    'Name variant generation via programmatic rules',
    `Generated 2,986 total variants, deduplicated to ${counts.total_variants} unique variants covering ${counts.equipment_with_variants} equipment items. ${counts.official_count} official variants from Jane's book.`
);

console.log(`  Audit entry logged: ${auditEntry.changes} row`);

// Summary
console.log('\n' + '='.repeat(80));
console.log('IMPORT SUMMARY');
console.log('='.repeat(80));
console.log(`CSV rows parsed:          ${variants.length}`);
console.log(`Valid variants:           ${validVariants.length}`);
console.log(`Variants imported:        ${counts.total_variants}`);
console.log(`Equipment with variants:  ${counts.equipment_with_variants}`);
console.log(`Official variants:        ${counts.official_count}`);

// Validation checks
const validationPassed = (
    counts.total_variants >= 2000 &&
    counts.equipment_with_variants >= 1000
);

if (validationPassed) {
    console.log('\n[SUCCESS] All validation checks PASSED');
} else {
    console.log('\n[WARNING] Some validation checks FAILED');

    if (counts.total_variants < 2000) {
        console.log(`  - Total variants: ${counts.total_variants} < 2000 (EXPECTED >= 2000)`);
    }
    if (counts.equipment_with_variants < 1000) {
        console.log(`  - Equipment coverage: ${counts.equipment_with_variants} < 1000 (EXPECTED >= 1000)`);
    }
}

db.close();
console.log('\n[COMPLETE] Import finished');
