"""
Hyperparameter Tuner using Optuna
Automatically finds best hyperparameters for ML models
"""
import optuna
from optuna.pruners import MedianPruner
from sklearn.model_selection import cross_val_score, TimeSeriesSplit
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from typing import Dict, Any, Optional
import numpy as np

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

try:
    import catboost as cb
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger()


class HyperparameterTuner:
    """
    Optimize model hyperparameters using Bayesian optimization (Optuna)
    
    Uses time-series cross-validation to prevent look-ahead bias
    """
    
    def __init__(self, n_trials: int = 100, cv_folds: int = 5, timeout: Optional[int] = 3600):
        """
        Initialize hyperparameter tuner
        
        Args:
            n_trials: Number of optimization trials
            cv_folds: Number of cross-validation folds
            timeout: Timeout in seconds (None for no limit)
        """
        self.n_trials = n_trials
        self.cv_folds = cv_folds
        self.timeout = timeout
        self.study = None
        self.logger = logger
    
    def optimize_xgboost(self, X_train, y_train, use_tscv: bool = True) -> Dict[str, Any]:
        """
        Find optimal XGBoost parameters
        
        Args:
            X_train: Training features
            y_train: Training labels
            use_tscv: Use TimeSeriesSplit instead of regular CV
            
        Returns:
            Dict with best parameters
        """
        self.logger.info("Starting XGBoost hyperparameter optimization", category="ml_training")
        
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 100, 500),
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
                'min_child_weight': trial.suggest_int('min_child_weight', 1, 7),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                'gamma': trial.suggest_float('gamma', 0, 5),
                'reg_alpha': trial.suggest_float('reg_alpha', 0, 1),
                'reg_lambda': trial.suggest_float('reg_lambda', 0, 1),
                'random_state': 42,
                'n_jobs': -1,
            }
            
            model = xgb.XGBClassifier(**params)
            
            if use_tscv:
                tscv = TimeSeriesSplit(n_splits=self.cv_folds)
                scores = cross_val_score(model, X_train, y_train, cv=tscv, scoring='accuracy', n_jobs=1)
            else:
                scores = cross_val_score(model, X_train, y_train, cv=self.cv_folds, scoring='accuracy')
            
            return scores.mean()
        
        self.study = optuna.create_study(
            direction='maximize',
            pruner=MedianPruner(n_startup_trials=10, n_warmup_steps=5),
            study_name='xgboost_optimization'
        )
        
        self.study.optimize(
            objective,
            n_trials=self.n_trials,
            timeout=self.timeout,
            show_progress_bar=True
        )
        
        self.logger.info(
            f"XGBoost optimization complete. Best accuracy: {self.study.best_value:.4f}",
            category="ml_training"
        )
        
        return self.study.best_params
    
    def optimize_random_forest(self, X_train, y_train, use_tscv: bool = True) -> Dict[str, Any]:
        """
        Find optimal Random Forest parameters
        
        Args:
            X_train: Training features
            y_train: Training labels
            use_tscv: Use TimeSeriesSplit instead of regular CV
            
        Returns:
            Dict with best parameters
        """
        self.logger.info("Starting Random Forest hyperparameter optimization", category="ml_training")
        
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 100, 500),
                'max_depth': trial.suggest_int('max_depth', 5, 20),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
                'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', None]),
                'random_state': 42,
                'n_jobs': -1,
            }
            
            model = RandomForestClassifier(**params)
            
            if use_tscv:
                tscv = TimeSeriesSplit(n_splits=self.cv_folds)
                scores = cross_val_score(model, X_train, y_train, cv=tscv, scoring='accuracy', n_jobs=1)
            else:
                scores = cross_val_score(model, X_train, y_train, cv=self.cv_folds, scoring='accuracy')
            
            return scores.mean()
        
        self.study = optuna.create_study(
            direction='maximize',
            pruner=MedianPruner(n_startup_trials=10, n_warmup_steps=5),
            study_name='random_forest_optimization'
        )
        
        self.study.optimize(
            objective,
            n_trials=self.n_trials,
            timeout=self.timeout,
            show_progress_bar=True
        )
        
        self.logger.info(
            f"Random Forest optimization complete. Best accuracy: {self.study.best_value:.4f}",
            category="ml_training"
        )
        
        return self.study.best_params
    
    def optimize_lightgbm(self, X_train, y_train, use_tscv: bool = True) -> Optional[Dict[str, Any]]:
        """
        Find optimal LightGBM parameters
        
        Args:
            X_train: Training features
            y_train: Training labels
            use_tscv: Use TimeSeriesSplit instead of regular CV
            
        Returns:
            Dict with best parameters or None if LightGBM not available
        """
        if not LIGHTGBM_AVAILABLE:
            self.logger.warning("LightGBM not available, skipping optimization", category="ml_training")
            return None
        
        self.logger.info("Starting LightGBM hyperparameter optimization", category="ml_training")
        
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 100, 500),
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
                'num_leaves': trial.suggest_int('num_leaves', 20, 100),
                'min_child_samples': trial.suggest_int('min_child_samples', 5, 50),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                'reg_alpha': trial.suggest_float('reg_alpha', 0, 1),
                'reg_lambda': trial.suggest_float('reg_lambda', 0, 1),
                'random_state': 42,
                'n_jobs': -1,
                'verbose': -1,
            }
            
            model = lgb.LGBMClassifier(**params)
            
            if use_tscv:
                tscv = TimeSeriesSplit(n_splits=self.cv_folds)
                scores = cross_val_score(model, X_train, y_train, cv=tscv, scoring='accuracy', n_jobs=1)
            else:
                scores = cross_val_score(model, X_train, y_train, cv=self.cv_folds, scoring='accuracy')
            
            return scores.mean()
        
        self.study = optuna.create_study(
            direction='maximize',
            pruner=MedianPruner(n_startup_trials=10, n_warmup_steps=5),
            study_name='lightgbm_optimization'
        )
        
        self.study.optimize(
            objective,
            n_trials=self.n_trials,
            timeout=self.timeout,
            show_progress_bar=True
        )
        
        self.logger.info(
            f"LightGBM optimization complete. Best accuracy: {self.study.best_value:.4f}",
            category="ml_training"
        )
        
        return self.study.best_params
    
    def optimize_catboost(self, X_train, y_train, use_tscv: bool = True) -> Optional[Dict[str, Any]]:
        """
        Find optimal CatBoost parameters
        
        Args:
            X_train: Training features
            y_train: Training labels
            use_tscv: Use TimeSeriesSplit instead of regular CV
            
        Returns:
            Dict with best parameters or None if CatBoost not available
        """
        if not CATBOOST_AVAILABLE:
            self.logger.warning("CatBoost not available, skipping optimization", category="ml_training")
            return None
        
        self.logger.info("Starting CatBoost hyperparameter optimization", category="ml_training")
        
        def objective(trial):
            params = {
                'iterations': trial.suggest_int('iterations', 100, 500),
                'depth': trial.suggest_int('depth', 3, 10),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
                'l2_leaf_reg': trial.suggest_float('l2_leaf_reg', 1, 10),
                'border_count': trial.suggest_int('border_count', 32, 255),
                'random_state': 42,
                'verbose': False,
                'thread_count': -1,
            }
            
            model = cb.CatBoostClassifier(**params)
            
            if use_tscv:
                tscv = TimeSeriesSplit(n_splits=self.cv_folds)
                scores = cross_val_score(model, X_train, y_train, cv=tscv, scoring='accuracy', n_jobs=1)
            else:
                scores = cross_val_score(model, X_train, y_train, cv=self.cv_folds, scoring='accuracy')
            
            return scores.mean()
        
        self.study = optuna.create_study(
            direction='maximize',
            pruner=MedianPruner(n_startup_trials=10, n_warmup_steps=5),
            study_name='catboost_optimization'
        )
        
        self.study.optimize(
            objective,
            n_trials=self.n_trials,
            timeout=self.timeout,
            show_progress_bar=True
        )
        
        self.logger.info(
            f"CatBoost optimization complete. Best accuracy: {self.study.best_value:.4f}",
            category="ml_training"
        )
        
        return self.study.best_params
    
    def get_optimization_history(self):
        """Get optimization history dataframe"""
        if self.study is None:
            return None
        return self.study.trials_dataframe()
    
    def plot_optimization_history(self):
        """Plot optimization history"""
        if self.study is None:
            self.logger.warning("No study available to plot", category="ml_training")
            return None
        
        try:
            import plotly
            fig = optuna.visualization.plot_optimization_history(self.study)
            return fig
        except Exception as e:
            self.logger.warning(f"Could not plot optimization history: {e}", category="ml_training")
            return None


if __name__ == "__main__":
    # Test hyperparameter tuner
    print("🎯 Testing Hyperparameter Tuner...")
    
    from sklearn.datasets import make_classification
    
    # Create sample data
    X, y = make_classification(n_samples=1000, n_features=20, random_state=42)
    
    tuner = HyperparameterTuner(n_trials=10, cv_folds=3)
    
    # Test XGBoost optimization
    best_params = tuner.optimize_xgboost(X, y)
    print(f"✓ Best XGBoost params: {best_params}")
    
    print("\n✓ Hyperparameter tuner test completed")
