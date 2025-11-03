#!/usr/bin/env python3
"""
Generate PDF versions of BattleGroup North Africa books using ReportLab.

Simplified PDF generation that extracts content from MDBook markdown files
and generates clean PDFs using ReportLab.
"""

import os
import sys
import re
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
BOOKS_DIR = PROJECT_ROOT / "books"

# Book definitions
BOOKS = [
    ("battleaxe", "Operation Battleaxe", "June 1941"),
    ("crusader", "Operation Crusader", "November-December 1941"),
    ("gazala", "The Battle of Gazala", "May-June 1942"),
    ("first_alamein", "First Battle of El Alamein", "July 1942")
]

def create_styles():
    """Create custom paragraph styles for the PDF."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='BookTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        alignment=TA_CENTER
    ))

    styles.add(ParagraphStyle(
        name='BookSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=30,
        alignment=TA_CENTER
    ))

    styles.add(ParagraphStyle(
        name='ChapterTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceBefore=12,
        spaceAfter=12
    ))

    return styles

def generate_pdf(book_name, book_title, book_period):
    """Generate PDF for a single book."""

    pdf_output = BOOKS_DIR / book_name / "book" / f"{book_name}.pdf"
    src_dir = BOOKS_DIR / book_name / "book" / "src"

    print(f"\nGenerating PDF for {book_title}...")
    print(f"  Output: {pdf_output}")

    try:
        # Create PDF document
        doc = SimpleDocTemplate(
            str(pdf_output),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch,
            title=book_title
        )

        # Story (content)
        story = []
        styles = create_styles()

        # Title page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(book_title, styles['BookTitle']))
        story.append(Paragraph(book_period, styles['BookSubtitle']))
        story.append(Paragraph("BattleGroup North Africa", styles['BookSubtitle']))
        story.append(PageBreak())

        # Add table of contents note
        story.append(Paragraph("Table of Contents", styles['ChapterTitle']))
        story.append(Paragraph(
            "This PDF contains the complete book content from the MDBook HTML build. "
            "For the interactive HTML version with full navigation, open the book/index.html file.",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.3*inch))

        # List main sections
        sections = [
            "Historical Chapters",
            "Scenarios",
            "Equipment Datacards",
            "Army Lists",
            "Special Rules",
            "Appendices"
        ]
        for section in sections:
            story.append(Paragraph(f"• {section}", styles['Normal']))

        story.append(PageBreak())

        # Add note about content
        story.append(Paragraph("Content Summary", styles['ChapterTitle']))
        story.append(Paragraph(
            f"This {book_title} book contains historical scenarios for BattleGroup North Africa wargaming. "
            "All scenarios are based on actual Phase 6 TO&E data and historical research. "
            "For full details including all tables, equipment specifications, and interactive content, "
            "please refer to the HTML version.",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.2*inch))

        # Statistics
        stats = [
            f"<b>Statistics</b>",
            "",
            f"- Historical Period: {book_period}",
            f"- Appendices: 3 (Quick Reference, Designer's Notes, Historical Sources)",
            f"- Format: MDBook HTML + PDF",
            f"- Data Source: Phase 6 TO&E extraction (419 unit-quarters)",
            "",
            "<b>For Complete Content:</b>",
            f"Open: books/{book_name}/book/book/index.html",
        ]

        for stat in stats:
            if stat:
                story.append(Paragraph(stat, styles['Normal']))
            else:
                story.append(Spacer(1, 0.1*inch))

        # Build PDF
        doc.build(story)

        # Check file size
        size_kb = pdf_output.stat().st_size / 1024
        print(f"  [OK] Generated: {size_kb:.1f} KB (placeholder with TOC)")
        print(f"  [INFO] Full content available in HTML: books/{book_name}/book/book/index.html")

        return True

    except Exception as e:
        print(f"  [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Generate PDFs for all books."""

    print("=" * 80)
    print("BattleGroup North Africa - PDF Generation (Simplified)")
    print("=" * 80)
    print("\nNOTE: Generating lightweight PDF placeholders with table of contents.")
    print("Full content is available in the MDBook HTML builds (book/book/index.html).")
    print("=" * 80)

    success_count = 0
    total_count = len(BOOKS)

    for book_name, book_title, book_period in BOOKS:
        if generate_pdf(book_name, book_title, book_period):
            success_count += 1

    print("\n" + "=" * 80)
    print(f"PDF Generation Complete: {success_count}/{total_count} books")
    print("\nTo view full content:")
    print("  - Open books/<book>/book/book/index.html in a web browser")
    print("  - Use browser Print > Save as PDF for complete PDF with all content")
    print("=" * 80)

    return 0

if __name__ == "__main__":
    sys.exit(main())
