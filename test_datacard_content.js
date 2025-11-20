const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();

    // Enable console logging
    page.on('console', msg => console.log(`[BROWSER] ${msg.text()}`));

    console.log('Testing datacard generation and inspecting new tab content...\n');

    await page.goto('https://sevcavhub.github.io/north-africa-toe-builder/tools.html', {
        waitUntil: 'networkidle0'
    });

    await page.waitForTimeout(3000);

    // Add a vehicle
    await page.evaluate(() => {
        const select = document.getElementById('vehicleSelect');
        if (select.options.length > 0) select.selectedIndex = 0;
    });

    await page.select('#nationSelect', 'british');
    await page.click('#addVehicleBtn');
    await page.waitForTimeout(1000);

    console.log('Clicking Build Datacards...');

    // Listen for new pages
    browser.on('targetcreated', async (target) => {
        console.log('New tab created!');
    });

    await page.click('#buildDatacardsBtn');
    await page.waitForTimeout(5000);

    // Get all pages
    const pages = await browser.pages();
    console.log(`\nTotal pages: ${pages.length}`);

    // Check the last page (should be the datacard)
    if (pages.length > 1) {
        const datacardPage = pages[pages.length - 1];
        await datacardPage.waitForTimeout(1000);

        const content = await datacardPage.content();

        console.log('\n========================================');
        console.log('DATACARD PAGE CONTENT (first 1000 chars):');
        console.log('========================================');
        console.log(content.substring(0, 1000));

        // Check for specific error messages
        const hasError = content.includes('Error') || content.includes('Could not generate');
        const hasDatacard = content.includes('datacard');
        const hasSuccess = content.includes('Success');

        console.log('\n========================================');
        console.log('CONTENT ANALYSIS:');
        console.log('========================================');
        console.log('Has error message:', hasError);
        console.log('Has datacard class:', hasDatacard);
        console.log('Has success message:', hasSuccess);

        // Get title
        const title = await datacardPage.title();
        console.log('Page title:', title);

        // Check if it's showing an error datacard
        if (content.includes('Could not generate datacard')) {
            console.log('\n⚠️ ISSUE CONFIRMED: "Could not generate datacard" error found');

            // Extract the error message
            const errorMatch = content.match(/Error: Could not generate datacard for ([^<]+)/);
            if (errorMatch) {
                console.log(`Failed vehicle: ${errorMatch[1]}`);
            }
        }
    }

    console.log('\nBrowser will remain open for manual inspection');
})();
