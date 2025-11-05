#!/usr/bin/env node

/**
 * Canonical Path Definitions - Architecture v4.0
 *
 * Single source of truth for all output locations.
 * Import this module in ALL scripts to prevent path drift.
 *
 * Created: 2025-10-14
 * Version: 1.0.0
 *
 * Usage:
 *   const paths = require('./lib/canonical_paths');
 *   const unitPath = paths.getUnitPath('german', '1941q2', '15_panzer_division');
 *   // Returns: D:\north-africa-toe-builder\data\output\units\german_1941q2_15_panzer_division_toe.json
 */

const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '../..');

/**
 * Canonical output directories (single source of truth)
 */
const CANONICAL_PATHS = {
    // Core output locations
    PROJECT_ROOT: PROJECT_ROOT,
    OUTPUT_ROOT: path.join(PROJECT_ROOT, 'data/output'),

    // Phase 1-6: Ground Forces (CANONICAL)
    UNITS_DIR: path.join(PROJECT_ROOT, 'data/output/units'),
    CHAPTERS_DIR: path.join(PROJECT_ROOT, 'data/output/chapters'),

    // Phase 7: Air Forces (CANONICAL - future)
    AIR_UNITS_DIR: path.join(PROJECT_ROOT, 'data/output/air_units'),
    AIR_CHAPTERS_DIR: path.join(PROJECT_ROOT, 'data/output/air_chapters'),

    // Phase 9: Scenarios (CANONICAL - future)
    SCENARIOS_DIR: path.join(PROJECT_ROOT, 'data/output/scenarios'),

    // Phase 10: Campaign data (CANONICAL - future)
    CAMPAIGN_DIR: path.join(PROJECT_ROOT, 'data/output/campaign'),

    // Session work (temporary - archived after completion)
    SESSIONS_DIR: path.join(PROJECT_ROOT, 'data/output/sessions'),

    // Other output locations
    QA_REPORTS_DIR: path.join(PROJECT_ROOT, 'data/output/qa_reports'),
    SHOWCASE_DIR: path.join(PROJECT_ROOT, 'data/output/showcase'),
    ARCHIVED_DIR: path.join(PROJECT_ROOT, 'data/output/_archived'),

    // Database
    DATABASE_PATH: path.join(PROJECT_ROOT, 'data/toe_database.db'),

    // State tracking
    WORKFLOW_STATE: path.join(PROJECT_ROOT, 'WORKFLOW_STATE.json'),
    SESSION_CHECKPOINT: path.join(PROJECT_ROOT, 'SESSION_CHECKPOINT.md'),
    SESSION_SUMMARY: path.join(PROJECT_ROOT, 'SESSION_SUMMARY.md')
};

/**
 * Helper functions for generating specific file paths
 */
