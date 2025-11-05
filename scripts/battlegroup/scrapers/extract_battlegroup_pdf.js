#!/usr/bin/env node

/**
 * Extract full text from Battlegroup Rules PDF
 *
 * This script extracts all text from the Battlegroup Rules PDF for analysis
 * to enable scenario generation from our historical TO&E data.
 */

const fs = require('fs');
const path = require('path');

async function extractBattlegroupRules() {
    console.log('Starting Battlegroup Rules PDF extraction...\n');

    // Require pdf2json (will install if needed)
    let PDFParser;
    try {
        PDFParser = require('pdf2json');
    } catch (err) {
        console.log('pdf2json not found. Installing...');
        const { execSync } = require('child_process');
        execSync('npm install pdf2json', { stdio: 'inherit' });
        PDFParser = require('pdf2json');
    }

    const pdfPath = path.join(__dirname, '..', 'Resource Documents', 'Battlegroup Game', 'Battlegroup Rules.pdf');
    const outputPath = path.join(__dirname, '..', 'sources', 'battlegroup_rules_extracted.txt');
    const jsonOutputPath = path.join(__dirname, '..', 'sources', 'battlegroup_rules_analysis.json');

    console.log(`Reading PDF from: ${pdfPath}`);
    console.log(`Output will be saved to: ${outputPath}\n`);

    return new Promise((resolve, reject) => {
        const pdfParser = new PDFParser();

        // Set up event handlers
        pdfParser.on('pdfParser_dataError', errData => {
            console.error('Error parsing PDF:', errData.parserError);
            reject(errData.parserError);
        });

        pdfParser.on('pdfParser_dataReady', pdfData => {
            try {
                console.log('Parsing PDF...');

                // Extract text from all pages
                let fullText = '';
                let pageCount = 0;

                if (pdfData.Pages) {
                    pageCount = pdfData.Pages.length;
                    pdfData.Pages.forEach((page, pageIndex) => {
                        if (page.Texts) {
                            page.Texts.forEach(text => {
                                if (text.R) {
                                    text.R.forEach(run => {
                                        if (run.T) {
                                            // Decode URI-encoded text (with error handling for malformed strings)
                                            try {
                                                fullText += decodeURIComponent(run.T) + ' ';
                                            } catch (e) {
                                                // If decode fails, use raw text
                                                fullText += run.T + ' ';
                                            }
                                        }
                                    });
                                }
                            });
                            fullText += '\n\n'; // Page break
                        }
                    });
                }

                // Extract metadata
                const metadata = {
                    title: pdfData.Meta?.Title || 'Battlegroup Rules',
                    pages: pageCount,
                    extractedAt: new Date().toISOString(),
                    fileSize: fs.statSync(pdfPath).size,
                    text_length: fullText.length
                };

                console.log(`\nExtraction complete!`);
                console.log(`- Total pages: ${metadata.pages}`);
                console.log(`- Text length: ${metadata.text_length.toLocaleString()} characters`);
                console.log(`- File size: ${(metadata.fileSize / 1024 / 1024).toFixed(2)} MB\n`);

                // Save full text
                fs.writeFileSync(outputPath, fullText, 'utf8');
                console.log(`✓ Full text saved to: ${outputPath}`);

                // Save metadata and structured analysis
                const analysisData = {
                    metadata,
                    sections: identifySections(fullText),
                    keywords: extractKeywords(fullText)
                };

                fs.writeFileSync(jsonOutputPath, JSON.stringify(analysisData, null, 2), 'utf8');
                console.log(`✓ Analysis data saved to: ${jsonOutputPath}\n`);

                // Print initial analysis
                console.log('=== INITIAL ANALYSIS ===\n');
                console.log('Key sections identified:');
                analysisData.sections.forEach(section => {
                    console.log(`  - ${section.name} (page ~${section.estimatedPage})`);
                });

                console.log('\nKey game mechanics keywords found:');
                analysisData.keywords.mechanics.slice(0, 10).forEach(kw => {
                    console.log(`  - ${kw.word} (${kw.count} mentions)`);
                });

                resolve(analysisData);

            } catch (error) {
                console.error('Error processing PDF data:', error);
                reject(error);
            }
        });

        // Load PDF
        pdfParser.loadPDF(pdfPath);
    });
}

/**
 * Identify major sections in the rules
 */
function identifySections(text) {
    const sections = [];
    const lines = text.split('\n');

    // Look for major headings (usually all caps or numbered)
    const sectionPatterns = [
        /^(\d+\.?\s+)?([A-Z][A-Z\s]{10,})$/,  // All caps headings
        /^CHAPTER\s+\d+/i,
        /^PART\s+\d+/i,
        /^SECTION\s+\d+/i,
        /^SCENARIO/i,
        /^ARMY\s+LIST/i,
        /^VEHICLE\s+DATA/i,
        /^WEAPON\s+DATA/i,
        /^UNIT\s+STATS/i
    ];

    lines.forEach((line, index) => {
        const trimmed = line.trim();
        if (trimmed.length > 5 && trimmed.length < 100) {
            for (const pattern of sectionPatterns) {
                if (pattern.test(trimmed)) {
                    sections.push({
                        name: trimmed,
                        lineNumber: index,
                        estimatedPage: Math.floor(index / 50) + 1
                    });
                    break;
                }
            }
        }
    });

    return sections;
}

/**
 * Extract key game mechanics keywords
 */
function extractKeywords(text) {
    const mechanicsKeywords = [
        'morale', 'battle rating', 'br', 'command', 'orders',
        'infantry', 'tank', 'vehicle', 'artillery', 'gun',
        'armour', 'armor', 'penetration', 'weapon', 'crew',
        'unit', 'squad', 'section', 'platoon', 'company',
        'scenario', 'objective', 'victory', 'points',
        'movement', 'combat', 'shooting', 'assault', 'close combat',
        'suppression', 'pin', 'hit', 'damage', 'destroy'
    ];

    const statsKeywords = [
        'attack', 'defense', 'range', 'rate of fire', 'rof',
        'armour value', 'av', 'damage value', 'dv',
        'skill', 'quality', 'veteran', 'regular', 'green',
        'points cost', 'cost', 'value'
    ];

    const mechanics = countKeywords(text, mechanicsKeywords);
    const stats = countKeywords(text, statsKeywords);

    return {
        mechanics: mechanics.sort((a, b) => b.count - a.count),
        stats: stats.sort((a, b) => b.count - a.count)
    };
}

function countKeywords(text, keywords) {
    const lowerText = text.toLowerCase();
    return keywords.map(word => {
        const regex = new RegExp(`\\b${word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
        const matches = lowerText.match(regex);
        return {
            word,
            count: matches ? matches.length : 0
        };
    }).filter(kw => kw.count > 0);
}

// Run extraction
if (require.main === module) {
    extractBattlegroupRules()
        .then(() => {
            console.log('\n✓ Extraction complete! Ready for detailed analysis.');
            process.exit(0);
        })
        .catch(err => {
            console.error('\n✗ Extraction failed:', err.message);
            process.exit(1);
        });
}

module.exports = { extractBattlegroupRules };
