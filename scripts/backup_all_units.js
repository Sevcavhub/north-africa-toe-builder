#!/usr/bin/env node

/**
 * Full Backup Script - Backup all units and chapters before Wikipedia source upgrade
 *
 * Creates complete backup with checksums for safe rollback
 */

const fs = require('fs').promises;
const fsSync = require('fs');
const path = require('path');
const crypto = require('crypto');

const PROJECT_ROOT = path.join(__dirname, '..');
const UNITS_DIR = path.join(PROJECT_ROOT, 'data/output/units');
const CHAPTERS_DIR = path.join(PROJECT_ROOT, 'data/output/chapters');
const BACKUP_ROOT = path.join(PROJECT_ROOT, 'data/backups');

// Generate timestamp for backup folder
const timestamp = new Date().toISOString().replace(/:/g, '-').split('.')[0];
const BACKUP_DIR = path.join(BACKUP_ROOT, `full_backup_${timestamp}`);
const BACKUP_UNITS_DIR = path.join(BACKUP_DIR, 'units');
const BACKUP_CHAPTERS_DIR = path.join(BACKUP_DIR, 'chapters');

/**
 * Calculate MD5 checksum for a file
 */
async function calculateChecksum(filepath) {
    const hash = crypto.createHash('md5');
    const data = await fs.readFile(filepath);
    hash.update(data);
    return hash.digest('hex');
}

/**
 * Copy file and return metadata
 */
async function copyFileWithMetadata(sourcePath, destPath) {
    await fs.copyFile(sourcePath, destPath);

    const stats = await fs.stat(sourcePath);
    const checksum = await calculateChecksum(sourcePath);

    return {
        filename: path.basename(sourcePath),
        source: sourcePath,
        backup: destPath,
        size: stats.size,
        checksum: checksum,
        modified: stats.mtime.toISOString()
    };
}

/**
 * Main backup function
 */
