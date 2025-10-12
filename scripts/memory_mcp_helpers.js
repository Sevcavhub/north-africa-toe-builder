#!/usr/bin/env node

/**
 * Memory MCP Integration Helpers
 *
 * Provides wrapper functions for Memory MCP operations with graceful fallback.
 * Stores cross-session knowledge about:
 * - Patterns discovered (quality trends, systematic gaps)
 * - Decisions made (workflow choices, threshold settings)
 * - Quality issues (validation failures, data conflicts)
 * - Source resolutions (how conflicts between sources were resolved)
 *
 * When Memory MCP unavailable, stores to local JSON files as fallback.
 */

const fs = require('fs').promises;
const path = require('path');

const PROJECT_ROOT = path.join(__dirname, '..');
const MEMORY_CACHE_DIR = path.join(PROJECT_ROOT, '.memory_cache');
const PATTERNS_FILE = path.join(MEMORY_CACHE_DIR, 'patterns.json');
const DECISIONS_FILE = path.join(MEMORY_CACHE_DIR, 'decisions.json');
const ISSUES_FILE = path.join(MEMORY_CACHE_DIR, 'quality_issues.json');
const SESSION_STATS_FILE = path.join(MEMORY_CACHE_DIR, 'session_stats.json');

/**
 * Initialize memory cache directory
 */
async function initializeCache() {
    try {
        await fs.mkdir(MEMORY_CACHE_DIR, { recursive: true });
    } catch (error) {
        console.warn('⚠️  Could not create memory cache directory:', error.message);
    }
}

/**
 * Check if Memory MCP is available
 * @returns {Promise<boolean>}
 */
async function isMemoryMCPAvailable() {
    // TODO: Implement actual MCP availability check
    // For now, return false to use file-based fallback
    return false;
}

/**
 * Read data from local cache file
 * @param {string} filepath - Cache file path
 * @returns {Promise<Array>}
 */
async function readCacheFile(filepath) {
    try {
        const data = await fs.readFile(filepath, 'utf-8');
        return JSON.parse(data);
    } catch (error) {
        // File doesn't exist or is invalid - return empty array
        return [];
    }
}

/**
 * Write data to local cache file
 * @param {string} filepath - Cache file path
 * @param {Array} data - Data to write
 */
async function writeCacheFile(filepath, data) {
    await initializeCache();
    await fs.writeFile(filepath, JSON.stringify(data, null, 2));
}

/**
 * Store a pattern discovered during work
 * @param {string} pattern - Pattern description
 * @param {Object} metadata - Additional context (session_id, timestamp, units_affected, etc.)
 * @returns {Promise<boolean>} Success status
 */
async function storePattern(pattern, metadata = {}) {
    const entry = {
        pattern,
        timestamp: new Date().toISOString(),
        ...metadata
    };

    const mcpAvailable = await isMemoryMCPAvailable();

    if (mcpAvailable) {
        // TODO: Use Memory MCP to store pattern
        console.log('📝 Storing pattern to Memory MCP:', pattern);
        return true;
    } else {
        // Fallback to local file
        const patterns = await readCacheFile(PATTERNS_FILE);
        patterns.push(entry);
        await writeCacheFile(PATTERNS_FILE, patterns);
        return true;
    }
}

/**
 * Store a decision made during work
 * @param {string} decision - Decision description
 * @param {string} rationale - Why this decision was made
 * @param {Object} metadata - Additional context
 * @returns {Promise<boolean>} Success status
 */
async function storeDecision(decision, rationale, metadata = {}) {
    const entry = {
        decision,
        rationale,
        timestamp: new Date().toISOString(),
        ...metadata
    };

    const mcpAvailable = await isMemoryMCPAvailable();

    if (mcpAvailable) {
        // TODO: Use Memory MCP to store decision
        console.log('📝 Storing decision to Memory MCP:', decision);
        return true;
    } else {
        // Fallback to local file
        const decisions = await readCacheFile(DECISIONS_FILE);
        decisions.push(entry);
        await writeCacheFile(DECISIONS_FILE, decisions);
        return true;
    }
}

/**
 * Store a quality issue discovered during validation
 * @param {string} issue - Issue description
 * @param {string} severity - 'critical', 'warning', 'info'
 * @param {Object} metadata - Additional context (unit_id, field, expected, actual, etc.)
 * @returns {Promise<boolean>} Success status
 */
