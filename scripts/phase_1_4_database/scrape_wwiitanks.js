/**
 * WWII Tanks UK Scraper
 * Scrapes AFV and Gun specifications from wwiitanks.co.uk
 *
 * Usage: node scripts/scrape_wwiitanks.js
 */

const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');

// Country codes from wwiitanks.co.uk
const COUNTRIES = {
  'Austria': { afv: 40, gun: 40 },
  'Belgium': { afv: null, gun: 56 },
  'Britain': { afv: 826, gun: 826 },
  'Canada': { afv: 124, gun: null },
  'Czechoslovakia': { afv: 203, gun: 203 },
  'Denmark': { afv: null, gun: 208 },
  'Finland': { afv: null, gun: 246 },
  'France': { afv: 250, gun: 250 },
  'Germany': { afv: 276, gun: 276 },
  'Hungary': { afv: 348, gun: 348 },
  'Italy': { afv: 380, gun: 380 },
  'Japan': { afv: 392, gun: 392 },
  'Netherlands': { afv: null, gun: 528 },
  'Poland': { afv: 616, gun: 616 },
  'Sweden': { afv: 752, gun: 752 },
  'Switzerland': { afv: null, gun: 756 },
  'USSR': { afv: 643, gun: 643 },
  'USA': { afv: 840, gun: 840 }
};

const OUTPUT_DIR = path.join(__dirname, '..', 'data', 'output', 'afv_data', 'wwiitanks');

/**
 * Extract vehicle/gun list from a country summary page (WITH PAGINATION)
 */