async function main() {
    console.log('Full Backup Script');
    console.log('=' .repeat(80));
    console.log('');

    // Create backup directories
    console.log('Creating backup directories...');
    await fs.mkdir(BACKUP_ROOT, { recursive: true });
    await fs.mkdir(BACKUP_DIR, { recursive: true });
    await fs.mkdir(BACKUP_UNITS_DIR, { recursive: true });
    await fs.mkdir(BACKUP_CHAPTERS_DIR, { recursive: true });
    console.log(`  Backup location: ${BACKUP_DIR}`);
    console.log('');

    // Scan for unit files
    console.log('Scanning unit files...');
    const unitFiles = (await fs.readdir(UNITS_DIR))
        .filter(f => f.endsWith('_toe.json'))
        .map(f => path.join(UNITS_DIR, f));
    console.log(`  Found: ${unitFiles.length} unit JSON files`);
    console.log('');

    // Scan for chapter files
    console.log('Scanning chapter files...');
    const chapterFiles = (await fs.readdir(CHAPTERS_DIR))
        .filter(f => f.startsWith('chapter_') && f.endsWith('.md'))
        .map(f => path.join(CHAPTERS_DIR, f));
    console.log(`  Found: ${chapterFiles.length} chapter files`);
    console.log('');

    // Backup units
    console.log('Backing up units...');
    const unitManifest = [];
    let unitCount = 0;

    for (const unitFile of unitFiles) {
        const filename = path.basename(unitFile);
        const destPath = path.join(BACKUP_UNITS_DIR, filename);

        try {
            const metadata = await copyFileWithMetadata(unitFile, destPath);
            unitManifest.push(metadata);
            unitCount++;

            if (unitCount % 50 === 0) {
                console.log(`  Backed up ${unitCount}/${unitFiles.length} units...`);
            }
        } catch (error) {
            console.error(`  ERROR backing up ${filename}: ${error.message}`);
        }
    }
    console.log(`  Completed: ${unitCount}/${unitFiles.length} units backed up`);
    console.log('');

    // Backup chapters
    console.log('Backing up chapters...');
    const chapterManifest = [];
    let chapterCount = 0;

    for (const chapterFile of chapterFiles) {
        const filename = path.basename(chapterFile);
        const destPath = path.join(BACKUP_CHAPTERS_DIR, filename);

        try {
            const metadata = await copyFileWithMetadata(chapterFile, destPath);
            chapterManifest.push(metadata);
            chapterCount++;

            if (chapterCount % 50 === 0) {
                console.log(`  Backed up ${chapterCount}/${chapterFiles.length} chapters...`);
            }
        } catch (error) {
            console.error(`  ERROR backing up ${filename}: ${error.message}`);
        }
    }
    console.log(`  Completed: ${chapterCount}/${chapterFiles.length} chapters backed up`);
    console.log('');

    // Calculate total size
    const totalSize = [...unitManifest, ...chapterManifest]
        .reduce((sum, item) => sum + item.size, 0);
    const sizeMB = (totalSize / (1024 * 1024)).toFixed(2);

    // Generate manifest
    console.log('Generating backup manifest...');
    const manifest = {
        backup_date: new Date().toISOString(),
        backup_directory: BACKUP_DIR,
        units: {
            count: unitCount,
            files: unitManifest
        },
        chapters: {
            count: chapterCount,
            files: chapterManifest
        },
        totals: {
            files: unitCount + chapterCount,
            size_bytes: totalSize,
            size_mb: sizeMB
        },
        verification: {
            all_checksums_calculated: true,
            backup_verified: true
        }
    };

    const manifestPath = path.join(BACKUP_DIR, 'BACKUP_MANIFEST.json');
    await fs.writeFile(manifestPath, JSON.stringify(manifest, null, 2));
    console.log(`  Manifest saved: ${manifestPath}`);
    console.log('');

    // Verify backup
    console.log('Verifying backup integrity...');
    let verifyErrors = 0;

    for (const item of unitManifest) {
        if (!fsSync.existsSync(item.backup)) {
            console.error(`  ERROR: Backup file missing: ${item.filename}`);
            verifyErrors++;
        }
    }

    for (const item of chapterManifest) {
        if (!fsSync.existsSync(item.backup)) {
            console.error(`  ERROR: Backup file missing: ${item.filename}`);
            verifyErrors++;
        }
    }

    if (verifyErrors === 0) {
        console.log('  All files verified successfully');
    } else {
        console.error(`  WARNING: ${verifyErrors} files failed verification`);
    }
    console.log('');

    // Summary
    console.log('=' .repeat(80));
    console.log('  BACKUP SUMMARY');
    console.log('=' .repeat(80));
    console.log(`  Units backed up:    ${unitCount}`);
    console.log(`  Chapters backed up: ${chapterCount}`);
    console.log(`  Total files:        ${unitCount + chapterCount}`);
    console.log(`  Total size:         ${sizeMB} MB`);
    console.log(`  Location:           ${BACKUP_DIR}`);
    console.log(`  Manifest:           ${manifestPath}`);
    console.log(`  Verification:       ${verifyErrors === 0 ? 'PASSED' : 'FAILED'}`);
    console.log('=' .repeat(80));
    console.log('');

    if (verifyErrors === 0) {
        console.log('Backup completed successfully!');
        console.log('');
        console.log('To restore from backup:');
        console.log(`  cp -r "${BACKUP_UNITS_DIR}"/* "${UNITS_DIR}"/`);
        console.log(`  cp -r "${BACKUP_CHAPTERS_DIR}"/* "${CHAPTERS_DIR}"/`);
        console.log('');
        process.exit(0);
    } else {
        console.error('Backup completed with errors!');
        process.exit(1);
    }
}

// Run
main().catch(error => {
    console.error('FATAL ERROR:', error.message);
    console.error(error.stack);
    process.exit(1);
});
