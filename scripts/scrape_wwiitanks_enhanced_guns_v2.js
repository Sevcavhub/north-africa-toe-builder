/**
 * WWII Tanks UK Enhanced Gun Scraper v2.1 (WORKING VERSION)
 * Properly handles TH+TD structure
 *
 * Usage: node scripts/scrape_wwiitanks_enhanced_guns_v2.js
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
 * Extract gun list from country summary page
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
        results.push({ name: text, href: href });
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
  });

  console.log(`  Total found: ${guns.length} guns`);
  return guns;
}

/**
 * Enhanced gun detail extraction - handles TH+TD structure correctly
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

      // Get all rows
      const allRows = Array.from(document.querySelectorAll('tr'));

      // Stage 1: Extract basic gun specs (rows with TH label + TD value)
      allRows.forEach(row => {
        const th = row.querySelector('th');
        const tds = Array.from(row.querySelectorAll('td'));

        if (th && tds.length > 0) {
          const label = th.textContent.trim();
          // Get the last non-empty TD as the value
          const value = tds.map(td => td.textContent.trim()).filter(t => t).pop() || '';

          if (label === 'Manufactured') result.basic_specs.manufactured = value;
          if (label === 'Calibre') result.basic_specs.calibre = value;
          if (label === 'Length') result.basic_specs.length = value;
          if (label === 'Rate of Fire') result.basic_specs.rate_of_fire = value;
          if (label === 'History' && value) result.basic_specs.history = value;
        }
      });

      // Stage 2: Extract ammunition sections
      const debug = { total_rows: allRows.length, th_rows: 0, ammo_matches: 0, match_details: [] };

      for (let i = 0; i < allRows.length; i++) {
        const row = allRows[i];
        const allCells = Array.from(row.querySelectorAll('th, td'));

        // Look for ammunition header row
        // Pattern: TH with ammunition name + TD with specs
        // Note: TH is not always first cell due to empty TD spacers
        const thCell = allCells.find(cell => cell.tagName === 'TH');

        if (thCell) {
          debug.th_rows++;
          const text = thCell.textContent.trim();

          // Check if this looks like an ammunition header
          // Pattern: "5.0cm PzGr..." or "5cm Sprgr..."
          const hasMatch = text.match(/^\d+\.?\d*\s*cm\s*.+/) && text.includes('(');
          if (hasMatch) {
            debug.ammo_matches++;
            debug.match_details.push({ row: i, text: text.substring(0, 80), cells: allCells.length });
          }

          if (hasMatch) {
              const ammo = {
                name: text.split('\n')[0].trim(),
                type_full: '',
                specs: {},
                penetration_table: []
              };

              // Extract type from parentheses
              const typeMatch = text.match(/\(([^)]+)\)/);
              if (typeMatch) {
                ammo.type_full = typeMatch[1].trim();
                const upper = ammo.type_full.toUpperCase();
                if (upper.includes('AP40') || upper.includes('TUNGSTEN')) ammo.type = 'AP40';
                else if (upper.includes('HEAT')) ammo.type = 'HEAT';
                else if (upper.includes('HE')) ammo.type = 'HE';
                else if (upper.includes('AP')) ammo.type = 'AP';
                else ammo.type = 'UNKNOWN';
              }

              // Parse specs from TD cells after the TH
              const thIndex = allCells.indexOf(thCell);
              const tdCells = allCells.slice(thIndex + 1).filter(cell => cell.tagName === 'TD');

              if (tdCells.length >= 1) {
                const specsText = tdCells[0].textContent.trim();

                const calibreMatch = specsText.match(/(\d+\.?\d*mm)/i);
                if (calibreMatch) ammo.specs.calibre = calibreMatch[1];

                const weightMatch = specsText.match(/(\d+\.?\d+)\s*kg/i);
                if (weightMatch) ammo.specs.weight_kg = parseFloat(weightMatch[1]);

                const velocityMatch = specsText.match(/(\d+)\s*m\/sec/i);
                if (velocityMatch) ammo.specs.muzzle_velocity_m_s = parseInt(velocityMatch[1]);
              }

              // Check second TD for explosive content
              if (tdCells.length >= 2) {
                const secondTdText = tdCells[1].textContent.trim();
                const explosiveMatch = secondTdText.match(/(\d+\.?\d+)\s*kg\s+explosive/i);
                if (explosiveMatch) ammo.specs.explosive_kg = parseFloat(explosiveMatch[1]);
              }

              // Look for quoted penetration in next row
              if (i + 1 < allRows.length) {
                const quotedRow = allRows[i + 1];
                const quotedText = quotedRow.textContent.trim();
                if (quotedText.includes('Quoted Penetration')) {
                  ammo.quoted_penetration = quotedText.replace(/^.*Quoted Penetration\s*/i, '').trim();
                }
              }

              // Look for penetration table
              // Find row with "Range(Mtr)" as first TH
              for (let j = i + 1; j < Math.min(i + 15, allRows.length); j++) {
                const dataRow = allRows[j];
                const dataCells = Array.from(dataRow.querySelectorAll('th, td'));

                if (dataCells.length >= 9 && dataCells[0].tagName === 'TH' && dataCells[0].textContent.trim() === 'Range(Mtr)') {
                  // Extract ranges from TH elements
                  const ranges = [];
                  for (let k = 1; k < 9 && k < dataCells.length; k++) {
                    const rangeVal = parseInt(dataCells[k].textContent.trim());
                    if (!isNaN(rangeVal)) ranges.push(rangeVal);
                  }

                  // Extract data rows (Flight Time, Penetration, Hit Probability)
                  const penetrationData = {};
                  for (let k = j + 1; k < Math.min(j + 6, allRows.length); k++) {
                    const valueRow = allRows[k];
                    const valueCells = Array.from(valueRow.querySelectorAll('th, td'));

                    if (valueCells.length >= 9 && valueCells[0].tagName === 'TH') {
                      const rowLabel = valueCells[0].textContent.trim();
                      const values = [];

                      for (let m = 1; m < 9 && m < valueCells.length; m++) {
                        if (valueCells[m].tagName === 'TD') {
                          const valueText = valueCells[m].textContent.trim();
                          const floatVal = parseFloat(valueText);
                          values.push(isNaN(floatVal) || valueText === '' ? null : floatVal);
                        }
                      }

                      if (rowLabel.includes('Flight Time')) {
                        penetrationData.flight_time = values;
                      } else if (rowLabel.includes('30°') || rowLabel.includes('30')) {
                        penetrationData.penetration_30deg = values;
                      } else if (rowLabel.includes('0°') || (rowLabel.includes('0') && rowLabel.includes('Penetration'))) {
                        penetrationData.penetration_0deg = values;
                      } else if (rowLabel.includes('Probability')) {
                        penetrationData.hit_probability = values;
                      }
                    }
                  }

                  // Build penetration table
                  if (ranges.length > 0) {
                    for (let k = 0; k < ranges.length; k++) {
                      const entry = { range_m: ranges[k] };
                      if (penetrationData.flight_time && penetrationData.flight_time[k] !== null) {
                        entry.flight_time_s = penetrationData.flight_time[k];
                      }
                      if (penetrationData.penetration_30deg && penetrationData.penetration_30deg[k] !== null) {
                        entry.penetration_30deg_mm = penetrationData.penetration_30deg[k];
                      }
                      if (penetrationData.penetration_0deg && penetrationData.penetration_0deg[k] !== null) {
                        entry.penetration_0deg_mm = penetrationData.penetration_0deg[k];
                      }
                      if (penetrationData.hit_probability && penetrationData.hit_probability[k] !== null) {
                        entry.hit_probability_pct = penetrationData.hit_probability[k];
                      }
                      ammo.penetration_table.push(entry);
                    }
                  }

                  break;
                }

                // Check for blast effects table
                const cellText = dataCells[0]?.textContent.trim() || '';
                if (cellText.includes('Blast') || cellText.includes('Fragmentation')) {
                  ammo.blast_effects = {};

                  // Parse blast radius rows
                  for (let k = j; k < Math.min(j + 10, allRows.length); k++) {
                    const blastRow = allRows[k];
                    const blastCells = Array.from(blastRow.querySelectorAll('th, td'));

                    if (blastCells.length >= 2 && blastCells[0].tagName === 'TH') {
                      const blastLabel = blastCells[0].textContent.trim();
                      const blastValue = blastCells[1]?.textContent.trim() || '';

                      if (blastLabel.includes('99% kill')) {
                        const radiusMatch = blastValue.match(/(\d+)/);
                        if (radiusMatch) ammo.blast_effects.kill_99pct_radius_m = parseInt(radiusMatch[1]);
                      } else if (blastLabel.includes('66% kill')) {
                        const radiusMatch = blastValue.match(/(\d+)/);
                        if (radiusMatch) ammo.blast_effects.kill_66pct_radius_m = parseInt(radiusMatch[1]);
                      } else if (blastLabel.includes('33% kill')) {
                        const radiusMatch = blastValue.match(/(\d+)/);
                        if (radiusMatch) ammo.blast_effects.kill_33pct_radius_m = parseInt(radiusMatch[1]);
                      } else if (blastLabel.includes('Armour Penetration')) {
                        const armorMatch = blastValue.match(/(\d+)/);
                        if (armorMatch) ammo.blast_effects.armor_penetration_1m_mm = parseInt(armorMatch[1]);
                      }
                    }
                  }
                  break;
                }
              }

              result.ammunition.push(ammo);
          }
        }

        // Check for vehicles using gun table (separate check, not inside thCell block)
        const firstCell = allCells.find(cell => cell.tagName === 'TH');
        if (firstCell && firstCell.textContent.trim().includes('Vehicles in our database')) {
          // Next rows are vehicle data
          for (let j = i + 2; j < Math.min(i + 50, allRows.length); j++) {
            const vehRow = allRows[j];
            const vehCells = Array.from(vehRow.querySelectorAll('td'));

            if (vehCells.length >= 2) {
              const vehicleName = vehCells[vehCells.length - 2]?.textContent.trim() || '';
              const commonName = vehCells[vehCells.length - 1]?.textContent.trim() || '';

              if (vehicleName && vehicleName.length > 2 && !vehicleName.includes('Vehicle Name')) {
                result.vehicles_using_gun.push({
                  vehicle_name: vehicleName,
                  common_name: commonName
                });
              }
            }
          }
          break;
        }
      }

      result.debug = debug;
      return result;
    });

    return data;
  } catch (error) {
    console.error(`    Error extracting details for ${gunName}: ${error.message}`);
    return null;
  }
}

