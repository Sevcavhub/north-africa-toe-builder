# BattleGroup Datacard Dimensions - CORRECTED

## Issue Found

The initial implementation had width and height **reversed**.

### Incorrect (Original)
- Card size: 48mm (width) × 84mm (height)
- Grid: 4 columns × 2 rows = 8 cards per page
- **Problem**: Cards were taller than wide (portrait orientation)

### Correct (Fixed)
- Card size: **84mm (width) × 48mm (height)** ✅
- Grid: **3 columns × 3 rows = 9 cards per page** ✅
- Cards are wider than tall (landscape orientation) ✅

## Official BattleGroup Specifications

- **Card dimensions**: 84mm wide × 48mm tall (landscape format)
- **White border**: 1mm around each card
- **Padding between cards**: 2mm
- **Page size**: A4 landscape (297mm × 210mm)

## Grid Layout Options

### Option 1: 3×3 Grid (9 cards per page) ✅ **IMPLEMENTED**
- Grid size: 256mm × 148mm
- Margins: 20.5mm horizontal, 31mm vertical
- **Fits perfectly** on A4 landscape
- Good balance of card count and margins

### Option 2: 3×4 Grid (12 cards per page)
- Grid size: 256mm × 198mm
- Margins: 20.5mm horizontal, 6mm vertical
- **Fits** on A4 landscape
- Maximum density, minimal margins
- Could be cramped for cutting

### Option 3: 3×2 Grid (6 cards per page)
- Grid size: 256mm × 98mm
- Margins: 20.5mm horizontal, 56mm vertical
- **Fits** on A4 landscape
- Lots of white space, fewer cards per page

**Recommendation**: **3×3 grid** (9 cards) - best balance

## Corrected CSS Values

```css
/* Grid layout - 3 columns × 3 rows */
.datacard-grid {
    display: grid;
    grid-template-columns: repeat(3, 84mm);  /* 3 columns of 84mm */
    grid-template-rows: repeat(3, 48mm);     /* 3 rows of 48mm */
    gap: 2mm;
    width: 256mm;   /* (84mm × 3) + (2mm × 2) */
    height: 148mm;  /* (48mm × 3) + (2mm × 2) */
}

/* Individual card dimensions */
.datacard {
    width: 84mm;   /* CORRECTED from 48mm */
    height: 48mm;  /* CORRECTED from 84mm */
}

/* Page margins to center grid */
@page {
    size: A4 landscape;
    margin: 31mm 20.5mm;  /* Vertical 31mm, Horizontal 20.5mm */
}
```

## Files Updated

1. ✅ **`datacard_print_layout.css`** - Corrected dimensions
2. ✅ **`datacard_print_test_corrected.html`** - New test file with 9 cards
3. ✅ **`CORRECTED_DIMENSIONS_SUMMARY.md`** - This file

## Files to Update

The following files still reference the old (incorrect) dimensions and should be updated:

- [ ] `DATACARD_PRINT_GUIDE.md` - Update all dimension references
- [ ] `PRINT_LAYOUT_IMPLEMENTATION.md` - Update specifications
- [ ] `print_layout_diagram.txt` - Redraw diagrams with correct dimensions
- [ ] `datacard_print_test.html` - Original test file (can be deleted or updated)

## Verification Steps

1. **Open test file**: `datacard_print_test_corrected.html`
2. **Print preview**: Should show 9 cards in 3×3 grid
3. **Print test page**: Use 100% scale, A4 landscape
4. **Measure cards**: Should be 84mm (width) × 48mm (height)

## Why This Happened

The confusion arose from describing cards as "landscape" but thinking of them in portrait orientation. BattleGroup datacards are **wider than they are tall**, like a typical playing card held sideways.

## Visual Reference

```
CORRECT ORIENTATION:
┌────────────────────────────────────────────┐
│  ┌──┐ VEHICLE NAME                         │  48mm
│  │🔲│ Type | Year                          │  height
│  └──┘ Special Rules                        │
│  [Equipment Stats Table]                   │
└────────────────────────────────────────────┘
              84mm width

NOT:
┌──────────────┐
│  ┌──┐        │
│  │🔲│ VEHICLE│  84mm
│  └──┘        │  height
│  Name        │  (WRONG!)
│  Type        │
│  [Stats]     │
│              │
│              │
└──────────────┘
   48mm width
```

## Integration Notes

When updating `generate_book_datacards.py`:
- Change cards per page from 8 to 9
- Update CSS reference to corrected file
- Verify table layouts work in wider (84mm) format
- May need to adjust font sizes or table column widths

---

**Status**: ✅ CSS corrected, test file created
**Date**: 2025-11-10
**Next**: Test print to verify physical dimensions match
