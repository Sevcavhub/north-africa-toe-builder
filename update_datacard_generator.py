#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update generate_book_datacards.py to use new schema (weapon_1-4, mount_1-4, ammo)
"""

import sys
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

datacard_script = Path(r"D:\north-africa-toe-builder\scripts\battlegroup\book\generate_book_datacards.py")

print("=" * 100)
print("UPDATING DATACARD GENERATOR FOR NEW SCHEMA")
print("=" * 100)

# Read the current script
with open(datacard_script, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"\n📖 Read {len(content)} characters from {datacard_script.name}")

# Backup
backup_path = datacard_script.parent / f"{datacard_script.stem}_backup_{Path(__file__).stem}.py"
with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"💾 Backup created: {backup_path.name}")

# Find and replace the weapons query section (lines ~390-414)
old_weapons_query = '''        # Source 2: bg_reference_vehicles (via reference_vehicle_id - for weapons only)
        if not main_gun and row['reference_vehicle_id']:
            cursor.execute("""
                SELECT weapons, name
                FROM bg_reference_vehicles
                WHERE id = ?
            """, (row['reference_vehicle_id'],))
            ref_row = cursor.fetchone()
            if ref_row:
                # Get weapons
                if ref_row['weapons']:
                    try:
                        weapons = json.loads(ref_row['weapons'])
                        # Find main gun (usually turret-mounted, not MG)
                        for weapon in weapons:
                            mount = weapon.get('mount', '').lower()
                            weapon_name = weapon.get('weapon', '')
                            ammo = weapon.get('ammo', None)
                            # Look for turret-mounted weapon that's not just "MG"
                            if 'turret' in mount and weapon_name.upper() != 'MG':
                                main_gun = weapon_name
                                main_gun_ammo = ammo
                                weapon_data = weapon
                                break
                    except (json.JSONDecodeError, TypeError):
                        pass'''

new_weapons_query = '''        # Source 2: bg_reference_vehicles (via reference_vehicle_id - for weapons only)
        if not main_gun and row['reference_vehicle_id']:
            cursor.execute("""
                SELECT weapon_1, weapon_2, weapon_3, weapon_4,
                       mount_1, mount_2, mount_3, mount_4,
                       ammo, name
                FROM bg_reference_vehicles
                WHERE id = ?
            """, (row['reference_vehicle_id'],))
            ref_row = cursor.fetchone()
            if ref_row:
                # Build weapons list from weapon_1-4 fields
                weapons_list = []
                for i in range(1, 5):
                    weapon = ref_row[f'weapon_{i}']
                    mount = ref_row[f'mount_{i}']
                    if weapon:
                        weapons_list.append({
                            'weapon': weapon,
                            'mount': mount or 'Unknown',
                            'ammo': ref_row['ammo']  # Single ammo value for now
                        })

                # Find main gun (usually turret-mounted, not MG)
                for weapon_data in weapons_list:
                    mount = weapon_data.get('mount', '').lower()
                    weapon_name = weapon_data.get('weapon', '')
                    ammo = weapon_data.get('ammo', None)
                    # Look for turret-mounted weapon that's not just "MG"
                    if 'turret' in mount and weapon_name.upper() != 'MG':
                        main_gun = weapon_name
                        main_gun_ammo = ammo
                        break'''

# Replace
if old_weapons_query in content:
    content = content.replace(old_weapons_query, new_weapons_query)
    print(f"✅ Updated main gun extraction (lines ~390-414)")
else:
    print(f"⚠️  Could not find exact match for main gun extraction")

# Find and replace the secondary weapons query (lines ~463-488)
old_secondary_query = '''        # If no secondary weapons, try bg_reference_vehicles via reference_vehicle_id (FIXED!)
        if not secondary and row['reference_vehicle_id']:
            cursor.execute("""
                SELECT weapons
                FROM bg_reference_vehicles
                WHERE id = ?
            """, (row['reference_vehicle_id'],))
            ref_row = cursor.fetchone()
            if ref_row and ref_row['weapons']:
                try:
                    weapons = json.loads(ref_row['weapons'])
                    # Get secondary weapons (MGs, etc.)
                    secondary = []
                    for weapon in weapons:
                        mount = weapon.get('mount', 'Unknown')
                        weapon_name = weapon.get('weapon', 'Unknown')
                        weapon_ammo = weapon.get('ammo', None)
                        # Get all weapons except the main gun we already extracted
                        # Include co-axial/bow MGs and other secondary armament
                        if weapon_name != main_gun and weapon_name.upper() != 'NONE':
                            secondary.append({
                                'name': weapon_name,
                                'mount': mount,
                                'ammo': weapon_ammo
                            })
                except (json.JSONDecodeError, TypeError):
                    pass'''

new_secondary_query = '''        # If no secondary weapons, try bg_reference_vehicles via reference_vehicle_id (FIXED!)
        if not secondary and row['reference_vehicle_id']:
            cursor.execute("""
                SELECT weapon_1, weapon_2, weapon_3, weapon_4,
                       mount_1, mount_2, mount_3, mount_4,
                       ammo
                FROM bg_reference_vehicles
                WHERE id = ?
            """, (row['reference_vehicle_id'],))
            ref_row = cursor.fetchone()
            if ref_row:
                # Build weapons list from weapon_1-4 fields
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
                            })'''

# Replace
if old_secondary_query in content:
    content = content.replace(old_secondary_query, new_secondary_query)
    print(f"✅ Updated secondary weapons extraction (lines ~463-488)")
else:
    print(f"⚠️  Could not find exact match for secondary weapons extraction")

# Write updated content
with open(datacard_script, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n📝 Updated {datacard_script.name}")
print(f"\n✅ Script updated to use new schema:")
print(f"   - weapon_1, weapon_2, weapon_3, weapon_4 (instead of JSON weapons)")
print(f"   - mount_1, mount_2, mount_3, mount_4")
print(f"   - ammo (single value)")

print("\n" + "=" * 100)
print("NEXT STEPS")
print("=" * 100)
print("""
The datacard generator has been updated to use the new schema.

Test it with:
    cd D:\\north-africa-toe-builder
    python scripts/battlegroup/book/generate_book_datacards.py --battle battleaxe

If you need to revert:
    The backup is saved at: {backup_path.name}
""")

print("=" * 100)
