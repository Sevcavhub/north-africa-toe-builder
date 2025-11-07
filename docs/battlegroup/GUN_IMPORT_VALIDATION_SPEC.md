# Gun Import Validation Specification

**Date**: November 5, 2025
**Purpose**: Flexible parser for manual CSV entry AND future OCR scraping
**Scope**: Accept edge cases gracefully, validate critical fields, warn on anomalies

---

## Design Philosophy

**Core Principle**: **Warn, Don't Reject**
- Parser accepts unusual data formats
- Validation flags items for manual review
- Import succeeds with warnings logged
- User decides what to keep/fix

**Why**: Manual CSV entry has same error patterns as OCR:
- Variable formats ("3", "D6", "3(4)")
- Missing data (blank fields, "-")
- Special cases (AA guns, bombs, flamethrowers)
- Typos and inconsistencies

**Goal**: Single flexible parser works for both use cases

---

## Field Validation Rules

### CRITICAL Fields (Must Be Present)

**Required for ALL weapons**:
- `name` - TEXT, non-empty, unique within table
- `nation` - TEXT, comma-separated, canonical values only
- `caliber_mm` - INTEGER or DECIMAL, >0

**Required for import success**:
- At least ONE of: `he_dice` OR `ap_0_10` (guns must have HE or AP data)

**Validation**:
```python
def validate_critical_fields(gun):
    errors = []
    if not gun.name or gun.name.strip() == '':
        errors.append("CRITICAL: Missing name")
    if not gun.nation or gun.nation.strip() == '':
        errors.append("CRITICAL: Missing nation")
    if gun.caliber_mm is None or gun.caliber_mm <= 0:
        errors.append("CRITICAL: Missing or invalid caliber_mm")

    has_he = gun.he_dice is not None
    has_ap = any([gun.ap_0_10, gun.ap_10_20, gun.ap_20_30,
                   gun.ap_30_40, gun.ap_40_50, gun.ap_50_70])

    if not has_he and not has_ap:
        errors.append("CRITICAL: No HE or AP data")

    return errors  # Empty list = valid
```

### NUMERIC Fields (Flexible Parsing)

**Fields**: All HE/AP range bands, ROF, points_cost, battle_rating

**Accept**:
- Fixed integers: `0`, `1`, `15`, `99`
- Decimal: `37.5` (for caliber_mm only)
- Dice formulas: `D6`, `D3`, `2D6`, `3D6+1`
- Dual values: `3(4)`, `7(8)` (extract base, warn)
- Empty: `-`, blank, `N/A`, `null`

**Reject**:
- Text garbage: `abc`, `unknown`, `varies`
- Invalid format: `3-4`, `3/4`, `3 or 4`

**Parser**:
```python
def parse_numeric_field(value, field_name):
    """Flexible parser accepting numbers, dice, dual values, empty."""
    if value is None or value == '':
        return None  # Empty is valid

    value = str(value).strip()

    # Handle standard "null" indicators
    if value.upper() in ['-', 'N/A', 'NULL', 'NONE']:
        return None

    # Handle dice formulas (D6, 2D6, etc.)
    if 'D' in value.upper():
        return value.upper()  # Store "D6" as TEXT

    # Handle dual values (Littlejohn Adaptor)
    if '(' in value:
        base = value.split('(')[0].strip()
        enhanced = value.split('(')[1].replace(')', '').strip()
        log_warning(f"DUAL_VALUE: {field_name} has {value}, using base={base}, enhanced={enhanced}")
        return base  # Use base value, log enhanced for reference

    # Handle standard integers
    if value.isdigit():
        return int(value)

    # Handle decimals (caliber_mm only)
    try:
        return float(value)
    except ValueError:
        log_error(f"INVALID_FORMAT: {field_name}={value}")
        return None  # Invalid format, store as NULL
```

### TEXT Fields (Case Normalization)

**Fields**: nation, he_shell_classification, weapon_category, special_rules

**Nation Validation**:
```python
CANONICAL_NATIONS = ['german', 'british', 'italian', 'american', 'french',
                     'canadian', 'australian', 'indian', 'south_african',
                     'new_zealand', 'polish', 'free_french']

def normalize_nation(value):
    """Accept comma-separated, normalize case, validate against canonical."""
    if not value:
        return None

    nations = [n.strip().lower() for n in value.split(',')]
    invalid = [n for n in nations if n not in CANONICAL_NATIONS]

    if invalid:
        log_warning(f"INVALID_NATION: {invalid}, valid={CANONICAL_NATIONS}")

    return ', '.join([n for n in nations if n in CANONICAL_NATIONS])
```

