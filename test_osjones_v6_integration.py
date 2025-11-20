#!/usr/bin/env python3
"""Test OSJones army list workflow with V6.1 generator (Sherman Jumbo)"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from scripts.battlegroup.book.parse_osjones_army_list import OSJonesArmyListParser
from scripts.battlegroup.book.generate_datacards_from_army_list_v6 import ArmyListDatacardGenerator

# Simulated OSJones army list with Sherman Jumbo (actual print format)
SAMPLE_ARMY_LIST = """
US Armoured Platoon  496 / 31br

180/15BR
Tank Platoon
3 M4A3E2 Sherman Jumbo

100/8BR
Tank Platoon
2 M4 Sherman (75mm)

90/6BR
Tank Destroyer
1 M10 Wolverine

60/4BR
Recon
2 M3 Stuart

35/2BR
Armoured Car
1 M8 Greyhound

Move    Armour    Weapon     HE      AP    Hits
M4A3E2 Sherman Jumbo      Off Road 8" Road 16"    Front 12 Side 8 Rear 6 Open-topped    75mmL40    6D6 HE    5/5/4/3/2 AP
M4 Sherman (75mm)         Off Road 8" Road 16"    Front 9 Side 6 Rear 6                 75mmL40    6D6 HE    5/5/4/3/2 AP
M10 Wolverine            Off Road 6" Road 12"    Front 7 Side 4 Rear 4 Open-topped    76.2mmL52  6D6 HE    7/7/6/5/4 AP
M3 Stuart                Off Road 10" Road 20"   Front 6 Side 5 Rear 5                 37mmL53    2D6 HE    4/4/3/2/1 AP
M8 Greyhound             Off Road 12" Road 24"   Front 5 Side 4 Rear 4 Open-topped    37mmL53    2D6 HE    4/4/3/2/1 AP
"""

def test_osjones_integration():
    print("="*70)
    print("Testing OSJones V6.1 Integration with Sherman Jumbo")
    print("="*70)

    # Parse army list
    parser = OSJonesArmyListParser()
    result = parser.parse_army_list(SAMPLE_ARMY_LIST)

    print(f"\nForce: {result.get('force_name', 'Unknown')}")
    print(f"Points: {result.get('points_total', 0)}")
    print(f"BR: {result.get('br_total', 0)}")
    print(f"\nEquipment extracted: {len(result['equipment'])} items")

    for eq in result['equipment']:
        print(f"  - {eq}")

    # Generate datacards
    print("\n" + "="*70)
    print("Generating datacards with V6.1 generator...")
    print("="*70 + "\n")

    output_dir = project_root / "interactive_outputs" / "test_osjones_v6"
    output_dir.mkdir(parents=True, exist_ok=True)

    generator = ArmyListDatacardGenerator()

    try:
        equipment_names = list(result['equipment'])

        # Check each equipment
        found_count = 0
        not_found_count = 0

        print("Equipment lookup results:")
        for name in equipment_names:
            bg_vehicle = generator.lookup_bg_builder_vehicle(name)
            bg_weapon = generator.lookup_bg_builder_weapon_by_name(name)

            if bg_vehicle or bg_weapon:
                found_count += 1
                print(f"  SUCCESS: {name}")
            else:
                not_found_count += 1
                print(f"  NOT FOUND: {name}")

        print(f"\nFound: {found_count}/{len(equipment_names)}")
        print(f"Not found: {not_found_count}/{len(equipment_names)}")

        # Generate datacard files
        generator.generate_datacards_from_list(equipment_names, output_dir)

        # Check for Sherman Jumbo specifically
        print("\n" + "="*70)
        print("Checking Sherman Jumbo datacard...")
        print("="*70)

        tanks_file = output_dir / "tanks.md"
        if tanks_file.exists():
            with open(tanks_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'Sherman Jumbo' in content:
                    print("SUCCESS: Sherman Jumbo datacard generated")

                    # Check if weapon is populated
                    if '75mmL40' in content or '75mm' in content:
                        print("SUCCESS: Main weapon populated (75mmL40)")
                    elif 'None' in content or not any(weapon in content for weapon in ['75mm', '76mm']):
                        print("WARNING: Weapon may not be populated correctly")

                    # Save sample for inspection
                    sample_file = project_root / "test_osjones_jumbo_datacard.html"
                    with open(sample_file, 'w', encoding='utf-8') as out:
                        out.write("<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Sherman Jumbo Test</title></head><body>")
                        out.write(content)
                        out.write("</body></html>")
                    print(f"\nFull datacards saved to: {sample_file}")
                else:
                    print("FAIL: Sherman Jumbo not in tanks.md")
        else:
            print("FAIL: tanks.md not generated")

        print(f"\nAll datacard files saved to: {output_dir}")

    finally:
        generator.close()

    print("\n" + "="*70)
    print("Test complete")
    print("="*70)

if __name__ == "__main__":
    test_osjones_integration()
