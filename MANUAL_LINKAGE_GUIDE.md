# Manual Vehicle Linkage Guide

**Purpose**: Link your manually-entered BattleGroup reference vehicles to official BG Builder data through a user-controlled interface (NOT fuzzy matching).

---

## Problem Statement

**Issue 1: Fuzzy Matching Created Bad Linkages**
- Automated fuzzy matching linked some vehicles incorrectly
- Name variations caused mismatches (e.g., "Sturmgeschutz" vs "StuG III G")
- You need manual control to approve/reject linkages

**Issue 2: Excel Pre-population Had All 599 Vehicles**
- Original script populated ALL BG Builder vehicles (including Japanese tanks)
- Should only populate Tobruk/Torch vehicles for North Africa focus
- Fixed: Now parses force list sections to extract actual Tobruk/Torch vehicles

---

## Solution: Three-Step Manual Linkage Workflow

### Step 1: Generate Linkage Review CSV

**Script**: `scripts/battlegroup/import/create_manual_linkage_interface.py`

**What it does**:
- Loads all 215 manually-entered vehicles from `bg_reference_vehicles`
- For each vehicle, finds top 3 candidate matches from BG Builder (599 vehicles)
- Shows existing fuzzy linkage (if any) for review
- Outputs `manual_vehicle_linkage_review.csv` with side-by-side comparison

**Run**:
```bash
python scripts/battlegroup/import/create_manual_linkage_interface.py
```

### Step 2: Review and Approve in Excel

**File**: `manual_vehicle_linkage_review.csv`

**Columns**:
- `manual_id` / `manual_name`: Your manually-entered vehicle
- `manual_armor_f_s_r`: Your armor values (format: "M/N/O")
- `manual_movement`: Your movement values (format: "8\"/12\"")
- `manual_weapon1`: Primary weapon
- `manual_nation`: Nation (german, british, italian, etc.)
- `manual_source`: Source battle (Tobruk, Torch, etc.)
- `CURRENT_bg_builder_id` / `CURRENT_bg_name`: Existing fuzzy linkage (review this!)
- `SUGGESTED_bg_id_1` / `SUGGESTED_bg_name_1` / `similarity_1`: Top candidate (with % match)
- `SUGGESTED_bg_id_2-3`: 2nd and 3rd candidates
- **`APPROVED_bg_id`**: **YOU FILL THIS** - Enter bg_id of correct match
- `NOTES`: Optional notes (e.g., "No match found", "Wrong variant")

**Process**:
1. Open CSV in Excel
2. For each row:
   - Check if `CURRENT` linkage is correct (if exists)
   - Review `SUGGESTED` matches and their similarity percentages
   - Compare armor/movement/weapons to validate match
   - Enter correct `bg_id` in `APPROVED_bg_id` column
   - Add notes if needed
3. **Leave `APPROVED_bg_id` blank** if no match exists (manual-only vehicle)
4. Save and close Excel

**Example Row**:
```
manual_id: 101
manual_name: A10
manual_armor: M/N/O
manual_movement: 5"/8"
manual_weapon1: 2 pdr
CURRENT_bg_builder_id: (blank - no fuzzy match)
SUGGESTED_bg_id_1: 80
SUGGESTED_bg_name_1: BA-10
similarity_1: 75.00%  ← WRONG (Russian vehicle, not British A10)
SUGGESTED_bg_id_2: 334
SUGGESTED_bg_name_2: A10 Cruiser Mk.II
similarity_2: 56.00%  ← CORRECT MATCH!

APPROVED_bg_id: 334  ← YOU ENTER THIS
NOTES: Correct - British A10 Cruiser
```

### Step 3: Import Approved Linkages

**Script**: `scripts/battlegroup/import/import_manual_linkages.py`

**What it does**:
- Reads `manual_vehicle_linkage_review.csv`
- Validates all approved linkages (checks IDs exist)
- Updates `bg_reference_vehicles.bg_builder_id` with approved values
- Shows final linkage statistics

**Run**:
```bash
python scripts/battlegroup/import/import_manual_linkages.py
```

---

## Automated Workflow (Batch File)

**For convenience**: `scripts/battlegroup/import/manual_linkage_workflow.bat`

**What it does**:
1. Runs Step 1 (generate CSV)
2. Opens CSV in Excel for you
3. Waits for you to finish and save
4. Runs Step 3 (import approved linkages)
5. Shows final statistics

**Run**:
```bash
scripts\battlegroup\import\manual_linkage_workflow.bat
```

