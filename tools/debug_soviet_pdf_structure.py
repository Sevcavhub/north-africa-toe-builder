#!/usr/bin/env python3
"""Debug Soviet BattleGroup PDF structure."""

import PyPDF2
from pathlib import Path

def main():
    pdf_path = Path(r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Battlegroup-DataCards-Soviets.pdf")

    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        total_pages = len(pdf_reader.pages)

        print(f"Total pages: {total_pages}\n")

        # Extract text from first 3 pages to see structure
        for page_num in range(min(3, total_pages)):
            print(f"{'='*60}")
            print(f"PAGE {page_num + 1}")
            print(f"{'='*60}")

            page = pdf_reader.pages[page_num]
            text = page.extract_text()

            # Print first 2000 chars
            print(text[:2000])
            print("\n")

if __name__ == "__main__":
    main()
