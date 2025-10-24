"""
MT5 Connector - Centralized MT5 Connection Management
Simple, single-point connection handler for ALL modules

This module provides ONE connection that all other modules can use.
No complex singletons, no session state, just one simple connection.
"""
import time
from datetime import datetime
from typing import Optional, Dict, Any

# Lazy import MT5
_mt5 = None
_initialized = False

def _ensure_mt5():
    """Ensure MT5 is imported"""
    global _mt5
    if _mt5 is None:
        try:
            import MetaTrader5 as mt5_module
            _mt5 = mt5_module
        except ImportError:
            raise ImportError(
                "MetaTrader5 not installed. Install with: pip install MetaTrader5"
            )
    return _mt5


# ============================================================================
# CONNECTION STATE (Module-level, shared by everyone)
# ============================================================================

_connection_active = False
_login = None
_password = None
_server = None
_connection_time = None
_last_error = None


# ============================================================================
# SIMPLE CONNECTION FUNCTIONS
# ============================================================================

def connect(login: int, password: str, server: str, timeout: int = 60000) -> bool:
    """
    Connect to MT5 (or return True if already connected)
    
    Args:
        login: MT5 account number
        password: MT5 password
        server: MT5 server name
        timeout: Connection timeout in milliseconds
        
    Returns:
        True if connected successfully
    """
    global _connection_active, _login, _password, _server, _connection_time, _last_error, _initialized
    
    mt5 = _ensure_mt5()
    
    # If already connected and working, return success
    if _connection_active and is_connected():
        print("✅ Already connected to MT5")
        return True
    
    # Clean up any stale connection
    if _initialized:
        print("🔄 Cleaning up previous connection...")
        disconnect()
        time.sleep(2)  # Wait for MT5 to fully release
    
    # Store credentials
    _login = login
    _password = password
    _server = server
    
    print(f"\n🔌 Connecting to MT5...")
    print(f"   Account: {login}")
    print(f"   Server: {server}")
    
    try:
        # Initialize MT5 with credentials
        if not mt5.initialize(
            login=login,
            password=password,
            server=server,
            timeout=timeout
        ):
            error = mt5.last_error()
            _last_error = f"MT5 initialization failed: {error}"
            print(f"❌ {_last_error}")
            return False
        
        _initialized = True
        
        # Wait for terminal to be ready
        for i in range(5):
            if mt5.terminal_info() is not None:
                break
            time.sleep(1)
        
        # Verify we're logged in
        account_info = mt5.account_info()
        if account_info is None:
            _last_error = "Failed to get account info after initialization"
            print(f"❌ {_last_error}")
            mt5.shutdown()
            _initialized = False
            return False
        
        if account_info.login != login:
            _last_error = f"Login mismatch: expected {login}, got {account_info.login}"
            print(f"❌ {_last_error}")
            mt5.shutdown()
            _initialized = False
            return False
        
        # Success!
        _connection_active = True
        _connection_time = datetime.now()
        _last_error = None
        
        print(f"✅ Connected successfully!")
        print(f"   Balance: {account_info.balance} {account_info.currency}")
        print(f"   Company: {account_info.company}")
        
        return True
        
    except Exception as e:
        _last_error = f"Connection error: {str(e)}"
        print(f"❌ {_last_error}")
        _connection_active = False
        _initialized = False
        return False


def disconnect() -> bool:
    """
    Disconnect from MT5
    
    Returns:
        True if disconnected successfully
    """
    global _connection_active, _connection_time, _initialized
    
    try:
        mt5 = _ensure_mt5()
        
        if _initialized:
            print("🔌 Disconnecting from MT5...")
            mt5.shutdown()
            time.sleep(1)  # Wait for clean shutdown
            _initialized = False
        
        _connection_active = False
        _connection_time = None
        
        print("✅ Disconnected successfully")
        return True
        
    except Exception as e:
        print(f"⚠️ Disconnect error: {e}")
        _connection_active = False
        _connection_time = None
        _initialized = False
        return False


def reconnect(login: int, password: str, server: str, timeout: int = 60000) -> bool:
    """
    Reconnect to MT5 (disconnect, wait, connect)
    
    Args:
        login: MT5 account number
        password: MT5 password
        server: MT5 server name
        timeout: Connection timeout in milliseconds
        
    Returns:
        True if reconnected successfully
    """
    print("🔄 Reconnecting to MT5...")
    disconnect()
    time.sleep(2)  # Extra wait for reconnection
    return connect(login, password, server, timeout)


