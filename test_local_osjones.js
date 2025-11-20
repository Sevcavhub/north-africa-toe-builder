#!/usr/bin/env node
/**
 * Test OSJones form submission with local HTML
 */

const puppeteer = require('puppeteer');
const path = require('path');

const LOCAL_FILE = 'file://' + path.resolve('test_local_tools.html');

const SAMPLE_ARMY_LIST = `Deutsches Afrikakorps
496 Points | 31 BR

PANZER IV F2                           150pts
88MM FLAK 36                            90pts`;

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
    console.log('Testing OSJones form submission locally...');
    console.log('File:', LOCAL_FILE);

    const browser = await puppeteer.launch({
        headless: false,
        args: ['--no-sandbox'],
        defaultViewport: { width: 1200, height: 800 }
    });

    const page = await browser.newPage();

    // Log all console messages
    page.on('console', msg => {
        console.log('  [Browser]:', msg.text());
    });

    await page.goto(LOCAL_FILE, { waitUntil: 'networkidle2' });
    console.log('Page loaded');

    await sleep(1000);

    // Type into textarea
    await page.type('#osjonesArmyList', SAMPLE_ARMY_LIST);
    console.log('Army list typed');

    await sleep(500);

    // Click submit button
    await page.click('button[type="submit"]');
    console.log('Submit button clicked');

    // Wait for loading indicator
    await sleep(500);
    const loadingVisible = await page.evaluate(() => {
        const loading = document.getElementById('osjonesLoading');
        return loading && loading.style.display === 'block';
    });
    console.log('Loading visible:', loadingVisible);

    // Wait for response
    await sleep(10000);

    const resultsVisible = await page.evaluate(() => {
        const results = document.getElementById('osjonesResults');
        return results && results.style.display === 'block';
    });
    console.log('Results visible:', resultsVisible);

    if (resultsVisible) {
        const resultsText = await page.evaluate(() => {
            return document.getElementById('osjonesOutput').textContent.substring(0, 300);
        });
        console.log('Results preview:', resultsText);
    }

    console.log('\nTest complete. Browser will remain open for 5 seconds...');
    await sleep(5000);

    await browser.close();
}

main().catch(error => {
    console.error('Error:', error);
    process.exit(1);
});
