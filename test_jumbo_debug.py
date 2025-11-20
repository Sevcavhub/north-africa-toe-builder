#!/usr/bin/env python3
"""Test datacard generation with full exception details"""

import sys
import traceback
from pathlib import Path

# Use web database like Render.com does
DATABASE_PATH = Path("scripts/battlegroup/web/database/web_database.db")

sys.path.insert(0, str(Path(__file__).parent))

from scripts.battlegroup.book.generate_book_datacards_v6_1 import BookDatacardGenerator

print("Testing Crusader I datacard generation")
print("=" * 70)
print(f"Database: {DATABASE_PATH}")
print(f"Exists: {DATABASE_PATH.exists()}")
print()

try:
    generator = BookDatacardGenerator(database_path=DATABASE_PATH)

    equipment = {
        'name': 'Crusader I',
        'nation_override': 'british'
    }

    print(f"Generating datacard for: {equipment}")
    print()

    datacard = generator.generate_datacard_markdown(equipment, 'r')

    if datacard:
        print("SUCCESS!")
        print()
        print("First 500 characters:")
        print(datacard[:500])
        print()

        if "Could not" in datacard or "Error" in datacard:
            print("WARNING: Datacard contains error message")
        else:
            print("Datacard generated successfully")
    else:
        print("ERROR: Generator returned None or empty string")

    generator.close()

except Exception as e:
    print(f"EXCEPTION CAUGHT: {type(e).__name__}")
    print(f"Message: {str(e)}")
    print()
    print("Full traceback:")
    traceback.print_exc()
