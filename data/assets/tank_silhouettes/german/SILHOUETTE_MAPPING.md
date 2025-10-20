# German Tank Silhouette Mapping

**Date**: 2025-10-20
**Purpose**: Map user-provided German tank silhouettes to project database canonical IDs and rename to project naming convention

## Naming Convention Rules

Project standard for silhouette filenames:
- **Lowercase only**: `panzer_iii_ausf_g.png` (not `PZ III Ausf G.png`)
- **Underscores for spaces**: `sd_kfz_251.png` (not `Sd.Kfz 251.png`)
- **No periods or parentheses**: `sd_kfz_250_3.png` (not `Sd.Kfz. 250(3).png`)
- **Variant designations included**: `panzer_iv_ausf_f1.png` (always include Ausf designation)

## Current Files → Canonical Mapping

### ✅ Main Battle Tanks (In Scope: North Africa 1940-1943 Q2)

| Current Filename | Canonical ID | New Filename | Status |
|------------------|--------------|--------------|--------|
| `PZ II Ausf E.png` | `GER_PANZER_II_AUSF_E` | `panzer_ii_ausf_e.png` | ⚠️ Not in database - need to verify if Ausf E in North Africa |
| `PZ III Ausf G.png` | `GER_PANZER_III_AUSF_G` | `panzer_iii_ausf_g.png` | ✅ In database |
| `PZ III Ausf J.png` | `GER_PANZER_III_AUSF_J` | `panzer_iii_ausf_j.png` | ✅ In database |
| `PZ III Ausf. L.png` | `GER_PANZER_III_AUSF_L` | `panzer_iii_ausf_l.png` | ✅ In database |
| `Pz III ausf N.png` | `GER_PANZER_III_AUSF_N` | `panzer_iii_ausf_n.png` | ⚠️ Not in database - need to verify if Ausf N in North Africa |
| `PZ IV Ausf F1.png` | `GER_PANZER_IV_AUSF_F1` | `panzer_iv_ausf_f1.png` | ✅ In database |
| `PZ IV Ausf F2.png` | `GER_PANZER_IV_AUSF_F2` | `panzer_iv_ausf_f2.png` | ✅ In database |

### ⚠️ Duplicate Files

| Current Filename | Issue | Action |
|------------------|-------|--------|
| `PzIV_Ausf_F1_Master_Icon.png` | Duplicate of `PZ IV Ausf F1.png` | Delete or move to archive |

### ⚠️ Post-War/Late War Vehicles (Out of Scope: North Africa)

| Current Filename | Issue | Action |
|------------------|-------|--------|
| `King Tiger II.png` | Tiger II not deployed to North Africa (1944+) | Move to `out_of_scope/` folder |

### ❌ Wrong Nation

| Current Filename | Issue | Action |
|------------------|-------|--------|
| `Semovente 90-53.png` | **ITALIAN** vehicle in German folder | Move to `../italian/semovente_90_53.png` |

### ✅ Armored Cars & Reconnaissance

| Current Filename | Canonical ID | New Filename | Status |
|------------------|--------------|--------------|--------|
| `Sd.Kfz 223.png` | `GER_SDKFZ_223` | `sd_kfz_223.png` | ✅ In database |
| `Sd.Kfz. 231 (8-Rad).png` | `GER_SDKFZ_231` | `sd_kfz_231_8_rad.png` | ✅ In database |
| `Sd.Kfz. 232 (8-Rad).png` | `GER_SDKFZ_232_8-RAD` | `sd_kfz_232_8_rad.png` | ✅ In database (note: 8-RAD variant) |
| `Sd.Kfz. 233 "Stummel".png` | `GER_SDKFZ_233` | `sd_kfz_233.png` | ⚠️ Not in current database extract |

### ✅ Halftracks & Support Vehicles

