#!/usr/bin/env python3
"""
Generate sample datacards v6 for print testing
V6 changes:
- Use bg_builder_vehicles.name as lookup key instead of equipment.canonical_id
"""

import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from scripts.battlegroup.book.generate_book_datacards_v6_1 import BookDatacardGenerator

DATABASE_PATH = project_root / "database" / "master_database.db"

# Sample equipment - Using bg_builder_vehicles.name as lookup
# Format: Either a string (auto-detect nation) or a dict with 'name' and 'nation' keys

SAMPLE_EQUIPMENT = [
    'M3 Grant',              # British medium tank (auto-detected)
    'SdKfz 251/1',           # German halftrack (auto-detected)
    'M13/40',                # Italian medium tank (auto-detected)
    'Matilda II',            # British infantry tank (auto-detected)
    'Crusader III',          # British cruiser tank (auto-detected)
    'Churchill III/IV',      # British infantry tank (auto-detected)
    'Panzer III H',          # German medium tank (auto-detected)
    'Panzer IV F2',          # German medium tank (auto-detected)

    # Override nation: Sherman used by British instead of American
    {'name': 'M4 Sherman (A1,A2,A3)', 'nation': 'british'},
]

def generate_sample():
    """Generate sample datacard page for print testing."""

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    generator = BookDatacardGenerator()

    # Get equipment data using bg_builder_vehicles.name as lookup key
    equipment_list = []
    for item in SAMPLE_EQUIPMENT:
        # Handle both string format and dict format
        if isinstance(item, str):
            vehicle_name = item
            nation_override = None  # Auto-detect
        else:
            vehicle_name = item['name']
            nation_override = item.get('nation')  # User-specified nation

        cursor.execute("""
            SELECT id, name
            FROM bg_builder_vehicles
            WHERE name = ?
        """, (vehicle_name,))

        row = cursor.fetchone()
        if row:
            equipment_list.append({
                'bg_builder_vehicle_id': row['id'],
                'name': row['name'],
                'nation_override': nation_override,  # Pass override to generator
                'equipment_type': 'vehicle',
                'category': 'armored_vehicle'
            })
        else:
            print(f"[WARNING] Vehicle not found in bg_builder_vehicles: {vehicle_name}")

    # Generate output file (HTML for direct printing)
    output_file = project_root / "SAMPLE_DATACARDS_V6.html"

    with open(output_file, 'w', encoding='utf-8') as f:
        # Write HTML header
        f.write("<!DOCTYPE html>\n<html>\n<head>\n")
        f.write("<meta charset='UTF-8'>\n")
        f.write("<title>Sample Datacards v6 - Print Test</title>\n")

        # Write CSS (extract from actual generator to ensure consistency)
        import re
        gen_path = project_root / "scripts" / "battlegroup" / "book" / "generate_book_datacards_v6_1.py"
        with open(gen_path, 'r', encoding='utf-8') as gen_file:
            gen_content = gen_file.read()
            # Use non-greedy match to stop at first closing """
            css_match = re.search(r'css = """(.*?)"""', gen_content, re.DOTALL)
            if css_match:
                css = css_match.group(1)
                # CSS already includes <style> tags, just write it directly
                # But strip markdown separator if present
                if '\n---\n' in css:
                    css = css.split('\n---\n')[0]
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
