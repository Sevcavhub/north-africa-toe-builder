# Wikipedia Source Upgrade Work Queue

**Generated:** 2025-10-26
**Total Units:** 97
**Total Batches:** 33 (32 batches of 3, 1 batch of 1)
**Backup Location:** `data/backups/full_backup_2025-10-26T23-33-43/`

---

## Workflow

**Per Batch:**
1. Launch 3 source_upgrader agents in parallel (Task tool)
2. Each agent:
   - Extracts Wikipedia bibliography via puppeteer
   - Checks Tier 1 local sources (Nafziger, Tessin, Army Lists)
   - Falls back to Tier 2 curated web (Feldgrau, Niehorster)
   - Replaces Wikipedia citations with primary sources
   - Preserves ALL unit data (equipment/personnel)
   - Updates confidence score
3. QA validation after batch completes
4. Checkpoint + session:end to commit

**Target:** 70-85 successful upgrades (72-88%)
**Expected:** 10-25 units may need archive research annotation

---

## Batch Queue

### Batch 1 (Units 1-3)
- [ ] `british_1943q1_v_corps_toe.json` (Nation: british, Quarter: 1943q1, Tier: 2, Conf: 78%)
- [ ] `british_1943q2_v_corps_toe.json` (Nation: british, Quarter: 1943q2, Tier: 2, Conf: 82%)
- [ ] `british_1943q1_x_corps_toe.json` (Nation: british, Quarter: 1943q1, Tier: 2, Conf: 85%)

### Batch 2 (Units 4-6)
- [ ] `french_1943q2_1st_moroccan_march_division_toe.json` (Nation: french, Quarter: 1943q2, Tier: 2, Conf: 62%)
- [ ] `british_1943q2_1st_armoured_division_toe.json` (Nation: british, Quarter: 1943q2, Tier: 2, Conf: 85%)
- [ ] `british_1943q2_10th_armoured_division_toe.json` (Nation: british, Quarter: 1943q2, Tier: 4, Conf: 35%)

### Batch 3 (Units 7-9)
- [ ] `italian_1943q1_trento_division_toe.json` (Nation: italian, Quarter: 1943q1, Tier: 4, Conf: 45%)
- [ ] `british_1943q2_2nd_new_zealand_division_toe.json` (Nation: british, Quarter: 1943q2, Tier: 2, Conf: 0%)
- [ ] `american_1943q2_2nd_armored_division_toe.json` (Nation: american, Quarter: 1943q2, Tier: 2, Conf: 78%)

### Batch 4 (Units 10-12)
- [ ] `italian_1943q2_la_spezia_division_toe.json` (Nation: italian, Quarter: 1943q2, Tier: 2, Conf: 65%)
- [ ] `french_1943q2_1re_division_fran_aise_libre_toe.json` (Nation: french, Quarter: 1943q2, Tier: unknown, Conf: 82%)
- [ ] `british_1943q2_4th_infantry_division_toe.json` (Nation: british, Quarter: 1943q2, Tier: 2, Conf: 80%)

### Batch 5 (Units 13-15)
- [ ] `british_1943q2_50th_infantry_division_toe.json` (Nation: british, Quarter: 1943q2, Tier: 2, Conf: 0%)
- [ ] `british_1943q2_46th_infantry_division_toe.json` (Nation: british, Quarter: 1943q2, Tier: 2, Conf: 76%)
- [ ] `american_1943q2_1st_infantry_division_toe.json` (Nation: american, Quarter: 1943q2, Tier: 2, Conf: 78%)

### Batch 6 (Units 16-18)
- [ ] `american_1943q2_34th_infantry_division_toe.json` (Nation: american, Quarter: 1943q2, Tier: 2, Conf: 82%)
- [ ] `american_1943q2_1st_armored_division_toe.json` (Nation: american, Quarter: 1943q2, Tier: 1, Conf: 82%)
- [ ] `british_1943q1_1st_armoured_division_toe.json` (Nation: british, Quarter: 1943q1, Tier: 2, Conf: 72%)

### Batch 7 (Units 19-21)
- [ ] `american_1943q1_2nd_armored_division_toe.json` (Nation: american, Quarter: 1943q1, Tier: 1, Conf: 75%)
- [ ] `italian_1943q1_giovani_fascisti_division_toe.json` (Nation: italian, Quarter: 1943q1, Tier: 1, Conf: 75%)
- [ ] `american_1942q4_2nd_armored_division_toe.json` (Nation: american, Quarter: 1942q4, Tier: unknown, Conf: 72%)

