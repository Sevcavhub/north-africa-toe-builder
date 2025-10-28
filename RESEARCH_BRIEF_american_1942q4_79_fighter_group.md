# Research Brief: 79th Fighter Group (1942-Q4)

**Status**: EXTRACTION REFUSED - Insufficient operational data for Q4 1942

**Date**: 2025-10-27  
**Unit**: 79th Fighter Group (USAAF)  
**Quarter**: 1942-Q4 (October-December 1942)  
**Theater**: North Africa (Egypt)

---

## Extraction Refusal Rationale

The 79th Fighter Group does **NOT meet the minimum requirements** for air unit extraction in 1942-Q4 because:

1. **Not operationally active** - Unit was in training/transit phase only
2. **No combat operations** - First combat missions not until March 1943
3. **No specific aircraft variants documented** - Only generic "P-40" references for Q4 1942
4. **Fails Hybrid Source Validation Protocol** - Cannot provide specific aircraft variant (e.g., P-40F-5)

---

## What Was Found (Tier 1/2 Sources)

### Tier 1 Sources

**Source**: "The Falcon: Combat History Of The 79th Fighter Group, United States Army Air Forces, 1942-1945" (Official Unit History, Archive.org)

**Key Facts**:
- Ground echelon departed Hampton Roads, VA: October 7, 1942
- Ground personnel arrived Port Tewfik, Egypt: November 12, 1942
- Unit established at Landing Ground 174 (Amirya, Egypt): November 16, 1942
- Aircraft: Trained with "P-40's" (no specific variant given)
- Operational Status: Training phase, "did not begin operations until March 1943"
- Duration at LG 174: "two-and-a-half months" (Nov 1942 - late Jan 1943)

**Source**: WITW _airgroup.csv (Gary Grigsby's War in the West game data)

**Key Facts**:
- Unit ID: 803
- Name: "79th USAAF FB Grp" (Fighter-Bomber Group)
- Type: Fighter Group (type=1)
- Nation: American (nat=13)
- Three squadrons: 85th, 86th, 87th Fighter Squadrons

### Tier 2 Sources

**Source**: Asisbiz.com (Aviation history database)

**Key Facts**:
- Aircraft: P-40F Warhawk confirmed
- Serial numbers documented: 41-14100, 41-14295, 41-14513, 41-19735, 41-19746, 41-19936
- Squadron assignments: 85th FS, 86th FS, 87th FS
- **Critical Issue**: All dated serial numbers are from 1943 operations, NOT 1942

**Source**: Multiple historical websites (historyofwar.org, 9af.org, 79thfightergroup.com)

**Key Facts**:
- Confirmed activation: February 9, 1942
- Confirmed redesignation from "Pursuit Group" to "Fighter Group": May 1942
- Confirmed assignment to Ninth Air Force: November 1942
- Confirmed aircraft type: P-40 Warhawk
- Confirmed first combat: March 1943

---

## What Was NOT Found

### Missing Required Data (60% Tier 1/2 minimum)

1. **Specific P-40 variant for Q4 1942**
   - Required: "P-40F-5" or "P-40F-1" or similar sub-variant
   - Found: Only "P-40" or "P-40F" (generic references)
   - Problem: Cannot determine which P-40F block/variant in Q4 1942

2. **Combat operations in Q4 1942**
   - Required: Battle names, dates, operational roles
   - Found: NONE - unit was in training phase
   - Official history explicitly states: "did not begin operations until March 1943"

3. **Aircraft assignments by squadron for Q4 1942**
   - Required: Which squadrons had which aircraft in Oct-Dec 1942
   - Found: Squadron names confirmed, but no aircraft allocations for Q4 1942
   - Problem: Asisbiz data is all from 1943 operations

4. **Unit strength for Q4 1942**
   - Required: Number of aircraft per squadron
   - Found: NONE - no strength returns for Q4 1942 training period

5. **Operational bases with dates**
   - Partial: Landing Ground 174 from November 16, 1942
   - Missing: Specific dates for aircraft receipt, training milestones

---

## Research Recommendations

To enable extraction of 79th Fighter Group, researchers need:

### Primary Sources Needed

1. **USAAF Unit History Files (AFHRA)**
   - Request: GP-79-HI (79th Fighter Group unit history)
   - Dates needed: October-December 1942
   - Information needed: Aircraft receipt dates, P-40 variant specifications, training activities

2. **Ninth Air Force Operations Orders**
   - Source: Air Force Historical Research Agency
   - Dates: November-December 1942
   - Information needed: Aircraft allocations to 79th FG

3. **Individual Aircraft Records (MACR/AAF)**
   - Source: National Archives
   - Serial numbers: P-40F aircraft assigned to 79th FG in Q4 1942
   - Information needed: Delivery dates, specific variant blocks

### Alternative Approach

**Consider extracting 1943-Q1 instead**:
- Unit became operational March 1943
- Combat operations documented
- Aircraft variants better documented (Asisbiz has multiple 1943 records)
- Meets all extraction requirements

---

## Source Quality Assessment

| Source | Type | Tier | Confidence | Coverage |
|--------|------|------|------------|----------|
| "The Falcon" unit history | Official USAAF | Tier 1 | 95% | Deployment timeline, but lacks aircraft variants |
| WITW _airgroup.csv | Game database | Tier 1 | 90% | Unit structure, but lacks Q4 1942 specifics |
| Asisbiz.com | Aviation database | Tier 2 | 85% | Excellent for 1943 operations, minimal for Q4 1942 |
| Various historical sites | Secondary | Tier 2 | 80% | Good for timeline, weak on technical details |

**Overall Tier 1/2 Coverage**: ~35% of required fields
- **Minimum required**: 60%
- **Verdict**: INSUFFICIENT for extraction

---

## Extraction Feasibility

| Requirement | Status | Notes |
|-------------|--------|-------|
| Unit designation | ✅ PASS | 79th Fighter Group confirmed |
| Specific aircraft variant | ❌ FAIL | Only "P-40" or "P-40F", no sub-variant |
| Operational dates OR battles | ❌ FAIL | No combat ops in Q4 1942, training only |
| 3+ key facts from Tier 1/2 | ⚠️ PARTIAL | Have timeline facts, lack technical facts |
| 60% minimum Tier 1/2 data | ❌ FAIL | Only ~35% coverage |

**Overall Verdict**: **EXTRACTION REFUSED**

---

## Recommendation

**Do NOT extract 79th Fighter Group for 1942-Q4.**

**Alternative actions**:
1. Extract 79th Fighter Group for **1943-Q1** instead (operational data available)
2. Extract 79th Fighter Group for **1943-Q2** (peak combat operations, excellent documentation)
3. Focus on other American fighter groups operational in Q4 1942:
   - 33rd Fighter Group (Operation Torch, Morocco)
   - 1st Fighter Group (Operation Torch, Algeria)
   - 14th Fighter Group (Operation Torch)

---

## Contact Information for Further Research

**Air Force Historical Research Agency (AFHRA)**
- Email: AFHRA.NEWS@us.af.mil
- Website: https://www.dafhistory.af.mil/
- Search: https://airforcehistoryindex.org/

**National Archives**
- Aircraft records: RG 18 (AAF Central Files)
- Unit records: RG 342 (USAF Historical Data)

---

**Prepared by**: Claude (AI Assistant)  
**Date**: October 27, 2025  
**Schema**: air_force_schema.json v1.0  
**Protocol**: Hybrid Source Validation Protocol
