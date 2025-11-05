#!/usr/bin/env node

/**
 * Generate American (USAAF) air summaries for North Africa
 *
 * Quarters:
 * - 1942-Q4: Operation Torch (November 8, 1942), Twelfth Air Force
 * - 1943-Q1: Tunisia Campaign, Northwest African Air Forces
 *
 * Sources: Wikipedia, Twelfth Air Force records, NAAF organizational data
 */

const fs = require('fs');
const path = require('path');

const outputDir = path.join(__dirname, '..', 'data', 'output', 'air_summaries');

// American 1942-Q4 (Operation Torch, Nov-Dec 1942)
const american1942q4 = {
  schema_version: "3.1.0_air",
  nation: "american",
  quarter: "1942q4",
  theater: "North Africa",
  source_document: {
    title: "Twelfth Air Force - Operation Torch",
    date: "1942-11-08",
    file: "online_research",
    collection: "Wikipedia + USAAF Records",
    tier: "tier_2"
  },
  air_command_structure: {
    theater_command: {
      designation: "Twelfth Air Force",
      commander: "Major General James H. Doolittle",
      headquarters: "Algeria (Oran)"
    },
    subordinate_formations: [
      {
        designation: "XII Bomber Command",
        note: "Heavy and medium bombardment groups"
      },
      {
        designation: "XII Fighter Command",
        note: "Fighter and fighter-bomber groups"
      },
      {
        designation: "51st Troop Carrier Wing",
        note: "Transport operations"
      }
    ]
  },
  aggregate_strength: {
    total_aircraft: 500,
    operational_aircraft: 400,
    serviceability_rate: "~80%",
    note: "Aggregate estimate for Operation Torch (November 8, 1942). Twelfth Air Force initially consisted of ~11 groups: 2 heavy bomb, 2 P-38 fighter, 2 Spitfire fighter, 3 medium bomb, 1 light bomb, 1 transport. Carrier-based included 76 P-40F Warhawks plus Navy aircraft. Total USAAF strength ~500 aircraft for Operation Torch.",
    data_source: "Twelfth Air Force organizational records + Operation Torch data",
    by_unit_composition: {
      total_groups: 11,
      heavy_bomb_groups: 2,
      fighter_groups: 4,
      medium_bomb_groups: 3,
      light_bomb_groups: 1,
      transport_groups: 1
    },
    primary_aircraft_types: ["B-17 Flying Fortress", "B-25 Mitchell", "B-26 Marauder", "P-38 Lightning", "P-40 Warhawk", "Spitfire", "C-47 Dakota"]
  },
  metadata: {
    sources: [
      "Wikipedia - Twelfth Air Force (activated 20 Aug 1942, deployed 24 Oct 1942)",
      "Operation Torch records (8 November 1942)",
      "Twelfth Air Force composition: 11 groups initially",
      "Carrier-based: 76 P-40F Warhawks + Navy aircraft"
    ],
    confidence: 70,
    tier: "partial_needs_research",
    extraction_date: "2025-10-29",
    extraction_method: "Organizational records + Operation Torch data + group strength estimates",
    notes: "Twelfth Air Force activated 20 Aug 1942 under Brig Gen Doolittle (promoted Maj Gen). Deployed to North Africa 24 Oct-8 Nov 1942 for Operation Torch. Initial composition: 2 heavy bomb (B-17), 2 P-38 fighter, 2 Spitfire fighter, 3 medium bomb (B-25/B-26), 1 light bomb, 1 transport. Estimated ~500 aircraft total, ~400 operational (~80% serviceability typical for new deployment). Operated west of Cape Tenez under Patton's command. RAF operated east under Air Marshal Welsh.",
    future_enhancement: "USAAF historical records for exact group strengths November 1942"
  }
};

