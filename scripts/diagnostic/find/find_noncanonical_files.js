#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');
const naming = require('./lib/naming_standard');

async function main() {
    const unitsDir = path.join(process.cwd(), 'data', 'output', 'units');
    const files = (await fs.readdir(unitsDir)).filter(f => f.endsWith('_toe.json'));

    console.log(`Checking ${files.length} files for canonical naming...\n`);

    const nonCanonical = [];

    for (const filename of files) {
        // Parse the filename
        const parsed = naming.parseFilename(filename);
        if (!parsed) {
            nonCanonical.push({ filename, issue: 'Cannot parse' });
            continue;
        }

        // Generate what the canonical filename SHOULD be
        const canonical = naming.generateFilename(
            parsed.nation,
            parsed.quarter,
            parsed.designation
        );

        // Check if it matches
        if (filename !== canonical) {
            // Check if canonical version exists
            const canonicalPath = path.join(unitsDir, canonical);
            let canonicalExists = false;
            try {
                await fs.access(canonicalPath);
                canonicalExists = true;
            } catch (err) {
                // Doesn't exist
            }

            nonCanonical.push({
                filename,
                canonical,
                canonicalExists,
                issue: canonicalExists ? 'Duplicate (canonical exists)' : 'Wrong naming'
            });
        }
    }

    if (nonCanonical.length === 0) {
        console.log('✅ All files use canonical naming!\n');
        return;
    }

    console.log(`⚠️  Found ${nonCanonical.length} files with non-canonical naming:\n`);

    // Group by issue type
    const duplicates = nonCanonical.filter(f => f.issue === 'Duplicate (canonical exists)');
    const wrongNaming = nonCanonical.filter(f => f.issue === 'Wrong naming');
    const unparseable = nonCanonical.filter(f => f.issue === 'Cannot parse');

    if (duplicates.length > 0) {
        console.log(`❌ DUPLICATES (canonical version exists) - ${duplicates.length}:\n`);
        for (const f of duplicates) {
            console.log(`   ${f.filename}`);
            console.log(`   → Canonical exists: ${f.canonical}\n`);
        }
    }

    if (wrongNaming.length > 0) {
        console.log(`🔧 WRONG NAMING (should be renamed) - ${wrongNaming.length}:\n`);
        for (const f of wrongNaming) {
            console.log(`   ${f.filename}`);
            console.log(`   → Should be: ${f.canonical}\n`);
        }
    }

    if (unparseable.length > 0) {
        console.log(`⚠️  UNPARSEABLE - ${unparseable.length}:\n`);
        for (const f of unparseable) {
            console.log(`   ${f.filename}\n`);
        }
    }

    console.log(`\n📊 Summary:`);
    console.log(`   Total files: ${files.length}`);
    console.log(`   Canonical: ${files.length - nonCanonical.length}`);
    console.log(`   Non-canonical: ${nonCanonical.length}`);
    console.log(`     - Duplicates: ${duplicates.length}`);
    console.log(`     - Wrong naming: ${wrongNaming.length}`);
    console.log(`     - Unparseable: ${unparseable.length}\n`);
}

main().catch(console.error);
