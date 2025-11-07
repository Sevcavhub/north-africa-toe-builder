#!/usr/bin/env python3
"""
Extract specific gun table pages from PDF as images using PyMuPDF (fitz).
More robust for handling corrupted PDFs.
"""

import fitz  # PyMuPDF
from pathlib import Path

PDF_PATH = Path(__file__).parent.parent.parent.parent / "Resource Documents" / "Battlegroup Game" / "Battlegroup-Canadas-Crucible.pdf"
OUTPUT_DIR = Path(__file__).parent.parent.parent.parent / "temp_gun_pages"

def extract_pages_as_images(start_page: int, end_page: int, prefix: str):
    """Extract PDF pages as images using PyMuPDF"""

    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"Opening PDF: {PDF_PATH}")

    try:
        # Open PDF
        doc = fitz.open(PDF_PATH)
        print(f"PDF has {len(doc)} pages")

        # Adjust for 0-indexed pages
        start_idx = start_page - 1
        end_idx = end_page - 1

        if start_idx < 0 or end_idx >= len(doc):
            print(f"ERROR: Page range {start_page}-{end_page} out of bounds (PDF has {len(doc)} pages)")
            return []

        print(f"Extracting pages {start_page}-{end_page} (indices {start_idx}-{end_idx})...")

        saved_files = []
        for page_num in range(start_idx, end_idx + 1):
            try:
                page = doc[page_num]

                # Render page to image (pixmap)
                # zoom=2 gives 144 DPI (good quality)
                mat = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat)

                # Save as PNG
                output_file = OUTPUT_DIR / f"{prefix}_page_{page_num + 1}.png"
                pix.save(output_file)

                print(f"  Saved page {page_num + 1}: {output_file.name} ({pix.width}x{pix.height})")
                saved_files.append(output_file)

            except Exception as e:
                print(f"  ERROR on page {page_num + 1}: {e}")
                continue

        doc.close()

        print(f"\nExtracted {len(saved_files)} pages successfully")
        return saved_files

    except Exception as e:
        print(f"ERROR opening PDF: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    """Extract Canadian and German gun pages"""

    print("=== EXTRACTING CANADIAN GUNS (pages 130-132) ===\n")
    canadian_files = extract_pages_as_images(130, 132, "canadian_guns")

    print("\n=== EXTRACTING GERMAN GUNS (pages 134-136) ===\n")
    german_files = extract_pages_as_images(134, 136, "german_guns")

    print(f"\n=== COMPLETE ===")
    print(f"Canadian pages: {len(canadian_files)}")
    print(f"German pages: {len(german_files)}")
    print(f"\nFiles saved in: {OUTPUT_DIR}")

    if canadian_files or german_files:
        print("\n✓ SUCCESS: Images extracted")
        print("Next: Use Claude vision to read these images and extract gun data")
    else:
        print("\n✗ FAILED: No images extracted")

if __name__ == '__main__':
    main()
