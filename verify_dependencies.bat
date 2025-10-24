@echo off
REM ========================================
REM Dependency Verification Script
REM Pure Python Version
REM ========================================

echo.
echo Running dependency verification...
echo.

REM Check if Python is available
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please run start_bot.bat first to set up the environment
    echo.
    pause
    exit /b 1
)

REM Check if we're in a virtual environment
if not defined VIRTUAL_ENV (
    echo [WARNING] Not in a virtual environment
    echo Attempting to activate venv...
    
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
        echo [OK] Virtual environment activated
    ) else (
        echo [ERROR] Virtual environment not found!
        echo Please run start_bot.bat first
        echo.
        pause
        exit /b 1
    )
)

echo [OK] Virtual environment: %VIRTUAL_ENV%
echo.

REM Run the verification script
python verify_dependencies.py

REM Exit code is passed from Python script
exit /b %errorlevel%
