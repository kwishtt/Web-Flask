"""
==============================================
TRAIN.PY - HUẤN LUYỆN MÔ HÌNH DỰ ĐOÁN THÀNH CÔNG PHIM
==============================================
"""

import os
import sys
import yaml
import json
import joblib
import logging
import hashlib
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, 
    average_precision_score, roc_curve, precision_recall_curve,
    f1_score, precision_score, recall_score
)

import xgboost as xgb
import lightgbm as lgb
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import shap

warnings.filterwarnings('ignore')

# ==============================================
# LOGGER SETUP
# ==============================================

def setup_logger(config):
    """Thiết lập logging"""
    logging.basicConfig(
        level=getattr(logging, config['logging']['level']),
        format=config['logging']['format']
    )
    return logging.getLogger(__name__)

# ==============================================
# DATA LOADING & VALIDATION
# ==============================================

def calculate_file_hash(filepath):
    """Tính SHA256 hash của file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def validate_data(df, logger):
    """Kiểm tra dữ liệu đầu vào"""
    required_cols = [
        'Budget', 'Revenue', 'Runtime', 'Release Date', 'Vote Average', 
        'Vote Count', 'Genres', 'Production Countries', 'Spoken Languages'
    ]
    
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Thiếu các cột bắt buộc: {missing_cols}")
    
    # Kiểm tra giá trị âm
    negative_budget = (df['Budget'] < 0).sum()
    negative_revenue = (df['Revenue'] < 0).sum()
    
    if negative_budget > 0:
        logger.warning(f"Phát hiện {negative_budget} giá trị Budget âm")
    if negative_revenue > 0:
        logger.warning(f"Phát hiện {negative_revenue} giá trị Revenue âm")
    
    # Log missing values
    logger.info("\n=== Thống kê Missing Values ===")
    missing_stats = df[required_cols].isnull().sum()
    missing_pct = (missing_stats / len(df)) * 100
    
    for col in required_cols:
        if missing_stats[col] > 0:
            logger.info(f"{col}: {missing_stats[col]} ({missing_pct[col]:.2f}%)")
    
    return True

def load_and_clean_data(config, logger):
    """Load và làm sạch dữ liệu"""
    logger.info(f"Đang load dữ liệu từ {config['data']['path']}...")
    
    df = pd.read_csv(config['data']['path'])
    logger.info(f"Đã load {len(df)} hàng")
    
    # Validate
    validate_data(df, logger)
    
    # Xóa giá trị âm
    df = df[(df['Budget'] >= 0) & (df['Revenue'] >= 0)]
    
    # Xử lý Budget và Revenue = 0
    zero_budget = (df['Budget'] == 0).sum()
    zero_revenue = (df['Revenue'] == 0).sum()
    
    logger.info(f"Số hàng với Budget=0: {zero_budget}")
    logger.info(f"Số hàng với Revenue=0: {zero_revenue}")
    
    # Drop nếu Budget hoặc Revenue = 0
    df = df[(df['Budget'] > 0) & (df['Revenue'] > 0)]
    logger.info(f"Sau khi xóa Budget/Revenue = 0: {len(df)} hàng")
    
    return df

# ==============================================
# TARGET CREATION
# ==============================================

def create_target(df, config, logger):
    """Tạo biến target Success"""
    logger.info("\n=== Tạo Target Variable ===")
    
    # Tính ROI
    df['ROI'] = df['Revenue'] / df['Budget']
    
    # Tạo Success label
    roi_threshold = config['preprocessing']['roi_threshold']
    vote_threshold = config['preprocessing']['vote_average_threshold']
    
    df['Success'] = (
        (df['ROI'] >= roi_threshold) & 
        (df['Vote Average'] >= vote_threshold)
    ).astype(int)
    
    success_count = df['Success'].sum()
    failure_count = len(df) - success_count
    imbalance_ratio = failure_count / success_count if success_count > 0 else 0
    
    logger.info(f"ROI Threshold: {roi_threshold}")
    logger.info(f"Vote Average Threshold: {vote_threshold}")
    logger.info(f"Success: {success_count} ({success_count/len(df)*100:.2f}%)")
    logger.info(f"Failure: {failure_count} ({failure_count/len(df)*100:.2f}%)")
    logger.info(f"Imbalance Ratio: {imbalance_ratio:.2f}")
    
    # Lưu sample
    sample_df = df[['Title', 'Budget', 'Revenue', 'ROI', 'Vote Average', 'Success']].head(10)
    os.makedirs(config['output']['reports_dir'], exist_ok=True)
    sample_df.to_csv(f"{config['output']['reports_dir']}/sample_with_labels.csv", index=False)
    logger.info(f"Đã lưu sample data vào reports/sample_with_labels.csv")
    
    return df

# ==============================================
# FEATURE ENGINEERING
# ==============================================

def engineer_features(df, logger):
    """Feature engineering"""
    logger.info("\n=== Feature Engineering ===")
    
    # Date features
    df['Release Date'] = pd.to_datetime(df['Release Date'], errors='coerce')
    df['release_year'] = df['Release Date'].dt.year
    df['release_month'] = df['Release Date'].dt.month
    df['release_weekday'] = df['Release Date'].dt.weekday
    
    # Season
    def get_season(month):
        if pd.isna(month):
            return 0
        if month in [12, 1, 2]:
            return 1  # Winter
        elif month in [3, 4, 5]:
            return 2  # Spring
        elif month in [6, 7, 8]:
            return 3  # Summer
        else:
            return 4  # Fall
    
    df['release_season'] = df['release_month'].apply(get_season)
    
    # Holiday release (summer = Jun-Aug, winter = Dec-Feb)
    df['is_holiday_release'] = df['release_month'].apply(
        lambda x: 1 if x in [6, 7, 8, 12, 1, 2] else 0 if pd.notna(x) else 0
    )
    
    # Popularity proxies
    df['vote_count_log'] = np.log1p(df['Vote Count'])
    
    # Interactions
    df['budget_vote_interaction'] = df['Budget'] * df['Vote Average']
    df['budget_per_minute'] = df['Budget'] / (df['Runtime'] + 1)
    
    # Missing flags
    for col in ['Budget', 'Revenue', 'Runtime', 'Vote Average']:
        df[f'is_missing_{col.lower().replace(" ", "_")}'] = df[col].isnull().astype(int)
    
    logger.info(f"Đã tạo {df.shape[1]} features tổng cộng")
    
    return df

# ==============================================
# PREPROCESSING PIPELINE
# ==============================================

def create_preprocessing_pipeline(X_train, config, logger):
    """Tạo preprocessing pipeline"""
    logger.info("\n=== Tạo Preprocessing Pipeline ===")
    
    # Numeric features
    numeric_features = [
        'Budget', 'Revenue', 'Runtime', 'Vote Average', 'Vote Count', 'ROI',
        'release_year', 'release_month', 'release_weekday', 'release_season',
        'vote_count_log', 'budget_vote_interaction', 'budget_per_minute'
    ]
    
    # Categorical features
    categorical_features = ['Production Countries', 'Spoken Languages']
    
    # Chọn scaler
    if config['preprocessing']['scaling']['method'] == 'minmax':
        scaler = MinMaxScaler()
    else:
        scaler = StandardScaler()
    
    # Numeric pipeline
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy=config['preprocessing']['imputation_strategy'])),
        ('scaler', scaler)
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
        ],
        remainder='drop'
    )
    
    logger.info(f"Numeric features: {len(numeric_features)}")
    logger.info(f"Categorical features: {len(categorical_features)}")
    
    return preprocessor, numeric_features, categorical_features

# ==============================================
# MODEL TRAINING
# ==============================================

def train_model(X_train, y_train, model_name, config, logger):
    """Train một mô hình với hyperparameter tuning"""
    logger.info(f"\n=== Training {model_name.upper()} ===")
    
    model_config = config['models'][model_name]
    
    if not model_config['enabled']:
        logger.info(f"{model_name} bị disabled, bỏ qua")
        return None
    
    # Chọn model
    if model_name == 'logistic_regression':
        model = LogisticRegression(**model_config['params'], random_state=config['random_state'])
    elif model_name == 'random_forest':
        model = RandomForestClassifier(**model_config['params'], random_state=config['random_state'])
    elif model_name == 'xgboost':
        model = xgb.XGBClassifier(**model_config['params'], random_state=config['random_state'])
    elif model_name == 'lightgbm':
        model = lgb.LGBMClassifier(**model_config['params'], random_state=config['random_state'])
    else:
        raise ValueError(f"Unknown model: {model_name}")
    
    # Cross-validation
    cv = StratifiedKFold(
        n_splits=config['tuning']['cv_folds'],
        shuffle=True,
        random_state=config['random_state']
    )
    
    # Hyperparameter search
    if config['tuning']['method'] == 'grid':
        search = GridSearchCV(
            model,
            model_config['param_grid'],
            cv=cv,
            scoring=config['tuning']['scoring'],
            n_jobs=-1,
            verbose=1
        )
    else:
        search = RandomizedSearchCV(
            model,
            model_config['param_grid'],
            n_iter=config['tuning']['n_iter'],
            cv=cv,
            scoring=config['tuning']['scoring'],
            n_jobs=-1,
            random_state=config['random_state'],
            verbose=1
        )
    
    # Train
    logger.info(f"Bắt đầu hyperparameter tuning với {config['tuning']['cv_folds']}-fold CV...")
    search.fit(X_train, y_train)
    
    logger.info(f"Best {config['tuning']['scoring']}: {search.best_score_:.4f}")
    logger.info(f"Best params: {search.best_params_}")
    
    return search.best_estimator_, search.best_params_, search.best_score_

# ==============================================
# EVALUATION
# ==============================================

def evaluate_model(model, X_test, y_test, model_name, config, logger):
    """Đánh giá mô hình"""
    logger.info(f"\n=== Đánh giá {model_name.upper()} ===")
    
    # Predict
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Metrics
    metrics = {
        'accuracy': (y_pred == y_test).mean(),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'roc_auc': roc_auc_score(y_test, y_pred_proba),
        'pr_auc': average_precision_score(y_test, y_pred_proba)
    }
    
    logger.info(f"Accuracy: {metrics['accuracy']:.4f}")
    logger.info(f"Precision: {metrics['precision']:.4f}")
    logger.info(f"Recall: {metrics['recall']:.4f}")
    logger.info(f"F1-Score: {metrics['f1']:.4f}")
    logger.info(f"ROC-AUC: {metrics['roc_auc']:.4f}")
    logger.info(f"PR-AUC: {metrics['pr_auc']:.4f}")
    
    # Classification report
    logger.info("\n" + classification_report(y_test, y_pred, target_names=['Failure', 'Success']))
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    
    return metrics, cm, y_pred, y_pred_proba

# ==============================================
# THRESHOLD OPTIMIZATION
# ==============================================

def optimize_threshold(y_test, y_pred_proba, config, logger):
    """Tối ưu threshold dựa trên F1-score"""
    logger.info("\n=== Tối ưu Threshold ===")
    
    if not config['threshold_optimization']['enabled']:
        logger.info("Threshold optimization bị disabled")
        return 0.5
    
    thresholds = np.arange(
        config['threshold_optimization']['range'][0],
        config['threshold_optimization']['range'][1],
        config['threshold_optimization']['step']
    )
    
    best_threshold = 0.5
    best_score = 0
    
    for threshold in thresholds:
        y_pred_thresh = (y_pred_proba >= threshold).astype(int)
        score = f1_score(y_test, y_pred_thresh)
        
        if score > best_score:
            best_score = score
            best_threshold = threshold
    
    logger.info(f"Best threshold: {best_threshold:.2f}")
    logger.info(f"Best F1-score: {best_score:.4f}")
    
    return best_threshold

# ==============================================
# VISUALIZATION
# ==============================================

def plot_confusion_matrix(cm, model_name, output_dir):
    """Vẽ confusion matrix"""
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Thất bại', 'Thành công'],
                yticklabels=['Thất bại', 'Thành công'])
    plt.title(f'Ma trận nhầm lẫn - {model_name}')
    plt.ylabel('Thực tế')
    plt.xlabel('Dự đoán')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/confusion_matrix_{model_name}.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_roc_curve(y_test, y_pred_proba, model_name, output_dir):
    """Vẽ ROC curve"""
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    auc = roc_auc_score(y_test, y_pred_proba)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f'{model_name} (AUC = {auc:.3f})', linewidth=2)
    plt.plot([0, 1], [0, 1], 'k--', label='Ngẫu nhiên')
    plt.xlabel('Tỷ lệ dương tính giả (FPR)')
    plt.ylabel('Tỷ lệ dương tính thật (TPR)')
    plt.title(f'Đường cong ROC - {model_name}')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/roc_curve_{model_name}.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_pr_curve(y_test, y_pred_proba, model_name, output_dir):
    """Vẽ Precision-Recall curve"""
    precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
    ap = average_precision_score(y_test, y_pred_proba)
    
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, label=f'{model_name} (AP = {ap:.3f})', linewidth=2)
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title(f'Đường cong Precision-Recall - {model_name}')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/pr_curve_{model_name}.png", dpi=300, bbox_inches='tight')
    plt.close()

# ==============================================
# FEATURE IMPORTANCE & SHAP
# ==============================================

def analyze_feature_importance(model, feature_names, model_name, output_dir, logger):
    """Phân tích feature importance"""
    logger.info(f"\n=== Feature Importance - {model_name} ===")
    
    # Lấy feature importance
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    elif hasattr(model, 'coef_'):
        importances = np.abs(model.coef_[0])
    else:
        logger.warning(f"{model_name} không hỗ trợ feature importance")
        return
    
    # Tạo DataFrame
    feature_importance_df = pd.DataFrame({
        'feature': feature_names[:len(importances)],
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    # Lưu CSV
    feature_importance_df.to_csv(f"{output_dir}/feature_importance_{model_name}.csv", index=False)
    
    # Log top 10
    logger.info("\nTop 10 Features quan trọng nhất:")
    for idx, row in feature_importance_df.head(10).iterrows():
        logger.info(f"{row['feature']}: {row['importance']:.4f}")
    
    # Plot
    plt.figure(figsize=(10, 8))
    top_features = feature_importance_df.head(20)
    plt.barh(range(len(top_features)), top_features['importance'])
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('Importance')
    plt.title(f'Top 20 Features - {model_name}')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/feature_importance_{model_name}.png", dpi=300, bbox_inches='tight')
    plt.close()

def create_shap_analysis(model, X_test, feature_names, model_name, output_dir, logger):
    """Tạo SHAP analysis"""
    logger.info(f"\n=== SHAP Analysis - {model_name} ===")
    
    try:
        # Chọn explainer phù hợp
        if model_name in ['xgboost', 'lightgbm', 'random_forest']:
            explainer = shap.TreeExplainer(model)
        else:
            # Giới hạn số lượng mẫu cho KernelExplainer
            X_sample = X_test[:100] if len(X_test) > 100 else X_test
            explainer = shap.KernelExplainer(model.predict_proba, X_sample)
        
        # Tính SHAP values
        shap_values = explainer.shap_values(X_test[:100])
        
        # Nếu là binary classification, lấy class 1
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        # Summary plot
        plt.figure(figsize=(10, 8))
        shap.summary_plot(shap_values, X_test[:100], feature_names=feature_names, show=False)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/shap_summary_{model_name}.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Đã lưu SHAP summary plot")
        
    except Exception as e:
        logger.error(f"Lỗi khi tạo SHAP analysis: {str(e)}")

# ==============================================
# MAIN TRAINING FUNCTION
# ==============================================

def main():
    """Main training function"""
    
    # Load config
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Setup logger
    logger = setup_logger(config)
    logger.info("=" * 60)
    logger.info("BẮT ĐẦU HUẤN LUYỆN MÔ HÌNH DỰ ĐOÁN THÀNH CÔNG PHIM")
    logger.info("=" * 60)
    
    # Tạo thư mục output
    os.makedirs(config['output']['models_dir'], exist_ok=True)
    os.makedirs(config['output']['reports_dir'], exist_ok=True)
    os.makedirs(config['output']['plots_dir'], exist_ok=True)
    
    # Load data
    df = load_and_clean_data(config, logger)
    data_hash = calculate_file_hash(config['data']['path'])
    logger.info(f"Dataset SHA256: {data_hash[:16]}...")
    
    # Create target
    df = create_target(df, config, logger)
    
    # Feature engineering
    df = engineer_features(df, logger)
    
    # Prepare features
    feature_cols = [col for col in df.columns if col not in ['Success', 'Title', 'Overview', 'Release Date']]
    X = df[feature_cols]
    y = df['Success']
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=config['preprocessing']['test_size'],
        stratify=y,
        random_state=config['random_state']
    )
    
    logger.info(f"\nTrain: {len(X_train)}, Test: {len(X_test)}")
    
    # Create preprocessing pipeline
    preprocessor, numeric_features, categorical_features = create_preprocessing_pipeline(X_train, config, logger)
    
    # Fit preprocessor
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    
    # Get feature names after preprocessing
    feature_names = numeric_features + list(preprocessor.named_transformers_['cat']
                                           .named_steps['onehot']
                                           .get_feature_names_out(categorical_features))
    
    logger.info(f"Tổng số features sau preprocessing: {len(feature_names)}")
    
    # Apply SMOTE if enabled
    if config['imbalance']['method'] in ['smote', 'both']:
        logger.info("\n=== Applying SMOTE ===")
        smote = SMOTE(random_state=config['random_state'])
        X_train_processed, y_train = smote.fit_resample(X_train_processed, y_train)
        logger.info(f"Sau SMOTE - Train: {len(X_train_processed)}")
    
    # Train models
    results = {}
    
    for model_name in ['logistic_regression', 'random_forest', 'xgboost', 'lightgbm']:
        if not config['models'][model_name]['enabled']:
            continue
        
        try:
            # Train
            model, best_params, best_score = train_model(
                X_train_processed, y_train, model_name, config, logger
            )
            
            # Evaluate
            metrics, cm, y_pred, y_pred_proba = evaluate_model(
                model, X_test_processed, y_test, model_name, config, logger
            )
            
            # Optimize threshold
            best_threshold = optimize_threshold(y_test, y_pred_proba, config, logger)
            
            # Save results
            results[model_name] = {
                'model': model,
                'metrics': metrics,
                'best_params': best_params,
                'best_cv_score': best_score,
                'best_threshold': best_threshold,
                'confusion_matrix': cm.tolist()
            }
            
            # Plots
            plot_confusion_matrix(cm, model_name, config['output']['plots_dir'])
            plot_roc_curve(y_test, y_pred_proba, model_name, config['output']['plots_dir'])
            plot_pr_curve(y_test, y_pred_proba, model_name, config['output']['plots_dir'])
            
            # Feature importance
            analyze_feature_importance(model, feature_names, model_name, 
                                     config['output']['reports_dir'], logger)
            
            # SHAP
            create_shap_analysis(model, X_test_processed, feature_names, 
                               model_name, config['output']['plots_dir'], logger)
            
        except Exception as e:
            logger.error(f"Lỗi khi train {model_name}: {str(e)}")
            continue
    
    # Select best model
    best_model_name = max(results, key=lambda x: results[x]['metrics']['f1'])
    best_model = results[best_model_name]['model']
    
    logger.info("\n" + "=" * 60)
    logger.info(f"MÔ HÌNH TỐT NHẤT: {best_model_name.upper()}")
    logger.info(f"F1-Score: {results[best_model_name]['metrics']['f1']:.4f}")
    logger.info("=" * 60)
    
    # Save best model
    logger.info("\n=== Lưu mô hình tốt nhất ===")
    
    # Save full pipeline
    full_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', best_model)
    ])
    
    joblib.dump(full_pipeline, f"{config['output']['models_dir']}/best_model.pkl")
    logger.info(f"Đã lưu: models/best_model.pkl")
    
    # Save metadata
    metadata = {
        'model_name': best_model_name,
        'hyperparameters': results[best_model_name]['best_params'],
        'cv_score': results[best_model_name]['best_cv_score'],
        'test_metrics': results[best_model_name]['metrics'],
        'best_threshold': results[best_model_name]['best_threshold'],
        'features': feature_names,
        'random_state': config['random_state'],
        'training_date': datetime.now().isoformat(),
        'dataset_hash': data_hash,
        'config': config
    }
    
    with open(f"{config['output']['models_dir']}/best_model_metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Đã lưu: models/best_model_metadata.json")
    
    # Generate evaluation report
    generate_evaluation_report(results, best_model_name, config, logger)
    
    logger.info("\n" + "=" * 60)
    logger.info("HOÀN THÀNH!")
    logger.info("=" * 60)

def generate_evaluation_report(results, best_model_name, config, logger):
    """Tạo báo cáo đánh giá"""
    report_path = f"{config['output']['reports_dir']}/evaluation_report.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# BÁO CÁO ĐÁNH GIÁ MÔ HÌNH DỰ ĐOÁN THÀNH CÔNG PHIM\n\n")
        f.write(f"**Ngày tạo:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 1. Tổng quan\n\n")
        f.write(f"- **Mô hình tốt nhất:** {best_model_name}\n")
        f.write(f"- **F1-Score:** {results[best_model_name]['metrics']['f1']:.4f}\n")
        f.write(f"- **ROC-AUC:** {results[best_model_name]['metrics']['roc_auc']:.4f}\n\n")
        
        f.write("## 2. So sánh các mô hình\n\n")
        f.write("| Mô hình | F1-Score | Precision | Recall | ROC-AUC |\n")
        f.write("|---------|----------|-----------|--------|----------|\n")
        
        for model_name, result in results.items():
            metrics = result['metrics']
            f.write(f"| {model_name} | {metrics['f1']:.4f} | {metrics['precision']:.4f} | ")
            f.write(f"{metrics['recall']:.4f} | {metrics['roc_auc']:.4f} |\n")
        
        f.write("\n## 3. Hyperparameters của mô hình tốt nhất\n\n")
        f.write("```json\n")
        f.write(json.dumps(results[best_model_name]['best_params'], indent=2))
        f.write("\n```\n\n")
        
        f.write("## 4. Kết luận & Khuyến nghị\n\n")
        
        best_f1 = results[best_model_name]['metrics']['f1']
        if best_f1 >= 0.75:
            f.write(f"✅ Mô hình đạt ngưỡng chấp nhận (F1 ≥ 0.75)\n\n")
        else:
            f.write(f"⚠️ Mô hình chưa đạt ngưỡng mong muốn (F1 = {best_f1:.4f} < 0.75)\n\n")
            f.write("### Đề xuất cải thiện:\n\n")
            f.write("1. Thu thập thêm dữ liệu training\n")
            f.write("2. Thêm features từ text (Overview, Title) bằng embeddings\n")
            f.write("3. Thử ensemble methods (stacking, blending)\n")
            f.write("4. Điều chỉnh threshold để cân bằng precision/recall\n")
    
    logger.info(f"Đã lưu báo cáo: {report_path}")

if __name__ == "__main__":
    main()
