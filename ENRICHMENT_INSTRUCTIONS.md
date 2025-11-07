# Gun Data Enrichment Instructions

**Date**: November 6, 2025
**Task**: Fill missing HE range bands, HE classification, and ROF for Canadian and German guns
**Estimated Time**: 1-1.5 hours per nation (2-3 hours total)

---

## Files to Fill

1. **canadian_guns_enrichment.csv** (10 guns)
2. **german_guns_enrichment.csv** (16 guns)

---

## CSV Column Reference

| Column | Description | Example Values | Source in PDF |
|--------|-------------|----------------|---------------|
| **gun_name** | Gun name (pre-filled) | "25 pdr", "88mm FlaK36/37" | N/A |
| **he_0_10** | HE effectiveness 0-10" | 3, 6, 9, 15, D6 | Datacard HE row |
| **he_10_20** | HE effectiveness 10-20" | 3, 6, 9, 15 | Datacard HE row |
| **he_20_30** | HE effectiveness 20-30" | 3, 6, 9, 15 | Datacard HE row |
| **he_30_40** | HE effectiveness 30-40" | 3, 6, 9, 15 | Datacard HE row |
| **he_40_50** | HE effectiveness 40-50" | 3, 6, 9, 15 | Datacard HE row |
| **he_50_70** | HE effectiveness 50-70" | 3, 6, 9 | Datacard HE row |
| **he_shell_classification** | HE shell weight class | v. light, light, medium, heavy, bomb, rocket, Cannon | Datacard header |
| **rof** | Rate of Fire (1-10) | 1, 2, 3, 6, 8, 10 | Datacard stats |

---

## HE Range Band Guidance

**What to look for on datacards**:
- Datacards show HE values in range bands like: `3 / 3 / 3 / 3 / 3 / -`
- Each number corresponds to a range band (0-10", 10-20", 20-30", 30-40", 40-50", 50-70")
- `-` means no HE effect at that range (leave blank in CSV)
- Some weapons have ALL ranges the same (artillery)
- Some weapons drop off (AT guns, tank guns)

**Example from British 25 pdr**:
```
Datacard shows: HE 3 / 3 / 3 / 3 / 3 / -
CSV entry:
  he_0_10 = 3
  he_10_20 = 3
  he_20_30 = 3
  he_30_40 = 3
  he_40_50 = 3
  he_50_70 = (leave blank - no value at this range)
```

**Example from British 17 pdr**:
```
Datacard shows: HE 3 / 3 / 3 / 3 / 3 / 3
CSV entry:
  he_0_10 = 3
  he_10_20 = 3
  he_20_30 = 3
  he_30_40 = 3
  he_40_50 = 3
  he_50_70 = 3
```

---

## HE Shell Classification Guidance

**Classification by caliber/type** (general guide):

| Classification | Typical Caliber | Examples |
|----------------|-----------------|----------|
| **v. light** | 20-50mm | 37mm PAK, 2 pdr, 20mm AA |
| **light** | 57-76mm | 6 pdr, 75mm Sherman, 3" Howitzer |
| **medium** | 87-105mm | 25 pdr, 88mm, 105mm Howitzer |
| **heavy** | 114-155mm+ | 5.5" gun, 4.5" gun, 149mm+ |
| **bomb** | Aircraft bombs | 250lb, 500lb, 1000lb bombs |
| **rocket** | Aircraft rockets | 60lb rocket, RP-3, Nebelwerfer |
| **Cannon** | Aircraft cannon | 20mm aircraft cannon |

**Note**: Check the actual datacard header - it should say the classification explicitly.

---

## ROF (Rate of Fire) Guidance

**ROF Scale**: 1 (slowest) to 10 (fastest)

| ROF | Typical Weapon Type | Examples |
|-----|---------------------|----------|
| **1** | Heavy AT guns, heavy artillery | 17 pdr, 88mm PaK, 5.5" gun |
| **2** | Medium AT guns, field artillery | 6 pdr, 75mm PAK40, 25 pdr |
| **3** | Light AT guns, tank guns | 2 pdr, 37mm PAK, 75mm Sherman |
| **4-5** | Howitzers, mortars | 3" Mortar, 105mm Howitzer |
| **6** | Light AA guns, HMG | 20mm Oerlikon, .50 cal |
| **8-10** | High-ROF AA guns, autocannon | 20mm FlaK 38, quad .50 cal |

