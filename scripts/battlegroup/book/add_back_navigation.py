#!/usr/bin/env python3
"""
Add 'Back to Main Site' navigation button to all MDBook books.

Creates theme/header.html with a custom navigation button that appears
at the top of every page in each book.
"""

import os
from pathlib import Path

# Books to update
BOOKS = [
    'compass', 'sonnenblume', 'tobruk', 'battleaxe',
    'crusader', 'gazala', 'first_alamein', 'alam_halfa',
    'second_alamein', 'torch', 'tunisia', 'mareth'
]

# Custom header HTML
HEADER_HTML = """<!-- Custom navigation header -->
<div style="background: linear-gradient(135deg, #4A5335 0%, #6B7F3D 100%);
            padding: 0.5rem 1rem;
            margin: -1rem -1rem 1rem -1rem;
            border-bottom: 3px solid #C9A77C;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    <a href="https://sevcavhub.github.io/north-africa-toe-builder/"
       style="display: inline-flex;
              align-items: center;
              gap: 0.5rem;
              color: white;
              text-decoration: none;
              font-weight: 600;
              font-size: 0.95rem;
              padding: 0.5rem 1rem;
              background: rgba(255,255,255,0.1);
              border-radius: 4px;
              border: 2px solid rgba(255,255,255,0.3);
              transition: all 0.3s ease;">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        <span>Back to Main Site</span>
    </a>
</div>

<style>
    /* Hover effect for back button */
    div[style*="background: linear-gradient"] a:hover {
        background: rgba(255,255,255,0.2) !important;
        border-color: rgba(255,255,255,0.5) !important;
        transform: translateX(-2px);
    }

    /* Ensure button works on mobile */
    @media (max-width: 768px) {
        div[style*="background: linear-gradient"] {
            padding: 0.5rem !important;
        }
        div[style*="background: linear-gradient"] a {
            font-size: 0.85rem !important;
            padding: 0.4rem 0.8rem !important;
        }
    }
</style>
"""

def main():
    """Add back navigation to all books."""
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    books_dir = project_root / "books"

    print("=" * 80)
    print("ADDING BACK NAVIGATION TO ALL BOOKS")
    print("=" * 80)
    print()

    for book in BOOKS:
        book_path = books_dir / book / "book"
        theme_dir = book_path / "theme"
        header_file = theme_dir / "header.html"

        print(f"Processing: {book}")

        # Create theme directory if it doesn't exist
        if not theme_dir.exists():
            theme_dir.mkdir(parents=True, exist_ok=True)
            print(f"  [OK] Created theme directory: {theme_dir}")

        # Write header.html
        with open(header_file, 'w', encoding='utf-8') as f:
            f.write(HEADER_HTML)
        print(f"  [OK] Created header.html: {header_file}")
        print()

    print("=" * 80)
    print(f"SUCCESS: Added back navigation to {len(BOOKS)} books")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Rebuild books: cd books/[battle]/book && mdbook build")
    print("2. Test locally by opening books/[battle]/book/book/index.html")
    print("3. Commit and push to deploy to GitHub Pages")

if __name__ == '__main__':
    main()
