# BattleGroup Weapon System Research

**Date**: November 5, 2025
**Source**: BattleGroup Rules.txt + British ROF for small arms.png
**Purpose**: Complete analysis of weapon mechanics for database schema design

---

## Executive Summary

This document contains comprehensive research findings from analyzing the BattleGroup tabletop wargame rules to ensure our gun reference database can properly handle all weapon types, special mechanics, and edge cases.

**Key Findings**:
- 30+ distinct weapon types identified across multiple classification systems
- Complex overlapping categorization (by type, role, size, mount)
- Rate of Fire (ROF) is core mechanic for all weapons
- Variable damage patterns (D6 for flamethrowers)
- Dual value systems (AP + HE with different mechanics)
- Special weapon classes (bombs, rockets, flamethrowers) require unique handling

---

## 1. Weapon Categories (Primary Classification)

### Infantry Small Arms

| Weapon Type | ROF | Max Range | Characteristics |
|-------------|-----|-----------|-----------------|
| **Rifles** | 1 | 30" | Standard infantry rifles |
| **SMG** (Sub-Machine Guns) | 1(2*) | 10" | ROF 2 in close assault (<5") |
| **Light MG** (Squad Support) | 2 | 30" | Bren, BAR, etc. |
| **Medium MG** (Crew-Served) | 5 | 30-40" | Vickers, MG34/42 on tripod |
| **Heavy MG** (AA Capable) | 6 | 40" | M2 .50 cal, DshK |
| **MG-34** (bipod) | 6 | 30" | German versatile MG |
| **MG-34** (tripod) | 8 | 40" | Deployed configuration |
| **MG-42** (bipod) | 6 | 30" | Advanced German MG |
| **MG-42** (tripod) | 8 | 40" | Deployed configuration |

### Vehicle-Mounted Machine Guns

| Mount Type | ROF | Max Range | Notes |
|------------|-----|-----------|-------|
| **Tank MG** (bow) | 3 | 30" | Hull-mounted |
| **Tank MG** (co-axial) | 3 | 30" | Turret-linked to main gun |
| **Pintle-mounted MG** | 5 | 40" | Swivel mount, often AA |

### Cannons & Autocannons

| Type | ROF | Max Range | HE | Notes |
|------|-----|-----------|----|----|
| **Light Autocannon** (20mm) | 6 | 50" | Very Light | AA-capable |
| **Heavy Autocannon** (37mm, 40mm) | 8 | 50" | Very Light | AA-capable |
| **Multiple Autocannons** | 10 | 50" | 2× Very Light | Dual/quad AA mount |
| **Multiple MG mount** | 10 | 30" | - | Quad MG AA mount |

### Anti-Tank Guns

| Type | Caliber Range | Primary Role | HE Capability |
|------|---------------|--------------|---------------|
| **Light AT** | 37-50mm | Early war AT | Limited/None |
| **Medium AT** | 57-76mm | Mid war AT | Some HE |
| **Heavy AT** | 88-128mm | Late war AT | Dual purpose |

### Field Artillery & Howitzers

| Type | Caliber Range | HE Rating | Range | Notes |
|------|---------------|-----------|-------|-------|
| **Light Field Gun** | 75-88mm | Light-Medium | 60-120" | Flat trajectory |
| **Medium Howitzer** | 105-122mm | Medium | 90-180" | High angle |
| **Heavy Howitzer** | 150-203mm | Heavy | 120-240" | Long range |

### Mortars

| Type | Caliber | HE Rating | Range | Special |
|------|---------|-----------|-------|---------|
| **Medium Mortar** | 80-82mm, 3" | 4/4+ | 10-90" | Minimum range 10" |
| **Heavy Mortar** | 120mm, 4.2" | 6/4+ | 15-240" | Minimum range 15" |

### Special Weapons

