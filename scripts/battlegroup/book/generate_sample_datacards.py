#!/usr/bin/env python3
"""
Generate sample datacards for testing V5.5 format.

V5.5 features:
- Armor modifiers (Open-topped, etc.)
- Silhouette images
- Nation-specific color themes
- Multi-row armament tables
- 16px centered titles

6 items in 3x2 grid:
- Open-topped vehicle
- Soft-skinned vehicle
- Vehicle with Schürzen
- AT gun
- 2 regular tanks
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# Import V5.5 generator (generate_book_datacards.py now uses V5.5)
from scripts.battlegroup.book.generate_book_datacards import BookDatacardGenerator

# Test items
TEST_ITEMS = [
    {
        'canonical_id': 'GER_SDKFZ_250',
        'name': 'SdKfz 250',
        'nation': 'german',
        'equipment_type': 'halftrack',
        'category': 'halftracks'
    },
    {
        'canonical_id': 'GBR_BEDFORD_MW',
        'name': 'Bedford MW',
        'nation': 'british',
        'equipment_type': 'truck',
        'category': 'trucks'
    },
    {
        'canonical_id': 'GER_PANZER_IV_AUSF_E',
        'name': 'Panzer IV Ausf E',
        'nation': 'german',
        'equipment_type': 'tank',
        'category': 'tanks'
    },
    {
        'canonical_id': 'GBR_2_PDR_AT',
        'name': '2 Pdr AT',
        'nation': 'british',
        'equipment_type': 'gun',
        'category': 'anti_tank_guns'
    },
    {
        'canonical_id': 'GBR_MATILDA_II',
        'name': 'Matilda II',
        'nation': 'british',
        'equipment_type': 'tank',
        'category': 'tanks'
    },
    {
        'canonical_id': 'GBR_A15_CRUSADER_MK_I',
        'name': 'A15 Crusader Mk I',
        'nation': 'british',
        'equipment_type': 'tank',
        'category': 'tanks'
    }
]


def main():
    """Generate sample datacards."""

    output_file = project_root / 'books' / 'battleaxe' / 'book' / 'src' / 'chapter2' / 'SAMPLE_DATACARDS_TEST.md'

    generator = BookDatacardGenerator()

    print('Generating sample datacards...\n')

    with open(output_file, 'w', encoding='utf-8') as f:
        # Write title
        f.write('# Sample Datacards - V5 Format Test\n\n')

        # Write CSS (from existing generator)
        css = """<style>
@media print {
    @page {
        size: A4 landscape;
        margin: 10mm;
    }

    .datacard-grid {
        page-break-after: always;
    }

    .datacard {
        page-break-inside: avoid;
    }
}

.datacard-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin: 20px 0;
}

.datacard {
    border: 3px solid #2c2416;
    padding: 8px;
    background-color: #d4c5a0;
    box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    font-family: Arial, sans-serif;
}

/* Nation-Specific Color Themes */
.datacard.datacard-german {
    background-color: #797768;
    border-color: #1a1a1a;
}

.datacard.datacard-german .datacard-title {
    color: white;
}

.datacard.datacard-german .datacard-subtitle {
    color: white;
}

.datacard.datacard-german .datacard-special-rules {
    color: white;
}

.datacard.datacard-german th {
    background-color: #ECD1A2;
    color: #1a1a1a;
}

.datacard.datacard-german td {
    background-color: #e8dcc8;
    color: #1a1a1a;
}

.datacard.datacard-british {
    background-color: #d4c5a0;
    border-color: #2c2416;
}

.datacard.datacard-british th {
    background-color: #8b7355;
    color: white;
}

.datacard.datacard-british td {
    background-color: #f5f5dc;
    color: #1a1a1a;
}

.datacard.datacard-italian {
    background-color: #c8b88a;
    border-color: #5a4a2a;
}

.datacard.datacard-italian th {
    background-color: #6b5d3f;
    color: white;
}

.datacard.datacard-italian td {
    background-color: #e8dcc0;
    color: #1a1a1a;
}

.datacard.datacard-american {
    background-color: #b8c5a0;
    border-color: #3a4a2a;
}

.datacard.datacard-american th {
    background-color: #5a6d45;
    color: white;
}

.datacard.datacard-american td {
    background-color: #dce8cf;
    color: #1a1a1a;
}

.datacard.datacard-french {
    background-color: #b8c4d4;
    border-color: #2a3a4a;
}

.datacard.datacard-french th {
    background-color: #4a5a6d;
    color: white;
}

.datacard.datacard-french td {
    background-color: #d8e4f4;
    color: #1a1a1a;
}

.datacard-header {
    display: flex;
    gap: 10px;
    margin-bottom: 8px;
    align-items: center;
}

.datacard-silhouette {
    width: 80px;
    height: 60px;
    background-color: #1a1a1a;
    border: 1px solid #333;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.datacard-silhouette img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    filter: brightness(0) invert(1);
}

.datacard-title-block {
    flex: 1;
    text-align: right;
}

.datacard-title {
    font-weight: bold;
    font-size: 14px;
    margin: 0;
    line-height: 1.2;
}

.datacard-subtitle {
    font-size: 9px;
    font-style: italic;
    margin: 2px 0 0 0;
    line-height: 1.2;
}

.datacard-special-rules {
    font-size: 7px;
    font-style: italic;
    margin: 2px 0 0 0;
    line-height: 1.2;
    color: #5a4a3a;
}

.datacard table {
    width: 100%;
    border-collapse: collapse;
    margin: 2px 0;
    font-size: 8px;
}

.datacard th {
    background-color: #8b7355;
    color: white;
    font-weight: bold;
    padding: 1px 2px;
    border: 1px solid #2c2416;
    text-align: center;
    font-size: 7px;
    line-height: 1.0;
}

.datacard td {
    background-color: #f5f5dc;
    border: 1px solid #2c2416;
    padding: 1px 2px;
    text-align: center;
    font-size: 8px;
    line-height: 1.0;
}

.datacard .main-header {
    font-size: 8px;
    font-weight: bold;
}

.armor-modifier-row td {
    font-style: italic;
    font-size: 7px;
    padding: 1px 3px;
}
</style>

---

"""
        f.write(css)

        # Open grid
        f.write('<div class="datacard-grid">\n\n')

        # Generate each datacard
        for item in TEST_ITEMS:
            print(f"Generating: {item['name']}")
            datacard = generator.generate_datacard_markdown(item, 'r')
            f.write(datacard)
            f.write('\n')

        # Close grid
        f.write('</div>\n')

    generator.close()

    print(f'\n[SUCCESS] Sample datacards generated: {output_file}')
    print('\nOpen in browser to view/print:')
    print(f'  cd books/battleaxe/book && mdbook build && start book/index.html')


if __name__ == '__main__':
    main()
