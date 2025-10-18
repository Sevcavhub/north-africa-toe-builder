#!/usr/bin/env node

/**
 * Parse OnWar.com references from HTML table and create sources JSON
 */

const fs = require('fs');
const path = require('path');

const HTML_FILE = path.join(__dirname, '..', 'temp_references.html');
const OUTPUT_FILE = path.join(__dirname, '..', 'sources', 'onwar_references.json');

// Read HTML file
const html = fs.readFileSync(HTML_FILE, 'utf-8');

// Extract all table rows
const references = [];
const rowPattern = /<tr>[\s\S]*?<td class="code">\[([^\]]+)\]<\/td>[\s\S]*?<td>(.*?)<\/td>[\s\S]*?<\/tr>/g;

let match;
while ((match = rowPattern.exec(html)) !== null) {
  const code = match[1].trim();
  let citation = match[2]
    .replace(/<em>/g, '')
    .replace(/<\/em>/g, '')
    .replace(/<a[^>]*>/g, '')
    .replace(/<\/a>/g, '')
    .replace(/&quot;/g, '"')
    .replace(/&amp;/g, '&')
    .replace(/&nbsp;/g, ' ')
    .trim();

  // Extract author, title, publisher, year from citation
  const parsed = parseCitation(citation);

  references.push({
    code: code,
    full_citation: citation,
    ...parsed
  });
}

console.log(`Extracted ${references.length} references from OnWar.com`);

// Save to JSON file
const output = {
  source: "OnWar.com - Tanks of World War II",
  url: "https://www.onwar.com/wwii/tanks/references.html",
  extracted_date: new Date().toISOString().split('T')[0],
  description: "Bibliography of primary and secondary sources used by OnWar.com for AFV technical specifications",
  total_references: references.length,
  confidence_rating: 80,
  usage_notes: [
    "These sources were used by OnWar.com to compile AFV specifications",
    "Not all sources have equal weight in their determinations",
    "Many sources are out-of-print or difficult to obtain",
    "Key sources: EGT (Encyclopedia of German Tanks), ST (Soviet Tanks), BAT (British and American Tanks)",
    "Includes primary documents (Tank Data from Aberdeen Proving Grounds) and secondary histories"
  ],
  references: references
};

fs.writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2));
console.log(`Saved to ${OUTPUT_FILE}`);

/**
 * Parse citation string into components
 */
function parseCitation(citation) {
  const result = {
    author: '',
    title: '',
    publisher: '',
    year: '',
    type: 'book'
  };

  // Detect type
  if (citation.includes('Military Modelling') || citation.includes('FineScale Modeler') || citation.includes('AFV News')) {
    result.type = 'article';
  } else if (citation.includes('Squadron/Signal') || citation.includes('Osprey')) {
    result.type = 'monograph';
  } else if (citation.includes('HMSO') || citation.includes('War Department')) {
    result.type = 'official_document';
  }

  // Extract year (4-digit number or 19??)
  const yearMatch = citation.match(/\b(19\d{2}|19\?\?)\b/);
  if (yearMatch) {
    result.year = yearMatch[1];
  }

  // Extract author (text before first comma or "ed.")
  const authorMatch = citation.match(/^([^,]+?)(?:,|\(ed\.\))/);
  if (authorMatch) {
    result.author = authorMatch[1].trim();
  }

  // Extract publisher location and name
  const publisherMatch = citation.match(/,\s*([A-Z]{2}):\s*([^,]+),/);
  if (publisherMatch) {
    result.publisher = `${publisherMatch[2].trim()}, ${publisherMatch[1]}`;
  }

  // Title is harder to extract reliably, so we'll leave the full citation
  result.title = citation.split(',')[0] || '';

  return result;
}
