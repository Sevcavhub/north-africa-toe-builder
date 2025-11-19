@echo off
REM Start Interactive Datacard Builder
REM Double-click this file to start the server

cd /d "%~dp0"

echo ======================================================================
echo Starting Interactive Datacard Builder Server
echo ======================================================================
echo.
echo Once started, open your browser to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
echo ======================================================================

python interactive_datacard_server.py

pause
