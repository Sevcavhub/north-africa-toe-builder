#!/usr/bin/env bash
# German Tank Silhouette Rename Script
# Renames user-provided files to project naming convention
# Date: 2025-10-20

# Change to german silhouettes directory
cd "$(dirname "$0")"

echo "German Tank Silhouette Batch Rename"
echo "===================================="
echo ""

# Create directories for organization
mkdir -p out_of_scope
mkdir -p archive
mkdir -p needs_verification

echo "Step 1: Moving out-of-scope and duplicate files..."
echo ""

# Move out-of-scope (post-1943 vehicles)
if [ -f "King Tiger II.png" ]; then
    echo "  ⚠️  Moving King Tiger II.png to out_of_scope/ (not in North Africa 1940-1943)"
    mv "King Tiger II.png" "out_of_scope/"
fi

# Move duplicate
if [ -f "PzIV_Ausf_F1_Master_Icon.png" ]; then
    echo "  🗑️  Moving PzIV_Ausf_F1_Master_Icon.png to archive/ (duplicate)"
    mv "PzIV_Ausf_F1_Master_Icon.png" "archive/"
fi

# Move Italian vehicle to correct folder
if [ -f "Semovente 90-53.png" ]; then
    echo "  ❌  Moving Semovente 90-53.png to ../italian/ (wrong nation)"
    mv "Semovente 90-53.png" "../italian/semovente_90_53.png"
fi

echo ""
echo "Step 2: Moving unverified vehicles to needs_verification/..."
echo "  (These may be post-North Africa or need database verification)"
echo ""

# Move vehicles that need verification (not found in North Africa database)
declare -a UNVERIFIED=(
    "PZ II Ausf E.png"
    "Pz III ausf N.png"
    "Sd Kfz 132 Marder II.png"
    "Sd Kfz 139 Marder III.png"
    "Sd.Kfz. 233 \"Stummel\".png"
    "Sd.Kfz. 263.png"
    "Stuf III Ausf C.png"
    "Stug III Ausf F Template.png"
)

for file in "${UNVERIFIED[@]}"; do
    if [ -f "$file" ]; then
        echo "  ⚠️  Moving: $file"
        mv "$file" "needs_verification/"
    fi
done

echo ""
echo "Step 3: Renaming confirmed vehicles to project convention..."
echo ""

# Rename confirmed Panzer III variants
if [ -f "PZ III Ausf G.png" ]; then
    echo "  ✅ PZ III Ausf G.png → panzer_iii_ausf_g.png"
    mv "PZ III Ausf G.png" "panzer_iii_ausf_g.png"
fi

if [ -f "PZ III Ausf J.png" ]; then
    echo "  ✅ PZ III Ausf J.png → panzer_iii_ausf_j.png"
    mv "PZ III Ausf J.png" "panzer_iii_ausf_j.png"
fi

if [ -f "PZ III Ausf. L.png" ]; then
    echo "  ✅ PZ III Ausf. L.png → panzer_iii_ausf_l.png"
    mv "PZ III Ausf. L.png" "panzer_iii_ausf_l.png"
fi

# Rename confirmed Panzer IV variants
if [ -f "PZ IV Ausf F1.png" ]; then
    echo "  ✅ PZ IV Ausf F1.png → panzer_iv_ausf_f1.png"
    mv "PZ IV Ausf F1.png" "panzer_iv_ausf_f1.png"
fi

if [ -f "PZ IV Ausf F2.png" ]; then
    echo "  ✅ PZ IV Ausf F2.png → panzer_iv_ausf_f2.png"
    mv "PZ IV Ausf F2.png" "panzer_iv_ausf_f2.png"
fi

# Rename confirmed armored cars
if [ -f "Sd.Kfz 223.png" ]; then
    echo "  ✅ Sd.Kfz 223.png → sd_kfz_223.png"
    mv "Sd.Kfz 223.png" "sd_kfz_223.png"
fi

if [ -f "Sd.Kfz. 231 (8-Rad).png" ]; then
    echo "  ✅ Sd.Kfz. 231 (8-Rad).png → sd_kfz_231_8_rad.png"
    mv "Sd.Kfz. 231 (8-Rad).png" "sd_kfz_231_8_rad.png"
fi

if [ -f "Sd.Kfz. 232 (8-Rad).png" ]; then
    echo "  ✅ Sd.Kfz. 232 (8-Rad).png → sd_kfz_232_8_rad.png"
    mv "Sd.Kfz. 232 (8-Rad).png" "sd_kfz_232_8_rad.png"
fi

# Rename confirmed halftracks
if [ -f "Sd.Kfz 251.png" ]; then
    echo "  ✅ Sd.Kfz 251.png → sd_kfz_251.png"
    mv "Sd.Kfz 251.png" "sd_kfz_251.png"
fi

if [ -f "Sd.Kfz. 250(10).png" ]; then
    echo "  ✅ Sd.Kfz. 250(10).png → sd_kfz_250_10.png"
    mv "Sd.Kfz. 250(10).png" "sd_kfz_250_10.png"
fi

if [ -f "Sd.Kfz. 250(3).png" ]; then
    echo "  ✅ Sd.Kfz. 250(3).png → sd_kfz_250_3.png"
    mv "Sd.Kfz. 250(3).png" "sd_kfz_250_3.png"
fi

echo ""
echo "===================================="
echo "Rename Complete!"
echo ""
echo "Summary:"
echo "  ✅ Confirmed files renamed to project convention"
echo "  ⚠️  Unverified files moved to needs_verification/"
echo "  🗑️  Out-of-scope/duplicates moved to out_of_scope/ and archive/"
echo ""
echo "Next steps:"
echo "  1. Review needs_verification/ folder"
echo "  2. Check North Africa deployment dates for unverified vehicles"
echo "  3. Update equipment database if vehicles confirmed in scope"
echo "  4. Move verified files back and rename as needed"
echo ""
