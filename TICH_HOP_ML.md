# 🎬 HƯỚNG DẪN TÍCH HỢP MÔ HÌNH ML VÀO WEBSITE

## 📋 Tổng quan

Tài liệu này hướng dẫn chi tiết cách tích hợp mô hình ML mới (được train bởi `train.py`) vào Flask web application.

---

## 🏗️ Kiến trúc hệ thống

### **Luồng dữ liệu:**

```
User Input (Form) 
    ↓
app.py (Flask Backend)
    ↓
Feature Engineering (giống train.py)
    ↓
best_model.pkl (Trained ML Model)
    ↓
Prediction + Probability
    ↓
Result Display (HTML Template)
```

---

## 📁 Cấu trúc file mới

```
Website/
├── app.py                    # ✨ FLASK APP MỚI (tích hợp ML)
├── run_app.sh               # ✨ SCRIPT CHẠY APP
├── train.py                 # Script train mô hình
├── predict.py               # CLI tool dự đoán
├── config.yaml              # Cấu hình ML pipeline
├── models/
│   ├── best_model.pkl       # Mô hình tốt nhất (được train bởi train.py)
│   └── best_model_metadata.json  # Metadata (metrics, threshold, etc.)
├── web/
│   ├── templates/
│   │   ├── index.html       # Trang chủ với form input
│   │   ├── result.html      # ✨ ĐÃ CẬP NHẬT - hiển thị kết quả
│   │   └── ...
│   └── static/
│       └── css/
│           └── style.css    # ✨ ĐÃ CẬP NHẬT - thêm .model-info
└── src/
    ├── main.py              # 🗑️ CŨ - không dùng nữa
    └── data_analysis.py     # Module tạo biểu đồ
```

---

## 🚀 Cách chạy website với mô hình mới

### **Bước 1: Train mô hình (nếu chưa có)**

```bash
# Chạy training pipeline
./train.sh

# Hoặc trực tiếp
python train.py
```

**Output:**
- `models/best_model.pkl` - Mô hình ML tốt nhất
- `models/best_model_metadata.json` - Thông tin mô hình
- `reports/evaluation_report.md` - Báo cáo đánh giá

---

### **Bước 2: Chạy web app**

```bash
# Sử dụng script tự động
./run_app.sh

# Hoặc chạy trực tiếp
python app.py
```

**Web app sẽ chạy tại:** http://localhost:5000

---

## 🔧 Chi tiết tích hợp

### **1. Load mô hình trong app.py**

```python
# Load best model
model = joblib.load('./models/best_model.pkl')

# Load metadata
with open('./models/best_model_metadata.json', 'r') as f:
    metadata = json.load(f)

BEST_THRESHOLD = metadata['best_threshold']
MODEL_NAME = metadata['model_name']
```

**Metadata chứa:**
- `model_name`: Tên thuật toán (RandomForest, XGBoost, etc.)
- `best_threshold`: Threshold tối ưu cho F1-score
- `test_metrics`: F1, precision, recall, ROC-AUC, etc.
- `training_time`: Thời gian train
- `feature_names`: Danh sách features

---

### **2. Feature Engineering**

Hàm `engineer_features()` trong `app.py` thực hiện **giống hệt** như trong `train.py`:

```python
def engineer_features(df):
    # 1. Date features
    df['release_year'] = ...
    df['release_month'] = ...
    df['release_weekday'] = ...
    df['release_season'] = ...
    df['is_holiday_release'] = ...
    
    # 2. Log transforms
    df['budget_log'] = np.log1p(df['Budget'])
    df['vote_count_log'] = np.log1p(df['Vote Count'])
    
    # 3. Interaction features
    df['budget_vote_interaction'] = df['Budget'] * df['Vote Average']
    df['budget_per_minute'] = df['Budget'] / (df['Runtime'] + 1)
    df['vote_score'] = df['Vote Average'] * np.log1p(df['Vote Count'])
    
    # 4. Missing flags
    df['is_missing_budget'] = df['Budget'].isnull().astype(int)
    
    return df
```

**⚠️ QUAN TRỌNG:** Features phải khớp 100% với lúc training!

---

### **3. Prediction với threshold tối ưu**

```python
# Predict probability
pred_proba = model.predict_proba(input_df)[:, 1][0]

# Apply optimized threshold
prediction = 1 if pred_proba >= BEST_THRESHOLD else 0
```

**Giải thích:**
- `pred_proba`: Xác suất phim thành công (0-1)
- `BEST_THRESHOLD`: Ngưỡng tối ưu từ threshold optimization
- `prediction`: 1 = Thành công, 0 = Không thành công

---

### **4. Hiển thị kết quả**

Template `result.html` hiển thị:

```html
<div class="model-info">
    <p><strong>🤖 Mô hình:</strong> {{ model_name }}</p>
    <p><strong>🎯 Threshold:</strong> {{ threshold }}%</p>
    <p><strong>📊 Xác suất thành công:</strong> {{ probability }}%</p>
</div>
```

**Variables truyền vào:**
- `model_name`: Tên mô hình (VD: "RandomForestClassifier")
- `threshold`: Best threshold (VD: 45.5%)
- `probability`: Xác suất thành công (VD: 78.2%)
- `confidence`: Độ tin cậy của dự đoán

---

## 🎨 CSS Updates

Thêm styling cho model info box trong `style.css`:

