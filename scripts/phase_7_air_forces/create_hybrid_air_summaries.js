#!/usr/bin/env node

/**
 * Create hybrid air summaries combining:
 * - Nafziger unit-level organizational details (squadrons, bases, aircraft types)
 * - Wikipedia aggregate strength data
 * - Estimated per-unit strength based on standard establishments
 */

const fs = require('fs');
const path = require('path');

const outputDir = path.join(__dirname, '..', 'data', 'output', 'air_summaries');

// Read current Nafziger extractions
const british1942q2_nafziger = JSON.parse(
  fs.readFileSync(path.join(outputDir, 'british_1942q2_air_summary.json'), 'utf8')
);
const british1942q3_nafziger = JSON.parse(
  fs.readFileSync(path.join(outputDir, 'british_1942q3_air_summary.json'), 'utf8')
);
const italian1942q1_nafziger = JSON.parse(
  fs.readFileSync(path.join(outputDir, 'italian_1942q1_air_summary.json'), 'utf8')
);
const italian1942q2_nafziger = JSON.parse(
  fs.readFileSync(path.join(outputDir, 'italian_1942q2_air_summary.json'), 'utf8')
);

// British 1942-Q2: Enhance with Wikipedia data
const british1942q2_hybrid = {
  ...british1942q2_nafziger,
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
    note: "Aggregate strength from Wikipedia Battle of Gazala (22 June 1942: 463 total, 420 operational). Squadron details from Nafziger Collection (26 May 1942). Per-squadron strength estimated using RAF standard establishment of 16 aircraft per squadron.",
    data_source: "Wikipedia Battle of Gazala + Nafziger organizational structure",
    by_unit: british1942q2_nafziger.aggregate_strength.by_unit.map(unit => ({
      ...unit,
      estimated_strength: 16, // RAF standard squadron establishment
      note: "Estimated using RAF standard 16 aircraft/squadron"
    }))
  },
  metadata: {
    ...british1942q2_nafziger.metadata,
    sources: [
      "Wikipedia - Battle of Gazala article (22 June 1942: 463 total, 420 operational aircraft)",
      "Nafziger Collection - 942bema.pdf (26 May 1942: organizational structure with 21 squadrons)"
    ],
    confidence: 75,
    tier: "review_recommended",
    extraction_method: "Hybrid: Wikipedia aggregate + Nafziger organization + RAF standard establishments",
    notes: "Organizational structure with 21 squadrons (designations, bases, aircraft types) from Nafziger Collection (26 May 1942). Aggregate strength (463 total, 420 operational, 91% serviceability) from Wikipedia Battle of Gazala (22 June 1942). Per-squadron strength estimated at 16 aircraft using RAF standard establishment. Data sources are 3-4 weeks apart. Detailed squadron-level strength data available in UK National Archives AIR 27 Operations Record Books (requires subscription).",
    future_enhancement: "AIR 27 ORBs for exact squadron strengths"
  }
};

// British 1942-Q3: Enhance with Wikipedia data
const british1942q3_hybrid = {
  ...british1942q3_nafziger,
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
    note: "Aggregate strength from Wikipedia Second Battle of El Alamein (October-November 1942: 730-750 aircraft, using midpoint 740). Squadron details from Nafziger Collection (1 September 1942). Per-squadron strength estimated using RAF standard establishment.",
    data_source: "Wikipedia El Alamein + Nafziger organizational structure",
    by_unit: british1942q3_nafziger.aggregate_strength.by_unit.map(unit => ({
      ...unit,
      estimated_strength: 16, // RAF standard squadron establishment
      note: "Estimated using RAF standard 16 aircraft/squadron"
    }))
  },
  metadata: {
    ...british1942q3_nafziger.metadata,
    sources: [
      "Wikipedia - Second Battle of El Alamein article (Oct-Nov 1942: 730-750 aircraft)",
      "Nafziger Collection - 942bima.pdf (1 September 1942: organizational structure with 37 squadrons)"
    ],
    confidence: 75,
    tier: "review_recommended",
    extraction_method: "Hybrid: Wikipedia aggregate + Nafziger organization + RAF standard establishments",
    notes: "Organizational structure with 37 squadrons (designations, bases, aircraft types) from Nafziger Collection (1 Sept 1942). Aggregate strength (730-750 aircraft per Wikipedia, using midpoint 740 total with 675 operational at ~91% serviceability) from Second Battle of El Alamein (Oct-Nov 1942). Per-squadron strength estimated at 16 aircraft using RAF standard establishment. Data sources are 6-10 weeks apart. Wikipedia mentions 29 squadrons vs Nafziger's 37 - may indicate more detailed breakdown or some squadrons not fully operational. Detailed squadron-level data available in UK National Archives AIR 27 ORBs.",
    future_enhancement: "AIR 27 ORBs for exact squadron strengths and reconciliation of squadron count"
  }
};

