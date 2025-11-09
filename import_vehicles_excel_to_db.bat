@echo off
REM Import Vehicles Manual Entry Form to bg_reference_vehicles Database
REM Runs the Python import script

echo ================================================================================
echo IMPORT VEHICLES MANUAL ENTRY FORM TO DATABASE
echo ================================================================================
echo.

python "D:\north-africa-toe-builder\import_vehicles_excel_to_db.py"

echo.
echo Press any key to exit...
pause >nul
