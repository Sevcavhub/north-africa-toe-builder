#!/usr/bin/env python3
import sqlite3
import json

conn = sqlite3.connect('D:/north-africa-toe-builder/database/master_database.db')
cursor = conn.cursor()

# Find WITW ID collisions (same witw_id for multiple equipment)
cursor.execute("""
SELECT witw_id, COUNT(*) as count, GROUP_CONCAT(canonical_id || ' (' || category || ')') as items
FROM equipment
WHERE witw_id IS NOT NULL AND witw_id != 'NOT_IN_DATABASE'
GROUP BY witw_id
HAVING COUNT(*) > 1
ORDER BY count DESC
LIMIT 30
""")

results = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
print('=== WITW ID Collisions (same WITW ID mapped to multiple equipment) ===')
print(json.dumps(results, indent=2))

# Check aircraft incorrectly categorized as tanks
cursor.execute("""
SELECT canonical_id, name, witw_name, category, equipment_type
FROM equipment
WHERE (category = 'tanks' OR category = 'main_tanks')
  AND (witw_name LIKE '%Lysander%' OR witw_name LIKE '%Blenheim%' OR
       witw_name LIKE '%Hurricane%' OR witw_name LIKE '%Spitfire%' OR
       witw_name LIKE '%aircraft%' OR witw_name LIKE '%(FI)%' OR witw_name LIKE '%(LB)%')
ORDER BY canonical_id
""")

aircraft_as_tanks = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
if aircraft_as_tanks:
    print('\n=== Aircraft incorrectly marked as tanks ===')
    print(json.dumps(aircraft_as_tanks, indent=2))

conn.close()
