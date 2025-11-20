#!/usr/bin/env node
/**
 * Final test - OSJones with longer waits for initialization
 */

const puppeteer = require('puppeteer');

const TOOLS_URL = 'https://sevcavhub.github.io/north-africa-toe-builder/tools.html';

const SAMPLE_ARMY_LIST = `Deutsches Afrikakorps
496 Points | 31 BR

PANZER IV F2                           150pts
88MM FLAK 36                            90pts`;

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
    console.log('Testing OSJones Army List Generator (Final Test)');
    console.log('URL:', TOOLS_URL);

    const browser = await puppeteer.launch({
        headless: false,
        args: ['--no-sandbox'],
        defaultViewport: { width: 1400, height: 900 }
    });

    const page = await browser.newPage();

    // Log all console output
    page.on('console', msg => {
        console.log('  [Page]:', msg.text());
    });

    console.log('Loading page...');
    await page.goto(TOOLS_URL, { waitUntil: 'networkidle2', timeout: 60000 });
    console.log('✓ Page loaded');

    // Wait extra time for JavaScript to initialize
    console.log('Waiting 5 seconds for JavaScript initialization...');
    await sleep(5000);

    // Scroll to OSJones section
    await page.evaluate(() => {
        const headers = Array.from(document.querySelectorAll('h3'));
        const osjonesHeader = headers.find(h => h.textContent.includes('Army List'));
        if (osjonesHeader) {
            osjonesHeader.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    });
    await sleep(2000);

    // Check if form and event listener exist
    const formCheck = await page.evaluate(() => {
        const form = document.getElementById('osjonesDatacardForm');
        const textarea = document.getElementById('osjonesArmyList');
        const button = form ? form.querySelector('button[type="submit"]') : null;

        return {
            hasForm: !!form,
            hasTextarea: !!textarea,
            hasButton: !!button,
            buttonText: button ? button.textContent : null
        };
    });

    console.log('Form elements:', formCheck);

    // Type into textarea
    await page.click('#osjonesArmyList');
    await page.keyboard.type(SAMPLE_ARMY_LIST, { delay: 10 });
    console.log('✓ Army list typed');

    await sleep(1000);

    // Get textarea value to confirm it was typed
    const textareaValue = await page.evaluate(() => {
        return document.getElementById('osjonesArmyList').value;
    });
    console.log('Textarea value length:', textareaValue.length);

    // Click the submit button
    console.log('Clicking submit button...');
    await page.evaluate(() => {
        const form = document.getElementById('osjonesDatacardForm');
        const button = form.querySelector('button[type="submit"]');
        button.click();
    });

    console.log('✓ Submit button clicked');

    // Wait and check for loading indicator
    await sleep(2000);

    const loadingCheck = await page.evaluate(() => {
        const loading = document.getElementById('osjonesLoading');
        const loadingClasses = loading ? Array.from(loading.classList) : [];
        const loadingDisplay = loading ? window.getComputedStyle(loading).display : null;

        return {
            exists: !!loading,
            classes: loadingClasses,
            hasShowClass: loadingClasses.includes('show'),
            display: loadingDisplay
        };
    });

    console.log('Loading indicator state:', loadingCheck);

    if (loadingCheck.hasShowClass) {
        console.log('✓✓✓ LOADING INDICATOR APPEARED - FORM SUBMISSION WORKING!');

        // Wait for API response
        console.log('Waiting for API response (up to 15 seconds)...');
        await sleep(15000);

        const resultsCheck = await page.evaluate(() => {
            const results = document.getElementById('osjonesResults');
            const output = document.getElementById('osjonesOutput');
            const hasError = results && results.classList.contains('error');
            const hasShow = results && results.classList.contains('show');

            return {
                hasShow,
                hasError,
                outputPreview: output ? output.textContent.substring(0, 300) : null
            };
        });

        console.log('Results state:', resultsCheck);

        if (resultsCheck.hasShow && !resultsCheck.hasError) {
            console.log('✓✓✓ API RESPONDED SUCCESSFULLY!');
            console.log('\nPreview:', resultsCheck.outputPreview);
            console.log('\n✓✓✓ OSJONES GENERATOR FULLY WORKING!');
        } else if (resultsCheck.hasError) {
            console.log('⚠ API returned error');
            console.log('Output:', resultsCheck.outputPreview);
        }
    } else {
        console.log('✗ Loading indicator did not appear');
        console.log('This suggests the event listener may not have attached correctly');

        // Check if there's an error in console
        await sleep(2000);
    }

    console.log('\nBrowser will remain open for 10 seconds...');
    await sleep(10000);

    await browser.close();
}

main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
