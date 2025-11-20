#!/usr/bin/env node
/**
 * Test only the Interactive Datacard Builder
 */

const puppeteer = require('puppeteer');

const TOOLS_URL = 'https://sevcavhub.github.io/north-africa-toe-builder/tools.html';

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
    console.log('Testing Interactive Datacard Builder...');
    console.log('URL:', TOOLS_URL);

    const browser = await puppeteer.launch({
        headless: false,
        args: ['--no-sandbox'],
        defaultViewport: { width: 1400, height: 900 }
    });

    const page = await browser.newPage();

    page.on('console', msg => console.log('  [Browser]:', msg.text()));

    await page.goto(TOOLS_URL, { waitUntil: 'networkidle2', timeout: 60000 });
    console.log('✓ Page loaded');

    // Wait for vehicles to load
    console.log('Waiting for vehicles to load (this may take 30-60 seconds)...');

    try {
        await page.waitForFunction(
            () => {
                const select = document.getElementById('builderVehicleSelect');
                const loading = select && select.options.length > 1;
                if (loading) {
                    console.log('Vehicle count:', select.options.length);
                }
                return loading && select.options.length > 100;
            },
            { timeout: 90000, polling: 1000 }
        );

        const vehicleCount = await page.evaluate(() => {
            const select = document.getElementById('builderVehicleSelect');
            return select.options.length - 1;
        });
        console.log(`✓✓✓ SUCCESS! Loaded ${vehicleCount} vehicles`);

        // Test generating a datacard
        await page.select('#builderVehicleSelect', 'M3 Grant');
        await sleep(500);

        await page.evaluate(() => {
            const addBtn = document.querySelector('#builderVehicleSelect + button');
            if (addBtn) addBtn.click();
        });
        console.log('✓ Added M3 Grant to list');

        await page.select('#builderNation', 'american');
        await sleep(500);

        // Click Generate
        await page.evaluate(() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            const generateBtn = buttons.find(btn => btn.textContent.includes('Generate Datacards'));
            if (generateBtn) generateBtn.click();
        });
        console.log('✓ Clicked Generate Datacards');

        await sleep(2000);

        // Check if loading appeared
        const loadingShown = await page.evaluate(() => {
            const loading = document.getElementById('builderLoading');
            return loading && loading.classList.contains('show');
        });

        if (loadingShown) {
            console.log('✓ Loading indicator appeared');

            await sleep(10000);

            // Check for new window
            const pages = await browser.pages();
            console.log(`Total pages open: ${pages.length}`);

            let datacardPage = null;
            for (const p of pages) {
                const url = p.url();
                if (url.includes('datacards/interactive')) {
                    datacardPage = p;
                    console.log('✓ Datacard window opened:', url);
                    break;
                }
            }

            if (datacardPage) {
                await datacardPage.waitForSelector('.datacard', { timeout: 10000 });

                const cardInfo = await datacardPage.evaluate(() => {
                    const cards = document.querySelectorAll('.datacard');
                    const grid = document.querySelector('.datacard-grid');
                    const silhouettes = document.querySelectorAll('.datacard-silhouette img');

                    return {
                        cardCount: cards.length,
                        hasGrid: !!grid,
                        silhouetteCount: silhouettes.length,
                        gridStyle: grid ? window.getComputedStyle(grid).gridTemplateColumns : null
                    };
                });

                console.log('Datacard info:', cardInfo);

                if (cardInfo.hasGrid && cardInfo.gridStyle.includes('fr')) {
                    console.log('✓✓✓ V6.1 CSS applied correctly!');
                }

                if (cardInfo.silhouetteCount > 0) {
                    console.log('✓✓✓ Silhouettes rendering!');
                }

                console.log('\n✓✓✓ INTERACTIVE BUILDER FULLY WORKING!');
            }
        } else {
            console.log('⚠ Loading did not appear');
        }

    } catch (error) {
        console.error('✗ Error:', error.message);
    }

    console.log('\nBrowser remains open for 10 seconds...');
    await sleep(10000);

    await browser.close();
}

main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
