const fs = require('fs');
const seeds = JSON.parse(fs.readFileSync('projects/north_africa_seed_units_COMPLETE.json', 'utf-8'));

let count = 0;
Object.entries(seeds).forEach(([k,v]) => {
    if (Array.isArray(v)) {
        v.forEach(u => {
            if (!u.quarters || !Array.isArray(u.quarters)) {
                console.log(`${k}: ${u.designation || 'NO DESIGNATION'}`);
                console.log('  Unit object keys:', Object.keys(u));
                count++;
            }
        });
    }
});

console.log(`\nTotal units without quarters array: ${count}`);
