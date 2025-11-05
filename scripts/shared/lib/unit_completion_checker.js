const fs = require('fs');
const path = require('path');

/**
 * Unit Completion Checker
 *
 * Checks if a unit is already completed using alias-aware matching.
 * Integrates with canonical master matcher logic.
 */
class UnitCompletionChecker {
    constructor() {
        this.matchingReport = null;
        this.completedMap = new Map();
        this.load();
    }

    /**
     * Load canonical matching report
     */
    load() {
        try {
            const reportPath = path.join(__dirname, '../../data/canonical/CANONICAL_MATCHING_REPORT.json');
            this.matchingReport = JSON.parse(fs.readFileSync(reportPath, 'utf8'));

            // Build quick lookup map
            this.buildCompletedMap();

        } catch (error) {
            console.warn(`⚠️  Could not load canonical matching report: ${error.message}`);
            console.warn('   Skip-completed logic will be disabled.');
        }
    }

    /**
     * Build map of completed units for O(1) lookup
     */
    buildCompletedMap() {
        if (!this.matchingReport) return;

        // Add exact matches
        for (const match of this.matchingReport.matches.exact_matches) {
            const key = `${match.nation}|${match.quarter}|${match.designation}`;
            this.completedMap.set(key, {
                matchType: 'exact',
                file: match.matched_file,
                canonical_id: match.canonical_id
            });
        }

        // Add valid alias matches
        for (const match of this.matchingReport.matches.alias_matches) {
            const key = `${match.nation}|${match.quarter}|${match.designation}`;
            this.completedMap.set(key, {
                matchType: 'alias',
                file: match.matched_file,
                canonical_id: match.canonical_id
            });
        }
    }

    /**
     * Check if a unit is completed
     *
     * @param {string} nation - Nation (american, british, etc.)
     * @param {string} quarter - Quarter (1940q2, 1941q1, etc.)
     * @param {string} designation - Unit designation
     * @returns {object|null} - Completion info or null if not completed
     */
    isCompleted(nation, quarter, designation) {
        if (!this.matchingReport) return null;

        // Normalize quarter format (1940-Q2 → 1940q2)
        const normalizedQuarter = quarter.toLowerCase().replace(/-/g, '');

        // Check exact match
        const key = `${nation}|${normalizedQuarter}|${designation}`;
        const match = this.completedMap.get(key);

        if (match) {
            return {
                completed: true,
                matchType: match.matchType,
                file: match.file,
                canonical_id: match.canonical_id,
                path: `data/output/units/${match.file}`
            };
        }

        return null;
    }

    /**
     * Get completion statistics
     */
    getStats() {
        if (!this.matchingReport) {
            return {
                available: false,
                message: 'Matching report not loaded'
            };
        }

        return {
            available: true,
            total: this.matchingReport.completion_stats.total_unit_quarters,
            completed: this.matchingReport.completion_stats.completed,
            incomplete: this.matchingReport.completion_stats.incomplete,
            percentage: this.matchingReport.completion_stats.completion_percentage,
            exact_matches: this.matchingReport.completion_stats.exact_matches,
            alias_matches: this.matchingReport.completion_stats.alias_matches,
            by_nation: this.matchingReport.completion_stats.by_nation
        };
    }

    /**
     * Filter incomplete units from a seed unit list
     *
     * @param {Array} seedUnits - Array of seed unit objects
     * @returns {object} - { incomplete: [], completed: [], stats: {} }
     */
    filterIncomplete(seedUnits) {
        const incomplete = [];
        const completed = [];

        for (const unit of seedUnits) {
            const completionInfo = this.isCompleted(
                unit.nation,
                unit.quarter,
                unit.unit_designation
            );

            if (completionInfo) {
                completed.push({
                    ...unit,
                    completion: completionInfo
                });
            } else {
                incomplete.push(unit);
            }
        }

        return {
            incomplete,
            completed,
            stats: {
                total: seedUnits.length,
                completed: completed.length,
                incomplete: incomplete.length,
                completion_percentage: ((completed.length / seedUnits.length) * 100).toFixed(1)
            }
        };
    }
}

module.exports = { UnitCompletionChecker };
