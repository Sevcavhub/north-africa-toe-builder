#!/usr/bin/env python3
"""
Extract vehicle costs and BR from bg_builder_forces.sections JSON.

This script parses the sections JSON field to extract individual vehicle costs and BR,
then updates the bg_builder_vehicle_costs table with complete data.

The sections JSON contains unit entries with:
- base_cost: Entry-level cost
- br: Battle rating
- options.choices: Individual vehicles with cost modifiers
  - v: Vehicle ID
  - cost: Cost modifier (added to base_cost)
  - br: Sometimes overrides entry BR

Formula: final_cost = entry.cost + choice.cost (if choice.cost exists)
         final_br = choice.br (if exists) OR entry.br
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime

# Database path
DB_PATH = Path(__file__).parent / 'database' / 'web_database.db'


def extract_vehicle_costs_from_sections():
    """
    Extract vehicle costs and BR from sections JSON and populate bg_builder_vehicle_costs.

    Returns:
        tuple: (total_extracted, total_forces_processed)
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all forces with sections data
    cursor.execute("""
        SELECT force_id, force_group, force_name, sections
        FROM bg_builder_forces
    """)

    forces = cursor.fetchall()

    extracted_records = []
    total_vehicles = set()

    print(f"Processing {len(forces)} forces...")

    for force in forces:
        force_id = force['force_id']
        force_group = force['force_group']
        force_name = force['force_name']

        try:
            sections = json.loads(force['sections'])
        except:
            print(f"  ⚠️  Failed to parse JSON for {force_name}")
            continue

        # Process each section
        for section in sections:
            if 'entries' not in section:
                continue

            # Process each entry (unit type)
            for entry in section['entries']:
                entry_name = entry.get('name', 'Unknown')
                entry_cost = entry.get('cost', 0)
                entry_br = entry.get('br', 0)

                # Look for vehicle in options/choices
                if 'options' in entry:
                    for option in entry['options']:
                        if 'choices' in option:
                            for choice in option['choices']:
                                # Extract vehicle ID(s)
                                v_val = choice.get('v')
                                if not v_val:
                                    continue

                                # Handle both single IDs and arrays
                                vehicle_ids = []
                                if isinstance(v_val, int):
                                    vehicle_ids = [v_val]
                                elif isinstance(v_val, str):
                                    try:
                                        if '[' in v_val:
                                            # Parse array notation like "[119,118]"
                                            ids = json.loads(v_val)
                                            vehicle_ids = ids if isinstance(ids, list) else [ids]
                                        else:
                                            vehicle_ids = [int(v_val)]
                                    except:
                                        continue

                                # Calculate cost and BR for each vehicle
                                choice_cost_modifier = choice.get('cost', 0) or 0
                                choice_br_override = choice.get('br')

                                # Cost = entry base cost + choice modifier
                                final_cost = entry_cost + choice_cost_modifier

                                # BR = choice override OR entry BR
                                final_br = choice_br_override if choice_br_override is not None else entry_br

                                # Get restricted/unique flags
                                restricted = choice.get('restricted', False) or entry.get('restricted', False)
                                unique_flag = choice.get('unique', False) or entry.get('unique', False)

                                # Add record for each vehicle ID
                                for vid in vehicle_ids:
                                    extracted_records.append({
                                        'vehicle_id': vid,
                                        'force_name': force_name,
                                        'cost_regular': final_cost,
                                        'br_regular': final_br,
                                        'restricted': restricted,
                                        'unique_flag': unique_flag,
                                        'entry_name': entry_name,
                                        'choice_text': choice.get('text', ''),
                                    })
                                    total_vehicles.add(vid)

                # Also check for direct vehicle ID on entry (single vehicle units)
                if 'v' in entry:
                    v_val = entry['v']
                    vehicle_ids = []

                    if isinstance(v_val, int):
                        vehicle_ids = [v_val]
                    elif isinstance(v_val, str):
                        try:
                            if '[' in v_val:
                                ids = json.loads(v_val)
                                vehicle_ids = ids if isinstance(ids, list) else [ids]
                            else:
                                vehicle_ids = [int(v_val)]
                        except:
                            continue

                    for vid in vehicle_ids:
                        extracted_records.append({
                            'vehicle_id': vid,
                            'force_name': force_name,
                            'cost_regular': entry_cost,
                            'br_regular': entry_br,
                            'restricted': entry.get('restricted', False),
                            'unique_flag': entry.get('unique', False),
                            'entry_name': entry_name,
                            'choice_text': entry_name,
                        })
                        total_vehicles.add(vid)

    print(f"\n[OK] Extracted {len(extracted_records)} cost/BR records for {len(total_vehicles)} unique vehicles")

    return extracted_records, len(forces)


