/**
 * Canonical Naming Standard for Unit Files
 *
 * Single source of truth for generating consistent unit filenames.
 * Pattern: {nation}_{quarter}_{unit_designation}_toe.json
 * Example: german_1941q2_15th_panzer_division_toe.json
 *
 * CRITICAL: ALL scripts must use this module to ensure consistency.
 */

const NATIONS = {
    GERMAN: 'german',
    ITALIAN: 'italian',
    BRITISH: 'british',      // Includes all Commonwealth (Australia, NZ, India, SA, Canada)
    AMERICAN: 'american',    // For USA units
    FRENCH: 'french'
};

// Map from seed file keys to canonical nation values
const NATION_MAP = {
    'german_units': 'german',
    'italian_units': 'italian',
    'british_units': 'british',
    'usa_units': 'american',
    'french_units': 'french'
};

// Reverse map for reading existing files
const NATION_VARIATIONS = {
    'german': ['german', 'germany'],
    'italian': ['italian', 'italy'],
    'british': ['british', 'britain', 'newzealand', 'australia', 'india', 'southafrican', 'canadian'],
    'american': ['american', 'usa', 'us'],
    'french': ['french', 'france']
};

/**
 * Normalize a nation value to canonical form
 * @param {string} nation - Nation value (can be any variation)
 * @returns {string} Canonical nation value
 */
function normalizeNation(nation) {
    const lower = nation.toLowerCase();

    // Check if it's already canonical
    if (Object.values(NATIONS).includes(lower)) {
        return lower;
    }

    // Check if it's in the seed map
    if (NATION_MAP[lower]) {
        return NATION_MAP[lower];
    }

    // Check variations
    for (const [canonical, variations] of Object.entries(NATION_VARIATIONS)) {
        if (variations.includes(lower)) {
            return canonical;
        }
    }

    // Default: return as lowercase
    console.warn(`⚠️  Unknown nation: ${nation}, using lowercase`);
    return lower;
}

/**
 * Normalize a quarter value to canonical form (lowercase, no hyphen)
 * @param {string} quarter - Quarter value (e.g., "1941-Q2", "1941Q2", "1941q2")
 * @returns {string} Canonical quarter value (e.g., "1941q2")
 */
function normalizeQuarter(quarter) {
    return quarter.toLowerCase().replace(/-/g, '');
}

/**
 * Normalize a unit designation for use in filename
 * @param {string} designation - Unit designation (e.g., "15th Panzer Division")
 * @returns {string} Cleaned designation (e.g., "15th_panzer_division")
 */
function normalizeDesignation(designation) {
    return designation
        .toLowerCase()
        .replace(/[^a-z0-9]/g, '_')  // Replace non-alphanumeric with underscore
        .replace(/_+/g, '_')          // Collapse multiple underscores
        .replace(/^_|_$/g, '');       // Remove leading/trailing underscores
}

/**
 * Generate canonical filename for a unit
 * @param {string} nation - Nation value (will be normalized)
 * @param {string} quarter - Quarter value (will be normalized)
 * @param {string} designation - Unit designation (will be normalized)
 * @returns {string} Canonical filename
 */
function generateFilename(nation, quarter, designation) {
    const cleanNation = normalizeNation(nation);
    const cleanQuarter = normalizeQuarter(quarter);
    const cleanDesignation = normalizeDesignation(designation);

    return `${cleanNation}_${cleanQuarter}_${cleanDesignation}_toe.json`;
}

/**
 * Parse a unit filename to extract components
 * @param {string} filename - Unit filename
 * @returns {object|null} Parsed components or null if invalid
 */
function parseFilename(filename) {
    // Pattern: {nation}_{quarter}_{designation}_toe.json
    const match = filename.match(/^([a-z]+)_(\d{4}[-]?q\d)_(.+)_toe\.json$/i);

    if (!match) {
        return null;
    }

    return {
        nation: normalizeNation(match[1]),
        quarter: normalizeQuarter(match[2]),
        designation: match[3],
        original: filename
    };
}

/**
 * Check if a filename matches a unit (handles variations)
 * @param {string} filename - Filename to check
 * @param {string} nation - Expected nation
 * @param {string} quarter - Expected quarter
 * @param {string} designation - Expected designation
 * @returns {boolean} True if filename matches
 */
function matchesUnit(filename, nation, quarter, designation) {
    const parsed = parseFilename(filename);
    if (!parsed) return false;

    const expectedNation = normalizeNation(nation);
    const expectedQuarter = normalizeQuarter(quarter);
    const expectedDesignation = normalizeDesignation(designation);

    // Nation must match exactly
    if (parsed.nation !== expectedNation) return false;

    // Quarter must match exactly
    if (parsed.quarter !== expectedQuarter) return false;

    // Designation: check if key words match
    // Filter out common words and numbers
    const commonWords = ['the', 'and', 'div', 'division', 'infantry', 'armoured', 'armored', 'de', 'di', 'du'];
    const parsedWords = parsed.designation.split('_').filter(w => w.length > 2 && !commonWords.includes(w) && !/^\d+$/.test(w));
    const expectedWords = expectedDesignation.split('_').filter(w => w.length > 2 && !commonWords.includes(w) && !/^\d+$/.test(w));

    // If no meaningful words left, check if designation is contained in filename
    if (expectedWords.length === 0) {
        return parsed.designation.includes(expectedDesignation) || expectedDesignation.includes(parsed.designation);
    }

    // Count matching words
    const matchingWords = parsedWords.filter(w => expectedWords.includes(w)).length;

    // Also check reverse - expected words found in parsed
    const reverseMatching = expectedWords.filter(w => parsedWords.includes(w)).length;
    const bestMatch = Math.max(matchingWords, reverseMatching);

    // Need at least 1 significant word match, or 2 if there are many words
    const minWords = expectedWords.length >= 3 ? 2 : 1;

    return bestMatch >= minWords;
}

module.exports = {
    NATIONS,
    NATION_MAP,
    NATION_VARIATIONS,
    normalizeNation,
    normalizeQuarter,
    normalizeDesignation,
    generateFilename,
    parseFilename,
    matchesUnit
};
