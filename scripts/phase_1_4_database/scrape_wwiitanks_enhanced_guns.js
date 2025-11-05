/**
 * WWII Tanks UK Enhanced Gun Scraper (v2)
 * Properly parses ammunition data with structured penetration tables
 *
 * Usage: node scripts/scrape_wwiitanks_enhanced_guns.js
 */

const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');

// Country codes for guns
const COUNTRIES = {
  'Austria': 40,
  'Belgium': 56,
  'Britain': 826,
  'Czechoslovakia': 203,
  'Denmark': 208,
  'Finland': 246,
  'France': 250,
  'Germany': 276,
  'Hungary': 348,
  'Italy': 380,
  'Japan': 392,
  'Netherlands': 528,
  'Poland': 616,
  'Sweden': 752,
  'Switzerland': 756,
  'USSR': 643,
  'USA': 840
};

const OUTPUT_DIR = path.join(__dirname, '..', 'data', 'output', 'afv_data', 'wwiitanks');

/**
 * Extract gun list from country summary page (no pagination for guns)
 */
async function extractGunList(page, url) {
  console.log(`Navigating to ${url}...`);
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
  await page.waitForTimeout(2000);

  const guns = await page.evaluate(() => {
    const results = [];
    const allLinks = document.querySelectorAll('a[href*="Gun_Data.php?I="]');

    allLinks.forEach(link => {
      const text = link.textContent.trim();
      const href = link.href;

      if (href && text && text.length > 3 && text.length < 200 && !text.includes('flag')) {
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

        results.push({ name: text, href: href, indicators: indicators });
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

  console.log(`  Total found: ${guns.length} guns`);
  return guns;
}

/**
 * Helper: Parse ammunition specifications from text
 * Example: "50mm 2.06Kg 840M/Sec" -> {calibre: "50mm", weight_kg: 2.06, muzzle_velocity_m_s: 840}
 */
function parseAmmoSpecs(text) {
  const specs = {};

  // Extract calibre (e.g., "50mm", "7.92mm")
  const calibreMatch = text.match(/(\d+\.?\d*mm)/i);
  if (calibreMatch) specs.calibre = calibreMatch[1];

  // Extract weight (e.g., "2.06Kg", "0.98kg")
  const weightMatch = text.match(/(\d+\.?\d+)\s*kg/i);
  if (weightMatch) specs.weight_kg = parseFloat(weightMatch[1]);

  // Extract muzzle velocity (e.g., "840M/Sec", "1198m/s")
  const velocityMatch = text.match(/(\d+)\s*m\/sec/i);
  if (velocityMatch) specs.muzzle_velocity_m_s = parseInt(velocityMatch[1]);

  // Extract explosive content for HE rounds (e.g., "0.165Kg explosive")
  const explosiveMatch = text.match(/(\d+\.?\d+)\s*kg\s+explosive/i);
  if (explosiveMatch) specs.explosive_kg = parseFloat(explosiveMatch[1]);

  return specs;
}

/**
 * Helper: Determine ammunition type abbreviation from full description
 */
function getAmmoType(text) {
  const upper = text.toUpperCase();
  if (upper.includes('AP40') || upper.includes('TUNGSTEN') || upper.includes('APCR')) return 'AP40';
  if (upper.includes('HEAT') || upper.includes('HIGH EXPLOSIVE ANTI-TANK')) return 'HEAT';
  if (upper.includes('HE') || upper.includes('HIGH EXPLOSIVE')) return 'HE';
  if (upper.includes('AP') || upper.includes('ARMOR PIERCING') || upper.includes('ARMOUR PIERCING')) return 'AP';
  return 'UNKNOWN';
}

/**
 * Enhanced gun detail extraction with structured ammunition data
 */
async function extractGunDetailsEnhanced(page, url, gunName) {
  console.log(`  Extracting details for: ${gunName}`);

  try {
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
    await page.waitForTimeout(1000);

    const data = await page.evaluate(() => {
      const result = {
        basic_specs: {},
        ammunition: [],
        vehicles_using_gun: []
      };

      // Stage 1: Extract basic gun specs from 2-column tables
      const allTables = document.querySelectorAll('table');

      for (let table of allTables) {
        const rows = table.querySelectorAll('tr');
        for (let row of rows) {
          const cells = row.querySelectorAll('td');
          if (cells.length === 2) {
            const label = cells[0].textContent.trim();
            const value = cells[1].textContent.trim();

            // Basic gun specifications
            if (label === 'Manufactured') result.basic_specs.manufactured = value;
            if (label === 'Calibre') result.basic_specs.calibre = value;
            if (label === 'Length') result.basic_specs.length = value;
            if (label === 'Rate of Fire') result.basic_specs.rate_of_fire = value;
            if (label === 'History') result.basic_specs.history = value;
          }
        }
      }

      // Stage 2: Extract gun name, full name, translation from header
      const headerCells = document.querySelectorAll('td');
      for (let cell of headerCells) {
        const text = cell.textContent.trim();
        if (text.includes('translates as')) {
          const lines = text.split('\n').map(l => l.trim()).filter(l => l);
          if (lines.length >= 2) {
            result.full_name = lines[1];
          }
          const transMatch = text.match(/\(translates as ([^)]+)\)/i);
          if (transMatch) {
            result.translation = transMatch[1];
          }
        }
      }

      // Stage 3: Extract ammunition sections
      // Look for 3-column tables with ammunition headers
      for (let table of allTables) {
        const rows = Array.from(table.querySelectorAll('tr'));

        let i = 0;
        while (i < rows.length) {
          const row = rows[i];
          const cells = row.querySelectorAll('td');

          if (cells.length === 3) {
            const firstCell = cells[0].textContent.trim();
            const secondCell = cells[1].textContent.trim();
            const thirdCell = cells[2].textContent.trim();

            // Detect ammunition section header
            // Pattern: "5.0cm PzGr. 39 L/60\n(AP Armor Piercing)"
            if (firstCell.match(/^\d+\.?\d*\s*cm\s+.+/) &&
                (firstCell.includes('(') || secondCell.match(/\d+mm\s+\d+/))) {

              const ammo = {
                name: firstCell.split('\n')[0].trim(),
                type_full: '',
                specs: {}
              };

              // Extract type from parentheses
              const typeMatch = firstCell.match(/\(([^)]+)\)/);
              if (typeMatch) {
                ammo.type_full = typeMatch[1].trim();
              }

              // Parse specs from second cell (e.g., "50mm 2.06Kg 840M/Sec")
              if (secondCell) {
                const calibreMatch = secondCell.match(/(\d+\.?\d*mm)/i);
                if (calibreMatch) ammo.specs.calibre = calibreMatch[1];

                const weightMatch = secondCell.match(/(\d+\.?\d+)\s*kg/i);
                if (weightMatch) ammo.specs.weight_kg = parseFloat(weightMatch[1]);

                const velocityMatch = secondCell.match(/(\d+)\s*m\/sec/i);
                if (velocityMatch) ammo.specs.muzzle_velocity_m_s = parseInt(velocityMatch[1]);
              }

              // Parse explosive content from third cell
              if (thirdCell && thirdCell.match(/kg\s+explosive/i)) {
                const explosiveMatch = thirdCell.match(/(\d+\.?\d+)\s*kg/i);
                if (explosiveMatch) ammo.specs.explosive_kg = parseFloat(explosiveMatch[1]);
              }

              // Extract quoted penetration
              i++;
              if (i < rows.length) {
                const quotedRow = rows[i];
                const quotedCells = quotedRow.querySelectorAll('td');
                if (quotedCells.length >= 2) {
                  const quotedText = quotedCells[0].textContent.trim();
                  if (quotedText.includes('Quoted Penetration')) {
                    ammo.quoted_penetration = quotedText.replace('Quoted Penetration', '').trim();
                  }
                }
              }

              // Look for penetration table
              // Pattern: Row with "Range(Mtr)" followed by data rows
              let foundPenetrationTable = false;
              while (i < rows.length && i < rows.indexOf(row) + 20) {
                const dataRow = rows[i];
                const dataCells = dataRow.querySelectorAll('td');

                if (dataCells.length >= 9) {
                  const firstDataCell = dataCells[0].textContent.trim();

                  // Check if this is the range header row
                  if (firstDataCell === 'Range(Mtr)' || firstDataCell.includes('Range')) {
                    foundPenetrationTable = true;

                    // Extract ranges from this row
                    const ranges = [];
                    for (let j = 1; j < dataCells.length && j <= 9; j++) {
                      const rangeText = dataCells[j].textContent.trim();
                      const rangeVal = parseInt(rangeText);
                      if (!isNaN(rangeVal)) ranges.push(rangeVal);
                    }

                    // Extract subsequent data rows
                    const penetrationData = {};
                    for (let k = i + 1; k < Math.min(i + 6, rows.length); k++) {
                      const valueRow = rows[k];
                      const valueCells = valueRow.querySelectorAll('td');

                      if (valueCells.length >= 2) {
                        const rowLabel = valueCells[0].textContent.trim();
                        const values = [];

                        for (let j = 1; j < valueCells.length && j <= ranges.length + 1; j++) {
                          const valueText = valueCells[j].textContent.trim();
                          const floatVal = parseFloat(valueText);
                          values.push(isNaN(floatVal) ? null : floatVal);
                        }

                        if (rowLabel.includes('Flight Time')) {
                          penetrationData.flight_time = values;
                        } else if (rowLabel.includes('30°') || rowLabel.includes('30')) {
                          penetrationData.penetration_30deg = values;
                        } else if (rowLabel.includes('0°') || rowLabel.includes('0')) {
                          penetrationData.penetration_0deg = values;
                        } else if (rowLabel.includes('Probability')) {
                          penetrationData.hit_probability = values;
                        }
                      }
                    }

                    // Build penetration table
                    if (ranges.length > 0) {
                      ammo.penetration_table = [];
                      for (let j = 0; j < ranges.length; j++) {
                        const entry = { range_m: ranges[j] };
                        if (penetrationData.flight_time && penetrationData.flight_time[j] !== null) {
                          entry.flight_time_s = penetrationData.flight_time[j];
                        }
                        if (penetrationData.penetration_30deg && penetrationData.penetration_30deg[j] !== null) {
                          entry.penetration_30deg_mm = penetrationData.penetration_30deg[j];
                        }
                        if (penetrationData.penetration_0deg && penetrationData.penetration_0deg[j] !== null) {
                          entry.penetration_0deg_mm = penetrationData.penetration_0deg[j];
                        }
                        if (penetrationData.hit_probability && penetrationData.hit_probability[j] !== null) {
                          entry.hit_probability_pct = penetrationData.hit_probability[j];
                        }
                        ammo.penetration_table.push(entry);
                      }
                    }

                    i = k; // Skip past data rows
                    break;
                  }

                  // Check for blast effects (HE ammunition)
                  if (firstDataCell.includes('Blast') || firstDataCell.includes('Fragmentation')) {
                    ammo.blast_effects = {};

                    // Parse blast radius data
                    for (let k = i; k < Math.min(i + 10, rows.length); k++) {
                      const blastRow = rows[k];
                      const blastCells = blastRow.querySelectorAll('td');

                      if (blastCells.length >= 2) {
                        const blastLabel = blastCells[0].textContent.trim();
                        const blastValue = blastCells[1].textContent.trim();

                        if (blastLabel.includes('99% kill')) {
                          const radiusMatch = blastValue.match(/(\d+)\s*mtr/);
                          if (radiusMatch) ammo.blast_effects.kill_99pct_radius_m = parseInt(radiusMatch[1]);
                        } else if (blastLabel.includes('66% kill')) {
                          const radiusMatch = blastValue.match(/(\d+)\s*mtr/);
                          if (radiusMatch) ammo.blast_effects.kill_66pct_radius_m = parseInt(radiusMatch[1]);
                        } else if (blastLabel.includes('33% kill')) {
                          const radiusMatch = blastValue.match(/(\d+)\s*mtr/);
                          if (radiusMatch) ammo.blast_effects.kill_33pct_radius_m = parseInt(radiusMatch[1]);
                        } else if (blastLabel.includes('Armour Penetration')) {
                          const armorMatch = blastValue.match(/(\d+)\s*mm/);
                          if (armorMatch) ammo.blast_effects.armor_penetration_1m_mm = parseInt(armorMatch[1]);
                        }
                      }
                    }
                    break;
                  }
                }

                i++;
                if (foundPenetrationTable) break;
              }

              result.ammunition.push(ammo);
            }

            // Detect vehicle relationship table
            if (firstCell.includes('Vehicles in our database') || firstCell.includes('Vehicle Name')) {
              // Skip header rows
              let j = i + 1;
              while (j < rows.length && j < i + 50) {
                const vehRow = rows[j];
                const vehCells = vehRow.querySelectorAll('td');

                if (vehCells.length >= 2) {
                  const vehicleName = vehCells[0].textContent.trim();
                  const commonName = vehCells.length >= 2 ? vehCells[1].textContent.trim() : '';

                  if (vehicleName && vehicleName.length > 2 && vehicleName !== 'Vehicle Name') {
                    result.vehicles_using_gun.push({
                      vehicle_name: vehicleName,
                      common_name: commonName
                    });
                  }
                }
                j++;
              }
              i = j;
              continue;
            }
          }

          i++;
        }
      }

      // Stage 4: Add ammunition type abbreviations
      result.ammunition.forEach(ammo => {
        const upper = ammo.type_full.toUpperCase();
        if (upper.includes('AP40') || upper.includes('TUNGSTEN') || upper.includes('APCR')) {
          ammo.type = 'AP40';
        } else if (upper.includes('HEAT')) {
          ammo.type = 'HEAT';
        } else if (upper.includes('HE')) {
          ammo.type = 'HE';
        } else if (upper.includes('AP')) {
          ammo.type = 'AP';
        } else {
          ammo.type = 'UNKNOWN';
        }
      });

      return result;
    });

    return data;
  } catch (error) {
    console.error(`    Error extracting details for ${gunName}: ${error.message}`);
    return null;
  }
}

/**
 * Scrape guns for a specific country with enhanced parsing
 */
async function scrapeCountryGunsEnhanced(page, countryName, countryCode) {
  console.log(`\n=== Scraping Guns for ${countryName} (Enhanced v2) ===`);

  const url = `https://wwiitanks.co.uk/FORM-Gun_Data-Summary.php?C=${countryCode}`;
  const gunList = await extractGunList(page, url);

  const results = [];

  for (let i = 0; i < gunList.length; i++) {
    const gun = gunList[i];
    console.log(`  [${i + 1}/${gunList.length}] ${gun.name}`);

    const details = await extractGunDetailsEnhanced(page, gun.href, gun.name);

    if (details) {
      // Extract ID from URL for unique identifier
      const urlMatch = gun.href.match(/Gun_Data\.php\?I=(\d+)/);
      const gunId = urlMatch ? urlMatch[1] : `unknown_${i}`;

      results.push({
        wwiitanks_id: `wwiitanks_${countryName.toLowerCase()}_gun_${gunId}`,
        source: 'wwiitanks.co.uk',
        source_url: gun.href,
        scraped_at: new Date().toISOString(),
        scraper_version: 'v2_enhanced',
        country: countryName.toLowerCase(),
        gun_name: gun.name,
        full_name: details.full_name || gun.name,
        translation: details.translation || '',
        indicators: gun.indicators,
        basic_specs: details.basic_specs,
        ammunition: details.ammunition,
        vehicles_using_gun: details.vehicles_using_gun
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
  console.log('WWII Tanks UK Enhanced Gun Scraper v2');
  console.log('=====================================\n');

  // Ensure output directory exists
  await fs.mkdir(OUTPUT_DIR, { recursive: true });

  // Launch browser
  console.log('Launching browser...');
  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: { width: 1400, height: 900 }
  });

  const page = await browser.newPage();

  // Set user agent
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');

  const allGuns = [];

  // Scrape each country
  for (const [countryName, countryCode] of Object.entries(COUNTRIES)) {
    try {
      const guns = await scrapeCountryGunsEnhanced(page, countryName, countryCode);
      allGuns.push(...guns);

      // Save incremental results
      await fs.writeFile(
        path.join(OUTPUT_DIR, `${countryName.toLowerCase()}_guns_v2.json`),
        JSON.stringify(guns, null, 2)
      );
      console.log(`  Saved ${guns.length} guns to ${countryName.toLowerCase()}_guns_v2.json`);
    } catch (error) {
      console.error(`Error scraping ${countryName}: ${error.message}`);
    }
  }

  // Save combined results
  console.log('\n=== Saving combined results ===');

  await fs.writeFile(
    path.join(OUTPUT_DIR, 'all_guns_v2.json'),
    JSON.stringify(allGuns, null, 2)
  );
  console.log(`Saved ${allGuns.length} guns to all_guns_v2.json`);

  await browser.close();
  console.log('\n=== Enhanced gun scraping complete! ===');
}

// Run the scraper
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

module.exports = { scrapeCountryGunsEnhanced, extractGunDetailsEnhanced };