async function storeQualityIssue(issue, severity = 'info', metadata = {}) {
    const entry = {
        issue,
        severity,
        timestamp: new Date().toISOString(),
        ...metadata
    };

    const mcpAvailable = await isMemoryMCPAvailable();

    if (mcpAvailable) {
        // TODO: Use Memory MCP to store quality issue
        console.log('📝 Storing quality issue to Memory MCP:', issue);
        return true;
    } else {
        // Fallback to local file
        const issues = await readCacheFile(ISSUES_FILE);
        issues.push(entry);
        await writeCacheFile(ISSUES_FILE, issues);
        return true;
    }
}

/**
 * Store session statistics at session end
 * @param {Object} stats - Session statistics object
 * @returns {Promise<boolean>} Success status
 */
async function storeSessionStats(stats) {
    const entry = {
        ...stats,
        timestamp: new Date().toISOString()
    };

    const mcpAvailable = await isMemoryMCPAvailable();

    if (mcpAvailable) {
        // TODO: Use Memory MCP to store session stats
        console.log('📊 Storing session stats to Memory MCP');
        return true;
    } else {
        // Fallback to local file
        const allStats = await readCacheFile(SESSION_STATS_FILE);
        allStats.push(entry);
        await writeCacheFile(SESSION_STATS_FILE, allStats);
        return true;
    }
}

/**
 * Query project knowledge at session start
 * @returns {Promise<Object>} Knowledge object with patterns, decisions, issues
 */
async function queryProjectKnowledge() {
    const mcpAvailable = await isMemoryMCPAvailable();

    if (mcpAvailable) {
        // TODO: Query Memory MCP for project knowledge
        console.log('🧠 Querying Memory MCP for project knowledge...');
        return {
            available: true,
            patterns: [],
            decisions: [],
            issues: []
        };
    } else {
        // Fallback to local files
        const patterns = await readCacheFile(PATTERNS_FILE);
        const decisions = await readCacheFile(DECISIONS_FILE);
        const issues = await readCacheFile(ISSUES_FILE);

        // Return most recent items (last 10 of each)
        return {
            available: false,
            patterns: patterns.slice(-10).map(p => p.pattern || p),
            decisions: decisions.slice(-10).map(d => d.decision || d),
            issues: issues.slice(-10).filter(i => i.severity === 'critical' || i.severity === 'warning')
        };
    }
}

/**
 * Get pattern statistics
 * @returns {Promise<Object>} Pattern statistics
 */
async function getPatternStats() {
    const patterns = await readCacheFile(PATTERNS_FILE);

    return {
        total_patterns: patterns.length,
        recent_patterns: patterns.slice(-5),
        pattern_categories: categorizeEntries(patterns, 'pattern')
    };
}

/**
 * Get decision statistics
 * @returns {Promise<Object>} Decision statistics
 */
async function getDecisionStats() {
    const decisions = await readCacheFile(DECISIONS_FILE);

    return {
        total_decisions: decisions.length,
        recent_decisions: decisions.slice(-5),
        decision_categories: categorizeEntries(decisions, 'decision')
    };
}

/**
 * Get quality issue statistics
 * @returns {Promise<Object>} Quality issue statistics
 */
async function getQualityIssueStats() {
    const issues = await readCacheFile(ISSUES_FILE);

    const bySeverity = {
        critical: issues.filter(i => i.severity === 'critical').length,
        warning: issues.filter(i => i.severity === 'warning').length,
        info: issues.filter(i => i.severity === 'info').length
    };

    return {
        total_issues: issues.length,
        by_severity: bySeverity,
        recent_critical: issues.filter(i => i.severity === 'critical').slice(-5),
        recent_warnings: issues.filter(i => i.severity === 'warning').slice(-5)
    };
}

/**
 * Helper: Categorize entries by common keywords
 * @param {Array} entries - Array of entry objects
 * @param {string} field - Field to categorize on
 * @returns {Object} Category counts
 */
function categorizeEntries(entries, field) {
    const categories = {};
    const keywords = ['missing', 'estimated', 'confidence', 'source', 'validation', 'quality'];

    for (const entry of entries) {
        const text = (entry[field] || '').toLowerCase();
        for (const keyword of keywords) {
            if (text.includes(keyword)) {
                categories[keyword] = (categories[keyword] || 0) + 1;
            }
        }
    }

    return categories;
}

/**
 * Clear local cache (useful for testing or reset)
 * @returns {Promise<void>}
 */
async function clearCache() {
    try {
        await fs.rm(MEMORY_CACHE_DIR, { recursive: true, force: true });
        console.log('✅ Memory cache cleared');
    } catch (error) {
        console.warn('⚠️  Could not clear cache:', error.message);
    }
}

/**
 * Export cache to file for backup/sharing
 * @param {string} exportPath - Path to export to
 * @returns {Promise<boolean>} Success status
 */