// Italian 1942-Q1: Enhance with Wikipedia data
const italian1942q1_hybrid = {
  ...italian1942q1_nafziger,
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
    note: "Aggregate strength from Wikipedia Regia Aeronautica article (~400 aircraft in Libya, 60-70% operational). Unit details from Nafziger Collection. Per-unit strength estimated using Italian standard establishments.",
    data_source: "Wikipedia general + Nafziger organizational structure",
    aircraft_types: {
      fighters: ["MC.202", "MC.200", "G.50", "CR.42"],
      bombers: ["SM.79", "Z.1007", "BR.20"],
      reconnaissance: ["CA.311", "Z.501", "Z.506B"],
      transport: ["SM.81", "SM.82", "SM.75"]
    },
    by_unit: italian1942q1_nafziger.aggregate_strength.by_unit ?
      italian1942q1_nafziger.aggregate_strength.by_unit.map(unit => ({
        ...unit,
        estimated_strength: unit.designation.includes('Stormo') ? 54 : 27,
        note: unit.designation.includes('Stormo') ?
          "Estimated: Stormo = 2 gruppi × 3 squadriglie × 9 aircraft = 54" :
          "Estimated: Gruppo = 3 squadriglie × 9 aircraft = 27"
      })) : []
  },
  metadata: {
    ...italian1942q1_nafziger.metadata,
    sources: [
      "Wikipedia - Regia Aeronautica article (general North Africa: ~400 aircraft, 60-70% operational)",
      "Nafziger Collection - 942game.pdf (18 January 1942: organizational structure with 22 units)"
    ],
    confidence: 70,
    tier: "partial_needs_research",
    extraction_method: "Hybrid: Wikipedia general aggregate + Nafziger organization + Italian standard establishments",
    notes: "Organizational structure with 22 units (gruppi and squadriglie, with bases and aircraft types) from Nafziger Collection (18 Jan 1942). General aggregate strength (~400 aircraft, 60-70% operational = 240-280 operational) from Wikipedia Regia Aeronautica article. Per-unit strength estimated using Italian standard: stormo = 54 aircraft (2 gruppi × 3 squadriglie × 9), gruppo = 27 aircraft (3 squadriglie × 9). Detailed Italian air force records may exist in Italian Ufficio Storico archives.",
    future_enhancement: "Italian Ufficio Storico archives for exact unit strengths"
  }
};

