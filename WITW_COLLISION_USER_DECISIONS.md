# WITW ID Collision User Decision Matrix

**Generated**: 2025-11-02
**Total Escalations**: 23 collisions requiring user decisions
**Database**: `master_database.db`
**Agent**: Specialist Data Cleaning & Normalization Agent v2.0.0

---

## Instructions

For each collision below, review the analysis and select an option (A, B, C, or D). Write your decision in the **User Decision** field.

**Decision Format**: Letter (A/B/C/D) + optional notes

**Example**:
```
User Decision: A - Confirmed in WITW database
User Decision: C - Too ambiguous, NULL all
```

---

## Escalation 1: WITW ID 251 (SdKfz Variants)

**Collision Type**: Multi-category (armored cars + halftrack)
**Collision Count**: 5 items

**Colliding Items**:
1. **GER_SDKFZ_222** - SdKfz 222 (armored_cars)
2. **GER_SDKFZ_231** - SdKfz 231 (armored_cars)
3. **GER_SDKFZ_251_1** - SdKfz 251/1 (halftracks)
4. **GER_SDKFZ_232_FU** - SdKfz 232 (fu) (armored_cars)
5. **GER_SDKFZ_223** - SdKfz 223 (armored_cars)

**Analysis**: WITW ID 251 numerically matches SdKfz 251/1 (halftrack), suggesting ID = model number. However, 4 armored cars (SdKfz 222/223/231/232) also share this ID.

**Options**:
- **A**: Retain SdKfz 251/1 (halftrack) - ID 251 = model 251
- **B**: Retain SdKfz 222 (armored car) - most common variant
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Research WITW database for correct assignment

**Recommendation**: Option D (research WITW database), fallback to Option A if unavailable

**User Decision**: _________________

---

## Escalation 2: WITW ID 626 (FIAT Model vs ID Number)

**Collision Type**: Same nation, different models (support vehicles + trucks)
**Collision Count**: 5 items

**Colliding Items**:
1. **ITA_FIAT_626_RECOVERY** - FIAT 626 Recovery (support_vehicles)
2. **ITA_FIAT_666** - FIAT 666 (trucks)
3. **ITA_FIAT_508C_BALILLA** - FIAT 508c Balilla (support_vehicles)
4. **ITA_FIAT_626_ALL_VARIANTS** - FIAT 626 (all Variants) (trucks)
5. **ITA_FIAT_665NM** - FIAT 665NM (trucks)

**Analysis**: WITW ID 626 likely refers to FIAT model 626, but collides with FIAT 666, 665NM, 508c (different model numbers). Suggests WITW uses model numbers as IDs for Italian vehicles.

**Options**:
- **A**: Retain FIAT 626 (all Variants) - ID matches model, umbrella term
- **B**: Retain FIAT 626 Recovery - ID matches model, specific variant
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Research if WITW Italian vehicles use model numbers as IDs

**Recommendation**: Option A (FIAT 626 all Variants), assuming ID 626 = model 626

**User Decision**: _________________

---

## Escalation 3: WITW ID 100049 (M3 Ambiguity)

**Collision Type**: Multi-category (armored cars + tanks + halftracks)
**Collision Count**: 5 items

**Colliding Items**:
1. **USA_M3_SCOUT_CAR** - M3 Scout Car (armored_cars_reconnaissance)
2. **USA_M3_STUART** - M3 Stuart (tanks)
3. **USA_M3A1_LEE** - M3A1 Lee (tanks)
4. **USA_M3A1_STUART** - M3A1 Stuart (tanks)
5. **USA_M3A1_SCOUT_CAR** - M3A1 Scout Car (halftracks)

**Analysis**: "M3" designates 5 DIFFERENT vehicles:
- M3 Scout Car (halftrack/armored car)
- M3 Stuart (light tank)
- M3 Lee (medium tank)
- M3A1 variants of above

WITW ID 100049 could refer to ANY of these. This is the most ambiguous collision in the database.

**Options**:
- **A**: Retain M3 Stuart (most common M3 tank)
- **B**: Retain M3 Scout Car (primary M3 designation chronologically)
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Research WITW database for category hint (tank vs vehicle)

**Recommendation**: Option C (NULL all), "M3" too ambiguous without WITW reference

**User Decision**: _________________

---

## Escalation 4: WITW ID 49 (Flak Gun Variants)

**Collision Type**: Multi-category (AA + AT, different calibers)
**Collision Count**: 3 items