**Note**: If ROF not visible on datacard, leave blank (we'll infer later or user can add).

---

## Special Cases

### AT Guns with No HE
Some AT guns have NO HE value at all (AP only):
- **2 pdr** (British/Canadian)
- **6 pdr** (early versions)
- **PIAT**

**What to do**: Leave ALL HE range bands blank (he_0_10 through he_50_70)

### Mortars/Artillery with No AP
Some weapons have HE but NO AP:
- **3" Mortar**
- **2" Mortar**
- **4.5" gun** (artillery)
- **5.5" medium gun**

**What to do**: Fill HE range bands normally (AP already empty in database)

### Rockets/Bombs
Aircraft weapons may have unusual patterns:
- **60lb Rocket**: May have short range, high HE
- **Bombs**: May have uniform HE across all ranges
- **Aircraft cannon**: May have limited range, high ROF

**What to do**: Fill exactly as shown on datacard

### Variable Damage (D6)
If datacard shows "D6" for HE:
- **2" Mortar** may show D6 in some ranges
- **Flamethrowers** show D6

**What to do**: Enter "D6" as TEXT in the CSV cell

---

## Filling Strategy

### Recommended Order

**Canadian (10 guns - easier)**:
1. **Artillery** (4 guns): 25 pdr, 4.5" gun, 5.5" medium gun, 2" Mortar
2. **AT Guns** (3 guns): 2 pounder, 6 pdr, 17 pdr
3. **Infantry** (2 guns): 3" Mortar, PIAT
4. **Special** (1 gun): 60lb Rocket

**German (16 guns - more complex)**:
1. **Field AT Guns** (3 guns): 37mm PAK35/36, 50mm PAK38, 75mm PAK40
2. **88mm Family** (5 guns): FlaK18, FlaK36/37, FlaK41, PaK43, PaK43/41
3. **Infantry** (2 guns): 75mm leIG18, PaK97/38
4. **Vehicle-mounted** (6 guns): All PzKPfw guns (2cm, 3.7cm, 5cm, 7.5cm variants)

---

## Example: Filling Canadian 25 pdr

**Looking at Crucible PDF datacard for 25 pdr**:

1. Find HE range values on card:
   - `HE: 3 / 3 / 3 / 3 / 3 / -`

2. Find HE classification in header:
   - Card header shows: "medium"

3. Find ROF (if visible):
   - Stats section shows: ROF 2

4. Fill CSV row:
```csv
25 pdr,3,3,3,3,3,,medium,2
```

**Notes**:
- he_50_70 left blank (datacard shows `-`)
- he_shell_classification = "medium"
- rof = 2

---

## Example: Filling German 88mm FlaK36/37

**Looking at Crucible PDF datacard**:

1. Find HE range values:
   - `HE: 6 / 6 / 5 / 4 / 3 / 2`

2. Find HE classification:
   - Card header: "medium" (88mm is medium-heavy)

3. Find ROF:
   - Stats: ROF 3 (heavy gun, slower)

4. Fill CSV row:
```csv
88mm FlaK36/37,6,6,5,4,3,2,medium,3
```

---

## Validation Before Import

**Check your CSV**:
- All gun_name rows filled (should match pre-filled names)
- At least ONE HE range value per gun (unless AT gun with no HE)
- HE classification filled for guns with HE data
- ROF filled where visible (OK to leave blank if not sure)

**Common mistakes**:
- Mixing up range order (0-10" should be FIRST, not last)
- Typos in classification ("lite" vs "light", "med" vs "medium")
- Entering "0" instead of leaving blank for no effect
- Entering AP values in HE columns (we're only doing HE ranges)

---

## After Filling CSVs

**Run the enrichment import**:

```bash
# Canadian
python scripts/battlegroup/manual_extraction/enrich_scraped_guns.py \
    --csv canadian_guns_enrichment.csv \
    --nation canadian

# German
python scripts/battlegroup/manual_extraction/enrich_scraped_guns.py \
    --csv german_guns_enrichment.csv \
    --nation german
```

**Then manual review**:
```bash
# Re-run audit to see improvement
python scripts/battlegroup/manual_extraction/audit_scraped_data.py

# Check specific guns
python scripts/battlegroup/manual_extraction/validate_british_guns_import.py
```

---

## Quick Reference Table

**Canadian Guns Quick Fill Guide** (verify against Crucible PDF):

| Gun | Expected HE Class | Expected ROF | Notes |
|-----|-------------------|--------------|-------|
| 25 pdr | medium | 2 | Field artillery |
| 17 pdr | light | 1 | Heavy AT gun |
| 6 pdr | v. light | 2-3 | Medium AT gun |
| 2 pounder | - | 3 | AT gun, NO HE |
| 3" Mortar | light | 4-5 | Infantry mortar, NO AP |
| 2" Mortar | v. light | 6 | Light mortar |
| 4.5" gun | heavy | 1 | Heavy artillery, NO AP |
| 5.5" medium gun | heavy | 1 | Heavy artillery, NO AP |
| PIAT | - | - | Infantry AT, may have limited HE |
| 60lb Rocket | rocket | - | Aircraft rocket |

**German Guns Quick Fill Guide** (verify against Crucible PDF):

| Gun | Expected HE Class | Expected ROF | Notes |
|-----|-------------------|--------------|-------|
| 37mm PAK35/36 | v. light | 3 | Light AT gun |
| 50mm PAK38 | v. light | 2-3 | Medium AT gun |
| 75mm PAK40 | light | 2 | Heavy AT gun |
| 75mm leIG18 | light | 2-3 | Infantry gun, NO AP |
| 88mm FlaK18 | medium | 3 | Dual-purpose AA/AT |
| 88mm FlaK36/37 | medium | 3 | Dual-purpose AA/AT |
| 88mm FlaK41 | medium | 3-4 | Improved FlaK |
| 88mm PaK43 | medium | 1-2 | Heavy AT gun |
| 88mm PaK43/41 | medium | 1-2 | Heavy AT gun |
| PaK97/38 | light | 2 | Captured French gun |
| PzKPfw 38(sf) 2cm | Cannon | 8-10 | Light autocannon |
| PzKPfw 38(sf) 3.7cm | v. light | 3-4 | Light AT gun |
| PzKPfw II 2cm | Cannon | 8-10 | Light autocannon |
| PzKPfw II 3.7cm | v. light | 3-4 | Light AT gun |
| PzKPfw IV 5cm | v. light | 2-3 | Medium tank gun |
| PzKPfw IV 7.5cm | light | 2 | Heavy tank gun |

---

**Ready to start!** Open the CSVs in Excel/spreadsheet, reference the Crucible PDF, and fill in the missing values.

**Estimated time**:
- Canadian: 45-60 minutes (10 guns)
- German: 60-90 minutes (16 guns)
- Total: 2-3 hours
