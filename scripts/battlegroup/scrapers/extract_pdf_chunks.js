#!/usr/bin/env node

/**
 * Extract large PDF files in manageable chunks
 *
 * Usage:
 *   node scripts/extract_pdf_chunks.js "path/to/file.pdf" --chunk-size 20
 *   node scripts/extract_pdf_chunks.js "path/to/file.pdf" --pages 1-50
 */

const fs = require('fs').promises;
const fssync = require('fs');
const path = require('path');
const PDFParser = require('pdf2json');

// Parse command line arguments
const args = process.argv.slice(2);
const pdfPath = args.find(arg => !arg.startsWith('--'));
const chunkSizeArg = args.find(arg => arg.startsWith('--chunk-size'));
const pagesArg = args.find(arg => arg.startsWith('--pages'));

const CHUNK_SIZE = chunkSizeArg ? parseInt(chunkSizeArg.split('=')[1]) : 20;
const OUTPUT_DIR = path.join(__dirname, '../data/output/pdf_extracts');

async function ensureOutputDir() {
  try {
    await fs.mkdir(OUTPUT_DIR, { recursive: true });
  } catch (err) {
    // Directory might already exist
  }
}

async function extractPdfInChunks(pdfFilePath) {
  return new Promise((resolve, reject) => {
    console.log(`\n📄 Extracting PDF: ${path.basename(pdfFilePath)}`);
    console.log(`📦 Chunk size: ${CHUNK_SIZE} pages\n`);

    const pdfParser = new PDFParser();

    pdfParser.on('pdfParser_dataError', errData => {
      console.error('❌ Parse error:', errData.parserError);
      reject(errData.parserError);
    });

    pdfParser.on('pdfParser_dataReady', async pdfData => {
      try {
        const totalPages = pdfData.Pages.length;
        console.log(`📊 Total pages: ${totalPages}`);
        console.log(`📁 Output directory: ${OUTPUT_DIR}\n`);

        // Determine page range
        let startPage = 1;
        let endPage = totalPages;

        if (pagesArg) {
          const range = pagesArg.split('=')[1].split('-');
          startPage = parseInt(range[0]);
          endPage = parseInt(range[1]);
          console.log(`🎯 Extracting pages ${startPage}-${endPage}\n`);
        }

        // Create base filename for chunks
        const baseName = path.basename(pdfFilePath, '.pdf');

        // Process in chunks
        let currentPage = startPage;

        while (currentPage <= endPage) {
          const chunkStart = currentPage;
          const chunkEnd = Math.min(currentPage + CHUNK_SIZE - 1, endPage);

          console.log(`⚙️  Processing pages ${chunkStart}-${chunkEnd}...`);

          try {
            // Extract pages for this chunk (0-indexed)
            const chunkPages = pdfData.Pages.slice(chunkStart - 1, chunkEnd);

            let chunkText = '';
            chunkPages.forEach((page, pageIdx) => {
              const pageNum = chunkStart + pageIdx;
              chunkText += `\n${"=".repeat(70)}\nPAGE ${pageNum}\n${"=".repeat(70)}\n\n`;

              // Extract text from all text items on the page
              if (page.Texts && page.Texts.length > 0) {
                let pageText = '';
                page.Texts.forEach(text => {
                  if (text.R && text.R.length > 0) {
                    text.R.forEach(run => {
                      if (run.T) {
                        // Decode URI-encoded text
                        pageText += decodeURIComponent(run.T) + ' ';
                      }
                    });
                  }
                });
                chunkText += pageText.trim() + '\n';
              } else {
                chunkText += '[No text content found - may be image-based page]\n';
              }
            });

            // Save chunk to file
            const outputFileName = `${baseName}_pages_${chunkStart}-${chunkEnd}.txt`;
            const outputPath = path.join(OUTPUT_DIR, outputFileName);

            const header = `${"=".repeat(80)}
PDF Extract: ${path.basename(pdfFilePath)}
Pages: ${chunkStart}-${chunkEnd} of ${totalPages}
Extracted: ${new Date().toISOString()}
${"=".repeat(80)}

`;

            await fs.writeFile(outputPath, header + chunkText, 'utf-8');

            console.log(`   ✅ Saved: ${outputFileName} (${chunkText.length} chars)`);

          } catch (err) {
            console.error(`   ❌ Error processing pages ${chunkStart}-${chunkEnd}:`, err.message);
          }

          currentPage = chunkEnd + 1;
        }

        console.log(`\n✨ Extraction complete!`);
        console.log(`📂 Files saved to: ${OUTPUT_DIR}`);
        resolve();

      } catch (err) {
        reject(err);
      }
    });

    // Load PDF file
    pdfParser.loadPDF(pdfFilePath);
  });
}

// Main execution
async function main() {
  if (!pdfPath) {
    console.error('❌ Error: Please provide a PDF file path');
    console.log('\nUsage:');
    console.log('  node scripts/extract_pdf_chunks.js "path/to/file.pdf"');
    console.log('  node scripts/extract_pdf_chunks.js "path/to/file.pdf" --chunk-size=30');
    console.log('  node scripts/extract_pdf_chunks.js "path/to/file.pdf" --pages=1-50');
    process.exit(1);
  }

  try {
    await ensureOutputDir();
    await extractPdfInChunks(pdfPath);
  } catch (err) {
    console.error('❌ Fatal error:', err.message);
    console.error(err.stack);
    process.exit(1);
  }
}

main();
