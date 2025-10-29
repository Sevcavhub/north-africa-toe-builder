#!/usr/bin/env node

/**
 * Generate final 9 quarterly air summaries to complete coverage
 *
 * Quarters filled:
 * - 1941-Q3: German, British, Italian (pre-Crusader)
 * - 1942-Q3: German, Italian (British already exists)
 * - 1942-Q4: German, Italian (British already exists)
 * - 1943-Q1: British, Italian (German already exists)
 *
 * Sources: Wikipedia, battle records, campaign data (all freely available online)
 */

const fs = require('fs');
const path = require('path');

const outputDir = path.join(__dirname, '..', 'data', 'output', 'air_summaries');

// ========== 1941-Q3 (September-October, pre-Crusader) ==========

// German 1941-Q3
const german1941q3 = {
  schema_version: "3.1.0_air",
  nation: "german",
  quarter: "1941q3",
  theater: "North Africa",
  source_document: {
    title: "Fliegerführer Afrika - Pre-Crusader",
    date: "1941-09-15",
    file: "online_research",
    collection: "Wikipedia + Battle Records",
    tier: "tier_3"
  },
  air_command_structure: {
    theater_command: {
      designation: "Fliegerführer Afrika",
      commander: "Generalmajor Stefan Fröhlich",
      headquarters: "Libya"
    },
    subordinate_formations: []
  },
  aggregate_strength: {
    total_aircraft: 120,
    operational_aircraft: 65,
    serviceability_rate: "~54%",
    note: "Aggregate estimate for September 1941 based on November data (140 aircraft, 76 operational on 15 November). II./JG 27 arrived 14 September, strengthening fighter forces. Reinforcement from Greece available (Fliegerkorps X: 181 aircraft, 104 operational).",
    data_source: "Operation Crusader battle records extrapolated to Q3",
    primary_units: ["JG 27", "Stab JG 27", "I./JG 27", "II./JG 27 (arrived Sept 14)"]
  },
  metadata: {
    sources: [
      "Wikipedia - Operation Crusader (15 November 1941 strength: 140 aircraft, 76 operational)",
      "Luftwaffe records - II./JG 27 arrival 14 September 1941"
    ],
    confidence: 60,
    tier: "partial_needs_research",
    extraction_date: "2025-10-29",
    extraction_method: "Battle records extrapolation + campaign data",
    notes: "Estimated strength for September 1941 based on documented November data (140 aircraft, 76 operational at Operation Crusader start). Serviceability rate ~54% typical for Luftwaffe in North Africa. II./JG 27 arrived mid-September, increasing fighter strength. Fliegerkorps X in Greece (181 aircraft) available for reinforcement. Exact unit-level breakdown not available in free sources.",
    future_enhancement: "Bundesarchiv Luftwaffe monthly strength reports"
  }
};

// British 1941-Q3
const british1941q3 = {
  schema_version: "3.1.0_air",
  nation: "british",
  quarter: "1941q3",
  theater: "North Africa",
  source_document: {
    title: "RAF Middle East - Pre-Crusader Buildup",
    date: "1941-10-01",
    file: "online_research",
    collection: "Wikipedia + RAF Records",
    tier: "tier_2"
  },
  air_command_structure: {
    theater_command: {
      designation: "RAF Middle East Command",
      commander: "Air Chief Marshal Arthur Tedder",
      headquarters: "Cairo"
    },
    subordinate_formations: [
      {
        designation: "Air Headquarters Western Desert",
        commander: "Air Vice-Marshal Arthur Coningham",
        note: "Created 21 October 1941 by upgrading 204 Group"
      }
    ]
  },
  aggregate_strength: {
    total_aircraft: 800,
    operational_aircraft: 730,
    serviceability_rate: "~91%",
    note: "Aggregate strength for October 1941 from RAF Middle East records. Sources report 16-27 squadrons (debate exists), with 600-1,000 aircraft available to Air Marshal Tedder. Using conservative estimate of 800 aircraft across ~20 squadrons.",
    data_source: "RAF Middle East pre-Crusader strength + Wikipedia",
    by_unit_composition: {
      squadrons_total: 20,
      fighters_short_range: 11,
      fighters_long_range: 2,
      bombers_medium: 5,
      reconnaissance: 2
    }
  },
  metadata: {
    sources: [
      "Wikipedia - Desert Air Force (October 1941: 16 squadrons OR 27 squadrons per different sources)",
      "RAF records - 600-1,000 aircraft available to Tedder in Cairo",
      "Air HQ Western Desert created 21 October 1941"
    ],
    confidence: 70,
    tier: "partial_needs_research",
    extraction_date: "2025-10-29",
    extraction_method: "RAF records aggregate + standard RAF establishments",
    notes: "Conservative estimate (800 aircraft, 20 squadrons) for October 1941 pre-Crusader period. Sources conflict on squadron count (16 vs 27), likely due to counting methods (operational vs total, or excluding reserve/training units). Air HQ Western Desert created 21 October 1941. RAF standard establishment ~16 aircraft per squadron. Detailed squadron identities available in UK National Archives AIR 27.",
    future_enhancement: "AIR 27 ORBs for exact squadron list and strengths"
  }
};

