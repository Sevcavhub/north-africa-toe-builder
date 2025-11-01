#!/usr/bin/env python3
"""
Extract vehicle and gun profiles from Battlegroup Overlord D-Day Scenarios text file.
Extracts equipment from D-Day landing scenarios (Omaha, Utah, British/Canadian beaches).
Context: June 6, 1944, Normandy invasion.
"""

import json
import re
from pathlib import Path

def parse_overlord_text():
    """Parse the Battlegroup Overlord text file for vehicles and guns."""

    # Initialize data structures
    vehicles = []
    guns = []

    # Expected D-Day equipment patterns
    vehicle_patterns = [
        # American vehicles
        r'DD Sherman',
        r'M4A4 Sherman',  # More specific first
        r'M4 Sherman',
        r'M10 Wolverine',
        r'M16 Halftrack',
        r'LVT-4 Buffalo',
        r'Sherman Bulldozer',
        r'DUKW',

        # British vehicles
        r'Churchill',
        r'Cromwell',
        r'Sherman.*AVRE',
        r'Sherman.*Crab',
        r'Sherman.*Crocodile',

        # German vehicles
        r'Panzer IV',
        r'StuG',
        r'Marder Ill H',  # Note: OCR has "Ill" not "III"
        r'Marder III H',  # Specific variant
        r'Marder Ill',    # OCR version
        r'Marder III',
        r'R-35',  # French tank in German service
        r'Jeep',  # British/US reconnaissance vehicle

        # Landing craft
        r'LCT\(R\)',  # More specific first
        r'LCT',
        r'LCVP',
        r'LCM',
        r'LCA',
    ]

    gun_patterns = [
        r'88mm PaK 43',
        r'50mm PaK 38',
        r'75mm infantry gun',
        r'20mm Flak 38',
        r'MG34',
        r'HMG42',
        r'Vickers HMG',
        r'\.30cal MMG',
        r'Bren gun',
        r'50mm mortar',
        r'60mm mortar',
        r'80mm mortar',
        r'105mm.*howitzer',
        r'25 pdr',
        r'3" mortar',
        r'76\.2mm Field Gun',
        r'155mm gun',
    ]

    # Read the text file
    txt_path = Path(r'D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Battlegroup-Overlord-D-Day-scenarios.txt')

    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract vehicles
    vehicle_set = set()
    for pattern in vehicle_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            vehicle_name = match.group(0)
            # Normalize name
            vehicle_name = vehicle_name.strip()
            vehicle_set.add(vehicle_name)

    # Extract guns
    gun_set = set()
    for pattern in gun_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            gun_name = match.group(0)
            # Normalize name
            gun_name = gun_name.strip()
            gun_set.add(gun_name)

    # Convert to structured data
    # Determine nation based on equipment type
    def determine_nation(equipment_name):
        equipment_lower = equipment_name.lower()
        if any(x in equipment_lower for x in ['sherman', 'm4', 'm10', 'm16', 'lvt', 'dukw', '.30cal', '60mm']):
            return 'american'
        elif any(x in equipment_lower for x in ['churchill', 'cromwell', 'vickers', 'bren', '25 pdr', '3" mortar', 'jeep']):
            return 'british'  # Jeep used by British recce in this scenario
        elif any(x in equipment_lower for x in ['panzer', 'stug', 'marder', 'pak', 'flak', 'mg34', 'hmg42', '50mm mortar']):
            return 'german'
        elif 'r-35' in equipment_lower:
            return 'french'  # French tank in German service
        elif any(x in equipment_lower for x in ['lca', 'lcvp', 'lcm', 'lct']):
            return 'allied'  # Landing craft used by US/British
        elif any(x in equipment_lower for x in ['155mm', '75mm infantry gun']):
            return 'german'  # Common German weapons
        elif '80mm' in equipment_lower:
            return 'german'  # German mortar caliber
        else:
            return 'unknown'

    # Process vehicles
    for vehicle_name in sorted(vehicle_set):
        nation = determine_nation(vehicle_name)

        vehicle_data = {
            'name': vehicle_name,
            'nation': nation,
            'type': 'AFV',
            'source': 'Battlegroup Overlord D-Day Scenarios',
            'context': 'D-Day, June 6, 1944, Normandy landings',
            'notes': ''
        }

        # Add specific notes based on vehicle type
        if 'DD' in vehicle_name:
            vehicle_data['notes'] = 'Duplex Drive amphibious tank'
        elif 'LVT' in vehicle_name:
            vehicle_data['notes'] = 'Amphibious landing vehicle'
        elif 'DUKW' in vehicle_name:
            vehicle_data['notes'] = 'Amphibious truck'
        elif any(x in vehicle_name for x in ['LCA', 'LCVP', 'LCM', 'LCT']):
            vehicle_data['notes'] = 'Landing craft'
        elif 'Marder' in vehicle_name:
            vehicle_data['notes'] = 'Tank destroyer'
        elif 'R-35' in vehicle_name:
            vehicle_data['notes'] = 'French tank in German service, used in static defense'
        elif 'AVRE' in vehicle_name:
            vehicle_data['notes'] = 'Armoured Vehicle Royal Engineers'
        elif 'Crab' in vehicle_name:
            vehicle_data['notes'] = 'Mine flail tank'
        elif 'Crocodile' in vehicle_name:
            vehicle_data['notes'] = 'Flamethrower tank'

        vehicles.append(vehicle_data)

    # Process guns
    for gun_name in sorted(gun_set):
        nation = determine_nation(gun_name)

        gun_data = {
            'name': gun_name,
            'nation': nation,
            'type': 'Gun',
            'source': 'Battlegroup Overlord D-Day Scenarios',
            'context': 'D-Day, June 6, 1944, Normandy landings',
            'notes': ''
        }

        # Add specific notes
        if 'PaK' in gun_name:
            gun_data['notes'] = 'Anti-tank gun'
        elif 'Flak' in gun_name:
            gun_data['notes'] = 'Anti-aircraft gun, also used in ground role'
        elif 'mortar' in gun_name.lower():
            gun_data['notes'] = 'Infantry mortar'
        elif 'howitzer' in gun_name.lower():
            gun_data['notes'] = 'Artillery piece'
        elif any(x in gun_name for x in ['MG', 'HMG', 'MMG', 'Bren', 'Vickers']):
            gun_data['notes'] = 'Machine gun'
        elif '25 pdr' in gun_name:
            gun_data['notes'] = 'British field gun/howitzer'

        guns.append(gun_data)

    return vehicles, guns


