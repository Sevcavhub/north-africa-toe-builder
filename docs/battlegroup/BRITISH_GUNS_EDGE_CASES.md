# British Guns Edge Cases

**Date**: November 5, 2025
**Source**: Manual CSV entry of British DataCards
**Discoveries**: 8 edge cases in 24 weapons

---

## Edge Case Summary

| Case | Count | Impact | Solution |
|------|-------|--------|----------|
| ROF column added | All rows | CSV mapping | Update import script |
| Littlejohn dual values | 1 gun | Data format | Separate gun records |
| Flamethrower D6 | 1 gun | Variable damage | Store TEXT, special rule |
| AA guns (AP only) | 2 guns | No HE data | Validation accepts |
| Bombs/rockets (HE only) | 5 items | No AP data | Validation accepts |
| Special classifications | 7 items | New he_shell values | Accept non-standard |
| Empty ROF values | ~18 guns | Missing data | Accept NULL |
| Partial range bands | Several | Incomplete data | Accept partial |

---

## Case 1: ROF Column Addition

**Discovery**: User added ROF between `caliber_mm` and `he_dice`
**CSV Structure**: Now 20 columns (was 19)

**New Column Order**:
```
name, common_name, nation, caliber_mm, ROF, he_dice, he_target,
he_shell_classification, he_0_10...he_50_70, ap_0_10...ap_50_70
```

**Solution**: Update import script mapping
**Database**: Add `rof INTEGER` column to bg_reference_guns

---

## Case 2: Littlejohn Adaptor Dual Values

**Row 17**: `2 pdr (Littlejohn Adaptor)`
**AP Values**: `3(4), 3(4), 2(3), 1(2), 1(2), -`

**Meaning**: Squeeze-bore adaptor improving penetration
- Base: 3 AP
- Enhanced: 4 AP (with adaptor)

