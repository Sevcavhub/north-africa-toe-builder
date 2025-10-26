#!/usr/bin/env node

/**
 * Wikipedia Source Validator
 *
 * Scans all unit JSON files for Wikipedia sources and reports violations
 * CRITICAL: Wikipedia sources are FORBIDDEN per project requirements
 *
 * Usage: node scripts/validate_no_wikipedia.js [--fix]
 *
 * Options:
 *   --fix: Flag units with Wikipedia sources for re-extraction
 */

const fs = require('fs').promises;
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..');
const UNITS_DIR = path.join(PROJECT_ROOT, 'data/output/units');
const REPORT_PATH = path.join(PROJECT_ROOT, 'data/output/qa_reports/wikipedia_violations.json');

const WIKIPEDIA_PATTERNS = [
    /wikipedia\.org/i,
    /wikipedia\.com/i,
    /de\.wikipedia/i,
    /en\.wikipedia/i,
    /it\.wikipedia/i,
    /fr\.wikipedia/i,
    /wikia\.com/i,
    /fandom\.com/i,
    /\bwiki\b.*source/i,
    /Wikipedia:/i,
    /Wikipedia -/i,
    /Wikipedia\s+\(/i
];

async function scanUnitFile(filePath) {
    try {
        const content = await fs.readFile(filePath, 'utf-8');
        const data = JSON.parse(content);

        const violations = [];

        // Check sources array
        if (data.sources && Array.isArray(data.sources)) {
            for (let i = 0; i < data.sources.length; i++) {
                const source = data.sources[i];
                const sourceStr = typeof source === 'string' ? source : JSON.stringify(source);

                for (const pattern of WIKIPEDIA_PATTERNS) {
                    if (pattern.test(sourceStr)) {
                        violations.push({
                            location: `sources[${i}]`,
                            source: sourceStr.substring(0, 200),
                            pattern: pattern.toString()
                        });
                        break; // Only report once per source
                    }
                }
            }
        }

        // Check data_quality_notes field (sometimes Wikipedia mentioned there)
        if (data.data_quality_notes && typeof data.data_quality_notes === 'string') {
            for (const pattern of WIKIPEDIA_PATTERNS) {
                if (pattern.test(data.data_quality_notes)) {
                    // Only flag if it's actually USING Wikipedia, not mentioning "no Wikipedia"
                    if (!data.data_quality_notes.toLowerCase().includes('no wikipedia used')) {
                        violations.push({
                            location: 'data_quality_notes',
                            source: data.data_quality_notes.substring(0, 200),
                            pattern: pattern.toString()
                        });
                        break;
                    }
                }
            }
        }

        // Recursively check all string fields in the object
        function checkObject(obj, path = []) {
            if (!obj || typeof obj !== 'object') return;

            for (const [key, value] of Object.entries(obj)) {
                const currentPath = [...path, key];

                if (typeof value === 'string') {
                    // Skip if it's saying "no Wikipedia" or "non-Wikipedia"
                    const lowerValue = value.toLowerCase();
                    if (lowerValue.includes('no wikipedia') ||
                        lowerValue.includes('non-wikipedia') ||
                        lowerValue.includes('without wikipedia')) {
                        continue;
                    }

                    for (const pattern of WIKIPEDIA_PATTERNS) {
                        if (pattern.test(value)) {
                            violations.push({
                                location: currentPath.join('.'),
                                source: value.substring(0, 200),
                                pattern: pattern.toString()
                            });
                            break;
                        }
                    }
                } else if (Array.isArray(value)) {
                    value.forEach((item, idx) => {
                        checkObject(item, [...currentPath, idx]);
                    });
                } else if (typeof value === 'object') {
                    checkObject(value, currentPath);
                }
            }
        }

        // Check remaining fields
        const fieldsToSkip = ['sources', 'data_quality_notes'];
        const remainingData = {...data};
        fieldsToSkip.forEach(field => delete remainingData[field]);
        checkObject(remainingData);

        return {
            file: path.basename(filePath),
            violations: violations,
            hasWikipedia: violations.length > 0
        };

    } catch (error) {
        return {
            file: path.basename(filePath),
            error: error.message,
            hasWikipedia: false
        };
    }
}

async function main() {
    const args = process.argv.slice(2);
    const fixMode = args.includes('--fix');

    console.log('\n🔍 Wikipedia Source Validator\n');
    console.log('═'.repeat(80));
    console.log('');

    // Get all unit files
    const files = await fs.readdir(UNITS_DIR);
    const unitFiles = files.filter(f => f.endsWith('_toe.json') && !f.includes('.backup'));

    console.log(`Scanning ${unitFiles.length} unit files for Wikipedia sources...\n`);

    const results = [];
    let violationCount = 0;

    for (const file of unitFiles) {
        const filePath = path.join(UNITS_DIR, file);
        const result = await scanUnitFile(filePath);

        if (result.hasWikipedia) {
            violationCount++;
            results.push(result);
            console.log(`❌ ${file}`);
            result.violations.forEach(v => {
                console.log(`   Location: ${v.location}`);
                console.log(`   Source: ${v.source.substring(0, 100)}...`);
                console.log('');
            });
        }
    }

    console.log('═'.repeat(80));
    console.log('');
    console.log(`📊 Results:`);
    console.log(`   Total files scanned: ${unitFiles.length}`);
    console.log(`   Files with Wikipedia: ${violationCount}`);
    console.log(`   Clean files: ${unitFiles.length - violationCount}`);
    console.log('');

    if (violationCount > 0) {
        console.log(`⚠️  POLICY VIOLATION: ${violationCount} units contain Wikipedia sources`);
        console.log('');
        console.log('Wikipedia sources are FORBIDDEN per project requirements.');
        console.log('These units should be re-extracted using Tier 1/2 sources only.');
        console.log('');

        // Write detailed report
        const report = {
            scan_date: new Date().toISOString(),
            total_files: unitFiles.length,
            violations: violationCount,
            clean: unitFiles.length - violationCount,
            violation_details: results,
            recommended_action: 'Re-extract units with Wikipedia sources using Tier 1/2 sources only'
        };

        await fs.writeFile(REPORT_PATH, JSON.stringify(report, null, 2));
        console.log(`📝 Detailed report: ${REPORT_PATH}`);
        console.log('');

        if (fixMode) {
            console.log('🔧 Fix mode: Creating re-extraction queue...');

            const reExtractionQueue = results.map(r => r.file.replace('_toe.json', ''));
            const queuePath = path.join(PROJECT_ROOT, 'WIKIPEDIA_REEXTRACTION_QUEUE.txt');
            await fs.writeFile(queuePath, reExtractionQueue.join('\n'));

            console.log(`   ✅ Queue created: WIKIPEDIA_REEXTRACTION_QUEUE.txt`);
            console.log(`   ${reExtractionQueue.length} units flagged for re-extraction`);
            console.log('');
        }

        process.exit(1); // Non-zero exit for CI/CD failure
    } else {
        console.log('✅ All units are Wikipedia-free!');
        console.log('');
        process.exit(0);
    }
}

main().catch(error => {
    console.error('❌ Error:', error);
    process.exit(1);
});