def main():
    """Main extraction function."""
    print("Extracting Battlegroup Overlord D-Day equipment...")

    vehicles, guns = parse_overlord_text()

    print(f"\nExtracted {len(vehicles)} vehicles:")
    for v in vehicles:
        print(f"  - {v['name']} ({v['nation']})")

    print(f"\nExtracted {len(guns)} guns:")
    for g in guns:
        print(f"  - {g['name']} ({g['nation']})")

    # Save to JSON files
    output_dir = Path(r'D:\north-africa-toe-builder\data\output')
    output_dir.mkdir(parents=True, exist_ok=True)

    vehicles_file = output_dir / 'battlegroup_overlord_vehicles.json'
    guns_file = output_dir / 'battlegroup_overlord_guns.json'

    with open(vehicles_file, 'w', encoding='utf-8') as f:
        json.dump(vehicles, f, indent=2, ensure_ascii=False)

    with open(guns_file, 'w', encoding='utf-8') as f:
        json.dump(guns, f, indent=2, ensure_ascii=False)

    print(f"\nSaved vehicles to: {vehicles_file}")
    print(f"Saved guns to: {guns_file}")

    # Create summary
    summary = {
        'extraction_date': '2025-10-31',
        'source': 'Battlegroup Overlord D-Day Scenarios',
        'context': 'D-Day, June 6, 1944, Normandy landings',
        'total_vehicles': len(vehicles),
        'total_guns': len(guns),
        'vehicles_by_nation': {},
        'guns_by_nation': {}
    }

    # Count by nation
    for v in vehicles:
        nation = v['nation']
        summary['vehicles_by_nation'][nation] = summary['vehicles_by_nation'].get(nation, 0) + 1

    for g in guns:
        nation = g['nation']
        summary['guns_by_nation'][nation] = summary['guns_by_nation'].get(nation, 0) + 1

    print("\n=== EXTRACTION SUMMARY ===")
    print(json.dumps(summary, indent=2))

    return summary


if __name__ == '__main__':
    main()
