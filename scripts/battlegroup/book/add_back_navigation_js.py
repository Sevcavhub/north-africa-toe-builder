#!/usr/bin/env python3
"""
Add JavaScript-based 'Back to Main Site' navigation to all books.

Creates theme/custom.js and updates book.toml to include it.
"""

import os
import re
from pathlib import Path

# Books to update
BOOKS = [
    'compass', 'sonnenblume', 'tobruk', 'battleaxe',
    'crusader', 'gazala', 'first_alamein', 'alam_halfa',
    'second_alamein', 'torch', 'tunisia', 'mareth'
]

# Custom JavaScript
CUSTOM_JS = """// Add "Back to Main Site" button to the top of each page
(function() {
    // Wait for DOM to be ready
    window.addEventListener('DOMContentLoaded', function() {
        // Find the main content div
        const contentDiv = document.getElementById('content');
        if (!contentDiv) return;

        // Create the navigation header
        const navHeader = document.createElement('div');
        navHeader.style.cssText = `
            background: linear-gradient(135deg, #4A5335 0%, #6B7F3D 100%);
            padding: 0.5rem 1rem;
            margin: -1rem -1rem 1rem -1rem;
            border-bottom: 3px solid #C9A77C;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;

        // Create the back button
        const backLink = document.createElement('a');
        backLink.href = 'https://sevcavhub.github.io/north-africa-toe-builder/';
        backLink.style.cssText = `
            display: inline-flex;
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
            transition: all 0.3s ease;
        `;

        // Add arrow SVG
        backLink.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            <span>Back to Main Site</span>
        `;

        // Add hover effect
        backLink.addEventListener('mouseenter', function() {
            this.style.background = 'rgba(255,255,255,0.2)';
            this.style.borderColor = 'rgba(255,255,255,0.5)';
            this.style.transform = 'translateX(-2px)';
        });

        backLink.addEventListener('mouseleave', function() {
            this.style.background = 'rgba(255,255,255,0.1)';
            this.style.borderColor = 'rgba(255,255,255,0.3)';
            this.style.transform = 'translateX(0)';
        });

        // Assemble and inject
        navHeader.appendChild(backLink);
        contentDiv.insertBefore(navHeader, contentDiv.firstChild);
    });
})();
"""

def update_book_toml(book_toml_path):
    """Update book.toml to include custom.js."""
    with open(book_toml_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already configured
    if 'theme/custom.js' in content:
        return False  # Already updated

    # Add theme configuration if not present
    if 'theme = "theme"' not in content:
        content = re.sub(
            r'(\[output\.html\][^\[]*)',
            r'\1theme = "theme"\n',
            content
        )

    # Add additional-js if not present
    if 'additional-js' not in content:
        content = re.sub(
            r'(\[output\.html\][^\[]*)',
            r'\1additional-js = ["theme/custom.js"]\n',
            content
        )
    else:
        # Modify existing additional-js
        content = re.sub(
            r'additional-js = \[\]',
            r'additional-js = ["theme/custom.js"]',
            content
        )

    with open(book_toml_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True  # Updated

def main():
    """Add back navigation to all books."""
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    books_dir = project_root / "books"

    print("=" * 80)
    print("ADDING JAVASCRIPT BACK NAVIGATION TO ALL BOOKS")
    print("=" * 80)
    print()

    for book in BOOKS:
        book_path = books_dir / book / "book"
        theme_dir = book_path / "theme"
        custom_js_file = theme_dir / "custom.js"
        book_toml_file = book_path / "book.toml"

        print(f"Processing: {book}")

        # Create theme directory if it doesn't exist
        if not theme_dir.exists():
            theme_dir.mkdir(parents=True, exist_ok=True)
            print(f"  [OK] Created theme directory")

        # Write custom.js
        with open(custom_js_file, 'w', encoding='utf-8') as f:
            f.write(CUSTOM_JS)
        print(f"  [OK] Created custom.js")

        # Update book.toml
        if update_book_toml(book_toml_file):
            print(f"  [OK] Updated book.toml")
        else:
            print(f"  [SKIP] book.toml already configured")

        print()

    print("=" * 80)
    print(f"SUCCESS: Added back navigation to {len(BOOKS)} books")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Rebuild books: python scripts/battlegroup/book/rebuild_all_books.py")
    print("2. Test locally by opening books/[battle]/book/book/index.html")
    print("3. Commit and push to deploy to GitHub Pages")

if __name__ == '__main__':
    main()
