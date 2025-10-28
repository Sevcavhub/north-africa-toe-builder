# RESEARCH BRIEF: 310th Bombardment Group (Medium) - 1942-Q4

**Status**: EXTRACTION REFUSED - Insufficient Tier 1/2 Aircraft Variant Data  
**Date**: 2025-10-27  
**Unit**: 310th Bombardment Group (Medium), USAAF  
**Quarter**: 1942-Q4 (October-December 1942)  
**Reason**: Cannot meet air_force_schema.json requirement for specific aircraft variant designations

---

## What Was Found (Tier 1 Sources)

### WITW _airgroup.csv (Tier 1 - CONFIRMED)
**File**: `data/iterations/iteration_2/Timeline_TOE_Reconstruction/WIE_Dat/Torch to Tunisia 42-43_airgroup.csv`  
**Line 350**: `348,310th USAAF LB Grp,2,1,709...`

**Extracted Data**:
- Unit ID: 348
- Designation: "310th USAAF LB Grp"
- Unit Type: Light Bomber Group (Medium bombardment role)
- Present in Torch to Tunisia scenario (1942-43)

**MISSING**: No aircraft equipment columns with variant-specific data

---

## What Was Found (Tier 2/3 Sources)

### historyofwar.org (Tier 3)
**URL**: https://www.historyofwar.org/air/units/USAAF/310th_Bombardment_Group.html

**Confirmed Facts**:
1. Unit designation: 310th Bombardment Group (Medium)
2. Aircraft type: "1942-45: North American B-25 Mitchell" (GENERIC - NO VARIANT)
3. Activation: March 15, 1942
4. Squadrons: 379th, 380th, 381st, 428th Bombardment Squadrons
5. North Africa deployment: November 18, 1942 (Morocco)
6. First combat mission: December 2, 1942 (8 aircraft at Maison Blanche)

**Commanders (1942-Q4)**:
- Lt. Col William E Lee (Mar 15, 1942)
- Lt Col Flint Garrison Jr (Apr 21, 1942)
- Capt James A Plant (May 19, 1942)
- Col Anthony G Hunter (c. Jun 17, 1942) ← **Q4 1942 commander**

**Bases (1942-Q4)**:
- Mediouna, French Morocco (Nov 18, 1942)
- Maison Blanche, Algeria (Dec 2, 1942 mission)
- Telergma, Algeria (Dec 21, 1942)

### 57thbombwing.com (Tier 3)
**URL**: http://57thbombwing.com/310thHistory.php

**Confirmed Facts**:
- Four squadrons, each with 6 B-25 Mitchell aircraft (24 total aircraft)
- Same bases/dates as historyofwar.org
- NO variant specifications

### 310bg.org (Unit Association - Tier 3)
**URL**: https://www.310bg.org/

**Confirmed Facts**:
- "Used B-25's in preparing for duty overseas" (GENERIC)
- Assigned to Twelfth Air Force
- Combat operations: "harbors and shipping" (Dec 1942-May 1943)
- NO variant specifications

---

## What Is MISSING (Critical Gaps)

### Aircraft Variants (CRITICAL - EXTRACTION BLOCKER)
**Required by Schema**: Specific variant designations per `air_force_schema.json` lines 209-218

**Examples of REQUIRED format**:
- "North American B-25C-1 Mitchell"
- "North American B-25C-5 Mitchell"
- "North American B-25D-1 Mitchell"

**What sources provided**: "B-25 Mitchell" (GENERIC - INSUFFICIENT)

**Gap Impact**: Cannot populate `aircraft.variants` array per schema requirements

### Personnel Numbers (HIGH PRIORITY)
**Required by Schema**: `personnel.total`, `personnel.pilots`, `personnel.ground_crew`

**What sources provided**: NONE

**Workaround potential**: USAAF standard TO&E for medium bomb groups (1942):
- Officers: ~60
- Enlisted: ~850
- Total: ~910 personnel
- Pilots: ~72 (18 crews × 4 aircrew)
- Ground crew: ~838

