#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR PDF Extraction Script - For Image-Based (Scanned) PDFs

Extracts text from scanned PDF files using Tesseract OCR in manageable chunks.

Requirements:
    pip install pytesseract pdf2image pillow

System Requirements:
    - Tesseract OCR installed (https://github.com/tesseract-ocr/tesseract)
      Windows: https://github.com/UB-Mannheim/tesseract/wiki
      Linux: sudo apt-get install tesseract-ocr
      Mac: brew install tesseract

    - Poppler installed (for pdf2image)
      Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases
      Linux: sudo apt-get install poppler-utils
      Mac: brew install poppler

Usage:
    python scripts/ocr_pdf_chunks.py "path/to/file.pdf" --chunk-size 10
    python scripts/ocr_pdf_chunks.py "path/to/file.pdf" --pages 1-20 --chunk-size 5
"""

import sys
import os
from pathlib import Path
import argparse

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
except ImportError as e:
    print("\n❌ Missing required Python packages!")
    print("\nPlease install:")
    print("  pip install pytesseract pdf2image pillow")
    print("\nAlso ensure Tesseract OCR and Poppler are installed (see script header for links)")
    sys.exit(1)

# Configure Tesseract path for Windows (if not in PATH)
if sys.platform == 'win32':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_pdf_with_ocr(pdf_path, chunk_size=10, page_range=None):
    """
    Extract text from scanned PDF using OCR in chunks

    Args:
        pdf_path: Path to PDF file
        chunk_size: Number of pages per chunk
        page_range: Tuple of (start_page, end_page) or None for all pages
    """

    print(f"\n📄 OCR Extraction: {Path(pdf_path).name}")
    print(f"📦 Chunk size: {chunk_size} pages\n")

    # Create output directory
    output_dir = Path(__file__).parent.parent / "data" / "output" / "pdf_extracts"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine page range
    if page_range:
        first_page, last_page = page_range
        print(f"🎯 Extracting pages {first_page}-{last_page}\n")
    else:
        first_page = None
        last_page = None
        print("🎯 Extracting all pages\n")

    # Convert PDF to images (page by page to save memory)
    print("⚙️  Converting PDF to images and running OCR...")

    # Base filename for outputs
    base_name = Path(pdf_path).stem

    # Process in chunks
    current_page = first_page if first_page else 1
    chunk_num = 1

    while True:
        chunk_start = current_page
        chunk_end = current_page + chunk_size - 1

        if last_page and chunk_end > last_page:
            chunk_end = last_page

        if last_page and chunk_start > last_page:
            break

        print(f"\n📖 Processing pages {chunk_start}-{chunk_end}...")

        try:
            # Convert just this chunk of pages
            images = convert_from_path(
                pdf_path,
                first_page=chunk_start,
                last_page=chunk_end,
                dpi=200  # Balance between quality and speed
            )

            # OCR each page
            chunk_text = ""
            for idx, image in enumerate(images):
                page_num = chunk_start + idx
                print(f"   🔍 OCR page {page_num}...", end="", flush=True)

                # Run OCR
                page_text = pytesseract.image_to_string(image, lang='eng')

                chunk_text += f"\n{'='*70}\nPAGE {page_num}\n{'='*70}\n\n"
                chunk_text += page_text.strip() + "\n"

                print(f" ✅ ({len(page_text)} chars)")

            # Save chunk to file
            output_filename = f"{base_name}_pages_{chunk_start}-{chunk_end}.txt"
            output_path = output_dir / output_filename

            header = f"""{'='*80}
PDF Extract (OCR): {Path(pdf_path).name}
Pages: {chunk_start}-{chunk_end}
Extracted: {__import__('datetime').datetime.now().isoformat()}
{'='*80}

"""

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(header + chunk_text)

            print(f"   ✅ Saved: {output_filename} ({len(chunk_text)} chars)")

        except Exception as e:
            print(f"   ❌ Error processing pages {chunk_start}-{chunk_end}: {e}")

        # Move to next chunk
        current_page = chunk_end + 1
        chunk_num += 1

        # Break if we've reached the end
        if last_page and current_page > last_page:
            break

    print(f"\n✨ OCR extraction complete!")
    print(f"📂 Files saved to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description='Extract text from scanned PDFs using OCR',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/ocr_pdf_chunks.py "file.pdf"
  python scripts/ocr_pdf_chunks.py "file.pdf" --chunk-size 5
  python scripts/ocr_pdf_chunks.py "file.pdf" --pages 1-20 --chunk-size 10
        """
    )

    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--chunk-size', type=int, default=10,
                       help='Number of pages per chunk (default: 10)')
    parser.add_argument('--pages', type=str,
                       help='Page range to extract (e.g., "1-20")')

    args = parser.parse_args()

    # Validate PDF exists
    if not os.path.exists(args.pdf_path):
        print(f"\n❌ Error: PDF file not found: {args.pdf_path}")
        sys.exit(1)

    # Parse page range
    page_range = None
    if args.pages:
        try:
            start, end = map(int, args.pages.split('-'))
            page_range = (start, end)
        except ValueError:
            print(f"\n❌ Error: Invalid page range format. Use: --pages 1-20")
            sys.exit(1)

    # Run OCR extraction
    try:
        extract_pdf_with_ocr(args.pdf_path, args.chunk_size, page_range)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