**Colliding Items**:
1. **GER_FLAK_18** - Flak 18 (anti_aircraft)
2. **GER_FLAK_38** - Flak 38 (anti_aircraft)
3. **GER_FLAK_36_8.8CM** - Flak 36 8.8cm (anti_tank)

**Analysis**: Three different Flak models:
- Flak 18: 88mm AA gun (early model, 1933)
- Flak 36: 88mm AA/AT gun (improved Flak 18, 1936)
- Flak 38: 20mm AA gun (totally different weapon!)

Flak 38 is 20mm, Flak 18/36 are 88mm - clear model AND caliber mismatch.

**Options**:
- **A**: Retain Flak 36 8.8cm (most famous 88mm variant, dual AA/AT role)
- **B**: Retain Flak 18 (original 88mm, earlier service date)
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Research WITW: Does ID 49 refer to caliber (88mm) or model year?

**Recommendation**: Option A (Flak 36), most common 88mm in North Africa (1941-1943)

**User Decision**: _________________

---

## Escalation 5: WITW ID 100032 (Bedford Trucks + Bofors AA)

**Collision Type**: Multi-category (trucks + anti-aircraft)
**Collision Count**: 7 items

**Colliding Items**:
1. **GBR_BEDFORD_MW** - Bedford MW (trucks)
2. **GBR_BEDFORD_OWL** - Bedford OWL (trucks)
3. **GBR_BOFORS_40MM** - Bofors 40mm (anti_aircraft)
4. **GBR_BEDFORD_MW_15CWT** - Bedford MW 15cwt (trucks)
5. **GBR_BEDFORD_OY_3-TON** - Bedford OY 3-ton (trucks)
6. **GBR_BEDFORD_MW_MWD** - Bedford MW/MWD (trucks)
7. **GBR_BEDFORD_OX** - Bedford OX (trucks)

**Analysis**: 6 Bedford truck variants + 1 Bofors AA gun. Clear category mismatch. Bedford variants may be same vehicle family (MW, OWL, OX are all Bedford trucks).

**Options**:
- **A**: Retain Bedford MW (most generic Bedford), NULL Bofors
- **B**: Retain Bedford MW/MWD (covers MW variants), NULL Bofors + others
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Research if Bedford variants are truly different vehicles

**Recommendation**: Option A (Bedford MW), NULL Bofors 40mm (category mismatch)

**User Decision**: _________________

---

## Escalation 6: WITW ID 100043 (Dodge WC Variants)

**Collision Type**: Same family (command vehicles + trucks)
**Collision Count**: 7 items

