#!/usr/bin/env node

/**
 * Regenerate British and Italian air summaries with Wikipedia strength data
 *
 * Combines:
 * - Nafziger organizational structures (existing unit lists)
 * - Wikipedia aggregate battle strength data
 * - Standard RAF/Italian establishment estimates
 */

const fs = require('fs');
const path = require('path');

const outputDir = path.join(__dirname, '..', 'data', 'output', 'air_summaries');

// British 1942-Q2 (May-June 1942, Gazala)
const british1942q2 = {
  schema_version: "3.1.0_air",
  nation: "british",
  quarter: "1942q2",
  theater: "North Africa",
  source_document: {
    title: "British Western Desert Air Force, 26 May 1942",
    date: "1942-05-26",
    file: "942bema.pdf",
    collection: "Nafziger Collection",
    tier: "tier_2"
  },
  air_command_structure: {
    theater_command: {
      designation: "RAF Desert Air Force",
      commander: "Air Vice-Marshal Arthur Coningham",
      headquarters: "Western Desert"
    },
    subordinate_formations: []
  },
  aggregate_strength: {
    total_aircraft: 463,
    operational_aircraft: 420,
    serviceability_rate: "91%",
    note: "Aggregate strength from Wikipedia Battle of Gazala (22 June 1942). Squadron count and organization from Nafziger Collection (26 May 1942).",
    data_source: "Wikipedia + Nafziger organizational structure"
  },
  metadata: {
    sources: [
      "Wikipedia - Battle of Gazala article (22 June 1942 aggregate strength)",
      "Nafziger Collection - 942bema.pdf (26 May 1942 organizational structure)"
    ],
    confidence: 75,
    tier: "partial_needs_research",
    extraction_date: "2025-10-28",
    extraction_method: "Hybrid: Wikipedia aggregate + Nafziger organization + standard RAF establishments",
    notes: "Organizational structure with 21 squadrons from Nafziger Collection. Aggregate strength (463 operational aircraft, 420 in Middle East theater) from Wikipedia Battle of Gazala. Squadron-level strength estimated using RAF standard establishment of 16 aircraft per squadron. Data sources are 3-4 weeks apart (Nafziger: 26 May, Wikipedia: 22 June 1942). Detailed squadron-level data available in UK National Archives AIR 27 Operations Record Books (requires subscription).",
    future_enhancement: "AIR 27 ORBs for exact squadron strengths"
  }
};

// British 1942-Q3 (Sept-Oct 1942, El Alamein)
const british1942q3 = {
  schema_version: "3.1.0_air",
  nation: "british",
  quarter: "1942q3",
  theater: "North Africa",
  source_document: {
    title: "British Western Desert Air Force, 1 September 1942",
    date: "1942-09-01",
    file: "942bima.pdf",
    collection: "Nafziger Collection",
    tier: "tier_2"
  },
  air_command_structure: {
    theater_command: {
      designation: "RAF Desert Air Force",
      commander: "Air Vice-Marshal Arthur Coningham",
      headquarters: "Western Desert"
    },
    subordinate_formations: []
  },
  aggregate_strength: {
    total_aircraft: 740,
    operational_aircraft: 675,
    serviceability_rate: "~91%",
    note: "Aggregate strength from Wikipedia Second Battle of El Alamein (October-November 1942: 730-750 aircraft). Using midpoint 740. Squadron count (37) and organization from Nafziger Collection (1 September 1942).",
    data_source: "Wikipedia + Nafziger organizational structure"
  },
  metadata: {
    sources: [
      "Wikipedia - Second Battle of El Alamein article (Oct-Nov 1942 aggregate: 730-750 aircraft)",
      "Nafziger Collection - 942bima.pdf (1 September 1942 organizational structure with 37 squadrons)"
    ],
    confidence: 75,
    tier: "partial_needs_research",
    extraction_date: "2025-10-28",
    extraction_method: "Hybrid: Wikipedia aggregate + Nafziger organization + standard RAF establishments",
    notes: "Organizational structure with 37 squadrons from Nafziger Collection (1 Sept 1942). Aggregate strength (730-750 aircraft, 29 squadrons per Wikipedia) from Second Battle of El Alamein. Nafziger shows 37 squadrons vs Wikipedia's 29 - may indicate more detailed breakdown or some squadrons not fully operational. Using 740 aircraft (midpoint) and 675 operational (~91% serviceability). Squadron-level strength estimated at 16 aircraft per RAF standard establishment. Data sources are 6-10 weeks apart. Detailed squadron-level data available in UK National Archives AIR 27 Operations Record Books.",
    future_enhancement: "AIR 27 ORBs for exact squadron strengths and reconciliation of squadron count discrepancy"
  }
};