### Batch 8 (Units 22-24)
- [ ] `italian_1942q3_pavia_division_toe.json` (Nation: italian, Quarter: 1942q3, Tier: 2, Conf: 65%)
- [ ] `french_1942q3_1re_division_fran_aise_libre_toe.json` (Nation: french, Quarter: 1942q3, Tier: 2, Conf: 70%)
- [ ] `british_1942q3_1st_armoured_division_toe.json` (Nation: british, Quarter: 1942q3, Tier: 2, Conf: 75%)

### Batch 9 (Units 25-27)
- [ ] `italian_1942q2_101st_trieste_division_toe.json` (Nation: italian, Quarter: 1942q2, Tier: 2, Conf: 75%)
- [ ] `italian_1942q2_brescia_division_toe.json` (Nation: italian, Quarter: 1942q2, Tier: 2, Conf: 75%)
- [ ] `italian_1942q2_pavia_division_toe.json` (Nation: italian, Quarter: 1942q2, Tier: 2, Conf: 70%)

### Batch 10 (Units 28-30)
- [ ] `british_1942q2_50th_infantry_division_toe.json` (Nation: british, Quarter: 1942q2, Tier: 2, Conf: 78%)
- [ ] `british_1942q2_2nd_south_african_division_toe.json` (Nation: british, Quarter: 1942q2, Tier: 1, Conf: 85%)
- [ ] `british_1942q2_4th_indian_division_toe.json` (Nation: british, Quarter: 1942q2, Tier: 3, Conf: 65%)

### Batch 11 (Units 31-33)
- [ ] `british_1942q2_2nd_new_zealand_division_toe.json` (Nation: british, Quarter: 1942q2, Tier: unknown, Conf: 78%)
- [ ] `british_1942q2_1st_south_african_division_toe.json` (Nation: british, Quarter: 1942q2, Tier: unknown, Conf: 82%)
- [ ] `british_1942q1_50th_infantry_division_toe.json` (Nation: british, Quarter: 1942q1, Tier: unknown, Conf: 78%)

### Batch 12 (Units 34-36)
- [ ] `british_1942q1_1st_south_african_division_toe.json` (Nation: british, Quarter: 1942q1, Tier: unknown, Conf: 78%)
- [ ] `italian_1941q3_trento_division_toe.json` (Nation: italian, Quarter: 1941q3, Tier: 2, Conf: 82%)
- [ ] `british_1941q3_4th_indian_division_toe.json` (Nation: british, Quarter: 1941q3, Tier: unknown, Conf: 72%)

### Batch 13 (Units 37-39)
- [ ] `british_1941q3_1st_south_african_division_toe.json` (Nation: british, Quarter: 1941q3, Tier: 2, Conf: 74%)
- [ ] `italian_1941q1_2nd_ccnn_division_28_ottobre_toe.json` (Nation: italian, Quarter: 1941q1, Tier: 1, Conf: 88%)
- [ ] `french_1943q2_force_l_toe.json` (Nation: french, Quarter: 1943q2, Tier: Tier 2, Conf: 75%)

### Batch 14 (Units 40-42)
- [ ] `italian_1941q1_1st_ccnn_division_23_marzo_toe.json` (Nation: italian, Quarter: 1941q1, Tier: 1, Conf: 85%)
- [ ] `italian_1940q4_pavia_division_toe.json` (Nation: italian, Quarter: 1940q4, Tier: unknown, Conf: 88%)
- [ ] `italian_1940q4_4th_ccnn_division_3_gennaio_toe.json` (Nation: italian, Quarter: 1940q4, Tier: 2, Conf: 70%)

### Batch 15 (Units 43-45)
- [ ] `italian_1940q4_brescia_division_toe.json` (Nation: italian, Quarter: 1940q4, Tier: 1, Conf: 83%)
- [ ] `italian_1940q4_1st_ccnn_division_23_marzo_toe.json` (Nation: italian, Quarter: 1940q4, Tier: 2, Conf: 70%)
- [ ] `italian_1940q3_4th_ccnn_division_3_gennaio_toe.json` (Nation: italian, Quarter: 1940q3, Tier: 2, Conf: 65%)

### Batch 16 (Units 46-48)
- [ ] `italian_1940q4_catanzaro_division_toe.json` (Nation: italian, Quarter: 1940q4, Tier: 1, Conf: 80%)
- [ ] `italian_1940q3_pavia_division_toe.json` (Nation: italian, Quarter: 1940q3, Tier: unknown, Conf: 85%)
- [ ] `british_1940q4_1st_south_african_division_toe.json` (Nation: british, Quarter: 1940q4, Tier: 2, Conf: 68%)

