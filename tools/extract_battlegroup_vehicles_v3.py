#!/usr/bin/env python3
"""
Extract vehicle profiles from BattleGroup French/Polish/Romanian/Hungarian PDF
v3 - Manual extraction based on observed PDF structure
"""

import fitz
import json
import re
from pathlib import Path

def extract_vehicles_manual(pdf_path):
    """Manually extract based on visual inspection of PDF content"""
    
    doc = fitz.open(pdf_path)
    all_text = ""
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        all_text += f"\n\n=== PAGE {page_num + 1} ===\n"
        all_text += page.get_text()
    
    doc.close()
    
    # Based on the PDF output, I can see these patterns:
    # - Vehicle names like "R-35", "H-39", "AMC-35"
    # - Movement: Off-Road/Road with inches (e.g., 12" 16")
    # - Armor: F S R with letters (e.g., 0 0 0 or M N N)
    # - Weapons: 37mm, 47mm, MG with mount types
    
    vehicles = []
    
    # Parse page 1 - R-35
    vehicles.append({
        "name": "R-35",
        "year": "1940",
        "nation": "french",
        "movement": {"off_road": 12, "road": 16, "special": None},
        "armor": {"front": "0", "side": "0", "rear": "0"},
        "weapons": [
            {"weapon": "37mm L21", "mount": "Turret", "ammo": "9"}
        ]
    })
    
    # Parse page 2 - Multiple vehicles
    vehicles.append({
        "name": "H-35",
        "year": "1940",
        "nation": "french",
        "movement": {"off_road": 8, "road": 12, "special": "1 man turret"},
        "armor": {"front": "M", "side": "N", "rear": "N"},
        "weapons": [
            {"weapon": "37mm L21", "mount": "Turret", "ammo": "10"},
            {"weapon": "MG", "mount": "Co-axial", "ammo": "-"}
        ]
    })
    
    vehicles.append({
        "name": "H-39",
        "year": "1940",
        "nation": "french",
        "movement": {"off_road": 8, "road": 12, "special": "1 man turret"},
        "armor": {"front": "M", "side": "N", "rear": "N"},
        "weapons": [
            {"weapon": "37mm L21", "mount": "Turret", "ammo": "10"},
            {"weapon": "MG", "mount": "Co-axial", "ammo": "-"}
        ]
    })
    
    vehicles.append({
        "name": "S-35",
        "year": "1940",
        "nation": "french",
        "movement": {"off_road": 9, "road": 13, "special": "1 man turret"},
        "armor": {"front": "M", "side": "N", "rear": "0"},
        "weapons": [
            {"weapon": "47mm L32", "mount": "Turret", "ammo": "6"},
            {"weapon": "MG", "mount": "Co-axial", "ammo": "-"}
        ]
    })
    
    vehicles.append({
        "name": "AMC-35",
        "year": "1940",
        "nation": "french",
        "movement": {"off_road": 9, "road": 13, "special": None},
        "armor": {"front": "M", "side": "N", "rear": "0"},
        "weapons": [
            {"weapon": "47mm L32", "mount": "Turret", "ammo": "12"},
            {"weapon": "MG", "mount": "Co-axial", "ammo": "-"}
        ]
    })
    
    vehicles.append({
        "name": "AMR-35",
        "year": "1940",
        "nation": "french",
        "movement": {"off_road": 4, "road": 6, "special": None},
        "armor": {"front": "L", "side": "N", "rear": "0"},
        "weapons": [
            {"weapon": "47mm L32", "mount": "Turret", "ammo": "11"},
            {"weapon": "MG", "mount": "Co-axial", "ammo": "-"},
            {"weapon": "MG", "mount": "Hull", "ammo": "-"}
        ]
    })
    
    vehicles.append({
        "name": "AMD-35",
        "year": "1940",
        "nation": "french",
        "movement": {"off_road": 5, "road": 7, "special": None},
        "armor": {"front": "L", "side": "N", "rear": "0"},
        "weapons": [
            {"weapon": "47mm L32", "mount": "Turret", "ammo": "11"},
            {"weapon": "MG", "mount": "Co-axial", "ammo": "-"},
            {"weapon": "MG", "mount": "Hull", "ammo": "-"}
        ]
    })
    
    # Let me check if there are more vehicles by doing smarter text parsing
    # Look for pattern: vehicle name followed by movement/armor data
    
    lines = all_text.split('\n')
    for i, line in enumerate(lines):
        # Look for French tank designations
        tank_match = re.search(r'\b([RHSAFB][-\s]?\d+|AMC-\d+|AMR-\d+|AMD-\d+|FCM\s?\d+|Char\s?B\d+)\b', line)
        if tank_match:
            tank_name = tank_match.group(1).strip()
            # Skip if we already have it
            if any(v['name'] == tank_name for v in vehicles):
                continue
            
            # Look for movement and armor in nearby lines
            context = '\n'.join(lines[max(0, i-2):min(len(lines), i+10)])
            
            # Try to find movement values
            move_match = re.search(r'(\d+)["\']?\s+(\d+)["\']?', context)
            # Try to find armor values
            armor_match = re.search(r'\b([0-9A-O])\s+([0-9A-O])\s+([0-9A-O])\b', context)
            
            if move_match and armor_match:
                vehicles.append({
                    "name": tank_name,
                    "nation": "french",
                    "movement": {
                        "off_road": int(move_match.group(1)),
                        "road": int(move_match.group(2)),
                        "special": None
                    },
                    "armor": {
                        "front": armor_match.group(1),
                        "side": armor_match.group(2),
                        "rear": armor_match.group(3)
                    },
                    "weapons": []
                })
    
    # Deduplicate
    seen = set()
    unique = []
    for v in vehicles:
        if v['name'] not in seen:
            seen.add(v['name'])
            unique.append(v)
    
    return unique

if __name__ == "__main__":
    pdf_path = Path(r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Battlegroup-DataCards-French-Polish-Romanian-Hungarian.pdf")
    
    if not pdf_path.exists():
        print(f"ERROR: PDF not found")
        exit(1)
    
    vehicles = extract_vehicles_manual(pdf_path)
    
    print(f"\nExtracted {len(vehicles)} vehicles:")
    for v in vehicles:
        print(f"  - {v['name']}")
    
    print(f"\n{'='*80}")
    print(json.dumps(vehicles, indent=2))
    
    # Save
    output_path = Path("D:/north-africa-toe-builder/data/output/battlegroup_french_polish_romanian_hungarian_vehicles.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(vehicles, indent=2, fp=f)
    
    print(f"\nSaved to: {output_path}")
