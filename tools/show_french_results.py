#!/usr/bin/env python3
"""
Display French equipment matching results from database
"""
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_FILE = PROJECT_ROOT / "database" / "master_database.db"

def print_section(title):
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}\n")

def main():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print_section("FRENCH EQUIPMENT - DATABASE RESULTS")

    # 1. Equipment table - French items
    print_section("1. FRENCH EQUIPMENT IN EQUIPMENT TABLE")
    cursor.execute("""
        SELECT
            canonical_id,
            name,
            equipment_type,
            category,
            witw_id,
            witw_name
        FROM equipment
        WHERE nation = 'french'
        ORDER BY name
    """)

    french_equipment = cursor.fetchall()

    if french_equipment:
        print(f"Total French equipment in database: {len(french_equipment)}\n")
        for idx, row in enumerate(french_equipment, 1):
            print(f"{idx}. {row['name']}")
            print(f"   ID: {row['canonical_id']}")
            print(f"   Type: {row['equipment_type'] or 'N/A'}")
            print(f"   Category: {row['category'] or 'N/A'}")
            print(f"   WITW ID: {row['witw_id'] or 'N/A'}")
            print(f"   WITW Name: {row['witw_name'] or 'N/A'}")
            print()
    else:
        print("No French equipment found in equipment table.")

    # 2. Match reviews - French items
    print_section("2. FRENCH EQUIPMENT MATCH REVIEWS")
    cursor.execute("""
        SELECT
            canonical_id,
            witw_name,
            review_status,
            reviewer_notes,
            reviewed_at
        FROM match_reviews
        WHERE canonical_id LIKE 'FRA_%'
        ORDER BY reviewed_at DESC
    """)

    reviews = cursor.fetchall()

    if reviews:
        print(f"Total match reviews for French equipment: {len(reviews)}\n")

        # Group by status
        approved = [r for r in reviews if r['review_status'] == 'approved']
        rejected = [r for r in reviews if r['review_status'] == 'rejected']
        skipped = [r for r in reviews if r['review_status'] == 'skipped']

        print(f"Status breakdown:")
        print(f"  Approved: {len(approved)}")
        print(f"  Rejected: {len(rejected)}")
        print(f"  Skipped: {len(skipped)}")
        print()

        # Show approved items
        if approved:
            print(f"\n--- APPROVED ({len(approved)} items) ---\n")
            for idx, row in enumerate(approved, 1):
                print(f"{idx}. {row['witw_name']}")
                print(f"   ID: {row['canonical_id']}")
                print(f"   Status: {row['review_status']}")
                print(f"   Reviewed: {row['reviewed_at']}")
                if row['reviewer_notes']:
                    # Show first 150 chars of notes
                    notes = row['reviewer_notes'][:150]
                    if len(row['reviewer_notes']) > 150:
                        notes += "..."
                    print(f"   Notes: {notes}")
                print()

        # Show rejected items
        if rejected:
            print(f"\n--- REJECTED ({len(rejected)} items) ---\n")
            for idx, row in enumerate(rejected, 1):
                print(f"{idx}. {row['witw_name']}")
                print(f"   ID: {row['canonical_id']}")
                print(f"   Status: {row['review_status']}")
                print(f"   Reviewed: {row['reviewed_at']}")
                if row['reviewer_notes']:
                    # Show first 150 chars of notes
                    notes = row['reviewer_notes'][:150]
                    if len(row['reviewer_notes']) > 150:
                        notes += "..."
                    print(f"   Notes: {notes}")
                print()

        # Show skipped items
        if skipped:
            print(f"\n--- SKIPPED ({len(skipped)} items) ---\n")
            for idx, row in enumerate(skipped, 1):
                print(f"{idx}. {row['witw_name']}")
                print(f"   ID: {row['canonical_id']}")
                print(f"   Status: {row['review_status']}")
                print(f"   Reviewed: {row['reviewed_at']}")
                if row['reviewer_notes']:
                    notes = row['reviewer_notes'][:150]
                    if len(row['reviewer_notes']) > 150:
                        notes += "..."
                    print(f"   Notes: {notes}")
                print()
    else:
        print("No match reviews found for French equipment.")

    # 3. Research items with full notes
    print_section("3. RESEARCH COMPLETE ITEMS (Full Notes)")
    cursor.execute("""
        SELECT
            canonical_id,
            witw_name,
            review_status,
            reviewer_notes,
            reviewed_at
        FROM match_reviews
        WHERE canonical_id LIKE 'FRA_%'
            AND reviewer_notes LIKE '%RESEARCH COMPLETE%'
        ORDER BY reviewed_at DESC
    """)

    research_items = cursor.fetchall()

    if research_items:
        print(f"Total researched items: {len(research_items)}\n")
        for idx, row in enumerate(research_items, 1):
            print(f"{idx}. {row['witw_name']}")
            print(f"   ID: {row['canonical_id']}")
            print(f"   Status: {row['review_status']}")
            print(f"   Reviewed: {row['reviewed_at']}")
            print(f"\n   RESEARCH NOTES:")
            print(f"   {row['reviewer_notes']}")
            print()
    else:
        print("No researched items found.")

    # 4. Import log for French research
    print_section("4. FRENCH RESEARCH IMPORT LOG")
    cursor.execute("""
        SELECT
            source_name,
            source_file,
            import_started_at,
            import_completed_at,
            records_imported,
            records_failed,
            import_status,
            imported_by
        FROM import_log
        WHERE source_name LIKE '%french%'
        ORDER BY import_completed_at DESC
    """)

    logs = cursor.fetchall()

    if logs:
        print(f"Total import logs: {len(logs)}\n")
        for idx, row in enumerate(logs, 1):
            print(f"{idx}. {row['source_name']}")
            print(f"   File: {row['source_file']}")
            print(f"   Started: {row['import_started_at']}")
            print(f"   Completed: {row['import_completed_at']}")
            print(f"   Records imported: {row['records_imported']}")
            print(f"   Records failed: {row['records_failed']}")
            print(f"   Status: {row['import_status']}")
            print(f"   Imported by: {row['imported_by']}")
            print()
    else:
        print("No import logs found for French research.")

    # 5. Summary statistics
    print_section("5. SUMMARY STATISTICS")

    # Count French equipment
    cursor.execute("SELECT COUNT(*) FROM equipment WHERE nation = 'french'")
    equipment_count = cursor.fetchone()[0]

    # Count match reviews
    cursor.execute("SELECT COUNT(*) FROM match_reviews WHERE canonical_id LIKE 'FRA_%'")
    review_count = cursor.fetchone()[0]

    # Count by status
    cursor.execute("""
        SELECT review_status, COUNT(*) as count
        FROM match_reviews
        WHERE canonical_id LIKE 'FRA_%'
        GROUP BY review_status
    """)
    status_counts = cursor.fetchall()

    print(f"French equipment in database: {equipment_count}")
    print(f"French match reviews recorded: {review_count}")
    print(f"\nReview status breakdown:")
    for row in status_counts:
        print(f"  {row['review_status']}: {row['count']}")

    print(f"\n{'='*80}")

    conn.close()

if __name__ == '__main__':
    main()
