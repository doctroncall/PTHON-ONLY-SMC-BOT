@echo off
REM =============================================
REM Loguru Fix Script - Pure Python
REM =============================================

echo.
echo =============================================
echo   Loguru Quick Fix (Pure Python)
echo =============================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run start_bot.bat first to create the environment.
    echo.
    pause
    exit /b 1
)

echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/3] Installing/Upgrading loguru...
pip uninstall -y loguru
pip install --upgrade loguru

echo [3/3] Verifying installation...
python -c "import loguru; print('[OK] Loguru version:', loguru.__version__)"

if errorlevel 1 (
    echo.
    echo [ERROR] Loguru installation failed!
    echo.
    echo Try:
    echo   1. pip install --upgrade pip
    echo   2. pip install loguru --force-reinstall
    echo.
    pause
    exit /b 1
)

echo.
echo =============================================
echo   Loguru Fix Complete!
echo =============================================
echo.
echo You can now run: start_bot.bat
echo.
pause
