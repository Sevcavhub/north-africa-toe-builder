# BattleGroup Datacard Print Layout Guide

## Official Specifications

Replicates the exact dimensions from official BattleGroup datacard pages:

- **Card size**: 48mm (width) × 84mm (height) - **landscape format**
- **White border**: 1mm around each card
- **Padding between cards**: 2mm
- **Grid layout**: 4 columns × 2 rows = **8 cards per page**
- **Page size**: A4 landscape (297mm × 210mm)
- **Page margins**: 49.5mm horizontal, 20mm vertical (centers the grid)

## Page Layout Calculations

```
Total grid width:  (48mm × 4 cards) + (2mm × 3 gaps) = 198mm
Total grid height: (84mm × 2 rows)  + (2mm × 1 gap)  = 170mm

A4 landscape: 297mm × 210mm
Horizontal margins: (297mm - 198mm) / 2 = 49.5mm per side
Vertical margins:   (210mm - 170mm) / 2 = 20mm per side
```

## HTML Structure

### Method 1: Single Page (8 cards)

```html
<div class="datacard-grid">
    <!-- Card 1 -->
    <div class="datacard datacard-british">
        <div class="datacard-header">
            <div class="datacard-silhouette">🔲</div>
            <div class="datacard-title-block">
                <p class="datacard-title">CRUSADER III</p>
                <p class="datacard-subtitle">1942 | Cruiser Tank</p>
                <p class="datacard-special-rules">Fast, Recce</p>
            </div>
        </div>
        <table>
            <!-- Vehicle stats table -->
        </table>
        <table>
            <!-- Weapon performance table -->
        </table>
    </div>

    <!-- Cards 2-8 -->
    <!-- ... -->
</div>
```

### Method 2: Multiple Pages

```html
<!-- Page 1 -->
<div class="datacard-grid">
    <!-- 8 cards -->
</div>

<!-- Page 2 -->
<div class="datacard-grid">
    <!-- 8 more cards -->
</div>
```

The CSS automatically handles page breaks between `.datacard-grid` containers.

## CSS Integration

### For MDBook Projects

Add to your markdown file header:

```markdown
# Equipment Datacards

<link rel="stylesheet" href="../../shared/datacard_print_layout.css">

<div class="datacard-grid">
    <!-- Your 8 datacards here -->
</div>
```

### For Standalone HTML

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>BattleGroup Datacards</title>
    <link rel="stylesheet" href="datacard_print_layout.css">
</head>
<body>
    <div class="datacard-grid">
        <!-- Your datacards -->
    </div>
</body>
</html>
```

## Printing Instructions

### From Browser

1. **Open the HTML page** in Chrome, Firefox, or Edge
2. **Print Settings**:
   - **Layout**: Landscape
   - **Paper size**: A4 (210mm × 297mm)
   - **Margins**: Custom (or use CSS-defined margins)
   - **Scale**: 100% (critical - do not adjust)
   - **Background graphics**: ON (to print colors)
   - **Headers and footers**: OFF

3. **Verify Preview**:
   - Should see exactly 8 cards in 4×2 grid
   - Cards should fill most of the page with even margins
   - No cards cut off or wrapping

4. **Print or Save as PDF**

### From Command Line (wkhtmltopdf)

```bash
wkhtmltopdf \
    --page-size A4 \
    --orientation Landscape \
    --margin-top 20mm \
    --margin-bottom 20mm \
    --margin-left 49.5mm \
    --margin-right 49.5mm \
    --print-media-type \
    --enable-local-file-access \
    datacards.html datacards.pdf
```

### From Python (weasyprint)

```python
from weasyprint import HTML, CSS

HTML('datacards.html').write_pdf(
    'datacards.pdf',
    stylesheets=[CSS('datacard_print_layout.css')]
)
```

## Screen Preview

The CSS includes screen-specific styles that show a print preview with:
- A4 page boundary visualization
- Same layout as printed output
- Helpful for alignment verification before printing

To disable preview styling, wrap your content:

```html
<div class="datacard-page-container">
    <div class="datacard-grid">
        <!-- Cards -->
    </div>
</div>
```

## Font Sizing

Default font sizes optimized for 48mm × 84mm cards:

- **Card title**: 9pt bold
- **Subtitle**: 6pt
- **Special rules**: 6pt italic
- **Table headers**: 7pt bold uppercase
- **Table data**: 7pt
- **Armor modifier**: 6pt italic

These sizes ensure readability when printed at actual size.

## Nation Color Themes

The CSS includes 5 nation-specific themes matching official BattleGroup colors:

1. **German** (`.datacard-german`): Gray background, dark borders
2. **British** (`.datacard-british`): Tan background, brown borders
3. **Italian** (`.datacard-italian`): Beige background, brown borders
4. **American** (`.datacard-american`): Olive background, green borders
5. **French** (`.datacard-french`): Blue-gray background, navy borders

Apply with class: `<div class="datacard datacard-german">`

## Quality Verification Checklist

Before mass printing:

- [ ] Print 1 test page
- [ ] Measure card dimensions with ruler (should be 48mm × 84mm)
- [ ] Check 1mm white border is visible around each card
- [ ] Verify 2mm gap between cards
- [ ] Ensure no text is cut off at card edges
- [ ] Colors print correctly (not washed out)
- [ ] 8 cards fit exactly on one page
- [ ] No cards overflow to next page
- [ ] Scale is 100% (not shrunk/enlarged)

## Troubleshooting

### Cards are too small/large
- Verify print scale is 100% (not "Fit to page")
- Check page size is A4 landscape
- Ensure no custom zoom applied

### Cards cut off at edges
- Increase page margins slightly
- Reduce card padding if content overflows
- Check font sizes aren't too large

### Only 6 cards fit per page
- Grid is set for 3×2, not 4×2
- Verify CSS has `grid-template-columns: repeat(4, 48mm)`

### Colors don't print
- Enable "Background graphics" in print settings
- Ensure `-webkit-print-color-adjust: exact` is in CSS
- Try different browser (Chrome recommended)

### White border not showing
- Border is simulated with `border: 1mm solid white`
- May need to adjust if printing on colored paper
- For actual white border, print on white cardstock and trim

## Cutting Guide

For physical cards:

1. **Print on cardstock** (200-300gsm recommended)
2. **Cut along outer edge** of white border
3. **Use paper cutter** for straight edges (rotary cutter or guillotine)
4. **Batch cutting**: Stack multiple sheets, cut columns first, then rows

### Cutting Marks (Optional)

Add corner marks for precision cutting:

```css
.datacard::before,
.datacard::after {
    content: "";
    position: absolute;
    width: 2mm;
    height: 2mm;
    border: 0.5px solid #ccc;
}

