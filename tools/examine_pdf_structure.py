#!/usr/bin/env python3
"""
Examine PDF structure to understand BattleGroup datacard format
"""

import sys
from pathlib import Path

try:
    import PyPDF2
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
    import PyPDF2

def examine_pdf(pdf_path):
    """Print first few pages to understand structure"""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        total_pages = len(pdf_reader.pages)
        print(f"Total pages: {total_pages}\n")

        # Examine first 2 pages in detail
        for page_num in range(min(2, total_pages)):
            print(f"{'='*80}")
            print(f"PAGE {page_num + 1}")
            print(f"{'='*80}")
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            print(text[:2000])  # First 2000 chars
            print("\n")

def main():
    pdf_path = Path(r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Battlegroup-DataCards-US.pdf")

    if not pdf_path.exists():
        print(f"ERROR: PDF not found at {pdf_path}")
        sys.exit(1)

    examine_pdf(pdf_path)

if __name__ == '__main__':
    main()