| Weapon | ROF | Range | Damage | Special Rules |
|--------|-----|-------|--------|---------------|
| **Man-pack Flamethrower** | 10 | 5" | D6 HE | One shot, Open cover save |
| **Vehicle Flamethrower** | 10 | 10" | D6 HE | Multi-shot, Open cover save |
| **Anti-Tank Grenades** | - | 5" | Varies | Infantry close assault |
| **Grenades** | +1 D6 | 5" | - | Adds to ROF in close assault |

### Aircraft Ordnance

| Type | Format | HE | AP | Notes |
|------|--------|----|----|-------|
| **Large bomb** | - | 11/2+ | - | 15 HE at all ranges |
| **Medium bomb** | - | 7/3+ | - | 9 HE at all ranges |
| **Small bomb** | - | 7/3+ | - | 9 HE at all ranges |
| **60 lbs Rocket** | - | 5/4+ | - | 8 HE at 20-30" only |
| **Aircraft Cannon** (20mm) | - | Cannon | 4-3 AP | Multi-role |

---

## 2. Special Mechanics

### Rate of Fire (ROF) System

**Core Mechanic**: ROF = number of D6 rolled for aimed fire

**Variable ROF Conditions**:
- SMGs: ROF 1 normally, **ROF 2 in close assault** (<5")
- MGs: ROF **halved** if reduced crew (casualties)
- Aircraft MGs: ROF 3 per gun, **limited to 3 shots/game**
- Multiple AA mounts: ROF 10, can **roll twice** for Area Fire

**ROF Value Ranges**:
- 1: Rifles, SMGs (normal)
- 2: Light MGs, SMGs (assault)
- 3: Tank MGs
- 5: Medium MGs, pintle mounts
- 6: Heavy MGs, autocannons, deployed MG-34/42
- 8: Heavy autocannons, deployed MG-42
- 10: Flamethrowers, multiple mounts

### HE (High Explosive) System

**Dual Value Format**: "X/Y+"
- **X**: Number of D6 rolled for damage
- **Y+**: Target number needed on each die

**Examples**:
- "4/4+": Roll 4 dice, hit on 4, 5, or 6
- "6/3+": Roll 6 dice, hit on 3, 4, 5, or 6
- "11/2+": Roll 11 dice, hit on 2, 3, 4, 5, or 6

**HE Shell Classification** (by gun size):
- **Very Light HE**: Light autocannons, small guns (<50mm)
- **Light HE**: 37-76mm guns, medium mortars (80-82mm)
- **Medium HE**: 75-105mm guns
- **Heavy HE**: 105mm+ guns, heavy mortars (120mm+)

**HE Range Effectiveness**:
- HE effectiveness can vary by range (stored as he_0_10 through he_50_70)
- Most guns maintain constant HE, some decrease at long range
- Mortars have minimum + maximum range restrictions

### AP (Armor Penetration) System

**Penetration Scale**: 1-15
- 1 = Weakest penetration (machine guns)
- 7-11 = Medium AT guns (2 pdr, 6 pdr, 75mm)
- 12-15 = Heavy AT guns (17 pdr, 88mm, 128mm)

**Range-Banded Values**:
- 0-10" band (point blank)
- 10-20" band
- 20-30" band
- 30-40" band (medium range)
- 40-50" band
- 50-70" band (long range - heavy AT guns only)

**AP decreases with range** (penetration weakens at distance)

**Armor Scale**: A-O (letter system)
- A = Thickest armor (Tiger, Panther frontal)
- K-M = Medium armor (Sherman, Panzer IV)
- O = Thinnest armor (light tanks, soft vehicles)

**Hit Resolution**: Roll 2D6 vs penetration table
- Greater than target = **Destroyed**
- Equal to target = **Pinned**
- Less than target = **Glancing hit** (morale test only)

### Variable Damage (Dice Formulas)

**D6**: Used for flamethrower HE damage
- Man-pack: D6 HE at 5" range
- Vehicle: D6 HE at 10" range
- Represents variable flame coverage/intensity

**D3**: Tank rider casualties (D6÷2, round up)
- When vehicle destroyed, riders take D3 casualties
- NOT a weapon stat, game mechanic

**2D6**: Armor penetration resolution
- NOT a weapon stat, hit resolution mechanic

**No other dice formulas found** in weapon stat tables

### Dual Values (Conditional Stats)

**Littlejohn Adaptor Example**: `3(4)`, `3(4)`, `2(3)`, `1(2)`, `1(2)`
- Squeeze-bore adaptor for 2 pdr gun
- Base value: 3 AP
- Enhanced value: 4 AP (with adaptor)
- Represents equipment upgrade affecting penetration

**SMG Variable ROF**: `1(2*)`
- Base: 1 ROF
- Enhanced: 2 ROF in close assault
- Conditional based on range/situation

**Format Pattern**: `BASE(ENHANCED)`
- Store base value in database
- Enhanced value in parentheses
- Indicates conditional or upgraded stat

---

## 3. Anti-Aircraft (AA) Weapons

### AA-Capable Weapons

**Dedicated AA Weapons**:
- Heavy MG (M2 .50 cal, DshK)
- Light Autocannons (20mm Oerlikon, Flak 38)
- Heavy Autocannons (37mm, 40mm Bofors)
- Multiple MG mounts (quad .50 cal)
- Multiple autocannon mounts (quad 20mm)

**Dual-Purpose Guns** (AA + AT/Artillery):
- 88mm Flak gun
- 37mm autocannon
- 40mm Bofors

### AA Mechanics

**Area Fire Rules**:
- All weapons can engage aircraft using Area Fire
- Aircraft get **no cover saves** (no cover in sky)
- If aircraft pinned by Area Fire, roll D6:
  - **4+**: Aircraft **damaged** (takes 1 hit)
  - **Multiple-mount weapons**: Aircraft takes **2 hits** if damaged
- Aircraft must take morale test when damaged

**Multiple Mount Bonus**:
- ROF 10
- Roll **twice** for Area Fire
- Counts as **Very Light HE** (autocannons only)
- Examples: Quad .50 cal, Quad 20mm, Wirbelwind

---

## 4. Weapon Mounting Types

| Mount Type | Description | Traverse | Examples |
|------------|-------------|----------|----------|
| **Turret** | Full traverse main gun | 360° | Tank main guns |
| **Hull** | Fixed forward mount | 45° arc | Assault guns, hull MGs |
| **Co-axial** | Turret-mounted MG | Linked to main gun | Tank MGs |
| **Bow** | Hull front MG | Limited arc | Early tanks |
| **Pintle** | Swivel mount | 180-360° | AA MGs |
| **Sponson** | Side-mounted weapon | 90° arc | WW1 tanks, rare |
| **Multiple mount** | Dual/quad configuration | Varies | AA weapons |

---

## 5. Ammunition Types

Referenced in BattleGroup rules:

| Type | Full Name | Purpose | Notes |
|------|-----------|---------|-------|
| **AP** | Armor Piercing | Standard AT | Solid shot or capped |
| **HE** | High Explosive | Anti-personnel, area | Fragmentation |
| **HEAT** | High Explosive Anti-Tank | Shaped charge AT | Range-independent penetration |
| **APCR** | Armor Piercing Composite Rigid | Enhanced AT | Tungsten core |
| **APDS** | Armor Piercing Discarding Sabot | Advanced AT | Sub-caliber penetrator |
| **HVAP** | High Velocity Armor Piercing | US enhanced AT | Similar to APCR |
| **AP40** | German tungsten AP | Enhanced AT | Limited availability |
| **Smoke** | Obscuration rounds | Blocking LOS | Mortars/artillery only |

**Game Mechanic**: Different ammo types not stored as separate stats
- Gun has single AP/HE rating
- Ammo type is flavor/narrative
- Exception: Some guns have multiple AP values representing different ammo

---

## 6. Special Rules & Abilities

### Weapon Special Rules

| Rule | Effect | Weapons |
|------|--------|---------|
| **Scout** | +1 to spot rolls | Recon vehicles |
| **Artillery Spotter** | Can call indirect fire | Forward observers |
| **Mortar Spotter** | Can call mortar fire | Infantry leaders |
| **Air Spotter** | Can call air strikes | Dedicated spotters |
| **Loader Team** | Extra shot if test passed | Some AT guns |
| **Open Cover Save** | Forces worse cover saves | Flamethrowers |
| **One Shot** | Single use only | Man-pack flamethrowers |
| **Limited Ammunition** | 3 shots per game | Aircraft weapons |
| **Schürzen** | +1 armor vs AP ≤5 | German side skirts |
| **Variable Damage** | Dice formula damage | Flamethrowers (D6) |
| **Multiple Mount** | Roll twice Area Fire | AA mounts |

---

## 7. British ROF Table (from Image)

| Weapon | ROF | Max Range | Crew | Special Notes |
|--------|-----|-----------|------|---------------|
| Rifle | 1 | 30" | - | Standard infantry |
| SMG | 1(2*) | 10" | - | *ROF 2 during Infantry Assault |
| Bren LMG | 2 | 30" | - | Squad support |
| Vickers HMG | 6 | 40" | 3 | On tripod |
| Tank MG (coax/bow) | 3 | 30" | - | Vehicle-mounted |
| Pintle-mounted MG | 5 | 40" | - | Swivel AA mount |
| Light Autocannon | 6 | 50" | 2 | Very light HE |
| Heavy Autocannon | 8 | 50" | 3 | Very light HE |
| Multiple Autocannons | 10 | 50" | 2 | 2× very light HE |
| Multiple MG mount | 10 | 30" | 3 | Quad MG |
| Man-pack Flamethrower | 10 | 5" | 1 | Open cover save, One shot |
| Vehicle Flamethrower | 10 | 10" | - | Open cover save |

---

## 8. Classification System Complexity

BattleGroup uses **multiple overlapping classification systems**:

### By Physical Type
- Rifle, SMG, MG, Autocannon, Gun, Howitzer, Mortar, Flamethrower

### By Role
- Anti-Tank (AT), Anti-Aircraft (AA), Field Artillery, Infantry Support, Tank Gun

### By Size (HE Classification)
- Very Light, Light, Medium, Heavy

### By Mount
- Vehicle, Infantry, Deployed, Multiple Mount

**Implication**: Database needs **multiple category fields**, not just one "type"

---

## 9. Data Relationships

### Small Arms (Rifles, MGs)
- Use **ROF + range**
- Usually **no AP/HE values** (or very low)
- Crew requirements vary
- Mount type important

### Guns & Artillery
- Have **AP range bands**
- Have **HE dual values** (dice/target)
- Caliber determines size class
- Role determines primary use

### Mortars
- **HE only** (no AP)
- **Minimum + maximum range** (not just max)
- Indirect fire capable
- Crew-served

### Flamethrowers
- **Special case**: D6 variable damage
- **Fixed ROF 10**, short range
- **Special rules**: One shot (man-pack), Open cover save
- No AP capability

### AA Weapons
- Can be: MGs, autocannons, or dual-purpose guns
- **ROF important** (high ROF for AA effectiveness)
- Multiple mounts: ROF 10, roll twice
- Some have AP capability (dual-purpose)

---

## 10. Schema Design Implications

### Required Fields

**Identification**:
- name, common_name (alias), nation, caliber_mm

**Weapon Stats**:
- rof (Rate of Fire, 1-10)
- he_dice, he_target (HE dual value)
- he_0_10 through he_50_70 (HE range bands)
- ap_0_10 through ap_50_70 (AP range bands)

**Classification**:
- weapon_category (primary type)
- he_shell_classification (size class)
- gun_role (primary purpose)

**Game Mechanics**:
- max_range_inches, min_range_inches (optional for mortars)
- crew_required
- special_rules (comma-separated)
- mount_types (where mountable)

**Provenance**:
- source_file, source_page, extraction_method, etc.

### Field Type Considerations

**Numeric Fields That Accept TEXT**:
- he_0_10 through he_50_70: Can be number OR "D6"
- ap_0_10 through ap_50_70: Can be number OR dual value "3(4)"
- Store as TEXT, validate format, parse when needed

**Optional vs Required**:
- MUST have: name, nation, caliber_mm
- MUST have: AP data OR HE data (at least one)
- CAN be empty: ROF (not all weapons specify), crew, min_range

**Multiple Values**:
- special_rules: Comma-separated TEXT
- mount_types: Comma-separated TEXT
- ammunition_types: Comma-separated TEXT (for reference)

---

## 11. Edge Cases Discovered

### From British DataCards Manual Entry:

1. **D6 Variable Damage**: Flamethrowers
2. **Dual AP Values**: Littlejohn Adaptor `3(4)`
3. **AA Guns**: AP only, no HE
4. **Bombs/Rockets**: HE only, no AP
5. **Empty ROF**: Many guns don't specify ROF
6. **Classification Values**: "v. light", "Cannon", "bomb", "rocket"
7. **Partial Range Bands**: Some guns only have close-range AP

### Anticipated (Other Nations):

1. **Squeeze-bore guns**: German Gerlich principle weapons
2. **APCR variants**: Dual penetration values
3. **Experimental weapons**: Unusual mechanics
4. **Chemical weapons**: If in game, special handling
5. **Cluster munitions**: Variable damage patterns

---

## 12. Validation Requirements

### Data Completeness

**MUST Have**:
- name (weapon identifier)
- nation (British, German, etc.)
- caliber_mm (gun size)
- AP data OR HE data (at least one combat stat)

**SHOULD Have**:
- ROF (if small arms or AA weapon)
- HE classification (if has HE capability)
- max_range (if specified in source)

**CAN Be Empty**:
- crew_required (not always specified)
- min_range (only mortars/artillery)
- special_rules (many weapons have none)

### Format Validation

**Accept**:
- Fixed numbers: `0-99`
- Dice formulas: `D6`, `D3`, `2D6`
- Dual values: `3(4)`, `7(8)`
- Empty: `-`, blank, `N/A`

**Warn**:
- Unusual formats (log for review)
- Dual values (suggest separate record)
- Variable damage (flag special rule)

**Reject**:
- Invalid characters (unless dice formula)
- Negative numbers
- Non-numeric non-dice values

---

## 13. OCR Implications

### Why Flexible Parser Enables OCR

**OCR Errors Similar to Manual Entry Errors**:
- Character misreads: `O` vs `0`, `l` vs `1`, `I` vs `1`
- Spacing issues: `3 (4)` vs `3(4)`
- Dash confusion: `-` vs `–` vs `—`
- Missing characters: `D6` → `D 6` or `D`

**Flexible Parser Handles Both**:
- Accept multiple formats
- Clean common artifacts
- Validate and warn
- Confidence scoring

### OCR Pre-Processing Layer

Add before existing parser:
```python
def clean_ocr_artifacts(text):
    text = text.replace('O', '0')  # Letter O → digit 0
    text = text.replace('l', '1')  # Lowercase L → digit 1
    text = text.replace('I', '1')  # Uppercase i → digit 1
    text = text.replace('–', '-')  # En-dash → hyphen
    text = text.replace(' ', '')   # Remove spaces
    return text.strip()
```

Then use **same validation logic** as CSV import.

---

## 14. Conclusion

BattleGroup weapon system is complex with:
- 30+ weapon types
- Multiple overlapping classification systems
- Special mechanics (ROF, dual values, variable damage)
- Range-banded effectiveness
- Extensive special rules

**Database must**:
- Handle multiple data formats (numbers, dice, dual values)
- Support flexible categorization
- Validate but accept edge cases
- Enable future OCR scraping

**Next Steps**:
1. Implement flexible parser for CSV import
2. Test on British guns (24 weapons, 8 edge cases)
3. Document lessons learned
4. Extend to OCR scraper (future)
5. Process remaining nations: German, Italian, American, French

---

**Research Complete**: November 5, 2025
**Source Confidence**: High (official BattleGroup rules + reference images)
**Coverage**: Comprehensive for North Africa theater (1940-1943)
