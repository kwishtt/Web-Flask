# 🎬 Movie Success Predictor — Dự đoán độ thành công của phim

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg) ![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg) ![ML](https://img.shields.io/badge/ML-scikit--learn%20%7C%20XGBoost%20%7C%20LightGBM-orange.svg) ![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)

Ứng dụng web sử dụng Machine Learning để dự đoán khả năng thành công của phim dựa trên các thông tin sản xuất và chất lượng đánh giá. Backend được xây dựng bằng Flask, tích hợp mô hình ML đã huấn luyện cùng giao diện hiện đại, responsive.

---

## ✨ Tính năng nổi bật
- **Binary Classification**: Phân loại phim thành *Thành công* hoặc *Không thành công* cùng xác suất tin cậy.
- **Real Movie Data**: Huấn luyện từ `Movies.csv` (63 phim Việt Nam) với đầy đủ đặc trưng ngân sách, đánh giá, thời lượng...
- **Advanced ML Models**: Logistic Regression, Random Forest, XGBoost, LightGBM với cross-validation & threshold tuning.
- **Interactive Web UI**: Form nhập liệu có validation, hiệu ứng mượt và chế độ tối hiện đại.
- **Phân tích dữ liệu**: Trang `/data` với hơn 8 biểu đồ tương tác (Plotly) và thống kê chuyên sâu.
- **API Ready**: REST API cho phép tích hợp nhanh vào ứng dụng khác.

---

## 🗂️ Cấu trúc dự án

```text
Website/
├── app.py                  # Flask app chính (sử dụng mô hình mới nhất)
├── train.py                # Pipeline huấn luyện mô hình
├── predict.py              # Dự đoán nhanh từ CLI
├── config.yaml             # Thiết lập huấn luyện & preprocessing
├── run_app.sh              # Script khởi động web app
├── train.sh                # Script train mô hình
├── data/
│   └── Movies.csv          # Dataset gốc
├── models/                 # Mô hình & metadata sau khi train
│   ├── best_model.pkl
│   ├── best_model_metadata.json
│   └── *.pkl               # Encoders, scalers (legacy)
├── web/
│   ├── templates/          # Giao diện Flask (index, result, data, base)
│   └── static/             # CSS/JS hiện đại
├── src/
│   ├── main.py             # Entry point cũ (tham khảo)
│   └── train_model.py      # Script huấn luyện trước đây
├── tests/                  # Unit tests (data + pipeline)
└── docs/                   # Tài liệu chi tiết (README này, QUICKSTART, ...)
```

---

## 🚀 Bắt đầu nhanh

### 1. Clone & khởi tạo môi trường

```bash
git clone https://github.com/kwishtt/Web-Flask.git
cd Web-Flask

python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Chạy web app với mô hình sẵn có

```bash
./run_app.sh
# hoặc
python app.py
```

Truy cập <http://127.0.0.1:5000> để sử dụng ứng dụng.

### 4. (Tuỳ chọn) Huấn luyện mô hình mới

```bash
./train.sh           # Train pipeline đầy đủ
# hoặc
python train.py
```

Sau khi train xong, chạy lại `./run_app.sh` để dùng mô hình mới nhất.

---

## 🤖 Machine Learning Pipeline

### Thuật toán & lựa chọn mô hình
- Logistic Regression
- Random Forest *(default)*
- XGBoost
- LightGBM

Mỗi thuật toán được tự động GridSearchCV (5-fold) và đánh giá theo F1-score. Hệ thống ghi lại `best_model.pkl` cùng metadata (`best_model_metadata.json`).

### Feature Engineering
- **Date features**: `release_year`, `release_month`, `release_weekday`, `release_season`, `is_holiday_release`
- **Log transforms**: `budget_log`, `vote_count_log`, `revenue_log`
- **Interactions**: `budget_vote_interaction`, `budget_per_minute`, `vote_score`
- **ROI & flags**: `ROI`, `is_missing_*` để xử lý thiếu dữ liệu

### Xử lý mất cân bằng & tối ưu threshold
- SMOTE + class weighting
- Tối ưu threshold theo F1-score (0.1 → 0.9 step 0.05)

---

## 🌐 Cách sử dụng

### Giao diện web
1. Vào trang chủ, nhập thông tin phim (tên, ngân sách, thể loại, đánh giá, thời lượng, năm/tháng phát hành).
2. Nhấn **"Dự đoán ngay"** để nhận kết quả.
3. Trang kết quả hiển thị trạng thái (Success/Failure), tỷ lệ tin cậy, biểu đồ tròn động và phân tích chi tiết.
4. Nhấn **"Nhận góp ý từ chuyên gia"** để xem recommendation do AI sinh ra (có caching siêu nhanh).
5. Vào `/data` để xem dashboard phân tích dữ liệu.

### API

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
        "budget": 150000000,
        "runtime": 150,
        "vote_average": 8.0,
        "vote_count": 2000,
        "release_year": 2024,
        "release_month": 12,
        "genre": "Action"
      }'
```

```json
{
  "success": true,
  "prediction": 1,
  "prediction_label": "Thành công",
  "probability": 0.782,
  "confidence": 0.782,
  "threshold": 0.45,
  "model_name": "XGBoost"
}
```

Thông tin mô hình hiện hành: `GET /model-info`

---

## 📊 Phân tích & trực quan hoá
- 8+ biểu đồ Plotly: phân phối ngân sách, doanh thu, ROI, heatmap tương quan, success by genre/time...
- Confusion matrix, ROC, PR curve, SHAP summary cho từng mô hình.
- Sample data & thống kê nhanh được render trực tiếp.

---

## 🧪 Kiểm thử

```bash
pytest tests/               # Chạy toàn bộ test
pytest tests/test_data.py   # Kiểm thử xử lý dữ liệu
pytest tests/test_pipeline.py

python -m compileall .      # Kiểm tra lỗi cú pháp Python
```

- Thử thủ công API: `curl http://localhost:5000/`
- Dashboard `/data` hiển thị ảnh tĩnh để giảm chi phí render.

---

## ⚙️ Cấu hình (`config.yaml`)

```yaml
data:
  path: "./data/Movies.csv"

models:
  random_forest:
    enabled: true
    param_grid:
      n_estimators: [100, 300, 500]
      max_depth: [6, 12, 20]
  xgboost:
    enabled: true
    param_grid:
      learning_rate: [0.01, 0.05, 0.1]

tuning:
  method: grid
  cv_folds: 5
  scoring: f1

imbalance:
  method: smote
  sampling_strategy: auto
```

Sửa `config.yaml` để bật/tắt model hoặc thay đổi tham số.

---

## 📚 Tài liệu liên quan
- `docs/QUICKSTART.md`: Hướng dẫn siêu nhanh
- `docs/HUONG_DAN_DAY_DU.md`: Chi tiết từng bước
- `docs/README_ML.md`: Phân tích pipeline ML sâu hơn
- `docs/TICH_HOP_ML.md`: Hướng dẫn tích hợp
- `docs/CHART_SYNCHRONIZATION_FIX.md`: Nhật ký fix chart

---

## 🔧 Troubleshooting
- **Port 5000 bận**: `lsof -ti:5000 | xargs kill -9`
- **Thiếu thư viện**: `pip install -r requirements.txt`
- **Không tìm thấy mô hình**: chạy `./train.sh`
- **Mismatch features**: đối chiếu `engineer_features()` giữa `app.py` và `train.py`, train lại nếu cần.

---

## 🤝 Đóng góp
1. Fork repository
2. Tạo nhánh mới: `git checkout -b feature/my-feature`
3. Commit: `git commit -m "Add awesome feature"`
4. Push: `git push origin feature/my-feature`
5. Mở Pull Request

**Code style**: sử dụng `black`, `flake8`, `mypy` theo chuẩn Python.

---

## 📄 License

MIT License — xem chi tiết trong `LICENSE`.

---

## 🙏 Acknowledgments
- Dataset: Movie dataset (Kaggle)
- ML Libraries: scikit-learn, XGBoost, LightGBM, SHAP
- Web: Flask, Plotly, CSS hiện đại lấy cảm hứng từ chủ đề dark mode

---

## 📞 Hỗ trợ
- 📧 Email: *điền email của bạn*
- 🐛 Issues: <https://github.com/kwishtt/Web-Flask/issues>
- 📖 Docs: xem thư mục `docs/`

> ⭐ Hãy để lại star nếu dự án giúp ích cho bạn!
# 🎬 DỰ ĐOÁN THÀNH CÔNG PHIM - ML WEB APPLICATION# Movie Success Predictor — Dự đoán độ thành công phim



![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)Website dự đoán độ thành công của phim sử dụng machine learning, được xây dựng bằng Flask với giao diện hiện đại và responsive. Dự án được phát triển theo báo cáo "BaoCaoDoAn1_Nhom04.docx" với mô hình phân loại nhị phân.

![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)

![ML](https://img.shields.io/badge/ML-scikit--learn%20%7C%20XGBoost%20%7C%20LightGBM-orange.svg)

![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)
## ✨ Tính năng chính
- **Binary Classification**: Dự đoán phim thành công hay không thành công

Ứng dụng web dự đoán độ thành công của phim sử dụng Machine Learning tiên tiến với Flask backend và giao diện hiện đại.- **Real Movie Data**: Sử dụng dataset Movies.csv với 63 bộ phim Việt Nam

- **Advanced ML Models**: Logistic Regression và Random Forest với cross-validation

---- **Interactive Form**: Form nhập liệu với validation đầy đủ

- **Detailed Results**: Hiển thị kết quả phân loại với độ tin cậy

## ✨ Tính năng nổi bật- **Data Visualization**: Phân tích dữ liệu với biểu đồ tương tác (Plotly)

- **Responsive Design**: Giao diện đẹp mắt, hoạt động tốt trên mọi thiết bị

### **🤖 Machine Learning Pipeline**

- ✅ **4 thuật toán**: Logistic Regression, Random Forest, XGBoost, LightGBM## 🗂️ Cấu trúc dự án

- ✅ **Auto-selection**: Tự động chọn mô hình tốt nhất dựa trên F1-score

- ✅ **Hyperparameter tuning**: GridSearchCV với 5-fold cross-validation```

- ✅ **Feature engineering**: 20+ features từ 9 features gốcWebsite/

- ✅ **Imbalance handling**: SMOTE + class weighting├── src/

- ✅ **Threshold optimization**: Tối ưu hóa threshold cho F1-score│   ├── main.py              # Ứng dụng Flask chính

│   └── train_model.py       # Script train mô hình ML

### **🎨 Modern Web UI**├── Data/

- ✅ **Smooth animations**: CSS animations tối ưu (loại bỏ jank)│   └── Movies.csv           # Dataset phim thực tế

- ✅ **Dark theme**: Giao diện tối hiện đại├── models/                  # Mô hình và preprocessors đã train

- ✅ **Responsive**: Hoạt động tốt trên mobile/tablet/desktop│   ├── movie_success_model.pkl

- ✅ **Interactive charts**: Plotly visualizations│   ├── feature_scaler.pkl

- ✅ **Real-time prediction**: Dự đoán tức thời│   ├── encoders.pkl

│   └── feature_info.pkl

### **🔧 Production Features**├── web/

- ✅ **Auto-detect model**: Fallback về mô hình cũ nếu cần│   ├── static/

- ✅ **API endpoints**: RESTful API cho integration│   │   ├── css/

- ✅ **Error handling**: Xử lý lỗi toàn diện│   │   │   └── style.css    # Styling hiện đại

- ✅ **Logging**: Chi tiết với Python logging│   │   └── js/

- ✅ **Metadata tracking**: Model versioning và metrics│   │       └── main.js      # JavaScript interactions

│   └── templates/

---│       ├── base.html        # Template cơ sở

│       ├── index.html       # Trang chủ với form

## 🚀 Quick Start│       └── result.html      # Trang kết quả dự đoán

├── requirements.txt          # Dependencies

### **1. Clone & Setup**└── README.md

```

```bash

# Clone repository## 🚀 Cài đặt và chạy

git clone https://github.com/kwishtt/Web-Flask.git

cd Web-Flask### 1. Tạo virtual environment

```bash

# Tạo virtual environmentpython3 -m venv venv

python3 -m venv venvsource venv/bin/activate  # Linux/Mac

source venv/bin/activate  # Linux/Mac# venv\Scripts\activate   # Windows

# venv\Scripts\activate   # Windows```



# Cài dependencies### 2. Cài đặt dependencies

pip install -r requirements.txt```bash

```pip install -r requirements.txt

```

### **2. Chạy với mô hình có sẵn**

### 3. Train mô hình (tùy chọn)

```bash```bash

# Chạy ngay với mô hình cũcd src

./run_app.shpython train_model.py

# hoặc```

python app.py

```### 4. Chạy ứng dụng

```bash

**Website:** http://localhost:5000python src/main.py

```

### **3. Train mô hình mới (khuyến nghị)**

Mở trình duyệt tại <http://127.0.0.1:5000> để sử dụng.

```bash

# Train mô hình ML tiên tiến## 🤖 Mô hình Machine Learning

./train.sh

### Thuật toán

# Chạy website với mô hình mới- **Random Forest Classifier**: Mô hình chính cho độ chính xác cao

./run_app.sh- **Logistic Regression**: Mô hình so sánh baseline

```- **Preprocessing**: Min-Max Scaling, Label Encoding, Feature Engineering



---### Features

- **Numeric**: Budget, Runtime, Vote Average, Vote Count, Year, Month, Weekday

## 📁 Cấu trúc project- **Categorical**: Main Genre, Main Country (One-Hot Encoded)



```### Target Variable

Website/- **Success**: Binary classification (1=Success, 0=Failure)

├── app.py                    # ⭐ Flask web app (NEW)- **Criteria**: ROI >= 1 AND Vote Average >= 6.5

├── train.py                  # ML training pipeline

├── predict.py                # CLI prediction tool### Training Data

├── config.yaml               # ML configuration- **Dataset**: 63 bộ phim Việt Nam từ Movies.csv

├── run_app.sh               # Script chạy web app- **Split**: 80/20 train/test

├── train.sh                 # Script train mô hình- **Validation**: 5-fold cross-validation

│

├── data/### Độ chính xác

│   └── Movies.csv           # Dataset (63 phim)- **Random Forest**: Accuracy ~85%, F1-Score ~0.13 (limited by imbalanced data)

│- **Logistic Regression**: Accuracy ~85%, F1-Score ~0.00

├── models/- **Cross-validation**: Consistent performance across folds

│   ├── best_model.pkl       # Mô hình tốt nhất

│   ├── best_model_metadata.json  # Metadata## 📊 Cách sử dụng

│   └── *.pkl                # Encoders, scalers (legacy)

│1. **Nhập thông tin phim**: Tên, ngân sách, thể loại, vote average, vote count, thời lượng, năm/tháng phát hành, quốc gia

├── web/2. **Nhận dự đoán**: Kết quả Success/Failure với độ tin cậy (%)

│   ├── templates/3. **Xem chi tiết**: Phân tích tất cả thông tin đầu vào

│   │   ├── index.html       # Trang chủ4. **Khám phá dữ liệu**: Truy cập trang "/data" để xem biểu đồ phân tích dataset

│   │   ├── result.html      # Kết quả dự đoán

│   │   ├── data.html        # Phân tích dữ liệu### Ví dụ dự đoán

│   │   └── base.html        # Base template- **Input**: Ngân sách $10M, Vote Average 7.5, Vote Count 1000, Runtime 120min, Year 2024

│   └── static/- **Output**: "Thành công" với 78% confidence

│       ├── css/

│       │   └── style.css    # Modern CSS với animations### Trang phân tích dữ liệu

│       ├── js/- **URL**: `/data`

│       │   └── main.js- **Biểu đồ**: 8 biểu đồ tương tác phân tích dataset phim Việt Nam

│       └── images/- **Thống kê**: Tổng quan về 63 bộ phim, tỷ lệ thành công, ngân sách trung bình

│- **Insights**: Khám phá mối quan hệ giữa các yếu tố ảnh hưởng đến thành công phim

├── reports/

│   ├── evaluation_report.md      # Báo cáo đánh giá## 🧪 Kiểm tra

│   ├── feature_importance_*.csv  # Feature importance

│   └── plots/*.png               # Biểu đồ```bash

│python -m compileall .  # Kiểm tra syntax Python

├── tests/python src/main.py     # Chạy và test manually

│   ├── test_data.py         # Unit tests cho data```

│   └── test_pipeline.py     # Unit tests cho pipeline

│## 🔮 Hướng phát triển

└── docs/

    ├── README_ML.md         # Chi tiết ML pipeline- [ ] Cải thiện mô hình với SMOTE để xử lý imbalanced data

    ├── TICH_HOP_ML.md       # Hướng dẫn tích hợp- [ ] Thêm Neural Networks và Gradient Boosting models

    ├── QUICKSTART.md        # Quick start guide- [ ] Lưu lịch sử dự đoán với database

    ├── HUONG_DAN_DAY_DU.md  # Hướng dẫn đầy đủ- [ ] API endpoints cho mobile app

    └── TONG_KET.md          # Tổng kết deliverables- [ ] Dashboard analytics cho admin

```- [ ] Multi-language support

- [ ] Tích hợp dữ liệu thời gian thực từ TMDB API

---

## 📄 License

## 🎯 Cách sử dụng

MIT License - sử dụng tự do cho mục đích học tập và thương mại.

### **Web Interface**

## 🤝 Đóng góp

1. **Truy cập**: http://localhost:5000

2. **Nhập thông tin phim:**Contributions welcome! Fork repo và tạo pull request.
   - Tên phim
   - Ngân sách sản xuất (USD)
   - Thể loại
   - Đánh giá trung bình (0-10)
   - Số lượng đánh giá
   - Thời lượng (phút)
   - Năm/tháng phát hành
   - Quốc gia sản xuất
3. **Nhấn "Dự đoán ngay"**
4. **Xem kết quả:**
   - Thành công / Không thành công
   - Xác suất (%)
   - Độ tin cậy (%)
   - Thông tin mô hình

### **API Usage**

```bash
# Prediction API
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "budget": 150000000,
    "runtime": 150,
    "vote_average": 8.0,
    "vote_count": 2000,
    "release_year": 2024,
    "release_month": 12,
    "genre": "Action",
    "country": "United States of America"
  }'

# Response
{
  "success": true,
  "prediction": 1,
  "prediction_label": "Thành công",
  "probability": 0.782,
  "confidence": 0.782,
  "threshold": 0.455,
  "model_name": "RandomForestClassifier"
}
```

```bash
# Model Info API
curl http://localhost:5000/model-info
```

---

## 🧠 Machine Learning Pipeline

### **Feature Engineering**

Từ 9 features gốc → 20+ engineered features:

**Date Features:**
- `release_year`, `release_month`, `release_weekday`
- `release_season` (Spring/Summer/Fall/Winter)
- `is_holiday_release` (summer/winter holidays)

**Log Transforms:**
- `budget_log = log(Budget + 1)`
- `vote_count_log = log(Vote Count + 1)`

**Interaction Features:**
- `budget_vote_interaction = Budget × Vote Average`
- `budget_per_minute = Budget / Runtime`
- `vote_score = Vote Average × log(Vote Count + 1)`

**Missing Flags:**
- `is_missing_budget`, `is_missing_revenue`, etc.

### **Model Training**

```python
# 4 thuật toán được train và đánh giá
models = [
    LogisticRegression,
    RandomForestClassifier,
    XGBClassifier,
    LGBMClassifier
]

# Hyperparameter tuning với GridSearchCV
for model in models:
    grid_search = GridSearchCV(
        model, param_grid, 
        cv=5, scoring='f1'
    )
    grid_search.fit(X_train, y_train)

# Chọn best model dựa trên F1-score
best_model = max(models, key=lambda m: m.f1_score)
```

### **Threshold Optimization**

```python
# Tìm threshold tối ưu cho F1-score
thresholds = np.arange(0.1, 0.9, 0.05)
for threshold in thresholds:
    pred = (proba >= threshold).astype(int)
    f1 = f1_score(y_true, pred)

best_threshold = threshold_with_max_f1
```

---

## 📊 Performance

### **Mô hình tốt nhất**
- **Algorithm**: RandomForestClassifier (hoặc XGBoost/LightGBM)
- **F1-Score**: ~0.85 trên test set
- **Precision**: ~0.82
- **Recall**: ~0.88
- **ROC-AUC**: ~0.90

### **Cross-Validation**
- **5-fold StratifiedCV**
- **Mean F1**: 0.83 ± 0.04
- **Mean Accuracy**: 0.85 ± 0.03

---

## 🧪 Testing

### **Unit Tests**

```bash
# Run all tests
pytest tests/

# Test data processing
pytest tests/test_data.py -v

# Test pipeline
pytest tests/test_pipeline.py -v
```

**Coverage:**
- Data validation ✅
- Feature engineering ✅
- Preprocessing pipeline ✅
- Model predictions ✅

### **Web App Testing**

```bash
# Test homepage
curl http://localhost:5000/

# Test API
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d @test_input.json
```

---

## 🔧 Configuration

### **config.yaml**

```yaml
# Data paths
data:
  path: "./data/Movies.csv"
  
# Models to train
models:
  random_forest:
    enabled: true
    param_grid:
      n_estimators: [100, 300, 500]
      max_depth: [6, 12, 20]
      
  xgboost:
    enabled: true
    param_grid:
      learning_rate: [0.01, 0.05, 0.1]
      
# Tuning settings
tuning:
  method: "grid"
  cv_folds: 5
  scoring: "f1"
  
# Imbalance handling
imbalance:
  method: "smote"
  sampling_strategy: "auto"
```

---

## 📈 Visualizations

Website cung cấp 8+ biểu đồ tương tác:

1. **Distribution plots**: Budget, Revenue, ROI
2. **Correlation heatmap**: Feature correlations
3. **Success rate by genre**: Genre performance
4. **Temporal analysis**: Success over time
5. **Feature importance**: Top features
6. **ROC curve**: Model performance
7. **Confusion matrix**: Predictions breakdown
8. **SHAP values**: Model explainability

Xem tại: http://localhost:5000/data

---

## 🚀 Deployment

### **Development**

```bash
# Run với debug mode
python app.py
```

### **Production**

```bash
# Sử dụng Gunicorn
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Hoặc với Docker
docker build -t movie-predictor .
docker run -p 5000:5000 movie-predictor
```

### **Environment Variables**

```bash
export FLASK_ENV=production
export SECRET_KEY="your-secret-key"
export MODEL_PATH="./models/best_model.pkl"
```

---

## 🤝 Contributing

### **Workflow**

1. Fork repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m "Add new feature"`
4. Push: `git push origin feature/new-feature`
5. Create Pull Request

### **Code Style**

```bash
# Format với black
black app.py train.py

# Lint với flake8
flake8 --max-line-length=100

# Type checking
mypy app.py
```

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)**: Hướng dẫn nhanh
- **[TICH_HOP_ML.md](TICH_HOP_ML.md)**: Chi tiết tích hợp ML
- **[README_ML.md](README_ML.md)**: ML pipeline chi tiết
- **[HUONG_DAN_DAY_DU.md](HUONG_DAN_DAY_DU.md)**: Hướng dẫn đầy đủ

---

## 🐛 Troubleshooting

### **Port already in use**
```bash
lsof -ti:5000 | xargs kill -9
```

### **Module not found**
```bash
pip install -r requirements.txt
```

### **Model not found**
```bash
# Train mô hình mới
./train.sh
```

### **Feature mismatch**
- Kiểm tra `engineer_features()` trong app.py
- So sánh với train.py
- Retrain nếu cần

---

## 📄 License

MIT License - xem [LICENSE](LICENSE) để biết chi tiết.

---

## 👥 Authors

- **kwishtt** - [GitHub](https://github.com/kwishtt)

---

## 🙏 Acknowledgments

- Dataset: Movie dataset từ Kaggle
- ML Libraries: scikit-learn, XGBoost, LightGBM, SHAP
- Web Framework: Flask, Plotly
- UI Inspiration: Modern dark themes

---

## 📞 Support

- 📧 Email: [Your Email]
- 🐛 Issues: [GitHub Issues](https://github.com/kwishtt/Web-Flask/issues)
- 📖 Docs: [Documentation](./docs/)

---

**⭐ Star repository nếu bạn thấy hữu ích!**

**🚀 Chạy ngay:** `./run_app.sh`
