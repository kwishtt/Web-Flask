# 🚀 HƯỚNG DẪN NHANH - TÍCH HỢP MÔ HÌNH ML

## ✅ Đã hoàn thành

### **Files mới:**
- ✨ `app.py` - Flask web app với ML integration
- ✨ `run_app.sh` - Script chạy web app
- ✨ `TICH_HOP_ML.md` - Tài liệu chi tiết

### **Files đã cập nhật:**
- 📝 `web/templates/result.html` - Hiển thị thông tin mô hình
- 🎨 `web/static/css/style.css` - Styling cho model info

---

## 🎯 Cách sử dụng

### **Option 1: Sử dụng mô hình CŨ (hiện tại)**

```bash
# Chạy web app ngay lập tức với mô hình có sẵn
./run_app.sh

# Hoặc
python app.py
```

Website sẽ chạy tại: **http://localhost:5000**

**Lưu ý:** Mô hình cũ (`movie_success_model.pkl`) sẽ được sử dụng với:
- Threshold cố định: 0.5
- 9 features cơ bản
- Không có metadata chi tiết

---

### **Option 2: Train mô hình MỚI (khuyến nghị)**

```bash
# 1. Train mô hình mới với ML pipeline tiên tiến
./train.sh

# Output sẽ tạo:
# - models/best_model.pkl
# - models/best_model_metadata.json
# - reports/evaluation_report.md

# 2. Chạy web app với mô hình mới
./run_app.sh
```

**Mô hình mới có:**
- ✅ Best model từ 4 thuật toán (LogisticRegression, RandomForest, XGBoost, LightGBM)
- ✅ 20+ engineered features (ROI, interactions, log transforms, etc.)
- ✅ Optimized threshold cho F1-score tối ưu
- ✅ SMOTE cho imbalance handling
- ✅ Hyperparameter tuning với 5-fold CV
- ✅ Đầy đủ metrics (F1, precision, recall, ROC-AUC)

---

## 📊 Features chính

### **1. Auto-detect mô hình**
App tự động phát hiện và sử dụng:
- `best_model.pkl` (mô hình mới) nếu có
- `movie_success_model.pkl` (mô hình cũ) nếu không có mô hình mới

### **2. Feature Engineering tự động**
Với mô hình mới, app sẽ tự động tạo:
- Date features (year, month, weekday, season, is_holiday)
- Log transforms (budget_log, vote_count_log)
- Interaction features (budget × vote_average, budget_per_minute)
- Missing value flags

### **3. Optimized Threshold**
- Mô hình mới: Sử dụng threshold được tối ưu hóa từ training
- Mô hình cũ: Sử dụng threshold mặc định 0.5

### **4. API Endpoints**
- `GET /` - Trang chủ với form
- `POST /predict` - Dự đoán từ form
- `POST /api/predict` - API endpoint cho JSON
- `GET /model-info` - Thông tin mô hình
- `GET /data` - Phân tích dữ liệu

---

## 🧪 Test nhanh

### **Test 1: Web UI**
```bash
# Mở trình duyệt
firefox http://localhost:5000
# hoặc
google-chrome http://localhost:5000
```

Điền form và submit để test dự đoán.

### **Test 2: API**
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

### **Test 3: Model Info**
```bash
curl http://localhost:5000/model-info
```

---

## 🔄 So sánh: Trước và Sau

| Aspect | Trước (src/main.py) | Sau (app.py) |
|--------|---------------------|--------------|
| **Mô hình** | Cố định 1 model | Auto-detect best model |
| **Features** | 9 cơ bản | 20+ engineered |
| **Threshold** | 0.5 cố định | Tối ưu hóa |
| **Metadata** | Không có | Đầy đủ F1, precision, recall |
| **Fallback** | Không | Dùng mô hình cũ nếu cần |
| **API** | Không | Có endpoints đầy đủ |
| **Feature Engineering** | Không | Tự động |

---

## 📝 Workflow khuyến nghị

### **Lần đầu sử dụng:**

```bash
# 1. Kiểm tra data
ls data/Movies.csv

# 2. Train mô hình mới
./train.sh

# 3. Review kết quả
cat reports/evaluation_report.md

# 4. Chạy web app
./run_app.sh

# 5. Test trên trình duyệt
# Mở http://localhost:5000
```

### **Khi cập nhật mô hình:**

```bash
# 1. Retrain
./train.sh

# 2. Restart app
pkill -f app.py
./run_app.sh

# 3. Verify
curl http://localhost:5000/model-info
```

---

## 🐛 Troubleshooting

### **Lỗi: "Module not found"**
```bash
pip install -r requirements.txt
```

### **Lỗi: "Port 5000 already in use"**
```bash
# Tìm và kill process
lsof -ti:5000 | xargs kill -9

# Hoặc đổi port trong app.py
app.run(port=5001)
```

### **Lỗi: "Missing preprocessing files"**
```bash
# Với mô hình cũ, cần có:
ls models/feature_scaler.pkl
ls models/encoders.pkl

# Nếu thiếu, train lại hoặc train mô hình mới
```

---

## 📚 Tài liệu chi tiết

Xem thêm:
- **TICH_HOP_ML.md** - Chi tiết tích hợp từng bước
- **README_ML.md** - Chi tiết về ML pipeline
- **HUONG_DAN_DAY_DU.md** - Hướng dẫn toàn diện

---

## ✨ Kết quả

Website giờ có:
- 🤖 **Mô hình ML tiên tiến** với auto-detection
- 🎯 **Optimized threshold** cho accuracy cao
- 📊 **Rich metadata** hiển thị trên UI
- 🔄 **Backward compatibility** với mô hình cũ
- 🚀 **Production-ready** với error handling
- 🎨 **Modern UI** với smooth animations

**Chạy ngay:** `./run_app.sh` 🚀
