#!/usr/bin/env node

/**
 * Research production dates for AFVs with gaps
 * Phase 1: Search Jane's WW2 Tanks local file
 * Phase 2: Generate research tasks for remaining gaps
 */

const fs = require('fs');
const path = require('path');

const GAPS_FILE = path.join(__dirname, '..', 'data', 'output', 'afv_data', 'production_date_gaps.json');
const JANES_FILE = path.join(__dirname, '..', 'Resource Documents', 'Janes-ww2-Tanks-And-Fighting-Vehicles.txt');
const RESEARCH_TASKS_DIR = path.join(__dirname, '..', 'tasks', 'research_production_dates');
const RESULTS_FILE = path.join(__dirname, '..', 'data', 'output', 'afv_data', 'production_date_research_results.json');

// Ensure directories exist
if (!fs.existsSync(RESEARCH_TASKS_DIR)) {
  fs.mkdirSync(RESEARCH_TASKS_DIR, { recursive: true });
}

console.log('='.repeat(80));
console.log('AFV Production Date Research - Phase 1: Local Jane\'s Search');
console.log('='.repeat(80));
console.log();

// Load gaps
const gaps = JSON.parse(fs.readFileSync(GAPS_FILE, 'utf-8'));
console.log(`Found ${gaps.vehicles_needing_research} vehicles needing research\n`);

// Load Jane's file (this is a large file, ~88k lines)
console.log('Loading Jane\'s WW2 Tanks reference (88,257 lines)...');
const janesContent = fs.readFileSync(JANES_FILE, 'utf-8');
console.log('✓ Jane\'s loaded\n');

const results = {
  total_vehicles_researched: gaps.vehicles_needing_research,
  found_in_janes: 0,
  still_need_web_research: 0,
  janes_results: [],
  web_research_needed: []
};

console.log('Searching Jane\'s for each vehicle...\n');

for (const [index, vehicle] of gaps.research_list.entries()) {
  const progress = `[${index + 1}/${gaps.vehicles_needing_research}]`;

  // Search for vehicle in Jane's
  const searchResult = searchJanesForVehicle(janesContent, vehicle);

  if (searchResult.found) {
    console.log(`${progress} ✓ FOUND: ${vehicle.country} ${vehicle.vehicle_name}`);
    if (searchResult.production_info) {
      console.log(`    Production: ${searchResult.production_info}`);
    }
    results.found_in_janes++;
    results.janes_results.push({
      ...vehicle,
      janes_search_result: searchResult
    });
  } else {
    console.log(`${progress} ✗ NOT FOUND: ${vehicle.country} ${vehicle.vehicle_name}`);
    results.still_need_web_research++;
    results.web_research_needed.push(vehicle);
  }
}

console.log('\n' + '='.repeat(80));
console.log('Phase 1 Results:');
console.log('='.repeat(80));
console.log(`Total vehicles: ${results.total_vehicles_researched}`);
console.log(`Found in Jane's: ${results.found_in_janes} (${Math.round(results.found_in_janes / results.total_vehicles_researched * 100)}%)`);
console.log(`Need web research: ${results.still_need_web_research} (${Math.round(results.still_need_web_research / results.total_vehicles_researched * 100)}%)`);
console.log();

// Save results
fs.writeFileSync(RESULTS_FILE, JSON.stringify(results, null, 2));
console.log(`✓ Saved results to: ${RESULTS_FILE}`);
console.log();

// Generate research task files for vehicles not found in Jane's
if (results.still_need_web_research > 0) {
  console.log('='.repeat(80));
  console.log(`Generating ${results.still_need_web_research} research task files...`);
  console.log('='.repeat(80));
  console.log();

  for (const vehicle of results.web_research_needed) {
    const taskFile = generateResearchTask(vehicle);
    console.log(`✓ Created: ${path.basename(taskFile)}`);
  }

  console.log();
  console.log('Research task files created in:', RESEARCH_TASKS_DIR);
  console.log('Use these with the historical_research agent for web-based research.');
}

