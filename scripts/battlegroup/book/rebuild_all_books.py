#!/usr/bin/env python3
"""
Rebuild all MDBook books with updated navigation.
"""

import subprocess
from pathlib import Path

# Books to rebuild
BOOKS = [
    'compass', 'sonnenblume', 'tobruk', 'battleaxe',
    'crusader', 'gazala', 'first_alamein', 'alam_halfa',
    'second_alamein', 'torch', 'tunisia', 'mareth'
]

def main():
    """Rebuild all books."""
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    books_dir = project_root / "books"

    print("=" * 80)
    print("REBUILDING ALL BOOKS WITH NEW NAVIGATION")
    print("=" * 80)
    print()

    success_count = 0
    fail_count = 0

    for book in BOOKS:
        book_path = books_dir / book / "book"

        print(f"Rebuilding: {book}")
        print(f"  Path: {book_path}")

        try:
            # Run mdbook build
            result = subprocess.run(
                ["mdbook", "build"],
                cwd=str(book_path),
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print(f"  [OK] Build successful")
                success_count += 1
            else:
                print(f"  [ERROR] Build failed:")
                print(f"    {result.stderr[:200]}")
                fail_count += 1
        except FileNotFoundError:
            print(f"  [ERROR] mdbook not found - install with: cargo install mdbook")
            fail_count += 1
        except subprocess.TimeoutExpired:
            print(f"  [ERROR] Build timed out after 60 seconds")
            fail_count += 1
        except Exception as e:
            print(f"  [ERROR] {e}")
            fail_count += 1

        print()

    print("=" * 80)
    print(f"REBUILD COMPLETE: {success_count} succeeded, {fail_count} failed")
    print("=" * 80)

if __name__ == '__main__':
    main()
