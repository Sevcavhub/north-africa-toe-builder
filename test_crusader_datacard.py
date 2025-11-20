#!/usr/bin/env python3
"""Test generating datacard for Crusader I"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from scripts.battlegroup.book.generate_book_datacards_v6_1 import BookDatacardGenerator

DATABASE_PATH = project_root / "database" / "master_database.db"

def test_crusader_datacard():
    generator = BookDatacardGenerator(database_path=DATABASE_PATH)

    # Test data matching what the web interface would send
    equipment = {
        'name': 'Crusader I',
        'nation_override': 'british'
    }

    print("=" * 70)
    print("Testing Crusader I Datacard Generation")
    print("=" * 70)
    print(f"Equipment: {equipment}")
    print()

    try:
        datacard = generator.generate_datacard_markdown(equipment, 'r')

        if datacard:
            print("SUCCESS: Datacard generated")
            print()
            print("Datacard Preview (first 500 chars):")
            print(datacard[:500])
            print()

            # Check for key elements
            checks = {
                'Has vehicle name': 'Crusader I' in datacard,
                'Has armor values': 'Armour' in datacard,
                'Has weapon data': 'Weapon' in datacard or 'AP Pen' in datacard,
                'Has nation colors': 'british-tan' in datacard or 'british' in datacard
            }

            print("Content checks:")
            for check, passed in checks.items():
                print(f"  {check}: {'PASS' if passed else 'FAIL'}")
        else:
            print("FAIL: Generator returned empty datacard")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        print()
        print("Full traceback:")
        traceback.print_exc()

    generator.close()

if __name__ == "__main__":
    test_crusader_datacard()