**Solution** (User's Approach):
1. Import with base values only: `3, 3, 2, 1, 1, -`
2. Create two separate guns:
   - `2 pdr` (standard) - AP: 4, 4, 3, 2, 1, -
   - `2 pdr (Littlejohn Adaptor)` - AP: 3, 3, 2, 1, 1, -
3. Create two vehicle records:
   - `Tetrarch` → weapon: "2 pdr"
   - `Tetrarch (Littlejohn Adaptor)` → weapon: "2 pdr (Littlejohn Adaptor)"

**Rationale**: Cleaner than storing dual values, matches game intent (different configurations)

**Parser Handling**:
```python
if '(' in ap_value:
    base = ap_value.split('(')[0]  # "3(4)" → "3"
    warn("WARN_DUAL_VALUE: Consider separate gun record")
    return base
```

---

## Case 3: Flamethrower Variable Damage

**Row 18**: `Flamethrower*`
**he_0_10**: `D6`
**Meaning**: Damage is variable (roll 1D6) instead of fixed number

**Solution**:
- Store `"D6"` as TEXT in he_0_10 field
- Add special_rule: `'variable_damage_D6'`
- Datacard generator recognizes and formats appropriately

**Parser Handling**:
```python
if 'D' in value.upper():
    return value.upper()  # Store "D6" as text
    add_special_rule('variable_damage_D6')
```

---

## Case 4: AA Guns Without HE

**Rows 14-15**: `40mmL60`, `20mm Oerlikon`
**Issue**: Have AP values but NO HE data

**Meaning**: Anti-aircraft autocannons (dedicated AT/AA role)
**Real cards**: Legitimately no HE on official datacards

**Solution**: Validation accepts guns with ONLY AP
```python
if has_ap_data(gun) or has_he_data(gun):  # OR, not AND
    return valid
```

---

## Case 5: Bombs/Rockets Without AP

**Rows 20-24**:
- `Large bomb`, `Medium bomb`, `Small bomb` (3 items)
- `60 lbs Rocket` (1 item)
- `AC 20mm` partially (1 item)

**Issue**: Have HE values but NO AP data

**Meaning**: Aircraft ordnance, area-effect weapons
**Real cards**: No AP penetration on bomb datacards

**Solution**: Validation accepts weapons with ONLY HE
**Classification**: `he_shell_classification = 'bomb'` or `'rocket'`

---

## Case 6: Special Weapon Classifications

**Values Found**:
- Standard: `'v. light'`, `'light'`, `'medium'`, `'heavy'`
- Non-standard: `'bomb'`, `'rocket'`, `'Cannon'`

**Issue**: he_shell_classification not limited to HE size categories

**Solution**: Accept all values, don't enforce enumeration
**Validation**: Warn on typos, but accept legitimate special types

---

## Case 7: Empty ROF Values

**Observation**: Most guns (18 of 24) have empty ROF field

**Meaning**: ROF primarily for small arms/AA guns, not field artillery
**Examples with ROF**:
- Row 14: 40mmL60 = 8 (AA autocannon)
- Row 19: Boyds AT Rifle = 2 (infantry weapon)

**Solution**: ROF is OPTIONAL field (NULL acceptable)
**Database**: `rof INTEGER DEFAULT NULL`

---

## Case 8: Partial Range Bands

**Observation**: Some weapons have data only in close range bands

**Examples**:
- AT rifles: AP at 0-20" only, empty beyond
- Rockets: HE at specific range only (20-30")
- Minimum range weapons: Empty at short range

**Solution**: Accept NULL in individual range band fields
**Validation**: Warn if ALL bands empty, accept if ANY band has data

---

## Additional Findings

### Multiple he_shell_classification Values
Found 7 distinct values:
1. `v. light`
2. `light`
3. `medium`
4. `heavy`
5. `bomb`
6. `rocket`
7. `Cannon`

### Special Weapon Types
- AT Rifle (Boyds): 14mm, ROF 2, low AP
- Aircraft weapons: Different mechanics
- Bombs: Area effect, no AP
- Flamethrower: Variable damage, special rules

### Empty vs Null Semantics
- `-` in CSV → NULL (not applicable)
- Blank → NULL (data not available)
- `0` → Zero (explicitly zero value)

---

## Parser Requirements

### Must Accept
- Fixed numbers: `0-99`
- Dice formulas: `D6`, `D3`, `2D6`
- Dual values: `3(4)` (extract base, warn)
- Empty values: `-`, blank, `N/A`

### Must Warn
- Dual values (suggest separate record)
- Unusual formats (manual review)
- Variable damage (flag special rule)

### Must Not Reject
- Partial data (some fields empty)
- Non-standard classifications
- Special weapon types

---

## Implementation Impact

### Import Script Changes
1. Add ROF field mapping
2. Implement flexible value parser (numbers, dice, dual, empty)
3. Add validation warnings (not errors)
4. Auto-detect weapon categories
5. Auto-flag special rules

### Database Schema Changes
1. Add ROF column
2. Add weapon_category column
3. Add special_rules column
4. Ensure TEXT fields accept dice formulas

### Validation Logic
- Require name, nation, caliber
- Require AP OR HE (not both)
- Accept partial range bands
- Accept empty optional fields

---

## Lessons Learned

**1. Flexible Formats Critical**
- Not all weapons fit standard patterns
- Parser must handle edge cases gracefully
- Warn but don't reject unusual data

**2. Validation Should Guide, Not Block**
- Warnings for review
- Recommendations for best practices
- But accept legitimate special cases

**3. Multiple Classification Systems**
- No single "weapon type" field adequate
- Need: weapon_category, gun_role, he_shell_classification
- Overlapping categories are normal

**4. OCR Preparedness**
- Edge cases from manual entry
- Similar to OCR error patterns
- Flexible parser enables both

---

## Next Session Handoff

**User Actions Needed**:
1. Edit CSV row 17: Remove parentheses `3(4)` → `3`
2. Review other rows for similar dual values
3. Verify ROF values are correct (cross-check with source)
4. Confirm he_shell_classification values

**Import Ready When**:
- Migration 4 complete (ROF + categories added)
- Import script updated (20-column mapping)
- CSV edited (Littlejohn dual values removed)

**Expected Outcome**:
- 24 British guns imported
- ~48+ gun name variants created
- Edge cases handled gracefully
- Validation warnings documented

---

**Documented**: November 5, 2025
**Status**: Ready for implementation
