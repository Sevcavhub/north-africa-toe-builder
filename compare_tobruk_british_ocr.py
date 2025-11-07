#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tobruk British PDF vs Text Comparison - OCR Quality Validation

Extracts text from Tobruk British.pdf using Tesseract OCR at 600 DPI
and compares with existing Tobruk British.txt for 100% match validation.

Requirements:
    pip install pytesseract pdf2image pillow difflib
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
import difflib

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
    print("\nAlso ensure Tesseract OCR and Poppler are installed")
    sys.exit(1)

# Configure Tesseract path for Windows (if not in PATH)
if sys.platform == 'win32':
    # Try common installation paths
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Users\chapm\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
    ]

    tesseract_found = False
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            tesseract_found = True
            print(f"✅ Found Tesseract at: {path}")
            break

    if not tesseract_found:
        print("\n⚠️  Tesseract not found in common locations.")
        print("Please install from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("\nOr set the path manually in the script.")


def extract_pdf_ocr_600dpi(pdf_path):
    """
    Extract text from PDF using OCR at 600 DPI (highest quality)

    Args:
        pdf_path: Path to PDF file

    Returns:
        dict with extracted text and metadata
    """

    print(f"\n📄 OCR Extraction (600 DPI): {Path(pdf_path).name}")
    print(f"⚙️  Converting PDF to images at 600 DPI...")

    try:
        # Convert PDF to images at 600 DPI for highest quality
        images = convert_from_path(
            pdf_path,
            dpi=600,  # Highest quality as requested
            fmt='png'
        )

        print(f"✅ Converted {len(images)} pages to images")

        # OCR each page
        full_text = ""
        page_texts = []

        for idx, image in enumerate(images):
            page_num = idx + 1
            print(f"   🔍 OCR page {page_num}/{len(images)}...", end="", flush=True)

            # Run OCR with custom config for best accuracy
            custom_config = r'--oem 3 --psm 1'  # LSTM engine, auto page segmentation
            page_text = pytesseract.image_to_string(image, lang='eng', config=custom_config)

            page_texts.append({
                'page_number': page_num,
                'text': page_text.strip(),
                'char_count': len(page_text)
            })

            full_text += f"\n{'='*70}\nPAGE {page_num}\n{'='*70}\n\n"
            full_text += page_text.strip() + "\n"

            print(f" ✅ ({len(page_text)} chars)")

        result = {
            'source': 'OCR_600DPI',
            'filename': Path(pdf_path).name,
            'extraction_date': datetime.now().isoformat(),
            'total_pages': len(images),
            'dpi': 600,
            'ocr_engine': 'Tesseract LSTM',
            'full_text': full_text.strip(),
            'page_texts': page_texts,
            'total_chars': len(full_text)
        }

        print(f"\n✨ OCR extraction complete!")
        print(f"📊 Total: {len(images)} pages, {len(full_text):,} characters")

        return result

    except Exception as e:
        print(f"\n❌ Error during OCR extraction: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def read_text_file(txt_path):
    """
    Read existing text file

    Args:
        txt_path: Path to text file

    Returns:
        dict with text content and metadata
    """

    print(f"\n📄 Reading existing text file: {Path(txt_path).name}")

    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Count pages (assuming page markers like in OCR output)
        page_count = content.count('PAGE ')

        result = {
            'source': 'EXISTING_TEXT',
            'filename': Path(txt_path).name,
            'read_date': datetime.now().isoformat(),
            'full_text': content.strip(),
            'total_chars': len(content),
            'estimated_pages': page_count if page_count > 0 else 1
        }

        print(f"✅ Read {len(content):,} characters")
        if page_count > 0:
            print(f"📊 Estimated pages: {page_count}")

        return result

    except Exception as e:
        print(f"\n❌ Error reading text file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def compare_texts(ocr_data, txt_data):
    """
    Compare OCR extraction with existing text file

    Args:
        ocr_data: OCR extraction result dict
        txt_data: Text file result dict

    Returns:
        dict with comparison analysis
    """

    print(f"\n📊 Performing Comparative Analysis...")
    print(f"{'='*70}")

    ocr_text = ocr_data['full_text']
    txt_text = txt_data['full_text']

    # Character counts
    ocr_chars = len(ocr_text)
    txt_chars = len(txt_text)

    print(f"\n📏 Character Counts:")
    print(f"   OCR (600 DPI):    {ocr_chars:,} chars")
    print(f"   Existing Text:    {txt_chars:,} chars")
    print(f"   Difference:       {abs(ocr_chars - txt_chars):,} chars ({abs(ocr_chars - txt_chars) / max(ocr_chars, txt_chars) * 100:.2f}%)")

    # Exact match check
    exact_match = (ocr_text == txt_text)

    print(f"\n✅ Exact Match: {'YES' if exact_match else 'NO'}")

    # If not exact match, perform detailed diff
    differences = []
    match_percentage = 100.0

    if not exact_match:
        print(f"\n🔍 Generating detailed diff...")

        # Line-by-line comparison
        ocr_lines = ocr_text.splitlines()
        txt_lines = txt_text.splitlines()

        print(f"   OCR Lines:  {len(ocr_lines):,}")
        print(f"   Text Lines: {len(txt_lines):,}")

        # Generate unified diff
        diff = list(difflib.unified_diff(
            txt_lines,
            ocr_lines,
            fromfile='Existing_Text',
            tofile='OCR_600DPI',
            lineterm=''
        ))

        differences = diff

        # Calculate similarity using SequenceMatcher
        matcher = difflib.SequenceMatcher(None, txt_text, ocr_text)
        match_percentage = matcher.ratio() * 100

        print(f"   Similarity: {match_percentage:.2f}%")
        print(f"   Diff Lines: {len(diff):,}")

    result = {
        'comparison_date': datetime.now().isoformat(),
        'ocr_source': ocr_data['source'],
        'text_source': txt_data['source'],
        'ocr_chars': ocr_chars,
        'text_chars': txt_chars,
        'char_difference': abs(ocr_chars - txt_chars),
        'char_diff_percentage': abs(ocr_chars - txt_chars) / max(ocr_chars, txt_chars) * 100,
        'exact_match': exact_match,
        'similarity_percentage': match_percentage,
        'differences': differences[:100] if differences else [],  # First 100 diff lines
        'total_diff_lines': len(differences)
    }

    return result


def save_json(data, filename):
    """Save data to JSON file"""
    output_path = Path(__file__).parent / filename

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"💾 Saved: {filename}")
    return output_path


def main():
    print("="*70)
    print("Tobruk British PDF vs Text - OCR Quality Validation")
    print("="*70)

    # Paths
    pdf_path = Path(r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Tobruk British.pdf")
    txt_path = Path(r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Tobruk British.txt")

    # Validate files exist
    if not pdf_path.exists():
        print(f"\n❌ Error: PDF not found: {pdf_path}")
        sys.exit(1)

    if not txt_path.exists():
        print(f"\n❌ Error: Text file not found: {txt_path}")
        sys.exit(1)

    print(f"\n✅ Found PDF: {pdf_path.name}")
    print(f"✅ Found TXT: {txt_path.name}")

    # Step 1: OCR extraction at 600 DPI
    print(f"\n{'='*70}")
    print("STEP 1: OCR Extraction (600 DPI)")
    print(f"{'='*70}")
    ocr_data = extract_pdf_ocr_600dpi(str(pdf_path))

    # Save OCR result to JSON
    ocr_json_path = save_json(ocr_data, 'tobruk_british_ocr_600dpi.json')

    # Step 2: Read existing text file
    print(f"\n{'='*70}")
    print("STEP 2: Read Existing Text File")
    print(f"{'='*70}")
    txt_data = read_text_file(str(txt_path))

    # Save text result to JSON
    txt_json_path = save_json(txt_data, 'tobruk_british_existing_text.json')

    # Step 3: Comparative analysis
    print(f"\n{'='*70}")
    print("STEP 3: Comparative Analysis")
    print(f"{'='*70}")
    comparison_result = compare_texts(ocr_data, txt_data)

    # Save comparison report
    comparison_json_path = save_json(comparison_result, 'tobruk_british_comparison_report.json')

    # Generate summary report
    print(f"\n{'='*70}")
    print("FINAL REPORT")
    print(f"{'='*70}")

    print(f"\n📁 Output Files:")
    print(f"   1. {ocr_json_path.name} - OCR extraction (600 DPI)")
    print(f"   2. {txt_json_path.name} - Existing text file")
    print(f"   3. {comparison_json_path.name} - Comparison analysis")

    print(f"\n📊 Quality Assessment:")
    print(f"   Exact Match:      {'✅ YES' if comparison_result['exact_match'] else '❌ NO'}")
    print(f"   Similarity:       {comparison_result['similarity_percentage']:.2f}%")
    print(f"   Char Difference:  {comparison_result['char_difference']:,} chars ({comparison_result['char_diff_percentage']:.2f}%)")

    if comparison_result['similarity_percentage'] >= 99.0:
        print(f"\n✅ VALIDATION: Near-perfect match (≥99%)")
    elif comparison_result['similarity_percentage'] >= 95.0:
        print(f"\n⚠️  VALIDATION: Good match (≥95%) but review differences")
    else:
        print(f"\n❌ VALIDATION: Significant differences detected (<95%)")
        print(f"   Review comparison_report.json for details")

    print(f"\n{'='*70}")
    print("✨ Analysis Complete!")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()
