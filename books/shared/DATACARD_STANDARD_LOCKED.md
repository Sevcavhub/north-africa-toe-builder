# BattleGroup Datacard Standard - LOCKED SPECIFICATION

**Date Locked**: November 10, 2025
**Reference Source**: Sherman.png (official BattleGroup datacard example)
**Status**: ✅ **FINAL - DO NOT MODIFY**

---

## Official Dimensions (from Battlegroup-DataCards-Early-German.pdf)

- **Card Size**: 67.8mm wide × 62mm tall
- **Grid Layout**: 4 columns × 3 rows = 12 cards per page
- **Gap Between Cards**: 2mm
- **Page Margins**: 10mm all sides
- **Page Size**: A4 landscape (297mm × 210mm)
- **Total Grid**: 277mm × 190mm

---

## Two-Table Structure (MANDATORY)

Every vehicle/tank datacard MUST have TWO tables:

### Table 1: Vehicle Statistics

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

**Columns**:
- VEHICLE: Vehicle name
- MOVEMENT: Off-Road (inches), Road (inches)
- ARMOUR: F (Front), S (Side), R (Rear) - letter ratings (A-O)
- ARMAMENT: Weapon name, Mount type, Ammo count

**Multi-weapon handling**:
- Main gun on first data row
- Secondary weapons (MGs, etc.) on additional rows
- Leave movement/armor columns blank for secondary weapons

### Table 2: Weapon Performance

```
┌────────┬──────┬─────┬──────────────────────────────────────────────────┐
│ WEAPON │ AMMO │ HE  │ RANGE                                            │
│        │      │     │ 0-10" │10-20"│20-30"│30-40"│40-50"│50-70"       │
├────────┼──────┼─────┼───────┼──────┼──────┼──────┼──────┼──────────────┤
│75mmL40 │ HE   │ 4/4+│   3   │  3   │  3   │  3   │  3   │             │
│        │ AP   │     │   6   │  6   │  5   │  4   │  3   │             │
└────────┴──────┴─────┴───────┴──────┴──────┴──────┴──────┴──────────────┘
```

**Columns**:
- WEAPON: Short gun name (use `bg_gun_name_conversion` table)
- AMMO: "HE" or "AP"
- HE: Dice value (e.g., "3D6", "4/4+", "2D6")
- RANGE: Penetration values at 6 range bands

**Range Bands** (standard):
- 0-10"
- 10-20"
- 20-30"
- 30-40"
- 40-50"
- 50-70"

**HE/AP rows**:
- First row: HE with dice value and range effectiveness
- Second row: AP with blank HE column and penetration values

---

## Header Section (Above Tables)

```html
<div class="datacard-header">
    <div class="datacard-silhouette">
        <!-- Tank silhouette image or placeholder -->
    </div>
    <div class="datacard-title-block">
        <p class="datacard-title">M4 SHERMAN</p>              <!-- RIGHT-ALIGNED -->
        <p class="datacard-subtitle">1942-1945 | Medium Tank</p> <!-- RIGHT-ALIGNED -->
        <p class="datacard-special-rules">Reliable</p>         <!-- RIGHT-ALIGNED -->
    </div>
</div>
```

**Alignment**: ALL text in title block must be **right-aligned** (see CSS line 161-179)

---

## CSS File

**Location**: `D:\north-africa-toe-builder\books\shared\datacard_print_layout_official.css`

**Key settings**:
```css
/* Card dimensions */
.datacard {
    width: 67.8mm;
    height: 62mm;
}

/* Grid layout */
.datacard-grid {
    display: grid;
    grid-template-columns: repeat(4, 67.8mm);
    grid-template-rows: repeat(3, 62mm);
    gap: 2mm;
}

/* Right-aligned titles */
.datacard-title,
.datacard-subtitle,
.datacard-special-rules {
    text-align: right;
}

/* Print settings */
@media print {
    @page {
        size: A4 landscape;
        margin: 10mm;
    }
}
```

---

## Reference Files

**✅ CORRECT IMPLEMENTATION**:
- `datacard_test_complete.html` - Complete two-table structure with weapon performance tables

**❌ INCORRECT IMPLEMENTATIONS** (DO NOT USE):
- `datacard_test_FIXED_GUNS.html` - Missing weapon performance table
- Any single-table implementations

**Official Reference**:
- `Sherman.png` - Shows official BattleGroup datacard with both tables
- `Battlegroup-DataCards-Early-German.pdf` - Official card dimensions and layout

---

## Database Linkage for Data Population

**Weapon Names**:
- Table: `bg_gun_name_conversion` (230 weapon mappings)
- Maps: `bg_builder_weapons.weapon_name` → `datacard_name`
- Example: "75mm Gun M3 (Sherman)" → "75mm M3"

**HE Values**:
- Table: `bg_builder_weapons.he_effect`
- Format: "3D6", "4/4+", "2D6", etc.

**AP Values**:
- Table: `bg_builder_weapons.ap_effect`
- Format: Already range-banded in database (comma-separated)
- Example: "6,6,5,4,3,-" for 6 range bands

**Armor Values**:
- Table: `equipment_battlegroup.armor_front`, `armor_side`, `armor_rear`
- Format: Letter ratings (A, B, C, D, E, F, G, H, I, J, K, L, M, N, O)

**Movement Values**:
- Table: `equipment_battlegroup.movement_off_road`, `movement_road`
- Format: Inches (e.g., "8\"", "16\"")

**Ammo Counts**:
- Table: `bg_reference_vehicles.ammo_1`, `ammo_2`, `ammo_3`, `ammo_4`
- Format: Integer counts (e.g., 97, 3150)

---

## Implementation Checklist

When generating datacards, EVERY card MUST have:

- [ ] Header with silhouette + right-aligned titles
- [ ] Table 1: Vehicle stats (movement, armor, armament summary)
- [ ] Table 2: Weapon performance (HE/AP penetration by range)
- [ ] 67.8mm × 62mm dimensions
- [ ] Nation-specific color theme
- [ ] Proper font sizes (7pt body, 6pt tables)
- [ ] All data populated from database (NO placeholders like "None", "???", "-")

---

## Quality Standards

**Publication Requirements**:
- ✅ 100% data coverage (no missing values)
- ✅ Weapon names from conversion table
- ✅ HE/AP values from weapons database
- ✅ Ammo counts from reference vehicles
- ✅ Armor/movement from equipment_battlegroup
- ✅ Two-table structure on every vehicle card
- ✅ Right-aligned titles
- ✅ Correct dimensions (67.8mm × 62mm)

**Zero Tolerance**:
- ❌ NO "None" for weapons
- ❌ NO "???" for armor values
- ❌ NO "-" for movement/ammo (except where legitimately unavailable)
- ❌ NO missing weapon performance tables
- ❌ NO single-table implementations

---

## Generator Script Integration

**Script**: `scripts/battlegroup/book/generate_book_datacards.py`

**Must implement**:
1. Query `equipment_battlegroup` for card data
2. LEFT JOIN `bg_gun_name_conversion` for weapon display names
3. LEFT JOIN `bg_builder_weapons` for HE/AP values
4. LEFT JOIN `bg_reference_vehicles` for ammo counts
5. Generate BOTH tables for each vehicle
6. Use official CSS (`datacard_print_layout_official.css`)
7. Apply nation color classes (datacard-german, datacard-british, etc.)
8. Validate 100% data completeness before output

---

**LOCKED**: This specification is final. All future datacard generation MUST follow this standard.

**Last Updated**: November 10, 2025
**Verified Against**: Sherman.png official reference