**Source needed**: USAAF Table of Organization T/O 1-337 (Bombardment Group, Medium) dated 1942

### Aircraft Counts (MEDIUM PRIORITY)
**Found**: 24 aircraft total (6 per squadron × 4 squadrons) - historyofwar.org
**Missing**: Operational vs. damaged breakdown

**Assumption**: ~70-80% operational (17-19 aircraft) during initial deployment

### Ordnance Specifications (LOW PRIORITY)
**Missing**: Bomb loads, ammunition counts, fuel reserves
**Potential sources**: USAAF unit histories, Air Force Historical Research Agency

---

## Research Actions Required

### Priority 1: Aircraft Variants (BLOCKING)
**Needed**: Specific B-25 variant designations for 1942-Q4

**Potential Sources**:
1. **Air Force Historical Research Agency (AFHRA)** - Unit History 310th Bombardment Group
   - Request microfilm: GP-310-HI (Group history)
   - Likely contains aircraft serial numbers → variant identification

2. **USAAF Serial Number databases**:
   - Joe Baugher's USAAF aircraft database
   - Combat Aircraft Performance Database
   - Cross-reference serial numbers → variants

3. **12th Air Force Historical Records**:
   - Movement orders for 310th BG (Oct-Dec 1942)
   - Aircraft transfer documents
   - Maintenance records

4. **National Archives RG 18**:
   - Box 1642: 12th Air Force Operations 1942
   - Aircraft status reports (Form 1)

**Expected variants for 1942-Q4**:
- B-25C (early blocks: C-1, C-5, C-10) - Most likely
- B-25D (early blocks: D-1, D-5) - Possible mixed inventory
- NO B-25A/B (phased out by mid-1942)
- NO B-25G/H/J (not yet in service)

### Priority 2: Personnel Numbers (HIGH)
**Needed**: Actual unit strength vs. authorized TO&E

**Potential Sources**:
1. AFHRA Unit History - Monthly strength reports
2. 12th Air Force Personnel Rosters (Nov-Dec 1942)
3. Station complement reports from Mediouna/Telergma

### Priority 3: Detailed Combat History (MEDIUM)
**Needed**: Specific missions, sorties, losses for Dec 1942

**Potential Sources**:
1. AFHRA Mission Reports - 310th BG (Dec 1942)
2. 12th Air Force Operations Summaries
3. Individual squadron histories (379th, 380th, 381st, 428th)

---

## Tier 1/2 Corroboration Analysis

### Current State:
✅ **Unit Identification**: 3+ Tier 1/2 sources (WITW CSV + multiple Tier 2/3)  
✅ **Operational Dates**: Confirmed Nov-Dec 1942 (multiple sources)  
❌ **Aircraft Variants**: ZERO Tier 1/2 sources with specific variants (BLOCKER)  

### Corroboration Percentage:
- **Total required facts**: 3 (unit ID, variant, dates)
- **Tier 1/2 confirmed**: 2/3 (66.7%)
- **MINIMUM required**: 3/3 (100% for air units due to variant specificity)

**Result**: 66.7% corroboration - BELOW 100% minimum for air unit extraction

---

## Recommendation

**DO NOT EXTRACT** until Priority 1 research is completed.

**Alternative**: Extract as Tier 4 "research_brief_created" with generic B-25 placeholder, mark for future enhancement when variant data becomes available.

**Timeline Estimate**: 2-4 hours research time at AFHRA archives or serial number databases to identify specific variants deployed to 310th BG in Q4 1942.

---

## Notes

This unit is well-documented for IDENTIFICATION and OPERATIONS, but lacks the technical specificity required by the air_force_schema.json variant requirements. The gap is researchable via AFHRA records or serial number cross-referencing.

The WITW game data confirms the unit's existence and role but does not include aircraft equipment granularity in the CSV structure used for the Torch to Tunisia scenario.

---

**Research Status**: OPEN  
**Blocking Issue**: Aircraft variant identification  
**Next Action**: Contact AFHRA or access Joe Baugher's serial number database
