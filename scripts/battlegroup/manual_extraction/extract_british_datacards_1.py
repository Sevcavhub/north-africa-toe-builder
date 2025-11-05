"""
Extract British DataCards from Britsh1.png

QRS card format:
- Top table: Vehicle stats (armor, movement, crew, points, BR, special rules)
- Bottom section (if applicable): Integrated gun stats for vehicle's main gun

Data goes to:
- bg_reference_vehicles (vehicle stats)
- bg_reference_guns (integrated gun stats)
"""

import sqlite3

def insert_vehicles_and_guns():
    """Insert British vehicles and their integrated guns from Britsh1.png"""

    conn = sqlite3.connect('D:/north-africa-toe-builder/data/master_database.db')
    cursor = conn.cursor()

    # Vehicle and gun data extracted from Britsh1.png
    # Format: (vehicle_data, gun_data_if_applicable)

    vehicles_with_guns = [
        # Row 1, Column 1: M3 Stuart
        {
            'vehicle': ('M3 Stuart', 'british', 'Light Tank', 'F3', 'S2', 'R1', 'TF3', 'TS2', 'TR1',
                       11, 3, 55, 4, 'Unreliable, Fast'),
            'gun': ('37mm M6', 'AT Gun', '20', '30', '40', '50', '60',
                   None, None, None, None, None,  # No HE values visible
                   4, 5, 5, 5, 5)  # AP values
        },

        # Row 1, Column 2: Valentine IX
        {
            'vehicle': ('Valentine IX', 'british', 'Medium Tank', 'F5', 'S3', 'R3', 'TF5', 'TS3', 'TR2',
                       7, 3, 110, 5, 'Reliable, Slow'),
            'gun': ('6pdr 57mm', 'AT Gun', '20', '30', '40', '50', '60',
                   None, None, None, None, None,  # No HE values visible
                   7, 8, 8, 7, 6)  # AP values
        },

        # Row 1, Column 3: Crusader II
        {
            'vehicle': ('Crusader II', 'british', 'Cruiser Tank', 'F4', 'S3', 'R2', 'TF4', 'TS3', 'TR2',
                       14, 5, 100, 5, 'Fast, Unreliable'),
            'gun': ('2pdr 40mm', 'AT Gun', '20', '30', '40', '50', '60',
                   None, None, None, None, None,
                   5, 6, 6, 5, 4)  # AP values
        },

        # Row 2, Column 1: Matilda II
        {
            'vehicle': ('Matilda II', 'british', 'Infantry Tank', 'F6', 'S4', 'R3', 'TF6', 'TS4', 'TR3',
                       4, 4, 145, 6, 'Slow, Reliable'),
            'gun': ('2pdr 40mm', 'AT Gun', '20', '30', '40', '50', '60',
                   None, None, None, None, None,
                   5, 6, 6, 5, 4)
        },

        # Row 2, Column 2: Matilda II CS
        {
            'vehicle': ('Matilda II CS', 'british', 'Infantry Tank', 'F6', 'S4', 'R3', 'TF6', 'TS4', 'TR3',
                       4, 4, 145, 6, 'Slow, Reliable, Smoke'),
            'gun': ('3in Howitzer', 'Howitzer', '20', '30', '40', '50', '60',
                   4, 3, 2, 1, 0,  # HE values
                   None, None, None, None, None)  # No AP for howitzer
        },

        # Row 2, Column 3: Matilda Frog (Flamethrower - no gun stats)
        {
            'vehicle': ('Matilda Frog', 'british', 'Flamethrower Tank', 'F6', 'S4', 'R3', 'TF6', 'TS4', 'TR3',
                       4, 4, 150, 6, 'Slow, Reliable, Flamethrower'),
            'gun': None  # Flamethrower, not a gun
        },

        # Row 3, Column 1: Crusader III
        {
            'vehicle': ('Crusader III', 'british', 'Cruiser Tank', 'F4', 'S3', 'R2', 'TF4', 'TS3', 'TR2',
                       14, 5, 115, 5, 'Fast, Unreliable'),
            'gun': ('6pdr 57mm', 'AT Gun', '20', '30', '40', '50', '60',
                   None, None, None, None, None,
                   7, 8, 8, 7, 6)
        },

        # Row 3, Column 2: Crusader III AA (AA gun - different format)
        {
            'vehicle': ('Crusader III AA', 'british', 'AA Tank', 'F4', 'S3', 'R2', 'TF2', 'TS2', 'TR2',
                       14, 3, 95, 5, 'Fast, Unreliable, AA'),
            'gun': ('Twin 20mm Oerlikon', 'AA Gun', '20', '30', '40', '50', '60',
                   2, 1, 0, 0, 0,  # HE values
                   3, 2, 1, 0, 0)  # AP values
        },

        # Row 3, Column 3: Valentine X
        {
            'vehicle': ('Valentine X', 'british', 'Medium Tank', 'F5', 'S3', 'R3', 'TF5', 'TS3', 'TR2',
                       7, 3, 115, 5, 'Reliable, Slow'),
            'gun': ('6pdr 57mm', 'AT Gun', '20', '30', '40', '50', '60',
                   None, None, None, None, None,
                   7, 8, 8, 7, 6)
        },

        # Row 4, Column 1: Churchill II
        {
            'vehicle': ('Churchill II', 'british', 'Infantry Tank', 'F7', 'S4', 'R3', 'TF6', 'TS4', 'TR4',
                       5, 5, 165, 7, 'Slow, Reliable'),
            'gun': ('2pdr 40mm', 'AT Gun', '20', '30', '40', '50', '60',
                   None, None, None, None, None,
                   5, 6, 6, 5, 4)
        },

        # Row 4, Column 2: Churchill III
        {
            'vehicle': ('Churchill III', 'british', 'Infantry Tank', 'F7', 'S4', 'R3', 'TF6', 'TS4', 'TR4',
                       5, 5, 180, 7, 'Slow, Reliable'),
            'gun': ('6pdr 57mm', 'AT Gun', '20', '30', '40', '50', '60',
                   None, None, None, None, None,
                   7, 8, 8, 7, 6)
        },

        # Row 4, Column 3: Churchill IV
        {
            'vehicle': ('Churchill IV', 'british', 'Infantry Tank', 'F7', 'S4', 'R3', 'TF6', 'TS4', 'TR4',
                       5, 5, 195, 8, 'Slow, Reliable'),
            'gun': ('75mm M3', 'Gun-Howitzer', '20', '30', '40', '50', '60',
                   5, 4, 3, 2, 1,  # HE values
                   6, 6, 5, 4, 3)  # AP values
        },

        # Row 5, Column 1: Churchill NA75
        {
            'vehicle': ('Churchill NA75', 'british', 'Infantry Tank', 'F7', 'S4', 'R3', 'TF6', 'TS4', 'TR4',
                       5, 5, 195, 8, 'Slow, Reliable'),
            'gun': ('75mm M3', 'Gun-Howitzer', '20', '30', '40', '50', '60',
                   5, 4, 3, 2, 1,
                   6, 6, 5, 4, 3)
        },

        # Row 5, Column 2: Churchill VI
        {
            'vehicle': ('Churchill VI', 'british', 'Infantry Tank', 'F7', 'S4', 'R3', 'TF7', 'TS4', 'TR4',
                       5, 5, 205, 8, 'Slow, Reliable'),
            'gun': ('75mm M3', 'Gun-Howitzer', '20', '30', '40', '50', '60',
                   5, 4, 3, 2, 1,
                   6, 6, 5, 4, 3)
        },

        # Row 5, Column 3: Churchill VII
        {
            'vehicle': ('Churchill VII', 'british', 'Infantry Tank', 'F9', 'S5', 'R4', 'TF7', 'TS5', 'TR4',
                       5, 5, 225, 9, 'Slow, Reliable'),
            'gun': ('75mm M3', 'Gun-Howitzer', '20', '30', '40', '50', '60',
                   5, 4, 3, 2, 1,
                   6, 6, 5, 4, 3)
        },
    ]

    vehicles_inserted = 0
    guns_inserted = 0
    vehicles_skipped = 0
    guns_skipped = 0

    for entry in vehicles_with_guns:
        vehicle_data = entry['vehicle']
        gun_data = entry['gun']

        # Insert vehicle
        try:
            cursor.execute('''
                INSERT INTO bg_reference_vehicles
                (name, nation, vehicle_type, armor_front, armor_side, armor_rear,
                 armor_turret_front, armor_turret_side, armor_turret_rear,
                 movement, crew, points, battle_rating, special_rules)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', vehicle_data)
            vehicles_inserted += 1
            print(f"✓ Inserted vehicle: {vehicle_data[0]}")
        except sqlite3.IntegrityError:
            vehicles_skipped += 1
            print(f"⊗ Skipped duplicate vehicle: {vehicle_data[0]}")

        # Insert gun if present
        if gun_data:
            try:
                cursor.execute('''
                    INSERT INTO bg_reference_guns
                    (name, gun_type, range_0_20, range_20_30, range_30_40, range_40_50, range_50_60,
                     he_0_20, he_20_30, he_30_40, he_40_50, he_50_60,
                     ap_0_20, ap_20_30, ap_30_40, ap_40_50, ap_50_60)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', gun_data)
                guns_inserted += 1
                print(f"  ✓ Inserted gun: {gun_data[0]}")
            except sqlite3.IntegrityError:
                guns_skipped += 1
                print(f"  ⊗ Skipped duplicate gun: {gun_data[0]}")

    conn.commit()
    conn.close()

    print(f"\n{'='*60}")
    print(f"Britsh1.png Extraction Complete")
    print(f"{'='*60}")
    print(f"Vehicles inserted: {vehicles_inserted}")
    print(f"Vehicles skipped (duplicates): {vehicles_skipped}")
    print(f"Guns inserted: {guns_inserted}")
    print(f"Guns skipped (duplicates): {guns_skipped}")
    print(f"Total vehicles processed: {len(vehicles_with_guns)}")

if __name__ == '__main__':
    insert_vehicles_and_guns()
