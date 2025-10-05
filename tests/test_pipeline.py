"""
==============================================
TEST_PIPELINE.PY - UNIT TESTS CHO ML PIPELINE
==============================================
"""

import pytest
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def test_numeric_pipeline():
    """Test numeric preprocessing pipeline"""
    # Sample data
    data = {
        'Budget': [100000000, np.nan, 50000000],
        'Revenue': [150000000, 75000000, np.nan],
        'Runtime': [120, 110, 130]
    }
    df = pd.DataFrame(data)
    
    # Create pipeline
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', MinMaxScaler())
    ])
    
    # Transform
    result = numeric_transformer.fit_transform(df)
    
    # Checks
    assert result.shape[0] == 3, "Số hàng không đúng!"
    assert result.shape[1] == 3, "Số cột không đúng!"
    assert not np.isnan(result).any(), "Vẫn còn missing values!"
    print("✅ Test numeric pipeline: PASSED")

def test_categorical_pipeline():
    """Test categorical preprocessing pipeline"""
    # Sample data
    data = {
        'Country': ['Vietnam', 'USA', 'Vietnam'],
        'Language': ['Vietnamese', 'English', 'Vietnamese']
    }
    df = pd.DataFrame(data)
    
    # Create pipeline
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    # Transform
    result = categorical_transformer.fit_transform(df)
    
    # Checks
    assert result.shape[0] == 3
    assert result.shape[1] > 2  # Sau one-hot encoding
    print("✅ Test categorical pipeline: PASSED")

def test_full_preprocessor():
    """Test full column transformer"""
    # Sample data
    data = {
        'Budget': [100000000, 50000000, 75000000],
        'Revenue': [150000000, 40000000, 90000000],
        'Country': ['Vietnam', 'USA', 'Vietnam']
    }
    df = pd.DataFrame(data)
    
    numeric_features = ['Budget', 'Revenue']
    categorical_features = ['Country']
    
    # Numeric pipeline
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', MinMaxScaler())
    ])
    
    # Categorical pipeline
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    # Combine
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )
    
    # Transform
    result = preprocessor.fit_transform(df)
    
    # Checks
    assert result.shape[0] == 3
    assert result.shape[1] >= 4  # 2 numeric + at least 2 from one-hot
    print("✅ Test full preprocessor: PASSED")

def test_pipeline_with_missing_values():
    """Test pipeline xử lý missing values"""
    data = {
        'Budget': [100000000, np.nan, 50000000],
        'Revenue': [np.nan, 75000000, 90000000],
        'Country': ['Vietnam', None, 'USA']
    }
    df = pd.DataFrame(data)
    
    numeric_features = ['Budget', 'Revenue']
    categorical_features = ['Country']
    
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )
    
    result = preprocessor.fit_transform(df)
    
    # Không được có NaN sau preprocessing
    assert not np.isnan(result).any(), "Pipeline không xử lý hết missing values!"
    print("✅ Test pipeline with missing values: PASSED")

def test_transform_shape_consistency():
    """Test consistency của output shape"""
    # Train data
    train_data = {
        'Budget': [100000000, 50000000, 75000000, 60000000],
        'Revenue': [150000000, 40000000, 90000000, 70000000],
        'Country': ['Vietnam', 'USA', 'France', 'Vietnam']
    }
    train_df = pd.DataFrame(train_data)
    
    # Test data (với country mới)
    test_data = {
        'Budget': [80000000, 55000000],
        'Revenue': [95000000, 60000000],
        'Country': ['Japan', 'USA']  # Japan là mới
    }
    test_df = pd.DataFrame(test_data)
    
    numeric_features = ['Budget', 'Revenue']
    categorical_features = ['Country']
    
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', MinMaxScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )
    
    # Fit on train, transform both
    train_result = preprocessor.fit_transform(train_df)
    test_result = preprocessor.transform(test_df)
    
    # Shape consistency check
    assert train_result.shape[1] == test_result.shape[1], \
        f"Shape không nhất quán! Train: {train_result.shape[1]}, Test: {test_result.shape[1]}"
    
    print("✅ Test transform shape consistency: PASSED")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("CHẠY PIPELINE TESTS")
    print("="*60 + "\n")
    
    test_numeric_pipeline()
    test_categorical_pipeline()
    test_full_preprocessor()
    test_pipeline_with_missing_values()
    test_transform_shape_consistency()
    
    print("\n" + "="*60)
    print("TẤT CẢ PIPELINE TESTS ĐÃ PASSED! ✅")
    print("="*60 + "\n")
