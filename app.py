"""
==============================================
APP.PY - FLASK WEB APP VỚI ML MODEL MỚI
==============================================
Tích hợp mô hình ML được train bởi train.py
"""

from flask import Flask, render_template, request, flash, jsonify
import joblib
import json
import numpy as np
import pandas as pd
import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Khởi tạo Flask app
app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
app.config["SECRET_KEY"] = "movie-success-predictor-ml-2024"
app.config["VERSION"] = "3.0"  # Tăng version để clear cache - Modern UI

# ==========================================
# LOAD MÔ HÌNH ML MỚI
# ==========================================
try:
    models_dir = './models'
    
    # Thử load best model (từ train.py)
    model_path = os.path.join(models_dir, 'best_model.pkl')
    
    if os.path.exists(model_path):
        # Sử dụng mô hình mới
        model = joblib.load(model_path)
        logger.info("✅ Đã load mô hình MỚI (best_model.pkl)")
        
        # Load metadata
        metadata_path = model_path.replace('.pkl', '_metadata.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            logger.info(f"✅ Mô hình: {metadata['model_name']}")
            logger.info(f"✅ F1-Score: {metadata['test_metrics']['f1']:.4f}")
            logger.info(f"✅ Best Threshold: {metadata['best_threshold']:.4f}")
            BEST_THRESHOLD = metadata['best_threshold']
            MODEL_NAME = metadata['model_name']
            MODEL_METRICS = metadata['test_metrics']
            USE_NEW_MODEL = True
        else:
            logger.warning("⚠️ Không tìm thấy metadata, sử dụng threshold mặc định")
            BEST_THRESHOLD = 0.5
            MODEL_NAME = "Best Model"
            MODEL_METRICS = {}
            USE_NEW_MODEL = True
    else:
        # Fallback: sử dụng mô hình cũ
        logger.warning("⚠️ Không tìm thấy best_model.pkl, sử dụng mô hình CŨ")
        old_model_path = os.path.join(models_dir, 'movie_success_model.pkl')
        
        if not os.path.exists(old_model_path):
            logger.error(f"❌ Không tìm thấy mô hình tại {old_model_path}")
            logger.info("💡 Vui lòng chạy ./train.sh để train mô hình mới")
            logger.info("💡 Hoặc đảm bảo có movie_success_model.pkl trong thư mục models/")
            sys.exit(1)
        
        model = joblib.load(old_model_path)
        logger.info("✅ Đã load mô hình CŨ (movie_success_model.pkl)")
        BEST_THRESHOLD = 0.5
        MODEL_NAME = "Legacy Model"
        MODEL_METRICS = {"note": "Train mô hình mới để có metrics chi tiết"}
        USE_NEW_MODEL = False

except Exception as e:
    logger.error(f"❌ Lỗi khi load model: {str(e)}")
    sys.exit(1)

# ==========================================
# FEATURE ENGINEERING (giống train.py)
# ==========================================
def engineer_features(df):
    """
    Feature engineering giống như trong train.py
    """
    df = df.copy()
    
    # 1. Date features
    if 'Release Date' in df.columns:
        df['Release Date'] = pd.to_datetime(df['Release Date'], errors='coerce')
        df['release_year'] = df['Release Date'].dt.year
        df['release_month'] = df['Release Date'].dt.month
        df['release_weekday'] = df['Release Date'].dt.weekday
        
        # Season
        def get_season(month):
            if pd.isna(month):
                return 0
            if month in [12, 1, 2]:
                return 1  # Winter
            elif month in [3, 4, 5]:
                return 2  # Spring
            elif month in [6, 7, 8]:
                return 3  # Summer
            else:
                return 4  # Fall
        
        df['release_season'] = df['release_month'].apply(get_season)
        df['is_holiday_release'] = df['release_month'].apply(
            lambda x: 1 if x in [6, 7, 8, 12, 1, 2] else 0 if pd.notna(x) else 0
        )
    
    # 2. ROI (nếu có Revenue)
    if 'Budget' in df.columns and 'Revenue' in df.columns:
        df['ROI'] = df['Revenue'] / (df['Budget'] + 1)
    
    # 3. Log transforms
    if 'Budget' in df.columns:
        df['budget_log'] = np.log1p(df['Budget'])
    
    if 'Revenue' in df.columns:
        df['revenue_log'] = np.log1p(df['Revenue'])
    
    if 'Vote Count' in df.columns:
        df['vote_count_log'] = np.log1p(df['Vote Count'])
    
    # 4. Interaction features
    if 'Budget' in df.columns and 'Vote Average' in df.columns:
        df['budget_vote_interaction'] = df['Budget'] * df['Vote Average']
    
    if 'Budget' in df.columns and 'Runtime' in df.columns:
        df['budget_per_minute'] = df['Budget'] / (df['Runtime'] + 1)
    
    if 'Vote Average' in df.columns and 'Vote Count' in df.columns:
        df['vote_score'] = df['Vote Average'] * np.log1p(df['Vote Count'])
    
    # 5. Missing value flags
    for col in ['Budget', 'Revenue', 'Runtime', 'Vote Average']:
        if col in df.columns:
            df[f'is_missing_{col.lower().replace(" ", "_")}'] = df[col].isnull().astype(int)
    
    return df

# ==========================================
# PREPARE INPUT DATA
# ==========================================
def prepare_input_data(form_data):
    """
    Chuẩn bị input data từ form để dự đoán
    """
    if USE_NEW_MODEL:
        # Sử dụng feature engineering cho mô hình mới
        data = {
            'Budget': float(form_data.get('budget', 0)),
            'Runtime': float(form_data.get('runtime', 120)),
            'Vote Average': float(form_data.get('vote_average', 5)),
            'Vote Count': float(form_data.get('vote_count', 100)),
            'Release Date': f"{form_data.get('release_year', 2024)}-{form_data.get('release_month', 1):02d}-15"
        }
        
        # Thêm categorical features nếu có
        if 'genre' in form_data:
            data['Main_Genre'] = form_data['genre']
        if 'country' in form_data:
            data['Main_Country'] = form_data['country']
        
        # Tạo DataFrame
        df = pd.DataFrame([data])
        
        # Feature engineering
        df = engineer_features(df)
        
        return df
    else:
        # Mô hình cũ: sử dụng encoders và scaler có sẵn
        logger.info("Sử dụng preprocessing cũ...")
        
        # Load encoders và scaler
        try:
            scaler = joblib.load('./models/feature_scaler.pkl')
            encoders = joblib.load('./models/encoders.pkl')
        except:
            logger.error("❌ Không tìm thấy scaler hoặc encoders cho mô hình cũ")
            raise ValueError("Missing preprocessing files")
        
        # Prepare numeric features
        numeric_values = [
            float(form_data.get('budget', 0)),
            float(form_data.get('runtime', 120)),
            float(form_data.get('vote_average', 5)),
            float(form_data.get('vote_count', 100)),
            int(form_data.get('release_year', 2024)),
            int(form_data.get('release_month', 1)),
            0  # weekday placeholder
        ]
        
        # Scale numeric features
        numeric_scaled = scaler.transform([numeric_values])
        
        # Encode categorical
        genre_encoded = encoders['Main_Genre'].transform([form_data.get('genre', 'Drama')])[0]
        country_encoded = encoders['Main_Country'].transform([form_data.get('country', 'United States of America')])[0]
        
        # Combine
        features = np.array([numeric_scaled[0].tolist() + [genre_encoded, country_encoded]])
        
        return features

# ==========================================
# ROUTES
# ==========================================
@app.route("/")
def home():
    """Trang chủ"""
    # Lấy danh sách genres và countries từ model nếu có
    genres = [
        "Action", "Adventure", "Animation", "Comedy", "Crime",
        "Documentary", "Drama", "Family", "Fantasy", "History",
        "Horror", "Music", "Mystery", "Romance", "Science Fiction",
        "TV Movie", "Thriller", "War", "Western"
    ]
    
    countries = [
        "United States of America", "United Kingdom", "France",
        "Germany", "Japan", "Canada", "Italy", "Spain",
        "Australia", "South Korea", "China", "India"
    ]
    
    return render_template("index.html", 
                         genres=genres, 
                         countries=countries,
                         model_name=MODEL_NAME,
                         model_metrics=MODEL_METRICS)

@app.route("/predict", methods=["POST"])
def predict():
    """Dự đoán thành công phim"""
    try:
        # Lấy dữ liệu từ form
        title = request.form.get("title", "").strip()
        
        # Validate
        if not title:
            flash("⚠️ Vui lòng nhập tên phim.", "error")
            return home()
        
        form_data = {
            'budget': request.form.get("budget", 0),
            'runtime': request.form.get("runtime", 120),
            'vote_average': request.form.get("director_rating", 5),
            'vote_count': request.form.get("actor_rating", 100),
            'release_year': request.form.get("release_year", 2024),
            'release_month': request.form.get("release_month", 1),
            'genre': request.form.get("genre", "Drama"),
            'country': request.form.get("country", "United States of America")
        }
        
        # Validate numeric inputs
        try:
            budget = float(form_data['budget'])
            runtime = float(form_data['runtime'])
            vote_average = float(form_data['vote_average'])
            vote_count = float(form_data['vote_count'])
            
            if budget <= 0 or runtime <= 0 or vote_count <= 0:
                flash("⚠️ Ngân sách, thời lượng và số lượng đánh giá phải lớn hơn 0.", "error")
                return home()
            
            if vote_average < 0 or vote_average > 10:
                flash("⚠️ Đánh giá trung bình phải từ 0 đến 10.", "error")
                return home()
                
        except ValueError:
            flash("⚠️ Vui lòng nhập các giá trị số hợp lệ.", "error")
            return home()
        
        # Chuẩn bị input
        logger.info(f"Dự đoán cho phim: {title}")
        input_data = prepare_input_data(form_data)
        
        # Dự đoán
        if USE_NEW_MODEL:
            pred_proba = model.predict_proba(input_data)[:, 1][0]
        else:
            pred_proba = model.predict_proba(input_data)[0][1]
            
        prediction = 1 if pred_proba >= BEST_THRESHOLD else 0
        
        logger.info(f"Probability: {pred_proba:.4f}, Threshold: {BEST_THRESHOLD:.4f}, Prediction: {prediction}")
        
        # Kết quả
        if prediction == 1:
            result_text = "Thành công"
            result_class = "success"
            result_icon = "🎉"
            confidence = pred_proba * 100
        else:
            result_text = "Không thành công"
            result_class = "failure"
            result_icon = "⚠️"
            confidence = (1 - pred_proba) * 100
        
        # Render kết quả
        return render_template("result.html",
                             title=title,
                             prediction=result_text,
                             confidence=round(confidence, 1),
                             probability=round(pred_proba * 100, 1),
                             color=result_class,
                             icon=result_icon,
                             budget=budget,  # Pass số thực, format trong template
                             genre=form_data['genre'],
                             vote_average=vote_average,
                             vote_count=int(vote_count),  # Pass số nguyên
                             runtime=int(runtime),  # Convert to int
                             release_year=int(form_data['release_year']),  # Convert to int
                             release_month=int(form_data['release_month']),  # Convert to int
                             country=form_data['country'],
                             model_name=MODEL_NAME,
                             threshold=round(BEST_THRESHOLD * 100, 1))
    
    except Exception as e:
        logger.error(f"Lỗi khi dự đoán: {str(e)}")
        flash(f"❌ Lỗi: {str(e)}", "error")
        return home()

@app.route("/data")
def data_analysis():
    """Trang phân tích dữ liệu"""
    try:
        from src.data_analysis import create_data_visualizations
        visualizations, stats = create_data_visualizations()
        return render_template("data.html", **visualizations, stats=stats)
    except Exception as e:
        logger.error(f"Lỗi khi tạo biểu đồ: {str(e)}")
        flash(f"⚠️ Lỗi khi tạo biểu đồ: {str(e)}", "error")
        return home()

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """API endpoint cho dự đoán"""
    try:
        data = request.get_json()
        
        # Chuẩn bị input
        input_df = prepare_input_data(data)
        
        # Dự đoán
        pred_proba = model.predict_proba(input_df)[:, 1][0]
        prediction = 1 if pred_proba >= BEST_THRESHOLD else 0
        
        return jsonify({
            'success': True,
            'prediction': int(prediction),
            'prediction_label': 'Thành công' if prediction == 1 else 'Không thành công',
            'probability': float(pred_proba),
            'confidence': float(pred_proba if prediction == 1 else 1 - pred_proba),
            'threshold': float(BEST_THRESHOLD),
            'model_name': MODEL_NAME
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route("/model-info")
def model_info():
    """Thông tin mô hình"""
    return jsonify({
        'model_name': MODEL_NAME,
        'threshold': float(BEST_THRESHOLD),
        'metrics': MODEL_METRICS,
        'status': 'active'
    })

@app.route("/css-test")
def css_test():
    """Trang test CSS"""
    return render_template('css_test.html')

# ==========================================
# ERROR HANDLERS
# ==========================================
@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return render_template('index.html'), 500

# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🎬 MOVIE SUCCESS PREDICTOR - ML WEB APP")
    logger.info("=" * 60)
    logger.info(f"📊 Model: {MODEL_NAME}")
    logger.info(f"🎯 F1-Score: {MODEL_METRICS.get('f1', 'N/A')}")
    logger.info(f"⚖️ Threshold: {BEST_THRESHOLD:.4f}")
    logger.info("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
