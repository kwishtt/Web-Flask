"""
==============================================
PREDICT.PY - DỰ ĐOÁN THÀNH CÔNG PHIM
==============================================
"""

import argparse
import json
import joblib
import pandas as pd
import numpy as np
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_model(model_path):
    """Load mô hình và metadata"""
    logger.info(f"Đang load mô hình từ {model_path}...")
    
    model = joblib.load(model_path)
    
    # Load metadata
    metadata_path = model_path.replace('.pkl', '_metadata.json')
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    logger.info(f"Đã load mô hình: {metadata['model_name']}")
    logger.info(f"F1-Score: {metadata['test_metrics']['f1']:.4f}")
    logger.info(f"Best threshold: {metadata['best_threshold']:.4f}")
    
    return model, metadata

def prepare_input(input_df):
    """Chuẩn bị input data"""
    # Feature engineering giống như trong training
    
    # Date features
    if 'Release Date' in input_df.columns:
        input_df['Release Date'] = pd.to_datetime(input_df['Release Date'], errors='coerce')
        input_df['release_year'] = input_df['Release Date'].dt.year
        input_df['release_month'] = input_df['Release Date'].dt.month
        input_df['release_weekday'] = input_df['Release Date'].dt.weekday
        
        def get_season(month):
            if pd.isna(month):
                return 0
            if month in [12, 1, 2]:
                return 1
            elif month in [3, 4, 5]:
                return 2
            elif month in [6, 7, 8]:
                return 3
            else:
                return 4
        
        input_df['release_season'] = input_df['release_month'].apply(get_season)
        input_df['is_holiday_release'] = input_df['release_month'].apply(
            lambda x: 1 if x in [6, 7, 8, 12, 1, 2] else 0 if pd.notna(x) else 0
        )
    
    # ROI
    if 'Budget' in input_df.columns and 'Revenue' in input_df.columns:
        input_df['ROI'] = input_df['Revenue'] / (input_df['Budget'] + 1)
    
    # Popularity
    if 'Vote Count' in input_df.columns:
        input_df['vote_count_log'] = np.log1p(input_df['Vote Count'])
    
    # Interactions
    if 'Budget' in input_df.columns and 'Vote Average' in input_df.columns:
        input_df['budget_vote_interaction'] = input_df['Budget'] * input_df['Vote Average']
    
    if 'Budget' in input_df.columns and 'Runtime' in input_df.columns:
        input_df['budget_per_minute'] = input_df['Budget'] / (input_df['Runtime'] + 1)
    
    # Missing flags
    for col in ['Budget', 'Revenue', 'Runtime', 'Vote Average']:
        if col in input_df.columns:
            input_df[f'is_missing_{col.lower().replace(" ", "_")}'] = input_df[col].isnull().astype(int)
    
    return input_df

def predict(model, input_df, threshold=0.5):
    """Thực hiện dự đoán"""
    # Predict probability
    pred_proba = model.predict_proba(input_df)[:, 1]
    
    # Apply threshold
    predictions = (pred_proba >= threshold).astype(int)
    
    return predictions, pred_proba

def main():
    parser = argparse.ArgumentParser(description='Dự đoán thành công phim')
    parser.add_argument('--model', type=str, required=True, help='Đường dẫn đến model file')
    parser.add_argument('--input', type=str, required=True, help='Đường dẫn đến input CSV')
    parser.add_argument('--output', type=str, required=True, help='Đường dẫn output CSV')
    parser.add_argument('--threshold', type=float, default=None, help='Threshold tùy chỉnh')
    
    args = parser.parse_args()
    
    try:
        # Load model
        model, metadata = load_model(args.model)
        
        # Load input
        logger.info(f"Đang load input từ {args.input}...")
        input_df = pd.read_csv(args.input)
        logger.info(f"Đã load {len(input_df)} hàng")
        
        # Prepare input
        input_df = prepare_input(input_df)
        
        # Predict
        threshold = args.threshold if args.threshold is not None else metadata['best_threshold']
        logger.info(f"Thực hiện dự đoán với threshold = {threshold:.4f}...")
        
        predictions, probabilities = predict(model, input_df, threshold)
        
        # Add results to dataframe
        input_df['prediction'] = predictions
        input_df['prediction_label'] = input_df['prediction'].map({0: 'Thất bại', 1: 'Thành công'})
        input_df['success_probability'] = probabilities
        
        # Save output
        input_df.to_csv(args.output, index=False, encoding='utf-8')
        logger.info(f"Đã lưu kết quả vào {args.output}")
        
        # Statistics
        success_count = predictions.sum()
        logger.info(f"\nThống kê:")
        logger.info(f"- Dự đoán Thành công: {success_count} ({success_count/len(predictions)*100:.1f}%)")
        logger.info(f"- Dự đoán Thất bại: {len(predictions)-success_count} ({(len(predictions)-success_count)/len(predictions)*100:.1f}%)")
        
    except Exception as e:
        logger.error(f"Lỗi: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
