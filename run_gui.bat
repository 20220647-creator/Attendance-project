@echo off
chcp 65001 >nul
REM Launcher for Face Recognition Attendance System GUI

echo ============================================================
echo   Face Recognition Attendance System - GUI Launcher
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

echo Starting GUI application...
echo.

REM Run the GUI application
python main_gui.py

REM If there's an error, keep the window open
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Application exited with error code %errorlevel%
    pause
)

