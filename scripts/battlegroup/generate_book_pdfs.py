#!/usr/bin/env python3
"""
Generate PDF versions of BattleGroup North Africa books from MDBook HTML output.

Uses WeasyPrint to convert the print.html file from each MDBook build to PDF.
"""

import os
import sys
from pathlib import Path
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
BOOKS_DIR = PROJECT_ROOT / "books"

# Book definitions
BOOKS = [
    {
        "name": "battleaxe",
        "title": "Operation Battleaxe",
        "subtitle": "June 1941 - British offensive meets German 88mm guns"
    },
    {
        "name": "crusader",
        "title": "Operation Crusader",
        "subtitle": "November-December 1941 - The largest desert battle"
    },
    {
        "name": "gazala",
        "title": "The Battle of Gazala",
        "subtitle": "May-June 1942 - Grant tanks and the Cauldron"
    },
    {
        "name": "first_alamein",
        "title": "First Battle of El Alamein",
        "subtitle": "July 1942 - Commonwealth diversity stops Rommel"
    }
]

def generate_pdf(book_name, book_title, book_subtitle):
    """Generate PDF for a single book."""

    # Paths
    html_file = BOOKS_DIR / book_name / "book" / "book" / "print.html"
    pdf_output = BOOKS_DIR / book_name / "book" / f"{book_name}.pdf"

    if not html_file.exists():
        print(f"ERROR: HTML file not found: {html_file}")
        return False

    print(f"\nGenerating PDF for {book_title}...")
    print(f"  Input:  {html_file}")
    print(f"  Output: {pdf_output}")

    try:
        # Font configuration for better rendering
        font_config = FontConfiguration()

        # Custom CSS for PDF output
        pdf_css = CSS(string="""
            @page {
                size: letter;
                margin: 0.75in;

                @top-center {
                    content: string(book-title);
                    font-size: 9pt;
                    color: #666;
                }

                @bottom-center {
                    content: counter(page);
                    font-size: 9pt;
                }
            }

            h1 {
                string-set: book-title content();
                page-break-before: always;
            }

            h1:first-of-type {
                page-break-before: avoid;
            }

            table {
                page-break-inside: avoid;
            }

            pre, code {
                page-break-inside: avoid;
            }

            /* Better table styling */
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 1em 0;
            }

            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }

            th {
                background-color: #f2f2f2;
                font-weight: bold;
            }

            /* Scenario boxes */
            .scenario {
                border: 2px solid #333;
                padding: 1em;
                margin: 1em 0;
                page-break-inside: avoid;
            }
        """, font_config=font_config)

        # Generate PDF
        HTML(filename=str(html_file)).write_pdf(
            str(pdf_output),
            stylesheets=[pdf_css],
            font_config=font_config
        )

        # Check file size
        size_mb = pdf_output.stat().st_size / (1024 * 1024)
        print(f"  ✓ Generated: {size_mb:.2f} MB")

        return True

    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False

def main():
    """Generate PDFs for all books."""

    print("=" * 80)
    print("BattleGroup North Africa - PDF Generation")
    print("=" * 80)

    success_count = 0
    total_count = len(BOOKS)

    for book in BOOKS:
        if generate_pdf(book["name"], book["title"], book["subtitle"]):
            success_count += 1

    print("\n" + "=" * 80)
    print(f"PDF Generation Complete: {success_count}/{total_count} books")
    print("=" * 80)

    if success_count < total_count:
        sys.exit(1)

    return 0

if __name__ == "__main__":
    sys.exit(main())
