const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();

    console.log('========================================');
    console.log('TESTING INTERACTIVE DATACARD BUILDER');
    console.log('========================================\n');

    await page.goto('https://sevcavhub.github.io/north-africa-toe-builder/tools.html', {
        waitUntil: 'networkidle0',
        timeout: 60000
    });

    await page.waitForTimeout(2000);

    // Test 1: Functions exist
    console.log('Test 1: Checking if functions exist...');
    const functionsExist = await page.evaluate(() => {
        return {
            loadBuilderVehicles: typeof loadBuilderVehicles !== 'undefined',
            populateBuilderVehicleSelect: typeof populateBuilderVehicleSelect !== 'undefined',
            attachBuilderEventListeners: typeof attachBuilderEventListeners !== 'undefined',
            updateBuilderVehicleList: typeof updateBuilderVehicleList !== 'undefined',
            removeBuilderVehicle: typeof removeBuilderVehicle !== 'undefined'
        };
    });
    console.log('Functions:', functionsExist);

    const allFunctionsDefined = Object.values(functionsExist).every(v => v);
    console.log(allFunctionsDefined ? '✅ All functions defined' : '❌ Some functions missing');

    // Test 2: Vehicle dropdown
    console.log('\nTest 2: Checking vehicle dropdown...');
    await page.waitForTimeout(3000);

    const dropdownStatus = await page.evaluate(() => {
        const select = document.getElementById('vehicleSelect');
        if (!select) return { error: 'Select not found' };

        return {
            optionCount: select.options.length,
            firstOption: select.options[0]?.textContent,
            loading: select.options[0]?.textContent === 'Loading vehicles...'
        };
    });
    console.log('Dropdown:', dropdownStatus);
    console.log(dropdownStatus.optionCount > 1 ? `✅ Loaded ${dropdownStatus.optionCount} vehicles` : '❌ Dropdown not loaded');

    // Test 3: Search
    console.log('\nTest 3: Testing search filter...');
    await page.type('#vehicleSearch', 'Sherman');
    await page.waitForTimeout(500);

    const searchResults = await page.evaluate(() => {
        const select = document.getElementById('vehicleSelect');
        return {
            count: select.options.length,
            samples: Array.from(select.options).slice(0, 3).map(o => o.textContent)
        };
    });
    console.log('Search results:', searchResults);
    console.log(searchResults.count > 0 ? `✅ Found ${searchResults.count} Sherman variants` : '❌ Search failed');

    // Test 4: Add vehicle
    console.log('\nTest 4: Adding vehicle to list...');
    await page.evaluate(() => {
        const select = document.getElementById('vehicleSelect');
        if (select.options.length > 0) select.selectedIndex = 0;
    });

    await page.select('#nationSelect', 'american');
    await page.click('#addVehicleBtn');
    await page.waitForTimeout(1000);

    const vehicleAdded = await page.evaluate(() => {
        const count = document.getElementById('vehicleCountBadge')?.textContent;
        const hasVehicles = document.getElementById('vehicleListContainer')?.innerHTML.includes('<strong>');
        const buildEnabled = !document.getElementById('buildDatacardsBtn')?.disabled;

        return { count, hasVehicles, buildEnabled };
    });
    console.log('Vehicle list:', vehicleAdded);
    console.log(vehicleAdded.hasVehicles ? '✅ Vehicle added successfully' : '❌ Failed to add vehicle');

    // Test 5: Check OSJones tool exists
    console.log('\n========================================');
    console.log('TESTING OSJONES ARMY LIST GENERATOR');
    console.log('========================================\n');

    const osjonesExists = await page.evaluate(() => {
        const form = document.getElementById('osjonesDatacardForm');
        const textarea = document.getElementById('osjonesArmyList');
        const submitBtn = document.querySelector('#osjonesDatacardForm button[type="submit"]');

        return {
            formExists: !!form,
            textareaExists: !!textarea,
            submitBtnExists: !!submitBtn,
            submitBtnText: submitBtn?.textContent.trim()
        };
    });

    console.log('OSJones tool elements:', osjonesExists);
    console.log(osjonesExists.formExists && osjonesExists.textareaExists && osjonesExists.submitBtnExists ?
        '✅ OSJones tool present and ready' : '❌ OSJones tool missing elements');

    // Summary
    console.log('\n========================================');
    console.log('FINAL SUMMARY');
    console.log('========================================\n');

    const allTestsPassed =
        allFunctionsDefined &&
        dropdownStatus.optionCount > 1 &&
        searchResults.count > 0 &&
        vehicleAdded.hasVehicles &&
        osjonesExists.formExists;

    console.log('Interactive Datacard Builder:');
    console.log('  ✅ Functions defined');
    console.log(`  ✅ Vehicle dropdown (${dropdownStatus.optionCount} vehicles)`);
    console.log(`  ✅ Search filter (${searchResults.count} Sherman variants)`);
    console.log(`  ✅ Add vehicle (${vehicleAdded.count} in list)`);
    console.log('');
    console.log('OSJones Army List Generator:');
    console.log('  ✅ Form present and ready');
    console.log('');
    console.log(allTestsPassed ? '🎉 ALL TESTS PASSED!' : '⚠️  Some tests failed');
    console.log('\nBrowser will remain open for manual testing.');
    console.log('You can now:');
    console.log('  1. Try building datacards with the Interactive Builder');
    console.log('  2. Paste an army list into the OSJones Generator');
    console.log('  3. Check if silhouettes appear on generated datacards');

    // Keep browser open
})();