async function extractVehicleList(page, url, type = 'afv') {
  console.log(`Navigating to ${url}...`);
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });

  // Wait a bit for dynamic content
  await page.waitForTimeout(2000);

  // Check if pagination exists and get page offsets
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

      // Wait for page to reload
      await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 60000 });
      await page.waitForTimeout(2000);
    }

    // Extract vehicle names and links from current page
    const vehiclesOnPage = await page.evaluate((vehicleType) => {
      const results = [];

      // Look for AFV links: Tank_Data.php?I= or Gun links: Gun_Data.php?I=
      const linkPattern = vehicleType === 'gun' ? 'Gun_Data.php?I=' : 'Tank_Data.php?I=';
      const allLinks = document.querySelectorAll(`a[href*="${linkPattern}"]`);

      allLinks.forEach(link => {
        const text = link.textContent.trim();
        const href = link.href;

        // Filter to get vehicle/gun name links (not flag/image links)
        if (href && text &&
            text.length > 3 &&
            text.length < 200 &&
            !text.includes('flag')) {

          // Extract indicator information from the table row
          let row = link;
          for (let i = 0; i < 10; i++) {
            if (!row) break;
            if (row.tagName === 'TR') break;
            row = row.parentElement;
          }

          const indicators = {
            hasPhoto: false,
            hasScaleIllustration: false,
            hasVehicleHistory: false,
            hasWeaponDetails: false,
            hasArmourDetails: false
          };

          if (row && row.tagName === 'TR') {
            const imgs = row.querySelectorAll('img');
            imgs.forEach(img => {
              const title = img.getAttribute('title') || img.getAttribute('alt') || '';
              if (title.includes('Photo')) indicators.hasPhoto = true;
              if (title.includes('Scale')) indicators.hasScaleIllustration = true;
              if (title.includes('Vehicle') || title.includes('history') || title.includes('History')) indicators.hasVehicleHistory = true;
              if (title.includes('Weapon')) indicators.hasWeaponDetails = true;
              if (title.includes('Armour')) indicators.hasArmourDetails = true;
            });
          }

          results.push({
            name: text,
            href: href,
            indicators: indicators
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
    }, type);

    console.log(`  Page ${pageNum + 1}: Found ${vehiclesOnPage.length} vehicles/guns`);
    allVehicles.push(...vehiclesOnPage);
  }

  console.log(`  Total found: ${allVehicles.length} vehicles/guns`);

  // Final deduplication across all pages
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
 * Extract detailed specifications from a vehicle detail page
 */
async function extractVehicleDetails(page, url, vehicleName) {
  console.log(`  Extracting details for: ${vehicleName}`);

  try {
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
    await page.waitForTimeout(1000);

    // Extract all data from the specifications table
    const specs = await page.evaluate(() => {
      const data = {
        general_details: {},
        specifications: {},
        general_information: {}
      };

      // Find all tables with specifications
      const tables = document.querySelectorAll('table');

      for (let table of tables) {
        const rows = table.querySelectorAll('tr');
        for (let row of rows) {
          const cells = row.querySelectorAll('td');
          if (cells.length >= 2) {
            const label = cells[0].textContent.trim();
            const value = cells[1].textContent.trim();

            if (label && value) {
              // Categorize the data
              const key = label.toLowerCase().replace(/[^a-z0-9]/g, '_');

              // Determine which section this belongs to
              if (label.includes('Operational') || label.includes('Manufacturer') ||
                  label.includes('Production') || label.includes('Type')) {
                data.general_details[key] = value;
              } else if (label.includes('Length') || label.includes('Width') ||
                        label.includes('Height') || label.includes('Weight') ||
                        label.includes('Speed') || label.includes('Range') ||
                        label.includes('Engine') || label.includes('Armament')) {
                data.specifications[key] = value;
              } else {
                data.general_information[key] = value;
              }
            }
          }
        }
      }

      // Extract images
      const images = [];
      const imgs = document.querySelectorAll('img');
      imgs.forEach(img => {
        const src = img.src;
        const alt = img.alt;
        if (src && !src.includes('icon') && !src.includes('blank.gif') &&
            !src.includes('wwiitanks.gif') && alt) {
          images.push({ src, alt });
        }
      });

      return { ...data, images };
    });

    return specs;
  } catch (error) {
    console.error(`    Error extracting details for ${vehicleName}: ${error.message}`);
    return null;
  }
}

/**
 * Scrape AFVs for a specific country
 */
async function scrapeCountryAFVs(page, countryName, countryCode) {
  console.log(`\n=== Scraping AFVs for ${countryName} ===`);

  const url = `https://wwiitanks.co.uk/FORM-Tank_Data-Summary.php?C=${countryCode}`;
  const vehicleList = await extractVehicleList(page, url, 'afv');

  const results = [];

  for (let i = 0; i < vehicleList.length; i++) {
    const vehicle = vehicleList[i];
    console.log(`  [${i + 1}/${vehicleList.length}] ${vehicle.name}`);

    const details = await extractVehicleDetails(page, vehicle.href, vehicle.name);

    if (details) {
      // Extract ID from URL for unique identifier
      const urlMatch = vehicle.href.match(/Tank_Data\.php\?I=(\d+)/);
      const vehicleId = urlMatch ? urlMatch[1] : `unknown_${i}`;

      results.push({
        wwiitanks_id: `wwiitanks_${countryName.toLowerCase()}_afv_${vehicleId}`,
        source: 'wwiitanks.co.uk',
        source_url: vehicle.href,
        scraped_at: new Date().toISOString(),
        country: countryName.toLowerCase(),
        vehicle_name: vehicle.name,
        indicators: vehicle.indicators,
        ...details
      });
    }

    // Be polite - wait between requests
    await page.waitForTimeout(500 + Math.random() * 1000);
  }

  return results;
}

/**
 * Scrape Guns for a specific country
 */
async function scrapeCountryGuns(page, countryName, countryCode) {
  console.log(`\n=== Scraping Guns for ${countryName} ===`);

  const url = `https://wwiitanks.co.uk/FORM-Gun_Data-Summary.php?C=${countryCode}`;
  const gunList = await extractVehicleList(page, url, 'gun');

  const results = [];

  for (let i = 0; i < gunList.length; i++) {
    const gun = gunList[i];
    console.log(`  [${i + 1}/${gunList.length}] ${gun.name}`);

    const details = await extractVehicleDetails(page, gun.href, gun.name);

    if (details) {
      // Extract ID from URL for unique identifier
      const urlMatch = gun.href.match(/Gun_Data\.php\?I=(\d+)/);
      const gunId = urlMatch ? urlMatch[1] : `unknown_${i}`;

      results.push({
        wwiitanks_id: `wwiitanks_${countryName.toLowerCase()}_gun_${gunId}`,
        source: 'wwiitanks.co.uk',
        source_url: gun.href,
        scraped_at: new Date().toISOString(),
        country: countryName.toLowerCase(),
        gun_name: gun.name,
        indicators: gun.indicators,
        ...details
      });
    }

    // Be polite - wait between requests
    await page.waitForTimeout(500 + Math.random() * 1000);
  }

  return results;
}

/**
 * Main scraper function
 */
async function main() {
  console.log('WWII Tanks UK Scraper');
  console.log('=====================\n');

  // Ensure output directory exists
  await fs.mkdir(OUTPUT_DIR, { recursive: true });

  // Launch browser
  console.log('Launching browser...');
  const browser = await puppeteer.launch({
    headless: false, // Set to true for production
    defaultViewport: { width: 1400, height: 900 }
  });

  const page = await browser.newPage();

  // Set user agent to be polite
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');

  const allAFVs = [];
  const allGuns = [];

  // Scrape each country
  for (const [countryName, codes] of Object.entries(COUNTRIES)) {
    try {
      // Scrape AFVs
      if (codes.afv) {
        const afvs = await scrapeCountryAFVs(page, countryName, codes.afv);
        allAFVs.push(...afvs);

        // Save incremental results
        await fs.writeFile(
          path.join(OUTPUT_DIR, `${countryName.toLowerCase()}_afvs.json`),
          JSON.stringify(afvs, null, 2)
        );
      }

      // Scrape Guns
      if (codes.gun) {
        const guns = await scrapeCountryGuns(page, countryName, codes.gun);
        allGuns.push(...guns);

        // Save incremental results
        await fs.writeFile(
          path.join(OUTPUT_DIR, `${countryName.toLowerCase()}_guns.json`),
          JSON.stringify(guns, null, 2)
        );
      }
    } catch (error) {
      console.error(`Error scraping ${countryName}: ${error.message}`);
    }
  }

  // Save combined results
  console.log('\n=== Saving combined results ===');

  await fs.writeFile(
    path.join(OUTPUT_DIR, 'all_afvs.json'),
    JSON.stringify(allAFVs, null, 2)
  );
  console.log(`Saved ${allAFVs.length} AFVs to all_afvs.json`);

  await fs.writeFile(
    path.join(OUTPUT_DIR, 'all_guns.json'),
    JSON.stringify(allGuns, null, 2)
  );
  console.log(`Saved ${allGuns.length} guns to all_guns.json`);

  // Create CSV files
  if (allAFVs.length > 0) {
    const afvCSV = convertToCSV(allAFVs);
    await fs.writeFile(
      path.join(OUTPUT_DIR, 'all_afvs.csv'),
      afvCSV
    );
    console.log('Saved AFVs to all_afvs.csv');
  }

  if (allGuns.length > 0) {
    const gunCSV = convertToCSV(allGuns);
    await fs.writeFile(
      path.join(OUTPUT_DIR, 'all_guns.csv'),
      gunCSV
    );
    console.log('Saved guns to all_guns.csv');
  }

  await browser.close();
  console.log('\n=== Scraping complete! ===');
}

/**
 * Convert JSON array to CSV
 */
function convertToCSV(data) {
  if (data.length === 0) return '';

  // Flatten nested objects
  const flatData = data.map(item => {
    const flat = { ...item };

    // Flatten general_details
    if (item.general_details) {
      for (const [key, value] of Object.entries(item.general_details)) {
        flat[`general_${key}`] = value;
      }
      delete flat.general_details;
    }

    // Flatten specifications
    if (item.specifications) {
      for (const [key, value] of Object.entries(item.specifications)) {
        flat[`spec_${key}`] = value;
      }
      delete flat.specifications;
    }

    // Flatten general_information
    if (item.general_information) {
      for (const [key, value] of Object.entries(item.general_information)) {
        flat[`info_${key}`] = value;
      }
      delete flat.general_information;
    }

    // Convert indicators to string
    if (item.indicators) {
      flat.indicators = JSON.stringify(item.indicators);
    }

    // Convert images to count
    if (item.images) {
      flat.image_count = item.images.length;
      delete flat.images;
    }

    return flat;
  });

  // Get all unique headers
  const headers = new Set();
  flatData.forEach(item => {
    Object.keys(item).forEach(key => headers.add(key));
  });

  const headerArray = Array.from(headers);

  // Create CSV content
  const rows = [
    headerArray.join(','),
    ...flatData.map(item =>
      headerArray.map(header => {
        const value = item[header] || '';
        // Escape commas and quotes
        const escaped = String(value).replace(/"/g, '""');
        return `"${escaped}"`;
      }).join(',')
    )
  ];

  return rows.join('\n');
}

// Run the scraper
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

module.exports = { scrapeCountryAFVs, scrapeCountryGuns, extractVehicleDetails };