| Current Filename | Canonical ID | New Filename | Status |
|------------------|--------------|--------------|--------|
| `Sd.Kfz 251.png` | `GER_SDKFZ_251` | `sd_kfz_251.png` | ✅ In database (base variant) |
| `Sd.Kfz. 250(10).png` | `GER_SDKFZ_250` | `sd_kfz_250_10.png` | ✅ In database (variant 10) |
| `Sd.Kfz. 250(3).png` | `GER_SDKFZ_250` | `sd_kfz_250_3.png` | ✅ In database (variant 3) |
| `Sd.Kfz. 263.png` | `GER_SDKFZ_263` | `sd_kfz_263.png` | ⚠️ Not in current database extract |

### ⚠️ Tank Destroyers & Assault Guns (Need Verification)

| Current Filename | Expected Canonical ID | New Filename | Status |
|------------------|----------------------|--------------|--------|
| `Sd Kfz 132 Marder II.png` | `GER_MARDER_II` or `GER_SDKFZ_132` | `marder_ii.png` | ⚠️ Not found in database - may be post-North Africa |
| `Sd Kfz 139 Marder III.png` | `GER_MARDER_III` or `GER_SDKFZ_139` | `marder_iii.png` | ⚠️ Not found in database - may be post-North Africa |
| `Stuf III Ausf C.png` | `GER_STUG_III_AUSF_C` | `stug_iii_ausf_c.png` | ⚠️ Not found in database - need to verify North Africa deployment |
| `Stug III Ausf F Template.png` | `GER_STUG_III_AUSF_F` | `stug_iii_ausf_f.png` | ⚠️ Not found in database - need to verify North Africa deployment |

## Database Reality Check

**Project Status** (from PROJECT_SCOPE.md):
- Phase 6 (Ground Forces): 118/420 unit-quarters (28.1% complete)
- German units in database: 12 units
- Total German scope: ~105 unit-quarters (1940 Q2 - 1943 Q2)

**This means**: Many North Africa vehicles aren't in the database yet because units haven't been extracted!

## Summary Statistics

- **Total files**: 23
- **✅ In database now**: 11 (can rename immediately)
- **⏳ Not in database yet**: 8 (likely in scope, pending unit extraction)
- **❌ Wrong location**: 1 (Italian vehicle in German folder)
- **🗑️ Duplicates**: 1
- **❌ Out of scope**: 1 (King Tiger - definitely post-1943)

## Action Items

### Immediate Actions (High Priority)

1. **Move Italian vehicle**:
   ```bash
   mv "Semovente 90-53.png" "../../italian/semovente_90_53.png"
   ```

2. **Move out-of-scope vehicle**:
   ```bash
   mkdir -p out_of_scope
   mv "King Tiger II.png" "out_of_scope/"
   ```

3. **Handle duplicate**:
   ```bash
   mkdir -p archive
   mv "PzIV_Ausf_F1_Master_Icon.png" "archive/"
   ```

### Verification Needed (Before Renaming)

Need to check if these variants were actually deployed to North Africa (1940 Q2 - 1943 Q2):
- Panzer II Ausf E
- Panzer III Ausf N
- Marder II (Sd.Kfz 132)
- Marder III (Sd.Kfz 139)
- StuG III Ausf C
- StuG III Ausf F
- Sd.Kfz 233
- Sd.Kfz 263

**Sources to check**:
- Tessin Wehrmacht Encyclopedia (German primary source)
- North Africa campaign equipment lists (1940-1943)
- Project equipment database Phase 5 matching results

### Automated Rename Script

Once verified, create `rename_silhouettes.sh` to batch rename all confirmed files to project convention.

## Notes

- **Project scope**: North Africa Campaign 1940 Q2 - 1943 Q2
- **Late-war vehicles** (Tiger II, late StuG variants, late Marder variants) likely not in scope
- **Database source**: `data/iterations/iteration_2/Timeline_TOE_Reconstruction/OUTPUT/v5_development/canonical_equipment_master_with_witw_ALL_NATIONS.json`
- **Naming convention source**: `scripts/lib/naming_standard.js` and project CLAUDE.md

## Cross-References

- Equipment database: Phase 5 matching (20/469 items matched as of Oct 18, 2025)
- Silhouette usage: MDBook diagrams (Hermann Göring style layouts)
- WITW scenario exports: Canonical IDs required for game import
