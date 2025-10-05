#!/bin/bash

# ==============================================
# TRAIN.SH - SCRIPT HUẤN LUYỆN MÔ HÌNH
# ==============================================

echo "=========================================="
echo "HUẤN LUYỆN MÔ HÌNH DỰ ĐOÁN THÀNH CÔNG PHIM"
echo "=========================================="
echo ""


# Kiểm tra Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Kiểm tra file config
if [ ! -f "config.yaml" ]; then
    echo "❌ Không tìm thấy config.yaml!"
    exit 1
fi

# Kiểm tra data
if [ ! -f "data/Movies.csv" ]; then
    echo "❌ Không tìm thấy data/Movies.csv!"
    exit 1
fi

echo "✅ Tất cả files cần thiết đã sẵn sàng"
echo ""

# Tạo thư mục output
mkdir -p models
mkdir -p reports
mkdir -p reports/plots

echo "📊 Bắt đầu training..."
echo ""

# Train model
python3 train.py --config config.yaml --output-dir models/ --random-seed 42

# Kiểm tra kết quả
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ TRAINING HOÀN TẤT THÀNH CÔNG!"
    echo "=========================================="
    echo ""
    echo "Các files đã được tạo:"
    echo "- models/best_model.pkl"
    echo "- models/best_model_metadata.json"
    echo "- reports/evaluation_report.md"
    echo "- reports/feature_importance_*.csv"
    echo "- reports/plots/*.png"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ TRAINING THẤT BẠI!"
    echo "=========================================="
    exit 1
fi
