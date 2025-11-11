#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build all 12 North Africa battle books (MDBook HTML output).

Runs 'mdbook build' for each book directory to generate HTML from markdown sources.
"""

import subprocess
from pathlib import Path
import sys
import os

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Base directory
BASE_DIR = Path("D:/north-africa-toe-builder/books")

# All 12 battle books
BATTLES = [
    'compass',
    'sonnenblume',
    'tobruk',
    'battleaxe',
    'crusader',
    'gazala',
    'first_alamein',
    'alam_halfa',
    'second_alamein',
    'torch',
    'tunisia',
    'mareth'
]

def build_book(battle_name: str) -> bool:
    """
    Build a single book using mdbook.

    Args:
        battle_name: Name of the battle (e.g., 'battleaxe')

    Returns:
        True if build succeeded, False otherwise
    """
    book_dir = BASE_DIR / battle_name / 'book'

    if not book_dir.exists():
        print(f"❌ Book directory not found: {book_dir}")
        return False

    print(f"\n{'='*80}")
    print(f"Building: {battle_name.replace('_', ' ').title()}")
    print(f"Directory: {book_dir}")
    print(f"{'='*80}")

    try:
        # Run mdbook build
        result = subprocess.run(
            ['mdbook', 'build'],
            cwd=book_dir,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print(f"✅ SUCCESS: {battle_name}")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ FAILED: {battle_name}")
            print(f"Error: {result.stderr}")
            return False

    except FileNotFoundError:
        print(f"❌ ERROR: mdbook command not found")
        print(f"Please install mdbook: https://rust-lang.github.io/mdBook/guide/installation.html")
        return False

    except subprocess.TimeoutExpired:
        print(f"❌ TIMEOUT: {battle_name} build took longer than 60 seconds")
        return False

    except Exception as e:
        print(f"❌ ERROR: {battle_name} - {e}")
        return False

def main():
    """Build all battle books."""
    print("\n" + "="*80)
    print("BUILDING ALL 12 NORTH AFRICA BATTLE BOOKS")
    print("="*80)

    successes = []
    failures = []

    for battle in BATTLES:
        if build_book(battle):
            successes.append(battle)
        else:
            failures.append(battle)

    # Summary
    print("\n" + "="*80)
    print("BUILD SUMMARY")
    print("="*80)
    print(f"✅ Successful: {len(successes)}/{len(BATTLES)}")
    for battle in successes:
        print(f"   - {battle}")

    if failures:
        print(f"\n❌ Failed: {len(failures)}/{len(BATTLES)}")
        for battle in failures:
            print(f"   - {battle}")
        sys.exit(1)
    else:
        print(f"\n🎉 All {len(BATTLES)} books built successfully!")
        print(f"\nHTML output locations:")
        for battle in BATTLES:
            html_dir = BASE_DIR / battle / 'book' / 'book'
            index_file = html_dir / 'index.html'
            if index_file.exists():
                print(f"   {battle}: {index_file}")

        sys.exit(0)

if __name__ == '__main__':
    main()
