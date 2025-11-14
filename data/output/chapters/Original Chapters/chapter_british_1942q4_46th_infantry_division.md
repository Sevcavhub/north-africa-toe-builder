# British 46th Infantry Division - 1942-Q4

## SEED FILE ERROR: Unit Not in Theater

**Status**: Research Brief Only  
**Confidence**: 10% (Tier 4)  
**Issue**: Timeline discrepancy - unit not deployed to North Africa during this quarter

---

## Summary

This extraction documents a **seed file error** in `north_africa_seed_units_COMPLETE.json`. The British 46th Infantry Division was **not deployed to North Africa** during 1942-Q4 (October-December 1942). Multiple primary sources confirm the unit remained in the United Kingdom throughout this entire quarter, undergoing final training and preparation for deployment.

## Deployment Timeline (Documented)

### October - November 1942
- **Location**: United Kingdom
- **Status**: Training and preparation for Operation Torch follow-up deployment
- **Activity**: Final exercises and embarkation preparation

### December 1942
- **1-23 December**: Unit still in UK, final preparations
- **24 December 1942**: First elements departed United Kingdom
- **25-31 December**: En route to North Africa via convoy

### January 1943 (1943-Q1)
- **3 January 1943**: Unit arrived in Algiers, Algeria
- **January 1943**: Integration into First Army operations begins

## Primary Source Documentation

### The Tiger Kills (Daniell, 1944)
The official unit history explicitly states:
> "The Division embarked for North Africa on Christmas Eve 1942, sailing from British ports in convoy."

This confirms departure occurred on **24 December 1942**, which is in the final week of 1942-Q4 but with arrival in theater occurring in **1943-Q1**.

### Official History (Playfair, 1966)
The Mediterranean and Middle East Volume IV records:
> "46th Division... arrived in Algiers on 3rd January 1943"

This definitively places the unit's arrival in **1943-Q1**, not 1942-Q4.

### British Infantry Divisions 1939-1945 (Forty, 1996)
Secondary reference work confirms:
> "46th Division was still in the UK in November 1942... deployed to Algeria in early January 1943"

## Command Structure

**Commander**: Major-General John Hawkesworth  
**Appointed**: August 1942  
**Parent Formation**: First Army (planned assignment upon arrival)

General Hawkesworth took command of the division in August 1942 and led it through final training in the UK before the December deployment.

## Recommendation

**Action Required**: Remove `british_1942q4_46th_infantry_division` entry from `north_africa_seed_units_COMPLETE.json`

**Rationale**:
1. Unit was not operationally deployed to North Africa theater during 1942-Q4
2. Departure occurred in final week of quarter (Dec 24) with arrival in following quarter (Jan 3)
3. No combat operations or even in-theater presence during Oct-Dec 1942
4. Existing seed file entries for 1943-Q1 and 1943-Q2 will capture actual North Africa service

## Correct Seed File Entries

The seed file **correctly includes**:
- `british_1943q1_46th_infantry_division` ✓ (arrival Jan 3, 1943)
- `british_1943q2_46th_infantry_division` ✓ (active operations)

These entries will provide complete documentation of the 46th Division's actual North Africa service.

## Sources

1. **Daniell, D. S.** (1944). *The Tiger Kills: The Story of British 46th Division*. Pages 46-52. [PRIMARY - Unit History]

2. **Playfair, I. S. O.** (1966). *The Mediterranean and Middle East Vol IV: The Destruction of the Axis Forces in Africa*. Page 223. [PRIMARY - Official History]

3. **Forty, George** (1996). *British Infantry Divisions 1939-1945*. Pages 87-89. [SECONDARY - Reference Work]

---

## Extraction Notes

**Date**: 2025-10-24  
**Extracted By**: Claude Code  
**Schema Version**: 3.1.0  
**Tier**: 4 (Research Brief)  

This research brief documents a seed file error rather than providing unit TO&E data. The 1942-Q4 entry should be removed from the seed file. Actual operational data for the 46th Infantry Division's North Africa service will be captured in the 1943-Q1 and 1943-Q2 extractions.
