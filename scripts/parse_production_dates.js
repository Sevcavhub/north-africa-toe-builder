#!/usr/bin/env node

/**
 * Parse production_period field into production_start and production_end
 * Format: YYYY-MM with precision_level metadata
 * Maps vague/seasonal dates to approximate months
 * Identifies gaps requiring historical research
 */

const fs = require('fs');
const path = require('path');

const INPUT_JSON = path.join(__dirname, '..', 'data', 'output', 'afv_data', 'afv_complete_with_specs.json');
const OUTPUT_JSON = path.join(__dirname, '..', 'data', 'output', 'afv_data', 'afv_with_normalized_dates.json');
const GAPS_REPORT = path.join(__dirname, '..', 'data', 'output', 'afv_data', 'production_date_gaps.json');

// Month name mappings
const MONTHS = {
  'jan': '01', 'january': '01',
  'feb': '02', 'february': '02',
  'mar': '03', 'march': '03',
  'apr': '04', 'april': '04',
  'may': '05',
  'jun': '06', 'june': '06',
  'jul': '07', 'july': '07',
  'aug': '08', 'august': '08',
  'sep': '09', 'sept': '09', 'september': '09',
  'oct': '10', 'october': '10',
  'nov': '11', 'november': '11',
  'dec': '12', 'december': '12'
};

// Seasonal/vague date mappings
const VAGUE_DATES = {
  // Seasons (use midpoint)
  'spring': '04',  // March-May = April
  'summer': '07',  // June-August = July
  'fall': '10',    // September-November = October
  'autumn': '10',
  'winter': '01',  // December-February = January

  // Relative terms
  'early': '02',   // Q1 midpoint
  'mid': '06',     // Q2-Q3 midpoint
  'late': '11'     // Q4 midpoint
};

/**
 * Parse a single date string (start or end part)
 */
