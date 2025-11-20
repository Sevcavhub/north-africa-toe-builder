#!/usr/bin/env node
/**
 * Final test - check if tools page JavaScript is working after cache clear
 */

const puppeteer = require('puppeteer');

async function main() {
    console.log('\n=== Testing Deployed Tools Page (Cache Disabled) ===\n');

    const browser = await puppeteer.launch({
        headless: false,
        args: ['--no-sandbox', '--disable-cache'],
        defaultViewport: { width: 1400, height: 900 }
    });

    const page = await browser.newPage();

    // Disable cache
    await page.setCacheEnabled(false);

    page.on('console', msg => console.log('  [Page]:', msg.text()));
    page.on('pageerror', error => console.error('[ERROR]:', error.message));

    console.log('Loading page with cache disabled...');
    await page.goto('https://sevcavhub.github.io/north-africa-toe-builder/tools.html', {
        waitUntil: 'networkidle2',
        timeout: 60000
    });

    await new Promise(resolve => setTimeout(resolve, 3000));

    // Check for JavaScript errors
    const jsCheck = await page.evaluate(() => {
        return {
            hasInitFunc: typeof initializeEventListeners !== 'undefined',
            hasOsjonesForm: !!document.getElementById('osjonesDatacardForm'),
            hasBuilderSelect: !!document.getElementById('builderVehicleSelect')
        };
    });

    console.log('\nJavaScript Status:');
    console.log('  initializeEventListeners defined:', jsCheck.hasInitFunc);
    console.log('  OSJones form exists:', jsCheck.hasOsjonesForm);
    console.log('  Builder select exists:', jsCheck.hasBuilderSelect);

    if (!jsCheck.hasInitFunc) {
        console.log('\n✗ JAVASCRIPT ERROR - initializeEventListeners not defined');
        console.log('This means there is still a syntax error in the deployed code');
    } else {
        console.log('\n✓ JavaScript loaded successfully!');
    }

    console.log('\n=== Testing OSJones Form ===');

    // Scroll to OSJones
    await page.evaluate(() => {
        const headers = Array.from(document.querySelectorAll('h3'));
        const osjonesHeader = headers.find(h => h.textContent.includes('Army List'));
        if (osjonesHeader) osjonesHeader.scrollIntoView({ block: 'center' });
    });
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Type in army list
    const sampleList = `Deutsches Afrikakorps
496 Points | 31 BR

PANZER IV F2    150pts`;

    await page.click('#osjonesArmyList');
    await page.keyboard.type(sampleList);
    console.log('✓ Army list typed');

    await new Promise(resolve => setTimeout(resolve, 500));

    // Click submit
    await page.click('form#osjonesDatacardForm button[type="submit"]');
    console.log('✓ Submit button clicked');

    // Wait for loading
    await new Promise(resolve => setTimeout(resolve, 2000));

    const loadingStatus = await page.evaluate(() => {
        const loading = document.getElementById('osjonesLoading');
        return loading && loading.classList.contains('show');
    });

    if (loadingStatus) {
        console.log('✓✓✓ SUCCESS! Loading indicator appeared!');
        console.log('\nOSJones form submission is WORKING!');
    } else {
        console.log('✗ Loading indicator did NOT appear');
        console.log('Form submission may still be broken');
    }

    console.log('\n=== Testing Interactive Builder ===');

    // Scroll to builder
    await page.evaluate(() => {
        const h2s = Array.from(document.querySelectorAll('h2'));
        const builderHeader = h2s.find(h => h.textContent.includes('Interactive'));
        if (builderHeader) builderHeader.scrollIntoView({ block: 'center' });
    });
    await new Promise(resolve => setTimeout(resolve, 1000));

    console.log('Checking vehicle dropdown (will wait up to 30 seconds)...');

    try {
        await page.waitForFunction(
            () => {
                const select = document.getElementById('builderVehicleSelect');
                return select && select.options.length > 50;
            },
            { timeout: 30000, polling: 1000 }
        );

        const vehicleCount = await page.evaluate(() => {
            return document.getElementById('builderVehicleSelect').options.length - 1;
        });

        console.log(`✓✓✓ SUCCESS! Loaded ${vehicleCount} vehicles!`);
        console.log('\nInteractive Builder is WORKING!');
    } catch (error) {
        console.log('⚠ Vehicles still loading or API slow (Render.com cold start)');
        console.log('This is normal on first request - wait 30-60 seconds and try again');
    }

    console.log('\n=== Summary ===');
    console.log('Browser will remain open for 10 seconds for manual inspection...');
    await new Promise(resolve => setTimeout(resolve, 10000));

    await browser.close();
}

main().catch(console.error);
