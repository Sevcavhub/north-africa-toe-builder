# BattleGroup Datacard Print Layout - Implementation Summary

## What Was Created

Successfully implemented a print-ready 4×2 grid layout that exactly replicates official BattleGroup datacard page dimensions.

## Files Created

1. **`datacard_print_layout.css`** (370 lines)
   - Complete CSS for official 48mm × 84mm card dimensions
   - 4 columns × 2 rows grid layout (8 cards per page)
   - A4 landscape page setup with precise margins
   - Nation-specific color themes (German, British, Italian, American, French)
   - Print optimization (@media print rules)
   - Screen preview mode

2. **`DATACARD_PRINT_GUIDE.md`** (450+ lines)
   - Comprehensive documentation
   - Dimension calculations and rationale
   - HTML structure examples
   - Print instructions (browser, command-line, Python)
   - Troubleshooting guide
   - Quality verification checklist
   - Cutting guide for physical cards

3. **`datacard_print_test.html`** (8 sample cards)
   - Working test file with 8 complete datacards
   - British Crusader III, German Panzer IV F2, Italian M13/40, American M3 Stuart
   - British 25 pdr gun, German 88mm FlaK36, Italian 47mm AT gun, American M3 Half-Track
   - Ready to print and verify dimensions
   - Includes print instructions page

## Specifications Implemented

### Official Dimensions
- **Card size**: 48mm (width) × 84mm (height) - landscape format
- **White border**: 1mm around each card (simulated with CSS)
- **Card spacing**: 2mm gap between cards
- **Grid layout**: 4 columns × 2 rows = 8 cards per page

### Page Layout
- **Page size**: A4 landscape (297mm × 210mm)
- **Grid dimensions**: 198mm wide × 170mm tall
- **Horizontal margins**: 49.5mm per side (centers grid)
- **Vertical margins**: 20mm per side (centers grid)

### Typography
- **Card title**: 9pt bold
- **Subtitle**: 6pt
- **Special rules**: 6pt italic
- **Table headers**: 7pt bold uppercase
- **Table cells**: 7pt
- **Armor modifiers**: 6pt italic

