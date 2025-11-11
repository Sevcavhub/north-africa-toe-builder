# BattleGroup Official Datacard Dimensions

## Measured from Official PDF

**Source**: `Battlegroup-DataCards-Early-German.pdf`

## Confirmed Layout

After examining the official PDF, the actual layout is:

- **Card size**: **67.8mm (width) × 62mm (height)**
- **Grid**: **4 columns × 3 rows = 12 cards per page**
- **Gap between cards**: 2mm
- **Page**: A4 landscape (297mm × 210mm)
- **Margins**: 10mm all sides
- **Total grid**: 277mm × 190mm

## Why Previous Attempts Were Wrong

### User's Initial Specification (84mm × 48mm)
- **Problem**: Too wide (342mm) for 4 columns - exceeds A4 width (297mm)
- **Would only fit**: 3 columns × 3 rows = 9 cards per page
- **Doesn't match official PDF**: PDF clearly shows 12 cards (4×3 grid)

### First Correction Attempt (48mm × 84mm)
- **Problem**: Height and width were reversed - cards would be portrait orientation
- **BattleGroup cards are landscape**: Wider than tall, not taller than wide

## Correct Official Dimensions

```
Card: 67.8mm × 62mm (landscape - slightly wider than tall)
Aspect ratio: 1.09:1
Grid: 4 columns × 3 rows
Total grid: 277mm × 190mm
Fits on: A4 landscape with 10mm margins
```

## Visual Layout

```
A4 LANDSCAPE (297mm × 210mm)
┌────────────────────────────────────────────────────┐
│ ← 10mm margin →                   ← 10mm margin → │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │ ↑
│  │  4×3 GRID (277mm × 190mm)                    │ │ 10mm
│  │                                               │ │ ↓
│  │  [Card] [Card] [Card] [Card]  ← Row 1        │ │
│  │    ↕2mm gap                                   │ │
│  │  [Card] [Card] [Card] [Card]  ← Row 2        │ │
│  │    ↕2mm gap                                   │ │
│  │  [Card] [Card] [Card] [Card]  ← Row 3        │ │
│  │                                               │ │
│  │  Each card: 67.8mm × 62mm                    │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │ ↑
└────────────────────────────────────────────────────┘ 10mm
                                                       ↓
```

## Files Created

1. ✅ **`datacard_print_layout_official.css`** - CSS with correct 67.8mm × 62mm dimensions
2. ✅ **`datacard_print_test_OFFICIAL.html`** - Test file with 12 sample cards (4×3 grid)
3. ✅ **`OFFICIAL_DIMENSIONS_FROM_PDF.md`** - This documentation

## Testing

**Open**: `D:\north-africa-toe-builder\books\shared\datacard_print_test_OFFICIAL.html`

**Expected result**:
- 12 cards visible on screen in 4×3 grid
- Each card 67.8mm wide × 62mm tall
- 2mm gaps between cards
- Centered on A4 landscape page
- Matches official Battlegroup-DataCards-Early-German.pdf layout

## Print Settings

**Critical settings** for accurate dimensions:
- **Layout**: Landscape
- **Paper**: A4 (210mm × 297mm)
- **Scale**: 100% (do not adjust!)
- **Margins**: 10mm all sides (or let CSS handle it)
- **Background graphics**: ON
- **Headers/footers**: OFF

## Comparison

| Spec | User's (84×48) | Corrected (48×84) | **Official (67.8×62)** |
|------|----------------|-------------------|----------------------|
| Width | 84mm | 48mm | **67.8mm** ✅ |
| Height | 48mm | 84mm | **62mm** ✅ |
| Aspect | 1.75:1 | 0.57:1 | **1.09:1** ✅ |
| Orientation | Too wide | Too tall | **Slightly wider** ✅ |
| Grid | 4×3 won't fit | 3×3 = 9 cards | **4×3 = 12 cards** ✅ |
| Matches PDF | ❌ No | ❌ No | **✅ Yes** |

## Integration

Update `generate_book_datacards.py` to use:
- CSS file: `datacard_print_layout_official.css`
- Cards per page: **12** (4 columns × 3 rows)
- Card dimensions: **67.8mm × 62mm**

```python
# Group datacards into pages of 12
cards_per_page = 12

# CSS reference in markdown
css_link = '<link rel="stylesheet" href="../../shared/datacard_print_layout_official.css">'

# Wrap each page of 12 cards
for i in range(0, len(datacards), cards_per_page):
    page_cards = datacards[i:i+cards_per_page]
    markdown += '<div class="datacard-grid">\n'
    for card in page_cards:
        markdown += card.html
    markdown += '</div>\n\n'
```

## Font Sizing

Official PDF uses small fonts to fit content in 67.8mm × 62mm space:
- **Title**: 8pt bold
- **Subtitle**: 5.5pt
- **Special rules**: 5.5pt italic
- **Table headers**: 6pt bold uppercase
- **Table data**: 6pt

These sizes are already set in `datacard_print_layout_official.css`.

## Next Steps

1. ✅ Measure official PDF dimensions
2. ✅ Create CSS with correct 67.8mm × 62mm cards
3. ✅ Create test HTML with 12 cards in 4×3 grid
4. ⏳ **Test print** to verify physical dimensions
5. ⏳ Update datacard generator script
6. ⏳ Regenerate all datacards with official layout
7. ⏳ Export final PDFs

---

**Status**: ✅ Official dimensions measured and implemented
**Source**: Battlegroup-DataCards-Early-German.pdf (page 1 shows 4×3 grid)
**Date**: 2025-11-10
