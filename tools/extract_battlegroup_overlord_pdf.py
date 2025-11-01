#!/usr/bin/env python3
"""
Extract vehicle and gun data from BattleGroup Overlord Army Lists PDF.
Uses PyMuPDF (fitz) with OCR for image-based PDFs.
Includes duplicate detection against existing database.
"""

import fitz  # PyMuPDF
import re
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
from datetime import datetime
import sys

# Paths
PDF_PATH = Path("D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Battlegroup-Overlord-Army-Lists.pdf")
DB_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")
OUTPUT_DIR = Path("D:/north-africa-toe-builder/data/output")
VEHICLES_OUTPUT = OUTPUT_DIR / "battlegroup_overlord_vehicles.json"
GUNS_OUTPUT = OUTPUT_DIR / "battlegroup_overlord_guns.json"
REPORT_OUTPUT = Path("D:/north-africa-toe-builder/BATTLEGROUP_OVERLORD_EXTRACTION.md")

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_existing_entries() -> Tuple[Set[Tuple[str, str]], Set[Tuple[str, str]]]:
    """Load existing vehicles and guns from database for duplicate detection."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute("SELECT name, nation FROM bg_reference_vehicles")
    existing_vehicles = {(row[0].lower().strip(), row[1].lower()) for row in cursor.fetchall()}

    cursor.execute("SELECT name, nation FROM bg_reference_guns")
    existing_guns = {(row[0].lower().strip(), row[1].lower()) for row in cursor.fetchall()}

    conn.close()

    print(f"Loaded {len(existing_vehicles)} existing vehicles")
    print(f"Loaded {len(existing_guns)} existing guns")

    return existing_vehicles, existing_guns

def extract_text_from_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    """Extract text from PDF page by page."""
    pages_data = []

    try:
        doc = fitz.open(str(pdf_path))
        print(f"PDF opened: {len(doc)} pages")

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()

            pages_data.append({
                'page_number': page_num + 1,
                'text': text
            })

            if (page_num + 1) % 10 == 0:
                print(f"Processed {page_num + 1}/{len(doc)} pages...")

        doc.close()
        print(f"Extraction complete: {len(pages_data)} pages processed")

    except Exception as e:
        print(f"Error extracting PDF: {e}")
        import traceback
        traceback.print_exc()
        return []

    return pages_data

def main():
    """Main extraction workflow."""
    print("=" * 80)
    print("BattleGroup Overlord PDF Extraction")
    print("=" * 80)

    # Check if PDF exists
    if not PDF_PATH.exists():
        print(f"ERROR: PDF not found at {PDF_PATH}")
        return 1

    print(f"PDF found: {PDF_PATH}")

    # Step 1: Load existing entries
    print("\n[1/3] Loading existing database entries...")
    existing_vehicles, existing_guns = load_existing_entries()

    # Step 2: Extract text from PDF
    print("\n[2/3] Extracting text from PDF...")
    pages_data = extract_text_from_pdf(PDF_PATH)

    if not pages_data:
        print("ERROR: Failed to extract PDF data")
        return 1

    # Step 3: Save raw text for manual review
    print("\n[3/3] Saving raw text...")
    raw_text_path = OUTPUT_DIR / "battlegroup_overlord_raw.txt"
    with open(raw_text_path, 'w', encoding='utf-8') as f:
        for page in pages_data:
            f.write(f"\n\n{'=' * 80}\n")
            f.write(f"PAGE {page['page_number']}\n")
            f.write(f"{'=' * 80}\n\n")
            f.write(page['text'])
    
    print(f"Raw text saved to {raw_text_path}")
    print(f"Total pages: {len(pages_data)}")
    print(f"Total characters extracted: {sum(len(p['text']) for p in pages_data)}")

    print("\n" + "=" * 80)
    print("TEXT EXTRACTION COMPLETE")
    print("=" * 80)
    print("\nNext step: Review raw text file to design parsing logic")

    return 0

if __name__ == '__main__':
    sys.exit(main())
