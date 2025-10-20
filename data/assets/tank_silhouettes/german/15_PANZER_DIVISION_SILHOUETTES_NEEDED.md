# 15. Panzer-Division (1941-Q2) - Silhouette Requirements

**Division**: 15. Panzer-Division
**Quarter**: 1941-Q2
**Commander**: Oberst Maximilian von Herff
**Total Tanks**: 140
**Database Unit ID**: 5

## Tank & AFV Variants Needed for Diagram

### Tanks (140 total)

| Variant | Count | User Has? | Status |
|---------|-------|-----------|--------|
| **Panzer I Ausf B** | 10 | ❌ No | **MISSING** - Need silhouette |
| **Panzer II Ausf C** | 20 | ⚠️ Has Ausf E instead | **MISSING** - Wrong variant |
| **Panzerbefehlswagen** | 5 | ❌ No | **MISSING** - Command tank silhouette needed |
| **Panzer III Ausf G** | 50 | ✅ YES | **HAVE** - `PZ III Ausf G.png` |
| **Panzer III Ausf H** | 35 | ⚠️ Has J, L, N instead | **MISSING** - Wrong variants |
| **Panzer IV Ausf D** | 15 | ⚠️ Has F1, F2 instead | **MISSING** - Wrong variants |
| **Panzer IV Ausf E** | 5 | ⚠️ Has F1, F2 instead | **MISSING** - Wrong variants |

**Summary**:
- ✅ Have: 1/7 variants (Panzer III Ausf G)
- ❌ Missing: 6/7 variants

### Armored Cars (22 total)

| Variant | Count | User Has? | Status |
|---------|-------|-----------|--------|
| **SdKfz 222** | 12 | ❌ No | **MISSING** - Need silhouette |
| **SdKfz 231 (8-rad)** | 10 | ✅ YES | **HAVE** - `Sd.Kfz. 231 (8-Rad).png` |

**Summary**:
- ✅ Have: 1/2 variants (SdKfz 231)
- ❌ Missing: 1/2 variants (SdKfz 222)

### Halftracks (130 total)

| Variant | Count | User Has? | Status |
|---------|-------|-----------|--------|
| **SdKfz 10** | 15 | ❌ No | **MISSING** - Need silhouette |
| **SdKfz 250** | 30 | ✅ YES | **HAVE** - `Sd.Kfz. 250(3).png`, `Sd.Kfz. 250(10).png` |
| **SdKfz 251** | 85 | ✅ YES | **HAVE** - `Sd.Kfz 251.png` |

**Summary**:
- ✅ Have: 2/3 variants (SdKfz 250, 251)
- ❌ Missing: 1/3 variants (SdKfz 10)

## Overall Silhouette Status for 15. Panzer-Division Diagram

**Total unique AFV types needed**: 12
**User has**: 4 ✅
**User missing**: 8 ❌

### ✅ CAN USE (4 silhouettes):
1. Panzer III Ausf G (50 tanks)
2. SdKfz 231 8-rad (10 armored cars)
3. SdKfz 250 (30 halftracks)
4. SdKfz 251 (85 halftracks)

### ❌ NEED TO CREATE/FIND (8 silhouettes):
1. Panzer I Ausf B (10 light tanks)
2. Panzer II Ausf C (20 light tanks)
3. Panzerbefehlswagen (5 command tanks)
4. Panzer III Ausf H (35 medium tanks)
5. Panzer IV Ausf D (15 medium tanks)
6. Panzer IV Ausf E (5 medium tanks)
7. SdKfz 222 (12 light armored cars)
8. SdKfz 10 (15 light halftracks)

## Recommendation

### Option 1: Create Diagram with What We Have
- Show Panzer III Ausf G, SdKfz 231, 250, 251
- Use placeholder boxes or generic silhouettes for missing variants
- Label clearly which are actual silhouettes vs. placeholders

### Option 2: Find/Create Missing Silhouettes First
- Priority: Panzer II Ausf C, Panzer IV Ausf D (major types)
- Then: Panzer I Ausf B, Panzerbefehlswagen, SdKfz 222
- Lower priority: Variant differences (Ausf H vs G are visually similar)

### Option 3: Use User's Similar Variants as Placeholders
- Use Panzer III Ausf J/L as placeholder for Ausf H (similar appearance)
- Use Panzer IV Ausf F1 as placeholder for Ausf D/E (close enough visually)
- Label diagram "(F1 silhouette shown for D/E variants)"

## Diagram Structure (Hermann Göring Style)

```
15. Panzer-Division (1941-Q2)
├── Division HQ (Commander + staff vehicles)
├── Panzer-Regiment 8
│   ├── Regimental HQ
│   ├── I. Abteilung (Battalion)
│   │   ├── Abteilung HQ (3x Panzerbefehlswagen)
│   │   ├── 1. Kompanie (17x Panzer III)
│   │   ├── 2. Kompanie (17x Panzer III)
│   │   ├── 3. Kompanie (17x Panzer III)
│   │   └── 4. Kompanie (17x Panzer III + 4x Panzer IV)
│   └── II. Abteilung (Battalion)
│       ├── Abteilung HQ (3x Panzerbefehlswagen)
│       ├── 5. Kompanie (17x Panzer III)
│       ├── 6. Kompanie (17x Panzer III)
│       ├── 7. Kompanie (17x Panzer III)
│       └── 8. Kompanie (17x Panzer III + 4x Panzer IV)
├── Reconnaissance Battalion (Aufklärungs-Abteilung 33)
│   ├── Armored Car Company (SdKfz 222, 231)
│   └── Motorcycle Company
└── Panzergrenadier Regiments (motorized infantry)
    └── Halftracks (SdKfz 250, 251)
```

## Next Steps

1. **Choose approach** (full silhouettes, placeholders, or similar variants)
2. **Gather missing silhouettes** if going for accuracy
3. **Create diagram** using Hermann Göring format
4. **Label clearly** which silhouettes are exact vs. placeholders

---

**Conclusion**: User has 33% of needed silhouettes (4/12). Can create diagram with placeholders or find missing variants.
