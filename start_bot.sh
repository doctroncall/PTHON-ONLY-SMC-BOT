#!/bin/bash
# ========================================
# MT5 Sentiment Analysis Bot Launcher
# Pure Python Version - No Conda Required
# For Linux/Mac users
# ========================================

echo ""
echo "========================================"
echo "MT5 Sentiment Analysis Bot (Pure Python)"
echo "========================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo ""
    echo "Please install Python 3.11 or higher:"
    echo "  - Ubuntu/Debian: sudo apt install python3.11 python3.11-venv python3-pip"
    echo "  - macOS: brew install python@3.11"
    echo "  - Or download from: https://www.python.org/downloads/"
    echo ""
    exit 1
fi

# Get Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "[OK] Python found - Version $PYTHON_VERSION"

# Check if version is 3.11+
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo "[WARNING] Python 3.11+ is recommended. Current version: $PYTHON_VERSION"
    echo "The bot may not work correctly with older versions."
    echo ""
fi

echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[SETUP] Creating Python virtual environment..."
    echo "This will take 1-2 minutes..."
    echo ""
    
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo ""
        echo "[ERROR] Failed to create virtual environment"
        echo ""
        echo "Try installing venv:"
        echo "  - Ubuntu/Debian: sudo apt install python3.11-venv"
        echo "  - Or: sudo apt install python3-venv"
        echo ""
        exit 1
    fi
    
    echo "[OK] Virtual environment created"
    echo ""
else
    echo "[OK] Virtual environment exists"
    echo ""
fi

# Activate virtual environment
echo "[SETUP] Activating virtual environment..."

source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment"
    echo ""
    echo "Try:"
    echo "  1. Delete venv folder: rm -rf venv"
    echo "  2. Run this script again"
    echo ""
    exit 1
fi

echo "[OK] Virtual environment activated"
echo ""

# Upgrade pip
echo "[SETUP] Upgrading pip..."
python -m pip install --upgrade pip --quiet
echo ""

# Install dependencies
echo "[SETUP] Installing dependencies..."
echo "This may take 5-10 minutes on first run..."
echo ""

pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Failed to install dependencies"
    echo ""
    echo "Common solutions:"
    echo "  1. Check your internet connection"
    echo "  2. Try: python -m pip install --upgrade pip"
    echo "  3. Delete venv and run again: rm -rf venv && ./start_bot.sh"
    echo ""
    echo "For TA-Lib installation issues:"
    echo "  - Ubuntu/Debian: sudo apt install build-essential python3-dev libta-lib-dev"
    echo "  - macOS: brew install ta-lib"
    echo ""
    exit 1
fi

echo ""
echo "[OK] All dependencies installed"
echo ""

# Create necessary directories
echo "[SETUP] Checking directory structure..."
mkdir -p data logs models reports
echo "[OK] Directory structure ready"
echo ""

# Check if database needs initialization
if [ ! -f "data/mt5_sentiment.db" ]; then
    echo "[SETUP] Initializing database..."
    python -c "from src.database.models import init_database; init_database(); print('[OK] Database initialized')" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "[WARNING] Database initialization failed - will retry on first run"
        echo "This is normal for first-time setup"
    else
        echo "[OK] Database initialized successfully"
    fi
else
    echo "[OK] Database already initialized"
fi

echo ""
echo "========================================"
echo "Starting MT5 Sentiment Analysis Bot..."
echo "========================================"
echo ""
echo "[INFO] Using Python virtual environment"
echo "[INFO] Dashboard will open in your browser automatically"
echo "[INFO] Press Ctrl+C to stop the bot"
echo ""
echo "Launching Streamlit..."
echo ""

# Start Streamlit with the app
streamlit run app.py --server.headless=true --server.port=8501
STREAMLIT_EXIT_CODE=$?

# If Streamlit exits, show message
echo ""
echo "========================================"
echo "Bot stopped"
echo "========================================"

if [ $STREAMLIT_EXIT_CODE -ne 0 ]; then
    echo ""
    echo "[WARNING] Application exited with error code: $STREAMLIT_EXIT_CODE"
    echo "Check the logs folder for error details"
    echo ""
fi

echo ""
echo "To restart the bot, run this script again: ./start_bot.sh"
echo "To deactivate venv: deactivate"
echo ""
