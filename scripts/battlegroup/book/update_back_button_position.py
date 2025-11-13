#!/usr/bin/env python3
"""
Update back button position to be next to search/print buttons in all books.
"""

from pathlib import Path

# Books to update
BOOKS = [
    'compass', 'sonnenblume', 'tobruk', 'battleaxe',
    'crusader', 'gazala', 'first_alamein', 'alam_halfa',
    'second_alamein', 'torch', 'tunisia', 'mareth'
]

# New custom.js content
NEW_CUSTOM_JS = """// Add "Back to Main Site" button next to search/print buttons
(function() {
    // Wait for DOM to be ready
    window.addEventListener('DOMContentLoaded', function() {
        // Find the right-buttons div in the menu bar
        const rightButtons = document.querySelector('.right-buttons');
        if (!rightButtons) return;

        // Create the back button link
        const backLink = document.createElement('a');
        backLink.href = 'https://sevcavhub.github.io/north-africa-toe-builder/';
        backLink.title = 'Back to Main Site';
        backLink.setAttribute('aria-label', 'Back to Main Site');
        backLink.style.cssText = `
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            color: var(--icons);
            text-decoration: none;
            font-size: 0.875rem;
            padding: 0.25rem 0.5rem;
            margin-right: 0.5rem;
            border-radius: 4px;
            transition: all 0.2s ease;
        `;

        // Add arrow SVG and text
        backLink.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            <span style="font-weight: 500;">Main Site</span>
        `;

        // Add hover effect
        backLink.addEventListener('mouseenter', function() {
            this.style.background = 'var(--sidebar-bg)';
        });

        backLink.addEventListener('mouseleave', function() {
            this.style.background = 'transparent';
        });

        // Insert before the first child (print button)
        rightButtons.insertBefore(backLink, rightButtons.firstChild);
    });
})();
"""

def main():
    """Update custom.js for all books."""
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    books_dir = project_root / "books"

    print("=" * 80)
    print("UPDATING BACK BUTTON POSITION TO MENU BAR")
    print("=" * 80)
    print()

    updated_count = 0

    for book in BOOKS:
        custom_js_file = books_dir / book / "book" / "theme" / "custom.js"

        print(f"Processing: {book}")

        if not custom_js_file.exists():
            print(f"  [SKIP] custom.js not found")
            print()
            continue

        # Write new custom.js
        with open(custom_js_file, 'w', encoding='utf-8') as f:
            f.write(NEW_CUSTOM_JS)

        print(f"  [OK] Updated custom.js - button now in menu bar")
        updated_count += 1
        print()

    print("=" * 80)
    print(f"SUCCESS: Updated {updated_count} books")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Rebuild books: python scripts/battlegroup/book/rebuild_all_books.py")
    print("2. Commit and push changes")

if __name__ == '__main__':
    main()
