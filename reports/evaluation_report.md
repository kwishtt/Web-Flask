# BÁO CÁO ĐÁNH GIÁ MÔ HÌNH DỰ ĐOÁN THÀNH CÔNG PHIM

**Ngày tạo:** 2025-10-06 01:29:16

## 1. Tổng quan

- **Mô hình tốt nhất:** xgboost
- **F1-Score:** 1.0000
- **ROC-AUC:** 1.0000

## 2. So sánh các mô hình

| Mô hình | F1-Score | Precision | Recall | ROC-AUC |
|---------|----------|-----------|--------|----------|
| logistic_regression | 0.8804 | 0.8679 | 0.8932 | 0.9323 |
| random_forest | 0.9952 | 0.9904 | 1.0000 | 1.0000 |
| xgboost | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| lightgbm | 0.9952 | 0.9904 | 1.0000 | 0.9997 |

## 3. Hyperparameters của mô hình tốt nhất

```json
{
  "colsample_bytree": 0.6,
  "learning_rate": 0.01,
  "max_depth": 3,
  "n_estimators": 100,
  "subsample": 0.6
}
```

## 4. Kết luận & Khuyến nghị

✅ Mô hình đạt ngưỡng chấp nhận (F1 ≥ 0.75)

