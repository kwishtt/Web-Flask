"""
==============================================
TEST_DATA.PY - UNIT TESTS CHO DATA PROCESSING
==============================================
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_target_creation():
    """Test tạo target Success"""
    # Sample data
    data = {
        'Budget': [100000000, 50000000, 30000000, 80000000],
        'Revenue': [150000000, 40000000, 90000000, 100000000],
        'Vote Average': [7.5, 6.0, 7.0, 8.0]
    }
    df = pd.DataFrame(data)
    
    # Tính ROI
    df['ROI'] = df['Revenue'] / df['Budget']
    
    # Tạo Success (ROI >= 1 AND Vote Average >= 6.5)
    df['Success'] = ((df['ROI'] >= 1.0) & (df['Vote Average'] >= 6.5)).astype(int)
    
    # Expected results
    expected = [1, 0, 1, 1]  # [1.5, 0.8, 3.0, 1.25] ROI và [7.5, 6.0, 7.0, 8.0] Vote
    
    assert df['Success'].tolist() == expected, "Target creation không đúng!"
    print("✅ Test target creation: PASSED")

def test_no_negative_budget_revenue():
    """Test không có giá trị Budget/Revenue âm"""
    data = {
        'Budget': [100000000, 50000000, -10000000],
        'Revenue': [150000000, -5000000, 90000000]
    }
    df = pd.DataFrame(data)
    
    # Remove negative values
    df_cleaned = df[(df['Budget'] >= 0) & (df['Revenue'] >= 0)]
    
    assert len(df_cleaned) == 1, "Không loại bỏ được giá trị âm!"
    assert df_cleaned['Budget'].min() >= 0
    assert df_cleaned['Revenue'].min() >= 0
    print("✅ Test no negative values: PASSED")

def test_roi_calculation():
    """Test tính ROI chính xác"""
    data = {
        'Budget': [100, 200, 50],
        'Revenue': [150, 300, 100]
    }
    df = pd.DataFrame(data)
    df['ROI'] = df['Revenue'] / df['Budget']
    
    expected_roi = [1.5, 1.5, 2.0]
    
    assert np.allclose(df['ROI'].tolist(), expected_roi), "ROI calculation không đúng!"
    print("✅ Test ROI calculation: PASSED")

def test_missing_value_handling():
    """Test xử lý missing values"""
    data = {
        'Budget': [100000, np.nan, 50000],
        'Revenue': [150000, 75000, np.nan],
        'Vote Average': [7.5, np.nan, 6.8]
    }
    df = pd.DataFrame(data)
    
    # Count missing
    missing_count = df.isnull().sum()
    
    assert missing_count['Budget'] == 1
    assert missing_count['Revenue'] == 1
    assert missing_count['Vote Average'] == 1
    print("✅ Test missing value detection: PASSED")

def test_feature_engineering():
    """Test feature engineering"""
    data = {
        'Budget': [100000000],
        'Revenue': [150000000],
        'Runtime': [120],
        'Vote Average': [7.5],
        'Vote Count': [1000]
    }
    df = pd.DataFrame(data)
    
    # Engineer features
    df['ROI'] = df['Revenue'] / df['Budget']
    df['vote_count_log'] = np.log1p(df['Vote Count'])
    df['budget_vote_interaction'] = df['Budget'] * df['Vote Average']
    df['budget_per_minute'] = df['Budget'] / df['Runtime']
    
    assert 'ROI' in df.columns
    assert 'vote_count_log' in df.columns
    assert df['budget_vote_interaction'].iloc[0] == 100000000 * 7.5
    print("✅ Test feature engineering: PASSED")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("CHẠY UNIT TESTS")
    print("="*60 + "\n")
    
    test_target_creation()
    test_no_negative_budget_revenue()
    test_roi_calculation()
    test_missing_value_handling()
    test_feature_engineering()
    
    print("\n" + "="*60)
    print("TẤT CẢ TESTS ĐÃ PASSED! ✅")
    print("="*60 + "\n")