### Batch 17 (Units 49-51)
- [ ] `british_1943q2_1st_greek_brigade_toe.json` (Nation: british, Quarter: 1943q2, Tier: 2, Conf: 70%)
- [ ] `french_1942q1_1re_brigade_fran_aise_libre_toe.json` (Nation: french, Quarter: 1942q1, Tier: 2, Conf: 68%)
- [ ] `french_1943q1_force_l_toe.json` (Nation: french, Quarter: 1943q1, Tier: Tier 2, Conf: 72%)

### Batch 18 (Units 52-54)
- [ ] `italian_1941q1_brescia_division_toe.json` (Nation: italian, Quarter: 1941q1, Tier: unknown, Conf: 78%)
- [ ] `italian_1940q3_catanzaro_division_toe.json` (Nation: italian, Quarter: 1940q3, Tier: 1, Conf: 77%)
- [ ] `italian_1943q1_centauro_division_toe.json` (Nation: italian, Quarter: 1943q1, Tier: unknown, Conf: 78%)

### Batch 19 (Units 55-57)
- [ ] `italian_1942q4_ariete_division_toe.json` (Nation: italian, Quarter: 1942q4, Tier: unknown, Conf: 88%)
- [ ] `italian_1942q3_ariete_division_toe.json` (Nation: italian, Quarter: 1942q3, Tier: unknown, Conf: 78%)
- [ ] `italian_1942q1_xxi_corpo_d_armata_xxi_corps_toe.json` (Nation: italian, Quarter: 1942q1, Tier: 2, Conf: 76%)

### Batch 20 (Units 58-60)
- [ ] `italian_1942q1_brescia_division_toe.json` (Nation: italian, Quarter: 1942q1, Tier: unknown, Conf: 78%)
- [ ] `italian_1941q4_littorio_division_toe.json` (Nation: italian, Quarter: 1941q4, Tier: unknown, Conf: 65%)
- [ ] `italian_1941q4_ariete_division_toe.json` (Nation: italian, Quarter: 1941q4, Tier: unknown, Conf: 92%)

### Batch 21 (Units 61-63)
- [ ] `italian_1941q2_brescia_division_toe.json` (Nation: italian, Quarter: 1941q2, Tier: 1, Conf: 82%)
- [ ] `italian_1941q1_sirte_division_toe.json` (Nation: italian, Quarter: 1941q1, Tier: unknown, Conf: 75%)
- [ ] `italian_1941q1_savona_division_toe.json` (Nation: italian, Quarter: 1941q1, Tier: unknown, Conf: 82%)

### Batch 22 (Units 64-66)
- [ ] `italian_1940q4_xxii_corpo_d_armata_xxii_corps_toe.json` (Nation: italian, Quarter: 1940q4, Tier: 4, Conf: 48%)
- [ ] `italian_1940q4_xxi_corpo_d_armata_xxi_corps_toe.json` (Nation: italian, Quarter: 1940q4, Tier: 4, Conf: 50%)
- [ ] `italian_1940q4_10_armata_italian_10th_army_toe.json` (Nation: italian, Quarter: 1940q4, Tier: 2, Conf: 72%)

### Batch 23 (Units 67-69)
- [ ] `german_1943q1_21_panzer_division_toe.json` (Nation: german, Quarter: 1943q1, Tier: 2, Conf: 0%)
- [ ] `german_1942q4_21_panzer_division_toe.json` (Nation: german, Quarter: 1942q4, Tier: unknown, Conf: 85%)
- [ ] `german_1942q3_panzerarmee_afrika_toe.json` (Nation: german, Quarter: 1942q3, Tier: unknown, Conf: 78%)

### Batch 24 (Units 70-72)
- [ ] `french_1943q1_1re_division_fran_aise_libre_toe.json` (Nation: french, Quarter: 1943q1, Tier: unknown, Conf: 78%)
- [ ] `french_1942q2_1re_brigade_fran_aise_libre_toe.json` (Nation: french, Quarter: 1942q2, Tier: unknown, Conf: 82%)
- [ ] `british_1943q1_2nd_new_zealand_division_toe.json` (Nation: british, Quarter: 1943q1, Tier: 2, Conf: 0%)

### Batch 25 (Units 73-75)
- [ ] `british_1943q1_50th_infantry_division_toe.json` (Nation: british, Quarter: 1943q1, Tier: 2, Conf: 0%)
- [ ] `british_1942q4_xiii_corps_toe.json` (Nation: british, Quarter: 1942q4, Tier: 1, Conf: 82%)
- [ ] `british_1942q4_78th_infantry_division_battleaxe_toe.json` (Nation: british, Quarter: 1942q4, Tier: 2, Conf: 80%)

