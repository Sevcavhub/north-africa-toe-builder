# Research Brief: 31st Fighter Group (1942-Q4)

**Status**: EXTRACTION REFUSED - Insufficient Tier 1/2 Corroboration  
**Date**: 2025-10-27  
**Agent**: Claude (Air Unit Extraction Protocol)

---

## Extraction Requirements NOT Met

### Hybrid Source Validation Protocol Status

**Required**: 3+ key facts from Tier 1/2 sources  
**Achieved**: 2 of 3 facts confirmed

| Requirement | Status | Source |
|-------------|--------|--------|
| Unit designation | ✅ CONFIRMED | WITW _airgroup.csv (Tier 1) |
| Specific aircraft variant | ❌ CONFLICTING | WITW shows Spitfire IX, Wikipedia shows Spitfire Vb |
| Operational dates | ✅ CONFIRMED | Multiple sources confirm Nov 1942 Operation Torch |

---

## Data Found (Tier 3 - Wikipedia)

### Unit Information
- **Designation**: 31st Fighter Group
- **Nation**: American (USAAF)
- **Quarter**: 1942-Q4 (November-December 1942)
- **Parent Formation**: 12th Air Force

### Squadron Composition
- **307th Fighter Squadron** (Squadron code: MX)
- **308th Fighter Squadron** (Squadron code: HL)  
- **309th Fighter Squadron** (Squadron code: WZ)

### Aircraft (UNCONFIRMED VARIANT)
- **Type**: Supermarine Spitfire (British)
- **Variant**: **Vb** (per Wikipedia) vs **IX** (per WITW data - incorrect for timeframe)
- **Note**: WITW aircraft type 733 is listed as "Spitfire IX (US)" but Spitfire IX did not enter service until 1943

### Operations (November-December 1942)
- **8 November 1942**: Participated in Operation Torch landings
  - Pilots flew Spitfires from Gibraltar to Tafaraoui, Algeria
  - Ground echelon landed at Arzeu beach
  - 308th FS CO Major Harrison Thyng shot down 2 Vichy D.520s (opening kills)
  - 309th FS engaged 3 Vichy D.520s strafing Tafaraoui during landing

- **8-11 November 1942**: Algeria/Morocco campaign
  - Attacked motor transports, gun positions, troop concentrations
  
- **12 November 1942**: Relocated from Tafaraoui to La Senia, Algeria

### Commander
- **308th FS CO**: Major Harrison Thyng (confirmed combat on 8 Nov 1942)

---

## Critical Data Gaps

### TIER 1/2 SOURCES NEEDED FOR:

1. **Aircraft Variant Confirmation**
   - WITW data shows "Spitfire IX" (type 733) but this is anachronistic for 1942-Q4
   - Wikipedia sources say "Spitfire Vb" but this is Tier 3
   - **NEED**: USAAF unit history, 12th Air Force records, or AFHRA documentation

2. **Aircraft Strength Numbers**
   - WITW shows: 60 total aircraft, 37 operational, 10 damaged (generic fighter group)
   - **NEED**: Official USAAF strength reports for November 1942

3. **Personnel Counts**
   - No pilot numbers found
   - No ground crew numbers found
   - **NEED**: Unit morning reports or personnel rosters

4. **Base Locations & Movements**
   - Tafaraoui (8-12 Nov) - confirmed
   - La Senia (12 Nov onward) - confirmed  
   - **NEED**: Detailed airfield assignments for rest of Q4 1942

5. **Combat Operations Detail**
   - Only Operation Torch opening (8-11 Nov) documented
   - **NEED**: Mission logs, sortie records for November-December 1942

6. **Squadron-Level Aircraft Distribution**
   - No per-squadron aircraft counts found
   - **NEED**: Squadron status reports

---

## Tier 1/2 Sources to Consult

### USAAF Official Sources (Tier 1)
- [ ] **AFHRA (Air Force Historical Research Agency)**
  - Unit history files for 31st Fighter Group
  - Squadron histories (307th, 308th, 309th FS)
  - Monthly strength reports November-December 1942

- [ ] **12th Air Force Historical Records**
  - Group status reports
  - Aircraft inventory reports
  - Combat mission summaries

### WITW Game Data (Tier 1 - with corrections)
- [x] **_airgroup.csv**: Confirms unit exists (ID 793)
- [x] **_aircraft.csv**: Type 733 linked but shows wrong variant (IX vs Vb)
- [ ] **Scenario files**: Check "Torch to Tunisia" scenario for accurate aircraft assignments

### Asisbiz.com (Tier 2)
- [ ] **31st Fighter Group page**
- [ ] **Squadron-specific pages** (307th/308th/309th FS)
- [ ] **Spitfire Vb USAAF operations**

### Books/Published Sources (Tier 2)
- [ ] "The 31st Fighter Group in World War II" by Ron Mackay
- [ ] Official USAAF squadron histories
- [ ] 12th Air Force operational histories

---

## Aircraft Variant Resolution Required

### The Spitfire IX Problem
**WITW Data Issue**: Aircraft type 733 is labeled "Spitfire IX (US)" but:
- Spitfire IX entered RAF service in **July 1942**
- USAAF did not receive Spitfire IXs until **1943**
- All sources confirm 31st FG flew **Spitfire Vb** during Operation Torch

**Conclusion**: WITW aircraft type 733 mislabeled OR wrong aircraft type assigned to group for Nov 1942 scenario

**Action Needed**: 
1. Verify WITW Spitfire Vb aircraft ID (likely different from 733)
2. Confirm which WITW aircraft ID maps to "Spitfire Vb" for USAAF units

---

## Recommended Next Steps

### Phase 1: Tier 1 Source Acquisition
1. **AFHRA Access**: Request 31st Fighter Group unit history microfilm/digital files
2. **USAAF Historical Office**: 12th Air Force operational reports November-December 1942

### Phase 2: Tier 2 Source Review  
1. **Asisbiz.com**: Extract squadron-level detail and aircraft serial numbers
2. **Published Histories**: Acquire Ron Mackay's "31st Fighter Group in WWII"

### Phase 3: WITW Data Correction
1. Identify correct Spitfire Vb aircraft ID in WITW database
2. Cross-reference with other USAAF Spitfire units (52nd FG, 14th FG)

### Phase 4: Re-attempt Extraction
- Once 3+ Tier 1/2 facts confirmed with specific aircraft variant
- Minimum 60% schema completion achievable
- Target Tier 2 (review_recommended) or higher

---

## Sources Consulted

### Tier 1 (Authoritative)
- ✅ WITW _airgroup.csv (Group designation confirmed, aircraft type problematic)

### Tier 2 (Reliable)
- ⏸️ Asisbiz.com (not yet accessed)
- ⏸️ AFHRA (not yet accessed)

### Tier 3 (Identification Only)
- ✅ Wikipedia (31st Operations Group article)
- ✅ wwiiaircraftperformance.org
- ✅ americanairmuseum.com
- ✅ Aviano AFB heritage pamphlet

---

## Extraction Decision

**REFUSED**: Cannot proceed with extraction using primarily Wikipedia (Tier 3) sources when specific aircraft variant cannot be confirmed from Tier 1/2 sources. The discrepancy between WITW data (Spitfire IX) and historical sources (Spitfire Vb) must be resolved with authoritative documentation before extraction can proceed.

**Estimated Research Time**: 2-4 hours to acquire and review Tier 1/2 sources

**Re-evaluation Trigger**: Acquisition of AFHRA unit history OR Asisbiz.com detailed squadron data with aircraft serials/variants confirmed

---

**End of Research Brief**