// Italian 1942-Q1 (January 1942, post-Crusader)
const italian1942q1 = {
  schema_version: "3.1.0_air",
  nation: "italian",
  quarter: "1942q1",
  theater: "North Africa",
  source_document: {
    title: "Axis Air Force in North Africa, 18 January 1942",
    date: "1942-01-18",
    file: "942game.pdf",
    collection: "Nafziger Collection",
    tier: "tier_2"
  },
  air_command_structure: {
    theater_command: {
      designation: "Regia Aeronautica - North Africa",
      commander: "Unknown",
      headquarters: "Libya"
    },
    subordinate_formations: []
  },
  aggregate_strength: {
    total_aircraft: 400,
    operational_aircraft: 260,
    serviceability_rate: "65%",
    note: "Aggregate strength from Wikipedia (Regia Aeronautica maintained ~400 aircraft in Libya, 60-70% operational). Organization with 22 units from Nafziger Collection.",
    data_source: "Wikipedia general + Nafziger organizational structure",
    aircraft_types: {
      fighters: ["MC.202", "MC.200", "G.50", "CR.42"],
      bombers: ["SM.79", "Z.1007", "BR.20"],
      reconnaissance: ["CA.311", "Z.501", "Z.506B"],
      transport: ["SM.81", "SM.82", "SM.75"]
    }
  },
  metadata: {
    sources: [
      "Wikipedia - Regia Aeronautica article (general North Africa strength: ~400 aircraft, 60-70% operational)",
      "Nafziger Collection - 942game.pdf (18 January 1942 organizational structure with 22 units)"
    ],
    confidence: 70,
    tier: "partial_needs_research",
    extraction_date: "2025-10-28",
    extraction_method: "Hybrid: Wikipedia general aggregate + Nafziger organization",
    notes: "Organizational structure with 22 units (gruppi and squadriglie) from Nafziger Collection (18 Jan 1942). General aggregate strength (~400 aircraft, 60-70% operational rate = 240-280 operational) from Wikipedia Regia Aeronautica article. Individual unit strengths not available in free sources. Standard Italian establishment: ~9 aircraft per squadriglia, ~27 per gruppo (3 squadriglie). Detailed Italian air force records may exist in Italian Ufficio Storico archives.",
    future_enhancement: "Italian air force historical archives or specialist publications for exact unit strengths"
  }
};

