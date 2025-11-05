#!/usr/bin/env node

/**
 * OnWar.com WWII AFV Scraper - Enhanced Version
 * Properly extracts data from HTML tables with class="subheading" and class="data"
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// Configuration
const OUTPUT_DIR = path.join(__dirname, '..', 'data', 'output', 'afv_data');
const VEHICLE_LIST_FILE = path.join(OUTPUT_DIR, 'onwar_afv_complete.csv');
const OUTPUT_JSON = path.join(OUTPUT_DIR, 'afv_complete_with_specs.json');
const OUTPUT_CSV = path.join(OUTPUT_DIR, 'afv_complete_with_specs.csv');
const ABBREVIATIONS_FILE = path.join(OUTPUT_DIR, 'abbreviations_final.json');

const DELAY_MS = 1000;

/**
 * Fetch HTML content from a URL
 */
function fetchPage(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        if (res.statusCode === 200) resolve(data);
        else reject(new Error(`HTTP ${res.statusCode}: ${url}`));
      });
    }).on('error', reject);
  });
}

/**
 * Strip HTML tags
 */
function stripHtml(html) {
  return html
    .replace(/<[^>]*>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&deg;/g, '°')
    .replace(/&shy;/g, '')
    .replace(/&#(\d+);/g, (match, dec) => String.fromCharCode(dec))
    .trim();
}

/**
 * Extract table data from HTML
 * Looks for <td class="subheading">Label</td><td class="data">Value</td> pairs
 */
function extractTableData(html) {
  const data = {};

  // Pattern to match table rows with subheading and data pairs
  const rowPattern = /<tr[^>]*>(.*?)<\/tr>/gis;
  let rowMatch;

  while ((rowMatch = rowPattern.exec(html)) !== null) {
    const rowHtml = rowMatch[1];

    // Extract all cells in this row
    const cells = [];
    const cellPattern = /<td[^>]*class="(subheading|data)"[^>]*>(.*?)<\/td>/gis;
    let cellMatch;

    while ((cellMatch = cellPattern.exec(rowHtml)) !== null) {
      cells.push({
        type: cellMatch[1],
        content: stripHtml(cellMatch[2])
      });
    }

    // Process pairs of subheading + data
    for (let i = 0; i < cells.length - 1; i++) {
      if (cells[i].type === 'subheading' && cells[i+1].type === 'data') {
        const key = cells[i].content;
        const value = cells[i+1].content;

        if (key && value && value !== '-') {
          data[key] = value;
        }
      }
    }
  }

  return data;
}

/**
 * Extract armor protection table data
 */
function extractArmorTable(html) {
  const armor = {
    hull_front: '',
    hull_side: '',
    hull_rear: '',
    hull_top_bottom: '',
    superstructure_front: '',
    superstructure_side: '',
    superstructure_rear: '',
    superstructure_top_bottom: '',
    turret_front: '',
    turret_side: '',
    turret_rear: '',
    turret_top_bottom: '',
    mantlet: ''
  };

  // Find the ARMOR PROTECTION table
  const armorTableMatch = html.match(/<table>[\s\S]*?ARMOR PROTECTION[\s\S]*?<\/table>/i);
  if (!armorTableMatch) return armor;

  const armorHtml = armorTableMatch[0];

  // Extract hull armor
  const hullMatch = armorHtml.match(/<tr[^>]*>[\s\S]*?<td[^>]*class="subheading"[^>]*>Hull<\/td>[\s\S]*?<td[^>]*class="data"[^>]*>(.*?)<\/td>[\s\S]*?<td[^>]*class="data"[^>]*>(.*?)<\/td>[\s\S]*?<td[^>]*class="data"[^>]*>(.*?)<\/td>[\s\S]*?<td[^>]*class="data"[^>]*>(.*?)<\/td>/i);
  if (hullMatch) {
    armor.hull_front = stripHtml(hullMatch[1]);
    armor.hull_side = stripHtml(hullMatch[2]);
    armor.hull_rear = stripHtml(hullMatch[3]);
    armor.hull_top_bottom = stripHtml(hullMatch[4]);
  }

  // Extract superstructure armor
  const superMatch = armorHtml.match(/<tr[^>]*>[\s\S]*?<td[^>]*class="subheading"[^>]*>Super.*?structure<\/td>[\s\S]*?<td[^>]*class="data"[^>]*>(.*?)<\/td>[\s\S]*?<td[^>]*class="data"[^>]*>(.*?)<\/td>[\s\S]*?<td[^>]*class="data"[^>]*>(.*?)<\/td>[\s\S]*?<td[^>]*class="data"[^>]*>(.*?)<\/td>/i);
  if (superMatch) {
    armor.superstructure_front = stripHtml(superMatch[1]);
    armor.superstructure_side = stripHtml(superMatch[2]);
    armor.superstructure_rear = stripHtml(superMatch[3]);
    armor.superstructure_top_bottom = stripHtml(superMatch[4]);
  }

  // Extract turret armor
  const turretMatch = armorHtml.match(/<tr[^>]*>[\s\S]*?<td[^>]*class="subheading"[^>]*>Turret<\/td>[\s\S]*?<td[^>]*class="data"[^>]*>(.*?)<\/td>[\s\S]*?<td[^>]*class="data"[^>]*>(.*?)<\/td>[\s\S]*?<td[^>]*class="data"[^>]*>(.*?)<\/td>[\s\S]*?<td[^>]*class="data"[^>]*>(.*?)<\/td>/i);
  if (turretMatch) {
    armor.turret_front = stripHtml(turretMatch[1]);
    armor.turret_side = stripHtml(turretMatch[2]);
    armor.turret_rear = stripHtml(turretMatch[3]);
    armor.turret_top_bottom = stripHtml(turretMatch[4]);
  }

  // Extract mantlet armor
  const mantletMatch = armorHtml.match(/<tr[^>]*>[\s\S]*?<td[^>]*class="subheading"[^>]*>Mantlet<\/td>[\s\S]*?<td[^>]*class="data"[^>]*>(.*?)<\/td>/i);
  if (mantletMatch) {
    armor.mantlet = stripHtml(mantletMatch[1]);
  }

  return armor;
}

/**
 * Extract abbreviations from page
 */
const abbreviations = new Map();

function extractAbbreviations(html) {
  // Look for abbreviations in tables or definition lists
  const pattern = /([A-Za-z][A-Za-z0-9.äöü]+)\s*[=:]\s*([^<\n]{5,100}?)(?:<br|<\/td|<\/p)/gi;
  let match;

  while ((match = pattern.exec(html)) !== null) {
    const abbr = stripHtml(match[1]).trim();
    const definition = stripHtml(match[2]).trim();

    if (abbr.length > 1 && definition.length > 3 &&
        !definition.includes('=') && !definition.includes('http')) {
      abbreviations.set(abbr, definition);
    }
  }
}

/**
 * Parse vehicle specifications from HTML
 */
function parseVehicleSpecs(html, vehicleName, country, url) {
  const tableData = extractTableData(html);
  const armorData = extractArmorTable(html);

  const specs = {
    country: country,
    vehicle_name: vehicleName,
    url: url,

    // General Data
    formal_designation: tableData['Formal Designation'] || '',
    type: tableData['Type'] || '',
    crew: tableData['Crew'] || '',
    manufacturers: tableData['Manufacturer(s)'] || '',
    production_quantity: tableData['Production Quantity'] || '',
    production_period: tableData['Production Period'] || '',

    // Dimensions
    length_hull: tableData['Length /hull (m)'] || '',
    width: tableData['Width (m)'] || '',
    height: tableData['Height (m)'] || '',
    combat_weight: tableData['Combat Weight (kg)'] || '',
    ground_clearance: tableData['Ground Clearance (m)'] || '',

    // Communications
    radio: tableData['Radio'] || '',

    // Firepower
    primary_armament: tableData['Primary Armament'] || '',
    secondary_armament: tableData['Secondary Armament'] || '',
    ammunition_carried: tableData['Ammunition Carried'] || '',
    traverse: tableData['Traverse (degrees)'] || '',
    elevation: tableData['Elevation (degrees)'] || '',

    // Mobility
    engine_make_model: tableData['Engine Make & Model'] || '',
    engine_type_displacement: tableData['Type & Displacement'] || '',
    horsepower: tableData['Horsepower (max.)'] || '',
    power_weight_ratio: tableData['Power/Weight Ratio'] || '',
    fuel_type: tableData['Fuel'] || '',
    fuel_capacity: tableData['Fuel Capacity (liters)'] || '',
    speed: tableData['Speed on/off road'] || '',
    range: tableData['Range on/off road (km)'] || '',
    gearbox: tableData['Gearbox'] || '',
    turning_radius: tableData['Turning Radius (m)'] || '',
    gradient: tableData['Gradient (degrees)'] || '',
    fording: tableData['Fording (m)'] || '',
    vertical_obstacle: tableData['Vertical Obstacle (m)'] || '',
    trench_crossing: tableData['Trench Crossing (m)'] || '',
    ground_pressure: tableData['Ground Pressure'] || '',
    track_width: tableData['Track Width'] || '',
    track_ground_contact: tableData['Track Ground Contact'] || '',

    // Armor Protection
    ...armorData
  };

  return specs;
}

/**
 * Sleep helper
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Main scraping function
 */
async function scrapeAllSpecs() {
  console.log('Enhanced OnWar.com AFV Scraper\n');
  console.log('Loading vehicle list from previous scrape...\n');

  // Read the vehicle list CSV
  const csvContent = fs.readFileSync(VEHICLE_LIST_FILE, 'utf-8');
  const lines = csvContent.split('\n').slice(1); // Skip header

  const vehicles = lines
    .filter(line => line.trim().length > 0)
    .map(line => {
      const parts = line.split(',');
      return {
        country: parts[0],
        name: parts[1],
        url: parts[parts.length - 1] // URL is last column
      };
    })
    .filter(v => v.url && !v.url.includes('about') && !v.url.includes('privacy') && !v.url.includes('contact'));

  console.log(`Found ${vehicles.length} vehicles to process\n`);

  const allSpecs = [];
  let count = 0;

  for (const vehicle of vehicles) {
    count++;
    try {
      console.log(`[${count}/${vehicles.length}] ${vehicle.country}: ${vehicle.name}`);

      const html = await fetchPage(vehicle.url);
      const specs = parseVehicleSpecs(html, vehicle.name, vehicle.country, vehicle.url);
      allSpecs.push(specs);

      // Extract abbreviations
      extractAbbreviations(html);

      await sleep(DELAY_MS);
    } catch (error) {
      console.error(`  Error: ${error.message}`);
    }
  }

  console.log(`\nSuccessfully scraped ${allSpecs.length} vehicles with full specifications\n`);

  // Save JSON
  console.log('Saving JSON data...');
  fs.writeFileSync(OUTPUT_JSON, JSON.stringify(allSpecs, null, 2));
  console.log(`  Saved to ${OUTPUT_JSON}`);

  // Save abbreviations
  const abbrObject = Object.fromEntries(abbreviations);
  fs.writeFileSync(ABBREVIATIONS_FILE, JSON.stringify(abbrObject, null, 2));
  console.log(`  Saved ${abbreviations.size} abbreviations to ${ABBREVIATIONS_FILE}`);

  // Save CSV
  console.log('\nConverting to CSV...');
  const headers = Object.keys(allSpecs[0]);
  const csvLines = [headers.join(',')];

  for (const spec of allSpecs) {
    const values = headers.map(header => {
      const value = (spec[header] || '').toString();
      // Escape CSV values
      if (value.includes(',') || value.includes('"') || value.includes('\n')) {
        return `"${value.replace(/"/g, '""')}"`;
      }
      return value;
    });
    csvLines.push(values.join(','));
  }

  fs.writeFileSync(OUTPUT_CSV, csvLines.join('\n'));
  console.log(`  Saved to ${OUTPUT_CSV}`);

  console.log('\n✓ Complete!');
  console.log(`  Total vehicles: ${allSpecs.length}`);
  console.log(`  Total abbreviations: ${abbreviations.size}`);
}

// Run the scraper
scrapeAllSpecs().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
