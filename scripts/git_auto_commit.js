#!/usr/bin/env node

/**
 * Automated Git Commit and Push
 *
 * Automatically commits and pushes changes after unit extraction batches
 * Usage: node scripts/git_auto_commit.js [batch_name]
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const AUTO_PUSH = process.env.GIT_AUTO_PUSH !== 'false'; // Default: true
const DRY_RUN = process.argv.includes('--dry-run');

function runGitCommand(command, options = {}) {
    try {
        const result = execSync(command, {
            cwd: path.join(__dirname, '..'),
            encoding: 'utf-8',
            ...options
        });
        return { success: true, output: result.trim() };
    } catch (error) {
        return {
            success: false,
            error: error.message,
            output: error.stdout?.toString() || ''
        };
    }
}

function getChangedFiles() {
    const result = runGitCommand('git status --porcelain');
    if (!result.success) return [];

    return result.output
        .split('\n')
        .filter(line => line.trim())
        .map(line => {
            const status = line.substring(0, 2);
            const file = line.substring(3);
            return { status, file };
        });
}

function countUnitFiles(changes) {
    return changes.filter(c =>
        c.file.includes('units/') && c.file.endsWith('.json')
    ).length;
}

function countChapterFiles(changes) {
    return changes.filter(c =>
        c.file.includes('north_africa_book/src/chapter_') && c.file.endsWith('.md')
    ).length;
}

function generateCommitMessage(changes, batchName) {
    const unitCount = countUnitFiles(changes);
    const chapterCount = countChapterFiles(changes);

    let message = '';

    if (batchName) {
        message = `feat: Add ${batchName} extraction\n\n`;
    } else {
        message = 'feat: Add unit extraction batch\n\n';
    }

    const details = [];
    if (unitCount > 0) details.push(`- ${unitCount} unit JSON files`);
    if (chapterCount > 0) details.push(`- ${chapterCount} MDBook chapters`);

    // Check for other significant changes
    const hasAgentChanges = changes.some(c => c.file.includes('agents/'));
    const hasSchemaChanges = changes.some(c => c.file.includes('schemas/'));
    const hasDocsChanges = changes.some(c => c.file.includes('docs/'));

    if (hasAgentChanges) details.push('- Agent configuration updates');
    if (hasSchemaChanges) details.push('- Schema updates');
    if (hasDocsChanges) details.push('- Documentation updates');

    if (details.length > 0) {
        message += details.join('\n') + '\n\n';
    }

    message += '🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\n';
    message += 'Co-Authored-By: Claude <noreply@anthropic.com>';

    return message;
}

async function main() {
    const batchName = process.argv[2];

    console.log('🔍 Checking for changes...');

    // Check if working tree is clean
    const statusResult = runGitCommand('git status --porcelain');
    if (!statusResult.success) {
        console.error('❌ Failed to check git status:', statusResult.error);
        process.exit(1);
    }

    if (!statusResult.output) {
        console.log('✅ Working tree clean - nothing to commit');
        return;
    }

    const changes = getChangedFiles();
    console.log(`📝 Found ${changes.length} changed files`);

    const unitCount = countUnitFiles(changes);
    const chapterCount = countChapterFiles(changes);

    if (unitCount > 0) console.log(`   - ${unitCount} unit files`);
    if (chapterCount > 0) console.log(`   - ${chapterCount} chapter files`);

    if (DRY_RUN) {
        console.log('\n🔍 DRY RUN MODE - No changes will be committed\n');
        const message = generateCommitMessage(changes, batchName);
        console.log('Would commit with message:');
        console.log('---');
        console.log(message);
        console.log('---');
        return;
    }

    // Stage all changes
    console.log('\n📦 Staging changes...');
    const addResult = runGitCommand('git add .');
    if (!addResult.success) {
        console.error('❌ Failed to stage changes:', addResult.error);
        process.exit(1);
    }

    // Generate commit message
    const commitMessage = generateCommitMessage(changes, batchName);

    // Commit
    console.log('💾 Creating commit...');
    const commitResult = runGitCommand(
        `git commit -m "${commitMessage.replace(/"/g, '\\"')}"`,
        { stdio: 'pipe' }
    );

    if (!commitResult.success) {
        console.error('❌ Failed to commit:', commitResult.error);
        process.exit(1);
    }

    console.log('✅ Commit created successfully');

    // Push to GitHub
    if (AUTO_PUSH) {
        console.log('\n🚀 Pushing to GitHub...');
        const pushResult = runGitCommand('git push', { stdio: 'inherit' });

        if (!pushResult.success) {
            console.error('⚠️  Failed to push to GitHub:', pushResult.error);
            console.log('💡 Changes are committed locally. Push manually later with: git push');
            process.exit(1);
        }

        console.log('✅ Pushed to GitHub successfully');
    } else {
        console.log('\n⏭️  Auto-push disabled (set GIT_AUTO_PUSH=true to enable)');
        console.log('💡 Push manually with: git push');
    }

    console.log('\n✨ Done!');
}

// Run
main().catch(error => {
    console.error('❌ Error:', error.message);
    process.exit(1);
});
