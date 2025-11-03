# Datacard Generation - Root Cause Analysis

**Date**: November 3, 2025
**Status**: Root cause identified, solution designed

## Problem Summary

Equipment datacards generated but missing critical gameplay data:
1. Tanks show "Weapon: None" 
2. All penetration values null ("-")
3. Ammo loads empty
4. Gun movement speeds incorrect

## Root Cause

**The `equipment_battlegroup.reference_vehicle_id` column is NULL for all 469 items.**

### Database Architecture

**Two separate data sources never linked**:

1. **equipment_battlegroup** (469 items - WITW equipment list)
   - Source: Phase 5 equipment matching work
   - Has: armor values, movement speeds, points, battle rating
   - Missing: weapons, penetration data, ammo loads
   - reference_vehicle_id: **ALL NULL** (0/469 populated)

2. **bg_reference_vehicles** (954 items - BattleGroup reference)
   - Source: Extracted from BattleGroup rulebooks/supplements  
   - Has: weapons (JSON), armor, movement, points, battle rating
   - Format: `weapons: [{"weapon": "50mmL60", "mount": "Turret", "ammo": "9"}, ...]`
   - Issue: NO link to equipment table

3. **bg_reference_guns** (57 guns with penetration data)
   - Has: ap_0_10, ap_10_20, ap_20_30, ap_30_40, ap_40_50, ap_50_70
   - Example: `50mmL60 (PaK38)` → ap values (5, 5, 4, 3, 3, 2)

### Current Datacard Generator Flow (BROKEN)

```
equipment (name, nation, type)
    ↓ JOIN
equipment_battlegroup (armor, movement)
    ↓ reference_vehicle_id = NULL ❌
bg_reference_vehicles (weapons JSON, penetration)
```

**Result**: Datacards get armor/movement but NO weapons/penetration

## Solution Design

### Approach: Name-Based Fuzzy Matching

Since reference_vehicle_id is unpopulated, implement intelligent name matching:

```python
# 1. Normalize names for matching
equipment.name → normalize → "panzer iii ausf f"
bg_reference_vehicles.name → normalize → "panzer iii j"

# 2. Fuzzy match logic
- Exact match (highest priority)
- Variant match (Panzer III Ausf F → Panzer III J/L)
- Fallback to base model (Panzer III → closest variant)

# 3. Extract weapons from JSON
weapons = json.loads(bg_ref.weapons)
main_gun = [w for w in weapons if w['mount'] == 'Turret'][0]

# 4. Look up penetration in bg_reference_guns
gun_name = normalize_gun_name(main_gun['weapon'])  # "50mmL60" → "50mmL60 (PaK38)"
penetration_data = query_bg_reference_guns(gun_name)

# 5. Get ammo from weapons JSON
ammo_load = main_gun['ammo']  # "9" from JSON
```

### Implementation Steps

1. **Update datacard_generator.py**:
   - Add fuzzy name matching function
   - Join to bg_reference_vehicles by name
   - Parse weapons JSON
   - Extract main gun (turret mount)
   - Get ammo from JSON

2. **Update generate_book_datacards.py**:
   - Query bg_reference_vehicles instead of equipment_battlegroup
   - OR add fallback: try equipment_battlegroup first, fallback to bg_reference
   - Extract weapon data from JSON
   - Link weapon to bg_reference_guns for penetration

3. **Gun Movement Fix**:
   - Detect equipment_type = 'gun' or category = 'artillery'
   - Apply manhandled gun rules:
     - Very Light (mortars, <50mm): 3" manhandled
     - Light (37-57mm AT): 2" manhandled  
     - Medium (75-88mm): 1" manhandled
     - Heavy (105mm+): 0" (must be towed)

4. **Infantry Weapons Fix**:
   - Detect equipment_type = 'infantry_weapon'
   - Use different datacard template
   - Show: ROF, Range, Special Rules
   - Omit: Armor, Movement (not applicable)

## Expected Outcomes

After fix:
- ✅ Tanks show main gun (e.g., "50mmL60 KwK")
- ✅ Penetration values populated (5/5/4/3/3/2)
- ✅ Ammo loads from JSON ("9" for Panzer III L)
- ✅ Gun movement realistic (3" for 81mm mortar vs 8"/12")
- ✅ Infantry weapons use correct format

## Testing Plan

1. Test Panzer III Ausf F:
   - Should show "50mmL42" main gun
   - Ammo: "10"
   - Penetration:查询 bg_reference_guns

2. Test Matilda II:
   - Should show "2-pdr" main gun
   - Ammo: from bg_reference JSON
   - Armor: K/K/L

3. Test M1 81mm Mortar:
   - Movement: 3" (not 8"/12")
   - Type: "Very Light Gun"

4. Test Lee Enfield rifle:
   - Use infantry weapon template
   - Show ROF, not armor/movement

## Risks & Mitigations

**Risk**: Name matching fails for variants
- Mitigation: Comprehensive normalization rules + manual review

**Risk**: bg_reference_vehicles weapons JSON incomplete
- Mitigation: Log warnings, use equipment_guns as fallback

**Risk**: Gun name format mismatch (bg_reference_guns uses "50mmL60 (PaK38)")
- Mitigation: Normalize gun names before lookup

## Timeline Estimate

- Database query updates: 1-2 hours
- Name matching logic: 1-2 hours  
- JSON parsing & weapon extraction: 1 hour
- Gun movement rules: 30 min
- Infantry weapon template: 1 hour
- Testing & regeneration: 1-2 hours

**Total**: 5-8 hours (revised from 4-6 hours)

