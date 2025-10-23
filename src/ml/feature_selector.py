"""
Feature Selection using SHAP and other methods
Remove redundant/low-importance features to improve model performance
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import shap
from sklearn.feature_selection import SelectKBest, f_classif, RFE, mutual_info_classif
from sklearn.ensemble import RandomForestClassifier
import warnings

from src.utils.logger import get_logger

warnings.filterwarnings('ignore')
logger = get_logger()


class FeatureSelector:
    """
    Advanced feature selection using multiple methods
    
    Methods:
    - SHAP values (TreeExplainer)
    - Correlation-based filtering
    - Recursive Feature Elimination (RFE)
    - Mutual Information
    - Statistical tests (F-test)
    """
    
    def __init__(self):
        """Initialize feature selector"""
        self.logger = logger
        self.selected_features = None
        self.feature_importances = None
    
    def select_by_shap(
        self,
        model: Any,
        X: pd.DataFrame,
        y: pd.Series,
        top_k: int = 50
    ) -> List[str]:
        """
        Select top features by SHAP importance
        
        Args:
            model: Trained tree-based model
            X: Feature matrix
            y: Target vector
            top_k: Number of top features to select
            
        Returns:
            List of selected feature names
        """
        try:
            self.logger.info(f"Selecting top {top_k} features using SHAP", category="ml_training")
            
            # Calculate SHAP values
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X)
            
            # For binary classification, use class 1 SHAP values
            if isinstance(shap_values, list):
                shap_values = shap_values[1]
            
            # Get mean absolute SHAP value for each feature
            importance = np.abs(shap_values).mean(axis=0)
            
            # Create feature importance dict
            self.feature_importances = dict(zip(X.columns, importance))
            
            # Select top K features
            top_features_idx = np.argsort(importance)[-top_k:]
            top_features = X.columns[top_features_idx].tolist()
            
            self.logger.info(f"Selected {len(top_features)} features by SHAP", category="ml_training")
            self.selected_features = top_features
            
            return top_features
            
        except Exception as e:
            self.logger.error(f"Error in SHAP feature selection: {e}", category="ml_training")
            return X.columns.tolist()
    
    def select_by_correlation(
        self,
        X: pd.DataFrame,
        threshold: float = 0.95
    ) -> List[str]:
        """
        Remove highly correlated features
        
        Args:
            X: Feature matrix
            threshold: Correlation threshold (0-1)
            
        Returns:
            List of selected feature names
        """
        try:
            self.logger.info(
                f"Removing features with correlation > {threshold}",
                category="ml_training"
            )
            
            # Calculate correlation matrix
            corr_matrix = X.corr().abs()
            
            # Select upper triangle of correlation matrix
            upper = corr_matrix.where(
                np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
            )
            
            # Find features with correlation greater than threshold
            to_drop = [col for col in upper.columns if any(upper[col] > threshold)]
            
            selected = [col for col in X.columns if col not in to_drop]
            
            self.logger.info(
                f"Removed {len(to_drop)} correlated features, kept {len(selected)}",
                category="ml_training"
            )
            self.selected_features = selected
            
            return selected
            
        except Exception as e:
            self.logger.error(f"Error in correlation filtering: {e}", category="ml_training")
            return X.columns.tolist()
    
    def select_by_rfe(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_features: int = 50
    ) -> List[str]:
        """
        Recursive Feature Elimination with Random Forest
        
        Args:
            X: Feature matrix
            y: Target vector
            n_features: Number of features to select
            
        Returns:
            List of selected feature names
        """
        try:
            self.logger.info(
                f"Selecting {n_features} features using RFE",
                category="ml_training"
            )
            
            # Use Random Forest for RFE
            estimator = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            )
            
            rfe = RFE(estimator, n_features_to_select=n_features, step=5)
            rfe.fit(X, y)
            
            selected = X.columns[rfe.support_].tolist()
            
            self.logger.info(f"Selected {len(selected)} features by RFE", category="ml_training")
            self.selected_features = selected
            
            return selected
            
        except Exception as e:
            self.logger.error(f"Error in RFE: {e}", category="ml_training")
            return X.columns.tolist()[:n_features]
    
    def select_by_mutual_info(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        top_k: int = 50
    ) -> List[str]:
        """
        Select features by mutual information
        
        Args:
            X: Feature matrix
            y: Target vector
            top_k: Number of top features to select
            
        Returns:
            List of selected feature names
        """
        try:
            self.logger.info(
                f"Selecting top {top_k} features by mutual information",
                category="ml_training"
            )
            
            # Calculate mutual information
            mi_scores = mutual_info_classif(X, y, random_state=42)
            
            # Create feature importance dict
            self.feature_importances = dict(zip(X.columns, mi_scores))
            
            # Select top K features
            top_features_idx = np.argsort(mi_scores)[-top_k:]
            selected = X.columns[top_features_idx].tolist()
            
            self.logger.info(
                f"Selected {len(selected)} features by mutual information",
                category="ml_training"
            )
            self.selected_features = selected
            
            return selected
            
        except Exception as e:
            self.logger.error(f"Error in mutual information selection: {e}", category="ml_training")
            return X.columns.tolist()[:top_k]
    
    def select_by_variance(
        self,
        X: pd.DataFrame,
        threshold: float = 0.01
    ) -> List[str]:
        """
        Remove low-variance features
        
        Args:
            X: Feature matrix
            threshold: Minimum variance threshold
            
        Returns:
            List of selected feature names
        """
        try:
            self.logger.info(
                f"Removing features with variance < {threshold}",
                category="ml_training"
            )
            
            # Calculate variance
            variances = X.var()
            
            # Select features with variance above threshold
            selected = variances[variances > threshold].index.tolist()
            
            self.logger.info(
                f"Kept {len(selected)}/{len(X.columns)} features",
                category="ml_training"
            )
            self.selected_features = selected
            
            return selected
            
        except Exception as e:
            self.logger.error(f"Error in variance filtering: {e}", category="ml_training")
            return X.columns.tolist()
    
    def select_combined(
        self,
        model: Any,
        X: pd.DataFrame,
        y: pd.Series,
        top_k: int = 50,
        corr_threshold: float = 0.95
    ) -> List[str]:
        """
        Combined feature selection using multiple methods
        
        Args:
            model: Trained model for SHAP
            X: Feature matrix
            y: Target vector
            top_k: Number of features to select
            corr_threshold: Correlation threshold
            
        Returns:
            List of selected feature names
        """
        self.logger.info("Running combined feature selection", category="ml_training")
        
        # Step 1: Remove low-variance features
        X_var = X[self.select_by_variance(X, threshold=0.001)]
        
        # Step 2: Remove highly correlated features
        X_corr = X_var[self.select_by_correlation(X_var, threshold=corr_threshold)]
        
        # Step 3: Select top features by SHAP
        final_features = self.select_by_shap(model, X_corr, y, top_k=min(top_k, len(X_corr.columns)))
        
        self.logger.info(
            f"Combined selection: {len(X.columns)} → {len(final_features)} features",
            category="ml_training"
        )
        
        return final_features
    
    def get_feature_importances(self) -> Optional[Dict[str, float]]:
        """Get feature importances from last selection"""
        return self.feature_importances


if __name__ == "__main__":
    # Test feature selector
    print("🔍 Testing Feature Selector...")
    
    from sklearn.datasets import make_classification
    from sklearn.ensemble import RandomForestClassifier
    
    # Create sample data with redundant features
    X, y = make_classification(
        n_samples=1000,
        n_features=100,
        n_informative=20,
        n_redundant=30,
        random_state=42
    )
    X = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(100)])
    y = pd.Series(y)
    
    # Train model for SHAP
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    selector = FeatureSelector()
    
    # Test SHAP selection
    shap_features = selector.select_by_shap(model, X, y, top_k=30)
    print(f"✓ SHAP selected {len(shap_features)} features")
    
    # Test correlation filtering
    corr_features = selector.select_by_correlation(X, threshold=0.9)
    print(f"✓ Correlation filtering kept {len(corr_features)} features")
    
    # Test combined selection
    combined_features = selector.select_combined(model, X, y, top_k=30)
    print(f"✓ Combined selection: {len(combined_features)} features")
    
    print("\n✓ Feature selector test completed")
