#!/usr/bin/env node

const fs = require('fs');
const master = JSON.parse(fs.readFileSync('data/canonical/MASTER_UNIT_DIRECTORY.json', 'utf8'));

console.log('UNITS WITHOUT ANY SOURCE COVERAGE:');
console.log('');

const missing = [];

for (const unit of master.canonical_units) {
    const hasNafziger = unit.authoritative_sources.nafziger_refs.length > 0;
    const hasItalian = unit.authoritative_sources.italian_source_refs && unit.authoritative_sources.italian_source_refs.length > 0;
    const hasBritish = unit.authoritative_sources.british_source_refs && unit.authoritative_sources.british_source_refs.length > 0;

    if (!hasNafziger && !hasItalian && !hasBritish) {
        missing.push(unit);
        console.log(`  ${unit.nation} | ${unit.quarter} | ${unit.designation}`);
    }
}

console.log('');
console.log(`Total missing: ${missing.length} unit-quarters`);
