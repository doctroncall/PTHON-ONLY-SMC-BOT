"""
Market Regime Detection
Identify and classify market conditions (trending/ranging, volatility levels, etc.)
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional
from sklearn.cluster import KMeans
import warnings

try:
    from hmmlearn import hmm
    HMM_AVAILABLE = True
except ImportError:
    HMM_AVAILABLE = False

from src.utils.logger import get_logger

warnings.filterwarnings('ignore')
logger = get_logger()


class RegimeDetector:
    """
    Detect and classify market regimes
    
    Regimes:
    - Volatility: low/normal/high
    - Trend: trending/ranging
    - Volume: dry/normal/surge
    - Hidden states via HMM
    """
    
    def __init__(self):
        """Initialize regime detector"""
        self.logger = logger
        self.current_regime = None
    
    def detect_volatility_regime(
        self,
        df: pd.DataFrame,
        window: int = 20
    ) -> pd.Series:
        """
        Classify volatility regime as low/normal/high
        
        Args:
            df: DataFrame with OHLCV data
            window: Rolling window for volatility calculation
            
        Returns:
            Series with regime labels (0=low, 1=normal, 2=high)
        """
        try:
            # Calculate returns volatility
            returns = df['Close'].pct_change()
            vol_short = returns.rolling(window).std()
            vol_long = returns.rolling(window * 3).std()
            
            # Relative volatility
            rel_vol = vol_short / vol_long
            
            # Classify into regimes
            regime = pd.cut(
                rel_vol,
                bins=[0, 0.7, 1.3, np.inf],
                labels=[0, 1, 2],  # low, normal, high
                include_lowest=True
            )
            
            # Forward fill NaN values
            regime = regime.fillna(method='ffill').fillna(1)
            
            return regime.astype(int)
            
        except Exception as e:
            self.logger.error(f"Error detecting volatility regime: {e}", category="analysis")
            return pd.Series([1] * len(df), index=df.index)
    
    def detect_trend_regime(
        self,
        df: pd.DataFrame,
        adx_threshold: int = 25
    ) -> pd.Series:
        """
        Classify as trending (1) or ranging (0)
        
        Args:
            df: DataFrame with indicators (needs 'adx' column)
            adx_threshold: ADX threshold for trending
            
        Returns:
            Series with regime labels (0=ranging, 1=trending)
        """
        try:
            # Calculate ADX if not present
            if 'adx' not in df.columns:
                self.logger.warning("ADX not found, calculating basic trend regime", category="analysis")
                # Simple EMA-based trend detection
                ema_fast = df['Close'].ewm(span=20).mean()
                ema_slow = df['Close'].ewm(span=50).mean()
                ema_diff = (ema_fast - ema_slow).abs()
                atr = df['High'].rolling(14).max() - df['Low'].rolling(14).min()
                trending = (ema_diff > atr).astype(int)
                return trending
            
            # ADX-based detection
            adx = df['adx']
            
            # Trending if ADX > threshold
            trending = (adx > adx_threshold).astype(int)
            
            # Confirm with directional movement
            if 'ema_20' in df.columns and 'ema_50' in df.columns:
                ema_diff = (df['ema_20'] - df['ema_50']).abs()
                if 'atr' in df.columns:
                    strong_trend = ema_diff > df['atr']
                    trending = trending & strong_trend.astype(int)
            
            return trending
            
        except Exception as e:
            self.logger.error(f"Error detecting trend regime: {e}", category="analysis")
            return pd.Series([0] * len(df), index=df.index)
    
    def detect_volume_regime(
        self,
        df: pd.DataFrame,
        window: int = 20
    ) -> pd.Series:
        """
        Classify volume regime as dry/normal/surge
        
        Args:
            df: DataFrame with Volume column
            window: Rolling window for volume average
            
        Returns:
            Series with regime labels (0=dry, 1=normal, 2=surge)
        """
        try:
            # Calculate volume moving average
            vol_ma = df['Volume'].rolling(window).mean()
            
            # Relative volume
            rel_vol = df['Volume'] / vol_ma
            
            # Classify into regimes
            regime = rel_vol.apply(
                lambda x: 0 if x < 0.7 else (2 if x > 1.5 else 1)
            )
            
            # Handle NaN values
            regime = regime.fillna(1)
            
            return regime.astype(int)
            
        except Exception as e:
            self.logger.error(f"Error detecting volume regime: {e}", category="analysis")
            return pd.Series([1] * len(df), index=df.index)
    
    def detect_price_efficiency(
        self,
        df: pd.DataFrame,
        window: int = 10
    ) -> pd.Series:
        """
        Calculate price efficiency (trending vs choppy)
        
        Higher values = more efficient (trending)
        Lower values = less efficient (choppy/ranging)
        
        Args:
            df: DataFrame with Close prices
            window: Lookback window
            
        Returns:
            Series with efficiency scores (0-1)
        """
        try:
            # Net price change
            price_change = (df['Close'] - df['Close'].shift(window)).abs()
            
            # Total path length
            path_length = df['Close'].diff().abs().rolling(window).sum()
            
            # Efficiency ratio
            efficiency = (price_change / path_length).fillna(0.5)
            
            # Clip to [0, 1]
            efficiency = efficiency.clip(0, 1)
            
            return efficiency
            
        except Exception as e:
            self.logger.error(f"Error calculating price efficiency: {e}", category="analysis")
            return pd.Series([0.5] * len(df), index=df.index)
    
    def detect_hidden_regimes_kmeans(
        self,
        df: pd.DataFrame,
        n_regimes: int = 3
    ) -> pd.Series:
        """
        Detect hidden regimes using K-means clustering
        
        Args:
            df: DataFrame with price and volume data
            n_regimes: Number of regimes to identify
            
        Returns:
            Series with regime labels (0, 1, 2, ...)
        """
        try:
            # Create features for clustering
            returns = df['Close'].pct_change()
            volatility = returns.rolling(20).std()
            volume_ratio = df['Volume'] / df['Volume'].rolling(20).mean()
            
            # Combine features
            features = pd.DataFrame({
                'returns': returns,
                'volatility': volatility,
                'volume_ratio': volume_ratio
            }).fillna(0)
            
            # Fit K-means
            kmeans = KMeans(n_clusters=n_regimes, random_state=42, n_init=10)
            regimes = kmeans.fit_predict(features)
            
            return pd.Series(regimes, index=df.index)
            
        except Exception as e:
            self.logger.error(f"Error in K-means regime detection: {e}", category="analysis")
            return pd.Series([0] * len(df), index=df.index)
    
    def detect_hidden_regimes_hmm(
        self,
        df: pd.DataFrame,
        n_states: int = 3
    ) -> Optional[pd.Series]:
        """
        Use Hidden Markov Model to detect market regimes
        
        Args:
            df: DataFrame with OHLCV data
            n_states: Number of hidden states
            
        Returns:
            Series with regime labels or None if HMM not available
        """
        if not HMM_AVAILABLE:
            self.logger.warning("hmmlearn not available, skipping HMM detection", category="analysis")
            return None
        
        try:
            # Features for HMM
            returns = df['Close'].pct_change()
            volume_change = df['Volume'].pct_change()
            
            features = pd.DataFrame({
                'returns': returns,
                'volume': volume_change
            }).fillna(0)
            
            # Fit Gaussian HMM
            model = hmm.GaussianHMM(
                n_components=n_states,
                covariance_type='full',
                n_iter=1000,
                random_state=42
            )
            
            model.fit(features.values)
            
            # Predict regimes
            regimes = model.predict(features.values)
            
            return pd.Series(regimes, index=df.index)
            
        except Exception as e:
            self.logger.error(f"Error in HMM regime detection: {e}", category="analysis")
            return None
    
    def get_current_regime(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Get comprehensive regime analysis for current market state
        
        Args:
            df: DataFrame with OHLCV and indicator data
            
        Returns:
            Dict with all regime classifications
        """
        try:
            regimes = {
                'volatility': self.detect_volatility_regime(df).iloc[-1],
                'trend': self.detect_trend_regime(df).iloc[-1],
                'volume': self.detect_volume_regime(df).iloc[-1],
                'efficiency': self.detect_price_efficiency(df).iloc[-1],
                'cluster': self.detect_hidden_regimes_kmeans(df).iloc[-1],
            }
            
            # Add HMM if available
            hmm_regimes = self.detect_hidden_regimes_hmm(df)
            if hmm_regimes is not None:
                regimes['hmm_state'] = hmm_regimes.iloc[-1]
            
            # Human-readable labels
            vol_labels = {0: 'low', 1: 'normal', 2: 'high'}
            trend_labels = {0: 'ranging', 1: 'trending'}
            volume_labels = {0: 'dry', 1: 'normal', 2: 'surge'}
            
            regimes['volatility_label'] = vol_labels[int(regimes['volatility'])]
            regimes['trend_label'] = trend_labels[int(regimes['trend'])]
            regimes['volume_label'] = volume_labels[int(regimes['volume'])]
            
            self.current_regime = regimes
            
            return regimes
            
        except Exception as e:
            self.logger.error(f"Error getting current regime: {e}", category="analysis")
            return {
                'volatility': 1,
                'trend': 0,
                'volume': 1,
                'efficiency': 0.5,
                'error': str(e)
            }
    
    def is_favorable_conditions(
        self,
        df: pd.DataFrame,
        strategy: str = 'trend_following'
    ) -> bool:
        """
        Check if current regime is favorable for trading strategy
        
        Args:
            df: DataFrame with market data
            strategy: 'trend_following' or 'mean_reversion'
            
        Returns:
            True if conditions are favorable
        """
        regimes = self.get_current_regime(df)
        
        if strategy == 'trend_following':
            # Favorable: trending market, normal/high volatility
            return (regimes['trend'] == 1 and 
                   regimes['volatility'] >= 1 and
                   regimes['efficiency'] > 0.6)
        
        elif strategy == 'mean_reversion':
            # Favorable: ranging market, normal volatility
            return (regimes['trend'] == 0 and
                   regimes['volatility'] <= 1 and
                   regimes['efficiency'] < 0.4)
        
        return True  # Default: trade in all conditions