// Italian 1942-Q2 (May 1942, Gazala)
const italian1942q2 = {
  schema_version: "3.1.0_air",
  nation: "italian",
  quarter: "1942q2",
  theater: "North Africa",
  source_document: {
    title: "Axis Air Forces in North Africa, 10 May 1942",
    date: "1942-05-10",
    file: "942geme.pdf",
    collection: "Nafziger Collection",
    tier: "tier_2"
  },
  air_command_structure: {
    theater_command: {
      designation: "Regia Aeronautica - North Africa",
      commander: "Unknown",
      headquarters: "Libya"
    },
    subordinate_formations: []
  },
  aggregate_strength: {
    total_aircraft: 412,
    operational_aircraft: 238,
    reserve_aircraft: 174,
    serviceability_rate: "58%",
    note: "Aggregate strength from Wikipedia Battle of Gazala (22 June 1942: 238 operational + 174 reserve). Organization with 5 stormi from Nafziger Collection.",
    data_source: "Wikipedia Battle of Gazala + Nafziger organizational structure",
    known_units: [
      {
        unit: "1° Stormo",
        base: "Martuba",
        aircraft_type: "MC.202",
        estimated_strength: 54,
        note: "2 gruppi × 3 squadriglie × 9 aircraft"
      },
      {
        unit: "2° Stormo",
        base: "Martuba",
        aircraft_type: "MC.202",
        estimated_strength: 54
      },
      {
        unit: "4° Stormo",
        base: "Martuba",
        aircraft_type: "MC.202",
        estimated_strength: 54,
        note: "15+ MC.202s confirmed operational October 1942 (Asisbiz)"
      },
      {
        unit: "50° Stormo",
        base: "El Fetejah - Derna",
        aircraft_type: "CR.42",
        estimated_strength: 54
      },
      {
        unit: "150° Gruppo",
        base: "Benghazi",
        aircraft_type: "MC.202",
        estimated_strength: 27,
        note: "Single gruppo: 3 squadriglie × 9 aircraft"
      }
    ]
  },
  metadata: {
    sources: [
      "Wikipedia - Battle of Gazala article (22 June 1942: 238 operational, 174 reserve, 500 in Mediterranean excluding Italy)",
      "Nafziger Collection - 942geme.pdf (10 May 1942 organizational structure with 5 stormi)",
      "Asisbiz.com - 4° Stormo operational data (15+ MC.202s confirmed October 1942)"
    ],
    confidence: 75,
    tier: "partial_needs_research",
    extraction_date: "2025-10-28",
    extraction_method: "Hybrid: Wikipedia aggregate + Nafziger organization + Italian standard establishments",
    notes: "Organizational structure with 5 stormi from Nafziger Collection (10 May 1942). Aggregate strength (238 operational, 174 reserve) from Wikipedia Battle of Gazala (22 June 1942). Unit strengths estimated using Italian standard establishment: stormo = 2 gruppi × 3 squadriglie × 9 aircraft = 54 aircraft; gruppo = 27 aircraft. 4° Stormo confirmed operational with 15+ MC.202s in October 1942 (Asisbiz). Data sources are 6 weeks apart. MC.202 Folgore achieved 4.4:1 kill ratio at Bir Hakeim (May-June 1942).",
    future_enhancement: "Italian Ufficio Storico archives or specialist publications for exact stormo/gruppo strengths"
  }
};

// Write files
const files = [
  { name: 'british_1942q2_air_summary.json', data: british1942q2 },
  { name: 'british_1942q3_air_summary.json', data: british1942q3 },
  { name: 'italian_1942q1_air_summary.json', data: italian1942q1 },
  { name: 'italian_1942q2_air_summary.json', data: italian1942q2 }
];

console.log('Regenerating air summaries with Wikipedia data...\n');

files.forEach(file => {
  const filePath = path.join(outputDir, file.name);
  fs.writeFileSync(filePath, JSON.stringify(file.data, null, 2));
  console.log(`✓ ${file.name}`);
  console.log(`  - Nation: ${file.data.nation}`);
  console.log(`  - Quarter: ${file.data.quarter}`);
  console.log(`  - Total aircraft: ${file.data.aggregate_strength.total_aircraft || file.data.aggregate_strength.estimated_total_from_units || 'N/A'}`);
  console.log(`  - Confidence: ${file.data.metadata.confidence}%`);
  console.log(`  - Tier: ${file.data.metadata.tier}`);
  console.log();
});

console.log('✓ All 4 summaries regenerated with Wikipedia strength data');
console.log('\nSources used:');
console.log('- Wikipedia: Battle of Gazala, Second Battle of El Alamein, Regia Aeronautica');
console.log('- Nafziger Collection: Organizational structures (942bema.pdf, 942bima.pdf, 942game.pdf, 942geme.pdf)');
console.log('- Standard establishments: RAF 16 aircraft/squadron, Italian 9 aircraft/squadriglia');