def update_vehicle_costs_table(extracted_records):
    """
    Update bg_builder_vehicle_costs table with extracted data.
    Clears existing data and inserts new records.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n[*] Updating bg_builder_vehicle_costs table...")

    # Check current row count
    cursor.execute("SELECT COUNT(*) FROM bg_builder_vehicle_costs")
    old_count = cursor.fetchone()[0]
    print(f"  Current records: {old_count}")

    # Clear existing data
    cursor.execute("DELETE FROM bg_builder_vehicle_costs")
    print(f"  [OK] Cleared {old_count} old records")

    # Get vehicle names for the records
    print("  [*] Enriching records with vehicle names...")

    enriched_records = []
    for record in extracted_records:
        cursor.execute("""
            SELECT name FROM bg_builder_vehicles WHERE id = ?
        """, (record['vehicle_id'],))

        row = cursor.fetchone()
        if row:
            record['vehicle_name'] = row[0]
            enriched_records.append(record)

    print(f"  [OK] Enriched {len(enriched_records)} records with vehicle names")

    # Insert new records
    import_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.executemany("""
        INSERT INTO bg_builder_vehicle_costs (
            vehicle_id,
            vehicle_name,
            force_name,
            cost_regular,
            br_regular,
            restricted,
            unique_flag,
            import_date,
            import_source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (
            r['vehicle_id'],
            r['vehicle_name'],
            r['force_name'],
            r['cost_regular'],
            r['br_regular'],
            r['restricted'],
            r['unique_flag'],
            import_date,
            'sections_json_extraction'
        )
        for r in enriched_records
    ])

    conn.commit()

    # Get new row count
    cursor.execute("SELECT COUNT(*) FROM bg_builder_vehicle_costs")
    new_count = cursor.fetchone()[0]

    print(f"  [OK] Inserted {new_count} new records")
    print(f"  [*] Growth: {old_count} -> {new_count} (+{new_count - old_count})")

    # Show sample data
    print("\n[*] Sample extracted data:")
    cursor.execute("""
        SELECT vehicle_name, force_name, cost_regular, br_regular
        FROM bg_builder_vehicle_costs
        WHERE vehicle_name LIKE '%A9%' OR vehicle_name LIKE '%Panzer III%'
        ORDER BY vehicle_name
        LIMIT 10
    """)

    for row in cursor.fetchall():
        print(f"  {row[0]:<30} | {row[1]:<35} | {row[2]:>3} pts | {row[3]} BR")

    conn.close()


def verify_extraction():
    """Verify the extraction was successful."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n[*] Verification:")

    # Count unique vehicles
    cursor.execute("SELECT COUNT(DISTINCT vehicle_id) FROM bg_builder_vehicle_costs")
    unique_vehicles = cursor.fetchone()[0]
    print(f"  Unique vehicles with cost/BR data: {unique_vehicles}")

    # Count unique forces
    cursor.execute("SELECT COUNT(DISTINCT force_name) FROM bg_builder_vehicle_costs")
    unique_forces = cursor.fetchone()[0]
    print(f"  Unique forces: {unique_forces}")

    # Check A9 Cruiser
    cursor.execute("""
        SELECT force_name, cost_regular, br_regular
        FROM bg_builder_vehicle_costs
        WHERE vehicle_name = 'A9 Cruiser Mk.I'
        LIMIT 5
    """)

    a9_records = cursor.fetchall()
    if a9_records:
        print(f"\n  [OK] A9 Cruiser Mk.I found in {len(a9_records)} forces:")
        for row in a9_records[:3]:
            print(f"    - {row[0]}: {row[1]} pts, {row[2]} BR")
    else:
        print("  [WARN] A9 Cruiser Mk.I not found")

    # Check Panzer III
    cursor.execute("""
        SELECT DISTINCT vehicle_name, COUNT(*) as force_count
        FROM bg_builder_vehicle_costs
        WHERE vehicle_name LIKE '%Panzer III%'
        GROUP BY vehicle_name
        ORDER BY vehicle_name
    """)

    panzer_records = cursor.fetchall()
    if panzer_records:
        print(f"\n  [OK] Panzer III variants found:")
        for row in panzer_records[:5]:
            print(f"    - {row[0]}: available in {row[1]} forces")
    else:
        print("  [WARN] No Panzer III variants found")

    conn.close()


if __name__ == '__main__':
    print("=" * 70)
    print("Extract Vehicle Costs/BR from sections JSON")
    print("=" * 70)

    # Extract data
    extracted_records, forces_count = extract_vehicle_costs_from_sections()

    # Update table
    update_vehicle_costs_table(extracted_records)

    # Verify
    verify_extraction()

    print("\n" + "=" * 70)
    print("[OK] Extraction complete!")
    print("=" * 70)
