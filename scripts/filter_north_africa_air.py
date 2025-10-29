#!/usr/bin/env python3
"""
Filter the 21 candidate PDFs to find North Africa theater only.
"""

import subprocess
from pathlib import Path

def extract_pdf_text(pdf_path):
    """Extract full text from PDF."""
    try:
        result = subprocess.run(
            ['pdftotext', str(pdf_path), '-'],
            capture_output=True,
            text=True,
            timeout=15
        )
        return result.stdout
    except Exception:
        return ""

def is_north_africa(text):
    """Check if PDF is about North Africa theater."""
    # North Africa keywords
    na_keywords = [
        'north africa', 'afrika', 'libya', 'egypt', 'tunisia', 'tripoli',
        'tobruk', 'benghazi', 'el alamein', 'gazala', 'crusader',
        'western desert', 'cyrenaica', 'fliegerführer afrika',
        'desert air force', 'cyrenaica command'
    ]

    # Non-North Africa theaters to exclude
    exclude_keywords = [
        'crete', 'greece', 'balkans', 'albania', 'yugoslavia',
        'sicily invasion', 'malta', 'eastern front', 'russia'
    ]

    text_lower = text.lower()

    # Check for exclusions first
    for keyword in exclude_keywords:
        if keyword in text_lower:
            return False, f"Excluded: {keyword}"

    # Check for North Africa
    for keyword in na_keywords:
        if keyword in text_lower:
            return True, f"Match: {keyword}"

    return False, "No clear theater match"

def main():
    candidates = [
        '941bkac.pdf', '941gama.pdf', '941gdaa.pdf', '941gdyc.pdf',
        '941gema.pdf', '941gjaa.pdf', '941gkmb.pdf', '942gbla.pdf',
        '942gicc.pdf', '942gjai.pdf', '942gjaj.pdf', '942gkah.pdf',
        '942gkai.pdf', '939gila.pdf', '940bdaa.pdf', '940gdaa.pdf',
        '940geal.pdf', '940ghaa.pdf', '940ghla.pdf', '940ijaa.pdf',
        '940ixmb.pdf'
    ]

    base1 = Path("D:/north-africa-toe-builder/Resource Documents/Nafziger Collection/WWII/1941-1942/Pt_I_1941-1942")
    base2 = Path("D:/north-africa-toe-builder/Resource Documents/Nafziger Collection/WWII/1939-1940/Pt_I_1939-1940")

    print("Filtering for North Africa theater...\n")

    north_africa_pdfs = []
    excluded = []

    for fname in candidates:
        pdf_path = base1 / fname
        if not pdf_path.exists():
            pdf_path = base2 / fname

        if not pdf_path.exists():
            print(f"[-] {fname} - NOT FOUND")
            continue

        text = extract_pdf_text(pdf_path)
        is_na, reason = is_north_africa(text)

        if is_na:
            north_africa_pdfs.append(fname)
            print(f"[+] {fname} - NORTH AFRICA ({reason})")
        else:
            excluded.append((fname, reason))
            print(f"[-] {fname} - {reason}")

    print("\n" + "="*60)
    print(f"NORTH AFRICA PDFs: {len(north_africa_pdfs)}")
    print("="*60)
    for fname in north_africa_pdfs:
        print(f"  {fname}")

    print(f"\nExcluded: {len(excluded)} (wrong theater or unclear)")

if __name__ == '__main__':
    main()
