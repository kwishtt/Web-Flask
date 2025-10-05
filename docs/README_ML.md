# ==============================================
# README - HỆ THỐNG DỰ ĐOÁN THÀNH CÔNG PHIM
# ==============================================

## 📋 Tổng quan

Hệ thống Machine Learning dự đoán khả năng thành công của phim điện ảnh dựa trên:
- Ngân sách (Budget)
- Doanh thu (Revenue) 
- ROI (Return on Investment)
- Đánh giá (Vote Average)
- Thể loại, quốc gia sản xuất, và nhiều yếu tố khác

**Tiêu chí thành công:** ROI ≥ 1.0 VÀ Vote Average ≥ 6.5

## 🎯 Mô hình đã thử nghiệm

1. **Logistic Regression** (baseline)
2. **Random Forest**
3. **XGBoost** ⭐
4. **LightGBM** ⭐

## 🚀 Cài đặt

### 1. Yêu cầu hệ thống
- Python >= 3.10
- RAM >= 8GB (khuyến nghị cho XGBoost/LightGBM)

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Chuẩn bị dữ liệu

Đặt file `Movies.csv` vào thư mục `data/`:
```
data/
└── Movies.csv
```

## 📊 Huấn luyện mô hình

### Cách 1: Sử dụng script

```bash
chmod +x train.sh
./train.sh
```

### Cách 2: Chạy trực tiếp

```bash
python3 train.py
```

### Cách 3: Tùy chỉnh config

Chỉnh sửa `config.yaml` theo nhu cầu, sau đó:

```bash
python3 train.py
```

## 🔮 Dự đoán

### Dự đoán từ file CSV

```bash
python3 predict.py \
    --model models/best_model.pkl \
    --input sample_inputs.csv \
    --output predictions.csv \
    --threshold 0.47
```

### Format input CSV

```csv
Title,Budget,Revenue,Runtime,Vote Average,Vote Count,Genres,Production Countries,Spoken Languages,Release Date
Avatar 2,350000000,2000000000,192,7.8,5000,Action|Adventure|Science Fiction,United States of America,English,2022-12-16
```

## 🧪 Chạy tests

```bash
# Chạy tất cả tests
pytest tests/

# Chạy specific test
python3 tests/test_data.py
python3 tests/test_pipeline.py

# Chạy với coverage
pytest tests/ --cov=. --cov-report=html
```

## 📁 Cấu trúc dự án

```
.
├── config.yaml                 # Cấu hình ML pipeline
├── train.py                    # Script huấn luyện chính
├── predict.py                  # Script dự đoán
├── train.sh                    # Shell script tiện lợi
├── requirements.txt            # Dependencies
├── README.md                   # Tài liệu này
│
├── data/
│   └── Movies.csv             # Dataset gốc
│
├── models/
│   ├── best_model.pkl         # Mô hình tốt nhất (saved)
│   └── best_model_metadata.json  # Metadata & metrics
│
├── reports/
│   ├── evaluation_report.md   # Báo cáo đánh giá
│   ├── sample_with_labels.csv # Sample data với labels
│   ├── feature_importance_*.csv
│   └── plots/
│       ├── confusion_matrix_*.png
│       ├── roc_curve_*.png
│       ├── pr_curve_*.png
│       ├── shap_summary_*.png
│       └── feature_importance_*.png
│
├── tests/
│   ├── test_data.py           # Unit tests cho data
│   └── test_pipeline.py       # Unit tests cho pipeline
│
└── web/                       # Web application (Flask)
    ├── static/
    │   ├── css/
    │   └── js/
    └── templates/
```

## ⚙️ Cấu hình (config.yaml)

### Các tham số quan trọng:

**Preprocessing:**
```yaml
preprocessing:
  roi_threshold: 1.0              # Ngưỡng ROI cho Success
  vote_average_threshold: 6.5     # Ngưỡng Vote Average
  scaling:
    method: "minmax"              # minmax hoặc standard
```

**Models:**
```yaml
models:
  xgboost:
    enabled: true
    param_grid:
      n_estimators: [100, 300, 500]
      max_depth: [3, 6, 10]
      learning_rate: [0.01, 0.05, 0.1]
```

**Hyperparameter Tuning:**
```yaml
tuning:
  method: "grid"      # grid, random, hoặc optuna
  cv_folds: 5
  scoring: "f1"       # f1, precision, recall, roc_auc
```

**Imbalance Handling:**
```yaml
imbalance:
  method: "smote"     # smote, class_weight, both, none
```

## 📈 Kết quả đầu ra

### 1. Mô hình (models/)
- `best_model.pkl`: Mô hình đã train (full pipeline)
- `best_model_metadata.json`: Thông tin chi tiết

### 2. Báo cáo (reports/)
- `evaluation_report.md`: Báo cáo tổng hợp
- `feature_importance_*.csv`: Độ quan trọng của features
- `sample_with_labels.csv`: 10 samples với labels

### 3. Biểu đồ (reports/plots/)
- Confusion Matrix
- ROC Curve & PR Curve
- Feature Importance plot
- SHAP summary & force plots

## 🎓 Metrics đánh giá

- **F1-Score**: Mục tiêu chính (≥ 0.75)
- **Precision**: Độ chính xác dự đoán thành công
- **Recall**: Khả năng phát hiện phim thành công
- **ROC-AUC**: Đánh giá tổng thể
- **PR-AUC**: Đánh giá với imbalanced data

## 🔧 Troubleshooting

### Lỗi "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Lỗi "Out of Memory"
- Giảm `n_estimators` trong config
- Giảm `cv_folds` xuống 3
- Sử dụng `tuning.method: "random"` với `n_iter: 20`

### Model F1 < 0.75
Xem phần "Kết luận & Khuyến nghị" trong `reports/evaluation_report.md`

## 📞 Hỗ trợ

- **Issues**: Tạo issue trên GitHub repository
- **Documentation**: Xem file `reports/evaluation_report.md` sau khi train
- **Code**: Tất cả code đều có docstrings chi tiết

## 📝 License

MIT License - Sử dụng tự do cho mục đích học tập và nghiên cứu.

## 🙏 Credits

- Dataset: Movies dataset (cần citation nếu publish)
- Libraries: scikit-learn, XGBoost, LightGBM, SHAP, Flask
- Methodology: Tuân theo best practices của ML Engineering

---

**Phiên bản:** 1.0.0  
**Ngày cập nhật:** 2025-10-05  
**Tác giả:** ML Team
