#!/usr/bin/env python3
"""
Test long vehicle names for title wrapping
"""

import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from scripts.battlegroup.book.generate_book_datacards_v5_5 import BookDatacardGenerator

DATABASE_PATH = project_root / "database" / "master_database.db"

# Test with longest names (29 characters)
LONG_NAME_IDS = [
    17,   # Humber Light Recce Vehicle II (29 chars)
    196,  # Marmon-Herrington II A (20mm) (29 chars)
    220,  # Panzer III H (for comparison - medium length)
]

def generate_sample():
    """Generate sample with long names."""

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    generator = BookDatacardGenerator()

    # Get equipment data directly from bg_reference_vehicles
    equipment_list = []
    for ref_id in LONG_NAME_IDS:
        cursor.execute("""
            SELECT name, nation, vehicle_type
            FROM bg_reference_vehicles
            WHERE id = ?
        """, (ref_id,))

        row = cursor.fetchone()
        if row:
            equipment_list.append({
                'reference_vehicle_id': ref_id,
                'name': row['name'],
                'nation': row['nation'],
                'equipment_type': row['vehicle_type']
            })

    # Generate output file (HTML for direct printing)
    output_file = project_root / "TEST_LONG_NAME.html"

    with open(output_file, 'w', encoding='utf-8') as f:
        # Write HTML header
        f.write("<!DOCTYPE html>\n<html>\n<head>\n")
        f.write("<meta charset='UTF-8'>\n")
        f.write("<title>Long Name Test</title>\n")

        # Write CSS (extract from actual generator)
        import re
        gen_path = project_root / "scripts" / "battlegroup" / "book" / "generate_book_datacards_v5_5.py"
        with open(gen_path, 'r', encoding='utf-8') as gen_file:
            gen_content = gen_file.read()
            css_match = re.search(r'css = """(.*?)"""', gen_content, re.DOTALL)
            if css_match:
                css = css_match.group(1)
                if '\n---\n' in css:
                    css = css.split('\n---\n')[0]
                f.write(css)

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

    print(f"Test generated: {output_file}")
    print(f"Total cards: {len(equipment_list)}")

    return output_file

if __name__ == "__main__":
    generate_sample()
