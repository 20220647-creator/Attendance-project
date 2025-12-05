@echo off
REM Quick check database status
echo.
echo =========================================
echo   DATABASE CHECK UTILITY
echo =========================================
echo.

REM Activate virtual environment if exists
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM Run check script
python check_database.py

echo.
echo =========================================
echo   Press any key to continue...
echo =========================================
pause > nul

