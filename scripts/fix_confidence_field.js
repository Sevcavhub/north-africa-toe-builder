#!/usr/bin/env node

const fs = require('fs');

const units = [
  'D:\\north-africa-toe-builder\\data\\output\\units\\british_1941q1_xiii_corps_toe.json',
  'D:\\north-africa-toe-builder\\data\\output\\units\\british_1941q3_8th_army_toe.json',
  'D:\\north-africa-toe-builder\\data\\output\\units\\british_1941q3_polish_carpathian_brigade_toe.json',
  'D:\\north-africa-toe-builder\\data\\output\\units\\british_1941q4_polish_carpathian_brigade_toe.json'
];

for (const unitPath of units) {
  const unit = JSON.parse(fs.readFileSync(unitPath, 'utf8'));

  if (unit.validation && unit.validation.confidence_level !== undefined && unit.validation.confidence === undefined) {
    unit.validation.confidence = unit.validation.confidence_level;
    delete unit.validation.confidence_level;
    fs.writeFileSync(unitPath, JSON.stringify(unit, null, 2));
    console.log(`✓ Fixed: ${unitPath.split('\\').pop()}`);
  } else {
    console.log(`✓ Already correct: ${unitPath.split('\\').pop()}`);
  }
}
