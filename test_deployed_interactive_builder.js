const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();

    // Enable console logging from the page
    page.on('console', msg => {
        const type = msg.type();
        const text = msg.text();
        if (type === 'error' || text.includes('Error') || text.includes('error')) {
            console.log(`[BROWSER ERROR] ${text}`);
        } else {
            console.log(`[BROWSER] ${text}`);
        }
    });

    // Capture network errors
    page.on('requestfailed', request => {
        console.log(`[NETWORK FAIL] ${request.url()} - ${request.failure().errorText}`);
    });

    console.log('========================================');
    console.log('TESTING DEPLOYED INTERACTIVE BUILDER');
    console.log('========================================\n');

    await page.goto('https://sevcavhub.github.io/north-africa-toe-builder/tools.html', {
        waitUntil: 'networkidle0',
        timeout: 60000
    });

    await page.waitForTimeout(3000);

    // Check dropdown
    console.log('Test 1: Checking vehicle dropdown...');
    const dropdownInfo = await page.evaluate(() => {
        const select = document.getElementById('vehicleSelect');
        if (!select) return { error: 'Select not found' };

        const options = Array.from(select.options).map(o => o.textContent);
        return {
            count: select.options.length,
            first10: options.slice(0, 10),
            hasLoading: options[0] === 'Loading vehicles...'
        };
    });
    console.log('Dropdown info:', dropdownInfo);

    if (dropdownInfo.hasLoading) {
        console.log('ISSUE: Still showing "Loading vehicles..."');

        // Check API URL
        const apiUrl = await page.evaluate(() => API_URL);
        console.log(`API_URL: ${apiUrl}`);

        // Try calling API directly from browser
        console.log('\nTrying to call /api/vehicles directly...');
        const apiResult = await page.evaluate(async (url) => {
            try {
                const response = await fetch(`${url}/api/vehicles`);
                const data = await response.json();
                return {
                    ok: response.ok,
                    status: response.status,
                    dataType: typeof data,
                    isArray: Array.isArray(data),
                    count: Array.isArray(data) ? data.length : 0,
                    sample: Array.isArray(data) ? data.slice(0, 5) : null
                };
            } catch (error) {
                return { error: error.message };
            }
        }, apiUrl);
        console.log('API call result:', apiResult);
    }

    // Try to add a vehicle and generate datacard
    if (dropdownInfo.count > 1) {
        console.log('\nTest 2: Trying to generate datacard...');

        // Select first vehicle
        await page.evaluate(() => {
            const select = document.getElementById('vehicleSelect');
            if (select.options.length > 0) {
                select.selectedIndex = 0;
            }
        });

        const selectedVehicle = await page.evaluate(() => {
            return document.getElementById('vehicleSelect').value;
        });
        console.log(`Selected vehicle: ${selectedVehicle}`);

        // Select nation
        await page.select('#nationSelect', 'british');

        // Add vehicle
        await page.click('#addVehicleBtn');
        await page.waitForTimeout(1000);

        const vehicleCount = await page.evaluate(() => {
            return document.getElementById('vehicleCountBadge')?.textContent;
        });
        console.log(`Vehicles in list: ${vehicleCount}`);

        if (vehicleCount === '1') {
            console.log('Clicking Build Datacards button...');
            await page.click('#buildDatacardsBtn');
            await page.waitForTimeout(5000); // Wait for API call

            // Check for error messages
            const errorCheck = await page.evaluate(() => {
                const resultsDiv = document.getElementById('interactiveResults');
                const outputDiv = document.getElementById('interactiveOutput');

                return {
                    resultsVisible: resultsDiv?.style.display !== 'none',
                    outputHTML: outputDiv?.innerHTML,
                    hasError: outputDiv?.innerHTML.includes('Error') || outputDiv?.innerHTML.includes('error')
                };
            });

            console.log('\nDatacard generation result:');
            console.log('Results visible:', errorCheck.resultsVisible);
            console.log('Has error:', errorCheck.hasError);
            if (errorCheck.outputHTML) {
                console.log('Output (first 300 chars):', errorCheck.outputHTML.substring(0, 300));
            }

            // Check if new tab opened
            const pages = await browser.pages();
            console.log(`Number of pages: ${pages.length} (should be 2 if datacard opened)`);
        }
    }

    console.log('\n========================================');
    console.log('Browser will remain open for inspection');
    console.log('========================================');

    // Keep browser open
})();