---

## Expected Outcomes

### Current Status (Before Manual Review)
- Total manual vehicles: 215
- Linked via fuzzy matching: 172 (80%)
- Unlinked: 43 (20%)
- **Problem**: Some fuzzy matches are incorrect

### After Manual Review (Target)
- Total manual vehicles: 215
- Correctly linked: ~180-190 (85-90%)
- Manual-only vehicles: ~25-35 (10-15%)
- **Benefit**: All linkages user-approved, zero incorrect matches

### Manual-Only Vehicles (Expected)
Vehicles that likely won't have BG Builder matches:
- Soft-skin variants (Bedford QLT, CMP, Opel Blitz)
- Specific field modifications (20mm Flak Truck, 37mm Flak Truck)
- Commonwealth-specific variants (Crusader AA MkII variants)
- Command vehicles (Cromwell HQ, M5 Recce)

**These are fine to leave unlinked** - they represent manual research that supplements BG Builder.

---

## Common Linkage Scenarios

### Scenario 1: Exact Match (Easy)
```
manual_name: Panzer IV H
SUGGESTED_bg_name_1: Panzer IV H (similarity: 100%)
Action: Enter suggested bg_id in APPROVED_bg_id
```

### Scenario 2: Name Variation (Common)
```
manual_name: Sturmgeschutz
SUGGESTED_bg_name_1: StuG III G (similarity: 65%)
Action: Verify armor/weapons match, then approve
```

### Scenario 3: Variant Mismatch (Requires Research)
```
manual_name: M4 Sherman (75mm)
SUGGESTED_bg_name_1: M4 Sherman (76mm)
Action: Check weapon in BG Builder, find correct variant ID
```

### Scenario 4: No Match (Manual-Only)
```
manual_name: 20mm Flak Truck (improvised)
SUGGESTED matches: All generic trucks (low similarity)
Action: Leave APPROVED_bg_id blank, add note "Manual-only"
```

---

## Data Quality Benefits

### Before (Fuzzy Matching)
- Automated, no user control
- Name similarity only (ignores weapons/armor)
- 80% linkage but some incorrect
- Example error: "A10" → "BA-10" (Russian vehicle!)

### After (Manual Review)
- User approves every linkage
- Can verify weapons/armor match
- Higher quality, fewer errors
- Example fix: "A10" → "A10 Cruiser Mk.II" (correct British tank)

---

## Integration with Excel Pre-population

**Fixed**: `scripts/battlegroup/import/prepopulate_excel_template.py`

**Changes**:
- Now parses force list JSON to extract vehicle IDs
- Only includes vehicles actually in Tobruk/Torch force lists
- No more Japanese tanks in North Africa template!

**Usage After Linkage**:
1. Complete manual linkage review
2. Run `prepopulate_excel_template.py`
3. Output: Only Tobruk/Torch vehicles, properly linked to your manual data
4. Excel shows BG Builder stats + your manual additions side-by-side

---

## Troubleshooting

### "No approved linkages found in CSV"
- You forgot to fill the `APPROVED_bg_id` column
- Open CSV, enter bg_ids, save

### "Invalid bg_id for manual_id X"
- You entered a non-numeric value or non-existent ID
- Check that bg_id exists in BG Builder (1-599)

### "Manual vehicle ID X not found"
- CSV was edited incorrectly
- Re-run `create_manual_linkage_interface.py` to regenerate

### Excel shows all 599 vehicles instead of Tobruk/Torch only
- Force list JSON parsing failed
- Check console output for "Extracted N unique vehicle IDs"
- If 0, sections JSON format may have changed

---

## Files Created

| File | Purpose |
|------|---------|
| `create_manual_linkage_interface.py` | Generate CSV for review |
| `import_manual_linkages.py` | Import approved linkages |
| `manual_linkage_workflow.bat` | Automated 3-step workflow |
| `manual_vehicle_linkage_review.csv` | User edits this in Excel |

---

## Summary

**Problem**: Fuzzy matching created incorrect linkages, Excel had all 599 vehicles

**Solution**: User-controlled linkage interface with side-by-side comparison

**Workflow**:
1. Generate CSV with suggestions
2. Review in Excel, approve correct matches
3. Import approved linkages to database

**Result**: High-quality linkages, user control, Tobruk/Torch focus

**Time**: ~30-45 minutes to review 215 vehicles (many are 100% matches)

---

**Ready to start?** Run `manual_linkage_workflow.bat` or follow the 3-step process above.
