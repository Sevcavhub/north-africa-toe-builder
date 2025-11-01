#!/usr/bin/env python3
"""Debug pdfplumber extraction."""

import pdfplumber
from pathlib import Path

def main():
    pdf_path = Path(r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Battlegroup-DataCards-Soviets.pdf")

    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}\n")

        # Check first 3 pages
        for i in range(min(3, len(pdf.pages))):
            page = pdf.pages[i]
            text = page.extract_text()

            print(f"{'='*60}")
            print(f"PAGE {i+1}")
            print(f"{'='*60}")

            if text:
                print(f"Text length: {len(text)} characters")
                print("\nFirst 1000 characters:")
                print(text[:1000])
            else:
                print("NO TEXT EXTRACTED")

            # Try extracting tables
            tables = page.extract_tables()
            if tables:
                print(f"\nFound {len(tables)} tables")
                for j, table in enumerate(tables[:2]):  # Show first 2 tables
                    print(f"\nTable {j+1}:")
                    for row in table[:5]:  # Show first 5 rows
                        print(row)
            else:
                print("\nNo tables found")

            print("\n")

if __name__ == "__main__":
    main()