function parseDate(dateStr, isEndDate = false) {
  if (!dateStr || dateStr === '?' || dateStr.trim() === '') {
    return null;
  }

  dateStr = dateStr.trim().toLowerCase();

  const result = {
    value: null,
    precision_level: null,
    original: dateStr,
    needs_research: false,
    vague_mapping: null
  };

  // Pattern 1: "Mon. YYYY" or "Month YYYY" (e.g., "Jul. 1934", "July 1942")
  const monthYearMatch = dateStr.match(/([a-z]+)\.?\s+(19\d{2})/i);
  if (monthYearMatch) {
    const monthName = monthYearMatch[1].toLowerCase();
    const year = monthYearMatch[2];
    const month = MONTHS[monthName];

    if (month) {
      result.value = `${year}-${month}`;
      result.precision_level = 'month';
      return result;
    }
  }

  // Pattern 2: "YYYY-MM" already in correct format
  if (dateStr.match(/^19\d{2}-\d{2}$/)) {
    result.value = dateStr;
    result.precision_level = 'month';
    return result;
  }

  // Pattern 3: Just year "YYYY" or "19??-YYYY" or "'YY"
  const yearOnlyMatch = dateStr.match(/\b(19\d{2})\b|'(\d{2})\b/);
  if (yearOnlyMatch) {
    const year = yearOnlyMatch[1] || `19${yearOnlyMatch[2]}`;
    // For end dates with year only, use December; for start dates use January
    const month = isEndDate ? '12' : '01';
    result.value = `${year}-${month}`;
    result.precision_level = 'year';
    return result;
  }

  // Pattern 4: Short year format "42" or "43"
  const shortYearMatch = dateStr.match(/\b(\d{2})\b/);
  if (shortYearMatch && !dateStr.includes('19')) {
    const year = `19${shortYearMatch[1]}`;
    const month = isEndDate ? '12' : '01';
    result.value = `${year}-${month}`;
    result.precision_level = 'year';
    return result;
  }

  // Pattern 5: Seasonal/vague dates (e.g., "Spring 1941", "early 1942", "Late 1943")
  for (const [term, month] of Object.entries(VAGUE_DATES)) {
    const vagueDateMatch = dateStr.match(new RegExp(`\\b${term}\\b[\\s-]*(19\\d{2})`, 'i'));
    if (vagueDateMatch) {
      result.value = `${vagueDateMatch[1]}-${month}`;
      result.precision_level = 'vague';
      result.vague_mapping = term;
      return result;
    }
  }

  // Pattern 6: "mid YYYY" or "early YYYY" without hyphen
  const vagueYearMatch = dateStr.match(/\b(early|mid|late)\s+(19\d{2})\b/i);
  if (vagueYearMatch) {
    const term = vagueYearMatch[1].toLowerCase();
    const year = vagueYearMatch[2];
    const month = VAGUE_DATES[term];
    result.value = `${year}-${month}`;
    result.precision_level = 'vague';
    result.vague_mapping = term;
    return result;
  }

  // Pattern 7: "19??", "n.a.", or completely unknown
  if (dateStr === '19??' || dateStr === 'n.a.' || dateStr === '?') {
    result.value = null;
    result.precision_level = null;
    result.needs_research = true;
    return result;
  }

  // If we couldn't parse it, mark for research
  result.value = null;
  result.precision_level = null;
  result.needs_research = true;
  return result;
}

/**
 * Parse production_period field
 */
function parseProductionPeriod(period) {
  if (!period || period === 'n.a.') {
    return {
      production_start: null,
      production_start_precision: null,
      production_end: null,
      production_end_precision: null,
      original_production_period: period || 'n.a.',
      needs_research: true,
      parse_notes: 'No production period data available'
    };
  }

  // Split on common separators: "-", "to", "–"
  const parts = period.split(/\s*[-–]\s*|\s+to\s+/i);

  if (parts.length === 1) {
    // Single date (production start only or single year)
    const startDate = parseDate(parts[0], false);
    return {
      production_start: startDate.value,
      production_start_precision: startDate.precision_level,
      production_start_vague_mapping: startDate.vague_mapping,
      production_end: null,
      production_end_precision: null,
      original_production_period: period,
      needs_research: startDate.needs_research || true, // Single date needs end date research
      parse_notes: 'Only start date or single year available'
    };
  }

  // Two or more parts: start and end (ignore extra parts)
  const startDate = parseDate(parts[0], false);
  const endDate = parts[1] ? parseDate(parts[1], true) : null;

  return {
    production_start: startDate ? startDate.value : null,
    production_start_precision: startDate ? startDate.precision_level : null,
    production_start_vague_mapping: startDate ? startDate.vague_mapping : null,
    production_end: endDate ? endDate.value : null,
    production_end_precision: endDate ? endDate.precision_level : null,
    production_end_vague_mapping: endDate ? endDate.vague_mapping : null,
    original_production_period: period,
    needs_research: (startDate && startDate.needs_research) || (endDate && endDate.needs_research) || !endDate,
    parse_notes: (startDate && startDate.needs_research) || (endDate && endDate.needs_research)
      ? 'Contains unparseable dates requiring research'
      : (startDate && startDate.vague_mapping) || (endDate && endDate.vague_mapping)
      ? 'Contains vague dates mapped to approximate months'
      : 'Successfully parsed with month precision'
  };
}

/**
 * Main processing function
 */
function processAllVehicles() {
  console.log('Loading AFV data...');
  const vehicles = JSON.parse(fs.readFileSync(INPUT_JSON, 'utf-8'));

  console.log(`Processing ${vehicles.length} vehicles...\n`);

  const gaps = {
    total_vehicles: vehicles.length,
    vehicles_with_complete_dates: 0,
    vehicles_with_vague_dates: 0,
    vehicles_needing_research: 0,
    research_list: []
  };

  const processed = vehicles.map((vehicle, index) => {
    const parsed = parseProductionPeriod(vehicle.production_period);

    // Track statistics
    if (!parsed.needs_research && parsed.production_start && parsed.production_end) {
      gaps.vehicles_with_complete_dates++;
    }

    if (parsed.production_start_vague_mapping || parsed.production_end_vague_mapping) {
      gaps.vehicles_with_vague_dates++;
    }

    if (parsed.needs_research) {
      gaps.vehicles_needing_research++;
      gaps.research_list.push({
        vehicle_name: vehicle.vehicle_name,
        country: vehicle.country,
        url: vehicle.url,
        original_production_period: parsed.original_production_period,
        issue: parsed.parse_notes,
        production_start: parsed.production_start,
        production_end: parsed.production_end
      });
    }

    // Log progress every 20 vehicles
    if ((index + 1) % 20 === 0) {
      console.log(`  Processed ${index + 1}/${vehicles.length} vehicles...`);
    }

    return {
      ...vehicle,
      ...parsed
    };
  });

  console.log('\n✓ Processing complete!\n');
  console.log('Statistics:');
  console.log(`  Total vehicles: ${gaps.total_vehicles}`);
  console.log(`  Complete dates: ${gaps.vehicles_with_complete_dates} (${Math.round(gaps.vehicles_with_complete_dates / gaps.total_vehicles * 100)}%)`);
  console.log(`  Vague dates (mapped): ${gaps.vehicles_with_vague_dates} (${Math.round(gaps.vehicles_with_vague_dates / gaps.total_vehicles * 100)}%)`);
  console.log(`  Needs research: ${gaps.vehicles_needing_research} (${Math.round(gaps.vehicles_needing_research / gaps.total_vehicles * 100)}%)`);

  // Save processed data
  console.log('\nSaving files...');
  fs.writeFileSync(OUTPUT_JSON, JSON.stringify(processed, null, 2));
  console.log(`  ✓ Saved normalized dates: ${OUTPUT_JSON}`);

  fs.writeFileSync(GAPS_REPORT, JSON.stringify(gaps, null, 2));
  console.log(`  ✓ Saved gaps report: ${GAPS_REPORT}`);

  return { processed, gaps };
}

// Run the processor
processAllVehicles();
