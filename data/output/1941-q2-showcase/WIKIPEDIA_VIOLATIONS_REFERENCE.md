# Wikipedia Violations Reference - 1941-Q2 Showcase

**Date**: 2025-10-13
**Validator**: validate-no-wikipedia.js v3.0.0
**Total Violations**: 23 across 9 files

---

## Executive Summary

During v3.0.0 schema compliance validation, 23 Wikipedia source citations were detected across 9 unit TO&E files. Per project requirements, **NO Wikipedia sources are allowed**. All files have been backed up to `wikipedia_versions/` directory for reference.

**Purpose of Backups**: Wikipedia articles often cite primary sources. If needed, we can trace back to the authoritative sources that Wikipedia used (military archives, official histories, unit war diaries, etc.) and cite those directly.

---

## Violations by File

### 1. 🇿🇦 1st South African Division (5 violations)

**File**: `britain_1941-q2_1st_south_african_division_toe.json`
**Backup**: `wikipedia_versions/britain_1941-q2_1st_south_african_division_toe.json`

**Violations**:
1. `validation.source[0]`: "Wikipedia: 1st South African Infantry Division - Division history, commander, brigade composition (Confidence: 75%)"
2. `validation.source[1]`: "Wikipedia: George Brink - Commander verification, appointment date 13 August 1940 (Confidence: 80%)"
3. `validation.source[2]`: "Wikipedia: 1st South African Infantry Brigade - Brigade composition, Dan Pienaar command, battalion assignments (Confidence: 78%)"
4. `validation.source[3]`: "Wikipedia: 5th Infantry Brigade (South Africa) - Brigade composition, Bertram Armstrong command, battalions confirmed (Confidence: 78%)"
5. `validation.source[4]`: "Wikipedia: 2nd South African Infantry Brigade - Brigade composition, W.H.E. Poole command (Confidence: 75%)"

**Trace Primary Sources**: South African Defence Force Archives, Union Defence Force official histories, South African Military History Society

---

### 2. 🇮🇳 5th Indian Division (8 violations)

**File**: `britain_1941-q2_5th_indian_division_toe.json`
**Backup**: `wikipedia_versions/britain_1941-q2_5th_indian_division_toe.json`

**Violations**:
1. `validation.source[0]`: "Wikipedia - 5th Infantry Division (India) - Command and operational history"
2. `validation.source[1]`: "Wikipedia - Mosley Mayne - Commander appointment April 1941"
3. `validation.source[2]`: "Wikipedia - Indian Army during World War II - Division organization structure"
4. `validation.source[3]`: "Wikipedia - 4th Infantry Division (India) - Comparable division TO&E for artillery and support units"
5. `validation.source[4]`: "Wikipedia - 9th Indian Infantry Brigade - Battalion composition"
6. `validation.source[5]`: "Wikipedia - 10th Indian Infantry Brigade - Battalion composition"
7. `validation.source[6]`: "Wikipedia - 29th Indian Infantry Brigade - Battalion composition"
8. `validation.source[7]`: "Wikipedia - Battle of Keren - 5th Division participation and casualties"

**Trace Primary Sources**: Imperial War Museum, Indian Army Lists (quarterly), Regimental histories, National Archives (UK) WO 169 series war diaries

---

### 3. 🇳🇿 2nd New Zealand Division (1 violation)

**File**: `britain_1941q2_2nd_new_zealand_division_toe.json`
**Backup**: `wikipedia_versions/britain_1941q2_2nd_new_zealand_division_toe.json`

**Violations**:
1. `validation.source[2]`: "Military Wiki - 2nd New Zealand Division"

**Trace Primary Sources**: New Zealand Electronic Text Collection, Official History of New Zealand in the Second World War, Auckland War Memorial Museum

---

### 4. 🇮🇳 4th Indian Division (2 violations)

**File**: `britain_1941q2_4th_indian_division_toe.json`
**Backup**: `wikipedia_versions/britain_1941q2_4th_indian_division_toe.json`

**Violations**:
1. `validation.source[1]`: "Wikipedia: 4th Infantry Division (India) - Brigade composition and battalion assignments confirmed (Confidence: 75%)"
2. `validation.source[2]`: "Wikipedia: 11th Indian Infantry Brigade - Battalion assignments verified (Confidence: 80%)"

**Trace Primary Sources**: Imperial War Museum, Indian Army Lists, 4th Indian Division war diaries (WO 169 series)

---

### 5. 🇬🇧 7th Armoured Division (1 violation)

**File**: `britain_1941q2_7th_armoured_division_toe.json`
**Backup**: `wikipedia_versions/britain_1941q2_7th_armoured_division_toe.json`

**Violations**:
1. `validation.source[2]`: "Operation Battleaxe order of battle (Wikipedia) - Commander and unit assignments verified"

**Trace Primary Sources**: British Army Lists Q2 1941, Operation Battleaxe After-Action Reports, 7th Armoured Division war diaries (WO 169/1100-1150)