// Italian 1941-Q3
const italian1941q3 = {
  schema_version: "3.1.0_air",
  nation: "italian",
  quarter: "1941q3",
  theater: "North Africa",
  source_document: {
    title: "Regia Aeronautica Libya - Pre-Crusader",
    date: "1941-09-01",
    file: "online_research",
    collection: "Wikipedia + Historical Records",
    tier: "tier_3"
  },
  air_command_structure: {
    theater_command: {
      designation: "Regia Aeronautica - Libya",
      commander: "Unknown",
      headquarters: "Libya"
    },
    subordinate_formations: []
  },
  aggregate_strength: {
    total_aircraft: 400,
    operational_aircraft: 240,
    serviceability_rate: "~60%",
    note: "Aggregate strength from general Regia Aeronautica Libya records (~400 aircraft maintained). After heavy losses in early 1941 (Operation Compass), reinforced with Rommel's arrival. Operational rate 60% typical for Italian forces in North Africa.",
    data_source: "Regia Aeronautica historical records"
  },
  metadata: {
    sources: [
      "Wikipedia - Regia Aeronautica (maintained ~400 aircraft in Libya)",
      "Historical records - Reinforcements arrived with Rommel after early 1941 losses"
    ],
    confidence: 60,
    tier: "partial_needs_research",
    extraction_date: "2025-10-29",
    extraction_method: "Historical records aggregate estimate",
    notes: "General strength estimate (~400 aircraft) for Libya theater in September-October 1941. After Operation Compass losses (300-400 aircraft lost by January 1941), Regia Aeronautica reinforced with new aircraft types (MC.200, MC.202) arriving with Rommel. Operational rate ~60% typical. Exact unit breakdown not available in free sources. Italian archives (Ufficio Storico) would have detailed gruppo strengths.",
    future_enhancement: "Italian Ufficio Storico archives for exact gruppo/squadriglia breakdown"
  }
};

// ========== 1942-Q3 (August-September, between Gazala and El Alamein) ==========

// German 1942-Q3
const german1942q3 = {
  schema_version: "3.1.0_air",
  nation: "german",
  quarter: "1942q3",
  theater: "North Africa",
  source_document: {
    title: "Luftwaffe North Africa - Pre-El Alamein",
    date: "1942-08-31",
    file: "online_research",
    collection: "Battle Records + Wikipedia",
    tier: "tier_3"
  },
  air_command_structure: {
    theater_command: {
      designation: "Luftflotte 2 (Africa Component)",
      commander: "Generalfeldmarschall Albert Kesselring",
      headquarters: "Sicily/Libya"
    },
    subordinate_formations: []
  },
  aggregate_strength: {
    total_aircraft: 200,
    operational_aircraft: 140,
    serviceability_rate: "~70%",
    note: "Aggregate estimate for August-September 1942 before El Alamein buildup. Weakened by continuous losses and supply issues. Could mount only 1 sortie for every 5 flown by Allies. By October El Alamein, Axis had 350 aircraft total (German ~45% = 157).",
    data_source: "El Alamein battle records extrapolated to Q3",
    primary_aircraft_types: ["Bf 109F/G", "Bf 110", "Ju 87", "Ju 88"]
  },
  metadata: {
    sources: [
      "Wikipedia - Second Battle of El Alamein (October 1942: 350 Axis aircraft total)",
      "Battle records - Luftwaffe operational challenges August-September 1942",
      "JG 27 and III./JG 53 primary fighter units"
    ],
    confidence: 60,
    tier: "partial_needs_research",
    extraction_date: "2025-10-29",
    extraction_method: "Battle records extrapolation + campaign data",
    notes: "Estimated ~200 aircraft for August-September 1942, reduced from May peak (542 aircraft) due to attrition and transfers. By Battle of Alam el Halfa (Aug 31), Luftwaffe faced severe numerical inferiority. October El Alamein saw 350 total Axis aircraft (German ~45% = 157), suggesting Q3 had ~200 before final buildup. Serviceability challenges throughout period.",
    future_enhancement: "Bundesarchiv monthly strength reports for exact August-September data"
  }
};