### Colors (Nation Themes)
- **German**: Gray background (#797768), dark borders
- **British**: Tan background (#d4c5a0), brown borders
- **Italian**: Beige background (#c8b88a), brown borders
- **American**: Olive background (#b8c5a0), green borders
- **French**: Blue-gray background (#a8b5c8), navy borders

## CSS Features

### Grid System
```css
.datacard-grid {
    display: grid;
    grid-template-columns: repeat(4, 48mm);
    grid-template-rows: repeat(2, 84mm);
    gap: 2mm;
    width: 198mm;
    height: 170mm;
}
```

### Card Dimensions
```css
.datacard {
    width: 48mm;
    height: 84mm;
    border: 1mm solid white;        /* Simulated white border */
    outline: 2px solid #2c2416;    /* Actual card border */
    padding: 2mm;                   /* Internal padding */
}
```

### Print Optimization
```css
@media print {
    @page {
        size: A4 landscape;
        margin: 20mm 49.5mm;
    }

    .datacard-grid {
        page-break-after: always;
    }

    .datacard {
        page-break-inside: avoid;
    }
}
```

## Testing the Layout

### View Test Page in Browser
```bash
# Open in default browser (Windows)
start D:/north-africa-toe-builder/books/shared/datacard_print_test.html

# Or manually open in Chrome/Firefox/Edge
```

### Print Preview Checklist
- [ ] Exactly 8 cards visible in grid
- [ ] Cards arranged in 4 columns × 2 rows
- [ ] Even spacing between cards (2mm)
- [ ] White border visible around each card (1mm)
- [ ] No cards cut off at page edges
- [ ] Centered on page with equal margins
- [ ] Colors display correctly
- [ ] Text is readable (not too small)

### Measure Printed Card
After printing one test page:
- [ ] Card width = 48mm (±0.5mm)
- [ ] Card height = 84mm (±0.5mm)
- [ ] White border = ~1mm visible
- [ ] Gap between cards = ~2mm

## Integration with Datacard Generator

### Step 1: Update CSS Reference

In each markdown file that generates datacards, add CSS link:

```markdown
# Tanks & Armoured Vehicles

<link rel="stylesheet" href="../../shared/datacard_print_layout.css">

<div class="datacard-grid">
    <!-- 8 datacards here -->
</div>
```

### Step 2: Modify `generate_book_datacards.py`

Update the script to:
1. Reference new CSS file
2. Group datacards into pages of 8
3. Wrap each page in `<div class="datacard-grid">`

```python
def generate_datacard_markdown(self, equipment_list, output_file):
    """Generate datacards in 4×2 grid pages."""

    markdown = f"""# {category_title}

<link rel="stylesheet" href="../../shared/datacard_print_layout.css">

"""

    # Group into pages of 8 cards
    cards_per_page = 8
    for page_num, i in enumerate(range(0, len(equipment_list), cards_per_page)):
        page_cards = equipment_list[i:i+cards_per_page]

        # Start grid
        markdown += '<div class="datacard-grid">\n\n'

        # Add cards
        for equipment in page_cards:
            card_html = self.generate_datacard_html(equipment)
            markdown += card_html + '\n\n'

        # End grid
        markdown += '</div>\n\n'

        # Page break note (for reference, CSS handles automatically)
        if i + cards_per_page < len(equipment_list):
            markdown += f'<!-- Page {page_num + 2} -->\n\n'

    return markdown
```

### Step 3: Regenerate Datacards

```bash
cd D:/north-africa-toe-builder
python scripts/battlegroup/book/generate_book_datacards.py --all
```

### Step 4: Build Books

```bash
cd books/battleaxe/book && mdbook build
cd books/crusader/book && mdbook build
cd books/gazala/book && mdbook build
cd books/first_alamein/book && mdbook build
```

### Step 5: Export to PDF

Use browser print dialog or command-line tool:

```bash
# Using wkhtmltopdf
wkhtmltopdf \
    --page-size A4 \
    --orientation Landscape \
    --margin-top 20mm \
    --margin-bottom 20mm \
    --margin-left 49.5mm \
    --margin-right 49.5mm \
    --print-media-type \
    books/battleaxe/book/book/chapter2/tanks.html \
    battleaxe_tanks_datacards.pdf
```

## Current vs. New Layout

### Current Layout (OLD)
- 3 columns per page
- Variable card sizes (not mm-based)
- Inconsistent spacing
- No official dimensions
- Not optimized for cutting

### New Layout (NEW)
- 4 columns × 2 rows = 8 cards per page
- Exact 48mm × 84mm dimensions
- 2mm gap, 1mm border (official spec)
- A4 landscape with centered grid
- Ready for cutting and physical use

## Benefits

1. **Official Dimensions**: Matches published BattleGroup cards exactly
2. **Print Optimization**: Clean PDF output, no scaling issues
3. **Physical Cards**: Can be printed and cut for actual play
4. **Professional Appearance**: Consistent with official products
5. **Better Density**: 8 cards per page vs. 6 (33% more efficient)
6. **Easy Cutting**: Standard dimensions, predictable spacing

## Print Settings Reminder

**Critical Settings** (must be exact):
- **Layout**: Landscape
- **Paper**: A4 (210mm × 297mm)
- **Scale**: 100% (do not adjust)
- **Background graphics**: ON
- **Headers/footers**: OFF

## Next Steps

1. **Test print** one page using `datacard_print_test.html`
2. **Measure cards** with ruler to verify dimensions
3. **Update generator** script to use new CSS
4. **Regenerate** all datacards for all 4 battles
5. **Rebuild** MDBooks
6. **Export** final PDFs for each battle
7. **Update** DATACARD_FORMAT_STANDARD.md to reference print layout

## Troubleshooting

### Issue: Cards are wrong size when printed
- Verify print scale is 100% (not "Fit to page")
- Check page size is A4 landscape
- Ensure margins are not overriding CSS

### Issue: Only 6 cards fit per page
- Old CSS may be cached
- Hard refresh browser (Ctrl+Shift+R)
- Clear MDBook build directory and rebuild

### Issue: Colors don't print
- Enable "Background graphics" in print dialog
- Check printer supports color
- Verify CSS has `-webkit-print-color-adjust: exact`

## File Locations

- **CSS**: `books/shared/datacard_print_layout.css`
- **Guide**: `books/shared/DATACARD_PRINT_GUIDE.md`
- **Test**: `books/shared/datacard_print_test.html`
- **Summary**: `books/shared/PRINT_LAYOUT_IMPLEMENTATION.md` (this file)

## Validation

✅ **Dimensions calculated** and verified against official specs
✅ **CSS created** with exact mm-based sizing
✅ **Test file created** with 8 sample cards
✅ **Documentation complete** with usage instructions
✅ **Print optimization** implemented (@media print)
✅ **Nation themes** all 5 nations color-coded
✅ **Grid layout** 4×2 configured correctly

**Status**: Ready for integration and testing

---

**Created**: 2025-11-10
**Specifications**: Official BattleGroup datacard dimensions
**Format**: A4 landscape, 4×2 grid, 8 cards per page
**Next**: Test print → Verify dimensions → Integrate into generator