### Batch 26 (Units 76-78)
- [ ] `british_1942q4_6th_armoured_division_toe.json` (Nation: british, Quarter: 1942q4, Tier: 2, Conf: 82%)
- [ ] `british_1942q4_4th_indian_division_toe.json` (Nation: british, Quarter: 1942q4, Tier: 2, Conf: 84%)
- [ ] `british_1942q4_4th_infantry_division_toe.json` (Nation: british, Quarter: 1942q4, Tier: 2, Conf: 78%)

### Batch 27 (Units 79-81)
- [ ] `british_1942q2_9th_australian_division_toe.json` (Nation: british, Quarter: 1942q2, Tier: unknown, Conf: 82%)
- [ ] `british_1942q1_xxx_corps_toe.json` (Nation: british, Quarter: 1942q1, Tier: 2, Conf: 80%)
- [ ] `british_1942q1_xiii_corps_toe.json` (Nation: british, Quarter: 1942q1, Tier: 2, Conf: 82%)

### Batch 28 (Units 82-84)
- [ ] `british_1941q4_czechoslovakian_11th_infantry_battalion_toe.json` (Nation: british, Quarter: 1941q4, Tier: unknown, Conf: 78%)
- [ ] `british_1941q4_polish_carpathian_brigade_karpacka_brygada_strzelc_w_toe.json` (Nation: british, Quarter: 1941q4, Tier: 2, Conf: 80%)
- [ ] `british_1941q4_70th_infantry_division_toe.json` (Nation: british, Quarter: 1941q4, Tier: unknown, Conf: 84%)

### Batch 29 (Units 85-87)
- [ ] `british_1941q4_2nd_south_african_division_toe.json` (Nation: british, Quarter: 1941q4, Tier: unknown, Conf: 80%)
- [ ] `british_1941q3_polish_carpathian_brigade_karpacka_brygada_strzelc_w_toe.json` (Nation: british, Quarter: 1941q3, Tier: 2, Conf: 78%)
- [ ] `british_1941q3_eighth_army_8th_army_toe.json` (Nation: british, Quarter: 1941q3, Tier: 1, Conf: 85%)

### Batch 30 (Units 88-90)
- [ ] `british_1941q2_5th_indian_division_toe.json` (Nation: british, Quarter: 1941q2, Tier: 2, Conf: 78%)
- [ ] `british_1941q2_2nd_south_african_division_toe.json` (Nation: british, Quarter: 1941q2, Tier: 2, Conf: 72%)
- [ ] `british_1941q1_xiii_corps_toe.json` (Nation: british, Quarter: 1941q1, Tier: 1, Conf: 87%)

### Batch 31 (Units 91-93)
- [ ] `british_1941q2_1st_south_african_division_toe.json` (Nation: british, Quarter: 1941q2, Tier: 2, Conf: 76%)
- [ ] `british_1941q1_4th_indian_division_toe.json` (Nation: british, Quarter: 1941q1, Tier: unknown, Conf: 82%)
- [ ] `british_1940q4_western_desert_force_toe.json` (Nation: british, Quarter: 1940q4, Tier: unknown, Conf: 85%)

### Batch 32 (Units 94-96)
- [ ] `british_1940q4_7th_armoured_division_toe.json` (Nation: british, Quarter: 1940q4, Tier: unknown, Conf: 82%)
- [ ] `british_1940q3_western_desert_force_toe.json` (Nation: british, Quarter: 1940q3, Tier: unknown, Conf: 78%)
- [ ] `british_1940q2_7th_armoured_division_toe.json` (Nation: british, Quarter: 1940q2, Tier: unknown, Conf: 85%)

### Batch 33 (Unit 97)
- [ ] `british_1940q2_4th_indian_division_toe.json` (Nation: british, Quarter: 1940q2, Tier: unknown, Conf: 78%)

---

## Progress Tracking

**Batches Completed:** 0/33
**Units Upgraded:** 0/97
**Success Rate:** N/A
**Annotations Required:** N/A

**Current Batch:** Batch 1
**Status:** Pending

---

## Success Metrics

**Target Outcomes:**
- 70-85 units (72-88%): Successfully upgraded to Tier 1/2 sources
- 10-25 units (10-26%): Annotated for archive research
- 2-5 units (2-5%): May require manual intervention

**Quality Gates:**
- Confidence >= 75% (preferred)
- Confidence >= 60% (minimum)
- No Wikipedia (unless annotated NEEDS_RESEARCH)
- All equipment/personnel data preserved
- Schema validation passes

---

## Restoration Plan

If upgrade fails for a unit:
1. Restore from backup: `data/backups/full_backup_2025-10-26T23-33-43/units/[filename]`
2. Annotate validation.source_upgrade with failure reason
3. Mark validation.source_upgrade.needs_research = true
4. Move to manual research queue

**Backup verification:** 402 units with MD5 checksums in `BACKUP_MANIFEST.json`
