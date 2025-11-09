#!/usr/bin/env python3
"""Import BG Builder force lists (117 entries) to database."""
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "database" / "master_database.db"
JSON_PATH = Path(__file__).parent.parent.parent.parent / "sources" / "bg_builder_forces.json"

def import_forces():
    print("BG Builder Forces Import")
    print("=" * 80)

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        forces = json.load(f)

    conn = sqlite3.connect(DB_PATH, timeout=60)
    cursor = conn.cursor()

    imported = 0

    for force in forces:
        cursor.execute("""
            INSERT INTO bg_builder_forces
            (force_id, force_group, force_name, infantry_tiers, sections)
            VALUES (?, ?, ?, ?, ?)
        """, (
            force.get('id'),
            force.get('group'),
            force.get('name'),
            json.dumps(force.get('infantry', [])),
            json.dumps(force.get('sections', []))
        ))
        imported += 1

    conn.commit()

    print(f"\nImported: {imported} force lists")

    # Show sample
    cursor.execute("""
        SELECT force_id, force_group, force_name
        FROM bg_builder_forces
        WHERE force_group LIKE '%Tobruk%'
        LIMIT 3
    """)
    print("\nSample North Africa forces:")
    for row in cursor.fetchall():
        print(f"   [{row[0]}] {row[1]} - {row[2]}")

    cursor.execute("SELECT COUNT(*) FROM bg_builder_forces")
    print(f"\nTotal force lists in database: {cursor.fetchone()[0]}")

    conn.close()

if __name__ == '__main__':
    import_forces()
