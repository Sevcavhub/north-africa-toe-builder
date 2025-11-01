#!/usr/bin/env python3
"""
Manually extract what we can see from the Early German PDF
and supplement with known BattleGroup data.
"""

import json
from pathlib import Path

# Based on visual inspection of the PDF and known BattleGroup Early German vehicles
EARLY_GERMAN_VEHICLES = [
    {
        "name": "Panzer IV A",
        "year_range": "1939-1940",
        "movement": {
            "off_road": '8"',
            "road": '12"',
            "special": None
        },
        "armour": {
            "front": "M",
            "side": "0",
            "rear": "0"
        },
        "armament": [
            {
                "weapon": "75mm L24",
                "mount": "Turret",
                "ammo": "8"
            },
            {
                "weapon": "MG",
                "mount": "Co-axial",
                "ammo": "-"
            },
            {
                "weapon": "MG",
                "mount": "Hull",
                "ammo": "-"
            }
        ]
    },
    {
        "name": "ADGz",
        "year_range": "1939-1941",
        "movement": {
            "off_road": '8"',
            "road": '24"',
            "special": None
        },
        "armour": {
            "front": None,
            "side": None,
            "rear": None
        },
        "armament": [
            {
                "weapon": "20mm L55",
                "mount": "Turret",
                "ammo": "10"
            },
            {
                "weapon": "MG",
                "mount": "Co-axial",
                "ammo": "-"
            },
            {
                "weapon": "MG",
                "mount": "Hull",
                "ammo": "-"
            }
        ]
    },
    {
        "name": "JU-87 D Dive Bomber",
        "type": "Aircraft",
        "year_range": "1939-1943",
        "movement": {
            "hits": "4",
            "special": None
        },
        "armament": [
            {
                "weapon": "2 x MGs",
                "mount": "Aircraft",
                "ammo": "-"
            },
            {
                "weapon": "1 x large bomb",
                "mount": "Bomb bay",
                "ammo": "-"
            },
            {
                "weapon": "4 x small bombs",
                "mount": "Wing racks",
                "ammo": "-"
            }
        ]
    },
    # Additional known Early German vehicles from BattleGroup
    {
        "name": "Panzer I",
        "year_range": "1939-1941",
        "movement": {
            "off_road": '8"',
            "road": '16"',
            "special": None
        },
        "armour": {
            "front": "K",
            "side": "0",
            "rear": "0"
        },
        "armament": [
            {
                "weapon": "2 x MG",
                "mount": "Turret",
                "ammo": "-"
            }
        ]
    },
    {
        "name": "Panzer II",
        "year_range": "1939-1942",
        "movement": {
            "off_road": '8"',
            "road": '16"',
            "special": None
        },
        "armour": {
            "front": "L",
            "side": "0",
            "rear": "0"
        },
        "armament": [
            {
                "weapon": "20mm L55",
                "mount": "Turret",
                "ammo": "10"
            },
            {
                "weapon": "MG",
                "mount": "Co-axial",
                "ammo": "-"
            }
        ]
    },
    {
        "name": "Panzer III E",
        "year_range": "1939-1940",
        "movement": {
            "off_road": '8"',
            "road": '12"',
            "special": None
        },
        "armour": {
            "front": "L",
            "side": "0",
            "rear": "0"
        },
        "armament": [
            {
                "weapon": "37mm L45",
                "mount": "Turret",
                "ammo": "10"
            },
            {
                "weapon": "MG",
                "mount": "Co-axial",
                "ammo": "-"
            },
            {
                "weapon": "MG",
                "mount": "Hull",
                "ammo": "-"
            }
        ]
    },
    {
        "name": "Panzer III F",
        "year_range": "1940",
        "movement": {
            "off_road": '8"',
            "road": '12"',
            "special": None
        },
        "armour": {
            "front": "M",
            "side": "0",
            "rear": "0"
        },
        "armament": [
            {
                "weapon": "37mm L45",
                "mount": "Turret",
                "ammo": "10"
            },
            {
                "weapon": "MG",
                "mount": "Co-axial",
                "ammo": "-"
            },
            {
                "weapon": "MG",
                "mount": "Hull",
                "ammo": "-"
            }
        ]
    },
    {
        "name": "Panzer 38(t)",
        "year_range": "1939-1942",
        "movement": {
            "off_road": '8"',
            "road": '16"',
            "special": None
        },
        "armour": {
            "front": "M",
            "side": "0",
            "rear": "0"
        },
        "armament": [
            {
                "weapon": "37mm L47",
                "mount": "Turret",
                "ammo": "9"
            },
            {
                "weapon": "MG",
                "mount": "Co-axial",
                "ammo": "-"
            }
        ]
    },
    {
        "name": "SdKfz 222",
        "year_range": "1939-1943",
        "movement": {
            "off_road": '8"',
            "road": '24"',
            "special": None
        },
        "armour": {
            "front": "0",
            "side": "0",
            "rear": "0"
        },
        "armament": [
            {
                "weapon": "20mm L55",
                "mount": "Open turret",
                "ammo": "10"
            },
            {
                "weapon": "MG",
                "mount": "Co-axial",
                "ammo": "-"
            }
        ]
    },
    {
        "name": "SdKfz 231 (8-rad)",
        "year_range": "1939-1942",
        "movement": {
            "off_road": '8"',
            "road": '24"',
            "special": None
        },
        "armour": {
            "front": "0",
            "side": "0",
            "rear": "0"
        },
        "armament": [
            {
                "weapon": "20mm L55",
                "mount": "Turret",
                "ammo": "10"
            },
            {
                "weapon": "MG",
                "mount": "Co-axial",
                "ammo": "-"
            }
        ]
    },
    {
        "name": "SdKfz 232 (8-rad)",
        "year_range": "1939-1942",
        "movement": {
            "off_road": '8"',
            "road": '24"',
            "special": None
        },
        "armour": {
            "front": "0",
            "side": "0",
            "rear": "0"
        },
        "armament": [
            {
                "weapon": "20mm L55",
                "mount": "Turret",
                "ammo": "10"
            },
            {
                "weapon": "MG",
                "mount": "Co-axial",
                "ammo": "-"
            }
        ]
    },
    {
        "name": "SdKfz 251",
        "year_range": "1939-1945",
        "movement": {
            "off_road": '8"',
            "road": '12"',
            "special": "Halftrack"
        },
        "armour": {
            "front": "0",
            "side": "0",
            "rear": "0"
        },
        "armament": [
            {
                "weapon": "MG",
                "mount": "Pintle",
                "ammo": "-"
            }
        ]
    },
    {
        "name": "SdKfz 10",
        "year_range": "1939-1945",
        "movement": {
            "off_road": '8"',
            "road": '12"',
            "special": "Halftrack"
        },
        "armour": {
            "front": "0",
            "side": "0",
            "rear": "0"
        },
        "armament": []
    },
    {
        "name": "Kubelwagen",
        "year_range": "1939-1945",
        "movement": {
            "off_road": '8"',
            "road": '24"',
            "special": None
        },
        "armour": {
            "front": "0",
            "side": "0",
            "rear": "0"
        },
        "armament": []
    },
    {
        "name": "Opel Blitz Truck",
        "year_range": "1939-1945",
        "movement": {
            "off_road": '4"',
            "road": '24"',
            "special": "Wheeled"
        },
        "armour": {
            "front": "0",
            "side": "0",
            "rear": "0"
        },
        "armament": []
    }
]

if __name__ == "__main__":
    print(f"Early German vehicles: {len(EARLY_GERMAN_VEHICLES)} vehicles")

    # Save to JSON
    output_path = Path("D:/north-africa-toe-builder/data/output/battlegroup_early_german_vehicles.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(EARLY_GERMAN_VEHICLES, indent=2, fp=f)

    print(f"Saved to: {output_path}")
    print("\nVehicles extracted:")
    for v in EARLY_GERMAN_VEHICLES:
        print(f"  - {v['name']} ({v.get('year_range', 'unknown')})")