.datacard::before {
    top: -1mm;
    left: -1mm;
    border-right: none;
    border-bottom: none;
}

.datacard::after {
    bottom: -1mm;
    right: -1mm;
    border-left: none;
    border-top: none;
}
```

## Integration with Datacard Generator

Update `generate_book_datacards.py` to use new CSS:

```python
# At top of markdown file
css_header = """
<link rel="stylesheet" href="../../shared/datacard_print_layout.css">
"""

# Group cards into pages of 8
cards_per_page = 8
for i in range(0, len(datacards), cards_per_page):
    page_cards = datacards[i:i+cards_per_page]

    markdown += '<div class="datacard-grid">\n'
    for card in page_cards:
        markdown += card.html
    markdown += '</div>\n\n'
```

## Example: Complete Datacard Page

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>British Tanks - Operation Crusader</title>
    <link rel="stylesheet" href="datacard_print_layout.css">
</head>
<body>
    <div class="datacard-grid">
        <!-- Crusader III -->
        <div class="datacard datacard-british">
            <div class="datacard-header">
                <div class="datacard-silhouette">🔲</div>
                <div class="datacard-title-block">
                    <p class="datacard-title">CRUSADER III</p>
                    <p class="datacard-subtitle">1942 | Cruiser Tank</p>
                    <p class="datacard-special-rules">Fast, Recce</p>
                </div>
            </div>
            <table>
                <tr>
                    <th class="main-header">VEHICLE</th>
                    <th class="main-header" colspan="3">MOVEMENT</th>
                    <th class="main-header" colspan="3">ARMOUR</th>
                    <th class="main-header" colspan="3">ARMAMENT</th>
                </tr>
                <tr>
                    <th></th>
                    <th>Off-Road</th>
                    <th>Road</th>
                    <th>Special</th>
                    <th>F</th>
                    <th>S</th>
                    <th>R</th>
                    <th>Weapon</th>
                    <th>Mount</th>
                    <th>Ammo</th>
                </tr>
                <tr>
                    <td>Crusader III</td>
                    <td>12"</td>
                    <td>24"</td>
                    <td>-</td>
                    <td>E</td>
                    <td>D</td>
                    <td>C</td>
                    <td>6 pdr</td>
                    <td>Turret</td>
                    <td>65</td>
                </tr>
                <tr>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td>Besa MG</td>
                    <td>Coax</td>
                    <td>3375</td>
                </tr>
            </table>
            <table>
                <tr>
                    <th class="main-header">WEAPON</th>
                    <th class="main-header">AMMO</th>
                    <th class="main-header">HE</th>
                    <th class="main-header" colspan="6">RANGE</th>
                </tr>
                <tr>
                    <th></th>
                    <th></th>
                    <th>3D6</th>
                    <th>0-10"</th>
                    <th>10-20"</th>
                    <th>20-30"</th>
                    <th>30-40"</th>
                    <th>40-50"</th>
                    <th>50-70"</th>
                </tr>
                <tr>
                    <td>6 pdr</td>
                    <td>HE</td>
                    <td>2D6</td>
                    <td>6</td>
                    <td>5</td>
                    <td>4</td>
                    <td>3</td>
                    <td>2</td>
                    <td>-</td>
                </tr>
                <tr>
                    <td>6 pdr</td>
                    <td>AP</td>
                    <td>-</td>
                    <td>8</td>
                    <td>7</td>
                    <td>6</td>
                    <td>5</td>
                    <td>4</td>
                    <td>3</td>
                </tr>
            </table>
        </div>

        <!-- 7 more cards... -->

    </div>
</body>
</html>
```

## File Locations

- **CSS**: `books/shared/datacard_print_layout.css`
- **Documentation**: `books/shared/DATACARD_PRINT_GUIDE.md`
- **Test HTML**: Create test file with 8 sample cards

## Next Steps

1. **Update datacard generator** to use new CSS
2. **Generate test page** with 8 cards
3. **Print test page** and verify dimensions
4. **Adjust if needed** (font sizes, spacing)
5. **Regenerate all datacards** for all 4 battles

---

**Created**: 2025-11-10
**Specifications**: Official BattleGroup datacard dimensions
**Status**: Ready for integration and testing
