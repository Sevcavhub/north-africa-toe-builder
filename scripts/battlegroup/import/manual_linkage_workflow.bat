@echo off
REM Manual Linkage Workflow - Step-by-step interface for linking manual vehicles to BG Builder
echo ================================================================================
echo MANUAL VEHICLE LINKAGE WORKFLOW
echo ================================================================================
echo.
echo This workflow helps you link your manually-entered vehicles to BG Builder data.
echo.
echo STEP 1: Generate linkage review CSV
echo    - Creates manual_vehicle_linkage_review.csv
echo    - Shows your manual vehicles side-by-side with suggested BG Builder matches
echo    - Includes current linkages (from fuzzy matching) for review
echo.
pause

cd /d "%~dp0..\..\..\"

python scripts\battlegroup\import\create_manual_linkage_interface.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to generate linkage review CSV
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo STEP 2: Review and approve linkages in Excel
echo ================================================================================
echo.
echo Opening manual_vehicle_linkage_review.csv in Excel...
echo.
echo INSTRUCTIONS:
echo   1. Review each row's SUGGESTED matches (with similarity percentages)
echo   2. Check the CURRENT linkage (if exists from fuzzy matching)
echo   3. Enter the correct BG Builder ID in the APPROVED_bg_id column
echo   4. Add notes if needed (e.g., 'No match', 'Wrong variant', etc.)
echo   5. Save and close Excel when done
echo.
echo Column Guide:
echo   - manual_id/name: Your manually-entered vehicle
echo   - manual_armor/movement/weapon: Your current data
echo   - CURRENT_bg_builder_id/name: Existing fuzzy match (if any)
echo   - SUGGESTED_bg_id/name_1-3: Top 3 candidates with similarity percentages
echo   - APPROVED_bg_id: YOU FILL THIS - enter bg_id of correct match
echo   - NOTES: Optional notes about the linkage decision
echo.
pause

start "" "manual_vehicle_linkage_review.csv"

echo.
echo Press any key AFTER you have finished reviewing in Excel and SAVED the file...
pause >nul

echo.
echo ================================================================================
echo STEP 3: Import approved linkages to database
echo ================================================================================
echo.

python scripts\battlegroup\import\import_manual_linkages.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to import approved linkages
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo LINKAGE WORKFLOW COMPLETE
echo ================================================================================
echo.
echo Your manual vehicles are now linked to BG Builder data.
echo.
echo Next steps:
echo   - Run prepopulate_excel_template.py to create Tobruk/Torch pre-populated form
echo   - Or query v_vehicles_unified view to see merged data
echo.
pause
