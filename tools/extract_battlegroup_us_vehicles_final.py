#!/usr/bin/env python3
"""
Extract US vehicle profiles from BattleGroup datacard PDF
Final version with comprehensive manual parsing
"""

import json
import re
import sys
from pathlib import Path

try:
    import PyPDF2
except ImportError:
    print("Installing PyPDF2...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
    import PyPDF2

# Manual extraction based on PDF text examination
VEHICLES = [
    {
        "name": "M5 Stuart (A1, A2, A3)",
        "year_range": "1942-1945",
        "off_road_inches": 12,
        "road_inches": 18,
        "special_movement": None,
        "armor_front": "L",
        "armor_side": "N",
        "armor_rear": "N",
        "weapons": [
            {"weapon": "37mmL53", "mount": "Turret", "ammo": 12},
            {"weapon": "MG", "mount": "Co-axial", "ammo": None},
            {"weapon": "MG", "mount": "Hull", "ammo": None}
        ]
    },
    {
        "name": "M4 Sherman",
        "year_range": "1942-1945",
        "off_road_inches": 9,
        "road_inches": 14,
        "special_movement": None,
        "armor_front": "K",
        "armor_side": "L",
        "armor_rear": "N",
        "weapons": [
            {"weapon": "75mmL40", "mount": "Turret", "ammo": 9},
            {"weapon": "MG", "mount": "Co-axial", "ammo": None},
            {"weapon": "MG", "mount": "Hull", "ammo": None}
        ]
    },
    {
        "name": "M4A3E8 Sherman",
        "year_range": "1945",
        "off_road_inches": 10,
        "road_inches": 15,
        "special_movement": "HVSS",
        "armor_front": "K",
        "armor_side": "L",
        "armor_rear": "M",
        "weapons": [
            {"weapon": "76mmL53", "mount": "Turret", "ammo": 7},
            {"weapon": "MG", "mount": "Co-axial", "ammo": None},
            {"weapon": "MG", "mount": "Hull", "ammo": None}
        ]
    },
    {
        "name": "M4 Sherman '76'",
        "year_range": "1944-1945",
        "off_road_inches": 9,
        "road_inches": 14,
        "special_movement": None,
        "armor_front": "K",
        "armor_side": "L",
        "armor_rear": "N",
        "weapons": [
            {"weapon": "76mmL53", "mount": "Turret", "ammo": 7},
            {"weapon": "MG", "mount": "Co-axial", "ammo": None},
            {"weapon": "MG", "mount": "Hull", "ammo": None}
        ]
    },
    {
        "name": "M4A3E2 Jumbo '75'",
        "year_range": "1945",
        "off_road_inches": 7,
        "road_inches": 11,
        "special_movement": None,
        "armor_front": "G",
        "armor_side": "K",
        "armor_rear": "M",
        "weapons": [
            {"weapon": "75mmL40", "mount": "Turret", "ammo": 9},
            {"weapon": "MG", "mount": "Co-axial", "ammo": None},
            {"weapon": "MG", "mount": "Hull", "ammo": None}
        ]
    },
    {
        "name": "M4A3E2 Jumbo '76'",
        "year_range": "1945",
        "off_road_inches": 7,
        "road_inches": 11,
        "special_movement": None,
        "armor_front": "G",
        "armor_side": "K",
        "armor_rear": "M",
        "weapons": [
            {"weapon": "76mmL53", "mount": "Turret", "ammo": 7},
            {"weapon": "MG", "mount": "Co-axial", "ammo": None},
            {"weapon": "MG", "mount": "Hull", "ammo": None}
        ]
    },
    {
        "name": "M4 Sherman 'Dozer'",
        "year_range": "1944-1945",
        "off_road_inches": 9,
        "road_inches": 14,
        "special_movement": "Engineer",
        "armor_front": "K",
        "armor_side": "L",
        "armor_rear": "M",
        "weapons": [
            {"weapon": "75mmL40", "mount": "Turret", "ammo": 9},
            {"weapon": "MG", "mount": "Co-axial", "ammo": None},
            {"weapon": "MG", "mount": "Hull", "ammo": None}
        ]
    },
    {
        "name": "M5 'Recce'",
        "year_range": "1944-1945",
        "off_road_inches": 12,
        "road_inches": 18,
        "special_movement": None,
        "armor_front": "L",
        "armor_side": "N",
        "armor_rear": "M",
        "weapons": [
            {"weapon": "MG", "mount": "Pintle", "ammo": None},
            {"weapon": "MG", "mount": "Hull", "ammo": None}
        ]
    },
    {
        "name": "M4 Sherman Crab",
        "year_range": "1945",
        "off_road_inches": 9,
        "road_inches": 14,
        "special_movement": "Engineer",
        "armor_front": "K",
        "armor_side": "L",
        "armor_rear": "N",
        "weapons": [
            {"weapon": "75mmL40", "mount": "Turret", "ammo": 9},
            {"weapon": "MG", "mount": "Co-axial", "ammo": None},
            {"weapon": "MG", "mount": "Hull", "ammo": None}
        ]
    },
    {
        "name": "M4 Sherman 'Crocodile'",
        "year_range": "1945",
        "off_road_inches": 9,
        "road_inches": 14,
        "special_movement": None,
        "armor_front": "K",
        "armor_side": "L",
        "armor_rear": "M",
        "weapons": [
            {"weapon": "75mmL40", "mount": "Turret", "ammo": 9},
            {"weapon": "MG", "mount": "Co-axial", "ammo": None},
            {"weapon": "Flamethrower", "mount": "Hull", "ammo": 4}
        ]
    },
    {
        "name": "M4 Sherman Mineroller",
        "year_range": "1944-1945",
        "off_road_inches": 9,
        "road_inches": 14,
        "special_movement": None,
        "armor_front": "K",
        "armor_side": "L",
        "armor_rear": "N",
        "weapons": [
            {"weapon": "75mmL40", "mount": "Turret", "ammo": 9},
            {"weapon": "MG", "mount": "Co-axial", "ammo": None},
            {"weapon": "MG", "mount": "Hull", "ammo": None}
        ]
    },
    {
        "name": "M4 Sherman 'Calliope'",
        "year_range": "1945",
        "off_road_inches": 9,
        "road_inches": 14,
        "special_movement": None,
        "armor_front": "K",
        "armor_side": "L",
        "armor_rear": "M",
        "weapons": [
            {"weapon": "75mmL40", "mount": "Turret", "ammo": 9},
            {"weapon": "MG", "mount": "Co-axial", "ammo": None},
            {"weapon": "MG", "mount": "Hull", "ammo": None},
            {"weapon": "4.5\" launcher", "mount": "Hull", "ammo": 3}
        ]
    },
    {
        "name": "M10 Wolverine",
        "year_range": "1944-1945",
        "off_road_inches": 9,
        "road_inches": 14,
        "special_movement": "Open-topped",
        "armor_front": "M",
        "armor_side": "N",
        "armor_rear": "O",
        "weapons": [
            {"weapon": "76mmL53", "mount": "Turret", "ammo": 6},
            {"weapon": "MG", "mount": "Pintle", "ammo": None}
        ]
    },
    {
        "name": "M7 Priest",
        "year_range": "1943-1945",
        "off_road_inches": 9,
        "road_inches": 14,
        "special_movement": "Open-topped",
        "armor_front": "M",
        "armor_side": "O",
        "armor_rear": "O",
        "weapons": [
            {"weapon": "105mmL22", "mount": "Hull", "ammo": 7},
            {"weapon": "MG", "mount": "Pintle", "ammo": None}
        ]
    },
    {
        "name": "M36 Jackson",
        "year_range": "1945",
        "off_road_inches": 9,
        "road_inches": 14,
        "special_movement": "Open-topped",
        "armor_front": "M",
        "armor_side": "N",
        "armor_rear": "O",
        "weapons": [
            {"weapon": "90mmL53", "mount": "Turret", "ammo": 6},
            {"weapon": "MG", "mount": "Pintle", "ammo": None}
        ]
    },
    {
        "name": "M8 Scott",
        "year_range": "1943-1945",
        "off_road_inches": 12,
        "road_inches": 18,
        "special_movement": "Open-topped",
        "armor_front": "L",
        "armor_side": "N",
        "armor_rear": "N",
        "weapons": [
            {"weapon": "75mmL15", "mount": "Turret", "ammo": 7},
            {"weapon": "MG", "mount": "Pintle", "ammo": None}
        ]
    },
    {
        "name": "M3 Grant",
        "year_range": "1942-1943",
        "off_road_inches": 9,
        "road_inches": 14,
        "special_movement": None,
        "armor_front": "L",
        "armor_side": "N",
        "armor_rear": "N",
        "weapons": [
            {"weapon": "75mmL40", "mount": "Hull", "ammo": 9},
            {"weapon": "37mmL53", "mount": "Turret", "ammo": 6},
            {"weapon": "MG", "mount": "Co-axial", "ammo": None},
            {"weapon": "MG", "mount": "Hull", "ammo": None}
        ]
    },
    {
        "name": "M3 Lee",
        "year_range": "1942-1943",
        "off_road_inches": 9,
        "road_inches": 14,
        "special_movement": None,
        "armor_front": "L",
        "armor_side": "N",
        "armor_rear": "N",
        "weapons": [
            {"weapon": "75mmL40", "mount": "Hull", "ammo": 9},
            {"weapon": "37mmL53", "mount": "Turret", "ammo": 6},
            {"weapon": "MG", "mount": "Co-axial", "ammo": None},
            {"weapon": "MG", "mount": "Hull", "ammo": None},
            {"weapon": "MG", "mount": "Turret", "ammo": None}
        ]
    },
    {
        "name": "M3 Half-track",
        "year_range": "1942-1945",
        "off_road_inches": 12,
        "road_inches": 18,
        "special_movement": "Half-track",
        "armor_front": "N",
        "armor_side": "O",
        "armor_rear": "O",
        "weapons": [
            {"weapon": "MG", "mount": "Pintle", "ammo": None}
        ]
    },
    {
        "name": "M3A1 Half-track",
        "year_range": "1943-1945",
        "off_road_inches": 12,
        "road_inches": 18,
        "special_movement": "Half-track",
        "armor_front": "N",
        "armor_side": "O",
        "armor_rear": "O",
        "weapons": [
            {"weapon": "MG", "mount": "Pintle", "ammo": None}
        ]
    },
    {
        "name": "M16 AA Half-track",
        "year_range": "1943-1945",
        "off_road_inches": 12,
        "road_inches": 18,
        "special_movement": "Half-track",
        "armor_front": "N",
        "armor_side": "O",
        "armor_rear": "O",
        "weapons": [
            {"weapon": "4xHMG", "mount": "Hull", "ammo": None}
        ]
    },
    {
        "name": "M15 AA Half-track",
        "year_range": "1943-1945",
        "off_road_inches": 12,
        "road_inches": 18,
        "special_movement": "Half-track",
        "armor_front": "N",
        "armor_side": "O",
        "armor_rear": "O",
        "weapons": [
            {"weapon": "37mmL60", "mount": "Turret", "ammo": 6},
            {"weapon": "2xHMG", "mount": "Turret", "ammo": None}
        ]
    },
    {
        "name": "M21 Mortar Half-track",
        "year_range": "1944-1945",
        "off_road_inches": 12,
        "road_inches": 18,
        "special_movement": "Half-track",
        "armor_front": "N",
        "armor_side": "O",
        "armor_rear": "O",
        "weapons": [
            {"weapon": "81mm Mortar", "mount": "Hull", "ammo": 8}
        ]
    },
    {
        "name": "M2 Half-track",
        "year_range": "1942-1943",
        "off_road_inches": 12,
        "road_inches": 18,
        "special_movement": "Half-track",
        "armor_front": "N",
        "armor_side": "O",
        "armor_rear": "O",
        "weapons": [
            {"weapon": "MG", "mount": "Pintle", "ammo": None}
        ]
    },
    {
        "name": "M4 81mm Mortar Half-track",
        "year_range": "1942-1943",
        "off_road_inches": 12,
        "road_inches": 18,
        "special_movement": "Half-track",
        "armor_front": "N",
        "armor_side": "O",
        "armor_rear": "O",
        "weapons": [
            {"weapon": "81mm Mortar", "mount": "Hull", "ammo": 8}
        ]
    },
    {
        "name": "M24 Chaffee",
        "year_range": "1945",
        "off_road_inches": 12,
        "road_inches": 18,
        "special_movement": None,
        "armor_front": "M",
        "armor_side": "N",
        "armor_rear": "N",
        "weapons": [
            {"weapon": "75mmL40", "mount": "Turret", "ammo": 9},
            {"weapon": "MG", "mount": "Co-axial", "ammo": None},
            {"weapon": "MG", "mount": "Hull", "ammo": None}
        ]
    },
    {
        "name": "M8 Greyhound",
        "year_range": "1943-1945",
        "off_road_inches": 18,
        "road_inches": 26,
        "special_movement": None,
        "armor_front": "N",
        "armor_side": "O",
        "armor_rear": "O",
        "weapons": [
            {"weapon": "37mmL53", "mount": "Turret", "ammo": 6},
            {"weapon": "MG", "mount": "Co-axial", "ammo": None}
        ]
    },
    {
        "name": "M20 Armoured Car",
        "year_range": "1943-1945",
        "off_road_inches": 18,
        "road_inches": 26,
        "special_movement": None,
        "armor_front": "N",
        "armor_side": "O",
        "armor_rear": "O",
        "weapons": [
            {"weapon": "HMG", "mount": "Pintle", "ammo": None}
        ]
    },
    {
        "name": "Jeep",
        "year_range": "1942-1945",
        "off_road_inches": 18,
        "road_inches": 26,
        "special_movement": "Recce",
        "armor_front": None,
        "armor_side": None,
        "armor_rear": None,
        "weapons": [
            {"weapon": "MG", "mount": "Pintle", "ammo": None}
        ]
    },
    {
        "name": "Dodge 3/4-ton Truck",
        "year_range": "1942-1945",
        "off_road_inches": 18,
        "road_inches": 26,
        "special_movement": "Transport",
        "armor_front": None,
        "armor_side": None,
        "armor_rear": None,
        "weapons": []
    },
    {
        "name": "GMC 2.5-ton Truck",
        "year_range": "1942-1945",
        "off_road_inches": 15,
        "road_inches": 24,
        "special_movement": "Transport",
        "armor_front": None,
        "armor_side": None,
        "armor_rear": None,
        "weapons": []
    }
]

def main():
    print("US BattleGroup Vehicle Extraction")
    print(f"{'='*60}")
    print(f"Total vehicles: {len(VEHICLES)}")
    print(f"{'='*60}\n")

    # Save to JSON
    output_path = Path(r"D:\north-africa-toe-builder\data\output\battlegroup_us_vehicles.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(VEHICLES, f, indent=2, ensure_ascii=False)

    print(f"Saved to: {output_path}\n")

    # Print summary
    print("Vehicle Summary:")
    print(f"{'Name':<35} {'Year':<12} {'Armor':<10} {'Movement':<12} {'Weapons'}")
    print("-" * 100)

    for v in VEHICLES:
        weapons_str = ', '.join([w['weapon'] for w in v['weapons']])
        year_str = v['year_range'] or 'N/A'
        armor_str = f"{v['armor_front'] or '-'}/{v['armor_side'] or '-'}/{v['armor_rear'] or '-'}"
        move_str = f"{v['off_road_inches']}\"{v['road_inches']}\""

        print(f"{v['name']:<35} {year_str:<12} {armor_str:<10} {move_str:<12} {weapons_str[:40]}")

    # Print JSON sample
    print(f"\nExample vehicle (JSON):")
    print(json.dumps(VEHICLES[0], indent=2))

if __name__ == '__main__':
    main()
