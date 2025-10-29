#!/usr/bin/env python3
"""
Search Nafziger PDFs for air force units with strength data.
Focus on finding Italian and British sources that have aircraft numbers.
"""

import os
import re
import subprocess
from pathlib import Path

def extract_pdf_text(pdf_path, max_pages=10):
    """Extract text from first N pages of PDF."""
    try:
        result = subprocess.run(
            ['pdftotext', '-l', str(max_pages), str(pdf_path), '-'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout
    except Exception as e:
        return ""

def has_air_units(text):
    """Check if text contains air unit designations."""
    patterns = [
        r'(JG|StG|KG|ZG|LG)\s*\d+',  # German: JG 27, StG 2, etc.
        r'\d+°?\s*(Stormo|Gruppo.*Caccia|Gruppo.*Bombardamento)',  # Italian
        r'No\.\s*\d+\s*(Squadron|Wing)',  # British
        r'(SAAF|RAF|RAAF)\s*(No\.)?\s*\d+',  # Commonwealth
    ]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def has_strength_data(text):
    """Check if text contains aircraft strength numbers."""
    patterns = [
        r'\d+\s*(aircraft|planes|serviceable)',  # "23 aircraft"
        r'\d+/\d+',  # "23/18" (total/operational)
        r'(strength|on hand)[:\s]+\d+',  # "Strength: 45"
    ]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def main():
    base_dir = Path("D:/north-africa-toe-builder/Resource Documents/Nafziger Collection/WWII")

    print("Searching Nafziger Collection for air units with strength data...\n")

    # Search 1941-1942 (main period)
    search_dirs = [
        base_dir / "1941-1942/Pt_I_1941-1942",
        base_dir / "1939-1940/Pt_I_1939-1940",
    ]

    already_processed = {
        '941gdmc.pdf', '942game.pdf', '942geme.pdf',
        '942bema.pdf', '942bima.pdf'
    }

    results = {
        'with_strength': [],
        'structure_only': [],
    }

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue

        print(f"Searching: {search_dir.name}")

        pdfs = sorted(search_dir.glob('*.pdf'))
        for i, pdf_path in enumerate(pdfs):
            if pdf_path.name in already_processed:
                continue

            if i % 100 == 0:
                print(f"   Progress: {i}/{len(pdfs)} files...")

            text = extract_pdf_text(pdf_path)

            if has_air_units(text):
                if has_strength_data(text):
                    results['with_strength'].append(pdf_path.name)
                    print(f"   [+] {pdf_path.name} - HAS STRENGTH DATA")
                else:
                    results['structure_only'].append(pdf_path.name)

    print("\n" + "="*60)
    print("SEARCH RESULTS")
    print("="*60)
    print(f"\n[+] PDFs with AIR UNITS + STRENGTH DATA: {len(results['with_strength'])}")
    for fname in results['with_strength'][:20]:  # Show first 20
        print(f"   - {fname}")
    if len(results['with_strength']) > 20:
        print(f"   ... and {len(results['with_strength']) - 20} more")

    print(f"\n[-] PDFs with AIR UNITS but NO STRENGTH: {len(results['structure_only'])}")
    for fname in results['structure_only'][:10]:  # Show first 10
        print(f"   - {fname}")
    if len(results['structure_only']) > 10:
        print(f"   ... and {len(results['structure_only']) - 10} more")

    print(f"\n[*] Already processed (excluded from search): {len(already_processed)}")

    print("\n" + "="*60)
    print("CONCLUSION:")
    if results['with_strength']:
        print(f"[+] Found {len(results['with_strength'])} candidate PDFs for extraction")
    else:
        print("[-] No additional PDFs found with air strength data")
        print("    --> May need to use online sources (AFHRA, RAF Museum, UK Archives)")

if __name__ == '__main__':
    main()
