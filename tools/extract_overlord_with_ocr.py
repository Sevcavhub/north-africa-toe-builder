#!/usr/bin/env python3
"""
Extract vehicle and gun data from BattleGroup Overlord Army Lists PDF using OCR.
This is an image-based scanned PDF, so we'll use Tesseract OCR via PyMuPDF.
"""

import fitz  # PyMuPDF
import json
import sqlite3
from pathlib import Path
from typing import Set, Tuple
import sys

# Paths
PDF_PATH = Path("D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Battlegroup-Overlord-Army-Lists.pdf")
DB_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")
OUTPUT_DIR = Path("D:/north-africa-toe-builder/data/output")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_existing_entries() -> Tuple[Set[Tuple[str, str]], Set[Tuple[str, str]]]:
    """Load existing vehicles and guns from database."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute("SELECT name, nation FROM bg_reference_vehicles")
    existing_vehicles = {(row[0].lower().strip(), row[1].lower()) for row in cursor.fetchall()}

    cursor.execute("SELECT name, nation FROM bg_reference_guns")
    existing_guns = {(row[0].lower().strip(), row[1].lower()) for row in cursor.fetchall()}

    conn.close()
    return existing_vehicles, existing_guns

def extract_with_ocr(pdf_path: Path, max_pages: int = 10):
    """Extract text using OCR from first few pages to test."""
    try:
        import pytesseract
        from PIL import Image
        import io
        
        doc = fitz.open(str(pdf_path))
        print(f"PDF opened: {len(doc)} pages")
        print(f"Extracting first {max_pages} pages with OCR...")
        
        ocr_text = []
        
        for page_num in range(min(max_pages, len(doc))):
            page = doc[page_num]
            
            # Render page to image
            pix = page.get_pixmap(dpi=300)  # High DPI for better OCR
            img_bytes = pix.tobytes("png")
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(img_bytes))
            
            # Run OCR
            text = pytesseract.image_to_string(image)
            
            ocr_text.append({
                'page_number': page_num + 1,
                'text': text
            })
            
            print(f"Page {page_num + 1}/{max_pages}: {len(text)} characters")
        
        doc.close()
        return ocr_text
        
    except ImportError:
        print("ERROR: Tesseract OCR not available")
        print("This is an image-based PDF and requires OCR")
        return None
    except Exception as e:
        print(f"OCR Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main extraction workflow."""
    print("=" * 80)
    print("BattleGroup Overlord OCR Extraction")
    print("=" * 80)

    if not PDF_PATH.exists():
        print(f"ERROR: PDF not found at {PDF_PATH}")
        return 1

    # Load existing entries
    print("\nLoading existing database entries...")
    existing_vehicles, existing_guns = load_existing_entries()
    print(f"Existing: {len(existing_vehicles)} vehicles, {len(existing_guns)} guns")

    # Try OCR on first 10 pages
    print("\nAttempting OCR extraction...")
    ocr_data = extract_with_ocr(PDF_PATH, max_pages=10)

    if ocr_data:
        # Save OCR text
        ocr_output = OUTPUT_DIR / "battlegroup_overlord_ocr_sample.txt"
        with open(ocr_output, 'w', encoding='utf-8') as f:
            for page in ocr_data:
                f.write(f"\n\n{'=' * 80}\n")
                f.write(f"PAGE {page['page_number']}\n")
                f.write(f"{'=' * 80}\n\n")
                f.write(page['text'])
        
        print(f"\nOCR sample saved to: {ocr_output}")
        total_chars = sum(len(p['text']) for p in ocr_data)
        print(f"Total characters: {total_chars}")
    else:
        print("\nOCR not available. Manual extraction required.")
        print("\nRECOMMENDATION:")
        print("1. Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
        print("2. Install pytesseract: pip install pytesseract pillow")
        print("3. Re-run this script")
        print("\nOR: Manual transcription of key data tables")

    return 0

if __name__ == '__main__':
    sys.exit(main())