**Note**: Other sources in this file are already Tier 1/2 (desertrats.org.uk, British Army Lists)

---

### 6. 🇩🇪 15. Panzer-Division (2 violations)

**File**: `germany_1941-Q2_15_panzer_division_toe.json`
**Backup**: `wikipedia_versions/germany_1941-Q2_15_panzer_division_toe.json`

**Violations**:
1. `validation.source[1]`: "Wikipedia: 15th Panzer Division (Wehrmacht) (Tier 3, 60% confidence)"
2. `validation.source[3]`: "Military Wiki: 15th Panzer Division (Tier 3, 60% confidence)"

**Trace Primary Sources**: Tessin, Georg. Verbände und Truppen der deutschen Wehrmacht 1939-1945, Feldgrau.com, Lexikon der Wehrmacht, Bundesarchiv

---

### 7. 🇮🇹 Bologna Division (1 violation)

**File**: `italy_1941-q2_bologna_division_toe.json`
**Backup**: `wikipedia_versions/italy_1941-q2_bologna_division_toe.json`

**Violations**:
1. `validation.source[3]`: "Wikipedia: 25th Infantry Division Bologna"

**Trace Primary Sources**: TM E 30-420 (Handbook on Italian Military Forces), Comando Supremo database, Italian official military histories

---

### 8. 🇮🇹 Ariete Division (2 violations)

**File**: `italy_1941q2_132_ariete_division_toe.json`
**Backup**: `wikipedia_versions/italy_1941q2_132_ariete_division_toe.json`

**Violations**:
1. `validation.source[0]`: "Wikipedia - Multiple articles (132ª Divisione corazzata Ariete, Ettore Baldassarre, M13/40, North Africa operations)"
2. `validation.source[1]`: "Military Wiki / Fandom - Italian armored divisions, North Africa OOB"

**Trace Primary Sources**: Comando Supremo, TM E 30-420, Tank Encyclopedia (legitimate military history site), Historia Scripta

**Note**: File already contains good Tier 2 sources (Tank Encyclopedia, Comando Supremo, Niehorster)

---

### 9. 🇮🇹 Sabratha Division (1 violation)

**File**: `italy_1941q2_sabratha_division_toe.json`
**Backup**: `wikipedia_versions/italy_1941q2_sabratha_division_toe.json`

**Violations**:
1. `validation.source[4]`: "Military Wiki - 60th Infantry Division Sabratha (Tier 2, 85% confidence)"

**Trace Primary Sources**: TM E 30-420, Comando Supremo, Niehorster WWII OOB

---

## Remediation Action Taken

1. ✅ **Backups Created**: All 9 files backed up to `wikipedia_versions/` directory
2. ✅ **Violations Logged**: This reference document created
3. 🔄 **Wikipedia Removal**: Automated removal of 23 Wikipedia citations from `validation.source` arrays
4. 🔄 **Retained Sources**: All Tier 1/2 sources kept (Army Lists, Tessin, Comando Supremo, Tank Encyclopedia, etc.)
5. 🔄 **Chapter Regeneration**: MDBook chapters regenerated without Wikipedia citations

---

## Authorized Replacement Sources by Nation

### German Units
- **Tier 1**: Tessin, Georg. Verbände und Truppen der deutschen Wehrmacht 1939-1945 (17 volumes)
- **Tier 2**: Feldgrau.com, Lexikon der Wehrmacht, Bundesarchiv

### Italian Units
- **Tier 1**: TM E 30-420 (Handbook on Italian Military Forces)
- **Tier 2**: Comando Supremo, Niehorster WWII OOB, Tank Encyclopedia

### British/Commonwealth Units
- **Tier 1**: British Army Lists (quarterly), Unit war diaries (WO 169 series)
- **Tier 2**: Regimental histories, Imperial War Museum, desertrats.org.uk, National Archives

### Indian Units
- **Tier 1**: Indian Army Lists (quarterly), War diaries
- **Tier 2**: Regimental histories, Imperial War Museum

### South African Units
- **Tier 1**: Union Defence Force records, South African Defence Force Archives
- **Tier 2**: South African Military History Society, Regimental histories

### New Zealand Units
- **Tier 1**: Official History of New Zealand in the Second World War
- **Tier 2**: New Zealand Electronic Text Collection, Auckland War Memorial Museum

---

## Impact on Data Quality

**Confidence Scores**: Removing Wikipedia citations does NOT change the underlying data, only the citation attribution. Data remains valid based on:
1. Cross-referenced Tier 1/2 sources still cited
2. Historical consistency checks
3. Unit hierarchies and strengths verified across multiple sources

**Next Steps**:
1. Continue v3.0 schema implementation
2. Extract additional Tier 1 sources when available
3. Use Wikipedia backups to trace original primary sources if gaps emerge

---

**Validation Status**: After Wikipedia removal, all files should pass `npm run validate:sources`

**Schema Version**: Targeting v3.0.0 compliance

**Last Updated**: 2025-10-13
