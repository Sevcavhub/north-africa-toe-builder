#!/usr/bin/env python3
"""
Extract text from Fall of the Reich PDF using OCR (pdf2image + pytesseract).
Falls back to alternative methods if OCR not available.
"""

import sys
from pathlib import Path

# Try to import OCR dependencies
try:
    import pdf2image
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("WARNING: OCR libraries not available. Install with:")
    print("  pip install pdf2image pytesseract pillow")
    print("  Also requires poppler and tesseract-ocr system packages")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

PDF_PATH = Path(r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Battlegroup-Fall-of-the-Reich-Full.pdf")
OUTPUT_PATH = Path(r"D:\north-africa-toe-builder\data\output\fall_of_reich_ocr_text.txt")

def extract_with_ocr():
    """Extract text using OCR (pdf2image + pytesseract)."""
    if not OCR_AVAILABLE:
        print("OCR not available. Cannot proceed.")
        return None

    print(f"Extracting text from {PDF_PATH.name} using OCR...")
    print("This may take 5-10 minutes for 96 pages...")

    all_text = []

    try:
        # Convert PDF to images
        print("Converting PDF pages to images...")
        images = pdf2image.convert_from_path(str(PDF_PATH), dpi=300)

        print(f"Processing {len(images)} pages with OCR...")
        for i, image in enumerate(images, 1):
            if i % 5 == 0:
                print(f"  OCR progress: {i}/{len(images)}")

            # Extract text from image
            text = pytesseract.image_to_string(image, lang='eng')
            all_text.append(f"\n--- PAGE {i} ---\n{text}")

        full_text = "\n".join(all_text)

        # Save to file
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            f.write(full_text)

        print(f"\nOCR complete! Text saved to: {OUTPUT_PATH}")
        print(f"Total characters extracted: {len(full_text):,}")

        return full_text

    except Exception as e:
        print(f"OCR failed: {e}")
        return None

def check_pdf_readability():
    """Check if PDF has extractable text or is image-only."""
    if not PDFPLUMBER_AVAILABLE:
        print("pdfplumber not available")
        return False

    print("Checking if PDF has extractable text...")

    with pdfplumber.open(str(PDF_PATH)) as pdf:
        # Check first 10 pages
        text_pages = 0
        for i in range(min(10, len(pdf.pages))):
            text = pdf.pages[i].extract_text()
            if text and len(text.strip()) > 100:
                text_pages += 1

        if text_pages > 0:
            print(f"PDF has extractable text on {text_pages}/10 sample pages")
            return True
        else:
            print("PDF appears to be image-only (scanned pages)")
            return False

def main():
    """Main execution."""
    print("=" * 80)
    print("Fall of the Reich PDF Text Extraction")
    print("=" * 80)

    # Check readability
    has_text = check_pdf_readability()

    if has_text:
        print("\nPDF has extractable text. Use standard extraction instead of OCR.")
        sys.exit(0)

    # Try OCR
    print("\nAttempting OCR extraction...")
    result = extract_with_ocr()

    if result:
        print("\nSUCCESS: Text extracted via OCR")
        print(f"Output: {OUTPUT_PATH}")
    else:
        print("\nFAILED: Could not extract text")
        print("\nAlternative options:")
        print("1. Install OCR dependencies:")
        print("   pip install pdf2image pytesseract pillow")
        print("   choco install poppler tesseract")
        print("2. Use online OCR service to extract text manually")
        print("3. Check if Fall of the Reich data is already in other datacard files")

if __name__ == '__main__':
    main()
