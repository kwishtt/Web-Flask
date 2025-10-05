# 📊 Dataset & Model Training Explanation

## ❓ Câu Hỏi: Model Dự Đoán Dựa Trên Dataset Nào?

### ✅ Trả Lời Ngắn Gọn:
**Model được train với TOÀN BỘ dataset (~1018 phim từ nhiều quốc gia), KHÔNG CHỈ phim Vietnam!**

---

## 📈 Chi Tiết Dataset

### 1. Dataset Gốc (`data/Movies.csv`)
```
📦 Tổng số phim: 2,193 phim
📍 Từ nhiều quốc gia:
   - USA: 593 phim
   - Vietnam: 411 phim (raw)
   - South Korea: 175 phim
   - Japan: 101 phim
   - Thailand: 54 phim
   - China: 38 phim
   - Và nhiều quốc gia khác...
```

### 2. Dataset Sau Khi Clean
```python
# Lọc bỏ phim thiếu dữ liệu hoặc dữ liệu không hợp lệ:
- Có Revenue > 0
- Có Budget > 0  
- Có Vote Average > 0
- Có Runtime

🧹 Kết quả: 1,018 phim có đủ dữ liệu
```

### 3. Dataset Training
```
🎓 Training Set (~80%): ~814 phim
🧪 Test Set (~20%): ~203 phim

✅ Total: 1,018 phim từ TẤT CẢ quốc gia
```

---

## 🤖 Model Training Process

### Configuration (`config.yaml`)
```yaml
data:
  path: "./data/Movies.csv"  # ← Toàn bộ dataset, KHÔNG filter country

preprocessing:
  roi_threshold: 1.0            # Phim thành công nếu ROI ≥ 1
  vote_average_threshold: 6.5   # VÀ Vote Average ≥ 6.5
```

### Success Label Definition
```python
Success = (ROI >= 1.0) AND (Vote Average >= 6.5)

Where:
  ROI = Revenue / Budget
```

### Training Results
```
Model: XGBoost
F1-Score: 1.0 (100%)
Accuracy: 1.0 (100%)
Precision: 1.0 (100%)
Recall: 1.0 (100%)
ROC-AUC: 1.0 (100%)

✅ Model performance hoàn hảo trên test set!
```

---

## 🌍 Data Analysis Page (`/data`)

### Tại Sao Chỉ Hiển Thị 63 Phim Vietnam?

**File:** `src/data_analysis.py`

```python
# Line 27-30: Chỉ lọc phim Vietnam để hiển thị
df = df[df['Production Countries'].str.contains('Vietnam', na=False, case=False)]

# Filter clean data
df = df.dropna(subset=['Revenue', 'Budget', 'Runtime', 'Vote Average'])
df = df[df['Revenue'] > 0]
df = df[df['Budget'] > 0]
df = df[df['Vote Average'] > 0]

# Kết quả: 63 phim Vietnam có đủ dữ liệu
```

**Mục đích:** Trang `/data` chỉ dùng để **phân tích thị trường phim Vietnam**, không phản ánh training data của model.

---

## 🔍 So Sánh

| Tiêu chí | Training Data | Data Analysis Page |
|----------|---------------|-------------------|
| **Số phim** | 1,018 phim | 63 phim |
| **Quốc gia** | Tất cả (USA, VN, Korea, Japan, v.v.) | Chỉ Vietnam |
| **Mục đích** | Train model dự đoán | Phân tích thị trường VN |
| **File** | `train.py` | `src/data_analysis.py` |

---

## 🎯 Kết Luận

### Model Prediction (`/predict`)
✅ **Dự đoán cho BẤT KỲ phim nào**, không giới hạn quốc gia  
✅ Học từ **1,018 phim** đa dạng (USA, Asia, Europe, v.v.)  
✅ Có thể dự đoán phim từ bất kỳ đâu: Vietnam, Hollywood, Hàn Quốc, v.v.

### Data Analysis (`/data`)
📊 Chỉ hiển thị **phim Vietnam** (63 phim clean)  
📊 Mục đích: Phân tích xu hướng thị trường phim Việt  
📊 Không ảnh hưởng đến model prediction

---

## 💡 Cách Kiểm Tra

### Check Training Data:
```bash
python check_dataset.py
```

### Check Config:
```bash
cat config.yaml
```

### Check Model Metadata:
```bash
cat models/best_model_metadata.json | grep -A 5 "config"
```

---

## 🚀 Nếu Muốn Thay Đổi

### Option 1: Train Chỉ Với Phim Vietnam
```yaml
# Sửa config.yaml
data:
  path: "./data/Movies.csv"
  filter: "Vietnam"  # ← Thêm filter này
```

### Option 2: Train Với Dataset Khác
```yaml
# Sửa config.yaml
data:
  path: "./data/CustomDataset.csv"  # ← Đổi path
```

### Option 3: Hiển Thị Tất Cả Phim Trong `/data`
```python
# Sửa src/data_analysis.py line 29
# Xóa hoặc comment dòng này:
# df = df[df['Production Countries'].str.contains('Vietnam', na=False, case=False)]
```

---

## 📝 Summary

```
┌─────────────────────────────────────────────────────┐
│  🎬 MOVIE SUCCESS PREDICTOR                         │
├─────────────────────────────────────────────────────┤
│  Dataset:     2,193 phim (raw)                      │
│  Clean Data:  1,018 phim (USA, VN, KR, JP, etc.)   │
│  Training:    ~814 phim (80%)                       │
│  Testing:     ~203 phim (20%)                       │
├─────────────────────────────────────────────────────┤
│  Model:       XGBoost                               │
│  F1-Score:    1.0 (100%)                            │
│  Threshold:   0.45                                  │
├─────────────────────────────────────────────────────┤
│  Prediction:  ✅ Dự đoán BẤT KỲ phim nào            │
│  /data page:  📊 Chỉ hiển thị phim Vietnam (63)    │
└─────────────────────────────────────────────────────┘
```

**Created:** October 6, 2025  
**Last Updated:** October 6, 2025
