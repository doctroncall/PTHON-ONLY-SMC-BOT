# 🚀 Quick Start Guide - Pure Python Edition

Get your MT5 Sentiment Analysis Bot running in 2 easy steps!

## ⚡ Fast Track Installation

Your bot uses **Pure Python** with virtual environments for maximum simplicity!

### Windows Users:

1. **Install Python 3.11+**
   - Download: https://www.python.org/downloads/
   - ⚠️ **Check "Add Python to PATH" during installation!**

2. **Double-click `start_bot.bat`**
3. **Wait 5-10 minutes (first time only)**
4. **Dashboard opens automatically!**

### Linux/Mac Users:

1. **Install Python 3.11+**
   - Ubuntu/Debian: `sudo apt install python3.11 python3.11-venv python3-pip`
   - macOS: `brew install python@3.11`
   - Or download from: https://www.python.org/downloads/

2. **Run in terminal:**
   ```bash
   chmod +x start_bot.sh
   ./start_bot.sh
   ```
3. **Wait 5-10 minutes (first time only)**
4. **Dashboard opens automatically!**

---

## 📋 What the Launcher Does:

✅ Checks if Python 3.11+ is installed  
✅ Creates isolated virtual environment (venv)  
✅ Installs all dependencies from requirements.txt  
✅ Installs all ML libraries (TensorFlow, XGBoost, etc.)  
✅ Installs Streamlit and all dependencies  
✅ Creates required directories (data, logs, models, reports)  
✅ Initializes SQLite database  
✅ Launches Streamlit dashboard  
✅ Opens browser at http://localhost:8501  

---

## 🌟 Why Pure Python is Better

### Simple & Direct:
✅ **No Conda required**  
✅ **Uses standard Python venv**  
✅ **Installs via pip from requirements.txt**  
✅ **Faster setup**  
✅ **Less disk space**  
✅ **Standard Python workflow**  

---

## ⚙️ What You Need:

### Prerequisites:
- [ ] **Python 3.11+ installed**
- [ ] Internet connection (first-time setup only)
- [ ] ~1.5GB free disk space
- [ ] 5-10 minutes (first run only)
- [ ] MT5 credentials (for later)

### First-Time Setup:

**1. Install Python 3.11+**

**Windows:**
- Download: https://www.python.org/downloads/
- Run installer
- ⚠️ **IMPORTANT:** Check "Add Python to PATH"
- Click "Install Now"

**macOS:**
```bash
brew install python@3.11
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**2. Run the Bot**

**Windows:**
```batch
start_bot.bat
```

**Linux/Mac:**
```bash
chmod +x start_bot.sh
./start_bot.sh
```

The launcher will:
- Create `venv` folder (virtual environment)
- Install all packages automatically
- Launch the dashboard

**3. Wait for Setup**

First run takes 5-10 minutes:
- ⏳ Creating virtual environment... (1 min)
- ⏳ Installing packages... (5-8 min)
- ✅ Launching bot... (instant!)

**Subsequent runs:** Instant! (venv already set up)

---

## 🔧 Configuration (Optional)

### MT5 Connection Settings:

1. Go to **Settings** tab in the dashboard
2. Enter your MT5 credentials:
   - **Account Number**: Your MT5 login
   - **Password**: Your MT5 password  
   - **Server**: Your broker's server (e.g., "ICMarkets-Demo")
3. Click **"Connect to MT5"**

### Analysis Settings:

1. **Symbol**: Choose currency pair (default: EURUSD)
2. **Timeframes**: Select timeframes to analyze (M15, H1, H4, D1)
3. **Update Frequency**: Auto-refresh interval (1-60 minutes)
4. **ML Settings**: Enable/disable machine learning features

---

## 📊 Dashboard Overview

Once the bot starts, you'll see:

### **Main Tab** - Sentiment Analysis
- Real-time market sentiment (Bullish/Neutral/Bearish)
- Confidence score (0-100%)
- Risk level indicator
- Interactive price chart with signals
- Contributing factors breakdown

### **Multi-Timeframe Tab** - Confluence Analysis
- Analysis across multiple timeframes
- Timeframe alignment score
- Individual timeframe sentiments
- Weighted consensus

### **Health Tab** - System Monitoring
- MT5 connection status
- Data pipeline health
- ML model status
- System resource usage
- Recent activity feed

### **Settings Tab** - Configuration
- MT5 connection settings
- Analysis parameters
- ML training controls
- System diagnostics

---

## 🎯 Next Steps

1. **Connect to MT5** (Settings tab)
2. **Select your symbol** (e.g., EURUSD, GBPUSD)
3. **Click "Analyze"** (Main tab)
4. **Review sentiment** and confidence
5. **Check multi-timeframe** alignment
6. **Monitor health** status

---

## 🆘 Troubleshooting

### "Python not found"
- Install Python 3.11+ from https://www.python.org/downloads/
- Make sure "Add to PATH" was checked during installation
- Restart your terminal/command prompt

### "Failed to create virtual environment"
- Windows: Make sure Python is in PATH
- Linux: Install venv: `sudo apt install python3.11-venv`
- Delete `venv` folder and try again

### "Failed to install dependencies"
- Check internet connection
- Try: `python -m pip install --upgrade pip`
- For TA-Lib on Windows: Download wheel from https://github.com/cgohlke/talib-build/releases

### "Streamlit command not found"
- Activate venv first:
  - Windows: `venv\Scripts\activate`
  - Linux/Mac: `source venv/bin/activate`
- Then: `pip install streamlit`

### MT5 Connection Issues
- Make sure MetaTrader 5 is installed
- Enable "Algo Trading" in MT5 (Tools → Options → Expert Advisors)
- Check firewall isn't blocking Python
- Verify credentials are correct

### More Help
See the full [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide

---

## ✅ Success Checklist

- [x] Python 3.11+ installed
- [x] Ran start_bot script
- [x] Virtual environment created
- [x] Dependencies installed
- [x] Dashboard opened in browser
- [x] Connected to MT5
- [x] First analysis completed
- [x] Health checks passing

---

## 📚 Additional Resources

- **Full Setup Guide**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Architecture**: [ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 💡 Pro Tips

1. **Keep Python updated**: `python -m pip install --upgrade pip`
2. **Update bot**: `pip install -r requirements.txt --upgrade`
3. **Check health regularly**: Health tab shows system status
4. **Enable auto-refresh**: Dashboard auto-updates analysis
5. **Review logs**: `logs/` folder has detailed logs
6. **Backup database**: `data/mt5_sentiment.db` stores all data

---

## 🎉 You're Ready!

Your MT5 Sentiment Analysis Bot is now running!

**Dashboard URL**: http://localhost:8501

**To stop**: Press `Ctrl+C` in the terminal  
**To restart**: Run `start_bot.bat` (Windows) or `./start_bot.sh` (Linux/Mac)

Happy trading! 📈
