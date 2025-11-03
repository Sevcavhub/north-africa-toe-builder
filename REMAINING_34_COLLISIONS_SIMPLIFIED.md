# Remaining 34 Collisions - Simplified Decision List

**Generated**: 2025-11-02
**Total**: 34 collisions

---

## Quick Instructions

For each collision, either:
- **Accept recommendation** (most are high confidence)
- **Change decision** (write A/B/C/D in User Decision field)
- **Skip for now** (leave blank, we'll handle later)

**Decision Key**:
- **A**: Retain one item (specified)
- **B**: Keep all separate (NULL all witw_ids)
- **C**: NULL all (too ambiguous)
- **D**: Research needed

---

## High Confidence Recommendations (9 collisions)

These have clear recommendations you can approve quickly.

### 1. WITW ID 73

- GER_8.8CM_FLAK_36: 8.8cm Flak 36 (anti_aircraft)
- GER_8.8CM_FLAK_18_36: 8.8cm Flak 18/36 (anti_aircraft)
- ITA_M13_40_SERIE_III: M13/40 Serie III (tanks)

**Type**: Cross Nation
**Recommendation**: C - Cross-nation collision: GER, ITA
**Action**: NULL all (Phase 5 re-match)
**Note**: Likely incorrect ID assignment

**User Decision**: C (accept recommendation)

---

### 2. WITW ID 91

- GER_PANZER_IV_AUSF_H: Panzer IV Ausf H (tanks)
- ITA_M13_40_SERIE_I: M13/40 Serie I (tanks)

**Type**: Cross Nation
**Recommendation**: C - Cross-nation collision: GER, ITA
**Action**: NULL all (Phase 5 re-match)
**Note**: Likely incorrect ID assignment

**User Decision**: C (accept recommendation)

---

### 3. WITW ID 92

- GER_PANZER_VI_TIGER_I: Panzer VI Tiger I (tanks)
- ITA_M13_40_SERIE_II: M13/40 Serie II (tanks)

**Type**: Cross Nation
**Recommendation**: C - Cross-nation collision: GER, ITA
**Action**: NULL all (Phase 5 re-match)
**Note**: Likely incorrect ID assignment

**User Decision**: C (accept recommendation)

---

### 4. WITW ID 180

- GER_PANZER_II_AUSF_F: Panzer II Ausf F (light_tanks)
- ITA_47MM_L_40: 47mm L/40 (anti_tank)

**Type**: Cross Nation
**Recommendation**: C - Cross-nation collision: GER, ITA
**Action**: NULL all (Phase 5 re-match)
**Note**: Likely incorrect ID assignment

**User Decision**: C (accept recommendation)

---

### 5. WITW ID 187

- GER_PANZER_III_AUSF_H: Panzer III Ausf H (tanks)
- ITA_AB41: AB41 (armored_cars)
- ITA_TOTAL_ARMORED_CARS: Total Armored Cars (armored_cars)

**Type**: Cross Nation
**Recommendation**: C - Cross-nation collision: GER, ITA
**Action**: NULL all (Phase 5 re-match)
**Note**: Likely incorrect ID assignment

**User Decision**: C (accept recommendation)

---

### 6. WITW ID 761

- GBR_VALENTINE_III: Valentine III (main_tanks)
- GBR_VALENTINE_MK_III: Valentine Mk III (tanks)

**Type**: Naming Convention
**Recommendation**: A - British naming convention prefers "Mk"
**Action**: Retain `GBR_VALENTINE_MK_III`, NULL others

**User Decision**: A (accept recommendation)

---

### 7. WITW ID 828

- GBR_VALENTINE_MK_IX: Valentine Mk IX (main_tanks)
- GBR_VALENTINE_IX: Valentine IX (main_tanks)

**Type**: Naming Convention
**Recommendation**: A - British naming convention prefers "Mk"
**Action**: Retain `GBR_VALENTINE_MK_IX`, NULL others

**User Decision**: A (accept recommendation)

---

### 8. WITW ID 2014

- GBR_CRUSADER_MK_II: Crusader Mk II (main_tanks)
- GBR_CRUSADER_II: Crusader II (main_tanks)

**Type**: Naming Convention
**Recommendation**: A - British naming convention prefers "Mk"
**Action**: Retain `GBR_CRUSADER_MK_II`, NULL others

**User Decision**: A (accept recommendation)

---

### 9. WITW ID 2044

- GBR_CHURCHILL_MK_IV: Churchill Mk IV (main_tanks)
- GBR_CHURCHILL_IV: Churchill IV (main_tanks)

**Type**: Naming Convention
**Recommendation**: A - British naming convention prefers "Mk"
**Action**: Retain `GBR_CHURCHILL_MK_IV`, NULL others

**User Decision**: A (accept recommendation)

---

## Medium Confidence (3 collisions)

These need your judgment on whether variants should be separate.

### 1. WITW ID 100034

- GBR_MORRIS_C8: Morris C8 (trucks)
- GBR_MORRIS_QUAD: Morris Quad (support_vehicles)
- GBR_MORRIS_C8_QUAD: Morris C8 Quad (trucks)

**Type**: Variant Series
**Recommendation**: A - Retain most specific Morris variant

**User Decision**: _________

---

### 2. WITW ID 100041

- USA_GMC_CCKW-352: GMC CCKW-352 (trucks)
- USA_GMC_CCKW-354: GMC CCKW-354 (trucks)
- USA_GMC_CCKW_66: GMC CCKW 6×6 (trucks)

**Type**: Variant Series
**Recommendation**: B - GMC CCKW variants (different cargo capacities)
**Note**: Keep separate if cargo capacity matters for logistics modeling

**User Decision**: _________

---

### 3. WITW ID 100044

- USA_DODGE_WC-52: Dodge WC-52 (trucks)
- USA_DODGE_WC-62: Dodge WC-62 (trucks)
- USA_DODGE_WC62: Dodge WC62 (trucks)

**Type**: Variant Series
**Recommendation**: B - Dodge WC variants (different models)

**User Decision**: _________

---

## Low Confidence / Needs Research (22 collisions)

These need investigation or can be deferred.

### 1. WITW ID 68

- GER_50MM_PAK_38: 50mm Pak 38 (anti_tank)
- GER_5.0CM_PAK_38: 5.0cm Pak 38 (anti_tank)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 2. WITW ID 84

- GER_PANZER_III_AUSF_G: Panzer III Ausf G (tanks)
- GER_PANZER_III_COMMAND: Panzer III Command (tanks)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 3. WITW ID 89

- GER_PANZER_IV_AUSF_E: Panzer IV Ausf E (tanks)
- GER_PANZER_IV_AUSF_F2: Panzer IV Ausf F2 (tanks)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 4. WITW ID 113

- GBR_GLADIATOR: Gladiator (fighters)
- GBR_GLOSTER_GLADIATOR: Gloster Gladiator (fighters)
- GBR_LIBERATOR_MK_III: Liberator Mk III (bombers)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 5. WITW ID 131

- GBR_MATILDA_MK_II: Matilda Mk II (tanks)
- GBR_GRANT_MK_II: Grant Mk II (tanks)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 6. WITW ID 159

- GBR_4_5_INCH_HOWITZER: 4 5 Inch Howitzer (field_artillery)
- GBR_4.5-INCH_HOWITZER: 4.5-inch Howitzer (field_artillery)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 7. WITW ID 177

- ITA_L3_33: L3/33 (light_tanks)
- ITA_L3_35: L3/35 (light_tanks)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 8. WITW ID 179

- ITA_M11_39_RECOVERY: M11/39 Recovery (support_vehicles)
- ITA_47MM_L_32: 47mm L/32 (anti_tank)
- ITA_90MM_MOD_939: 90mm Mod 939 (anti_aircraft)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 9. WITW ID 192

- ITA_47MM_MOD_37: 47mm Mod 37 (anti_tank)
- ITA_47MM_AT: 47mm AT (anti_tank)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 10. WITW ID 205

- ITA_100MM_MOD_14: 100mm Mod 14 (field_artillery)
- ITA_100MM_HOWITZER: 100mm Howitzer (field_artillery)
- ITA_SEMOVENTE_75_18: Semovente 75/18 (tanks)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 11. WITW ID 231

- USA_P-38G: P-38G (Lockheed P-38 Lightning)
- USA_P-38H: P-38H (Lockheed P-38 Lightning)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 12. WITW ID 258

- USA_37MM_M3: 37mm M3 (anti_tank)
- USA_57MM_M1: 57mm M1 (anti_tank)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 13. WITW ID 268

- USA_M1_155MM_HOWITZER: M1 155mm Howitzer (artillery)
- USA_M2A1_105MM_HOWITZER: M2A1 105mm Howitzer (artillery)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 14. WITW ID 271

- USA_M1_57MM_AT_GUN: M1 57mm AT Gun (anti_tank)
- USA_M3_37MM_AT_GUN: M3 37mm AT Gun (anti_tank)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 15. WITW ID 2003

- GBR_STUART_I_M3_LIGHT: Stuart I (M3 Light) (tanks)
- GBR_M3_STUART_I: M3 Stuart I (main_tanks)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 16. WITW ID 2011

- GBR_A13_MK_II_CRUISER_MK_IV: A13 Mk II (cruiser Mk IV) (tanks)
- GBR_A13_MK_II: A13 Mk II (tanks)
- GBR_A13_MK_II_CRUISER: A13 Mk II Cruiser (main_tanks)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 17. WITW ID 2024

- GBR_GRANT_M3: Grant M3 (tanks)
- GBR_M3_GRANT: M3 Grant (main_tanks)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 18. WITW ID 2059

- GBR_DAIMLER_ARMORED_CAR: Daimler Armored Car (armored_cars)
- GBR_DAIMLER_MK_I: Daimler Mk I (armored_cars)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 19. WITW ID 3098

- GBR_LIGHT_TANK_MK_VI: Light Tank Mk VI (tanks)
- GBR_LIGHT_MK_VI: Light Mk VI (main_tanks)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 20. WITW ID 100021

- GBR_FORD_F15_15CWT: Ford F15 15cwt (trucks)
- GBR_FORD_F15A_CMP: Ford F15A CMP (trucks)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 21. WITW ID 100024

- GBR_CMP_CHEVROLET: CMP Chevrolet (trucks)
- GBR_CHEVROLET_C30_CMP: Chevrolet C30 CMP (trucks)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

### 22. WITW ID 100050

- USA_DIAMOND_T_980: Diamond T 980 (recovery_vehicles)
- USA_DIAMOND_T_WORKSHOP: Diamond T Workshop (workshop_vehicles)

**Recommendation**: NULL all or defer to Phase 5

**User Decision**: C (NULL all)

---

## Summary

- **High Confidence**: 9 (can auto-apply)
- **Medium Confidence**: 3 (need quick review)
- **Low Confidence**: 22 (recommend NULL all)

**Estimated review time**: 15-25 minutes