/**
 * Scrape guns for a specific country
 */
async function scrapeCountryGunsEnhanced(page, countryName, countryCode) {
  console.log(`\n=== Scraping Guns for ${countryName} (Enhanced v2.1) ===`);

  const url = `https://wwiitanks.co.uk/FORM-Gun_Data-Summary.php?C=${countryCode}`;
  const gunList = await extractGunList(page, url);

  const results = [];

  for (let i = 0; i < gunList.length; i++) {
    const gun = gunList[i];
    console.log(`  [${i + 1}/${gunList.length}] ${gun.name}`);

    const details = await extractGunDetailsEnhanced(page, gun.href, gun.name);

    if (details) {
      const urlMatch = gun.href.match(/Gun_Data\.php\?I=(\d+)/);
      const gunId = urlMatch ? urlMatch[1] : `unknown_${i}`;

      results.push({
        wwiitanks_id: `wwiitanks_${countryName.toLowerCase()}_gun_${gunId}`,
        source: 'wwiitanks.co.uk',
        source_url: gun.href,
        scraped_at: new Date().toISOString(),
        scraper_version: 'v2.1_enhanced',
        country: countryName.toLowerCase(),
        gun_name: gun.name,
        full_name: details.full_name || gun.name,
        basic_specs: details.basic_specs,
        ammunition: details.ammunition,
        vehicles_using_gun: details.vehicles_using_gun
      });
    }

    await page.waitForTimeout(500 + Math.random() * 1000);
  }

  return results;
}

