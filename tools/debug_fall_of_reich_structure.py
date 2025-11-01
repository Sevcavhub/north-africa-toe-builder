#!/usr/bin/env python3
"""Debug script to examine Fall of the Reich PDF structure."""

import pdfplumber
from pathlib import Path

PDF_PATH = Path(r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Battlegroup-Fall-of-the-Reich-Full.pdf")
OUTPUT_PATH = Path(r"D:\north-africa-toe-builder\data\output\fall_of_reich_sample_pages.txt")

def extract_sample_pages():
    """Extract a few sample pages to understand structure."""
    samples = []

    with pdfplumber.open(str(PDF_PATH)) as pdf:
        # Get pages with likely vehicle/gun data
        # Table of contents, army lists, datacards typically in middle/back
        page_ranges = [
            (0, 5, "Opening pages"),
            (20, 25, "Mid-book section 1"),
            (40, 45, "Mid-book section 2"),
            (60, 65, "Later section 1"),
            (80, 85, "Later section 2"),
            (90, 96, "End section")
        ]

        for start, end, description in page_ranges:
            samples.append(f"\n{'=' * 80}\n{description} (Pages {start+1}-{end})\n{'=' * 80}\n")

            for page_num in range(start, min(end, len(pdf.pages))):
                page = pdf.pages[page_num]
                text = page.extract_text()

                samples.append(f"\n--- PAGE {page_num + 1} ---\n")
                samples.append(text[:2000] if text else "[NO TEXT]")  # First 2000 chars
                samples.append(f"\n... (page {page_num + 1} truncated)\n")

    full_sample = "\n".join(samples)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(full_sample)

    print(f"Sample pages saved to: {OUTPUT_PATH}")
    print(f"Total pages in PDF: {len(pdf.pages)}")

    # Also print first page to console
    with pdfplumber.open(str(PDF_PATH)) as pdf:
        print("\n" + "=" * 80)
        print("FIRST PAGE SAMPLE:")
        print("=" * 80)
        print(pdf.pages[0].extract_text()[:1500])

if __name__ == '__main__':
    extract_sample_pages()