if __name__ == "__main__":
    # Test regime detector
    print("🔍 Testing Regime Detector...")
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=500, freq='1H')
    
    # Create trending period followed by ranging period
    trend = np.linspace(100, 120, 250)
    trend += np.random.normal(0, 1, 250)
    
    ranging = np.random.normal(120, 2, 250)
    
    prices = np.concatenate([trend, ranging])
    
    df = pd.DataFrame({
        'Open': prices - np.random.uniform(0, 0.5, 500),
        'High': prices + np.random.uniform(0, 1, 500),
        'Low': prices - np.random.uniform(0, 1, 500),
        'Close': prices,
        'Volume': np.random.randint(1000, 10000, 500),
    }, index=dates)
    
    detector = RegimeDetector()
    
    # Test volatility regime
    vol_regime = detector.detect_volatility_regime(df)
    print(f"✓ Volatility regime detected: {vol_regime.value_counts().to_dict()}")
    
    # Test trend regime
    trend_regime = detector.detect_trend_regime(df)
    print(f"✓ Trend regime: {trend_regime.value_counts().to_dict()}")
    
    # Test volume regime
    volume_regime = detector.detect_volume_regime(df)
    print(f"✓ Volume regime: {volume_regime.value_counts().to_dict()}")
    
    # Test current regime
    current = detector.get_current_regime(df)
    print(f"✓ Current regime: {current}")
    
    # Test clustering
    clusters = detector.detect_hidden_regimes_kmeans(df, n_regimes=3)
    print(f"✓ K-means clusters: {clusters.value_counts().to_dict()}")
    
    print("\n✓ Regime detector test completed")
