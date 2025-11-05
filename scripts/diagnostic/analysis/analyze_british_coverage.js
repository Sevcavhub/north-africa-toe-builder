#!/usr/bin/env node

const fs = require('fs');
const master = JSON.parse(fs.readFileSync('data/canonical/MASTER_UNIT_DIRECTORY.json', 'utf8'));

const britishUnits = {};

for (const unit of master.canonical_units) {
    if (unit.nation !== 'british') continue;

    if (!britishUnits[unit.designation]) {
        britishUnits[unit.designation] = {
            quarters: 0,
            with_source: 0,
            without_source: 0
        };
    }

    britishUnits[unit.designation].quarters++;

    const hasNafziger = unit.authoritative_sources.nafziger_refs.length > 0;

    if (hasNafziger) {
        britishUnits[unit.designation].with_source++;
    } else {
        britishUnits[unit.designation].without_source++;
    }
}

console.log('BRITISH UNITS - SOURCE COVERAGE:');
console.log('');
for (const [designation, stats] of Object.entries(britishUnits)) {
    const status = stats.without_source === 0 ? '✅' : '❌';
    console.log(`  ${status} ${designation}: ${stats.with_source}/${stats.quarters} quarters`);
}

console.log('');
console.log('MISSING COVERAGE (units with 0 sources):');
const missing = Object.entries(britishUnits).filter(([_, stats]) => stats.with_source === 0);
for (const [designation, stats] of missing) {
    console.log(`  - ${designation} (${stats.quarters} quarters)`);
}