**HE Shell Classification**:
```python
KNOWN_CLASSIFICATIONS = ['v. light', 'light', 'medium', 'heavy',
                          'bomb', 'rocket', 'Cannon']

def validate_he_classification(value):
    """Accept known values, warn on unknown."""
    if not value:
        return None

    if value not in KNOWN_CLASSIFICATIONS:
        log_warning(f"UNKNOWN_CLASSIFICATION: {value}, known={KNOWN_CLASSIFICATIONS}")
        return value  # Accept anyway (may be legitimate special type)

    return value
```

### OPTIONAL Fields (Accept NULL)

**Fields**: ROF, common_name, weapon_category, max_range_inches, special_rules, all source_* fields

**Validation**: None required (NULL is valid)

---

## Validation Levels

### Level 1: CRITICAL (Import Fails)
- Missing name
- Missing nation
- Missing caliber_mm
- No HE and No AP data

**Action**: Reject row, log error, continue processing other rows

### Level 2: ERROR (Import Succeeds, Requires Review)
- Invalid nation value
- Invalid numeric format
- Dual values detected (Littlejohn)
- Dice formulas in unexpected fields

**Action**: Import row, log error, flag for manual review

### Level 3: WARNING (Import Succeeds, FYI)
- Partial range data (some bands empty)
- Unknown he_shell_classification
- Empty optional fields
- Unusual caliber values

**Action**: Import row, log warning, no review required

### Level 4: INFO (Logged for Reference)
- Successfully normalized values
- Auto-detected weapon categories
- Common name variants created

**Action**: Import row, log info, track statistics

---

## Validation Output Format

**Console Output**:
```
[IMPORT] british_datacards_ALL_GUNS_UPDATED.csv
[INFO] Processing 24 rows...

Row 1: Ordnance QF 25-pdr
  [+] Valid critical fields
  [+] HE data: 6/4+ with ranges
  [+] AP data: 0-40" ranges
  [INFO] Created variant: "25 pdr"

Row 17: 2 pdr (Littlejohn Adaptor)
  [+] Valid critical fields
  [!] WARNING: Dual values detected in AP fields (3(4))
  [!] Using base values (3), enhanced values logged (4)
  [!] RECOMMEND: Create separate gun record for enhanced version

Row 18: Flamethrower
  [+] Valid critical fields
  [!] WARNING: Dice formula in he_0_10 (D6)
  [INFO] Auto-flagged special_rule: variable_damage_D6

Row 14: 40mmL60
  [+] Valid critical fields
  [!] WARNING: HE data missing (AP only)
  [INFO] Auto-detected weapon_category: aa_gun

Summary:
  Total rows: 24
  Imported: 24
  Errors: 0 (requiring review)
  Warnings: 4 (flagged for attention)
  Info: 24 (successful operations)
```

**Database Logging** (import_log table):
```sql
INSERT INTO import_log (
    timestamp,
    operation,
    record_id,
    record_name,
    validation_level,
    message
) VALUES (
    '2025-11-05 14:32:01',
    'import_british_guns',
    17,
    '2 pdr (Littlejohn Adaptor)',
    'WARNING',
    'Dual values detected in ap_0_10: 3(4), using base=3, enhanced=4'
);
```

---

## Edge Case Handling

### Case 1: Dual Values (Littlejohn Adaptor)

**Input**: `ap_0_10 = "3(4)"`

**Parser Logic**:
```python
if '(' in value:
    base = value.split('(')[0].strip()  # "3"
    enhanced = value.split('(')[1].replace(')', '').strip()  # "4"

    # Store base value in database
    # Log enhanced value for reference
    # Recommend creating separate gun record

    return {
        'value': int(base),
        'warning': f'DUAL_VALUE: base={base}, enhanced={enhanced}',
        'recommendation': 'Create separate gun record for enhanced variant'
    }
```

**Database Action**: Store base (3), flag for review

**User Action**: Create two guns:
1. "2 pdr" → AP: 4, 4, 3, 2, 1, -
2. "2 pdr (Littlejohn Adaptor)" → AP: 3, 3, 2, 1, 1, -

### Case 2: Variable Damage (Flamethrower)

**Input**: `he_0_10 = "D6"`

**Parser Logic**:
```python
if 'D' in value.upper():
    # Store as TEXT (not INTEGER)
    # Auto-flag special rule

    return {
        'value': value.upper(),  # "D6"
        'special_rule': 'variable_damage_D6',
        'info': 'Dice formula detected, stored as TEXT'
    }
```

**Database Action**: Store "D6" as TEXT, add special_rule

