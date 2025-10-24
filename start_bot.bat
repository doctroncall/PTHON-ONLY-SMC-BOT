@echo off
setlocal enabledelayedexpansion
REM =============================================
REM SMC Bot - Pure Python Launcher
REM No Conda Required - Uses Python venv
REM =============================================

echo.
echo =============================================
echo      SMC BOT - PURE PYTHON LAUNCHER
echo =============================================
echo.

REM Step 1: Check if Python is installed
echo [1/5] Checking Python installation...

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python 3.11 or higher from:
    echo   https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python found - Version %PYTHON_VERSION%

REM Check Python version is 3.11+
python -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>nul
if errorlevel 1 (
    echo [WARNING] Python 3.11+ is recommended. Current version: %PYTHON_VERSION%
    echo The bot may not work correctly with older versions.
    echo.
)

echo.

REM Step 2: Check if virtual environment exists, create if needed
echo [2/5] Checking virtual environment...

if not exist "venv\" (
    echo [INFO] Creating Python virtual environment...
    echo This will take 1-2 minutes...
    echo.
    
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        echo Try running: python -m pip install --upgrade pip
        pause
        exit /b 1
    )
    
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment exists
)

echo.

REM Step 3: Activate virtual environment
echo [3/5] Activating virtual environment...

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)

echo [OK] Virtual environment activated
echo.

REM Step 4: Install/Update dependencies
echo [4/5] Installing dependencies...
echo.

REM Upgrade pip first
python -m pip install --upgrade pip --quiet

REM Install all dependencies from requirements.txt
echo [INFO] Installing packages from requirements.txt...
echo This may take 5-10 minutes on first run...
echo.

pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies!
    echo.
    echo Common solutions:
    echo   1. Check your internet connection
    echo   2. Try: python -m pip install --upgrade pip
    echo   3. Delete 'venv' folder and run this script again
    echo.
    echo For TA-Lib installation issues on Windows:
    echo   Download wheel from: https://github.com/cgohlke/talib-build/releases
    echo   Then: pip install path\to\TA_Lib-0.4.XX-cpXXX-win_amd64.whl
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] All dependencies installed
echo.

REM Create necessary directories
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "models" mkdir models
if not exist "reports" mkdir reports

REM Step 5: Launch the bot
echo [5/5] Launching SMC Bot...
echo.
echo =============================================
echo      BOT IS STARTING
echo =============================================
echo.
echo The dashboard will open in your browser
echo Press Ctrl+C to stop the bot
echo.

streamlit run app.py --server.headless=true --server.port=8501

REM When bot stops
echo.
echo =============================================
echo      BOT STOPPED
echo =============================================
echo.
echo To restart: Run "start_bot.bat" again
echo To deactivate venv: deactivate
echo.
pause

endlocal
