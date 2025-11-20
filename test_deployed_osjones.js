#!/usr/bin/env node
/**
 * Test OSJones on deployed GitHub Pages
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
    console.log('Testing OSJones on deployed GitHub Pages...');
    console.log('URL:', TOOLS_URL);

    const browser = await puppeteer.launch({
        headless: false,
        args: ['--no-sandbox'],
        defaultViewport: { width: 1400, height: 900 }
    });

    const page = await browser.newPage();

    // Log console messages
    page.on('console', msg => {
        const text = msg.text();
        if (text.includes('submit') || text.includes('listener') || text.includes('API')) {
            console.log('  [Browser]:', text);
        }
    });

    await page.goto(TOOLS_URL, { waitUntil: 'networkidle2', timeout: 60000 });
    console.log('✓ Page loaded');

    // Scroll to OSJones section
    await page.evaluate(() => {
        const headers = Array.from(document.querySelectorAll('h3'));
        const osjonesHeader = headers.find(h => h.textContent.includes('Army List'));
        if (osjonesHeader) {
            osjonesHeader.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    });
    await sleep(1000);

    // Type army list
    await page.click('#osjonesArmyList');
    await page.keyboard.type(SAMPLE_ARMY_LIST);
    console.log('✓ Army list entered');

    await sleep(500);

    // Click generate button
    await page.click('button[type="submit"]');
    console.log('✓ Generate button clicked');

    // Check for loading indicator
    await sleep(1000);
    const loadingAppeared = await page.evaluate(() => {
        const loading = document.getElementById('osjonesLoading');
        return loading && loading.classList.contains('show');
    });
    console.log('Loading indicator appeared:', loadingAppeared);

    if (loadingAppeared) {
        console.log('✓ Form submission working!');

        // Wait for results
        await sleep(15000);

        const hasResults = await page.evaluate(() => {
            const results = document.getElementById('osjonesResults');
            const hasError = results && results.classList.contains('error');
            const hasShow = results && results.classList.contains('show');
            const content = document.getElementById('osjonesOutput')?.textContent || '';

            return {
                hasShow,
                hasError,
                preview: content.substring(0, 200)
            };
        });

        console.log('Results:', hasResults);

        if (hasResults.hasShow && !hasResults.hasError) {
            console.log('✓✓✓ SUCCESS! OSJones generator working correctly!');
        } else if (hasResults.hasError) {
            console.log('⚠ API returned error:', hasResults.preview);
        }
    } else {
        console.log('✗ Loading indicator did not appear - form submission may have failed');
        console.log('This likely means GitHub Pages has not deployed the updated tools.html yet');
    }

    console.log('\nBrowser will remain open for 10 seconds for inspection...');
    await sleep(10000);

    await browser.close();
}

main().catch(error => {
    console.error('Error:', error);
    process.exit(1);
});
