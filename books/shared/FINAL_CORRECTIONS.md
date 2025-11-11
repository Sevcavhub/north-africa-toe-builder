# Final Corrections Applied

## Issues Fixed

### 1. Title Alignment ✅
**Problem**: Titles were left-aligned
**Fix**: Added `text-align: right` to:
- `.datacard-title`
- `.datacard-subtitle`
- `.datacard-special-rules`

### 2. Weapon Performance Tables ✅
**Problem**: Simplified test cards didn't include the HE/AP range tables
**Fix**: Created complete example showing both tables:

**Table 1 - Vehicle Stats**:
```
VEHICLE | MOVEMENT | ARMOUR | ARMAMENT
        | Off | Rd | F S R | Weapon | Mount | Ammo
```

**Table 2 - Weapon Performance**:
```
WEAPON | AMMO | HE  | RANGE (0-10" | 10-20" | 20-30" | 30-40" | 40-50" | 50-70")
Gun    | HE   | 3D6 |   6   |   5    |   4    |   3    |   2    |   -
Gun    | AP   |  -  |   9   |   8    |   7    |   6    |   5    |   4
```

## Files Updated

1. ✅ **`datacard_print_layout_official.css`**
   - Added `text-align: right` for title, subtitle, special rules

2. ✅ **`datacard_test_complete.html`**
   - Complete 4-card examples with full weapon performance tables
   - Shows both vehicle stats AND weapon HE/AP range tables
   - Demonstrates right-aligned titles

## Datacard Structure

Each complete datacard now has:

```html
<div class="datacard datacard-{nation}">
    <!-- Header with silhouette + right-aligned titles -->
    <div class="datacard-header">
        <div class="datacard-silhouette">🔲</div>
        <div class="datacard-title-block">
            <p class="datacard-title">VEHICLE NAME</p>        <!-- RIGHT-ALIGNED -->
            <p class="datacard-subtitle">Year | Type</p>      <!-- RIGHT-ALIGNED -->
            <p class="datacard-special-rules">Rules</p>       <!-- RIGHT-ALIGNED -->
        </div>
    </div>

    <!-- Table 1: Vehicle stats -->
    <table>
        <tr><th>VEHICLE</th><th colspan="2">MOVEMENT</th><th colspan="3">ARMOUR</th><th colspan="3">ARMAMENT</th></tr>
        <tr><th></th><th>Off-Road</th><th>Road</th><th>F</th><th>S</th><th>R</th><th>Weapon</th><th>Mount</th><th>Ammo</th></tr>
        <tr><td>Name</td><td>8"</td><td>16"</td><td>F</td><td>E</td><td>D</td><td>75mmL43</td><td>Turret</td><td>87</td></tr>
        <tr><td></td><td></td><td></td><td></td><td></td><td></td><td>2 x MGs</td><td>Co-ax</td><td>3150</td></tr>
    </table>

    <!-- Table 2: Weapon performance (HE/AP ranges) -->
    <table>
        <tr><th>WEAPON</th><th>AMMO</th><th>HE</th><th colspan="6">RANGE</th></tr>
        <tr><th></th><th></th><th>3D6</th><th>0-10"</th><th>10-20"</th><th>20-30"</th><th>30-40"</th><th>40-50"</th><th>50-70"</th></tr>
        <tr><td>75mmL43</td><td>HE</td><td>3D6</td><td>6</td><td>5</td><td>4</td><td>3</td><td>2</td><td>-</td></tr>
        <tr><td>75mmL43</td><td>AP</td><td>-</td><td>9</td><td>8</td><td>7</td><td>6</td><td>5</td><td>4</td></tr>
    </table>
</div>
```

## Visual Appearance

```
┌────────────────────────────────────────────────────┐
│  🔲                        PANZER IV F2            │ ← Right-aligned
│                            1942 | Medium Tank      │ ← Right-aligned
│                            Reliable                │ ← Right-aligned
├────────────────────────────────────────────────────┤
│ VEHICLE | MOVEMENT | ARMOUR | ARMAMENT            │
│         | Off | Rd | F S R  | Wpn | Mount | Ammo │
│ Pz IV   | 8"  | 16"| F E D  |75L43| Turret| 87   │
│         |     |    |        |2xMGs| Co-ax | 3150 │
├────────────────────────────────────────────────────┤
│ WEAPON  | AMMO| HE | R A N G E                    │
│         |     |3D6 | 0-10|10-20|20-30|30-40|...  │
│ 75L43   | HE  |3D6 | 6 | 5 | 4 | 3 | 2 | -        │
│ 75L43   | AP  | -  | 9 | 8 | 7 | 6 | 5 | 4        │
└────────────────────────────────────────────────────┘
         67.8mm wide × 62mm tall
```

