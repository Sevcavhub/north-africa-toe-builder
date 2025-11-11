#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copy MDBook structure from battleaxe to incomplete books.

Creates full book scaffolding (SUMMARY.md, chapters, scenarios, etc.) for the 8 books
that currently only have chapter2/ datacards.
"""

import shutil
from pathlib import Path
import re
import sys
import io

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Base directory
BOOKS_DIR = Path("D:/north-africa-toe-builder/books")

# Template book (has complete structure)
TEMPLATE_BOOK = 'battleaxe'

# Incomplete books (need structure)
INCOMPLETE_BOOKS = [
    'compass',
    'sonnenblume',
    'tobruk',
    'alam_halfa',
    'second_alamein',
    'torch',
    'tunisia',
    'mareth'
]

# Battle metadata for customization
BATTLE_METADATA = {
    'compass': {
        'title': 'Operation Compass',
        'quarters': ['1940q4', '1941q1'],
        'period': 'December 1940 - February 1941'
    },
    'sonnenblume': {
        'title': 'Operation Sonnenblume',
        'quarters': ['1941q1'],
        'period': 'February - March 1941'
    },
    'tobruk': {
        'title': 'Siege of Tobruk',
        'quarters': ['1941q2', '1941q3'],
        'period': 'April - November 1941'
    },
    'alam_halfa': {
        'title': 'Battle of Alam Halfa',
        'quarters': ['1942q3'],
        'period': 'August - September 1942'
    },
    'second_alamein': {
        'title': 'Second Battle of El Alamein',
        'quarters': ['1942q4'],
        'period': 'October - November 1942'
    },
    'torch': {
        'title': 'Operation Torch',
        'quarters': ['1942q4'],
        'period': 'November 1942'
    },
    'tunisia': {
        'title': 'Tunisia Campaign',
        'quarters': ['1943q1'],
        'period': 'November 1942 - May 1943'
    },
    'mareth': {
        'title': 'Battle of Mareth Line',
        'quarters': ['1943q1'],
        'period': 'March 1943'
    }
}

def customize_file_content(content: str, battle_key: str, template_name: str) -> str:
    """
    Customize file content by replacing battle-specific references.

    Args:
        content: Original file content
        battle_key: Battle identifier (e.g., 'compass')
        template_name: Original battle name (e.g., 'battleaxe')

    Returns:
        Customized content
    """
    metadata = BATTLE_METADATA[battle_key]

    # Replace title references
    content = content.replace('Operation Battleaxe', metadata['title'])
    content = content.replace('Battleaxe', metadata['title'])
    content = content.replace('battleaxe', battle_key)

    # Update period if mentioned
    if 'June 1941' in content:
        content = content.replace('June 1941', metadata['period'])

    return content

def copy_book_structure(template_book: str, target_book: str):
    """
    Copy complete MDBook structure from template to target book.

    Args:
        template_book: Source book with complete structure
        target_book: Target book to populate
    """
    template_dir = BOOKS_DIR / template_book / 'book'
    target_dir = BOOKS_DIR / target_book / 'book'

    print(f"\n{'='*80}")
    print(f"Copying structure: {template_book} → {target_book}")
    print(f"{'='*80}")

    # Ensure target directory exists
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy book.toml
    template_toml = template_dir / 'book.toml'
    target_toml = target_dir / 'book.toml'

    if template_toml.exists():
        with open(template_toml, 'r', encoding='utf-8') as f:
            toml_content = f.read()

        # Customize book.toml
        toml_content = customize_file_content(toml_content, target_book, template_book)

        with open(target_toml, 'w', encoding='utf-8') as f:
            f.write(toml_content)

        print(f"✓ Copied and customized book.toml")

    # Copy src directory structure (except chapter2 which already exists)
    template_src = template_dir / 'src'
    target_src = target_dir / 'src'

    # Ensure target src exists
    target_src.mkdir(parents=True, exist_ok=True)

    # Directories to copy
    dirs_to_copy = [
        'chapter1',
        'scenarios',
        'army_lists',
        'special_rules',
        'appendices'
    ]

    # Individual files at src root
    files_to_copy = [
        'SUMMARY.md',
        'intro.md'
    ]

    # Copy directories
    for dir_name in dirs_to_copy:
        template_subdir = template_src / dir_name
        target_subdir = target_src / dir_name

        if template_subdir.exists():
            # Remove if exists (to ensure clean copy)
            if target_subdir.exists():
                shutil.rmtree(target_subdir)

            # Copy entire directory
            shutil.copytree(template_subdir, target_subdir)

            # Customize all .md files in this directory
            for md_file in target_subdir.rglob('*.md'):
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                customized = customize_file_content(content, target_book, template_book)

                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(customized)

            print(f"✓ Copied {dir_name}/ ({len(list(target_subdir.rglob('*.md')))} markdown files)")

    # Copy individual files
    for file_name in files_to_copy:
        template_file = template_src / file_name
        target_file = target_src / file_name

        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()

            customized = customize_file_content(content, target_book, template_book)

            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(customized)

            print(f"✓ Copied and customized {file_name}")

    # Copy chapter2 files that don't exist yet (preserve existing datacards)
    template_ch2 = template_src / 'chapter2'
    target_ch2 = target_src / 'chapter2'

    if template_ch2.exists() and target_ch2.exists():
        # Copy only missing files (don't overwrite existing datacards)
        for template_file in template_ch2.glob('*.md'):
            target_file = target_ch2 / template_file.name

            if not target_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                customized = customize_file_content(content, target_book, template_book)

                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(customized)

                print(f"✓ Copied chapter2/{template_file.name}")

    print(f"✅ Structure copy complete for {target_book}")

def main():
    """Copy book structure to all incomplete books."""
    print("\n" + "="*80)
    print("COPYING MDBOOK STRUCTURE TO INCOMPLETE BOOKS")
    print("="*80)
    print(f"Template: {TEMPLATE_BOOK}")
    print(f"Targets: {', '.join(INCOMPLETE_BOOKS)}")

    for book in INCOMPLETE_BOOKS:
        copy_book_structure(TEMPLATE_BOOK, book)

    print("\n" + "="*80)
    print("✅ ALL STRUCTURE COPIES COMPLETE")
    print("="*80)
    print(f"\nCreated full MDBook structure for {len(INCOMPLETE_BOOKS)} books:")
    for book in INCOMPLETE_BOOKS:
        metadata = BATTLE_METADATA[book]
        print(f"  - {book}: {metadata['title']} ({metadata['period']})")

    print("\nNext step: Run build_all_books.py to build HTML for all 12 books")

if __name__ == '__main__':
    main()
