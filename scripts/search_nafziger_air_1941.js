const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const NAFZIGER_DIR = 'D:/north-africa-toe-builder/Resource Documents/Nafziger Collection/WWII/1941-1942/Pt_I_1941-1942';

// Quarter definitions
const QUARTERS = {
  'Q1': { prefixes: ['941a', '941b', '941c'], label: '1941-Q1 (Jan-Mar)' },
  'Q3': { prefixes: ['941g', '941h', '941i'], label: '1941-Q3 (Jul-Sep)' },
  'Q4': { prefixes: ['941j', '941k', '941l'], label: '1941-Q4 (Oct-Dec)' }
};

// North Africa keywords
const NA_KEYWORDS = [
  'libya', 'egypt', 'tobruk', 'benghazi', 'western desert',
  'afrika', 'crusader', 'tripoli', 'cyrenaica', 'el alamein',
  'sidi barrani', 'sollum', 'bardia', 'derna', 'gazala'
];

// Air unit patterns
const AIR_PATTERNS = {
  german: [
    /\b(JG|ZG|StG|KG|LG)\s*\d+/gi,  // Jagdgeschwader, Kampfgeschwader, etc.
    /\bGeschwader\b/gi,
    /\bStaffel\b/gi,
    /\bFliegerkorps\b/gi,
    /Luftwaffe/gi
  ],
  italian: [
    /\b\d+[°º]\s*(Stormo|Gruppo|Squadriglia)/gi,
    /Regia\s+Aeronautica/gi,
    /\bStormo\b/gi,
    /\bGruppo\s+(Bombardamento|Caccia|Assalto)/gi
  ],
  british: [
    /\bNo\.\s*\d+\s*Squadron/gi,
    /\b\d+\s*Squadron\s*(RAF|SAAF|RAAF)/gi,
    /\bRAF\b/gi,
    /Desert\s+Air\s+Force/gi,
    /\bSAAF\b/gi  // South African Air Force
  ]
};

// Strength indicators
const STRENGTH_PATTERNS = [
  /\b\d+\s*(aircraft|planes)/gi,
  /serviceable/gi,
  /on\s+strength/gi,
  /operational/gi,
  /available/gi
];

function getPDFsForQuarter(quarter) {
  const { prefixes } = QUARTERS[quarter];
  const allFiles = fs.readdirSync(NAFZIGER_DIR);

  return allFiles.filter(file => {
    if (!file.endsWith('.pdf')) return false;
    return prefixes.some(prefix => file.startsWith(prefix));
  });
}

function extractPDFText(pdfPath) {
  try {
    const output = execSync(`pdftotext "${pdfPath}" -`, {
      encoding: 'utf8',
      maxBuffer: 10 * 1024 * 1024,
      timeout: 30000
    });
    return output;
  } catch (error) {
    console.error(`Error extracting ${path.basename(pdfPath)}: ${error.message}`);
    return '';
  }
}

function detectNation(text) {
  const nations = [];

  if (AIR_PATTERNS.german.some(pattern => pattern.test(text))) {
    nations.push('german');
  }
  if (AIR_PATTERNS.italian.some(pattern => pattern.test(text))) {
    nations.push('italian');
  }
  if (AIR_PATTERNS.british.some(pattern => pattern.test(text))) {
    nations.push('british');
  }

  return nations;
}

function findAirUnits(text, nation) {
  const units = new Set();
  const patterns = AIR_PATTERNS[nation] || [];

  patterns.forEach(pattern => {
    const matches = text.match(pattern);
    if (matches) {
      matches.forEach(match => units.add(match.trim()));
    }
  });

  return Array.from(units);
}

function hasNorthAfricaKeywords(text) {
  const lowerText = text.toLowerCase();
  return NA_KEYWORDS.some(keyword => lowerText.includes(keyword));
}

function hasStrengthData(text) {
  return STRENGTH_PATTERNS.some(pattern => pattern.test(text));
}

function extractSampleText(text, units) {
  // Find context around first unit mention
  const firstUnit = units[0];
  if (!firstUnit) return '';

  const index = text.indexOf(firstUnit);
  if (index === -1) return '';

  const start = Math.max(0, index - 200);
  const end = Math.min(text.length, index + 400);

  return text.substring(start, end).replace(/\n+/g, ' ').trim();
}

console.log('='.repeat(80));
console.log('NAFZIGER COLLECTION AIR FORCES SEARCH - 1941 Q1/Q3/Q4');
console.log('='.repeat(80));
console.log('');

