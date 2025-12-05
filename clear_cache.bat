@echo off
REM Quick clear cache utility
echo.
echo =========================================
echo   CLEAR RECOGNITION CACHE
echo =========================================
echo.
echo This will delete all cached model files (.pkl)
echo to force fresh face recognition.
echo.
echo Use this when:
echo   - Recognition is inaccurate
echo   - After adding new images
echo   - Weekly maintenance
echo.
echo =========================================
echo.

set /p confirm="Are you sure? (Y/N): "

if /i "%confirm%"=="Y" (
    echo.
    echo Deleting cache files...
    del /F /Q "data\students\*.pkl" 2>nul

    if %ERRORLEVEL% EQU 0 (
        echo.
        echo [SUCCESS] Cache cleared!
        echo Next recognition will build fresh cache.
    ) else (
        echo.
        echo [INFO] No cache files found or already cleared.
    )
) else (
    echo.
    echo Operation cancelled.
)

echo.
echo =========================================
echo   Press any key to exit...
echo =========================================
pause > nul