const PathHelpers = {
    /**
     * Get canonical path for a unit TO&E JSON file
     * @param {string} nation - Nation code (german, italian, british, american, french)
     * @param {string} quarter - Quarter (1941q2, 1941-Q2, etc - will normalize)
     * @param {string} designation - Unit designation (15_panzer_division)
     * @returns {string} Full path to unit file
     */
    getUnitPath(nation, quarter, designation) {
        // Normalize quarter format (remove hyphen, lowercase q)
        const normalizedQuarter = quarter.replace('-', '').replace('Q', 'q').toLowerCase();
        const filename = `${nation}_${normalizedQuarter}_${designation}_toe.json`;
        return path.join(CANONICAL_PATHS.UNITS_DIR, filename);
    },

    /**
     * Get canonical path for an air unit TO&E JSON file
     * @param {string} nation - Nation code
     * @param {string} quarter - Quarter
     * @param {string} designation - Air unit designation
     * @returns {string} Full path to air unit file
     */
    getAirUnitPath(nation, quarter, designation) {
        const normalizedQuarter = quarter.replace('-', '').replace('Q', 'q').toLowerCase();
        const filename = `${nation}_${normalizedQuarter}_${designation}_air_toe.json`;
        return path.join(CANONICAL_PATHS.AIR_UNITS_DIR, filename);
    },

    /**
     * Get canonical path for an MDBook chapter
     * @param {string} nation - Nation code
     * @param {string} quarter - Quarter
     * @param {string} designation - Unit designation
     * @returns {string} Full path to chapter file
     */
    getChapterPath(nation, quarter, designation) {
        const normalizedQuarter = quarter.replace('-', '').replace('Q', 'q').toLowerCase();
        const filename = `chapter_${nation}_${normalizedQuarter}_${designation}.md`;
        return path.join(CANONICAL_PATHS.CHAPTERS_DIR, filename);
    },

    /**
     * Get canonical path for an air unit MDBook chapter
     * @param {string} nation - Nation code
     * @param {string} quarter - Quarter
     * @param {string} designation - Air unit designation
     * @returns {string} Full path to air chapter file
     */
    getAirChapterPath(nation, quarter, designation) {
        const normalizedQuarter = quarter.replace('-', '').replace('Q', 'q').toLowerCase();
        const filename = `chapter_air_${nation}_${normalizedQuarter}_${designation}.md`;
        return path.join(CANONICAL_PATHS.AIR_CHAPTERS_DIR, filename);
    },

    /**
     * Get session work directory (temporary)
     * @param {string} sessionId - Session identifier
     * @returns {string} Full path to session directory
     */
    getSessionDir(sessionId) {
        return path.join(CANONICAL_PATHS.SESSIONS_DIR, sessionId);
    },

    /**
     * Get scenario output path
     * @param {string} scenarioName - Name of scenario (e.g., "operation_battleaxe_1941q2")
     * @returns {string} Full path to scenario directory
     */
    getScenarioPath(scenarioName) {
        return path.join(CANONICAL_PATHS.SCENARIOS_DIR, scenarioName);
    }
};

/**
 * Validation: Ensure canonical directories exist
 * Call this at the start of any script that writes output
 */
async function ensureCanonicalDirectoriesExist() {
    const fs = require('fs').promises;

    const requiredDirs = [
        CANONICAL_PATHS.UNITS_DIR,
        CANONICAL_PATHS.CHAPTERS_DIR,
        CANONICAL_PATHS.AIR_UNITS_DIR,
        CANONICAL_PATHS.AIR_CHAPTERS_DIR,
        CANONICAL_PATHS.SCENARIOS_DIR,
        CANONICAL_PATHS.CAMPAIGN_DIR,
        CANONICAL_PATHS.SESSIONS_DIR,
        CANONICAL_PATHS.QA_REPORTS_DIR
    ];

    for (const dir of requiredDirs) {
        await fs.mkdir(dir, { recursive: true });
    }
}

/**
 * Check if a path is canonical (not in archived session directory)
 * @param {string} filePath - Path to check
 * @returns {boolean} True if canonical, false if in archived session
 */
function isCanonicalPath(filePath) {
    const normalized = path.normalize(filePath);

    // Canonical paths (Ground Forces)
    if (normalized.includes(path.normalize(CANONICAL_PATHS.UNITS_DIR))) return true;
    if (normalized.includes(path.normalize(CANONICAL_PATHS.CHAPTERS_DIR))) return true;

    // Canonical paths (Air Forces - Phase 7)
    if (normalized.includes(path.normalize(CANONICAL_PATHS.AIR_UNITS_DIR))) return true;
    if (normalized.includes(path.normalize(CANONICAL_PATHS.AIR_CHAPTERS_DIR))) return true;

    // Canonical paths (Scenarios - Phase 9)
    if (normalized.includes(path.normalize(CANONICAL_PATHS.SCENARIOS_DIR))) return true;

    // Canonical paths (Campaign - Phase 10)
    if (normalized.includes(path.normalize(CANONICAL_PATHS.CAMPAIGN_DIR))) return true;

    // Non-canonical (archived sessions)
    if (normalized.includes(path.normalize(CANONICAL_PATHS.SESSIONS_DIR))) return false;
    if (normalized.includes(path.normalize(CANONICAL_PATHS.ARCHIVED_DIR))) return false;
    if (normalized.includes('autonomous_')) return false; // Old session pattern

    return false; // Unknown, treat as non-canonical
}

// Export all paths and helpers
module.exports = {
    ...CANONICAL_PATHS,
    ...PathHelpers,
    ensureCanonicalDirectoriesExist,
    isCanonicalPath
};