```css
.model-info {
    background: var(--bg-soft);
    border-left: 3px solid var(--accent);
    padding: 1rem 1.5rem;
    margin: 1rem 0;
    border-radius: 8px;
}

.model-info p {
    margin: 0.5rem 0;
    font-size: 0.95rem;
}

.model-info strong {
    color: var(--accent);
}
```

---

## 🔄 So sánh: Cũ vs Mới

| Aspect | src/main.py (CŨ) | app.py (MỚI) |
|--------|------------------|--------------|
| **Mô hình** | `movie_success_model.pkl` (đơn giản) | `best_model.pkl` (best từ 4 thuật toán) |
| **Features** | 9 features cơ bản | 20+ features với engineering |
| **Threshold** | Cố định 0.5 | Tối ưu hóa (VD: 0.455) |
| **Preprocessing** | Manual encoding | Pipeline tự động |
| **Metrics** | Không có metadata | Đầy đủ F1, precision, recall, ROC-AUC |
| **Feature Engineering** | Không có | ROI, interactions, log transforms, missing flags |
| **Imbalance Handling** | class_weight | SMOTE + class_weight |

---

## 📊 API Endpoints

### **1. Trang chủ**
```
GET /
Hiển thị form dự đoán
```

### **2. Dự đoán (Web Form)**
```
POST /predict
Body: form-data với các fields
Response: Render result.html
```

### **3. Dự đoán (API)**
```
POST /api/predict
Body: JSON
{
    "budget": 100000000,
    "runtime": 120,
    "vote_average": 7.5,
    "vote_count": 1000,
    "release_year": 2024,
    "release_month": 6,
    "genre": "Action",
    "country": "United States of America"
}

Response: JSON
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

### **4. Thông tin mô hình**
```
GET /model-info
Response: JSON với model metadata
```

### **5. Phân tích dữ liệu**
```
GET /data
Hiển thị biểu đồ và thống kê
```

---

## 🧪 Testing

### **Test 1: Kiểm tra mô hình đã load**

```bash
python -c "import joblib; m = joblib.load('models/best_model.pkl'); print('✅ Model loaded')"
```

### **Test 2: Test API endpoint**

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
    "genre": "Action",
    "country": "United States of America"
  }'
```

### **Test 3: Test web form**

1. Mở http://localhost:5000
2. Điền form với dữ liệu test
3. Submit và kiểm tra kết quả
4. Verify model_name, threshold, probability được hiển thị

---

## 🐛 Troubleshooting

### **Lỗi: "Không tìm thấy model"**

```bash
# Kiểm tra model có tồn tại không
ls -lh models/best_model.pkl

# Nếu không có, train lại
./train.sh
```

### **Lỗi: "Feature mismatch"**

**Nguyên nhân:** Features trong input không khớp với lúc training

**Giải pháp:**
1. Kiểm tra `engineer_features()` trong app.py
2. So sánh với `engineer_features()` trong train.py
3. Đảm bảo tất cả features được tạo giống nhau

### **Lỗi: "Module not found"**

```bash
# Cài đặt dependencies
source venv/bin/activate
pip install -r requirements.txt
```

### **Lỗi: Import error với src/data_analysis.py**

```bash
# Thêm PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/home/ktmjin/Documents/Website"
python app.py
```

---

## 🎯 Best Practices

### **1. Version Control**

```bash
# Commit model metadata cùng với code
git add models/best_model_metadata.json
git commit -m "🤖 Update model: F1=0.85, threshold=0.455"
```

### **2. Model Monitoring**

- Log predictions để phân tích
- Track confidence distribution
- Monitor performance over time

### **3. Model Updates**

Khi retrain mô hình:

```bash
# 1. Train mô hình mới
./train.sh

# 2. Restart web app
pkill -f app.py
./run_app.sh

# 3. Verify model info
curl http://localhost:5000/model-info
```

### **4. Production Deployment**

```python
# Trong app.py, thay đổi cho production
if __name__ == "__main__":
    app.run(
        debug=False,          # Tắt debug mode
        host='0.0.0.0',       # Allow external connections
        port=5000,
        threaded=True         # Handle multiple requests
    )
```

---

## 📚 Tài liệu liên quan

- **README_ML.md**: Chi tiết về ML pipeline
- **HUONG_DAN_DAY_DU.md**: Hướng dẫn toàn diện
- **TONG_KET.md**: Checklist deliverables
- **reports/evaluation_report.md**: Đánh giá mô hình

---

## ✅ Checklist hoàn thành

- [x] Tạo `app.py` với ML integration
- [x] Load best_model.pkl và metadata
- [x] Implement feature engineering giống train.py
- [x] Apply optimized threshold
- [x] Update `result.html` template
- [x] Add CSS styling cho model info
- [x] Tạo `run_app.sh` script
- [x] Viết tài liệu tích hợp
- [x] Provide API endpoints
- [x] Add error handling

---

## 🎉 Kết quả

Website giờ đây sử dụng mô hình ML tiên tiến với:

✅ **Best model** từ 4 thuật toán (LogisticRegression, RandomForest, XGBoost, LightGBM)  
✅ **20+ engineered features** thay vì 9 features cơ bản  
✅ **Optimized threshold** cho F1-score tối ưu  
✅ **SMOTE** cho imbalance handling  
✅ **Hyperparameter tuning** với 5-fold CV  
✅ **Metadata tracking** cho model monitoring  
✅ **Modern UI** với smooth animations  

**Chạy ngay:** `./run_app.sh` 🚀
