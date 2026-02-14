
@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo      Excel to Tally AI Agent Launcher
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo During installation, make sure to check "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

REM Check for virtual environment
if not exist ".venv" (
    echo.
    echo [INFO] Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [INFO] Activating environment...
call .venv\Scripts\activate.bat

REM Update dependencies
echo [INFO] Checking dependencies...
python -m pip install --upgrade pip >nul
pip install -r backend\requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

REM Run the application
echo.
echo [INFO] Starting application...
python start_app.py

REM Pause on exit if error occurred
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application stopped unexpectedly.
    pause
)
