#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update generate_book_datacards.py to use ammo_1, ammo_2, ammo_3, ammo_4 fields"""

import sys
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

datacard_script = Path(r"D:\north-africa-toe-builder\scripts\battlegroup\book\generate_book_datacards.py")

print("=" * 100)
print("UPDATING DATACARD GENERATOR FOR AMMO_1-4 FIELDS")
print("=" * 100)

# Read the current script
with open(datacard_script, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"\n📖 Read {len(content)} characters from {datacard_script.name}")

# Backup
backup_path = datacard_script.parent / f"{datacard_script.stem}_backup_ammo_fields.py"
with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"💾 Backup created: {backup_path.name}")

# Update 1: Main gun extraction query (add ammo_1-4 to SELECT)
old_query_1 = """            cursor.execute(\"\"\"
                SELECT weapon_1, weapon_2, weapon_3, weapon_4,
                       mount_1, mount_2, mount_3, mount_4,
                       ammo, name
                FROM bg_reference_vehicles
                WHERE id = ?
            \"\"\", (row['reference_vehicle_id'],))"""

new_query_1 = """            cursor.execute(\"\"\"
                SELECT weapon_1, weapon_2, weapon_3, weapon_4,
                       mount_1, mount_2, mount_3, mount_4,
                       ammo_1, ammo_2, ammo_3, ammo_4, name
                FROM bg_reference_vehicles
                WHERE id = ?
            \"\"\", (row['reference_vehicle_id'],))"""

if old_query_1 in content:
    content = content.replace(old_query_1, new_query_1)
    print(f"✅ Updated main gun query (SELECT clause)")
else:
    print(f"⚠️  Could not find main gun query SELECT clause")

# Update 2: Build weapons list with individual ammo values
old_build_weapons = """                # Build weapons list from weapon_1-4 fields
                weapons_list = []
                for i in range(1, 5):
                    weapon = ref_row[f'weapon_{i}']
                    mount = ref_row[f'mount_{i}']
                    if weapon:
                        weapons_list.append({
                            'weapon': weapon,
                            'mount': mount or 'Unknown',
                            'ammo': ref_row['ammo']  # Single ammo value for now
                        })"""

new_build_weapons = """                # Build weapons list from weapon_1-4 fields
                weapons_list = []
                for i in range(1, 5):
                    weapon = ref_row[f'weapon_{i}']
                    mount = ref_row[f'mount_{i}']
                    ammo = ref_row[f'ammo_{i}']
                    if weapon:
                        weapons_list.append({
                            'weapon': weapon,
                            'mount': mount or 'Unknown',
                            'ammo': ammo
                        })"""

if old_build_weapons in content:
    content = content.replace(old_build_weapons, new_build_weapons)
    print(f"✅ Updated main gun weapons list builder")
else:
    print(f"⚠️  Could not find main gun weapons list builder")

# Update 3: Secondary weapons query
old_secondary_query = """            cursor.execute(\"\"\"
                SELECT weapon_1, weapon_2, weapon_3, weapon_4,
                       mount_1, mount_2, mount_3, mount_4,
                       ammo
                FROM bg_reference_vehicles
                WHERE id = ?
            \"\"\", (row['reference_vehicle_id'],))"""

new_secondary_query = """            cursor.execute(\"\"\"
                SELECT weapon_1, weapon_2, weapon_3, weapon_4,
                       mount_1, mount_2, mount_3, mount_4,
                       ammo_1, ammo_2, ammo_3, ammo_4
                FROM bg_reference_vehicles
                WHERE id = ?
            \"\"\", (row['reference_vehicle_id'],))"""

if old_secondary_query in content:
    content = content.replace(old_secondary_query, new_secondary_query)
    print(f"✅ Updated secondary weapons query (SELECT clause)")
else:
    print(f"⚠️  Could not find secondary weapons query SELECT clause")

# Update 4: Secondary weapons list builder
old_secondary_build = """                # Build weapons list from weapon_1-4 fields
                secondary = []
                for i in range(1, 5):
                    weapon_name = ref_row[f'weapon_{i}']
                    mount = ref_row[f'mount_{i}']
                    if weapon_name:
                        # Get all weapons except the main gun we already extracted
                        # Include co-axial/bow MGs and other secondary armament
                        if weapon_name != main_gun and weapon_name.upper() != 'NONE':
                            secondary.append({
                                'name': weapon_name,
                                'mount_type': mount or 'Unknown',
                                'ammunition_count': ref_row['ammo']  # Single ammo value for now
                            })"""

new_secondary_build = """                # Build weapons list from weapon_1-4 fields
                secondary = []
                for i in range(1, 5):
                    weapon_name = ref_row[f'weapon_{i}']
                    mount = ref_row[f'mount_{i}']
                    ammo = ref_row[f'ammo_{i}']
                    if weapon_name:
                        # Get all weapons except the main gun we already extracted
                        # Include co-axial/bow MGs and other secondary armament
                        if weapon_name != main_gun and weapon_name.upper() != 'NONE':
                            secondary.append({
                                'name': weapon_name,
                                'mount_type': mount or 'Unknown',
                                'ammunition_count': ammo
                            })"""

if old_secondary_build in content:
    content = content.replace(old_secondary_build, new_secondary_build)
    print(f"✅ Updated secondary weapons list builder")
else:
    print(f"⚠️  Could not find secondary weapons list builder")

# Write updated content
with open(datacard_script, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n📝 Updated {datacard_script.name}")
print(f"\n✅ Script updated to use ammo_1, ammo_2, ammo_3, ammo_4 fields")
print(f"   - Main gun query: SELECT includes ammo_1-4")
print(f"   - Main gun builder: Uses ammo_{i} for each weapon")
print(f"   - Secondary weapons query: SELECT includes ammo_1-4")
print(f"   - Secondary weapons builder: Uses ammo_{i} for each weapon")

print("\n" + "=" * 100)
print("READY TO GENERATE DATACARDS")
print("=" * 100)
print("""
The datacard generator now properly handles:
- Multiple weapons with individual ammo counts
- Churchill Crocodile (ammo_3 for flamethrower)
- Any future vehicles with ammo for secondary weapons

Test with:
    cd D:\\north-africa-toe-builder
    python scripts/battlegroup/book/generate_book_datacards.py --battle battleaxe
""")
print("=" * 100)
