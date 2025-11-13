#!/usr/bin/env python3
"""
Remove SAMPLE V5 Format Test from all book SUMMARY.md files.
"""

import os
from pathlib import Path

# Books to update
BOOKS = [
    'compass', 'sonnenblume', 'tobruk', 'battleaxe',
    'crusader', 'gazala', 'first_alamein', 'alam_halfa',
    'second_alamein', 'torch', 'tunisia', 'mareth'
]

def remove_sample_line(summary_file):
    """Remove the SAMPLE_DATACARDS_TEST line from SUMMARY.md."""
    with open(summary_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Filter out the SAMPLE line
    new_lines = []
    removed = False
    for line in lines:
        if 'SAMPLE' in line and 'DATACARDS_TEST' in line:
            print(f"    [REMOVED] {line.strip()}")
            removed = True
        else:
            new_lines.append(line)

    if removed:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    return False

def delete_sample_file(sample_file):
    """Delete the SAMPLE_DATACARDS_TEST.md file if it exists."""
    if sample_file.exists():
        sample_file.unlink()
        return True
    return False

def main():
    """Remove sample test from all books."""
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    books_dir = project_root / "books"

    print("=" * 80)
    print("REMOVING SAMPLE V5 FORMAT TEST FROM ALL BOOKS")
    print("=" * 80)
    print()

    removed_count = 0
    deleted_count = 0

    for book in BOOKS:
        book_src = books_dir / book / "book" / "src"
        summary_file = book_src / "SUMMARY.md"
        sample_file = book_src / "chapter2" / "SAMPLE_DATACARDS_TEST.md"

        print(f"Processing: {book}")

        if not summary_file.exists():
            print(f"  [SKIP] SUMMARY.md not found")
            print()
            continue

        # Remove line from SUMMARY.md
        if remove_sample_line(summary_file):
            removed_count += 1
        else:
            print(f"  [SKIP] SAMPLE line not found in SUMMARY.md")

        # Delete sample file
        if delete_sample_file(sample_file):
            print(f"  [DELETED] SAMPLE_DATACARDS_TEST.md")
            deleted_count += 1
        else:
            print(f"  [SKIP] SAMPLE_DATACARDS_TEST.md not found")

        print()

    print("=" * 80)
    print(f"COMPLETE: {removed_count} SUMMARY.md files updated, {deleted_count} sample files deleted")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Rebuild books: python scripts/battlegroup/book/rebuild_all_books.py")
    print("2. Commit and push changes")

if __name__ == '__main__':
    main()
