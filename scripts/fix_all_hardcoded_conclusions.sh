#!/bin/bash

# Regenerate all chapters with hardcoded conclusion bug

echo "Regenerating 23 chapters with corrected conclusions..."
echo ""

# American units (1)
node scripts/generate_single_chapter.js american 1943q1 1st_infantry_division

# British units (16)
node scripts/generate_single_chapter.js british 1941q3 polish_carpathian_brigade_karpacka_brygada_strzelc_w
node scripts/generate_single_chapter.js british 1941q4 2nd_south_african_division
node scripts/generate_single_chapter.js british 1941q4 czechoslovakian_11th_infantry_battalion
node scripts/generate_single_chapter.js british 1941q4 polish_carpathian_brigade_karpacka_brygada_strzelc_w
node scripts/generate_single_chapter.js british 1942q3 1st_greek_brigade
node scripts/generate_single_chapter.js british 1942q4 1st_parachute_brigade
node scripts/generate_single_chapter.js british 1942q4 1st_south_african_division
node scripts/generate_single_chapter.js british 1942q4 4th_indian_division
node scripts/generate_single_chapter.js british 1942q4 4th_infantry_division
node scripts/generate_single_chapter.js british 1942q4 6th_armoured_division
node scripts/generate_single_chapter.js british 1942q4 78th_infantry_division_battleaxe
node scripts/generate_single_chapter.js british 1943q1 2nd_new_zealand_division
node scripts/generate_single_chapter.js british 1943q1 50th_infantry_division
node scripts/generate_single_chapter.js british 1943q1 51st_highland_infantry_division
node scripts/generate_single_chapter.js british 1943q1 6_armoured_division

# French units (1)
node scripts/generate_single_chapter.js french 1942q3 1st_free_french_brigade

# German units (3)
node scripts/generate_single_chapter.js german 1943q1 10_panzer_division
node scripts/generate_single_chapter.js german 1943q1 21_panzer_division
node scripts/generate_single_chapter.js german 1943q1 334_infantry_division

# Italian units (3)
node scripts/generate_single_chapter.js italian 1941q1 brescia_division
node scripts/generate_single_chapter.js italian 1941q4 littorio_division
node scripts/generate_single_chapter.js italian 1943q1 centauro_division

echo ""
echo "All 23 chapters regenerated successfully!"