async function exportCache(exportPath) {
    try {
        const patterns = await readCacheFile(PATTERNS_FILE);
        const decisions = await readCacheFile(DECISIONS_FILE);
        const issues = await readCacheFile(ISSUES_FILE);
        const stats = await readCacheFile(SESSION_STATS_FILE);

        const exportData = {
            exported_at: new Date().toISOString(),
            patterns,
            decisions,
            issues,
            session_stats: stats
        };

        await fs.writeFile(exportPath, JSON.stringify(exportData, null, 2));
        console.log(`✅ Cache exported to: ${exportPath}`);
        return true;
    } catch (error) {
        console.error('❌ Export failed:', error.message);
        return false;
    }
}

/**
 * Import cache from backup file
 * @param {string} importPath - Path to import from
 * @returns {Promise<boolean>} Success status
 */
async function importCache(importPath) {
    try {
        const data = await fs.readFile(importPath, 'utf-8');
        const importData = JSON.parse(data);

        await initializeCache();

        if (importData.patterns) {
            await writeCacheFile(PATTERNS_FILE, importData.patterns);
        }
        if (importData.decisions) {
            await writeCacheFile(DECISIONS_FILE, importData.decisions);
        }
        if (importData.issues) {
            await writeCacheFile(ISSUES_FILE, importData.issues);
        }
        if (importData.session_stats) {
            await writeCacheFile(SESSION_STATS_FILE, importData.session_stats);
        }

        console.log(`✅ Cache imported from: ${importPath}`);
        return true;
    } catch (error) {
        console.error('❌ Import failed:', error.message);
        return false;
    }
}

module.exports = {
    // Core functions
    storePattern,
    storeDecision,
    storeQualityIssue,
    storeSessionStats,
    queryProjectKnowledge,

    // Statistics
    getPatternStats,
    getDecisionStats,
    getQualityIssueStats,

    // Utilities
    isMemoryMCPAvailable,
    clearCache,
    exportCache,
    importCache
};

// CLI interface for testing
if (require.main === module) {
    const command = process.argv[2];

    async function runCommand() {
        switch (command) {
            case 'test-store':
                console.log('Testing storage...\n');
                await storePattern('80% of units have estimated battalion TO&E', { confidence: 0.8 });
                await storeDecision('Use 2-3 agents max', 'More agents caused crashes', { agents: 3 });
                await storeQualityIssue('WITW IDs missing', 'warning', { units_affected: 213 });
                console.log('✅ Test storage complete\n');
                break;

            case 'test-query':
                console.log('Testing query...\n');
                const knowledge = await queryProjectKnowledge();
                console.log('Patterns:', knowledge.patterns);
                console.log('Decisions:', knowledge.decisions);
                console.log('Issues:', knowledge.issues);
                console.log('✅ Test query complete\n');
                break;

            case 'stats':
                console.log('Memory Statistics\n');
                console.log('═'.repeat(60));
                const patternStats = await getPatternStats();
                const decisionStats = await getDecisionStats();
                const issueStats = await getQualityIssueStats();

                console.log(`\n📊 Patterns: ${patternStats.total_patterns} total`);
                console.log('   Categories:', patternStats.pattern_categories);

                console.log(`\n📊 Decisions: ${decisionStats.total_decisions} total`);
                console.log('   Categories:', decisionStats.decision_categories);

                console.log(`\n📊 Quality Issues: ${issueStats.total_issues} total`);
                console.log('   By Severity:', issueStats.by_severity);
                console.log('');
                break;

            case 'export':
                const exportPath = process.argv[3] || path.join(PROJECT_ROOT, 'memory_export.json');
                await exportCache(exportPath);
                break;

            case 'import':
                const importPath = process.argv[3];
                if (!importPath) {
                    console.error('❌ Usage: node memory_mcp_helpers.js import <filepath>');
                    process.exit(1);
                }
                await importCache(importPath);
                break;

            case 'clear':
                console.log('⚠️  Clearing memory cache...');
                await clearCache();
                break;

            default:
                console.log('Memory MCP Helpers - CLI Interface\n');
                console.log('Commands:');
                console.log('  test-store   - Test storing data');
                console.log('  test-query   - Test querying data');
                console.log('  stats        - Show memory statistics');
                console.log('  export <path> - Export cache to file');
                console.log('  import <path> - Import cache from file');
                console.log('  clear        - Clear local cache');
                console.log('');
        }
    }

    runCommand().catch(error => {
        console.error('❌ Error:', error.message);
        process.exit(1);
    });
}
