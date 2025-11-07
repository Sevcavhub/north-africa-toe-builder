import sqlite3

conn = sqlite3.connect('D:/north-africa-toe-builder/database/master_database.db')
cursor = conn.cursor()

print("="*120)
print("GUN DATA QA REPORT")
print("="*120)

# Get all Canadian and German guns with detailed data
cursor.execute("""
    SELECT id, name, nation, caliber_mm, he_dice, he_target,
           ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70,
           he_0_10, he_10_20, he_20_30, he_30_40, he_40_50, he_50_70,
           he_shell_classification, rof,
           source_document, extraction_method
    FROM bg_reference_guns 
    WHERE nation IN ('canadian', 'german')
    ORDER BY nation, id
""")

issues = []
current_nation = None

for row in cursor.fetchall():
    (gun_id, name, nation, caliber, he_dice, he_target,
     ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70,
     he_0_10, he_10_20, he_20_30, he_30_40, he_40_50, he_50_70,
     he_class, rof, source_doc, method) = row
    
    if nation != current_nation:
        current_nation = nation
        print(f"\n{'='*120}")
        print(f"{nation.upper()} GUNS - DETAILED CHECK")
        print(f"{'='*120}")
    
    print(f"\nID {gun_id}: {name}")
    print(f"  Caliber: {caliber}mm" if caliber else "  Caliber: MISSING")
    
    # HE Data
    if he_dice:
        print(f"  HE: {he_dice}D6/{he_target}")
    else:
        print(f"  HE: None (AP-only or autocannon)")
    
    # AP Data
    ap_values = [ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70]
    if any(ap_values):
        ap_str = "/".join([str(v) if v else "-" for v in ap_values])
        print(f"  AP: {ap_str}")
    else:
        print(f"  AP: None (mortar/artillery)")
    
    # HE Range Bands - THE CRITICAL CHECK
    he_ranges = [he_0_10, he_10_20, he_20_30, he_30_40, he_40_50, he_50_70]
    if any(he_ranges):
        he_str = "/".join([str(v) if v else "-" for v in he_ranges])
        print(f"  HE Ranges: {he_str}")
    else:
        if he_dice:  # Has HE but no range bands
            print(f"  HE Ranges: MISSING (has HE but no range data)")
            issues.append(f"ID {gun_id} ({name}): Missing HE range bands")
        else:
            print(f"  HE Ranges: N/A (no HE)")
    
    # Classification
    if he_class:
        print(f"  Classification: {he_class}")
    else:
        if he_dice or caliber and caliber >= 37:  # Should have classification
            print(f"  Classification: MISSING")
            issues.append(f"ID {gun_id} ({name}): Missing HE shell classification")
    
    # ROF
    if rof:
        print(f"  ROF: {rof}")
    else:
        print(f"  ROF: MISSING")
        issues.append(f"ID {gun_id} ({name}): Missing ROF")
    
    # Source
    print(f"  Source: {source_doc or 'None'} ({method or 'None'})")

# Summary
print(f"\n{'='*120}")
print("QA ISSUES SUMMARY")
print(f"{'='*120}")

if issues:
    print(f"\nFound {len(issues)} issues:\n")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("\nNo issues found - all data complete!")

# Statistics
cursor.execute("""
    SELECT nation,
           COUNT(*) as total,
           COUNT(he_0_10) as he_ranges,
           COUNT(he_shell_classification) as he_class,
           COUNT(rof) as rof_count
    FROM bg_reference_guns
    WHERE nation IN ('canadian', 'german')
    GROUP BY nation
""")

print(f"\n{'='*120}")
print("DATA COMPLETENESS STATISTICS")
print(f"{'='*120}")

for row in cursor.fetchall():
    nation, total, he_ranges, he_class, rof_count = row
    print(f"\n{nation.upper()}:")
    print(f"  Total guns: {total}")
    print(f"  HE range bands populated: {he_ranges}/{total} ({he_ranges/total*100:.0f}%)")
    print(f"  HE classification populated: {he_class}/{total} ({he_class/total*100:.0f}%)")
    print(f"  ROF populated: {rof_count}/{total} ({rof_count/total*100:.0f}%)")

conn.close()
