# Weapon Category Classification System

**Date**: November 5, 2025
**Purpose**: Auto-detection algorithms for weapon_category field
**Scope**: BattleGroup game system weapon taxonomy

---

## Classification Architecture

### Multiple Overlapping Systems

BattleGroup uses **THREE classification dimensions**:

1. **weapon_category** (PRIMARY) - What IS it?
   - rifle, mg, at_gun, aa_gun, field_artillery, mortar, flamethrower, bomb, rocket, etc.

2. **he_shell_classification** (SIZE) - How BIG is the HE shell?
   - v. light, light, medium, heavy, bomb, rocket, Cannon

3. **gun_role** (FUTURE) - What does it DO?
   - anti_tank, anti_aircraft, infantry_support, field_artillery, close_support

**Example**: 88mm FlaK 36
- weapon_category: `aa_gun` (it's an AA gun)
- he_shell_classification: `heavy` (large HE shells)
- gun_role: `anti_aircraft, anti_tank` (dual-purpose)

---

## weapon_category Taxonomy

### Infantry Weapons

**rifle**:
- Caliber: ≤ 15mm
- ROF: 1-2
- Examples: Lee-Enfield, Kar98k, M1 Garand

**at_rifle** (Anti-Tank Rifle):
- Caliber: 13-20mm
- ROF: 1-3
- AP data only (no HE)
- Examples: Boys AT Rifle (14mm), PTRD-41 (14.5mm), Panzerbüchse 39 (7.92mm)

**lmg** (Light Machine Gun):
- Caliber: 7-8mm
- ROF: 4-6
- Examples: Bren gun, MG34 (bipod), BAR

**hmg** (Heavy Machine Gun):
- Caliber: 12-15mm
- ROF: 6-8
- Examples: Vickers .50 cal, Browning M2 HMG

**smg** (Submachine Gun):
- Caliber: 9-11mm
- ROF: 6-10
- Short range only
- Examples: Sten, MP40, Thompson

### Anti-Tank Guns

**at_gun**:
- Caliber: 37-90mm
- AP-focused (may have limited HE)
- Medium ROF (1-3)
- Examples: 2 pdr (40mm), 6 pdr (57mm), PAK 40 (75mm), 17 pdr (76mm)

**at_gun_heavy**:
- Caliber: 88-128mm
- Dual-purpose (AT + AA)
- Examples: 88mm FlaK, 90mm M1

### Anti-Aircraft Guns

**aa_gun_light**:
- Caliber: 20-40mm
- ROF: 6-10 (very high)
- AP only (no HE typically)
- Examples: 20mm Oerlikon, 40mm Bofors, FlaK 38

**aa_gun_heavy**:
- Caliber: 75-128mm
- ROF: 3-6
- Dual-purpose (AA + AT)
- Examples: 88mm FlaK 36/37, 90mm M1, 128mm FlaK 40

### Field Artillery

**field_artillery_light**:
- Caliber: 75-105mm
- HE-focused
- Examples: 25 pdr (87.6mm), 105mm Howitzer M2

**field_artillery_medium**:
- Caliber: 114-155mm
- HE only
- Examples: 5.5" gun (140mm), 155mm Long Tom

**field_artillery_heavy**:
- Caliber: 149-240mm
- HE only, indirect fire
- Examples: 149mm sFH 18, 8" howitzer (203mm)

### Mortars

**mortar_light**:
- Caliber: 50-60mm
- Infantry support
- Examples: 2" mortar (51mm), 50mm Granatenwerfer 36

**mortar_medium**:
- Caliber: 75-82mm
- Company/battalion level
- Examples: 3" mortar (76mm), 81mm M1

**mortar_heavy**:
- Caliber: 100-120mm
- Regiment level
- Examples: 4.2" mortar (107mm), 120mm PM-38

### Tank Guns

**tank_gun_light**:
- Caliber: 37-50mm
- Mounted in light/medium tanks
- Examples: 37mm M6, 2 pdr, 50mm KwK 38

**tank_gun_medium**:
- Caliber: 57-76mm
- Medium/heavy tanks
- Examples: 6 pdr, 75mm M3, 76mm M1, 75mm KwK 40

**tank_gun_heavy**:
- Caliber: 88-128mm
- Heavy tanks, tank destroyers
- Examples: 88mm KwK 36, 90mm M3, 122mm D-25T

### Special Weapons

**flamethrower**:
- Variable damage (D6)
- Short range only
- Special rules: one_shot, variable_damage_D6
- Examples: Wasp flamethrower, Churchill Crocodile

**bomb**:
- Aircraft-delivered
- HE only, no AP
- Special rules: one_shot
- Examples: 250lb bomb, 500lb bomb, 1000lb bomb

**rocket**:
- Aircraft or vehicle mounted
- HE focused
- Examples: 60lb rocket, RP-3 rocket, Nebelwerfer rocket

**demolition_charge**:
- Infantry-placed
- HE only, close range
- Examples: Satchel charge, Bangalore torpedo

**grenade**:
- Hand-thrown
- Very short range
- Examples: Mills bomb, Stielhandgranate

---

## Auto-Detection Algorithm

### Decision Tree

```python
def auto_detect_weapon_category(gun):
    """
    Multi-factor classification based on:
    - caliber_mm (primary factor)
    - ROF (rate of fire)
    - HE/AP data patterns
    - Name keywords
    """

    caliber = gun.caliber_mm
    rof = gun.rof or 0  # Default to 0 if NULL
    name_lower = gun.name.lower()

    has_he = gun.he_dice is not None
    has_ap = any([gun.ap_0_10, gun.ap_10_20, gun.ap_20_30])

    # SPECIAL CASES (name-based, highest priority)
    if 'flame' in name_lower:
        return 'flamethrower'
    if 'bomb' in name_lower:
        return 'bomb'
    if 'rocket' in name_lower:
        return 'rocket'
    if 'mortar' in name_lower:
        return classify_mortar(caliber)
    if 'grenade' in name_lower:
        return 'grenade'

    # ANTI-AIRCRAFT GUNS (high ROF + AP-only)
    if rof >= 6 and has_ap and not has_he:
        if 20 <= caliber <= 40:
            return 'aa_gun_light'
        elif caliber >= 75:
            return 'aa_gun_heavy'

    # DUAL-PURPOSE AA/AT GUNS (88mm, 90mm)
    if 85 <= caliber <= 128 and has_he and has_ap:
        if '88' in name_lower or 'flak' in name_lower:
            return 'aa_gun_heavy'

    # INFANTRY WEAPONS (small caliber)
    if caliber <= 20:
        if has_ap and not has_he:
            return 'at_rifle'
        if rof >= 6:
            if caliber <= 12:
                return 'smg'
            else:
                return 'hmg'
        if rof >= 4:
            return 'lmg'
        return 'rifle'

    # ANTI-TANK GUNS (medium caliber, AP-focused)
    if 37 <= caliber < 90 and has_ap:
        if has_he and caliber >= 75:
            return 'at_gun_heavy'  # Dual-purpose
        return 'at_gun'

    # FIELD ARTILLERY (large caliber, HE-focused)
    if caliber >= 75 and has_he:
        if caliber < 114:
            return 'field_artillery_light'
        elif caliber < 160:
            return 'field_artillery_medium'
        else:
            return 'field_artillery_heavy'

    # TANK GUNS (vehicle-mounted)
    if 'kwk' in name_lower or 'tank gun' in name_lower:
        if caliber < 57:
            return 'tank_gun_light'
        elif caliber < 88:
            return 'tank_gun_medium'
        else:
            return 'tank_gun_heavy'

    # DEFAULT: Unknown, manual classification needed
    return None


def classify_mortar(caliber):
    """Sub-classifier for mortars by caliber."""
    if caliber < 75:
        return 'mortar_light'
    elif caliber < 100:
        return 'mortar_medium'
    else:
        return 'mortar_heavy'
```

### Confidence Scoring

```python
def get_classification_confidence(gun, detected_category):
    """
    Score 0-100 based on how certain the classification is.
    """
    confidence = 50  # Base confidence

    name_lower = gun.name.lower()

    # High confidence (name keywords match)
    if detected_category == 'flamethrower' and 'flame' in name_lower:
        confidence = 100
    if detected_category == 'bomb' and 'bomb' in name_lower:
        confidence = 100
    if detected_category == 'mortar_*' and 'mortar' in name_lower:
        confidence = 95

    # Medium-high confidence (caliber + data pattern)
    if detected_category == 'at_gun' and 37 <= gun.caliber_mm < 90:
        if gun.ap_0_10 and not gun.he_dice:
            confidence = 90
        elif gun.ap_0_10 and gun.he_dice:
            confidence = 80

    # Medium confidence (caliber alone)
    if detected_category == 'field_artillery_light' and 75 <= gun.caliber_mm < 114:
        confidence = 75

    # Low confidence (ambiguous)
    if detected_category is None:
        confidence = 0  # Manual classification required

    return confidence
```

---

## Classification Examples

### British Guns (24 examples)

| Gun Name | Caliber | ROF | HE | AP | Auto-Detected Category | Confidence |
|----------|---------|-----|----|----|------------------------|------------|
| Ordnance QF 25-pdr | 87.6 | - | ✓ | ✓ | field_artillery_light | 85 |
| Ordnance QF 6-pdr 7cwt | 57 | - | - | ✓ | at_gun | 90 |
| Ordnance QF 2-pdr | 40 | - | - | ✓ | at_gun | 90 |
| 40mmL60 Bofors | 40 | 8 | - | ✓ | aa_gun_light | 95 |
| 20mm Oerlikon | 20 | 10 | - | ✓ | aa_gun_light | 95 |
| Boys AT Rifle | 14 | 2 | - | ✓ | at_rifle | 100 |
| Flamethrower | - | - | D6 | - | flamethrower | 100 |
| Large bomb | - | - | ✓ | - | bomb | 100 |
| 60 lbs Rocket | - | - | ✓ | - | rocket | 100 |
| 3" mortar | 76 | - | ✓ | - | mortar_medium | 95 |
| 2" mortar | 51 | - | ✓ | - | mortar_light | 95 |

### German Guns (hypothetical)

| Gun Name | Caliber | ROF | Category | Confidence |
|----------|---------|-----|----------|------------|
| 88mm FlaK 36 | 88 | 4 | aa_gun_heavy | 95 |
| 75mm PAK 40 | 75 | 2 | at_gun | 90 |
| 50mm KwK 38 | 50 | 3 | tank_gun_light | 85 |
| 105mm leFH 18 | 105 | - | field_artillery_light | 85 |
| 150mm sFH 18 | 150 | - | field_artillery_medium | 85 |
| 81mm Granatenwerfer 34 | 81 | - | mortar_medium | 95 |
| 20mm FlaK 38 | 20 | 10 | aa_gun_light | 95 |

---

## Edge Cases and Manual Review

### Ambiguous Classifications

**88mm FlaK 36**:
- Could be: `aa_gun_heavy` (primary role) OR `at_gun_heavy` (secondary)
- Decision: Use **primary role** → `aa_gun_heavy`
- Store secondary in `gun_role` field → `anti_aircraft, anti_tank`

**75mm Gun M2/M3 (Sherman)**:
- Could be: `tank_gun_medium` OR `field_artillery_light`
- Decision: Context matters (vehicle-mounted) → `tank_gun_medium`

**Howitzer vs Gun**:
- Howitzer: High-angle fire, HE-focused → `field_artillery_*`
- Gun: Flat trajectory, AP capable → `at_gun` or `tank_gun`

### Manual Override Required

**Weapons requiring human review** (confidence < 70):
1. Dual-purpose guns (88mm FlaK, 90mm M1)
2. Improvised weapons (captured equipment repurposed)
3. Experimental weapons (squeeze-bore, discarding sabot)
4. Multi-role weapons (tank guns used as AT guns)

**Import Process**:
```python
category = auto_detect_weapon_category(gun)
confidence = get_classification_confidence(gun, category)

if confidence < 70:
    log_warning(f"MANUAL_REVIEW: {gun.name} classified as {category} (confidence={confidence})")
    # Flag for manual review, but accept tentative classification
```

---

## Database Integration

### Schema Addition

```sql
ALTER TABLE bg_reference_guns
ADD COLUMN weapon_category TEXT DEFAULT NULL;

ALTER TABLE bg_reference_guns
ADD COLUMN category_confidence INTEGER DEFAULT NULL;

ALTER TABLE bg_reference_guns
ADD COLUMN gun_role TEXT DEFAULT NULL;  -- Comma-separated: "anti_tank,anti_aircraft"
```

### Auto-Population Script

```python
def populate_weapon_categories():
    """Run auto-detection on all guns in database."""
    conn = sqlite3.connect('database/master_database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, caliber_mm, rof, he_dice, ap_0_10 FROM bg_reference_guns")
    guns = cursor.fetchall()

    for gun_id, name, caliber_mm, rof, he_dice, ap_0_10 in guns:
        gun_obj = Gun(id=gun_id, name=name, caliber_mm=caliber_mm,
                      rof=rof, he_dice=he_dice, ap_0_10=ap_0_10)

        category = auto_detect_weapon_category(gun_obj)
        confidence = get_classification_confidence(gun_obj, category)

        cursor.execute("""
            UPDATE bg_reference_guns
            SET weapon_category = ?,
                category_confidence = ?
            WHERE id = ?
        """, (category, confidence, gun_id))

        if confidence < 70:
            print(f"[!] REVIEW: {name} → {category} ({confidence}%)")
        else:
            print(f"[+] {name} → {category} ({confidence}%)")

    conn.commit()
    conn.close()
```

---

## Validation Rules

### Category Completeness

**After auto-detection**:
- 80%+ should have category assigned (confidence ≥ 70)
- 20% manual review acceptable

**Quality Thresholds**:
- Confidence ≥ 90: Auto-accept
- Confidence 70-89: Auto-accept, log for spot-check
- Confidence < 70: Flag for mandatory manual review

### Cross-Validation

**Check category vs caliber**:
```python
def validate_category_caliber(gun):
    """Ensure category matches expected caliber range."""
    expected_ranges = {
        'at_rifle': (13, 20),
        'at_gun': (37, 90),
        'aa_gun_light': (20, 40),
        'field_artillery_light': (75, 114),
        'mortar_medium': (75, 99),
    }

    if gun.weapon_category in expected_ranges:
        min_cal, max_cal = expected_ranges[gun.weapon_category]
        if not (min_cal <= gun.caliber_mm <= max_cal):
            log_warning(f"CALIBER_MISMATCH: {gun.name} is {gun.weapon_category} but {gun.caliber_mm}mm")
```

**Check category vs HE/AP data**:
```python
def validate_category_data(gun):
    """Ensure category matches expected data patterns."""
    if gun.weapon_category == 'bomb':
        if gun.ap_0_10:
            log_error(f"DATA_ERROR: Bomb should not have AP data: {gun.name}")

    if gun.weapon_category == 'aa_gun_light':
        if gun.he_dice:
            log_warning(f"UNUSUAL: AA gun has HE data: {gun.name}")
```

---

## Future Enhancements

### Machine Learning Classification

**If dataset grows** (500+ guns):
- Train classification model on manually-reviewed guns
- Features: caliber, ROF, HE/AP ratios, name tokens
- Output: category + confidence score
- Fallback to rule-based for edge cases

### Multi-Language Support

**German gun names**:
- KwK → Kampfwagenkanone → tank_gun
- PaK → Panzerabwehrkanone → at_gun
- FlaK → Flugabwehrkanone → aa_gun
- leFH → leichte Feldhaubitze → field_artillery_light
- sFH → schwere Feldhaubitze → field_artillery_heavy

**Russian gun names**:
- ZiS → Zavod imeni Stalina → at_gun or field_artillery
- D-series → Degtyaryov → various (context-dependent)

### Context-Aware Classification

**Vehicle-mounted weapons**:
- Same gun may be different category based on mount
- 75mm M3 on Sherman → tank_gun_medium
- 75mm M2 on carriage → field_artillery_light

**Solution**: Separate `vehicle_weapon_category` vs `towed_weapon_category`

---

**Status**: Classification system designed, algorithms specified
**Next**: Implement in import script, run auto-detection on existing 26 Canadian guns
