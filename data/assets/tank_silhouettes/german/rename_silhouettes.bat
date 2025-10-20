@echo off
REM German Tank Silhouette Rename Script (Windows)
REM Renames user-provided files to project naming convention
REM Date: 2025-10-20

cd /d "%~dp0"

echo German Tank Silhouette Batch Rename
echo ====================================
echo.

REM Create directories for organization
if not exist "out_of_scope" mkdir out_of_scope
if not exist "archive" mkdir archive
if not exist "needs_verification" mkdir needs_verification

echo Step 1: Moving out-of-scope and duplicate files...
echo.

REM Move out-of-scope (post-1943 vehicles)
if exist "King Tiger II.png" (
    echo   WARNING Moving King Tiger II.png to out_of_scope/ (not in North Africa 1940-1943^)
    move "King Tiger II.png" "out_of_scope\"
)

REM Move duplicate
if exist "PzIV_Ausf_F1_Master_Icon.png" (
    echo   DUPLICATE Moving PzIV_Ausf_F1_Master_Icon.png to archive/ (duplicate^)
    move "PzIV_Ausf_F1_Master_Icon.png" "archive\"
)

REM Move Italian vehicle to correct folder
if exist "Semovente 90-53.png" (
    echo   ERROR Moving Semovente 90-53.png to ..\italian\ (wrong nation^)
    move "Semovente 90-53.png" "..\italian\semovente_90_53.png"
)

echo.
echo Step 2: Moving unverified vehicles to needs_verification/...
echo   (These may be post-North Africa or need database verification^)
echo.

REM Move vehicles that need verification
if exist "PZ II Ausf E.png" (
    echo   WARNING Moving: PZ II Ausf E.png
    move "PZ II Ausf E.png" "needs_verification\"
)

if exist "Pz III ausf N.png" (
    echo   WARNING Moving: Pz III ausf N.png
    move "Pz III ausf N.png" "needs_verification\"
)

if exist "Sd Kfz 132 Marder II.png" (
    echo   WARNING Moving: Sd Kfz 132 Marder II.png
    move "Sd Kfz 132 Marder II.png" "needs_verification\"
)

if exist "Sd Kfz 139 Marder III.png" (
    echo   WARNING Moving: Sd Kfz 139 Marder III.png
    move "Sd Kfz 139 Marder III.png" "needs_verification\"
)

if exist "Sd.Kfz. 233 \"Stummel\".png" (
    echo   WARNING Moving: Sd.Kfz. 233 "Stummel".png
    move "Sd.Kfz. 233 \"Stummel\".png" "needs_verification\"
)

if exist "Sd.Kfz. 263.png" (
    echo   WARNING Moving: Sd.Kfz. 263.png
    move "Sd.Kfz. 263.png" "needs_verification\"
)

if exist "Stuf III Ausf C.png" (
    echo   WARNING Moving: Stuf III Ausf C.png
    move "Stuf III Ausf C.png" "needs_verification\"
)

if exist "Stug III Ausf F Template.png" (
    echo   WARNING Moving: Stug III Ausf F Template.png
    move "Stug III Ausf F Template.png" "needs_verification\"
)

echo.
echo Step 3: Renaming confirmed vehicles to project convention...
echo.

REM Rename confirmed Panzer III variants
if exist "PZ III Ausf G.png" (
    echo   OK PZ III Ausf G.png -^> panzer_iii_ausf_g.png
    ren "PZ III Ausf G.png" "panzer_iii_ausf_g.png"
)

if exist "PZ III Ausf J.png" (
    echo   OK PZ III Ausf J.png -^> panzer_iii_ausf_j.png
    ren "PZ III Ausf J.png" "panzer_iii_ausf_j.png"
)

if exist "PZ III Ausf. L.png" (
    echo   OK PZ III Ausf. L.png -^> panzer_iii_ausf_l.png
    ren "PZ III Ausf. L.png" "panzer_iii_ausf_l.png"
)

REM Rename confirmed Panzer IV variants
if exist "PZ IV Ausf F1.png" (
    echo   OK PZ IV Ausf F1.png -^> panzer_iv_ausf_f1.png
    ren "PZ IV Ausf F1.png" "panzer_iv_ausf_f1.png"
)

if exist "PZ IV Ausf F2.png" (
    echo   OK PZ IV Ausf F2.png -^> panzer_iv_ausf_f2.png
    ren "PZ IV Ausf F2.png" "panzer_iv_ausf_f2.png"
)

REM Rename confirmed armored cars
if exist "Sd.Kfz 223.png" (
    echo   OK Sd.Kfz 223.png -^> sd_kfz_223.png
    ren "Sd.Kfz 223.png" "sd_kfz_223.png"
)

if exist "Sd.Kfz. 231 (8-Rad).png" (
    echo   OK Sd.Kfz. 231 (8-Rad^).png -^> sd_kfz_231_8_rad.png
    ren "Sd.Kfz. 231 (8-Rad).png" "sd_kfz_231_8_rad.png"
)

if exist "Sd.Kfz. 232 (8-Rad).png" (
    echo   OK Sd.Kfz. 232 (8-Rad^).png -^> sd_kfz_232_8_rad.png
    ren "Sd.Kfz. 232 (8-Rad).png" "sd_kfz_232_8_rad.png"
)

REM Rename confirmed halftracks
if exist "Sd.Kfz 251.png" (
    echo   OK Sd.Kfz 251.png -^> sd_kfz_251.png
    ren "Sd.Kfz 251.png" "sd_kfz_251.png"
)

if exist "Sd.Kfz. 250(10).png" (
    echo   OK Sd.Kfz. 250(10^).png -^> sd_kfz_250_10.png
    ren "Sd.Kfz. 250(10).png" "sd_kfz_250_10.png"
)

if exist "Sd.Kfz. 250(3).png" (
    echo   OK Sd.Kfz. 250(3^).png -^> sd_kfz_250_3.png
    ren "Sd.Kfz. 250(3).png" "sd_kfz_250_3.png"
)

echo.
echo ====================================
echo Rename Complete!
echo.
echo Summary:
echo   OK Confirmed files renamed to project convention
echo   WARNING Unverified files moved to needs_verification/
echo   DUPLICATE Out-of-scope/duplicates moved to out_of_scope/ and archive/
echo.
echo Next steps:
echo   1. Review needs_verification/ folder
echo   2. Check North Africa deployment dates for unverified vehicles
echo   3. Update equipment database if vehicles confirmed in scope
echo   4. Move verified files back and rename as needed
echo.

pause