/**
 * Check if country file already exists (resume capability)
 */
async function isCountryCompleted(countryName) {
  try {
    const filePath = path.join(OUTPUT_DIR, `${countryName.toLowerCase()}_guns_v2.json`);
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

/**
 * Main scraper function with browser restart every 3 countries
 */
async function main() {
  console.log('WWII Tanks UK Enhanced Gun Scraper v2.1 (with auto-restart)');
  console.log('============================================================\n');

  await fs.mkdir(OUTPUT_DIR, { recursive: true });

  const allGuns = [];
  const countryEntries = Object.entries(COUNTRIES);
  let browser = null;
  let page = null;
  let countriesProcessed = 0;

  for (let i = 0; i < countryEntries.length; i++) {
    const [countryName, countryCode] = countryEntries[i];

    // Check if already completed (resume capability)
    if (await isCountryCompleted(countryName)) {
      console.log(`\n⏭️  Skipping ${countryName} (already completed)`);
      try {
        const existingData = JSON.parse(
          await fs.readFile(path.join(OUTPUT_DIR, `${countryName.toLowerCase()}_guns_v2.json`), 'utf8')
        );
        allGuns.push(...existingData);
      } catch (error) {
        console.log(`  Warning: Could not load existing data: ${error.message}`);
      }
      continue;
    }

    // Launch browser if needed or restart every 3 countries
    if (!browser || countriesProcessed >= 3) {
      if (browser) {
        console.log('\n🔄 Restarting browser to prevent timeouts...');
        await browser.close();
      } else {
        console.log('Launching browser...');
      }

      browser = await puppeteer.launch({
        headless: false,
        defaultViewport: { width: 1400, height: 900 },
        protocolTimeout: 180000 // 3 minutes
      });

      page = await browser.newPage();
      await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
      countriesProcessed = 0;
    }

    try {
      const guns = await scrapeCountryGunsEnhanced(page, countryName, countryCode);
      allGuns.push(...guns);

      await fs.writeFile(
        path.join(OUTPUT_DIR, `${countryName.toLowerCase()}_guns_v2.json`),
        JSON.stringify(guns, null, 2)
      );
      console.log(`  ✅ Saved ${guns.length} guns to ${countryName.toLowerCase()}_guns_v2.json`);
      countriesProcessed++;
    } catch (error) {
      console.error(`❌ Error scraping ${countryName}: ${error.message}`);
      console.log(`  Continuing with next country...\n`);
    }
  }

  // Save combined results
  console.log('\n=== Saving combined results ===');
  await fs.writeFile(
    path.join(OUTPUT_DIR, 'all_guns_v2.json'),
    JSON.stringify(allGuns, null, 2)
  );
  console.log(`Saved ${allGuns.length} guns to all_guns_v2.json`);

  if (browser) {
    await browser.close();
  }

  console.log('\n=== ✅ Enhanced gun scraping complete! ===');
}

if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

module.exports = { scrapeCountryGunsEnhanced, extractGunDetailsEnhanced };