// American 1943-Q1 (Tunisia Campaign, Jan-Mar 1943)
const american1943q1 = {
  schema_version: "3.1.0_air",
  nation: "american",
  quarter: "1943q1",
  theater: "North Africa",
  source_document: {
    title: "Northwest African Air Forces - Tunisia Campaign",
    date: "1943-02-18",
    file: "online_research",
    collection: "NAAF + Tunisia Campaign Records",
    tier: "tier_2"
  },
  air_command_structure: {
    theater_command: {
      designation: "Northwest African Air Forces (NAAF)",
      commander: "Lieutenant General Carl Spaatz",
      headquarters: "Algeria",
      note: "Created February 18, 1943, combining all Allied air forces"
    },
    subordinate_formations: [
      {
        designation: "Northwest African Strategic Air Force (NASAF)",
        commander: "Major General James H. Doolittle",
        note: "Heavy bombardment - former Twelfth AF commander"
      },
      {
        designation: "Northwest African Tactical Air Force (NATAF)",
        commander: "Air Vice-Marshal Arthur Coningham",
        note: "Tactical air support - includes USAAF elements"
      },
      {
        designation: "Twelfth Air Force (subordinate to NAAF)",
        note: "USAAF component of NAAF"
      }
    ]
  },
  aggregate_strength: {
    total_aircraft: 190,
    operational_aircraft: 150,
    serviceability_rate: "~79%",
    note: "Aggregate USAAF component estimate for Tunisia Campaign (Jan-Mar 1943). Early 1943: total Allied 480 aircraft vs Axis 690. USAAF estimated ~35-40% of Allied total = ~170-190 aircraft. Reorganized under NAAF (Feb 18, 1943) with Lt Gen Spaatz commanding.",
    data_source: "Tunisia Campaign records + NAAF organization",
    by_unit_composition: {
      note: "USAAF component of Northwest African Air Forces",
      primary_commands: ["NASAF (strategic bombing)", "NATAF (tactical support component)", "NACAF (coastal component)"],
      estimated_groups: "12-15 groups (fighters, medium/heavy bombers)"
    },
    primary_aircraft_types: ["B-17 Flying Fortress", "B-25 Mitchell", "B-26 Marauder", "P-38 Lightning", "P-40 Warhawk", "P-39 Airacobra", "A-20 Havoc"]
  },
  metadata: {
    sources: [
      "Northwest African Air Forces (NAAF) created February 18, 1943",
      "Tunisia Campaign: Early 1943 total Allied 480 aircraft vs Axis 690",
      "NAAF under Lt Gen Carl Spaatz (USAAF)",
      "NASAF under Maj Gen James Doolittle (former Twelfth AF commander)",
      "USAAF component estimated 35-40% of total Allied strength"
    ],
    confidence: 72,
    tier: "partial_needs_research",
    extraction_date: "2025-10-29",
    extraction_method: "Campaign records + organizational data + Allied total calculation",
    notes: "Tunisia Campaign (Jan-May 1943) saw reorganization of Allied air forces. Early 1943: Axis had numerical superiority (690 vs 480 Allied). NAAF created Feb 18 under Lt Gen Spaatz (USAAF) to unify command. USAAF component (Twelfth AF elements + Ninth AF heavy bombers) estimated ~35-40% of Allied total = ~170-190 aircraft, ~150 operational. By May, Allied air superiority achieved (2,000+ sorties on May 6). USAAF groups included fighters (1st, 14th, 33rd, 82nd FG) and bombers (12th, 310th, 321st, 340th BG).",
    future_enhancement: "USAAF records for exact Twelfth AF strength January-March 1943"
  }
};

// Write files
const files = [
  { name: 'american_1942q4_air_summary.json', data: american1942q4 },
  { name: 'american_1943q1_air_summary.json', data: american1943q1 }
];

console.log('Generating American (USAAF) air summaries for North Africa...\n');

files.forEach(file => {
  const filePath = path.join(outputDir, file.name);

  fs.writeFileSync(filePath, JSON.stringify(file.data, null, 2));

  console.log(`✓ ${file.name}`);
  console.log(`  - Nation: ${file.data.nation}`);
  console.log(`  - Quarter: ${file.data.quarter}`);
  console.log(`  - Total aircraft: ${file.data.aggregate_strength.total_aircraft}`);
  console.log(`  - Operational: ${file.data.aggregate_strength.operational_aircraft}`);
  console.log(`  - Confidence: ${file.data.metadata.confidence}%`);
  console.log(`  - Tier: ${file.data.metadata.tier}`);
  console.log();
});

console.log('='.repeat(60));
console.log('✓ Generated 2 American (USAAF) air summaries');
console.log('  - 1942-Q4: Operation Torch (500 aircraft, 11 groups)');
console.log('  - 1943-Q1: Tunisia Campaign (190 aircraft, NAAF component)');
console.log('='.repeat(60));
console.log('\nTotal coverage now: 23 quarterly summaries (4 nations)');
console.log('- German: 7 summaries');
console.log('- British: 7 summaries');
console.log('- Italian: 7 summaries');
console.log('- American: 2 summaries');
console.log('\nAll sources: Freely available online (Wikipedia, USAAF records, campaign data)');