**Colliding Items**:
1. **USA_DODGE_COMMAND_CAR** - Dodge Command Car (command_vehicles)
2. **USA_DODGE_WC-51** - Dodge WC-51 (trucks)
3. **USA_DODGE_WC-53** - Dodge WC-53 (trucks)
4. **USA_DODGE_WC-54** - Dodge WC-54 (trucks)
5. **USA_DODGE_WC-56** - Dodge WC-56 (trucks)
6. **USA_DODGE_WC54** - Dodge WC54 (trucks) [duplicate of #4]
7. **USA_DODGE_WC_SERIES** - Dodge WC Series (trucks)

**Analysis**: All Dodge WC variants (WC-51, WC-53, WC-54, WC-56 are specific models). "Dodge WC Series" is umbrella term covering all variants.

**Options**:
- **A**: Retain Dodge WC Series (umbrella term for all variants)
- **B**: Retain Dodge Command Car (functionally distinct from trucks)
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Research if WC variants should be separate equipment items

**Recommendation**: Option A (Dodge WC Series), covers all variants generically

**User Decision**: _________________

---

## Escalation 7: WITW ID 504 (M2/M3 Halftrack Variants)

**Collision Type**: Same family (halftracks + command vehicles)
**Collision Count**: 4 items

**Colliding Items**:
1. **USA_M2_HALFTRACK** - M2 Halftrack (halftracks)
2. **USA_M3_COMMAND_HALFTRACK** - M3 Command Halftrack (command_vehicles)
3. **USA_M3_HALFTRACK** - M3 Halftrack (halftracks)
4. **USA_M3A1_HALFTRACK** - M3A1 Halftrack (halftracks)

**Analysis**: M2 and M3 are different halftrack models (M2 = personnel carrier, M3 = armored personnel carrier). M3A1 is improved M3. M3 Command is variant of M3.

**Options**:
- **A**: Retain M3 Halftrack (primary variant, most common)
- **B**: Retain M2 Halftrack (earlier model, different vehicle)
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Research if M2 vs M3 should be separate equipment

**Recommendation**: Option A (M3 Halftrack), primary North Africa variant

**User Decision**: _________________

---

## Escalation 8: WITW ID 100031 (Marmon-Herrington + Wellington Bombers)

**Collision Type**: Multi-category (armored cars + bombers)
**Collision Count**: 5 items

**Colliding Items**:
1. **GBR_MARMON-HERRINGTON** - Marmon-herrington (armored_cars)
2. **GBR_BOSTON_MK_III** - Boston Mk III (bombers)
3. **GBR_WELLINGTON_MK_VIII** - Wellington Mk VIII (bombers)
4. **GBR_WELLINGTON_MK_X** - Wellington Mk X (bombers)
5. **GBR_WELLINGTON_MK3** - Wellington Mk3 (bombers)

**Analysis**: 1 armored car + 3 Wellington bomber variants + 1 Boston bomber. Clear category mismatch.

**Options**:
- **A**: Retain Wellington Mk VIII (primary North Africa variant)
- **B**: Set all to NULL - Phase 5 re-match
- **C**: NULL armored car only, retain one Wellington variant
- **D**: Research WITW to determine ground vs air equipment

**Recommendation**: Option B (NULL all), multi-category collision

**User Decision**: _________________

---

## Escalation 9: WITW ID 2 (Panzer I Variants)

**Collision Type**: Same family (light tanks)
**Collision Count**: 3 items

**Colliding Items**:
1. **GER_PANZER_I_AUSF_A** - Panzer I Ausf A (light_tanks)
2. **GER_PANZER_I_AUSF_B** - Panzer I Ausf B (light_tanks)
3. **GER_PANZER_I** - Panzer I (light_tanks)

**Analysis**: Three Panzer I variants:
- Ausf A (early production)
- Ausf B (improved engine)
- Generic "Panzer I" (umbrella term)

**Options**:
- **A**: Retain generic "Panzer I" (covers all Ausf variants)
- **B**: Retain Panzer I Ausf B (most common in North Africa)
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Keep separate (Ausf A and B are different vehicles)

**Recommendation**: Option A (generic Panzer I), unless Ausf variants need to be distinct

**User Decision**: _________________

---

## Escalation 10: WITW ID 3 (Panzer II Variants)

**Collision Type**: Same family (light tanks)
**Collision Count**: 3 items

**Colliding Items**:
1. **GER_PANZER_II_AUSF_A** - Panzer II Ausf A (light_tanks)
2. **GER_PANZER_II_AUSF_B** - Panzer II Ausf B (light_tanks)
3. **GER_PANZER_II** - Panzer II (light_tanks)

**Analysis**: Same pattern as Panzer I - three variants (Ausf A, Ausf B, generic).

**Options**:
- **A**: Retain generic "Panzer II" (umbrella term)
- **B**: Retain Panzer II Ausf B (most common variant)
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Keep separate (Ausf A and B are different)

**Recommendation**: Option A (generic Panzer II), consistent with Escalation 9 decision

**User Decision**: _________________

---

## Escalation 11: WITW ID 11 (Panzer III Variants)

**Collision Type**: Same family (tanks, different armament)
**Collision Count**: 4 items

**Colliding Items**:
1. **GER_PANZER_III_F** - Panzer III F (tanks)
2. **GER_PANZER_III_G** - Panzer III G (tanks)
3. **GER_PANZER_III_H** - Panzer III H (tanks)
4. **GER_PANZER_III** - Panzer III (tanks)

**Analysis**: Panzer III variants F/G/H have different main guns (37mm → 50mm progression). Generic "Panzer III" umbrella term.

**Options**:
- **A**: Retain generic "Panzer III" (umbrella term)
- **B**: Retain Panzer III G (mid-series variant, 50mm gun)
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Keep separate (F/G/H have different armament)

**Recommendation**: Option D (keep separate), armament differences are significant for wargaming

**User Decision**: _________________

---

## Escalation 12: WITW ID 12 (Panzer IV Variants)

**Collision Type**: Same family (tanks, different armament)
**Collision Count**: 3 items

**Colliding Items**:
1. **GER_PANZER_IV_D** - Panzer IV D (tanks)
2. **GER_PANZER_IV_E** - Panzer IV E (tanks)
3. **GER_PANZER_IV** - Panzer IV (tanks)

**Analysis**: Panzer IV variants D/E (both short 75mm gun). Generic "Panzer IV" umbrella.

**Options**:
- **A**: Retain generic "Panzer IV" (umbrella term)
- **B**: Retain Panzer IV E (later variant)
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Keep separate (D and E have minor differences)

**Recommendation**: Option A (generic Panzer IV), D/E differences minor

**User Decision**: _________________

---

## Escalation 13: WITW ID 17 (StuG III Variants)

**Collision Type**: Same family (self-propelled guns)
**Collision Count**: 3 items

**Colliding Items**:
1. **GER_STUG_III_AUSF_D** - StuG III Ausf D (self_propelled_guns)
2. **GER_STUG_III_AUSF_E** - StuG III Ausf E (self_propelled_guns)
3. **GER_STUG_III** - StuG III (self_propelled_guns)

**Analysis**: StuG III assault gun variants (Ausf D, Ausf E). Generic "StuG III" umbrella.

**Options**:
- **A**: Retain generic "StuG III" (umbrella term)
- **B**: Retain StuG III Ausf E (later variant, better armor)
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Keep separate (Ausf D and E have different armor)

**Recommendation**: Option A (generic StuG III), unless armor differences critical

**User Decision**: _________________

---

## Escalation 14: WITW ID 100001 (British Light Tanks)

**Collision Type**: Same family (light tanks, different marks)
**Collision Count**: 3 items

**Colliding Items**:
1. **GBR_LIGHT_TANK_MK_VI** - Light Tank Mk VI (light_tanks)
2. **GBR_LIGHT_TANK_MK_VIB** - Light Tank Mk VIb (light_tanks)
3. **GBR_LIGHT_TANK_MK_VIC** - Light Tank Mk VIc (light_tanks)

**Analysis**: Light Tank Mk VI variants (a, b, c). Incremental improvements (armor, armament).

**Options**:
- **A**: Retain Light Tank Mk VI (generic, covers all variants)
- **B**: Retain Light Tank Mk VIb (most common variant)
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Keep separate (variants have different armament)

**Recommendation**: Option D (keep separate), armament varies (Vickers .303 vs .50 cal)

**User Decision**: _________________

---

## Escalation 15: WITW ID 100002 (A9 Cruiser Variants)

**Collision Type**: Same family (cruiser tanks)
**Collision Count**: 2 items

**Colliding Items**:
1. **GBR_A9_CRUISER_MK_I** - A9 Cruiser Mk I (tanks)
2. **GBR_A9** - A9 (main_tanks)

**Analysis**: A9 Cruiser Mk I (official designation) vs generic "A9". Same tank.

**Options**:
- **A**: Retain A9 Cruiser Mk I (full official designation)
- **B**: Retain generic "A9" (shorter name)
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Keep both (different name conventions)

**Recommendation**: Option A (A9 Cruiser Mk I), full designation more precise

**User Decision**: _________________

---

## Escalation 16: WITW ID 100003 (A10 Cruiser Variants)

**Collision Type**: Same family (cruiser tanks)
**Collision Count**: 2 items

**Colliding Items**:
1. **GBR_A10_CRUISER_MK_II** - A10 Cruiser Mk II (tanks)
2. **GBR_A10** - A10 (main_tanks)

**Analysis**: A10 Cruiser Mk II (official) vs generic "A10". Same tank.

**Options**:
- **A**: Retain A10 Cruiser Mk II (full designation)
- **B**: Retain generic "A10" (shorter)
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Keep both (different conventions)

**Recommendation**: Option A (A10 Cruiser Mk II), consistent with Escalation 15

**User Decision**: _________________

---

## Escalation 17: WITW ID 100004 (A13 Cruiser Variants)

**Collision Type**: Same family (cruiser tanks, multiple variants)
**Collision Count**: 3 items

**Colliding Items**:
1. **GBR_A13_CRUISER** - A13 Cruiser (tanks)
2. **GBR_A13_MK_II_CRUISER** - A13 Mk II Cruiser (main_tanks)
3. **GBR_A13_MK_II_CRUISER_MK_IV** - A13 Mk II (cruiser Mk IV) (tanks)

**Analysis**: A13 Cruiser variants:
- A13 Cruiser (generic)
- A13 Mk II (improved armor)
- A13 Mk II Cruiser Mk IV (official designation)

A13 Mk II and Cruiser Mk IV are the SAME tank (official name: Cruiser Tank Mk IV A13 Mk II).

**Options**:
- **A**: Retain A13 Mk II Cruiser Mk IV (full official designation)
- **B**: Retain A13 Cruiser (generic, covers all)
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Keep Mk I and Mk II separate (different armor)

**Recommendation**: Option A (A13 Mk II Cruiser Mk IV), most precise designation

**User Decision**: _________________

---

## Escalation 18: WITW ID 100005 (Matilda II Variants)

**Collision Type**: Same family (infantry tanks)
**Collision Count**: 2 items

**Colliding Items**:
1. **GBR_MATILDA_MK_II** - Matilda Mk II (tanks)
2. **GBR_A12_MATILDA_II** - A12 Matilda II (tanks)

**Analysis**: Same tank, two naming conventions:
- Matilda Mk II (common name)
- A12 Matilda II (official A-number designation)

**Options**:
- **A**: Retain Matilda Mk II (common name)
- **B**: Retain A12 Matilda II (official designation with A-number)
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Keep both (different conventions)

**Recommendation**: Option B (A12 Matilda II), consistent with A9/A10/A13 pattern

**User Decision**: _________________

---

## Escalation 19: WITW ID 100006 (Valentine Variants)

**Collision Type**: Same family (infantry tanks, multiple marks)
**Collision Count**: 4 items

**Colliding Items**:
1. **GBR_VALENTINE_I** - Valentine I (main_tanks)
2. **GBR_VALENTINE_MK_II** - Valentine Mk II (main_tanks)
3. **GBR_VALENTINE_MK_IX** - Valentine Mk IX (main_tanks)
4. **GBR_VALENTINE** - Valentine (tanks)

**Analysis**: Valentine tank marks I, II, IX, and generic "Valentine". Marks have different armament:
- Mk I: 2pdr gun
- Mk II: 2pdr gun, diesel engine
- Mk IX: 6pdr gun

**Options**:
- **A**: Retain generic "Valentine" (umbrella term)
- **B**: Retain Valentine Mk II (most common North Africa variant)
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Keep separate (different armament, especially Mk IX)

**Recommendation**: Option D (keep separate), Mk IX has different gun (6pdr vs 2pdr)

**User Decision**: _________________

---

## Escalation 20: WITW ID 100007 (Crusader Variants)

**Collision Type**: Same family (cruiser tanks, multiple marks)
**Collision Count**: 3 items

**Colliding Items**:
1. **GBR_CRUSADER_MK_I** - Crusader Mk I (main_tanks)
2. **GBR_CRUSADER_MK_II** - Crusader Mk II (main_tanks)
3. **GBR_CRUSADER_MK_III** - Crusader Mk III (main_tanks)

**Analysis**: Crusader marks I, II, III. Significant armament differences:
- Mk I: 2pdr gun
- Mk II: 2pdr gun, improved armor
- Mk III: 6pdr gun (major upgrade)

**Options**:
- **A**: Retain Crusader Mk II (most common variant)
- **B**: Keep all separate (different armament)
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Retain generic "Crusader" (create umbrella entry)

**Recommendation**: Option B (keep separate), Mk III has different gun (6pdr)

**User Decision**: _________________

---

## Escalation 21: WITW ID 100008 (Stuart Variants)

**Collision Type**: Same family (light tanks, M3/M5 variants)
**Collision Count**: 3 items

**Colliding Items**:
1. **GBR_M3_STUART_I** - M3 Stuart I (main_tanks)
2. **GBR_M3A1_STUART_III** - M3A1 Stuart III (main_tanks)
3. **GBR_M5_STUART** - M5 Stuart (tanks)

**Analysis**: British designations for American Stuart light tanks:
- Stuart I = M3
- Stuart III = M3A1
- Stuart (generic) = M5

M3 and M5 are different tank models (M5 has improved armor, different hull).

**Options**:
- **A**: Retain M3 Stuart I (earliest North Africa variant)
- **B**: Keep all separate (M3 vs M5 are different tanks)
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Retain generic "Stuart" (umbrella term)

**Recommendation**: Option B (keep separate), M3 and M5 are different vehicles

**User Decision**: _________________

---

## Escalation 22: WITW ID 100009 (Sherman Variants)

**Collision Type**: Same family (medium tanks, multiple marks)
**Collision Count**: 3 items

**Colliding Items**:
1. **GBR_SHERMAN_I_M4** - Sherman I (M4) (tanks)
2. **GBR_SHERMAN_II_M4A1** - Sherman II (M4A1) (tanks)
3. **GBR_SHERMAN_III_M4A4** - Sherman III (M4A4) (tanks)

**Analysis**: British designations for American Sherman tanks:
- Sherman I = M4 (welded hull, Continental engine)
- Sherman II = M4A1 (cast hull, Continental engine)
- Sherman III = M4A4 (welded hull, Chrysler Multibank engine)

Different hull types and engines, but same 75mm gun.

**Options**:
- **A**: Retain Sherman I (M4) (most common variant)
- **B**: Keep all separate (different hull/engine variants)
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Retain generic "Sherman" (umbrella term)

**Recommendation**: Option B (keep separate), hull and engine differences matter for maintenance/reliability

**User Decision**: _________________

---

## Escalation 23: WITW ID 100010 (Churchill Variants)

**Collision Type**: Same family (infantry tanks)
**Collision Count**: 2 items

**Colliding Items**:
1. **GBR_CHURCHILL_MK_IV** - Churchill Mk IV (main_tanks)
2. **GBR_CHURCHILL_IV** - Churchill IV (main_tanks)

**Analysis**: Same tank, two naming conventions:
- "Churchill Mk IV" (with "Mk")
- "Churchill IV" (without "Mk")

**Options**:
- **A**: Retain Churchill Mk IV (with "Mk", consistent with other British tanks)
- **B**: Retain Churchill IV (without "Mk", shorter)
- **C**: Set all to NULL - Phase 5 re-match
- **D**: Keep both (different conventions)

**Recommendation**: Option A (Churchill Mk IV), consistent with Valentine Mk X, Crusader Mk III, etc.

**User Decision**: _________________

---

## Summary Table

| Escalation | WITW ID | Collision Type | Items | Recommendation |
|------------|---------|----------------|-------|----------------|
| 1 | 251 | SdKfz variants | 5 | Option D (research) → A (251/1) |
| 2 | 626 | FIAT models | 5 | Option A (FIAT 626) |
| 3 | 100049 | M3 ambiguity | 5 | Option C (NULL all) |
| 4 | 49 | Flak variants | 3 | Option A (Flak 36) |
| 5 | 100032 | Bedford + Bofors | 7 | Option A (Bedford MW) |
| 6 | 100043 | Dodge WC | 7 | Option A (WC Series) |
| 7 | 504 | M2/M3 halftracks | 4 | Option A (M3) |
| 8 | 100031 | Marmon + Wellington | 5 | Option B (NULL all) |
| 9 | 2 | Panzer I | 3 | Option A (generic) |
| 10 | 3 | Panzer II | 3 | Option A (generic) |
| 11 | 11 | Panzer III F/G/H | 4 | Option D (keep separate) |
| 12 | 12 | Panzer IV D/E | 3 | Option A (generic) |
| 13 | 17 | StuG III | 3 | Option A (generic) |
| 14 | 100001 | Light Tank Mk VI | 3 | Option D (keep separate) |
| 15 | 100002 | A9 Cruiser | 2 | Option A (A9 Cruiser Mk I) |
| 16 | 100003 | A10 Cruiser | 2 | Option A (A10 Cruiser Mk II) |
| 17 | 100004 | A13 Cruiser | 3 | Option A (A13 Mk II Cruiser Mk IV) |
| 18 | 100005 | Matilda II | 2 | Option B (A12 Matilda II) |
| 19 | 100006 | Valentine | 4 | Option D (keep separate) |
| 20 | 100007 | Crusader | 3 | Option B (keep separate) |
| 21 | 100008 | Stuart | 3 | Option B (keep separate) |
| 22 | 100009 | Sherman | 3 | Option B (keep separate) |
| 23 | 100010 | Churchill | 2 | Option A (Churchill Mk IV) |

**Quick Decision Guide**:
- **Keep Separate**: When armament/armor differs (Panzer III F/G/H, Valentine I/II/IX, Crusader I/II/III, Stuart M3/M5, Sherman I/II/III)
- **Use Generic**: When variants are minor (Panzer I, Panzer II, Panzer IV D/E, StuG III)
- **Use Full Designation**: When official name is clearer (A9 Cruiser Mk I, A10 Cruiser Mk II, A13 Mk II Cruiser Mk IV, A12 Matilda II)
- **NULL All**: When too ambiguous (M3 Scout/Stuart/Lee collision)

---

## Decision Deadline

**Recommended**: Complete decisions within 1 business day
**Reason**: Phase 3 execution blocked until decisions made

---

## Sign-Off

**Status**: ⏳ **AWAITING USER DECISIONS**
**Total Escalations**: 23
**Estimated Decision Time**: 30-60 minutes

**Prepared by**: Specialist Data Cleaning & Normalization Agent v2.0.0
**Date**: 2025-11-02

---

**END OF USER DECISION MATRIX**
