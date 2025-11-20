#!/usr/bin/env node
/**
 * Check for JavaScript errors on tools page
 */

const puppeteer = require('puppeteer');

async function main() {
    const browser = await puppeteer.launch({
        headless: false,
        args: ['--no-sandbox'],
        defaultViewport: { width: 1400, height: 900 }
    });

    const page = await browser.newPage();

    // Capture all console messages
    const messages = [];
    page.on('console', msg => {
        messages.push({
            type: msg.type(),
            text: msg.text()
        });
        console.log(`[${msg.type()}]`, msg.text());
    });

    // Capture errors
    const errors = [];
    page.on('pageerror', error => {
        errors.push(error.message);
        console.error('[PAGE ERROR]', error.message);
    });

    console.log('Loading:', 'https://sevcavhub.github.io/north-africa-toe-builder/tools.html');

    await page.goto('https://sevcavhub.github.io/north-africa-toe-builder/tools.html', {
        waitUntil: 'networkidle2',
        timeout: 60000
    });

    await new Promise(resolve => setTimeout(resolve, 5000));

    console.log('\n=== Summary ===');
    console.log(`Total console messages: ${messages.length}`);
    console.log(`Errors: ${errors.length}`);

    if (errors.length > 0) {
        console.log('\nJavaScript Errors:');
        errors.forEach(err => console.log('  -', err));
    }

    // Check if initializeEventListeners was called
    const initCalled = await page.evaluate(() => {
        return typeof window.initializeEventListeners !== 'undefined';
    });

    console.log(`\ninitializeEventListeners defined: ${initCalled}`);

    await new Promise(resolve => setTimeout(resolve, 5000));
    await browser.close();
}

main().catch(console.error);
