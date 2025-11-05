#!/usr/bin/env node

/**
 * Batch Research Processor for Production Dates
 * Processes 10 vehicles at a time with Task agents
 */

const fs = require('fs');
const path = require('path');

const RESULTS_FILE = path.join(__dirname, '..', 'data', 'output', 'afv_data', 'production_date_research_results.json');
const BATCH_DIR = path.join(__dirname, '..', 'data', 'output', 'afv_data', 'research_batches');
const BATCH_SIZE = 10;

// Ensure batch directory exists
if (!fs.existsSync(BATCH_DIR)) {
  fs.mkdirSync(BATCH_DIR, { recursive: true });
}

// Load research results
const results = JSON.parse(fs.readFileSync(RESULTS_FILE, 'utf-8'));
const vehiclesNeedingResearch = results.web_research_needed;

console.log('='.repeat(80));
console.log('AFV Production Date Research - Batch Processor');
console.log('='.repeat(80));
console.log();
console.log(`Total vehicles needing web research: ${vehiclesNeedingResearch.length}`);
console.log(`Batch size: ${BATCH_SIZE}`);
console.log(`Total batches: ${Math.ceil(vehiclesNeedingResearch.length / BATCH_SIZE)}`);
console.log();

// Split into batches
const batches = [];
for (let i = 0; i < vehiclesNeedingResearch.length; i += BATCH_SIZE) {
  batches.push(vehiclesNeedingResearch.slice(i, i + BATCH_SIZE));
}

// Generate batch files with research prompts
console.log('Generating batch files...\n');

batches.forEach((batch, batchIndex) => {
  const batchNumber = batchIndex + 1;
  const batchFile = path.join(BATCH_DIR, `batch_${batchNumber}_research_prompts.json`);

  const batchData = {
    batch_number: batchNumber,
    total_batches: batches.length,
    vehicles_in_batch: batch.length,
    status: 'pending',
    created_at: new Date().toISOString(),
    vehicles: batch.map((vehicle, idx) => ({
      index: idx + 1,
      vehicle_name: vehicle.vehicle_name,
      country: vehicle.country,
      original_production_period: vehicle.original_production_period,
      onwar_url: vehicle.url,
      research_prompt: generateResearchPrompt(vehicle),
      result: null
    }))
  };

  fs.writeFileSync(batchFile, JSON.stringify(batchData, null, 2));
  console.log(`✓ Created batch ${batchNumber}: ${batch.length} vehicles`);
  batch.forEach((v, idx) => {
    console.log(`    ${idx + 1}. [${v.country}] ${v.vehicle_name}`);
  });
  console.log();
});

console.log('='.repeat(80));
console.log('Batch files created!');
console.log('='.repeat(80));
console.log();
console.log('Next steps:');
console.log('1. Claude will process Batch 1 (10 vehicles) using Task agents');
console.log('2. You review the results');
console.log('3. Claude continues with Batch 2, etc.');
console.log();
console.log(`Batch files location: ${BATCH_DIR}`);
console.log();

/**
 * Generate a research prompt for historical_research agent
 */
function generateResearchPrompt(vehicle) {
  return `Research the production dates for the ${vehicle.vehicle_name} (${vehicle.country}).

**Current data:**
- Original production period: ${vehicle.original_production_period}
- OnWar URL: ${vehicle.url}

**Research sources to check:**
1. **wwiitanks.co.uk** - Search for vehicle name and production dates
2. **OnWar references** - Check the references cited for this vehicle
3. **Cross-reference** - Verify dates across multiple sources

**Required output format:**
\`\`\`json
{
  "vehicle_name": "${vehicle.vehicle_name}",
  "country": "${vehicle.country}",
  "research_results": {
    "production_start": "YYYY-MM",
    "production_start_precision": "year|month|day",
    "production_end": "YYYY-MM",
    "production_end_precision": "year|month|day",
    "sources_used": [
      {
        "source": "wwiitanks.co.uk",
        "url": "exact URL",
        "excerpt": "verbatim quote with dates"
      }
    ],
    "confidence": 75,
    "notes": "Any caveats or uncertainties"
  }
}
\`\`\`

**Search strategy:**
1. Go to https://wwiitanks.co.uk and search for "${vehicle.vehicle_name}"
2. Look for "Production" or "Manufactured" sections
3. Extract start and end dates
4. Cross-reference with OnWar data if possible
5. Return structured JSON with YYYY-MM dates

Focus on finding exact month/year if possible. If only year available, use January for start and December for end.`;
}