// Italian 1942-Q3
const italian1942q3 = {
  schema_version: "3.1.0_air",
  nation: "italian",
  quarter: "1942q3",
  theater: "North Africa",
  source_document: {
    title: "Regia Aeronautica North Africa - Alam el Halfa",
    date: "1942-08-31",
    file: "online_research",
    collection: "Comando Supremo + Battle Records",
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
    total_aircraft: 372,
    operational_aircraft: 260,
    serviceability_rate: "70%",
    note: "Aggregate from July 1942 Italian reports. Operational availability 60-70%. This period considered peak of Italian fighter arm in Africa. For Alam el Halfa (Aug 31), Italian aircraft showed 60% combat readiness vs RAF 73-77%. Italian aircraft = 55% of total Axis air power.",
    data_source: "Comando Supremo + Battle of Alam el Halfa records",
    aircraft_breakdown: {
      mc202_folgore: 93,
      mc200_fighter: 46,
      mc200_fighter_bomber: 50,
      g50_freccia: 43,
      cr42_falco: 40,
      sm79_sparviero: 34,
      z1007_alcyone: 25,
      ca311: 24,
      z501: 17
    }
  },
  metadata: {
    sources: [
      "Comando Supremo - Italian aircraft in North Africa July 1942 breakdown",
      "Battle of Alam el Halfa records (Aug 31, 1942: 60% Italian combat readiness)",
      "Italian aircraft = 55% of Panzer Army Afrika air power"
    ],
    confidence: 75,
    tier: "partial_needs_research",
    extraction_date: "2025-10-29",
    extraction_method: "Italian military records + battle data",
    notes: "Detailed breakdown from Italian sources for July 1942: 93 MC.202, 46+50 MC.200, 43 G.50, 40 CR.42 fighters; 34 SM.79, 25 Z.1007 bombers; 24 CA.311, 17 Z.501 recon. Total 372 aircraft, 60-70% operational (260 aircraft). Peak period for Italian fighter arm. Combat readiness 60% for Alam el Halfa vs RAF 73-77%. Italian component = 55% of total Axis air power.",
    future_enhancement: "Italian Ufficio Storico for exact stormo/gruppo assignments"
  }
};

// ========== 1942-Q4 (October-December, El Alamein and retreat) ==========

// German 1942-Q4 (upgrade from partial)
const german1942q4 = {
  schema_version: "3.1.0_air",
  nation: "german",
  quarter: "1942q4",
  theater: "North Africa",
  source_document: {
    title: "Luftwaffe - El Alamein and Retreat to Tunisia",
    date: "1942-10-23",
    file: "online_research",
    collection: "El Alamein Battle Records",
    tier: "tier_2"
  },
  air_command_structure: {
    theater_command: {
      designation: "Luftflotte 2 (Africa Component)",
      commander: "Generalfeldmarschall Albert Kesselring",
      headquarters: "Sicily/Tunisia"
    },
    subordinate_formations: []
  },
  aggregate_strength: {
    total_aircraft: 157,
    operational_aircraft: 110,
    serviceability_rate: "~70%",
    note: "Aggregate from El Alamein battle records. Total Axis: 350 aircraft, German = 45% (Italian = 55%). Severe numerical inferiority vs British 1,500 aircraft. Allied air/submarine attacks on supply lines prevented adequate replenishment. Forced retreat to Tunisia by November.",
    data_source: "Second Battle of El Alamein records",
    primary_aircraft_types: ["Bf 109F/G", "Bf 110", "Ju 87", "Ju 88"]
  },
  metadata: {
    sources: [
      "Wikipedia - Second Battle of El Alamein (October 1942: 350 Axis vs 1,500 British)",
      "Battle records - German = 45% of Axis air strength",
      "Retreat timeline: 15 November Derna captured, Martuba airfield lost"
    ],
    confidence: 72,
    tier: "partial_needs_research",
    extraction_date: "2025-10-29",
    extraction_method: "Battle records calculation from Axis totals",
    notes: "At El Alamein (Oct 23-Nov 11), total Axis air strength 350 aircraft. German component ~45% = 157 aircraft, ~70% operational = 110 aircraft. Severe numerical inferiority (1:4.3 ratio vs British 1,500). Supply line attacks prevented fuel/ammunition resupply. Panzerarmee Afrika crushed and forced to retreat from Egypt/Libya to Tunisia. Martuba airfield captured 15 November, reducing forward basing.",
    future_enhancement: "Bundesarchiv for exact unit identities and daily strength during retreat"
  }
};

