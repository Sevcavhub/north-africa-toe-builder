#!/usr/bin/env node

/**
 * PDF Text Extraction Script
 *
 * Extracts text from PDF files and saves to both:
 * 1. Plain text file (.txt) - Full text for simple reading
 * 2. JSON file (.json) - Structured page-by-page data for research agents
 *
 * Usage:
 *   node scripts/extract_pdf_to_json.js <path-to-pdf>
 *
 * Example:
 *   node scripts/extract_pdf_to_json.js "Resource Documents/British_PRIMARY_SOURCES/682349763-Battle-Orders-028-Desert-Rats-British-8th-Army-in-North-Africa-1941-43.pdf"
 */

const fs = require('fs');
const path = require('path');
const pdf = require('pdf-parse');

/**
 * Extract text from a PDF file
 * @param {string} pdfPath - Path to the PDF file
 * @returns {Promise<Object>} - Extracted data with text, pages, info, etc.
 */
async function extractPdfText(pdfPath) {
  console.log(`\n📄 Extracting text from: ${pdfPath}`);

  // Read the PDF file as a buffer
  const dataBuffer = fs.readFileSync(pdfPath);

  // Parse PDF using pdf-parse v1.x simple API
  let data;
  try {
    // pdf-parse v1.x is a simple function that takes a buffer
    data = await pdf(dataBuffer);
  } catch (error) {
    console.error('Error parsing PDF:', error.message);
    throw error;
  }

  console.log(`✅ Successfully extracted ${data.numpages} pages`);
  console.log(`📊 Total text length: ${data.text.length} characters\n`);

  return data;
}

/**
 * Save extracted data to files
 * @param {Object} data - Extracted PDF data
 * @param {string} pdfPath - Original PDF path
 */
function saveExtractedData(data, pdfPath) {
  const pdfDir = path.dirname(pdfPath);
  const pdfBaseName = path.basename(pdfPath, '.pdf');

  // Create output paths
  const txtPath = path.join(pdfDir, `${pdfBaseName}_full_text.txt`);
  const jsonPath = path.join(pdfDir, `${pdfBaseName}_structured.json`);

  // Save full text
  fs.writeFileSync(txtPath, data.text, 'utf8');
  console.log(`✅ Saved full text to: ${txtPath}`);

  // Create structured JSON
  const structuredData = {
    metadata: {
      filename: path.basename(pdfPath),
      extracted_date: new Date().toISOString(),
      total_pages: data.numpages,
      total_characters: data.text.length,
      pdf_info: data.info || {}
    },
    full_text: data.text,
    // Split text into estimated pages (PDF-parse doesn't provide page-by-page in all cases)
    // We'll save the full text and let the research agent work with it
    pages_info: {
      note: "Full text extracted - page boundaries may not be precise",
      total_pages: data.numpages
    }
  };

  fs.writeFileSync(jsonPath, JSON.stringify(structuredData, null, 2), 'utf8');
  console.log(`✅ Saved structured JSON to: ${jsonPath}\n`);

  // Print summary
  console.log(`📊 EXTRACTION SUMMARY:`);
  console.log(`   - Total pages: ${data.numpages}`);
  console.log(`   - Total characters: ${data.text.length.toLocaleString()}`);
  console.log(`   - Full text file: ${path.basename(txtPath)}`);
  console.log(`   - Structured JSON: ${path.basename(jsonPath)}`);
  console.log(`\n✨ Ready for research agent processing!\n`);

  return { txtPath, jsonPath };
}

/**
 * Main execution
 */
async function main() {
  // Get PDF path from command line arguments
  const pdfPath = process.argv[2];

  if (!pdfPath) {
    console.error(`\n❌ ERROR: No PDF path provided\n`);
    console.log(`Usage: node scripts/extract_pdf_to_json.js <path-to-pdf>\n`);
    console.log(`Example:`);
    console.log(`  node scripts/extract_pdf_to_json.js "Resource Documents/British_PRIMARY_SOURCES/battle-orders.pdf"\n`);
    process.exit(1);
  }

  // Check if file exists
  if (!fs.existsSync(pdfPath)) {
    console.error(`\n❌ ERROR: PDF file not found: ${pdfPath}\n`);
    process.exit(1);
  }

  try {
    // Extract PDF text
    const data = await extractPdfText(pdfPath);

    // Save to files
    const outputPaths = saveExtractedData(data, pdfPath);

    console.log(`\n🎉 SUCCESS! PDF extraction complete.`);
    console.log(`\n📝 Next steps:`);
    console.log(`   1. Use the JSON file for research agent processing`);
    console.log(`   2. Update primary source documentation`);
    console.log(`   3. Reference the structured data in agent prompts\n`);

  } catch (error) {
    console.error(`\n❌ ERROR during PDF extraction:`, error);
    console.error(`\nDebug info: pdf-parse type: ${typeof pdf}, keys: ${Object.keys(pdf).join(', ')}`);
    process.exit(1);
  }
}

// Run main function
main();
