#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', 'RESTORATION_PLAN.md');
const content = fs.readFileSync(filePath, 'utf-8');

const updated = content.replace(
    /\*\*Phase 3\*\*: ⬜⬜ 0\/2 complete/,
    '**Phase 3**: ✅✅ 2/2 complete (100%)'
).replace(
    /\*\*Phase 4\*\*: ⬜⬜ 0\/2 complete/,
    '**Phase 4**: ✅✅ 2/2 complete (100%)'
).replace(
    /\*\*Phase 5\*\*: ⬜⬜ 0\/2 complete/,
    '**Phase 5**: ✅✅ 2/2 complete (100%)'
).replace(
    /\*\*Overall\*\*: 6\/12 tasks complete \(50%\)/,
    '**Overall**: 12/12 tasks complete (100%) ✅ RESTORATION COMPLETE'
);

fs.writeFileSync(filePath, updated, 'utf-8');
console.log('✅ Updated RESTORATION_PLAN.md progress to 100% complete');
