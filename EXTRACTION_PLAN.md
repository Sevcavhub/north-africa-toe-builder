# Unit Extraction Dependency Analysis & Sequential Plan

**Generated:** 2025-10-20
**Analyst:** Claude Code
**Status:** 307/420 unit-quarters remaining (73% remaining, 27% complete)

---

## Executive Summary

### Current Status
- **Total unit-quarters:** 420
- **Completed:** 113 (27%)
- **Remaining:** 307 (73%)

### Key Findings

**1. HIERARCHICAL DEPENDENCIES: 35 parent-child relationships identified**
- German: 4 Army/Corps dependencies
- Italian: 13 Army/Corps dependencies
- British: 18 Army/Corps dependencies
- Must extract ARMIES before CORPS before DIVISIONS

**2. TEMPORAL DEPENDENCIES: 82 units appearing in multiple quarters**
- Same unit across quarters should be extracted sequentially (Q1→Q2→Q3→Q4)
- Enables "changed since last quarter" documentation
- Examples:
  - 4th Indian Division (11 quarters: 1940-Q2 through 1943-Q2)
  - Trieste Division (9 quarters: 1941-Q1 through 1943-Q2)
  - XXI Corps (8 quarters: 1940-Q4 through 1943-Q2)

**3. PARALLEL OPPORTUNITIES: Different nations can be extracted simultaneously**
- No cross-nation dependencies (German units don't depend on British units)
- 1942 has 119 unit-quarters across 5 nations
- Can parallelize up to 5 nations at once

---

## Critical Dependencies

### Type 1: Hierarchical (Parent → Child)

**RULE:** Must extract parent formation BEFORE subordinate units in the same quarter.

**German Examples:**
```
Panzerarmee Afrika (army) → Deutsches Afrikakorps (corps)
  ↓
Deutsches Afrikakorps (corps) → 15. Panzer-Division (division)
```

**British Examples:**
```
8th Army (army) → XIII Corps (corps) → 7th Armoured Division (division)
8th Army (army) → XXX Corps (corps) → 50th Infantry Division (division)
First Army (army) → V Corps (corps) → 78th Infantry Division (division)
```

**Italian Examples:**
```
10th Army (army) → XXI Corps (corps) → Bologna Division (division)
First Italian Army (army) → X Corps (corps) → Trieste Division (division)
```

**Critical Pairs (35 total):**
| Quarter | Nation | Parent | Child |
|---------|--------|--------|-------|
| 1942-Q2 | german | Panzerarmee Afrika | Deutsches Afrikakorps |
| 1940-Q4 | italian | 10th Army | XXI Corps |
| 1942-Q1 | british | 8th Army | XIII Corps |
| 1942-Q1 | british | 8th Army | XXX Corps |
| 1942-Q3 | british | 8th Army | X Corps |
| 1942-Q4 | british | First Army | V Corps |
| 1942-Q4 | british | First Army | IX Corps |
| 1943-Q1 | italian | First Italian Army | XXI Corps |
| 1943-Q1 | italian | First Italian Army | X Corps |
| 1943-Q1 | italian | First Italian Army | XIX Corps |

*(See dependency_analysis.json for complete list of 35 relationships)*

---

### Type 2: Temporal (Same Unit → Next Quarter)

**RULE:** Extract sequentially Q1→Q2→Q3→Q4 for units appearing in multiple quarters.

**Reason:** Later quarters reference earlier for "changes since last quarter" narrative.

**Top 15 Multi-Quarter Units:**

| Unit | Nation | Quarters | Sequence |
|------|--------|----------|----------|
| 4th Indian Division | british | 11 | 1940-Q2, Q3, Q4, 1941-Q2, Q3, 1942-Q1, Q2, Q3, Q4, 1943-Q1, Q2 |
| Trieste Division | italian | 9 | 1941-Q1, Q3, Q4, 1942-Q1, Q2, Q3, Q4, 1943-Q1, Q2 |
| XXI Corps | italian | 8 | 1940-Q4, 1941-Q1, 1942-Q1, Q2, Q3, Q4, 1943-Q1, Q2 |
| Bologna Division | italian | 8 | 1940-Q3, Q4, 1941-Q1, Q3, 1942-Q1, Q2, Q3, Q4 |
| Brescia Division | italian | 8 | 1940-Q3, Q4, 1941-Q1, Q2, 1942-Q1, Q2, Q3, Q4 |
| Trento Division | italian | 8 | 1940-Q4, 1941-Q3, Q4, 1942-Q1, Q2, Q3, Q4, 1943-Q1 |
| 90. leichte Division | german | 7 | 1941-Q3, Q4, 1942-Q1, Q2, Q3, 1943-Q1, Q2 |
| XX Mobile Corps | italian | 7 | 1941-Q2, Q3, Q4, 1942-Q1, Q2, Q3, Q4 |
| Ariete Division | italian | 7 | 1940-Q4, 1941-Q3, Q4, 1942-Q1, Q2, Q3, Q4 |
| XXX Corps | british | 7 | 1941-Q2, 1942-Q1, Q2, Q3, Q4, 1943-Q1, Q2 |
| 50th Infantry Division | british | 7 | 1941-Q2, Q3, 1942-Q1, Q2, Q3, 1943-Q1, Q2 |
| Littorio Division | italian | 6 | 1941-Q4, 1942-Q1, Q2, Q3, Q4, 1943-Q1 |
| Pavia Division | italian | 6 | 1940-Q3, Q4, 1941-Q1, 1942-Q1, Q2, Q3 |
| Savona Division | italian | 6 | 1940-Q3, Q4, 1941-Q4, 1942-Q1, Q2, Q3 |
| XIII Corps | british | 6 | 1942-Q1, Q2, Q3, Q4, 1943-Q1, Q2 |

*(See dependency_analysis.json for complete list of 82 temporal sequences)*

---

### Type 3: Equipment Sharing (Informational - Not Blocking)

**NOTE:** Equipment dependencies do NOT block extraction. Equipment allocations are calculated post-extraction during Phase 3 (Equipment Distribution).

**Examples of equipment sharing:**
- Ariete & Trieste divisions shared equipment from XX Mobile Corps artillery pool
- British Commonwealth divisions shared 25-pdr field guns from corps artillery
- German panzer divisions shared repair depots and spare parts

**Action:** Document equipment sharing in unit notes, but proceed with extraction regardless.

---

## Recommended Extraction Strategy

### Strategy A: Chronological-First (RECOMMENDED)

**Rationale:**
- Preserves historical continuity (1940→1941→1942→1943)
- Temporal sequences naturally satisfied
- Enables "changed since" narrative for multi-quarter units
- Allows parallel nation batches within each year

**Approach:**

**Phase 1: 1940 (42 unit-quarters)**
- Focus: Italian invasion of Egypt, Operation Compass
- Parallel by nation:
  - Italian: 42 unit-quarters (10th Army, XXII Corps, multiple divisions)
  - British: Already complete (Western Desert Force, 4th Indian, 7th Armoured)

**Phase 2: 1941 (40 unit-quarters remaining)**
- Focus: Afrika Korps arrival, Siege of Tobruk, Operation Crusader
- Parallel by nation:
  - German: 0 remaining (complete!)
  - Italian: 14 unit-quarters
  - British: 24 unit-quarters
  - French: 2 unit-quarters (1re Brigade Française Libre Q4, 1942-Q1)

**Phase 3: 1942 (119 unit-quarters - LARGEST)**
- Focus: Gazala, El Alamein battles
- Parallel by nation (5 nations simultaneously):
  - German: 15 unit-quarters
  - Italian: 48 unit-quarters
  - British: 48 unit-quarters
  - American: 3 unit-quarters (Operation Torch late 1942)
  - French: 5 unit-quarters (Free French)

**Phase 4: 1943 (106 unit-quarters)**
- Focus: Tunisia Campaign final offensive
- Parallel by nation:
  - German: 19 unit-quarters
  - Italian: 68 unit-quarters
  - British: 60 unit-quarters
  - American: 14 unit-quarters (II Corps, multiple divisions)
  - French: 13 unit-quarters (multiple March divisions)

**Within each year, extract by hierarchy:**
1. Armies (theater level)
2. Corps
3. Divisions
4. Brigades/Regiments (if any)

---

### Strategy B: Hierarchical-First (Alternative)

**Rationale:**
- Ensures parent formations exist before subordinates
- Satisfies hierarchical dependencies first
- Risk: Breaks temporal continuity (same division across years extracted non-sequentially)

**Approach:**

**Phase 1: Extract all Army-level units (theater commands)**
- German: Panzergruppe Afrika, Panzerarmee Afrika, 5th Panzer Army
- Italian: 10th Army, First Italian Army
- British: 8th Army, First Army
- American: (no remaining - II Corps is corps level)

**Phase 2: Extract all Corps-level units**
- German: Deutsches Afrikakorps (3 quarters)
- Italian: XXI Corps (8 quarters), XXII Corps (2 quarters), X Corps (4 quarters), XIX Corps (2 quarters), XX Mobile Corps (7 quarters)
- British: XIII Corps (6 quarters), XXX Corps (7 quarters), X Corps (4 quarters), V Corps (3 quarters), IX Corps (3 quarters)
- American: II Corps (2 quarters)

**Phase 3: Extract all Division-level units**
- 200+ unit-quarters across all nations
- Subdivide by type: Panzer, Armoured, Infantry, Motorized, Light

**Phase 4: Extract remaining Brigade/Regiment level**
- Polish Carpathian Brigade
- Greek Brigade
- Czechoslovakian 11th Infantry Battalion
- Various French brigades

**Drawback:** Breaks temporal flow. Extracting "4th Indian Division 1942-Q2" before "4th Indian Division 1940-Q2" loses historical context.

---

## Parallelization Opportunities

### Maximum Parallel Batches

**1942 Example (119 unit-quarters across 5 nations):**

Can extract **5 nations simultaneously** with no conflicts:

| Nation | Count | Example Units |
|--------|-------|---------------|
| German | 15 | Panzerarmee Afrika, Deutsches Afrikakorps, 15. Pz.Div, 21. Pz.Div, 90. le.Div, 164. le.Div |
| Italian | 48 | XX Mobile Corps, XXI Corps, Ariete, Trieste, Littorio, Bologna, Brescia, Trento, Pavia, Savona, Folgore |
| British | 48 | 8th Army, XIII Corps, XXX Corps, X Corps, 7th Armoured, 1st Armoured, 50th Inf, 51st Highland, 4th Indian, 2nd NZ |
| American | 3 | 1st Inf Div, 3rd Inf Div, 9th Inf Div (Operation Torch) |
| French | 5 | 1re Division Française Libre (Bir Hakeim, El Alamein, Tunisia) |

**Implementation:**
- Assign each nation to separate autonomous agent
- No cross-nation data dependencies
- Reduces 119 sequential tasks to 5 parallel batches
- **Time savings:** ~95% reduction (if agents run truly in parallel)

---

## Recommended Extraction Plan: Chronological-First, Hierarchy-Phased

### Year 1: 1940 (42 unit-quarters)

**Batch 1.1: Italian Armies & Corps (1940-Q3, Q4)**
```
1940-Q3:
  - 10th Army (army)
  - XXII Corps (corps)

1940-Q4:
  - 10th Army (army, Q4)
  - XXI Corps (corps)
  - XXII Corps (corps, Q4)
```

**Batch 1.2: Italian Divisions (1940-Q2, Q3, Q4)**

*1940-Q2:* (4 divisions)
- Sirte Division
- Marmarica Division
- Cirene Division
- Sabratha Division

*1940-Q3:* (13 divisions - after 10th Army/XXII Corps)
- Bologna Division
- Pavia Division
- Brescia Division
- Savona Division
- Catanzaro Division
- Sirte Division (Q3)
- Marmarica Division (Q3)
- Cirene Division (Q3)
- Sabratha Division (Q3)
- 1st Libyan Division
- 2nd Libyan Division
- 4th CC.NN. Division '3 Gennaio'

*1940-Q4:* (22 divisions - after 10th Army/XXI/XXII Corps)
- Ariete Division
- Trento Division
- Bologna Division (Q4)
- Pavia Division (Q4)
- Brescia Division (Q4)
- Savona Division (Q4)
- Catanzaro Division (Q4)
- Sirte Division (Q4)
- Marmarica Division (Q4)
- Cirene Division (Q4)
- Sabratha Division (Q4)
- 1st Libyan Division (Q4)
- 2nd Libyan Division (Q4)
- 4th CC.NN. Division '3 Gennaio' (Q4)
- 1st CC.NN. Division '23 Marzo'
- 2nd CC.NN. Division '28 Ottobre'

**Dependencies:**
- 1940-Q3: Extract 10th Army BEFORE XXII Corps
- 1940-Q4: Extract 10th Army BEFORE XXI/XXII Corps
- 1940-Q4: Extract XXI/XXII Corps BEFORE divisions

**Parallelization:** After armies/corps extracted, all divisions within quarter can be parallel.

---

### Year 2: 1941 (40 unit-quarters remaining)

**Batch 2.1: Italian Corps & Divisions (1941-Q1, Q2, Q3, Q4)**

*1941-Q1:* (14 unit-quarters)
- XXI Corps
- Trieste Division
- Ariete Division (Q1, after 1940-Q4)
- Bologna Division (Q1, after 1940-Q4)
- Pavia Division (Q1, after 1940-Q4)
- Brescia Division (Q1, after 1940-Q4)
- 1st Libyan Division (Q1, after 1940-Q4)
- 2nd Libyan Division (Q1, after 1940-Q4)
- 4th CC.NN. Division '3 Gennaio' (Q1, after 1940-Q4)
- 1st CC.NN. Division '23 Marzo' (Q1, after 1940-Q4)
- 2nd CC.NN. Division '28 Ottobre' (Q1, after 1940-Q4)

*1941-Q2:* (2 unit-quarters)
- XX Mobile Corps
- Brescia Division (Q2, after 1941-Q1)

*1941-Q3:* (5 unit-quarters)
- XX Mobile Corps (Q3, after 1941-Q2)
- Trieste Division (Q3, after 1941-Q1)
- Ariete Division (Q3, after 1941-Q1)
- Bologna Division (Q3, after 1941-Q1)
- Trento Division (Q3, after 1940-Q4)

*1941-Q4:* (7 unit-quarters)
- XX Mobile Corps (Q4, after 1941-Q3)
- Trieste Division (Q4, after 1941-Q3)
- Ariete Division (Q4, after 1941-Q3)
- Littorio Division (first quarter)
- Trento Division (Q4, after 1941-Q3)
- Savona Division (Q4, after 1940-Q4)

**Batch 2.2: British Corps & Divisions (1941-Q1, Q2, Q3, Q4)**

*1941-Q1:* (2 unit-quarters)
- 5th Indian Division (first quarter)

*1941-Q2:* (1 unit-quarter)
- XXX Corps (first quarter)

*1941-Q3:* (3 unit-quarters)
- 1st South African Division (Q3, after 1940-Q4)
- 2nd South African Division (first quarter)
- 5th Indian Division (Q3, after 1941-Q1)
- Czechoslovakian 11th Infantry Battalion (first quarter)

*1941-Q4:* (2 unit-quarters)
- 2nd South African Division (Q4, after 1941-Q3)
- Czechoslovakian 11th Infantry Battalion (Q4, after 1941-Q3)

**Batch 2.3: French Brigades (1941-Q4, 1942-Q1)**

- 1re Brigade Française Libre (1941-Q4)
- 1re Brigade Française Libre (1942-Q1, after 1941-Q4)

**Batch 2.4: German (1941 complete - 0 remaining!)**

---

### Year 3: 1942 (119 unit-quarters - LARGEST BATCH)

**Parallel Strategy: 5 nations simultaneously (after armies/corps extracted)**

**Batch 3.1: Armies & High Commands (extract FIRST)**

*1942-Q1:*
- Panzerarmee Afrika (german)
- Panzergruppe Afrika (german, Q1 after 1941-Q3)
- 8th Army (british)

*1942-Q2:*
- Panzerarmee Afrika (german, Q2 after 1942-Q1)
- 8th Army (british, Q2 after 1942-Q1)

*1942-Q3:*
- Panzerarmee Afrika (german, Q3 after 1942-Q2)
- 8th Army (british, Q3 after 1942-Q2)

*1942-Q4:*
- Panzerarmee Afrika (german, Q4 after 1942-Q3)
- 8th Army (british, Q4 after 1942-Q3)
- First Army (british, first quarter)
- 5th Panzer Army (german, first quarter)

**Batch 3.2: Corps (extract AFTER armies)**

*1942-Q1:* (5 corps)
- XXI Corps (italian, Q1 after 1941-Q1)
- XX Mobile Corps (italian, Q1 after 1941-Q4)
- XIII Corps (british, Q1 after 1941-Q4)
- XXX Corps (british, Q1 after 1941-Q2)

*1942-Q2:* (5 corps)
- Deutsches Afrikakorps (german)
- XXI Corps (italian, Q2 after 1942-Q1)
- XX Mobile Corps (italian, Q2 after 1942-Q1)
- XIII Corps (british, Q2 after 1942-Q1)
- XXX Corps (british, Q2 after 1942-Q1)

*1942-Q3:* (6 corps)
- XXI Corps (italian, Q3 after 1942-Q2)
- XX Mobile Corps (italian, Q3 after 1942-Q2)
- X Corps (italian, first quarter)
- XIII Corps (british, Q3 after 1942-Q2)
- XXX Corps (british, Q3 after 1942-Q2)
- X Corps (british, first quarter)

*1942-Q4:* (9 corps)
- Deutsches Afrikakorps (german, Q4 after 1942-Q2)
- XXI Corps (italian, Q4 after 1942-Q3)
- XX Mobile Corps (italian, Q4 after 1942-Q3)
- X Corps (italian, Q4 after 1942-Q3)
- XIII Corps (british, Q4 after 1942-Q3)
- XXX Corps (british, Q4 after 1942-Q3)
- X Corps (british, Q4 after 1942-Q3)
- V Corps (british, first quarter)
- IX Corps (british, first quarter)

**Batch 3.3: Divisions (extract AFTER corps) - PARALLEL BY NATION**

*German (15 unit-quarters):*
- 1942-Q2: 15. Panzer-Division, 90. leichte Division (Q2 after 1942-Q1)
- 1942-Q3: 15. Panzer-Division (Q3 after 1942-Q2), 90. leichte Division (Q3 after 1942-Q2), 164. leichte Division, Ramcke Parachute Brigade
- 1942-Q4: 15. Panzer-Division (Q4 after 1942-Q3), 90. leichte Division (Q4 after 1942-Q3), 164. leichte Division (Q4 after 1942-Q3), Ramcke Parachute Brigade (Q4 after 1942-Q3), 5th Panzer Army (Q4), 10. Panzer-Division, Hermann Göring Division

*Italian (48 unit-quarters):*
- 1942-Q1: Trieste (Q1 after 1941-Q4), Ariete (Q1 after 1941-Q4), Littorio (Q1 after 1941-Q4), Brescia (Q1 after 1941-Q2), Bologna (Q1 after 1941-Q3), Trento (Q1 after 1941-Q4), Pavia (Q1 after 1941-Q1), Savona (Q1 after 1941-Q4)
- 1942-Q2: Trieste (Q2 after 1942-Q1), Ariete (Q2 after 1942-Q1), Littorio (Q2 after 1942-Q1), Brescia (Q2 after 1942-Q1), Bologna (Q2 after 1942-Q1), Trento (Q2 after 1942-Q1), Pavia (Q2 after 1942-Q1), Savona (Q2 after 1942-Q1), 1re Division Française Libre (Q2 after 1942-Q1), Superga Division
- 1942-Q3: Trieste (Q3 after 1942-Q2), Ariete (Q3 after 1942-Q2), Littorio (Q3 after 1942-Q2), Brescia (Q3 after 1942-Q2), Bologna (Q3 after 1942-Q2), Trento (Q3 after 1942-Q2), Pavia (Q3 after 1942-Q2), Savona (Q3 after 1942-Q2), Folgore Division, Superga Division (Q3 after 1942-Q2)
- 1942-Q4: Trieste (Q4 after 1942-Q3), Ariete (Q4 after 1942-Q3), Littorio (Q4 after 1942-Q3), Brescia (Q4 after 1942-Q3), Bologna (Q4 after 1942-Q3), Trento (Q4 after 1942-Q3), Folgore Division (Q4 after 1942-Q3), Superga Division (Q4 after 1942-Q3), Centauro Division, La Spezia Division, Pistoia Division

*British (48 unit-quarters):*
- 1942-Q1: 7th Armoured (Q1 after 1941-Q4), 1st South African (Q1 after 1941-Q3), 2nd South African (Q1 after 1941-Q4), 4th Indian (Q1 after 1941-Q4), 5th Indian (Q1 after 1941-Q3), 50th Infantry (Q1 after 1941-Q3), 2nd New Zealand (Q1 after 1941-Q4), 9th Australian
- 1942-Q2: 1st Armoured (Q2 after 1942-Q1), 7th Armoured (Q2 after 1942-Q1), 1st South African (Q2 after 1942-Q1), 2nd South African (Q2 after 1942-Q1), 4th Indian (Q2 after 1942-Q1), 5th Indian (Q2 after 1942-Q1), 50th Infantry (Q2 after 1942-Q1), 2nd New Zealand (Q2 after 1942-Q1), 1re Division Française Libre (french)
- 1942-Q3: 1st Armoured (Q3 after 1942-Q2), 7th Armoured (Q3 after 1942-Q2), 10th Armoured Division, 4th Indian (Q3 after 1942-Q2), 44th Infantry Division, 50th Infantry (Q3 after 1942-Q2), 51st Highland Division, 2nd New Zealand (Q3 after 1942-Q2), 9th Australian (Q3 after 1942-Q1), Greek Brigade, 1re Division Française Libre (french, Q3 after 1942-Q2)
- 1942-Q4: 1st Armoured (Q4 after 1942-Q3), 7th Armoured (Q4 after 1942-Q3), 10th Armoured Division (Q4 after 1942-Q3), 6th Armoured Division, 1st Infantry Division, 4th Infantry Division, 4th Indian (Q4 after 1942-Q3), 44th Infantry Division (Q4 after 1942-Q3), 46th Infantry Division, 50th Infantry (Q4 after 1942-Q3), 51st Highland Division (Q4 after 1942-Q3), 78th Infantry Division, 2nd New Zealand (Q4 after 1942-Q3), Greek Brigade (Q4 after 1942-Q3)

*American (3 unit-quarters):*
- 1942-Q4: II Corps, 2nd Armored Division, 34th Infantry Division

*French (5 unit-quarters):*
- 1942-Q2: 1re Division Française Libre (counted with British)
- 1942-Q3: 1re Division Française Libre (Q3, counted with British)
- 1942-Q4: 1re Division Française Libre (Q4), Force L

**Dependencies Summary for 1942:**
- Armies MUST be extracted before Corps (same quarter)
- Corps MUST be extracted before Divisions (same quarter)
- Same unit temporal: Q1→Q2→Q3→Q4
- Different nations: PARALLEL (no dependencies)

---

### Year 4: 1943 (106 unit-quarters)

**Batch 4.1: Armies (extract FIRST)**

*1943-Q1:*
- Panzerarmee Afrika (german, Q1 after 1942-Q4)
- 8th Army (british, Q1 after 1942-Q4)
- First Army (british, Q1 after 1942-Q4)
- First Italian Army (italian)

*1943-Q2:*
- 8th Army (british, Q2 after 1943-Q1)
- First Army (british, Q2 after 1943-Q1)
- 5th Panzer Army (german, Q2 after 1942-Q4)
- First Italian Army (italian, Q2 after 1943-Q1)

**Batch 4.2: Corps (extract AFTER armies)**

*1943-Q1:* (9 corps)
- Deutsches Afrikakorps (german, Q1 after 1942-Q4)
- XXI Corps (italian, Q1 after 1942-Q4)
- X Corps (italian, Q1 after 1942-Q4)
- XIX Corps (italian)
- XIII Corps (british, Q1 after 1942-Q4)
- XXX Corps (british, Q1 after 1942-Q4)
- X Corps (british, Q1 after 1942-Q4)
- V Corps (british, Q1 after 1942-Q4)
- IX Corps (british, Q1 after 1942-Q4)

*1943-Q2:* (10 corps)
- Deutsches Afrikakorps (german, Q2 after 1943-Q1)
- XXI Corps (italian, Q2 after 1943-Q1)
- X Corps (italian, Q2 after 1943-Q1)
- XIX Corps (italian, Q2 after 1943-Q1)
- II Corps (american)
- XIII Corps (british, Q2 after 1943-Q1)
- XXX Corps (british, Q2 after 1943-Q1)
- X Corps (british, Q2 after 1943-Q1)
- V Corps (british, Q2 after 1943-Q1)
- IX Corps (british, Q2 after 1943-Q1)

**Batch 4.3: Divisions (extract AFTER corps) - PARALLEL BY NATION**

*German (19 unit-quarters):*
- 1943-Q1: 90. leichte Division (Q1 after 1942-Q4), 15. Panzer-Division (Q1 after 1942-Q4), 21. Panzer-Division (Q1 after 1942-Q4), 164. leichte Division (Q1 after 1942-Q3), Hermann Göring Division (Q1 after 1942-Q4)
- 1943-Q2: 90. leichte Division (Q2 after 1943-Q1), 15. Panzer-Division (Q2 after 1943-Q1), 21. Panzer-Division (Q2 after 1943-Q1), 10. Panzer-Division (Q2 after 1942-Q4), 164. leichte Division (Q2 after 1943-Q1), Hermann Göring Division (Q2 after 1943-Q1)

*Italian (68 unit-quarters):*
- 1943-Q1: Trieste (Q1 after 1942-Q4), Littorio (Q1 after 1942-Q4), Trento (Q1 after 1942-Q4), Superga (Q1 after 1942-Q4), Centauro (Q1 after 1942-Q4), La Spezia (Q1 after 1942-Q4), Pistoia (Q1 after 1942-Q4), Giovani Fascisti Division
- 1943-Q2: Trieste (Q2 after 1943-Q1), Trento (Q2 after 1943-Q1), Superga (Q2 after 1943-Q1), Centauro (Q2 after 1943-Q1), La Spezia (Q2 after 1943-Q1), Pistoia (Q2 after 1943-Q1), Giovani Fascisti Division (Q2 after 1943-Q1)

*British (60 unit-quarters):*
- 1943-Q1: 1st Armoured (Q1 after 1942-Q4), 7th Armoured (Q1 after 1942-Q4), 10th Armoured (Q1 after 1942-Q4), 6th Armoured (Q1 after 1942-Q4), 1st Infantry (Q1 after 1942-Q4), 4th Infantry (Q1 after 1942-Q4), 4th Indian (Q1 after 1942-Q4), 44th Infantry (Q1 after 1942-Q4), 46th Infantry (Q1 after 1942-Q4), 50th Infantry (Q1 after 1942-Q4), 51st Highland (Q1 after 1942-Q4), 78th Infantry (Q1 after 1942-Q4), 2nd New Zealand (Q1 after 1942-Q4), Greek Brigade (Q1 after 1942-Q4)
- 1943-Q2: 1st Armoured (Q2 after 1943-Q1), 7th Armoured (Q2 after 1943-Q1), 10th Armoured (Q2 after 1943-Q1), 6th Armoured (Q2 after 1943-Q1), 1st Infantry (Q2 after 1943-Q1), 4th Infantry (Q2 after 1943-Q1), 4th Indian (Q2 after 1943-Q1), 44th Infantry (Q2 after 1943-Q1), 46th Infantry (Q2 after 1943-Q1), 50th Infantry (Q2 after 1943-Q1), 51st Highland (Q2 after 1943-Q1), 78th Infantry (Q2 after 1943-Q1), 2nd New Zealand (Q2 after 1943-Q1), Greek Brigade (Q2 after 1943-Q1)

*American (14 unit-quarters):*
- 1943-Q1: 1st Armored Division, 1st Infantry Division, 3rd Infantry Division, 9th Infantry Division, 34th Infantry Division (Q1 after 1942-Q4)
- 1943-Q2: II Corps (Q2 after 1942-Q4), 1st Armored Division (Q2 after 1943-Q1), 1st Infantry Division (Q2 after 1943-Q1), 3rd Infantry Division (Q2 after 1943-Q1), 9th Infantry Division (Q2 after 1943-Q1), 34th Infantry Division (Q2 after 1943-Q1), 45th Infantry Division

*French (13 unit-quarters):*
- 1943-Q1: 1re Division Française Libre (Q1 after 1942-Q4), Force L (Q1 after 1942-Q4), 2e Division d'Infanterie Marocaine, Constantine March Division, Algerian March Division, 1st Moroccan March Division
- 1943-Q2: 1re Division Française Libre (Q2 after 1943-Q1), Force L (Q2 after 1943-Q1), 2e Division d'Infanterie Marocaine (Q2 after 1943-Q1), Constantine March Division (Q2 after 1943-Q1), Algerian March Division (Q2 after 1943-Q1), 1st Moroccan March Division (Q2 after 1943-Q1)

---

## Parallelization Matrix

### Optimal Parallel Batches by Year

| Year | Total Unit-Quarters | Nations | Parallel Capacity | Sequential Phases |
|------|---------------------|---------|-------------------|-------------------|
| 1940 | 42 | 1 (Italian only) | Low (1 nation) | 3 phases (Army→Corps→Division) |
| 1941 | 40 | 3 (Italian, British, French) | Medium (3 nations) | 3-4 phases per nation |
| 1942 | 119 | 5 (All nations) | **HIGH (5 nations)** | 3 phases per nation (Army→Corps→Division) |
| 1943 | 106 | 5 (All nations) | **HIGH (5 nations)** | 3 phases per nation (Army→Corps→Division) |

**Maximum parallelization:** 1942-1943 can have 5 simultaneous extraction agents (one per nation).

---

## Critical Rules Summary

### MUST DO (Blocking Dependencies)

1. **Extract parent BEFORE child** (same nation, same quarter)
   - Example: Cannot extract "XXI Corps 1942-Q1" until "10th Army 1942-Q1" complete
   - Example: Cannot extract "7th Armoured Division 1942-Q2" until "XXX Corps 1942-Q2" complete

2. **Extract temporal sequences in order** (same unit, different quarters)
   - Example: Must extract "Trieste Division 1941-Q1" before "Trieste Division 1941-Q3"
   - Reason: Later quarters reference "changes since last quarter"

3. **Extract armies → corps → divisions within same quarter**
   - Strict hierarchy enforcement

### CAN DO (Non-Blocking)

1. **Parallel extraction across nations** (same year, same quarter)
   - German units don't depend on British units
   - Italian units don't depend on American units
   - Example: Can extract "15. Panzer-Division 1942-Q2" and "7th Armoured Division 1942-Q2" simultaneously

2. **Parallel extraction within same hierarchy level** (same quarter, after parent extracted)
   - Once "XXI Corps 1942-Q1" complete, can extract ALL Italian divisions subordinate to XXI Corps in parallel
   - Once "8th Army 1942-Q2" complete, can extract "XIII Corps" and "XXX Corps" in parallel

3. **Equipment sharing documentation** (informational only)
   - Document that Ariete & Trieste shared XX Mobile Corps artillery
   - Do NOT wait for equipment reconciliation to complete extraction

---

## Implementation Recommendations

### For Autonomous Extraction

**Option 1: Year-by-Year with Parallel Nations (Recommended)**

```bash
# Phase 1: 1940 (Italian only)
npm run extract:year:1940

# Phase 2: 1941 (Italian, British, French parallel)
npm run extract:year:1941 --parallel-nations=italian,british,french

# Phase 3: 1942 (All 5 nations parallel)
npm run extract:year:1942 --parallel-nations=german,italian,british,american,french

# Phase 4: 1943 (All 5 nations parallel)
npm run extract:year:1943 --parallel-nations=german,italian,british,american,french
```

**Option 2: Nation-by-Nation Sequential**

```bash
# Extract each nation independently, all years
npm run extract:nation:italian --chronological
npm run extract:nation:german --chronological
npm run extract:nation:british --chronological
npm run extract:nation:american --chronological
npm run extract:nation:french --chronological
```

**Option 3: Hybrid (Best for Large Batches)**

```bash
# 1940: Italian only (42 units)
npm run extract:batch --year=1940 --nation=italian

# 1941: 3 parallel agents
npm run extract:batch --year=1941 --nation=italian &
npm run extract:batch --year=1941 --nation=british &
npm run extract:batch --year=1941 --nation=french &
wait

# 1942: 5 parallel agents (maximize throughput)
npm run extract:batch --year=1942 --nation=german &
npm run extract:batch --year=1942 --nation=italian &
npm run extract:batch --year=1942 --nation=british &
npm run extract:batch --year=1942 --nation=american &
npm run extract:batch --year=1942 --nation=french &
wait

# 1943: 5 parallel agents
npm run extract:batch --year=1943 --nation=german &
npm run extract:batch --year=1943 --nation=italian &
npm run extract:batch --year=1943 --nation=british &
npm run extract:batch --year=1943 --nation=american &
npm run extract:batch --year=1943 --nation=french &
wait
```

### Skip-Completed Logic

**Critical:** All extraction scripts MUST check WORKFLOW_STATE.json and skip already-completed units.

```javascript
function shouldExtractUnit(nation, quarter, designation) {
  const workflow = require('./WORKFLOW_STATE.json');
  const canonicalId = `${nation}_${quarter.toLowerCase().replace('-', '')}_${designation.toLowerCase().replace(/[^a-z0-9]+/g, '_')}`;

  return !workflow.completed.includes(canonicalId);
}
```

---

## Risk Mitigation

### Risk 1: Breaking Temporal Sequences

**Problem:** Extracting "4th Indian Division 1942-Q4" before "4th Indian Division 1940-Q2" loses historical context.

**Mitigation:** Use **Chronological-First** strategy. Always extract Q1→Q2→Q3→Q4 for same unit.

### Risk 2: Missing Hierarchical Dependencies

**Problem:** Extracting "XXI Corps" before parent "10th Army" causes validation failures.

**Mitigation:**
- Phase extraction within each year: Armies first, then Corps, then Divisions
- Enforce dependency checks in extraction scripts

### Risk 3: Equipment Reconciliation Delays

**Problem:** Waiting for equipment database matching (Phase 5) before extracting units.

**Mitigation:**
- Extract units with COUNTS ONLY (from historical sources)
- Phase 5 equipment matching runs in parallel
- Phase 6 post-processing adds specifications after both complete

### Risk 4: Duplicate Extraction

**Problem:** Multiple agents extracting same unit simultaneously.

**Mitigation:**
- Check WORKFLOW_STATE.json before starting each unit
- Lock mechanism: Write "in_progress" status to prevent collisions
- Atomic file writes to canonical locations

---

## Success Metrics

### Progress Tracking

**By Year:**
- 1940: 0/42 complete (100% remaining)
- 1941: 73/113 complete (35% remaining) - NOTE: Many 1941 units already done!
- 1942: 0/119 complete (100% remaining)
- 1943: 0/106 complete (100% remaining)

**By Nation (Remaining):**
- German: 34/69 remaining (49% to go)
- Italian: 130/186 remaining (70% to go)
- British: 108/188 remaining (57% to go)
- American: 17/17 remaining (100% to go)
- French: 18/18 remaining (100% to go)

**Target Completion:**
- Phase 1 (1940): 42 unit-quarters → 1-2 days
- Phase 2 (1941): 40 unit-quarters → 1-2 days
- Phase 3 (1942): 119 unit-quarters → 3-5 days (parallelized)
- Phase 4 (1943): 106 unit-quarters → 3-5 days (parallelized)

**Total estimate:** 8-14 days if fully automated with parallel agents.

---

## Next Steps

1. **Review this plan** with human oversight
2. **Choose strategy:** Chronological-First (recommended) vs Hierarchical-First
3. **Implement extraction scripts** with:
   - Skip-completed logic
   - Dependency enforcement
   - Parallel nation support
4. **Start with 1940** (smallest batch, 42 units, 1 nation)
5. **Validate 1940 output** before proceeding to 1941
6. **Scale to 1942-1943** with full parallelization

---

## Appendix: Complete Dependency Graph

See `dependency_analysis.json` for machine-readable format with:
- All 35 hierarchical parent-child pairs
- All 82 temporal sequences
- Parallel grouping opportunities

**Key Dependencies:**

| Type | Count | Description |
|------|-------|-------------|
| Hierarchical | 35 | Parent→Child relationships requiring sequential extraction |
| Temporal | 82 | Same unit across multiple quarters (Q1→Q2→Q3→Q4) |
| Equipment | N/A | Non-blocking (informational only) |
| Cross-Nation | 0 | No dependencies between nations |

---

**Document Status:** COMPLETE
**Approved for Implementation:** Pending Review
**Generated:** 2025-10-20 by Claude Code Dependency Analysis Engine
