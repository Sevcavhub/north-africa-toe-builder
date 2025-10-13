const fs = require('fs');
const path = require('path');

// Find all JSON files in autonomous session folders
const outputDir = 'data/output';
const sessions = fs.readdirSync(outputDir).filter(d => d.startsWith('autonomous'));

const jsonFiles = [];
const chapterFiles = [];

// Scan all session folders for units and chapters
sessions.forEach(session => {
  const unitsDir = path.join(outputDir, session, 'units');
  const chaptersDir = path.join(outputDir, session, 'chapters');
  const northAfricaBookDir = path.join(outputDir, session, 'north_africa_book', 'src');

  if (fs.existsSync(unitsDir)) {
    const files = fs.readdirSync(unitsDir);
    files.forEach(f => {
      if (f.endsWith('_toe.json')) {
        jsonFiles.push({
          session,
          file: f,
          path: path.join(unitsDir, f),
          unit: f.replace('_toe.json', '')
        });
      }
    });
  }

  // Check for chapters in chapters/ directory
  if (fs.existsSync(chaptersDir)) {
    const files = fs.readdirSync(chaptersDir);
    files.forEach(f => {
      if (f.endsWith('.md') && f.startsWith('chapter_')) {
        chapterFiles.push(f);
      }
    });
  }

  // Check for chapters in north_africa_book/src/ directory
  if (fs.existsSync(northAfricaBookDir)) {
    const files = fs.readdirSync(northAfricaBookDir);
    files.forEach(f => {
      if (f.endsWith('.md') && f.startsWith('chapter_')) {
        chapterFiles.push(f);
      }
    });
  }

  // Check for standalone chapter files in session root
  const sessionPath = path.join(outputDir, session);
  if (fs.existsSync(sessionPath)) {
    const files = fs.readdirSync(sessionPath);
    files.forEach(f => {
      if (f.endsWith('.md') && f.startsWith('chapter_')) {
        chapterFiles.push(f);
      }
    });
  }
});

// Deduplicate JSON files (keep most recent)
const uniqueUnits = new Map();
jsonFiles.forEach(entry => {
  if (!uniqueUnits.has(entry.unit) || entry.session > uniqueUnits.get(entry.unit).session) {
    uniqueUnits.set(entry.unit, entry);
  }
});

console.log(`Total unique JSON files: ${uniqueUnits.size}`);
console.log(`Total chapter files found: ${chapterFiles.length}`);

// Find units missing chapters
const missing = [];
uniqueUnits.forEach((entry, unit) => {
  // Check if any chapter file matches this unit
  const hasChapter = chapterFiles.some(chap => {
    const chapUnit = chap.replace('chapter_', '').replace('.md', '');
    return chapUnit === unit || chap.includes(unit.replace(/_/g, '_').substring(0, 20));
  });

  if (!hasChapter) {
    missing.push(entry);
  }
});

console.log(`\nUnits missing chapters: ${missing.length}\n`);

// Show first 20 missing
console.log('First 20 units missing chapters:');
missing.slice(0, 20).forEach((entry, i) => {
  console.log(`  ${i+1}. ${entry.unit}`);
  console.log(`     Session: ${entry.session}`);
});

// Save full list
fs.writeFileSync('temp_missing_chapters.json', JSON.stringify(missing, null, 2));
console.log(`\nFull list saved to: temp_missing_chapters.json`);
