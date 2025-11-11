#!/usr/bin/env python3
"""
Generate sample datacards v5.2 for print testing
Demonstrates fixes:
- Weapons from bg_reference_vehicles (weapon_1-4, mount_1-4)
- Ammo counts from bg_reference_vehicles (ammo_1-4)
- Weapon performance tables with HE/AP values
"""

import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from scripts.battlegroup.book.generate_book_datacards import BookDatacardGenerator

DATABASE_PATH = project_root / "database" / "master_database.db"

# Sample equipment IDs - British tanks with good reference data
SAMPLE_EQUIPMENT = [
    'GBR_A10_CRUISER_MK_II',
    'GBR_A12_MATILDA_II',
    'GBR_A13_MK_II',
    'GBR_CRUSADER_I',
    'GBR_CRUSADER_III',
    'GER_PANZER_III_AUSF_H'  # Add one German tank for variety
]

def generate_sample():
    """Generate sample datacard page for print testing."""

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    generator = BookDatacardGenerator()

    # Get equipment data
    equipment_list = []
    for equip_id in SAMPLE_EQUIPMENT:
        cursor.execute("""
            SELECT canonical_id, name, nation, equipment_type, category
            FROM equipment
            WHERE canonical_id = ?
        """, (equip_id,))

        row = cursor.fetchone()
        if row:
            equipment_list.append({
                'canonical_id': row['canonical_id'],
                'name': row['name'],
                'nation': row['nation'],
                'equipment_type': row['equipment_type'],
                'category': row['category']
            })

    # Generate output file (HTML for direct printing)
    output_file = project_root / "SAMPLE_DATACARDS_V5.2.html"

    with open(output_file, 'w', encoding='utf-8') as f:
        # Write HTML header
        f.write("<!DOCTYPE html>\n<html>\n<head>\n")
        f.write("<meta charset='UTF-8'>\n")
        f.write("<title>Sample Datacards v5.2 - Print Test</title>\n")

        # Write CSS (extract from actual generator to ensure consistency)
        import re
        gen_path = project_root / "scripts" / "battlegroup" / "book" / "generate_book_datacards.py"
        with open(gen_path, 'r', encoding='utf-8') as gen_file:
            gen_content = gen_file.read()
            css_match = re.search(r'css = """(.*)"""', gen_content, re.DOTALL)
            if css_match:
                css = css_match.group(1)
                f.write(css)
            else:
                # Fallback: write minimal CSS
                f.write("""<style>
@media print {
    @page { size: A4 landscape; margin: 10mm; }
    .datacard-grid { page-break-after: always; }
    .datacard { page-break-inside: avoid; }
}
.datacard-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin: 20px 0;
}
</style>
""")

        # Close head, open body
        f.write("</head>\n<body>\n")

        # Open grid
        f.write('<div class="datacard-grid">\n\n')

        # Generate datacards
        for equipment in equipment_list:
            datacard = generator.generate_datacard_markdown(equipment, 'r')
            f.write(datacard)
            f.write('\n')

        # Close grid and HTML
        f.write("</div>\n")
        f.write("</body>\n</html>\n")

    generator.close()
    conn.close()

    print(f"Sample datacards generated: {output_file}")
    print(f"Total cards: {len(equipment_list)}")
    print("\nTo view/print:")
    print("1. Open {output_file} in web browser")
    print("2. Use browser's Print function (Ctrl+P) for PDF or direct printing")

    return output_file

if __name__ == "__main__":
    generate_sample()
