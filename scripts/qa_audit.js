const fs = require('fs');
const path = require('path');

// Find all unit JSON files
function findUnitFiles(dir) {
    const files = [];

    function walk(directory) {
        const entries = fs.readdirSync(directory, { withFileTypes: true });

        for (const entry of entries) {
            const fullPath = path.join(directory, entry.name);

            if (entry.isDirectory()) {
                walk(fullPath);
            } else if (entry.isFile() && entry.name.endsWith('.json') && !entry.name.includes('validation')) {
                files.push(fullPath);
            }
        }
    }

    walk(dir);
    return files;
}

// Analyze a single unit file
function analyzeUnit(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf8');
        const unit = JSON.parse(content);

        const validation = unit.validation || {};
        const confidence = validation.confidence || 0;
        const knownGaps = validation.known_gaps || [];

        // Categorize gaps by severity keywords
        const gapCategories = {
            critical: [],
            important: [],
            moderate: [],
            low: []
        };

        // Convert all gaps to text format (handle both string and object formats)
        const gapTexts = [];

        knownGaps.forEach(gap => {
            // Handle both string format and structured object format
            let gapText;
            if (typeof gap === 'string') {
                gapText = gap;
            } else if (typeof gap === 'object' && gap !== null) {
                // Structured format: {field, reason, mitigation}
                gapText = `${gap.field || ''} ${gap.reason || ''}`.trim();
            } else {
                gapText = '';
            }

            gapTexts.push(gapText);

            const lowerGap = gapText.toLowerCase();
            if (lowerGap.includes('commander') && lowerGap.includes('name unknown')) {
                gapCategories.moderate.push(gapText);
            } else if (lowerGap.includes('exact') || lowerGap.includes('precise')) {
                gapCategories.moderate.push(gapText);
            } else if (lowerGap.includes('not identified') || lowerGap.includes('not confirmed')) {
                gapCategories.moderate.push(gapText);
            } else if (lowerGap.includes('detailed breakdown') || lowerGap.includes('specific dates')) {
                gapCategories.low.push(gapText);
            } else if (lowerGap.includes('strength') || lowerGap.includes('personnel')) {
                gapCategories.important.push(gapText);
            } else if (lowerGap.includes('artillery') || lowerGap.includes('equipment')) {
                gapCategories.important.push(gapText);
            } else {
                gapCategories.low.push(gapText);
            }
        });

        return {
            file: path.basename(filePath),
            fullPath: filePath,
            nation: unit.nation || 'unknown',
            quarter: unit.quarter || 'unknown',
            designation: unit.unit_designation || 'unknown',
            confidence: confidence,
            totalGaps: knownGaps.length,
            gapsBySeverity: {
                critical: gapCategories.critical.length,
                important: gapCategories.important.length,
                moderate: gapCategories.moderate.length,
                low: gapCategories.low.length
            },
            gaps: gapTexts, // Use converted text array instead of raw gaps
            sources: (validation.source || []).length,
            lastUpdated: validation.last_updated || 'unknown'
        };
    } catch (err) {
        return {
            file: path.basename(filePath),
            fullPath: filePath,
            error: err.message,
            confidence: 0
        };
    }
}

// Main analysis (Architecture v4.0 - canonical location only)
const outputDir = path.join(__dirname, '..', 'data', 'output', 'units');
const unitFiles = findUnitFiles(outputDir);

console.log(`Found ${unitFiles.length} unit JSON files\n`);

const analyses = unitFiles.map(analyzeUnit);
const validAnalyses = analyses.filter(a => !a.error);
const errorAnalyses = analyses.filter(a => a.error);

// Calculate metrics
const totalGaps = validAnalyses.reduce((sum, a) => sum + a.totalGaps, 0);
const avgConfidence = validAnalyses.reduce((sum, a) => sum + a.confidence, 0) / validAnalyses.length;

const gapsByCategory = validAnalyses.reduce((acc, a) => {
    a.gaps.forEach(gap => {
        const lower = gap.toLowerCase();
        if (lower.includes('commander')) acc.commanders++;
        else if (lower.includes('equipment') || lower.includes('variant')) acc.equipment_variants++;
        else if (lower.includes('subordinate') || lower.includes('battalion') || lower.includes('regiment')) acc.subordinate_units++;
        else if (lower.includes('personnel') || lower.includes('strength')) acc.personnel++;
        else if (lower.includes('supply') || lower.includes('fuel') || lower.includes('ammunition')) acc.supply_status++;
        else if (lower.includes('witw')) acc.witw_ids++;
        else acc.other++;
    });
    return acc;
}, {
    commanders: 0,
    equipment_variants: 0,
    subordinate_units: 0,
    personnel: 0,
    supply_status: 0,
    witw_ids: 0,
    other: 0
});

const confidenceBands = validAnalyses.reduce((acc, a) => {
    if (a.confidence >= 90) acc['90_100']++;
    else if (a.confidence >= 80) acc['80_89']++;
    else if (a.confidence >= 75) acc['75_79']++;
    else acc['below_75']++;
    return acc;
}, { '90_100': 0, '80_89': 0, '75_79': 0, 'below_75': 0 });

const gapsBySeverity = validAnalyses.reduce((acc, a) => {
    acc.critical += a.gapsBySeverity.critical;
    acc.important += a.gapsBySeverity.important;
    acc.moderate += a.gapsBySeverity.moderate;
    acc.low += a.gapsBySeverity.low;
    return acc;
}, { critical: 0, important: 0, moderate: 0, low: 0 });

// Quarter completion
const byQuarter = validAnalyses.reduce((acc, a) => {
    const q = a.quarter;
    if (!acc[q]) acc[q] = [];
    acc[q].push(a);
    return acc;
}, {});

// Output results
const results = {
    summary: {
        total_files: unitFiles.length,
        valid_units: validAnalyses.length,
        error_units: errorAnalyses.length,
        avg_confidence: Math.round(avgConfidence * 10) / 10,
        total_gaps: totalGaps
    },
    gaps_by_severity: gapsBySeverity,
    gaps_by_category: gapsByCategory,
    confidence_distribution: confidenceBands,
    by_quarter: Object.keys(byQuarter).sort().map(q => ({
        quarter: q,
        count: byQuarter[q].length,
        avg_confidence: Math.round(byQuarter[q].reduce((s, u) => s + u.confidence, 0) / byQuarter[q].length * 10) / 10
    })),
    recent_units: validAnalyses
        .filter(a => a.fullPath.includes('autonomous_1760302575079'))
        .map(a => ({
            file: a.file,
            nation: a.nation,
            quarter: a.quarter,
            designation: a.designation,
            confidence: a.confidence,
            total_gaps: a.totalGaps,
            gaps_by_severity: a.gapsBySeverity
        })),
    low_confidence_units: validAnalyses
        .filter(a => a.confidence < 80)
        .sort((a, b) => a.confidence - b.confidence)
        .slice(0, 10)
        .map(a => ({
            file: a.file,
            confidence: a.confidence,
            designation: a.designation,
            quarter: a.quarter
        })),
    errors: errorAnalyses.map(a => ({
        file: a.file,
        error: a.error
    }))
};

console.log(JSON.stringify(results, null, 2));
