const fs = require('fs');
const path = require('path');

const unitsDir = path.join(__dirname, '../data/output/units');
const chaptersDir = path.join(__dirname, '../data/output/chapters');

// Get all unit files
const unitFiles = fs.readdirSync(unitsDir)
  .filter(f => f.endsWith('_toe.json'))
  .map(f => f.replace('_toe.json', ''));

// Get all chapter files
const chapterFiles = fs.readdirSync(chaptersDir)
  .filter(f => f.endsWith('.md'))
  .map(f => f.replace('chapter_', '').replace('.md', ''));

// Find missing chapters
const missing = unitFiles.filter(u => !chapterFiles.includes(u));

console.log(`\n📚 MDBOOK CHAPTER STATUS\n`);
console.log(`Total Units: ${unitFiles.length}`);
console.log(`Chapters Found: ${chapterFiles.length}`);
console.log(`Missing Chapters: ${missing.length}\n`);

if (missing.length > 0) {
  console.log(`Missing chapters:\n`);
  missing.sort().forEach((u, i) => {
    console.log(`${(i + 1).toString().padStart(2)}. ${u}`);
  });
}
