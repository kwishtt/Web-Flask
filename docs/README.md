# Movie Success Predictor — Dự đoán độ thành công phim

Website dự đoán độ thành công của phim sử dụng machine learning, được xây dựng bằng Flask với giao diện hiện đại và responsive.

## ✨ Tính năng chính

- **AI-Powered Prediction**: Sử dụng Random Forest model để dự đoán độ thành công dựa trên nhiều yếu tố
- **Interactive Form**: Form nhập liệu dễ sử dụng với validation
- **Detailed Results**: Hiển thị điểm dự đoán, phân tích chi tiết và giải thích
- **Responsive Design**: Giao diện đẹp mắt, hoạt động tốt trên mọi thiết bị
- **Real-time Processing**: Dự đoán nhanh chóng trong vài giây

## 🗂️ Cấu trúc dự án

```
movie-success-predictor/
├── data/                    # Dữ liệu training
│   └── Movies.csv
├── models/                  # Mô hình và preprocessors
│   ├── movie_success_model.pkl
│   ├── genre_encoder.pkl
│   ├── feature_scaler.pkl
│   └── genre_mapping.pkl
├── src/                     # Source code
│   ├── main.py             # Ứng dụng Flask
│   └── train_model.py      # Script train mô hình
├── web/                     # Frontend
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   └── result.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
├── docs/                    # Documentation
│   └── README.md
├── requirements.txt         # Dependencies
├── .gitignore
└── venv/                    # Virtual environment
```

## 🚀 Cài đặt và chạy

### 1. Tạo virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng
```bash
python src/main.py
```

Mở trình duyệt tại <http://127.0.0.1:5000> để sử dụng.

## 🤖 Mô hình Machine Learning

### Thuật toán
- **Random Forest Regressor**: Ensemble learning cho độ chính xác cao
- **Features**: Budget, Runtime, Director Rating, Vote Count, Marketing Budget, Genre
- **Target**: Vote Average (1-10 scale)

### Training Data
- Dataset: Movies.csv với ~1000 phim
- R² Score: 0.97 (rất tốt)
- Mean Absolute Error: 0.02

### Dự đoán
Mô hình dự đoán điểm Vote Average dựa trên các yếu tố đầu vào, sau đó phân loại thành công:
- ≥7: Rất thành công
- 5-7: Thành công  
- <5: Ít thành công

## 📊 Cách sử dụng

1. **Nhập thông tin phim**: Tên, ngân sách, thể loại, đánh giá đạo diễn, số lượng đánh giá, thời lượng, ngân sách marketing
2. **Nhận dự đoán**: Điểm Vote Average dự đoán và phân tích chi tiết
3. **Xem kết quả**: Hiển thị mức độ thành công với màu sắc trực quan

## 🧪 Kiểm tra

```bash
python -c "import sys; sys.path.append('src'); import main; print('App OK')"
python src/train_model.py  # Retrain model
```

## 🔮 Hướng phát triển

- [ ] Tích hợp API IMDb để lấy dữ liệu thực
- [ ] Thêm nhiều mô hình ML (Neural Networks, Gradient Boosting)
- [ ] Lưu lịch sử dự đoán với database
- [ ] API endpoints cho mobile app
- [ ] Dashboard analytics cho admin
- [ ] Multi-language support

## 📄 License

MIT License - sử dụng tự do cho mục đích học tập và thương mại.

## 🤝 Đóng góp

Contributions welcome! Fork repo và tạo pull request.
