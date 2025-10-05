#!/bin/bash

# ==============================================
# RUN_APP.SH - CHẠY FLASK WEB APP
# ==============================================

echo "================================================"
echo "🎬 MOVIE SUCCESS PREDICTOR - WEB APP"
echo "================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment không tồn tại!"
    echo "📦 Đang tạo virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Kích hoạt virtual environment..."
source venv/bin/activate

# Check if best_model.pkl exists
if [ ! -f "models/best_model.pkl" ]; then
    echo "❌ Chưa có mô hình ML!"
    echo "⚠️  Vui lòng chạy ./train.sh để train mô hình trước"
    echo ""
    read -p "Bạn có muốn train mô hình ngay bây giờ? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🚀 Đang train mô hình..."
        ./train.sh
    else
        echo "❌ Không thể chạy app mà không có mô hình"
        exit 1
    fi
fi

# Install dependencies if needed
echo "📦 Kiểm tra dependencies..."
pip install -q -r requirements.txt

# Clear cache
echo "🗑️  Xóa cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo ""
echo "================================================"
echo "✅ Mọi thứ đã sẵn sàng!"
echo "================================================"
echo "🌐 Web app sẽ chạy tại: http://localhost:5000"
echo "🛑 Nhấn Ctrl+C để dừng"
echo "================================================"
echo ""

# Run Flask app
python app.py
