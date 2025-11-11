#!/usr/bin/env python3
"""
Test script to verify bg_reference_vehicles data prioritization fix.

Generates sample datacards for equipment with reference_vehicle_id to verify:
1. Display name uses bg_reference_vehicles.name
2. Armor values use bg_reference_vehicles armor columns
3. Movement uses bg_reference_vehicles off_road_inches/road_inches
"""

import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from scripts.battlegroup.book.generate_book_datacards import BookDatacardGenerator

DATABASE_PATH = project_root / "database" / "master_database.db"

def get_sample_equipment_with_reference():
    """Get sample equipment items that have reference_vehicle_id."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            e.canonical_id,
            e.name as equipment_name,
            e.nation,
            e.equipment_type,
            e.category,
            eb.reference_vehicle_id,
            bg.name as bg_name,
            bg.armor_front,
            bg.armor_side,
            bg.armor_rear,
            bg.off_road_inches,
            bg.road_inches
        FROM equipment e
        JOIN equipment_battlegroup eb ON e.canonical_id = eb.equipment_id
        LEFT JOIN bg_reference_vehicles bg ON eb.reference_vehicle_id = bg.id
        WHERE eb.reference_vehicle_id IS NOT NULL
        LIMIT 5
    """)

    items = cursor.fetchall()
    conn.close()

    return items

def main():
    """Generate sample datacards to test the fix."""
    print("=" * 80)
    print("Testing bg_reference_vehicles Data Prioritization Fix")
    print("=" * 80)
    print()

    # Get sample equipment
    sample_items = get_sample_equipment_with_reference()

    if not sample_items:
        print("ERROR: No equipment found with reference_vehicle_id!")
        return 1

    print(f"Found {len(sample_items)} equipment items with reference_vehicle_id:\n")

    for item in sample_items:
        print(f"Equipment Table Name: {item['equipment_name']}")
        print(f"BG Reference Name:    {item['bg_name']}")
        print(f"Armor (F/S/R):        {item['armor_front']}/{item['armor_side']}/{item['armor_rear']}")
        print(f"Movement (Off/Road):  {item['off_road_inches']}\"/  {item['road_inches']}\"")
        print(f"Reference Vehicle ID: {item['reference_vehicle_id']}")
        print()

    # Generate datacards
    print("-" * 80)
    print("Generating sample datacards...")
    print("-" * 80)
    print()

    generator = BookDatacardGenerator()

    # Create output file
    output_file = project_root / "TEST_BG_REFERENCE_DATACARDS.html"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>BG Reference Vehicles Data Test</title>
    <style>
@media print {
    @page {
        size: A4 landscape;
        margin: 10mm;
    }
}

.datacard-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin: 20px;
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
</head>
<body>
<h1>BG Reference Vehicles Data Prioritization Test</h1>
<p>This test verifies that equipment datacards use bg_reference_vehicles data when available.</p>
<p><strong>Expected Results:</strong></p>
<ul>
    <li>Equipment names should show bg_reference_vehicles.name (e.g., "M4A4 Sherman" not "TANK_M4_SHERMAN")</li>
    <li>Armor values should show bg_reference_vehicles armor columns (e.g., K, L, N)</li>
    <li>Movement should show bg_reference_vehicles inches (e.g., 8", 14")</li>
</ul>

<div class="datacard-grid">
""")

        # Generate datacards for sample items
        for item in sample_items:
            equipment_dict = {
                'canonical_id': item['canonical_id'],
                'name': item['equipment_name'],
                'nation': item['nation'],
                'equipment_type': item['equipment_type'],
                'category': item['category']
            }

            datacard_html = generator.generate_datacard_markdown(equipment_dict, 'r')
            f.write(datacard_html)
            f.write('\n')

        f.write("""
</div>
</body>
</html>
""")

    generator.close()

    print(f"[SUCCESS] Test datacards generated: {output_file}")
    print()
    print("=" * 80)
    print("Test Complete!")
    print("=" * 80)
    print()
    print("Open the HTML file in a browser to verify:")
    print(f"  {output_file}")
    print()
    print("Verify that:")
    print("  1. Equipment names show BG reference names (e.g., 'M4A4 Sherman')")
    print("  2. Armor values show letter grades (e.g., K, L, N)")
    print("  3. Movement shows inches format (e.g., 8\", 14\")")
    print()

    return 0

if __name__ == "__main__":
    sys.exit(main())