// Italian 1942-Q2: Enhance with Wikipedia data
const italian1942q2_hybrid = {
  ...italian1942q2_nafziger,
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
    note: "Aggregate strength from Wikipedia Battle of Gazala (22 June 1942: 238 operational + 174 reserve). Unit details from Nafziger Collection. Per-unit strength estimated using Italian standard establishments.",
    data_source: "Wikipedia Battle of Gazala + Nafziger organizational structure",
    aircraft_types: {
      fighters: ["MC.202", "MC.200", "CR.42"],
      bombers: ["SM.79"],
      reconnaissance: ["CA.311"]
    },
    by_unit: italian1942q2_nafziger.aggregate_strength.by_unit ?
      italian1942q2_nafziger.aggregate_strength.by_unit.map(unit => {
        const isStormo = unit.designation.includes('Stormo');
        const isGruppo = unit.designation.includes('Gruppo') && !isStormo;
        return {
          ...unit,
          estimated_strength: isStormo ? 54 : (isGruppo ? 27 : 18),
          note: isStormo ?
            "Estimated: Stormo = 2 gruppi × 3 squadriglie × 9 aircraft = 54" :
            (isGruppo ?
              "Estimated: Gruppo = 3 squadriglie × 9 aircraft = 27" :
              "Estimated: Squadriglia = 2 squadrons × 9 aircraft = 18")
        };
      }) : [
        {
          designation: "1° Stormo",
          base: "Martuba",
          aircraft_types: ["MC.202"],
          estimated_strength: 54,
          note: "2 gruppi × 3 squadriglie × 9 aircraft"
        },
        {
          designation: "2° Stormo",
          base: "Martuba",
          aircraft_types: ["MC.202"],
          estimated_strength: 54,
          note: "2 gruppi × 3 squadriglie × 9 aircraft"
        },
        {
          designation: "4° Stormo",
          base: "Martuba",
          aircraft_types: ["MC.202"],
          estimated_strength: 54,
          note: "2 gruppi × 3 squadriglie × 9 aircraft; 15+ MC.202s confirmed operational October 1942 (Asisbiz)"
        },
        {
          designation: "50° Stormo",
          base: "El Fetejah - Derna",
          aircraft_types: ["CR.42"],
          estimated_strength: 54,
          note: "2 gruppi × 3 squadriglie × 9 aircraft"
        },
        {
          designation: "150° Gruppo",
          base: "Benghazi",
          aircraft_types: ["MC.202"],
          estimated_strength: 27,
          note: "Single gruppo: 3 squadriglie × 9 aircraft"
        }
      ]
  },
  metadata: {
    ...italian1942q2_nafziger.metadata,
    sources: [
      "Wikipedia - Battle of Gazala article (22 June 1942: 238 operational, 174 reserve, 500 in Mediterranean excluding Italy)",
      "Nafziger Collection - 942geme.pdf (10 May 1942: organizational structure with 5 stormi)",
      "Asisbiz.com - 4° Stormo operational data (15+ MC.202s confirmed October 1942)"
    ],
    confidence: 75,
    tier: "partial_needs_research",
    extraction_method: "Hybrid: Wikipedia aggregate + Nafziger organization + Italian standard establishments",
    notes: "Organizational structure with 5 stormi (designations, bases, aircraft types) from Nafziger Collection (10 May 1942). Aggregate strength (238 operational, 174 reserve) from Wikipedia Battle of Gazala (22 June 1942). Per-unit strength estimated using Italian standard: stormo = 54 aircraft (2 gruppi × 3 squadriglie × 9), gruppo = 27 aircraft. 4° Stormo confirmed operational with 15+ MC.202s in October 1942 (Asisbiz). Data sources are 6 weeks apart. MC.202 Folgore achieved 4.4:1 kill ratio at Bir Hakeim (May-June 1942).",
    future_enhancement: "Italian Ufficio Storico archives for exact stormo/gruppo strengths"
  }
};

// Write hybrid summaries
const files = [
  { name: 'british_1942q2_air_summary.json', data: british1942q2_hybrid },
  { name: 'british_1942q3_air_summary.json', data: british1942q3_hybrid },
  { name: 'italian_1942q1_air_summary.json', data: italian1942q1_hybrid },
  { name: 'italian_1942q2_air_summary.json', data: italian1942q2_hybrid }
];

console.log('Creating hybrid air summaries (Nafziger + Wikipedia)...\n');

files.forEach(file => {
  const filePath = path.join(outputDir, file.name);
  fs.writeFileSync(filePath, JSON.stringify(file.data, null, 2));

  const unitCount = file.data.aggregate_strength.by_unit?.length || 0;
  const totalAircraft = file.data.aggregate_strength.total_aircraft || 'N/A';

  console.log(`✓ ${file.name}`);
  console.log(`  - Nation: ${file.data.nation}`);
  console.log(`  - Quarter: ${file.data.quarter}`);
  console.log(`  - Units: ${unitCount}`);
  console.log(`  - Total aircraft: ${totalAircraft}`);
  console.log(`  - Confidence: ${file.data.metadata.confidence}%`);
  console.log(`  - Tier: ${file.data.metadata.tier}`);
  console.log();
});

console.log('✓ All 4 hybrid summaries created');
console.log('\nData sources:');
console.log('- Nafziger Collection: Unit designations, bases, aircraft types');
console.log('- Wikipedia: Aggregate strength numbers (Battle of Gazala, El Alamein)');
console.log('- Standard establishments: RAF 16 aircraft/squadron, Italian 54/27/9 per stormo/gruppo/squadriglia');
console.log('\nResult: Best of both worlds - detailed unit lists + aggregate strength data');
