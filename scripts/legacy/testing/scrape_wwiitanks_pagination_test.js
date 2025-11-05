/**
 * WWII Tanks UK Scraper - Pagination Test
 * Tests pagination fix with Germany AFVs only (should get all 204 vehicles)
 *
 * Usage: node scripts/scrape_wwiitanks_pagination_test.js
 */

const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');

const OUTPUT_DIR = path.join(__dirname, '..', 'data', 'output', 'afv_data', 'wwiitanks');

/**
 * Extract vehicle list from country summary page WITH PAGINATION
 */
async function extractVehicleListWithPagination(page, url, type = 'afv') {
  console.log(`Navigating to ${url}...`);
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
  await page.waitForTimeout(2000);

  // Check pagination and get offset values
  const paginationInfo = await page.evaluate(() => {
    const dropdown = document.querySelector('select#PAGER_PG1');
    if (dropdown) {
      const offsets = Array.from(dropdown.options).map(opt => opt.value);
      return {
        hasPagination: true,
        totalPages: dropdown.options.length,
        offsets: offsets  // e.g., ['0', '30', '60', '90', ...]
      };
    }
    return { hasPagination: false, totalPages: 1, offsets: ['0'] };
  });

  console.log(`  Pagination: ${paginationInfo.hasPagination ? `${paginationInfo.totalPages} pages` : 'single page'}`);

  let allVehicles = [];

  // Loop through all pages using correct offset values
  for (let pageNum = 0; pageNum < paginationInfo.totalPages; pageNum++) {
    if (pageNum > 0) {
      console.log(`  Loading page ${pageNum + 1}/${paginationInfo.totalPages}...`);

      // Navigate to next page using the offset value
      const offset = paginationInfo.offsets[pageNum];
      await page.evaluate((offsetValue) => {
        const dropdown = document.querySelector('select#PAGER_PG1');
        const hiddenInput = document.querySelector('input[name="PAGER_PG1"]');
        if (dropdown && hiddenInput) {
          dropdown.value = offsetValue;
          hiddenInput.value = offsetValue;
          const form = document.getElementById('PG1');
          if (form) {
            form.submit();
          }
        }
      }, offset);

      // Wait for page reload
      await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 60000 });
      await page.waitForTimeout(2000);
    }

    // Extract vehicles from current page
    const vehiclesOnPage = await page.evaluate((vehicleType) => {
      const results = [];
      const linkPattern = vehicleType === 'gun' ? 'Gun_Data.php?I=' : 'Tank_Data.php?I=';
      const allLinks = document.querySelectorAll(`a[href*="${linkPattern}"]`);

      allLinks.forEach(link => {
        const text = link.textContent.trim();
        const href = link.href;

        if (href && text && text.length > 3 && text.length < 200 && !text.includes('flag')) {
          results.push({
            name: text,
            href: href
          });
        }
      });

      // Remove duplicates
      const unique = [];
      const seen = new Set();
      results.forEach(item => {
        if (!seen.has(item.href)) {
          seen.add(item.href);
          unique.push(item);
        }
      });

      return unique;
    }, type);

    console.log(`  Page ${pageNum + 1}: Found ${vehiclesOnPage.length} vehicles`);
    allVehicles.push(...vehiclesOnPage);
  }

  console.log(`  Total found: ${allVehicles.length} vehicles`);

  // Final deduplication
  const uniqueVehicles = [];
  const seen = new Set();
  allVehicles.forEach(item => {
    if (!seen.has(item.href)) {
      seen.add(item.href);
      uniqueVehicles.push(item);
    }
  });

  return uniqueVehicles;
}

/**
 * Test pagination with Germany AFVs
 */
async function testPagination() {
  console.log('WWII Tanks UK Pagination Test');
  console.log('==============================\n');
  console.log('Testing with Germany AFVs (expected: 204 vehicles)\n');

  // Ensure output directory exists
  await fs.mkdir(OUTPUT_DIR, { recursive: true });

  // Launch browser
  console.log('Launching browser...');
  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: { width: 1400, height: 900 }
  });

  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');

  try {
    // Scrape Germany AFVs with pagination
    const url = 'https://wwiitanks.co.uk/FORM-Tank_Data-Summary.php?C=276';
    const vehicleList = await extractVehicleListWithPagination(page, url, 'afv');

    // Save results
    const outputFile = path.join(OUTPUT_DIR, 'pagination_test_germany_afvs.json');
    await fs.writeFile(outputFile, JSON.stringify(vehicleList, null, 2));

    console.log(`\n=== Test Results ===`);
    console.log(`Expected: 204 vehicles`);
    console.log(`Found: ${vehicleList.length} vehicles`);
    console.log(`Status: ${vehicleList.length === 204 ? '✅ SUCCESS' : vehicleList.length > 30 ? '⚠️ PARTIAL (but improved!)' : '❌ FAILED (no improvement)'}`);
    console.log(`Output saved to: ${outputFile}`);

    // Show first few vehicles
    if (vehicleList.length > 0) {
      console.log(`\nFirst 5 vehicles:`);
      vehicleList.slice(0, 5).forEach((v, i) => {
        console.log(`  ${i + 1}. ${v.name}`);
      });

      if (vehicleList.length > 5) {
        console.log(`\nLast 5 vehicles:`);
        vehicleList.slice(-5).forEach((v, i) => {
          console.log(`  ${vehicleList.length - 4 + i}. ${v.name}`);
        });
      }
    }

  } catch (error) {
    console.error('Test failed:', error);
  } finally {
    await browser.close();
    console.log('\nBrowser closed');
  }
}

// Run test
if (require.main === module) {
  testPagination().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

module.exports = { testPagination };