### Case 3: Partial Range Data (AT Rifles)

**Input**: `ap_0_10=3, ap_10_20=2, ap_20_30=None, ap_30_40=None...`

**Validation**:
```python
def validate_range_bands(gun):
    """Accept partial data if ANY band has value."""
    he_bands = [gun.he_0_10, gun.he_10_20, gun.he_20_30,
                gun.he_30_40, gun.he_40_50, gun.he_50_70]
    ap_bands = [gun.ap_0_10, gun.ap_10_20, gun.ap_20_30,
                gun.ap_30_40, gun.ap_40_50, gun.ap_50_70]

    has_any_he = any(he_bands)
    has_any_ap = any(ap_bands)

    if not has_any_he and not has_any_ap:
        return "ERROR: No HE or AP data"

    # Count populated bands
    he_count = sum(1 for x in he_bands if x is not None)
    ap_count = sum(1 for x in ap_bands if x is not None)

    if he_count > 0 and he_count < 3:
        log_warning(f"Partial HE data: {he_count}/6 bands")
    if ap_count > 0 and ap_count < 3:
        log_warning(f"Partial AP data: {ap_count}/6 bands")

    return "VALID"  # Accept partial data
```

### Case 4: AA Guns Without HE

**Input**: `he_dice=None, ap_0_10=8, ap_10_20=7...`

**Validation**:
```python
if has_ap_data(gun) and not has_he_data(gun):
    log_info(f"AP-only weapon (likely AA gun)")
    auto_detect_category(gun, 'aa_gun')
    return "VALID"
```

### Case 5: Bombs Without AP

**Input**: `he_dice=8, he_0_10=6, ap_0_10=None...`

**Validation**:
```python
if has_he_data(gun) and not has_ap_data(gun):
    if gun.he_shell_classification in ['bomb', 'rocket']:
        log_info(f"HE-only weapon (aircraft ordnance)")
        auto_detect_category(gun, 'aircraft_weapon')
        return "VALID"
```

---

## Auto-Detection Logic

### Weapon Category

```python
def auto_detect_category(gun):
    """Infer weapon_category from caliber, data patterns, name."""

    # AA guns: High ROF, AP-only, caliber 20-40mm
    if gun.rof and gun.rof >= 6 and has_ap_only(gun):
        if 20 <= gun.caliber_mm <= 40:
            return 'aa_gun'

    # Infantry weapons: Small caliber, low ROF
    if gun.caliber_mm <= 20:
        if gun.rof and gun.rof <= 3:
            return 'at_rifle'
        else:
            return 'infantry_weapon'

    # Artillery: Large caliber, HE-focused
    if gun.caliber_mm >= 75:
        if has_he_data(gun):
            return 'field_artillery'

    # Anti-tank: Medium caliber, AP-focused
    if 37 <= gun.caliber_mm <= 90:
        if has_ap_data(gun) and gun.caliber_mm < 75:
            return 'at_gun'

    # Mortars: Indirect fire, HE-only
    if 'mortar' in gun.name.lower():
        return 'mortar'

    # Bombs/Rockets: Name-based
    if any(x in gun.name.lower() for x in ['bomb', 'rocket']):
        return 'aircraft_weapon'

    # Flamethrower: Special case
    if 'flame' in gun.name.lower():
        return 'flamethrower'

    return None  # Unknown, manual review
```

### Special Rules

```python
def auto_detect_special_rules(gun):
    """Infer special_rules from data patterns."""
    rules = []

    # Variable damage
    if any('D' in str(x) for x in [gun.he_0_10, gun.he_10_20] if x):
        rules.append('variable_damage_D6')

    # High ROF
    if gun.rof and gun.rof >= 8:
        rules.append('high_rate_of_fire')

    # One-shot weapons (bombs)
    if gun.he_shell_classification == 'bomb':
        rules.append('one_shot')

    # Open-topped (inferred from weapon type)
    # (This would come from vehicle, not gun)

    return ','.join(rules) if rules else None
```

---

## CSV Column Mapping

**British Guns CSV** (20 columns):
```
0:  name
1:  common_name
2:  nation
3:  caliber_mm
4:  ROF                    ← NEW (between caliber_mm and he_dice)
5:  he_dice
6:  he_target
7:  he_shell_classification
8:  he_0_10
9:  he_10_20
10: he_20_30
11: he_30_40
12: he_40_50
13: he_50_70
14: ap_0_10
15: ap_10_20
16: ap_20_30
17: ap_30_40
18: ap_40_50
19: ap_50_70
```