// Italian 1942-Q4
const italian1942q4 = {
  schema_version: "3.1.0_air",
  nation: "italian",
  quarter: "1942q4",
  theater: "North Africa",
  source_document: {
    title: "Regia Aeronautica - El Alamein and Withdrawal",
    date: "1942-10-23",
    file: "online_research",
    collection: "El Alamein Battle Records",
    tier: "tier_2"
  },
  air_command_structure: {
    theater_command: {
      designation: "Regia Aeronautica - North Africa",
      commander: "Unknown",
      headquarters: "Libya / Tunisia"
    },
    subordinate_formations: []
  },
  aggregate_strength: {
    total_aircraft: 193,
    operational_aircraft: 135,
    serviceability_rate: "~70%",
    note: "Aggregate from El Alamein battle records. Total Axis: 350 aircraft, Italian = 55% (German = 45%). Progressively withdrawn from Egypt → Tobruk → Benghazi → Tripoli → Tunisia following Panzerarmee Afrika defeat. Heavy losses during retreat.",
    data_source: "Second Battle of El Alamein records",
    primary_aircraft_types: ["MC.202 Folgore", "MC.200 Saetta", "G.50 Freccia", "CR.42 Falco", "SM.79 Sparviero"]
  },
  metadata: {
    sources: [
      "Wikipedia - Second Battle of El Alamein (October 1942: 350 Axis total)",
      "Italian component = 55% of Axis air strength",
      "Progressive withdrawal: Egypt → Tobruk → Benghazi → Tripoli → Tunisia"
    ],
    confidence: 72,
    tier: "partial_needs_research",
    extraction_date: "2025-10-29",
    extraction_method: "Battle records calculation from Axis totals",
    notes: "At El Alamein (Oct 23-Nov 11), total Axis 350 aircraft. Italian component ~55% = 193 aircraft, ~70% operational = 135 aircraft. After defeat, Regia Aeronautica withdrawn progressively westward. By December, concentrated in Tunisia. Heavy losses during retreat reduced operational strength. Supply difficulties throughout period.",
    future_enhancement: "Italian Ufficio Storico for withdrawal timeline and unit losses"
  }
};

// ========== 1943-Q1 (January-March, Tunisia) ==========

// British 1943-Q1
const british1943q1 = {
  schema_version: "3.1.0_air",
  nation: "british",
  quarter: "1943q1",
  theater: "North Africa",
  source_document: {
    title: "Northwest African Tactical Air Force - Tunisia Campaign",
    date: "1943-02-01",
    file: "online_research",
    collection: "Tunisia Campaign Records",
    tier: "tier_2"
  },
  air_command_structure: {
    theater_command: {
      designation: "Northwest African Tactical Air Force",
      commander: "Air Vice-Marshal Arthur Coningham",
      headquarters: "Tunisia"
    },
    subordinate_formations: [
      {
        designation: "Desert Air Force (WDAF/DAF)",
        commander: "Air Vice-Marshal Harry Broadhurst",
        note: "Became sub-command of NATAF in February 1943"
      }
    ]
  },
  aggregate_strength: {
    total_aircraft: 900,
    operational_aircraft: 800,
    serviceability_rate: "~89%",
    note: "Aggregate estimate for Tunisia campaign. Reorganized under Northwest African Air Forces at Casablanca Conference (January 1943). WDAF became sub-command of NATAF in February. Continued 29+ squadrons from El Alamein. 'Even greater' numerical superiority by March 1943 per records.",
    data_source: "Tunisia campaign records + NATAF reorganization",
    by_unit_composition: {
      squadrons_total: 29,
      note: "29 British, Australian, South African squadrons from El Alamein period, reorganized under NATAF"
    }
  },
  metadata: {
    sources: [
      "Wikipedia - Northwest African Tactical Air Force (created February 1943)",
      "Casablanca Conference (January 1943) - Allied air forces reorganization",
      "Tunisia records - 'Even greater numerical superiority by March 1943'",
      "WDAF: 29 squadrons from November 1942 continued into Tunisia"
    ],
    confidence: 75,
    tier: "partial_needs_research",
    extraction_date: "2025-10-29",
    extraction_method: "Campaign records + organizational documents",
    notes: "Tunisia campaign (Jan-May 1943) saw major Allied air reorganization. Churchill and Roosevelt created Northwest African Air Forces at Casablanca Conference. WDAF (29+ squadrons) became sub-command of NATAF under Coningham (Broadhurst commanded DAF). Numerical superiority over Axis increased through Q1. Estimate ~900 aircraft, ~800 operational based on continued squadron strength from El Alamein. Squadron-level detail in AIR 27 ORBs.",
    future_enhancement: "AIR 27 ORBs for exact Tunisia squadron identities and strengths"
  }
};

