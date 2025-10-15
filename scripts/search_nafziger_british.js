#!/usr/bin/env node

const fs = require('fs');

const index1939_1942 = JSON.parse(fs.readFileSync('Resource Documents/Nafziger Collection/WWII/North_Africa_Index/NORTH_AFRICA_FILES.json', 'utf8'));

console.log('='.repeat(80));
console.log('NAFZIGER 1939-1942 - BRITISH/COMMONWEALTH ENTRIES');
console.log('='.repeat(80));
console.log();

const britishEntries = [];

for (const period of index1939_1942) {
    for (const entry of period.entries) {
        const title = entry.title.toLowerCase();

        // Look for British/Commonwealth references
        if (title.includes('indian') ||
            title.includes('australian') ||
            title.includes('new zealand') ||
            title.includes('south african') ||
            title.includes('armoured division') ||
            title.includes('infantry division') ||
            title.includes('highland')) {

            britishEntries.push({
                code: entry.fileCode,
                title: entry.title.trim().replace(/\s+/g, ' ')
            });
        }
    }
}

console.log(`Found ${britishEntries.length} British/Commonwealth entries:`);
console.log();

britishEntries.forEach(e => {
    console.log(`${e.code}: ${e.title}`);
});
