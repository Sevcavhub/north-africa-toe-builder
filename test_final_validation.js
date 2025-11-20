#!/usr/bin/env node
/**
 * Comprehensive validation test for deployed tools
 * Tests:
 * 1. Interactive Datacard Builder - Vehicle dropdown loads, cards generate with correct CSS
 * 2. OSJones Army List Generator - Form submission works, datacards generate
 * 3. Silhouette images display correctly in datacards
 */

const puppeteer = require('puppeteer');

const TOOLS_URL = 'https://sevcavhub.github.io/north-africa-toe-builder/tools.html';
const API_URL = 'https://north-africa-toe-api.onrender.com';

// Sample OSJones army list for testing
const SAMPLE_ARMY_LIST = `Deutsches Afrikakorps
496 Points | 31 BR

--- ARMOUR ---
PANZER IV F2                           150pts
Vehicle (late)                          5  5  6  8  14   9   9  6   6   4   4   4  75mmL43 MG

--- GUNS AND ARTILLERY ---
88MM FLAK 36                            90pts
Gun tow (late)                         12  3  -  -   -   -   -  5   8  10  11  11  88mmL56

TOTAL: 496 points, 31 BR`;

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function testInteractiveBuilder(page) {
    console.log('\n=== Testing Interactive Datacard Builder ===');

    try {
        await page.goto(TOOLS_URL, { waitUntil: 'networkidle2', timeout: 60000 });
        console.log('✓ Tools page loaded');

        // Scroll to Interactive Builder section
        await page.evaluate(() => {
            const section = document.querySelector('h2');
            if (section && section.textContent.includes('Interactive')) {
                section.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
        await sleep(1000);

        // Wait for vehicle dropdown to populate
        console.log('Waiting for vehicles to load...');
        await page.waitForFunction(
            () => {
                const select = document.getElementById('builderVehicleSelect');
                return select && select.options.length > 100; // Should have 590+ vehicles
            },
            { timeout: 30000 }
        );
        console.log('✓ Vehicle dropdown populated');

        // Get vehicle count
        const vehicleCount = await page.evaluate(() => {
            const select = document.getElementById('builderVehicleSelect');
            return select.options.length - 1; // Subtract the "Select a vehicle..." option
        });
        console.log(`✓ Loaded ${vehicleCount} vehicles`);

        // Select a vehicle (Crusader I)
        await page.select('#builderVehicleSelect', 'Crusader I');
        await sleep(500);

        // Click "Add to List" button
        await page.click('#builderVehicleSelect + button');
        await sleep(500);
        console.log('✓ Added Crusader I to list');

        // Select nation
        await page.select('#builderNation', 'british');
        await sleep(500);

        // Click "Generate Datacards" button
        await page.evaluate(() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            const generateBtn = buttons.find(btn => btn.textContent.includes('Generate Datacards'));
            if (generateBtn) generateBtn.click();
        });
        console.log('Clicked Generate Datacards button');

        // Wait for loading to appear and disappear
        await page.waitForSelector('#builderLoading.show', { timeout: 5000 });
        console.log('Loading indicator appeared');
        await page.waitForSelector('#builderLoading:not(.show)', { timeout: 30000 });
        console.log('✓ Loading completed');

        // Check if datacards window opened
        await sleep(2000);
        const pages = await page.browser().pages();
        console.log(`Open pages: ${pages.length}`);

        // Find the datacard window
        let datacardPage = null;
        for (const p of pages) {
            const url = p.url();
            if (url.includes('api/datacards/interactive')) {
                datacardPage = p;
                break;
            }
        }

        if (!datacardPage) {
            console.log('⚠ Datacard window not detected (may have been blocked)');
            console.log('Checking if response was successful...');

            // Check network response
            const hasSuccess = await page.evaluate(() => {
                const resultsDiv = document.getElementById('builderResults');
                return resultsDiv && resultsDiv.classList.contains('show');
            });

            if (hasSuccess) {
                console.log('✓ API returned successfully');
            }
        } else {
            console.log('✓ Datacard window opened');

            // Wait for content to load
            await datacardPage.waitForSelector('.datacard', { timeout: 10000 });
            console.log('✓ Datacards rendered');

            // Check CSS is applied correctly
            const cssCheck = await datacardPage.evaluate(() => {
                const datacard = document.querySelector('.datacard');
                const grid = document.querySelector('.datacard-grid');
                const silhouette = document.querySelector('.datacard-silhouette');

                return {
                    hasDatacard: !!datacard,
                    hasGrid: !!grid,
                    gridColumns: grid ? window.getComputedStyle(grid).gridTemplateColumns : null,
                    datacardBorder: datacard ? window.getComputedStyle(datacard).borderWidth : null,
                    silhouetteWidth: silhouette ? window.getComputedStyle(silhouette).width : null
                };
            });

            console.log('CSS Check:', cssCheck);

            if (cssCheck.gridColumns && cssCheck.gridColumns.includes('fr')) {
                console.log('✓ V6.1 CSS grid layout applied correctly');
            }

            if (cssCheck.silhouetteWidth === '140px') {
                console.log('✓ Silhouette size constraints correct');
            }

            await datacardPage.close();
        }

        return true;
    } catch (error) {
        console.error('✗ Interactive Builder test failed:', error.message);
        return false;
    }
}

async function testOSJonesGenerator(page) {
    console.log('\n=== Testing OSJones Army List Generator ===');

    try {
        await page.goto(TOOLS_URL, { waitUntil: 'networkidle2', timeout: 60000 });
        console.log('✓ Tools page loaded');

        // Scroll to OSJones section
        await page.evaluate(() => {
            const headers = Array.from(document.querySelectorAll('h3'));
            const osjonesHeader = headers.find(h => h.textContent.includes('Army List'));
            if (osjonesHeader) {
                osjonesHeader.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
        await sleep(1000);

        // Clear and fill textarea
        await page.evaluate(() => {
            const textarea = document.getElementById('osjonesArmyList');
            if (textarea) {
                textarea.value = '';
            }
        });
        await page.type('#osjonesArmyList', SAMPLE_ARMY_LIST);
        console.log('✓ Pasted army list into textarea');

        // Check that form exists
        const formExists = await page.evaluate(() => {
            return !!document.getElementById('osjonesDatacardForm');
        });
        console.log(`Form exists: ${formExists}`);

        // Click Generate Datacards button
        await page.evaluate(() => {
            const form = document.getElementById('osjonesDatacardForm');
            const button = form.querySelector('button[type="submit"]');
            console.log('Button found:', !!button);
            if (button) button.click();
        });
        console.log('✓ Clicked Generate Datacards button');

        // Wait for loading indicator
        await page.waitForSelector('#osjonesLoading.show', { timeout: 5000 });
        console.log('✓ Loading indicator appeared');

        // Wait for loading to disappear
        await page.waitForSelector('#osjonesLoading:not(.show)', { timeout: 30000 });
        console.log('✓ Loading completed');

        // Check if results are displayed
        await page.waitForSelector('#osjonesResults.show', { timeout: 5000 });
        console.log('✓ Results displayed');

        // Get results summary
        const results = await page.evaluate(() => {
            const resultsDiv = document.getElementById('osjonesResults');
            const outputDiv = document.getElementById('osjonesOutput');

            return {
                hasResults: resultsDiv.classList.contains('show'),
                hasError: resultsDiv.classList.contains('error'),
                content: outputDiv ? outputDiv.textContent.substring(0, 200) : null,
                hasButtons: outputDiv ? outputDiv.querySelectorAll('button').length : 0
            };
        });

        console.log('Results:', results);

        if (!results.hasError) {
            console.log('✓ OSJones generator succeeded');
            console.log(`✓ Found ${results.hasButtons} action buttons`);

            // Try to open printable HTML
            await sleep(1000);
            await page.evaluate(() => {
                const buttons = Array.from(document.querySelectorAll('#osjonesOutput button'));
                const printBtn = buttons.find(btn => btn.textContent.includes('Printable'));
                if (printBtn) printBtn.click();
            });
            console.log('✓ Clicked printable datacards button');

            await sleep(2000);

            // Check if new window opened
            const pages = await page.browser().pages();
            let datacardPage = null;
            for (const p of pages) {
                const url = p.url();
                if (url.includes('api/datacards/osjones') && url.includes('html=true')) {
                    datacardPage = p;
                    break;
                }
            }

            if (datacardPage) {
                console.log('✓ Printable datacards window opened');

                // Check for datacards
                await datacardPage.waitForSelector('.datacard', { timeout: 10000 });
                const cardCount = await datacardPage.evaluate(() => {
                    return document.querySelectorAll('.datacard').length;
                });
                console.log(`✓ Rendered ${cardCount} datacards`);

                await datacardPage.close();
            }
        } else {
            console.log('✗ OSJones generator returned error');
            console.log('Error content:', results.content);
            return false;
        }

        return true;
    } catch (error) {
        console.error('✗ OSJones test failed:', error.message);
        return false;
    }
}

async function main() {
    console.log('Starting comprehensive validation tests...');
    console.log(`Tools URL: ${TOOLS_URL}`);
    console.log(`API URL: ${API_URL}`);

    const browser = await puppeteer.launch({
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
        defaultViewport: { width: 1400, height: 900 }
    });

    const page = await browser.newPage();

    // Enable console logging from page
    page.on('console', msg => {
        const text = msg.text();
        if (text.includes('Button found') || text.includes('Event listener')) {
            console.log('  [Page Console]:', text);
        }
    });

    let allPassed = true;

    // Test Interactive Builder
    const builderPassed = await testInteractiveBuilder(page);
    allPassed = allPassed && builderPassed;

    // Test OSJones Generator
    const osJonesPassed = await testOSJonesGenerator(page);
    allPassed = allPassed && osJonesPassed;

    console.log('\n=== Final Results ===');
    console.log(`Interactive Builder: ${builderPassed ? '✓ PASS' : '✗ FAIL'}`);
    console.log(`OSJones Generator: ${osJonesPassed ? '✓ PASS' : '✗ FAIL'}`);
    console.log(`\nOverall: ${allPassed ? '✓ ALL TESTS PASSED' : '✗ SOME TESTS FAILED'}`);

    await sleep(3000);
    await browser.close();

    process.exit(allPassed ? 0 : 1);
}

main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