**Import Script Mapping**:
```python
def map_csv_row(row):
    """Map 20-column CSV to database fields."""
    return {
        'name': clean_value(row[0]),
        'common_name': clean_value(row[1]),
        'nation': normalize_nation(row[2]),
        'caliber_mm': parse_numeric_field(row[3], 'caliber_mm'),
        'rof': parse_numeric_field(row[4], 'rof'),
        'he_dice': parse_numeric_field(row[5], 'he_dice'),
        'he_target': clean_value(row[6]),
        'he_shell_classification': validate_he_classification(row[7]),
        'he_0_10': parse_numeric_field(row[8], 'he_0_10'),
        'he_10_20': parse_numeric_field(row[9], 'he_10_20'),
        'he_20_30': parse_numeric_field(row[10], 'he_20_30'),
        'he_30_40': parse_numeric_field(row[11], 'he_30_40'),
        'he_40_50': parse_numeric_field(row[12], 'he_40_50'),
        'he_50_70': parse_numeric_field(row[13], 'he_50_70'),
        'ap_0_10': parse_numeric_field(row[14], 'ap_0_10'),
        'ap_10_20': parse_numeric_field(row[15], 'ap_10_20'),
        'ap_20_30': parse_numeric_field(row[16], 'ap_20_30'),
        'ap_30_40': parse_numeric_field(row[17], 'ap_30_40'),
        'ap_40_50': parse_numeric_field(row[18], 'ap_40_50'),
        'ap_50_70': parse_numeric_field(row[19], 'ap_50_70'),
        # Auto-detected fields
        'weapon_category': None,  # Filled by auto_detect_category()
        'special_rules': None,    # Filled by auto_detect_special_rules()
    }
```

---

## Import Success Criteria

**Import is successful when**:
1. All CRITICAL fields validated (name, nation, caliber, HE or AP)
2. All rows processed (even if some have warnings)
3. Validation log generated
4. gun_name_variants created for common_name entries
5. Statistics reported (total, errors, warnings, info)

**Import fails when**:
- CSV file not found
- CSV encoding error (retry with windows-1252)
- Database connection error
- Critical field missing in >50% of rows

**Post-Import Actions**:
1. Review ERROR-level items (dual values, invalid formats)
2. Review WARNING-level items (partial data, unknown classifications)
3. Update weapon_category for NULL entries
4. Update special_rules for NULL entries
5. Create variant gun records (Littlejohn, etc.)
6. Create vehicle variants (Tetrarch, etc.)

---

## OCR Adaptation Notes

**Same parser works for OCR because**:
- Accepts variable formats (OCR may produce "D 6" vs "D6")
- Handles missing data (OCR may skip empty cells)
- Flexible numeric parsing (OCR may produce "O" vs "0")
- Validation warnings guide correction

**OCR-Specific Enhancements**:
```python
def ocr_normalize(value):
    """Common OCR error corrections."""
    if not value:
        return None

    value = str(value).strip()

    # Common OCR mistakes
    replacements = {
        'O': '0',  # Letter O → Zero
        'l': '1',  # Lowercase L → One
        'I': '1',  # Uppercase I → One
        'S': '5',  # Sometimes S → 5
        'B': '8',  # Sometimes B → 8
    }

    # Apply only if entire value is suspect
    if value in replacements:
        log_info(f"OCR_CORRECTION: {value} → {replacements[value]}")
        return replacements[value]

    return value
```

**Future OCR workflow**:
1. OCR extraction → raw CSV
2. Run ocr_normalize() on all fields
3. Run standard flexible parser
4. Review ERROR + WARNING items
5. Manual correction of flagged items
6. Re-import corrected CSV

---

## Testing Strategy

**Test Cases** (24 British guns provide coverage):

1. **Standard gun**: 25-pdr (complete HE + AP data)
2. **Dual values**: 2 pdr Littlejohn (3(4) format)
3. **Variable damage**: Flamethrower (D6 format)
4. **AA gun**: 40mmL60 (AP only, no HE)
5. **Bomb**: Large bomb (HE only, no AP)
6. **Partial data**: AT rifle (short range only)
7. **Empty ROF**: Most guns (18/24 have empty ROF)
8. **Special classification**: Rocket (non-standard he_shell_classification)

**Import Test**:
```bash
python scripts/battlegroup/manual_extraction/import_british_datacards_guns.py \
    --csv "D:/north-africa-toe-builder/british_datacards_ALL_GUNS_UPDATED.csv" \
    --validate-only  # Dry run, no database changes

# Review validation output
# Fix critical errors
# Re-run with --commit flag
```

---

**Status**: Specification complete, ready for implementation
**Next**: Update import_british_datacards_guns.py with flexible parser
