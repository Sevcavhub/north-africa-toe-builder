/**
 * WWII Tanks UK Scraper - Test Script
 * Tests scraping for a single country (Germany AFVs only)
 *
 * Usage: node scripts/scrape_wwiitanks_test.js
 */

const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');

const OUTPUT_DIR = path.join(__dirname, '..', 'data', 'output', 'afv_data', 'wwiitanks');

/**
 * Extract vehicle list from country summary page
 */
async function extractVehicleList(page, url) {
  console.log(`Navigating to ${url}...`);
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
  await page.waitForTimeout(2000);

  const vehicles = await page.evaluate(() => {
    const results = [];

    // Find all links to Tank_Data.php?I= (these are the vehicle detail pages)
    const allLinks = document.querySelectorAll('a[href*="Tank_Data.php?I="]');

    allLinks.forEach(link => {
      const text = link.textContent.trim();
      const href = link.getAttribute('href');

      // Filter to get vehicle name links (not flag/image links)
      if (href && text &&
          text.length > 3 &&
          text.length < 200 &&
          !text.includes('flag') &&
          !text.toLowerCase().includes('germany')) {

        const fullHref = href.startsWith('http') ? href : `https://wwiitanks.co.uk/${href}`;

        results.push({
          name: text,
          href: fullHref
        });
      }
    });

    // Remove duplicates based on href
    const unique = [];
    const seen = new Set();
    results.forEach(item => {
      if (!seen.has(item.href)) {
        seen.add(item.href);
        unique.push(item);
      }
    });

    return unique;
  });

  console.log(`Found ${vehicles.length} vehicles`);
  return vehicles;
}

/**
 * Extract vehicle details
 */
async function extractVehicleDetails(page, url, vehicleName) {
  console.log(`  Extracting: ${vehicleName}`);

  try {
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
    await page.waitForTimeout(1500);

    const specs = await page.evaluate(() => {
      const data = {};

      // Find all table cells with label-value pairs
      const tables = document.querySelectorAll('table');

      tables.forEach(table => {
        const rows = table.querySelectorAll('tr');
        rows.forEach(row => {
          const cells = row.querySelectorAll('td');
          if (cells.length >= 2) {
            const label = cells[0].textContent.trim();
            const value = cells[1].textContent.trim();

            if (label && value && label.length > 0 && label.length < 100) {
              // Clean up the label to use as key
              const key = label
                .toLowerCase()
                .replace(/[^a-z0-9]+/g, '_')
                .replace(/^_+|_+$/g, '');

              if (key && key.length > 0) {
                data[key] = value;
              }
            }
          }
        });
      });

      return data;
    });

    return specs;
  } catch (error) {
    console.error(`    Error: ${error.message}`);
    return null;
  }
}

/**
 * Test scrape - Germany AFVs only (first 5)
 */
async function testScrape() {
  console.log('WWII Tanks UK Scraper - TEST MODE');
  console.log('=================================\n');
  console.log('Testing with Germany AFVs (first 5 vehicles)\n');

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
    // Scrape Germany AFVs
    const url = 'https://wwiitanks.co.uk/FORM-Tank_Data-Summary.php?C=276';
    const vehicleList = await extractVehicleList(page, url);

    // Take only first 5 for testing
    const testVehicles = vehicleList.slice(0, 5);
    console.log(`\nTesting with ${testVehicles.length} vehicles:\n`);

    const results = [];

    for (let i = 0; i < testVehicles.length; i++) {
      const vehicle = testVehicles[i];
      console.log(`[${i + 1}/${testVehicles.length}] ${vehicle.name}`);

      const details = await extractVehicleDetails(page, vehicle.href, vehicle.name);

      if (details) {
        // Extract ID from URL for unique identifier
        const urlMatch = vehicle.href.match(/Tank_Data\.php\?I=(\d+)/);
        const vehicleId = urlMatch ? urlMatch[1] : `unknown_${i}`;

        results.push({
          wwiitanks_id: `wwiitanks_germany_afv_${vehicleId}`,
          source: 'wwiitanks.co.uk',
          source_url: vehicle.href,
          scraped_at: new Date().toISOString(),
          country: 'germany',
          vehicle_name: vehicle.name,
          ...details
        });
      }

      // Wait between requests
      await page.waitForTimeout(1000);
    }

    // Save test results
    const outputFile = path.join(OUTPUT_DIR, 'test_germany_afvs.json');
    await fs.writeFile(outputFile, JSON.stringify(results, null, 2));

    console.log(`\n=== Test Results ===`);
    console.log(`Scraped ${results.length} vehicles successfully`);
    console.log(`Output saved to: ${outputFile}`);

    // Show sample data
    if (results.length > 0) {
      console.log(`\nSample data (first vehicle):`);
      console.log(JSON.stringify(results[0], null, 2));
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
  testScrape().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

module.exports = { testScrape };