/**
 * Search Jane's file for a vehicle
 */
function searchJanesForVehicle(content, vehicle) {
  const result = {
    found: false,
    production_info: null,
    excerpt: null
  };

  // Create search terms based on vehicle name
  const searchTerms = generateSearchTerms(vehicle.vehicle_name, vehicle.country);

  for (const term of searchTerms) {
    const regex = new RegExp(term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
    const match = regex.exec(content);

    if (match) {
      // Found the vehicle - extract surrounding context
      const startPos = Math.max(0, match.index - 500);
      const endPos = Math.min(content.length, match.index + 2000);
      const excerpt = content.substring(startPos, endPos);

      result.found = true;
      result.excerpt = excerpt;

      // Try to extract production info from excerpt
      const productionMatch = excerpt.match(/production[:\s]+([^\n.]+)/i) ||
                              excerpt.match(/manufactured[:\s]+([^\n.]+)/i) ||
                              excerpt.match(/built[:\s]+([^\n.]+)/i) ||
                              excerpt.match(/\b(19\d{2})\s*[-–to]+\s*(19\d{2})\b/);

      if (productionMatch) {
        result.production_info = productionMatch[1] || `${productionMatch[1]}-${productionMatch[2]}`;
      }

      break; // Found it, no need to continue
    }
  }

  return result;
}

/**
 * Generate search terms for a vehicle
 */
function generateSearchTerms(vehicleName, country) {
  const terms = [vehicleName];

  // Add variations
  terms.push(vehicleName.replace(/\s+/g, ''));  // Remove spaces
  terms.push(vehicleName.replace(/-/g, ' '));   // Replace hyphens with spaces

  // Country-specific variations
  if (country === 'germany') {
    terms.push(vehicleName.replace(/PzKpfw/, 'Panzerkampfwagen'));
    terms.push(vehicleName.replace(/PzKpfw/, 'Panzer'));
    terms.push(vehicleName.replace(/Ausf\./, 'Ausführung'));
  }

  if (country === 'ussr') {
    terms.push(vehicleName.replace(/-/g, ''));
    terms.push(vehicleName.replace(/Model/, 'Mod.'));
  }

  if (country === 'usa') {
    terms.push(vehicleName.replace(/M(\d+)/, 'M-$1'));
  }

  return [...new Set(terms)]; // Remove duplicates
}

/**
 * Generate a research task file for historical_research agent
 */
function generateResearchTask(vehicle) {
  const taskId = `production_date_${vehicle.country}_${vehicle.vehicle_name.replace(/[^a-zA-Z0-9]/g, '_')}`;
  const taskFile = path.join(RESEARCH_TASKS_DIR, `${taskId}.json`);

  const task = {
    task_id: taskId,
    agent_id: "historical_research",
    created_at: new Date().toISOString(),
    status: "pending",
    vehicle: vehicle.vehicle_name,
    country: vehicle.country,
    research_question: `What are the exact production start and end dates for the ${vehicle.vehicle_name}?`,
    current_data: {
      original_production_period: vehicle.original_production_period,
      parsed_start: vehicle.production_start,
      parsed_end: vehicle.production_end
    },
    sources_to_check: [
      {
        source: "JANES_WW2_TANKS",
        priority: 1,
        status: "checked",
        result: "not_found"
      },
      {
        source: "WWIITANKS_UK",
        priority: 2,
        url: `https://wwiitanks.co.uk`,
        status: "pending"
      },
      {
        source: "ONWAR_TANKS",
        priority: 3,
        url: vehicle.url,
        status: "already_extracted",
        note: "Source of original data - may have more detail on references page"
      }
    ],
    output_format: {
      production_start: "YYYY-MM format",
      production_start_precision: "year|month|day",
      production_end: "YYYY-MM format",
      production_end_precision: "year|month|day",
      sources_used: "array of source citations",
      confidence: "0-100",
      notes: "any caveats or uncertainties"
    }
  };

  fs.writeFileSync(taskFile, JSON.stringify(task, null, 2));
  return taskFile;
}
