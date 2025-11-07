# Gun Reference Schema Evolution

**Date**: November 5, 2025
**Status**: Active Development

---

## Migration History

### Migration 1: HE Range Columns (Nov 5, 2025)
**Issue**: Missing HE range bands (had AP ranges but not HE)
**Added**: `he_0_10, he_10_20, he_20_30, he_30_40, he_40_50, he_50_70 INTEGER`
**Rationale**: HE effectiveness varies by range like AP does

### Migration 2: Gun Name Variants (Nov 5, 2025)
**Issue**: Vehicles reference guns by aliases ("2 pdr") but DB has official names
**Added**:
- `common_name TEXT` column in bg_reference_guns
- `gun_name_variants` table (gun_id, variant_name, variant_source, is_official)
**Rationale**: Enable flexible weapon lookups, follows equipment_name_variants pattern from Phase 5.5

### Migration 3: HE Shell Classification (Nov 5, 2025)
**Issue**: Need to track shell weight/size for game mechanics
**Added**: `he_shell_classification TEXT`
**Values**: 'v. light', 'light', 'medium', 'heavy', 'bomb', 'rocket', 'Cannon'

### Migration 4: ROF and Categories (Nov 5, 2025 - IN PROGRESS)
**Issue**: Missing Rate of Fire, weapon categorization, special mechanics
**Adding**:
- `rof INTEGER` - Rate of Fire (1-10), core mechanic for all weapons
- `weapon_category TEXT` - Primary classification (rifle, mg, at_gun, aa_gun, flamethrower, bomb, rocket, etc.)
- `max_range_inches INTEGER` - Maximum effective range
- `special_rules TEXT` - Comma-separated special abilities

---

## Current Schema (30+ columns)

### Core Identification
- id, name, common_name, nation, caliber_mm, barrel_length

### HE (High Explosive) Stats
- he_dice, he_target - Dual value system ("6/4+" = 6 dice on 4+)
- he_shell_classification - Size category
- he_0_10, he_10_20, he_20_30, he_30_40, he_40_50, he_50_70 - Range bands

### AP (Armor Penetration) Stats
- ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70 - Range bands (1-15 scale)

### Game Mechanics (NEW)
- rof - Rate of Fire (1-10)
- weapon_category - Type classification
- max_range_inches - Maximum range
- special_rules - Special abilities

### Game Stats
- points_cost, battle_rating

### Provenance
- source_file, source_page, source_document, extraction_method, extraction_confidence, notes, etc.

---

## Field Type Decisions

### TEXT for Numeric Fields (Flexible Parser)
**Fields**: he_0_10 through he_50_70, ap_0_10 through ap_50_70

**Why**: Must accept:
- Numbers: `3`, `11`, `15`
- Dice formulas: `D6`, `D3`, `2D6`
- Dual values: `3(4)`, `7(8)` (Littlejohn Adaptor)
- Empty: `-`, blank, `N/A`

**Storage**: TEXT with validation, parse on read
**Alternative Rejected**: Separate columns for base/enhanced values (too complex)

### Comma-Separated TEXT
**Fields**: special_rules, mount_types, ammunition_types

**Why**: Multiple values possible
**Example**: `"one_shot,open_cover_save,variable_damage_D6"`

---

## gun_name_variants Table Structure

```sql
CREATE TABLE gun_name_variants (
    variant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    gun_id INTEGER NOT NULL,
    variant_name TEXT NOT NULL UNIQUE,
    variant_source TEXT,  -- 'official', 'vehicle_weapon', 'datacard', 'manual'
    is_official BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (gun_id) REFERENCES bg_reference_guns(id) ON DELETE CASCADE
);
```

**Indexes**: variant_name, gun_id (fast lookups)

**Example**:
```
Gun: "Ordnance QF 2-pounder" (gun_id=5)
Variants:
  - "Ordnance QF 2-pounder" (official)
  - "2 pdr" (vehicle_weapon)
  - "2-pdr" (vehicle_weapon)
  - "QF 2-pounder" (datacard)
```

**Lookup**: Vehicle weapon "2 pdr" → gun_id 5 → full gun stats

---

## Design Rationale

### Why Multiple Classification Fields?
BattleGroup uses overlapping classifications:
- By type: rifle, mg, gun, mortar
- By role: anti_tank, anti_aircraft, field_artillery
- By size: very_light, light, medium, heavy
- By mount: vehicle, infantry, deployed

Solution: Multiple fields (weapon_category, gun_role, he_shell_classification, mount_types)

### Why TEXT for Numeric Ranges?
Edge cases found in British import:
- Flamethrower: `he_0_10 = "D6"` (variable damage)
- Littlejohn: `ap_0_10 = "3(4)"` (dual values)
- AA guns: Empty HE fields (AP only)
- Bombs: Empty AP fields (HE only)

Solution: Accept TEXT, validate format, parse when needed

### Why Separate Variants Table?
Follows Phase 5.5 equipment_name_variants pattern:
- Proven architecture
- Supports unlimited aliases
- Proper normalization
- Easy weapon lookups
- Future-proof

---

## Migration SQL Scripts

### Location
`scripts/battlegroup/manual_extraction/migrate_guns_add_he_ranges_and_variants.sql`

### Execution Record
- Nov 5, 2025: Added HE ranges (he_0_10 through he_50_70)
- Nov 5, 2025: Added common_name column
- Nov 5, 2025: Created gun_name_variants table (26 initial variants)
- Nov 5, 2025: Added he_shell_classification
- Nov 5, 2025 PENDING: Add ROF, weapon_category, max_range_inches, special_rules

---

## Current Database State

**Tables**:
- bg_reference_guns: 26 guns (Canada's Crucible)
- gun_name_variants: 26 variants (1:1 currently, will grow)

**After British Import** (pending):
- bg_reference_guns: 26 + ~24 British = ~50 guns
- gun_name_variants: ~100+ variants (2-4 per gun)

---

## Next Steps

1. Complete Migration 4 (ROF + categories)
2. Import British guns (24 weapons)
3. Test edge case handling
4. Document lessons learned
5. Extend to German/Italian/American/French

**Schema Status**: Designed to handle all known edge cases + unknown future cases