// Italian 1943-Q1 (final quarter)
const italian1943q1 = {
  schema_version: "3.1.0_air",
  nation: "italian",
  quarter: "1943q1",
  theater: "North Africa",
  source_document: {
    title: "Regia Aeronautica Tunisia - Final Phase",
    date: "1943-02-01",
    file: "online_research",
    collection: "Tunisia Campaign Records",
    tier: "tier_3"
  },
  air_command_structure: {
    theater_command: {
      designation: "Regia Aeronautica - Tunisia",
      commander: "Unknown",
      headquarters: "Tunisia"
    },
    subordinate_formations: []
  },
  aggregate_strength: {
    total_aircraft: 120,
    operational_aircraft: 60,
    serviceability_rate: "~50%",
    note: "Aggregate from Tunisia campaign records. Mid-February: ~1,570 Axis in Mediterranean, ~300 in Tunisia. Italian component estimated ~40% of Tunisia forces = 120 aircraft. Lost 22 aircraft Feb 14-Mar 28. Poor maintenance meant only 50% serviceability. Withdrawn from Egypt after heavy losses.",
    data_source: "Tunisia campaign Axis strength reports"
  },
  metadata: {
    sources: [
      "Tunisia records - Mid-Feb 1943: ~300 Axis aircraft in Tunisia from ~1,570 Mediterranean total",
      "Losses Feb 14-Mar 28: 136 German + 22 Italian aircraft",
      "Poor maintenance: only 50% serviceability typical"
    ],
    confidence: 60,
    tier: "partial_needs_research",
    extraction_date: "2025-10-29",
    extraction_method: "Campaign records estimate from Axis totals",
    notes: "Final phase of Regia Aeronautica in North Africa. Mid-February: ~1,570 Axis aircraft in Mediterranean, ~300 based in Tunisia. Italian component estimated ~40% of Tunisia forces (lower than earlier 55% due to losses) = ~120 aircraft. Lost 22 aircraft Feb 14-Mar 28. Poor maintenance and supply meant only ~50% serviceability (~60 operational). Progressively withdrawn from Libya to Tunisia after El Alamein defeat.",
    future_enhancement: "Italian Ufficio Storico for final North Africa unit dispositions"
  }
};

// Write files
const files = [
  { name: 'german_1941q3_air_summary.json', data: german1941q3 },
  { name: 'british_1941q3_air_summary.json', data: british1941q3 },
  { name: 'italian_1941q3_air_summary.json', data: italian1941q3 },
  { name: 'german_1942q3_air_summary.json', data: german1942q3 },
  { name: 'italian_1942q3_air_summary.json', data: italian1942q3 },
  { name: 'german_1942q4_air_summary.json', data: german1942q4 },
  { name: 'italian_1942q4_air_summary.json', data: italian1942q4 },
  { name: 'british_1943q1_air_summary.json', data: british1943q1 },
  { name: 'italian_1943q1_air_summary.json', data: italian1943q1 }
];

console.log('Generating final 9 quarterly air summaries to complete coverage...\n');

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
console.log('✓ Generated 9 new quarterly air summaries');
console.log('  - 1941-Q3: German, British, Italian (3)');
console.log('  - 1942-Q3: German, Italian (2)');
console.log('  - 1942-Q4: German, Italian (2)');
console.log('  - 1943-Q1: British, Italian (2)');
console.log('='.repeat(60));
console.log('\nTotal coverage now: 21 quarterly summaries across all major quarters');
console.log('Coverage: 1941-Q1 through 1943-Q1 (all major combatants)');
console.log('\nAll summaries generated from freely available online sources:');
console.log('- Wikipedia battle articles');
console.log('- Comando Supremo Italian records');
console.log('- Operation Crusader/El Alamein battle records');
console.log('- Tunisia campaign strength reports');
