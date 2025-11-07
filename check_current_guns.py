import sqlite3

conn = sqlite3.connect('D:/north-africa-toe-builder/database/master_database.db')
cursor = conn.cursor()

print("="*120)
print("CURRENT DATABASE STATE - ALL GUNS")
print("="*120)

# Get all guns
cursor.execute("""
    SELECT id, name, nation, caliber_mm, he_dice, he_target, 
           ap_0_10, source_document, extraction_method
    FROM bg_reference_guns 
    ORDER BY nation, id
""")

current_nation = None
for row in cursor.fetchall():
    gun_id, name, nation, caliber, he_dice, he_target, ap_0_10, source_doc, method = row
    
    if nation != current_nation:
        current_nation = nation
        print(f"\n{'='*120}")
        print(f"{(nation or 'unknown').upper()} GUNS")
        print(f"{'='*120}")
    
    has_he = "✓" if he_dice else "✗"
    has_ap = "✓" if ap_0_10 else "✗"
    cal_str = f"{caliber}" if caliber else "N/A"
    print(f"ID {gun_id:3d}: {name:35s} | {cal_str:>4s}mm | HE:{has_he} AP:{has_ap} | {source_doc or 'None':30s} | {method or 'None'}")

# Summary
cursor.execute("SELECT nation, COUNT(*) FROM bg_reference_guns GROUP BY nation ORDER BY nation")
print(f"\n{'='*120}")
print("SUMMARY")
print(f"{'='*120}")
for row in cursor.fetchall():
    print(f"{(row[0] or 'unknown'):15s}: {row[1]:3d} guns")

conn.close()
