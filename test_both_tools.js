const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();

    console.log('========================================');
    console.log('TESTING INTERACTIVE DATACARD BUILDER');
    console.log('========================================\n');

    // Navigate to tools page
    await page.goto('https://sevcavhub.github.io/north-africa-toe-builder/tools.html', {
        waitUntil: 'networkidle0',
        timeout: 60000
    });

    // Wait for page to fully load
    await page.waitForTimeout(2000);

    // Test 1: Check if functions exist
    console.log('Test 1: Checking if Interactive Builder functions exist...');
    const functionsExist = await page.evaluate(() => {
        return {
            loadBuilderVehicles: typeof loadBuilderVehicles !== 'undefined',
            populateBuilderVehicleSelect: typeof populateBuilderVehicleSelect !== 'undefined',
            attachBuilderEventListeners: typeof attachBuilderEventListeners !== 'undefined',
            updateBuilderVehicleList: typeof updateBuilderVehicleList !== 'undefined',
            removeBuilderVehicle: typeof removeBuilderVehicle !== 'undefined'
        };
    });
    console.log('Functions defined:', functionsExist);

    // Test 2: Check vehicle dropdown
    console.log('\nTest 2: Checking vehicle dropdown...');
    await page.waitForTimeout(3000); // Give API time to load vehicles

    const dropdownStatus = await page.evaluate(() => {
        const select = document.getElementById('vehicleSelect');
        if (!select) return { error: 'Select element not found' };

        return {
            exists: true,
            optionCount: select.options.length,
            firstOption: select.options[0]?.textContent,
            loadingText: select.options[0]?.textContent === 'Loading vehicles...',
            selectedValue: select.value
        };
    });
    console.log('Dropdown status:', dropdownStatus);

    if (dropdownStatus.optionCount > 1) {
        console.log('✅ SUCCESS: Vehicle dropdown populated with', dropdownStatus.optionCount, 'vehicles');
    } else if (dropdownStatus.loadingText) {
        console.log('❌ FAIL: Still showing "Loading vehicles..."');
    } else {
        console.log('⚠️  WARNING: Unexpected dropdown state');
    }

    // Test 3: Search functionality
    console.log('\nTest 3: Testing search filter...');
    await page.type('#vehicleSearch', 'Sherman');
    await page.waitForTimeout(500);

    const searchResults = await page.evaluate(() => {
        const select = document.getElementById('vehicleSelect');
        const options = Array.from(select.options).map(opt => opt.textContent);
        return {
            count: options.length,
            vehicles: options.slice(0, 5) // First 5 results
        };
    });
    console.log('Search results for "Sherman":', searchResults);

    // Test 4: Add vehicle to list
    console.log('\nTest 4: Testing add vehicle functionality...');
    await page.evaluate(() => {
        const select = document.getElementById('vehicleSelect');
        if (select.options.length > 0) {
            select.selectedIndex = 0; // Select first Sherman
        }
    });

    await page.select('#nationSelect', 'american');
    await page.click('#addVehicleBtn');
    await page.waitForTimeout(1000);

    const vehicleListStatus = await page.evaluate(() => {
        const listContainer = document.getElementById('vehicleListContainer');
        const countBadge = document.getElementById('vehicleCountBadge');
        const buildBtn = document.getElementById('buildDatacardsBtn');

        return {
            count: countBadge?.textContent,
            hasVehicles: listContainer?.innerHTML.includes('<strong>'),
            buildBtnEnabled: !buildBtn?.disabled,
            listHTML: listContainer?.innerHTML.substring(0, 200)
        };
    });
    console.log('Vehicle list status:', vehicleListStatus);

    if (vehicleListStatus.hasVehicles) {
        console.log('✅ SUCCESS: Vehicle added to list');
    } else {
        console.log('❌ FAIL: Vehicle not added to list');
    }

    // Test 5: Clear search and add another vehicle
    console.log('\nTest 5: Adding second vehicle (Panzer IV)...');
    await page.evaluate(() => {
        document.getElementById('vehicleSearch').value = '';
        // Trigger input event
        const event = new Event('input', { bubbles: true });
        document.getElementById('vehicleSearch').dispatchEvent(event);
    });
    await page.waitForTimeout(500);

    await page.type('#vehicleSearch', 'Panzer IV');
    await page.waitForTimeout(500);

    await page.evaluate(() => {
        const select = document.getElementById('vehicleSelect');
        if (select.options.length > 0) {
            select.selectedIndex = 0;
        }
    });

    await page.select('#nationSelect', 'german');
    await page.click('#addVehicleBtn');
    await page.waitForTimeout(1000);

    const finalCount = await page.evaluate(() => {
        return document.getElementById('vehicleCountBadge')?.textContent;
    });
    console.log('Final vehicle count:', finalCount);

    console.log('\n========================================');
    console.log('TESTING OSJONES ARMY LIST GENERATOR');
    console.log('========================================\n');

    // Test OSJones generator
    console.log('Test 6: Testing OSJones Army List Generator...');

    const testArmyList = `Deutsches Afrikakorps 496 pts / 31 BR
==============================
Panzer Regiment (1 of 3)
==============================
0-1 Regimental HQ Unit (Regular)                              29 pts / 1 BR

| Type | Unit                     | BA | HE    | #MG | AP Pen | Armour | Spd | Special Rules           |
|------|--------------------------|----|-------|-----|--------|--------|-----|-------------------------|
| AFV  | PanzerBefehlswagen III H | +3 | D6    | 2   | 4/3/2  | 8/5/3  | 8"  | HE from Turret, recce   |

==============================
Panzer Company (1 of 3)
==============================
Panzer Platoon (Regular)                                     135 pts / 3 BR
3x Panzer IV G

| Type | Unit        | BA | HE  | #MG | AP Pen | Armour | Spd | Special Rules  |
|------|-------------|----|-----|-----|--------|--------|-----|----------------|
| AFV  | Panzer IV G | +3 | 4D6 | 2   | 9/8/6  | 8/5/4  | 7"  | HE from Turret |`;

    await page.evaluate((armyList) => {
        const textarea = document.getElementById('osjones-army-list-input');
        if (textarea) {
            textarea.value = armyList;
        }
    }, testArmyList);

    await page.waitForTimeout(500);

    // Click generate button
    const generateBtn = await page.$('#generate-osjones-datacards-btn');
    if (generateBtn) {
        console.log('Clicking Generate Datacards button...');
        await generateBtn.click();
        await page.waitForTimeout(3000); // Wait for API call

        const osjonesResults = await page.evaluate(() => {
            const resultsDiv = document.getElementById('osjones-results');
            const outputDiv = document.getElementById('osjones-output');

            return {
                resultsVisible: resultsDiv?.style.display !== 'none',
                hasOutput: outputDiv?.innerHTML.length > 0,
                outputPreview: outputDiv?.innerHTML.substring(0, 300)
            };
        });

        console.log('OSJones results:', osjonesResults);

        if (osjonesResults.resultsVisible && osjonesResults.hasOutput) {
            console.log('✅ SUCCESS: OSJones generator working');
        } else {
            console.log('❌ FAIL: OSJones generator not responding');
        }
    } else {
        console.log('❌ FAIL: Generate button not found');
    }

    console.log('\n========================================');
    console.log('TEST SUMMARY');
    console.log('========================================\n');

    console.log('Interactive Datacard Builder:');
    console.log('  - Functions defined: ', Object.values(functionsExist).every(v => v) ? '✅' : '❌');
    console.log('  - Vehicle dropdown loaded:', dropdownStatus.optionCount > 1 ? '✅' : '❌');
    console.log('  - Search filter works:', searchResults.count > 0 ? '✅' : '❌');
    console.log('  - Add vehicle works:', vehicleListStatus.hasVehicles ? '✅' : '❌');

    console.log('\nOSJones Army List Generator:');
    console.log('  - Generator working:', osjonesResults?.resultsVisible ? '✅' : '❌');

    console.log('\nTest complete. Browser will remain open for manual inspection.');
    console.log('Close browser window when done.');

    // Keep browser open for inspection
    // await browser.close();
})();
