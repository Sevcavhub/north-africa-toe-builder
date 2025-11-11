#!/usr/bin/env python3
"""
Generate sample datacards using ONLY bg_reference_vehicles data
No Phase 1-8 equipment tables - pure BattleGroup reference data
"""

import sqlite3
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
DATABASE_PATH = project_root / "database" / "master_database.db"

def generate_bg_only_sample():
    """Generate sample using only bg_reference_vehicles."""

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get sample vehicles from bg_reference_vehicles
    cursor.execute("""
        SELECT id, name, weapon_1, weapon_2, weapon_3, weapon_4,
               mount_1, mount_2, mount_3, mount_4,
               ammo_1, ammo_2, ammo_3, ammo_4,
               armor_front, armor_side, armor_rear,
               off_road_inches, road_inches,
               nation, vehicle_type, year_range
        FROM bg_reference_vehicles
        WHERE nation IN ('british', 'german', 'italian')
          AND armor_front IS NOT NULL
          AND weapon_1 IS NOT NULL
        ORDER BY nation, name
        LIMIT 6
    """)

    vehicles = cursor.fetchall()

    print(f"Found {len(vehicles)} vehicles from bg_reference_vehicles:")
    for v in vehicles:
        print(f"  {v['name']} ({v['nation']})")

    # Generate output
    output_file = project_root / "SAMPLE_DATACARDS_BG_ONLY.html"

    with open(output_file, 'w', encoding='utf-8') as f:
        # HTML header
        f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>BG Reference Data Only - Sample Datacards</title>
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

.datacard-header {
    text-align: center;
    margin-bottom: 8px;
    border-bottom: 2px solid #2c2416;
    padding-bottom: 4px;
}

.datacard-title {
    font-weight: bold;
    font-size: 14px;
    margin: 0;
}

.datacard-subtitle {
    font-size: 9px;
    font-style: italic;
    margin: 2px 0 0 0;
}

.datacard table {
    width: 100%;
    border-collapse: collapse;
    margin: 4px 0;
    font-size: 8px;
}

.datacard th {
    background-color: #8b7355;
    color: white;
    font-weight: bold;
    padding: 2px 3px;
    border: 1px solid #2c2416;
    text-align: center;
    font-size: 7px;
}

.datacard td {
    background-color: #f5f5dc;
    border: 1px solid #2c2416;
    padding: 2px 3px;
    text-align: center;
    font-size: 8px;
}
    </style>
</head>
<body>
<h1>Sample Datacards - BG Reference Data Only</h1>
<p><strong>Data Source:</strong> bg_reference_vehicles table ONLY (no Phase 1-8 equipment tables)</p>
<p><strong>Count:</strong> """ + str(len(vehicles)) + """ vehicles</p>

<div class="datacard-grid">
""")

        # Generate each datacard
        for vehicle in vehicles:
            nation = vehicle['nation'] or 'unknown'

            f.write(f"""
<div class="datacard">
<div class="datacard-header">
<p class="datacard-title">{vehicle['name'].upper()}</p>
<p class="datacard-subtitle">{vehicle['year_range'] or '1940-1945'} | {vehicle['vehicle_type'] or 'Vehicle'} | {nation.title()}</p>
</div>

<table>
<tr>
<th>VEHICLE</th>
<th colspan="2">MOVEMENT</th>
<th colspan="3">ARMOUR</th>
<th colspan="3">ARMAMENT</th>
</tr>
<tr>
<th></th>
<th>Off-Road</th>
<th>Road</th>
<th>F</th>
<th>S</th>
<th>R</th>
<th>Weapon</th>
<th>Mount</th>
<th>Ammo</th>
</tr>
<tr>
<td>{vehicle['vehicle_type'] or 'Vehicle'}</td>
<td>{vehicle['off_road_inches'] or '-'}"</td>
<td>{vehicle['road_inches'] or '-'}"</td>
<td>{vehicle['armor_front'] or '-'}</td>
<td>{vehicle['armor_side'] or '-'}</td>
<td>{vehicle['armor_rear'] or '-'}</td>
<td>{vehicle['weapon_1'] or 'None'}</td>
<td>{vehicle['mount_1'] or '-'}</td>
<td>{vehicle['ammo_1'] or '-'}</td>
</tr>
</table>
""")

            # Secondary weapons if present
            if vehicle['weapon_2']:
                f.write("<table><tr><th colspan='3'>Secondary Armament</th></tr>\n")
                for i in range(2, 5):
                    weapon = vehicle[f'weapon_{i}']
                    if weapon:
                        mount = vehicle[f'mount_{i}'] or '-'
                        ammo = vehicle[f'ammo_{i}'] or '-'
                        f.write(f"<tr><td>{weapon}</td><td>{mount}</td><td>{ammo}</td></tr>\n")
                f.write("</table>\n")

            f.write("</div>\n")

        # Close HTML
        f.write("""
</div>
</body>
</html>
""")

    conn.close()
    print(f"\nGenerated: {output_file}")
    print("Open in browser to view/print")

if __name__ == "__main__":
    generate_bg_only_sample()
