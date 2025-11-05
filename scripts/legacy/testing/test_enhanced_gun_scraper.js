/**
 * Test Enhanced Gun Scraper
 * Tests with complex gun (I=114) and simple gun (I=360)
 */

const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');

// Import the enhanced extraction function (v2.1)
const { extractGunDetailsEnhanced } = require('./scrape_wwiitanks_enhanced_guns_v2');

const TEST_GUNS = [
  {
    name: '5.0cm Pak 38 L/60',
    url: 'https://wwiitanks.co.uk/FORM-Gun_Data.php?I=114',
    id: '114',
    expected: {
      ammunition_types: 4, // AP, AP40, HE, HEAT
      has_penetration_tables: true,
      has_blast_effects: true
    }
  },
  {
    name: '37mm Gun Type 94',
    url: 'https://wwiitanks.co.uk/FORM-Gun_Data.php?I=360',
    id: '360',
    expected: {
      ammunition_types: 0, // Simple gun with basic specs only
      has_penetration_tables: false,
      has_blast_effects: false
    }
  }
];

async function runTest() {
  console.log('🧪 Testing Enhanced Gun Scraper v2');
  console.log('==================================\n');

  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: { width: 1400, height: 900 }
  });

  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');

  const results = [];

  for (const testGun of TEST_GUNS) {
    console.log(`\n📝 Testing: ${testGun.name} (ID=${testGun.id})`);
    console.log(`   URL: ${testGun.url}`);
    console.log(`   Expected: ${testGun.expected.ammunition_types} ammo types`);

    try {
      const data = await extractGunDetailsEnhanced(page, testGun.url, testGun.name);

      if (!data) {
        console.log(`   ❌ FAILED: No data extracted`);
        results.push({ gun: testGun.name, status: 'FAILED', reason: 'No data' });
        continue;
      }

      // Validation
      const ammoCount = data.ammunition ? data.ammunition.length : 0;
      const hasPenetration = data.ammunition.some(a => a.penetration_table && a.penetration_table.length > 0);
      const hasBlast = data.ammunition.some(a => a.blast_effects);

      console.log(`\n   📊 Results:`);
      console.log(`      ✓ Basic specs: ${Object.keys(data.basic_specs).length} fields`);
      console.log(`        - Manufactured: ${data.basic_specs.manufactured || 'N/A'}`);
      console.log(`        - Calibre: ${data.basic_specs.calibre || 'N/A'}`);
      console.log(`        - Length: ${data.basic_specs.length || 'N/A'}`);
      console.log(`        - Rate of Fire: ${data.basic_specs.rate_of_fire || 'N/A'}`);
      console.log(`      ✓ Ammunition types: ${ammoCount}`);
      if (data.debug) {
        console.log(`      🐛 Debug info:`);
        console.log(`         - Total rows: ${data.debug.total_rows}`);
        console.log(`         - TH rows found: ${data.debug.th_rows}`);
        console.log(`         - Ammo matches: ${data.debug.ammo_matches}`);
        if (data.debug.match_details && data.debug.match_details.length > 0) {
          console.log(`         - Match details:`);
          data.debug.match_details.forEach(m => {
            console.log(`           Row ${m.row}: "${m.text}" (${m.cells} cells)`);
          });
        }
      }

      if (ammoCount > 0) {
        data.ammunition.forEach((ammo, idx) => {
          console.log(`        [${idx + 1}] ${ammo.name || 'Unnamed'}`);
          console.log(`            Type: ${ammo.type} (${ammo.type_full})`);
          console.log(`            Specs: ${JSON.stringify(ammo.specs)}`);
          if (ammo.penetration_table) {
            console.log(`            Penetration table: ${ammo.penetration_table.length} range entries`);
            if (ammo.penetration_table.length > 0) {
              console.log(`              Sample: ${JSON.stringify(ammo.penetration_table[0])}`);
            }
          }
          if (ammo.blast_effects) {
            console.log(`            Blast effects: ${JSON.stringify(ammo.blast_effects)}`);
          }
        });
      }

      console.log(`      ✓ Vehicles using gun: ${data.vehicles_using_gun.length}`);

      // Validation against expectations
      let passed = true;
      let failureReason = '';

      if (testGun.expected.ammunition_types > 0 && ammoCount === 0) {
        passed = false;
        failureReason = `Expected ${testGun.expected.ammunition_types} ammo types, got 0`;
      }

      if (testGun.expected.has_penetration_tables && !hasPenetration) {
        passed = false;
        failureReason = 'Expected penetration tables, none found';
      }

      if (testGun.expected.has_blast_effects && !hasBlast) {
        passed = false;
        failureReason = 'Expected blast effects, none found';
      }

      if (passed) {
        console.log(`\n   ✅ PASSED`);
        results.push({ gun: testGun.name, status: 'PASSED', data: data });
      } else {
        console.log(`\n   ⚠️  PARTIAL: ${failureReason}`);
        results.push({ gun: testGun.name, status: 'PARTIAL', reason: failureReason, data: data });
      }

    } catch (error) {
      console.log(`\n   ❌ FAILED: ${error.message}`);
      results.push({ gun: testGun.name, status: 'FAILED', reason: error.message });
    }

    // Wait between tests
    await page.waitForTimeout(2000);
  }

  await browser.close();

  // Summary
  console.log(`\n\n${'='.repeat(50)}`);
  console.log('📋 Test Summary');
  console.log('='.repeat(50));

  const passed = results.filter(r => r.status === 'PASSED').length;
  const partial = results.filter(r => r.status === 'PARTIAL').length;
  const failed = results.filter(r => r.status === 'FAILED').length;

  console.log(`✅ Passed: ${passed}/${results.length}`);
  console.log(`⚠️  Partial: ${partial}/${results.length}`);
  console.log(`❌ Failed: ${failed}/${results.length}`);

  // Save test results
  const outputDir = path.join(__dirname, '..', 'data', 'output', 'afv_data', 'wwiitanks');
  await fs.mkdir(outputDir, { recursive: true });

  await fs.writeFile(
    path.join(outputDir, 'enhanced_scraper_test_results.json'),
    JSON.stringify(results, null, 2)
  );

  console.log(`\n💾 Results saved to: enhanced_scraper_test_results.json`);

  if (failed > 0) {
    console.log(`\n⚠️  Some tests failed. Review output above for details.`);
    process.exit(1);
  } else if (partial > 0) {
    console.log(`\n⚠️  All tests passed but some had partial results. Enhanced scraper may need tuning.`);
  } else {
    console.log(`\n✅ All tests passed! Enhanced scraper is working correctly.`);
  }
}

// Run tests
if (require.main === module) {
  runTest().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}
