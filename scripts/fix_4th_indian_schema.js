#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', 'data', 'output', 'units', 'british_1940q3_4th_indian_division_toe.json');

// Read the file
const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));

// Add required top-level v3.1.0 schema fields
const fixed = {
    schema_type: 'division_toe',
    schema_version: '3.1.0',
    nation: data.unit_identification.nation,
    quarter: data.unit_identification.quarter,
    unit_designation: data.unit_identification.unit_designation,
    organization_level: 'division',
    theater: 'North Africa',
    location: data.unit_identification.hq_location,
    formation_date: '1940',

    commander: {
        name: data.command_structure.commanding_officer.name,
        rank: data.command_structure.commanding_officer.rank,
        appointment_date: data.command_structure.commanding_officer.appointment_date,
        sources: ['Nafziger Collection 940BLAB.pdf'],
        confidence: 90
    },

    // Preserve all existing nested data
    ...data
};

// Write back
fs.writeFileSync(filePath, JSON.stringify(fixed, null, 2), 'utf-8');

console.log('✅ Fixed british_1940q3_4th_indian_division_toe.json');
console.log('   Added: schema_type, schema_version, top-level commander');
