/**
 * Flexible Unit Matching Library
 *
 * Handles matching unit designations against completed files with support for:
 * - Exact matches
 * - Alias matches (full official names, abbreviated names, variants)
 * - Normalized string matching (removes special chars, handles spacing)
 * - Partial word matching (careful to avoid quarter-crossing)
 *
 * Created: October 2025
 * Purpose: Fix naming variant issues where agents find full official names
 *          but seed file has abbreviated names
 */

/**
 * Normalize a designation string for matching
 * Removes special characters, extra whitespace, converts to lowercase
 *
 * @param {string} designation - Original designation
 * @returns {string} Normalized designation
 */
function normalizeDesignation(designation) {
    return designation
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '_')
        .replace(/^_+|_+$/g, '');
}

/**
 * Check if a unit is completed using flexible matching
 *
 * @param {string} nation - Nation (german, italian, british, american, french)
 * @param {string} quarter - Quarter in yyyyqn format (e.g., "1943q1")
 * @param {string} designation - Unit designation to check
 * @param {Array<string>} aliases - Optional array of aliases to also check
 * @param {Set<string>} completedSet - Set of completed unit IDs
 * @returns {boolean} True if unit is completed
 */
function isUnitCompleted(nation, quarter, designation, aliases = [], completedSet) {
    // Normalize inputs
    const normalizedQuarter = quarter.toLowerCase().replace(/-/g, '');
    const normalizedDesignation = normalizeDesignation(designation);

    // 1. Try exact canonical match first (normalized designation)
    const canonicalId = `${nation}_${normalizedQuarter}_${normalizedDesignation}`;
    if (completedSet.has(canonicalId)) {
        return true;
    }

    // 1.5. Try non-normalized designation (for backwards compatibility)
    // Handles workflow state entries like "italian_1941q3_101st TRIESTE Division"
    const nonNormalizedId = `${nation}_${normalizedQuarter}_${designation}`;
    if (completedSet.has(nonNormalizedId)) {
        return true;
    }

    // 2. Try all aliases (if provided)
    if (aliases && aliases.length > 0) {
        for (const alias of aliases) {
            const aliasNormalized = normalizeDesignation(alias);
            const aliasId = `${nation}_${normalizedQuarter}_${aliasNormalized}`;
            if (completedSet.has(aliasId)) {
                return true;
            }
            // Also try non-normalized alias
            const aliasNonNormId = `${nation}_${normalizedQuarter}_${alias}`;
            if (completedSet.has(aliasNonNormId)) {
                return true;
            }
        }
    }

    // 3. Try partial word matching (ONLY within same nation and quarter)
    // This handles cases where file has extra words not in seed
    // Example: seed "4th Indian Division" matches file "4th Indian Infantry Division"
    const prefix = `${nation}_${normalizedQuarter}_`;
    const designationWords = designation.toLowerCase().split(/\s+/).filter(w => w.length > 2);

    if (designationWords.length > 0) {
        for (const completedId of completedSet) {
            // CRITICAL: Only match within same nation and quarter
            if (!completedId.startsWith(prefix)) {
                continue;
            }

            // Extract designation part from completed ID
            const completedDesignation = completedId.substring(prefix.length);

            // Check if all significant words from seed appear in completed file
            const allWordsMatch = designationWords.every(word => {
                // For short words (3-4 chars), require exact match
                // For longer words, allow partial match (first 4+ chars)
                const searchTerm = word.length <= 4 ? word : word.substring(0, 4);
                return completedDesignation.includes(searchTerm);
            });

            if (allWordsMatch) {
                return true;
            }
        }
    }

    return false;
}

/**
 * Find all completed units that match a seed unit
 * Useful for reconciliation and debugging
 *
 * @param {string} nation - Nation
 * @param {string} quarter - Quarter
 * @param {string} designation - Unit designation
 * @param {Array<string>} aliases - Aliases
 * @param {Set<string>} completedSet - Set of completed unit IDs
 * @returns {Array<string>} Array of matching completed unit IDs
 */
function findMatchingCompletedUnits(nation, quarter, designation, aliases = [], completedSet) {
    const matches = [];
    const normalizedQuarter = quarter.toLowerCase().replace(/-/g, '');
    const normalizedDesignation = normalizeDesignation(designation);

    // Check canonical ID
    const canonicalId = `${nation}_${normalizedQuarter}_${normalizedDesignation}`;
    if (completedSet.has(canonicalId)) {
        matches.push(canonicalId);
    }

    // Check aliases
    if (aliases && aliases.length > 0) {
        for (const alias of aliases) {
            const aliasNormalized = normalizeDesignation(alias);
            const aliasId = `${nation}_${normalizedQuarter}_${aliasNormalized}`;
            if (completedSet.has(aliasId)) {
                matches.push(aliasId);
            }
        }
    }

    // Check partial matches
    const prefix = `${nation}_${normalizedQuarter}_`;
    const designationWords = designation.toLowerCase().split(/\s+/).filter(w => w.length > 2);

    if (designationWords.length > 0) {
        for (const completedId of completedSet) {
            if (!completedId.startsWith(prefix)) continue;
            if (matches.includes(completedId)) continue; // Already found via exact/alias match

            const completedDesignation = completedId.substring(prefix.length);
            const allWordsMatch = designationWords.every(word => {
                const searchTerm = word.length <= 4 ? word : word.substring(0, 4);
                return completedDesignation.includes(searchTerm);
            });

            if (allWordsMatch) {
                matches.push(completedId);
            }
        }
    }

    return matches;
}

/**
 * Build a mapping of seed units to completed file IDs
 * Useful for reconciliation reporting
 *
 * @param {Object} seed - Seed file data
 * @param {Set<string>} completedSet - Set of completed unit IDs
 * @returns {Object} Mapping of seed keys to matched file IDs
 */
function buildSeedToFileMapping(seed, completedSet) {
    const nationMap = {
        german_units: 'german',
        italian_units: 'italian',
        british_units: 'british',
        usa_units: 'american',  // Seed uses usa_units, files use american
        french_units: 'french'
    };

    const mapping = {};

    for (const [seedKey, nationName] of Object.entries(nationMap)) {
        if (!seed[seedKey]) continue;

        const units = seed[seedKey];

        units.forEach(unit => {
            const designation = unit.designation;
            const aliases = unit.aliases || [];

            unit.quarters.forEach(quarter => {
                const normalizedQuarter = quarter.toLowerCase().replace(/-/g, '');
                const seedId = `${nationName}_${normalizedQuarter}_${normalizeDesignation(designation)}`;

                const matches = findMatchingCompletedUnits(
                    nationName,
                    quarter,
                    designation,
                    aliases,
                    completedSet
                );

                if (matches.length > 0) {
                    mapping[seedId] = {
                        seed_designation: designation,
                        aliases: aliases,
                        matched_files: matches,
                        match_count: matches.length
                    };
                }
            });
        });
    }

    return mapping;
}

module.exports = {
    normalizeDesignation,
    isUnitCompleted,
    findMatchingCompletedUnits,
    buildSeedToFileMapping
};
