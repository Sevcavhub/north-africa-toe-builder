# Sample Datacards - V5 Format Test

**Generated:** 6 datacards in 3x2 grid layout

---

## What's In This Sample

### Row 1:
1. **SdKfz 250** (German Halftrack)
   - Armor: F=N, S=O, R=O
   - **NEW V5:** Shows "Open-Topped" in italics below armor values

2. **Bedford MW** (British Truck)
   - Armor: F=Soft-Skinned
   - No modifier row (soft-skinned displays normally)

3. **Panzer IV Ausf E** (German Tank)
   - Armor: F=N, **S=O(M)**, R=O
   - **NEW V5:** Side armor shows Schürzen format "O(M)"

### Row 2:
4. **2 Pdr AT** (British AT Gun)
   - Armor: F=N, S=O, R=O
   - No modifier (regular gun)

5. **Matilda II** (British Tank)
   - Armor: F=K, S=K, R=L
   - No modifier (regular tank)

6. **Crusader Mk I** (British Tank)
   - Armor: F=N, S=O, R=O
   - No modifier (regular tank)

---

## V5 Format Features Demonstrated

### 1. Open-Topped Display
**SdKfz 250** shows:
```
| Halftrack | 8"  | 18" | - | N | O | O | None | Turret | - |
```
**NEW:** Additional row below armor:
```
|           |     |     |     | Open-Topped |     |
```
*(Centered below armor columns, displayed in italics)*

### 2. Schürzen Display
**Panzer IV Ausf E** shows:
```
| Tank | 10" | 14" | - | N | O(M) | O | None | Turret | - |
```
*(Side armor displays as base value with Schürzen value in parentheses)*

### 3. Backward Compatibility
Bedford MW, 2 Pdr, Matilda II, and Crusader display exactly as V4 format (no changes when fields are NULL).

---

## How To View/Print

1. **Open in Browser:**
   ```bash
   cd books/battleaxe/book
   mdbook build
   start book/chapter2/SAMPLE_DATACARDS_TEST.html
   ```

2. **Print Settings:**
   - Page Size: A4 Landscape
   - Margins: 10mm
   - Scale: 100%
   - Background graphics: ON

3. **What You'll See:**
   - 3x2 grid of datacards
   - BattleGroup tan/brown color scheme
   - Professional layout matching official supplements

---

## Database Fields Used

All data read from `equipment_battlegroup` table:
- `armor_front`, `armor_side`, `armor_rear` (armor values)
- `armor_modifier` (e.g., "Open-Topped")
- `armor_side_schurzen` (e.g., "M" for Schürzen value)
- `off_road_movement`, `road_movement`
- `points_regular`, `battle_rating_regular`

**No joins to reference tables needed** - self-contained!

---

## CSS Not Modified

Uses existing V4 CSS with one addition:
```css
.armor-modifier-row td {
    font-style: italic;
    font-size: 7px;
    padding: 1px 3px;
}
```

---

**File:** `SAMPLE_DATACARDS_TEST.md`
**Generator:** `scripts/battlegroup/book/generate_sample_datacards.py`