const results = {};

for (const [quarter, config] of Object.entries(QUARTERS)) {
  console.log(`\nSearching ${config.label}...`);
  console.log('-'.repeat(80));

  const pdfs = getPDFsForQuarter(quarter);
  console.log(`Found ${pdfs.length} PDFs with matching prefixes`);

  results[quarter] = [];
  let processed = 0;

  for (const filename of pdfs) {
    // Skip already processed Q2 file
    if (filename === '941gdmc.pdf') {
      console.log(`  Skipping ${filename} (already processed as 1941-Q2)`);
      continue;
    }

    const fullPath = path.join(NAFZIGER_DIR, filename);
    processed++;

    if (processed % 10 === 0) {
      console.log(`  Processed ${processed}/${pdfs.length} files...`);
    }

    const text = extractPDFText(fullPath);
    if (!text) continue;

    // Check for North Africa context
    const hasNA = hasNorthAfricaKeywords(text);
    if (!hasNA) continue;

    // Detect nations with air units
    const nations = detectNation(text);
    if (nations.length === 0) continue;

    // Extract air units for each nation
    const nationData = {};
    let hasAirUnits = false;

    nations.forEach(nation => {
      const units = findAirUnits(text, nation);
      if (units.length > 0) {
        hasAirUnits = true;
        nationData[nation] = {
          units: units,
          hasStrength: hasStrengthData(text),
          sampleText: extractSampleText(text, units)
        };
      }
    });

    if (hasAirUnits) {
      results[quarter].push({
        filename: filename,
        quarter: quarter,
        nations: nationData
      });

      console.log(`  ✓ ${filename} - Found air units: ${nations.join(', ')}`);
    }
  }

  console.log(`\n${config.label}: ${results[quarter].length} PDFs with air unit data`);
}

// Generate detailed report
console.log('\n');
console.log('='.repeat(80));
console.log('DETAILED FINDINGS');
console.log('='.repeat(80));

for (const [quarter, config] of Object.entries(QUARTERS)) {
  console.log(`\n\n## ${config.label}`);
  console.log(`Found ${results[quarter].length} PDFs with air unit data\n`);

  results[quarter].forEach((result, idx) => {
    console.log(`\n### ${idx + 1}. ${result.filename}`);
    console.log(`Quarter: ${result.quarter}`);

    Object.entries(result.nations).forEach(([nation, data]) => {
      console.log(`\n**Nation: ${nation}**`);
      console.log(`Units found: ${data.units.length}`);
      console.log(`Has strength data: ${data.hasStrength ? 'YES' : 'NO'}`);
      console.log(`\nUnits:`);
      data.units.slice(0, 10).forEach(unit => {
        console.log(`  - ${unit}`);
      });
      if (data.units.length > 10) {
        console.log(`  ... and ${data.units.length - 10} more`);
      }

      console.log(`\nSample text:`);
      console.log(`"${data.sampleText.substring(0, 300)}..."`);
    });

    console.log('\n' + '-'.repeat(80));
  });
}

// Summary statistics
console.log('\n\n');
console.log('='.repeat(80));
console.log('SUMMARY STATISTICS');
console.log('='.repeat(80));

let totalPDFs = 0;
const nationCounts = { german: 0, italian: 0, british: 0 };

Object.entries(results).forEach(([quarter, pdfs]) => {
  totalPDFs += pdfs.length;
  pdfs.forEach(pdf => {
    Object.keys(pdf.nations).forEach(nation => {
      nationCounts[nation]++;
    });
  });
});

console.log(`\nTotal PDFs with air unit data: ${totalPDFs}`);
console.log(`\nBy nation:`);
console.log(`  German (Luftwaffe): ${nationCounts.german} PDFs`);
console.log(`  Italian (Regia Aeronautica): ${nationCounts.italian} PDFs`);
console.log(`  British (RAF/Commonwealth): ${nationCounts.british} PDFs`);

console.log(`\nBy quarter:`);
Object.entries(QUARTERS).forEach(([quarter, config]) => {
  console.log(`  ${config.label}: ${results[quarter].length} PDFs`);
});

// Save results to JSON
const outputPath = 'D:/north-africa-toe-builder/data/output/nafziger_air_search_1941_q1_q3_q4.json';
fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
console.log(`\n\nResults saved to: ${outputPath}`);
