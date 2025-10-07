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
- 📧 Email: *kforwork04@gmail.com*
- 🐛 Issues: <https://github.com/kwishtt/Du-Doan-Do-Thanh-Cong-Phim/issues>
- 📖 Docs: xem thư mục `docs/`

## 🚀 Fast run
**⭐ Star repository nếu bạn thấy hữu ích!**

**🚀 Chạy ngay:** `./run_app.sh`