def is_connected() -> bool:
    """
    Check if MT5 is connected and working
    
    Returns:
        True if connected and responsive
    """
    global _connection_active
    
    if not _connection_active or not _initialized:
        return False
    
    try:
        mt5 = _ensure_mt5()
        # Quick check - if terminal_info() works, we're connected
        return mt5.terminal_info() is not None
    except:
        _connection_active = False
        return False


def get_account_info() -> Optional[Dict[str, Any]]:
    """
    Get MT5 account information
    
    Returns:
        Dict with account info or None if not connected
    """
    if not is_connected():
        return None
    
    try:
        mt5 = _ensure_mt5()
        info = mt5.account_info()
        
        if info is None:
            return None
        
        return {
            'login': info.login,
            'server': info.server,
            'balance': info.balance,
            'equity': info.equity,
            'margin': info.margin,
            'margin_free': info.margin_free,
            'margin_level': info.margin_level,
            'currency': info.currency,
            'company': info.company,
            'name': info.name,
        }
    except Exception as e:
        print(f"⚠️ Error getting account info: {e}")
        return None


def get_connection_status() -> Dict[str, Any]:
    """
    Get connection status information
    
    Returns:
        Dict with connection status
    """
    return {
        'connected': is_connected(),
        'connection_time': _connection_time,
        'login': _login,
        'server': _server,
        'last_error': _last_error,
        'uptime_seconds': int((datetime.now() - _connection_time).total_seconds()) if _connection_time else 0
    }


def get_mt5():
    """
    Get the MT5 module instance (for direct API calls)
    
    Returns:
        MetaTrader5 module
        
    Raises:
        RuntimeError if not connected
    """
    if not is_connected():
        raise RuntimeError("Not connected to MT5. Call connect() first.")
    
    return _ensure_mt5()


# ============================================================================
# CONVENIENCE FUNCTIONS (for common operations)
# ============================================================================

def get_symbols() -> list:
    """Get list of available symbols"""
    if not is_connected():
        return []
    
    try:
        mt5 = _ensure_mt5()
        symbols = mt5.symbols_get()
        return [s.name for s in symbols] if symbols else []
    except:
        return []


def get_ohlcv(symbol: str, timeframe: str, bars: int = 1000):
    """
    Get OHLCV data for a symbol
    
    Args:
        symbol: Symbol name (e.g., "EURUSD")
        timeframe: Timeframe (e.g., "H1", "D1")
        bars: Number of bars to fetch
        
    Returns:
        DataFrame with OHLCV data or None
    """
    if not is_connected():
        print("❌ Not connected to MT5")
        return None
    
    try:
        import pandas as pd
        mt5 = _ensure_mt5()
        
        # Map timeframe string to MT5 constant
        timeframe_map = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1,
            'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1,
            'W1': mt5.TIMEFRAME_W1,
        }
        
        tf = timeframe_map.get(timeframe.upper())
        if tf is None:
            print(f"❌ Invalid timeframe: {timeframe}")
            return None
        
        # Fetch data
        rates = mt5.copy_rates_from_pos(symbol, tf, 0, bars)
        
        if rates is None or len(rates) == 0:
            print(f"❌ No data for {symbol} {timeframe}")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        # Rename columns to standard OHLCV format
        df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'tick_volume': 'Volume'
        }, inplace=True)
        
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None


# ============================================================================
# MODULE INFO
# ============================================================================

def get_module_info() -> str:
    """Get module information"""
    return """
MT5 Connector Module
====================
Simple, centralized MT5 connection management.

Usage:
    import mt5_connector
    
    # Connect
    mt5_connector.connect(login=12345, password="pass", server="Broker-Demo")
    
    # Check connection
    if mt5_connector.is_connected():
        print("Connected!")
    
    # Get data
    df = mt5_connector.get_ohlcv("EURUSD", "H1", 1000)
    
    # Get MT5 module for direct API calls
    mt5 = mt5_connector.get_mt5()
    
    # Disconnect
    mt5_connector.disconnect()

Connection is shared by ALL modules automatically!
"""


if __name__ == "__main__":
    print(get_module_info())
    print("\n" + "="*60)
    print("MT5 Connector Module Loaded")
    print("="*60)
