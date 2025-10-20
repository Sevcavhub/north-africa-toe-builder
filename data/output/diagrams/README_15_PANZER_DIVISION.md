# 15. Panzer-Division Diagram - README

**Date**: 2025-10-20
**Division**: 15. Panzer-Division (1941-Q2)
**Commander**: Oberst Maximilian von Herff
**Total Tanks**: 140

## Files Created

### Diagrams
1. **`15_panzer_division_1941q2_v2.svg`** - Improved diagram (Hermann Göring style)
   - Clean left-right layout (org boxes → equipment rows)
   - Simplified organizational boxes (name + count only)
   - Commander names below boxes
   - ONE silhouette per vehicle type with count label
   - Company-level detail (all 8 companies shown)
   - Uses similar variants as placeholders where needed
   - File size: 1600×1350px

### Documentation
2. **`15_PANZER_DIVISION_SILHOUETTES_NEEDED.md`** - Equipment cross-reference
   - What variants the division actually had
   - Which silhouettes you have ✅
   - Which ones you're missing ❌
   - Recommendations for placeholder usage

## Viewing the Diagram

Open in any SVG-compatible viewer or browser:
```
data/output/diagrams/15_panzer_division_1941q2_v2.svg
```

## Silhouette Status

**Available ✅ (4/12 variants)**:
- Panzer III Ausf G (50 tanks) → `panzer_iii_ausf_g.png`
- SdKfz 231 (8-rad) (10 armored cars) → `sd_kfz_231_8_rad.png`
- SdKfz 250 (30 halftracks) → `sd_kfz_250_3.png`
- SdKfz 251 (85 halftracks) → `sd_kfz_251.png`

**Using as Placeholders ⚠️ (3 variants)**:
- Panzer III Ausf J → standing in for Ausf H (35 tanks)
- Panzer IV Ausf F1 → standing in for Ausf D/E (20 tanks)

**Missing ❌ (5 variants - shown as text)**:
- Panzer I Ausf B (10 light tanks)
- Panzer II Ausf C (20 light tanks)
- Panzerbefehlswagen (5 command tanks)
- SdKfz 222 (12 light armored cars)
- SdKfz 10 (15 halftracks)

## Improvements Over Original Diagram

### What Changed:
1. **Layout**: Wider canvas (1600px), proper left-right flow
2. **Boxes**: Simplified to just unit name + count
3. **Commanders**: Moved below boxes (italic text)
4. **Equipment**: Horizontal rows of silhouettes to the right
5. **Silhouettes**: ONE per type with "50x" count labels
6. **Colors**: Removed all colored backgrounds - black on white only
7. **Legend**: Removed giant legend box, added simple footer notes
8. **Detail**: Shows all 8 companies (I. and II. Abteilung)

### Hermann Göring Style Compliance:
✅ Clean organizational boxes (left column)
✅ Horizontal equipment rows (right side)
✅ Commander names below boxes
✅ ONE silhouette per vehicle type
✅ Simple black/white design
✅ Clear hierarchical connecting lines
✅ Section dividers between overview and detailed breakout

## Database Source

Unit data from: `database/master_database.db`
- **Unit ID**: 5
- **Nation**: german
- **Quarter**: 1941-Q2
- **Organization Level**: division

Query used:
```sql
SELECT ev.equipment_category, ev.variant_name, ev.count
FROM equipment_variants ev
WHERE ev.unit_id = 5
ORDER BY ev.equipment_category, ev.variant_name
```

## Silhouette File Organization

After running `rename_silhouettes.bat`:
- ✅ **Renamed** (11 files): Confirmed vehicles with project naming convention
- 📁 **needs_verification/** (8 files): Variants not yet in database (Marder, StuG, etc.)
- 📁 **out_of_scope/** (1 file): King Tiger II (post-1943)
- 📁 **archive/** (1 file): Duplicate PzIV file

**Silhouette paths in SVG**:
```
../../assets/tank_silhouettes/german/panzer_iii_ausf_g.png
../../assets/tank_silhouettes/german/sd_kfz_231_8_rad.png
etc.
```

## Next Steps

### To Complete This Diagram:
1. **Find/create missing silhouettes**:
   - Priority: Panzer I Ausf B, Panzer II Ausf C
   - Medium: Panzerbefehlswagen, SdKfz 222
   - Lower: SdKfz 10

2. **Verify unverified vehicles** in needs_verification/:
   - Check Tessin Vol 12 for North Africa deployments
   - StuG III, Marder II/III likely used in 1942-1943
   - Move verified files back and rename

3. **Create similar diagrams** for other divisions:
   - Use as template for other German divisions
   - Adjust for different equipment compositions
   - Maintain consistent formatting

## Technical Notes

- **SVG version**: 1.0 encoding UTF-8
- **Canvas**: 1600×1350px
- **Font**: Arial (10px units, 8px details, 14-16px titles)
- **Image dimensions**: 50-55px wide × 25-28px tall
- **Line weight**: 1px connecting lines, 2px section dividers
- **Box stroke**: 2px width

## Credits

- **Diagram format**: Based on Hermann Göring Panzer Division example
- **Data source**: North Africa TO&E project database (Phase 6 - 28.1% complete)
- **Silhouettes**: User-provided tank images (German collection)
- **Created**: 2025-10-20 using Claude Code

---

**For questions about equipment or missing silhouettes, see:**
- `15_PANZER_DIVISION_SILHOUETTES_NEEDED.md` (detailed equipment list)
- `SILHOUETTE_MAPPING.md` (filename mapping and verification status)