## Testing

**✅ CORRECT FILE**: `D:\north-africa-toe-builder\books\shared\datacard_test_complete.html`
**❌ INCORRECT FILE**: `D:\north-africa-toe-builder\books\shared\datacard_test_FIXED_GUNS.html` (missing weapon performance table)

**Reference Example**: See `Sherman.png` - shows complete two-table structure

**Verify**:
- ✅ Titles align to the right (next to silhouette)
- ✅ Two tables present on each card
- ✅ Weapon performance table shows HE/AP rows with range bands
- ✅ 12 cards fit in 4×3 grid
- ✅ Nation colors work correctly

## Integration Notes

When updating `generate_book_datacards.py`:

1. Ensure titles use right-aligned CSS (already in official CSS)
2. Generate BOTH tables for each vehicle:
   - Vehicle stats table (movement, armour, armament summary)
   - Weapon performance table (HE/AP penetration by range)
3. Use gun name conversion table for weapon names
4. Pull HE/AP values from `bg_builder_weapons` table
5. Format range bands: 0-10", 10-20", 20-30", 30-40", 40-50", 50-70"

---

## Sherman.png Analysis (November 10, 2025)

**Reference File**: `D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Sherman.png`

**Confirmed Two-Table Structure**:

**Table 1 - Vehicle Statistics**:
```
┌──────────┬──────────────────┬─────────────────┬─────────────────────────────┐
│ VEHICLE  │ MOVEMENT         │ ARMOUR          │ ARMAMENT                    │
│          │ Off-Road │ Road │ F │ S │ R       │ Weapon │ Mount │ Ammo       │
├──────────┼──────────┼───────┼───┼───┼─────────┼────────┼───────┼────────────┤
│M4 Sherman│ 8"       │ 16"  │ L │ L │ N       │75mm M3 │Turret │ 97         │
│(A1,A2,A3)│          │      │   │   │         │MG      │Co-axial│            │
│          │          │      │   │   │         │MG      │Hull    │            │
└──────────┴──────────┴──────┴───┴───┴─────────┴────────┴───────┴────────────┘
```

**Table 2 - Weapon Performance** (HE/AP penetration by range):
```
┌────────┬──────┬─────┬──────────────────────────────────────────────────┐
│ WEAPON │ AMMO │ HE  │ RANGE                                            │
│        │      │     │ 0-10" │10-20"│20-30"│30-40"│40-50"│50-70"       │
├────────┼──────┼─────┼───────┼──────┼──────┼──────┼──────┼──────────────┤
│75mmL40 │ HE   │ 4/4+│   3   │  3   │  3   │  3   │  3   │             │
│        │ AP   │     │   6   │  6   │  5   │  4   │  3   │             │
└────────┴──────┴─────┴───────┴──────┴──────┴──────┴──────┴──────────────┘
```

**Critical Implementation Details**:
1. **Both tables required** - Vehicle stats + Weapon performance
2. **HE column** shows dice (e.g., "4/4+", "3D6")
3. **AP values** show penetration rating by range band
4. **Range bands**: 0-10", 10-20", 20-30", 30-40", 40-50", 50-70"
5. **Multi-weapon vehicles**: Secondary weapons (MGs) listed in separate rows with mount/ammo

**Database Linkage**:
- Weapon names: Use `bg_gun_name_conversion` table (230 mappings)
- HE values: From `bg_builder_weapons.he_effect`
- AP values: From `bg_builder_weapons.ap_effect` (already range-banded in database)
- Ammo counts: From `bg_reference_vehicles.ammo_1`, `ammo_2`, etc.

---

**Status**: ✅ All corrections applied | ✅ Two-table structure confirmed with Sherman.png
**Date**: 2025-11-10
**Files ready**: CSS updated, complete test HTML created (`datacard_test_complete.html`)
