#!/usr/bin/env python3
"""
Extract specific gun table pages from PDF as images for Claude vision reading.
"""

from pathlib import Path
from pdf2image import convert_from_path

PDF_PATH = Path(__file__).parent.parent.parent.parent / "Resource Documents" / "Battlegroup Game" / "Battlegroup-Canadas-Crucible.pdf"
OUTPUT_DIR = Path(__file__).parent.parent.parent.parent / "temp_gun_pages"

def extract_pages(start_page: int, end_page: int, prefix: str):
    """Extract PDF pages as images"""

    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"Extracting pages {start_page}-{end_page} from PDF...")
    print(f"PDF: {PDF_PATH}")
    print(f"Output: {OUTPUT_DIR}")

    try:
        images = convert_from_path(
            PDF_PATH,
            first_page=start_page,
            last_page=end_page,
            dpi=200  # Good balance of quality and file size
        )

        saved_files = []
        for i, image in enumerate(images, start=start_page):
            output_file = OUTPUT_DIR / f"{prefix}_page_{i}.png"
            image.save(output_file, 'PNG')
            print(f"  Saved: {output_file}")
            saved_files.append(output_file)

        print(f"\nExtracted {len(saved_files)} pages successfully")
        return saved_files

    except Exception as e:
        print(f"ERROR: {e}")
        return []

def main():
    """Extract Canadian and German gun pages"""

    print("=== EXTRACTING CANADIAN GUNS (pages 130-132) ===")
    canadian_files = extract_pages(130, 132, "canadian_guns")

    print("\n=== EXTRACTING GERMAN GUNS (pages 134-136) ===")
    german_files = extract_pages(134, 136, "german_guns")

    print(f"\n=== COMPLETE ===")
    print(f"Canadian pages: {len(canadian_files)}")
    print(f"German pages: {len(german_files)}")
    print(f"\nFiles saved in: {OUTPUT_DIR}")
    print("\nNext: Use Claude vision to read these images and extract gun data")

if __name__ == '__main__':
    main()
