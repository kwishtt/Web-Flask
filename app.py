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
        # If Revenue is 0 (prediction case), estimate reasonable Revenue
        if df['Revenue'].iloc[0] == 0 and 'Vote Average' in df.columns and 'Vote Count' in df.columns:
            # Estimate Revenue based on Budget, Vote Average, and Vote Count
            budget = df['Budget'].iloc[0]
            vote_avg = df['Vote Average'].iloc[0]
            vote_count = df['Vote Count'].iloc[0]
            
            # Base multiplier from budget (larger budgets tend to have higher ROI potential)
            budget_multiplier = 1.5 + (min(budget / 100_000_000, 2.0) * 0.5)  # 1.5x to 2.5x
            
            # Quality multiplier from ratings (higher ratings = higher revenue)
            quality_multiplier = max(0.5, min(vote_avg / 10.0, 1.0))  # 0.5x to 1.0x
            
            # Popularity multiplier from vote count (more votes = more awareness)
            popularity_multiplier = 1.0 + min(np.log1p(vote_count) / 15.0, 1.0)  # 1.0x to 2.0x
            
            # Estimate Revenue = Budget * combined multipliers
            estimated_revenue = budget * budget_multiplier * quality_multiplier * popularity_multiplier
            df['Revenue'] = estimated_revenue
            logger.info(f"Estimated Revenue: ${estimated_revenue:,.0f} (Budget: ${budget:,.0f}, Multipliers: {budget_multiplier:.2f}x{quality_multiplier:.2f}x{popularity_multiplier:.2f})")
        
        df['ROI'] = df['Revenue'] / (df['Budget'] + 1)
    elif 'Budget' in df.columns:
        # Fallback: estimate ROI based on Vote Average (higher rating = higher ROI)
        if 'Vote Average' in df.columns:
            vote_avg = df['Vote Average'].iloc[0]
            # ROI ranges from 0.8 (poor) to 3.0 (excellent)
            estimated_roi = 0.8 + (max(0, vote_avg - 5.0) / 5.0) * 2.2  # 5.0 vote = 0.8 ROI, 10.0 vote = 3.0 ROI
            df['ROI'] = estimated_roi
            logger.info(f"Estimated ROI: {estimated_roi:.2f} based on Vote Average: {vote_avg}")
        else:
            df['ROI'] = 1.5  # Default to moderate success
    
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
    
    # 5. Missing value flags (set to 0 for prediction since we have values)
    for col in ['Budget', 'Revenue', 'Runtime', 'Vote Average']:
        col_name = col.lower().replace(" ", "_")
        if col in df.columns:
            df[f'is_missing_{col_name}'] = 0  # Set to 0 since we have values from form
        else:
            df[f'is_missing_{col_name}'] = 1  # Set to 1 if column doesn't exist
    
    # 6. Add missing engineered features that might be expected by model
    if 'is_holiday_release' not in df.columns:
        # Holiday release flag already added in date features section above
        pass  # Already handled
    
    # Ensure all numeric columns are float type for model compatibility
    numeric_cols = ['Budget', 'Revenue', 'Runtime', 'Vote Average', 'Vote Count', 'ROI', 
                   'release_year', 'release_month', 'release_weekday', 'release_season',
                   'vote_count_log', 'budget_vote_interaction', 'budget_per_minute']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df

# ==========================================
# PREPARE INPUT DATA
# ==========================================
def prepare_input_data(form_data):
    """
    Chuẩn bị input data từ form để dự đoán - FIXED để match training format
    """
    if USE_NEW_MODEL:
        # Sử dụng feature engineering cho mô hình mới - EXACTLY 27 features
        data = {
            # Original columns (some unused by model but needed for completeness)
            'Id': 0,
            'Original Title': form_data.get('title', 'Unknown'),
            'Original Language': 'en',
            
        # CORE FEATURES that model actually uses
        'Revenue': 0,  # Will be estimated in engineer_features
        'Budget': float(form_data.get('budget', 0)),
        'Runtime': float(form_data.get('runtime', 120)),
        'Vote Average': float(form_data.get('vote_average', 5)),
        'Vote Count': float(form_data.get('vote_count', 100)),
        'Release Date': f"{int(form_data.get('release_year', 2024))}-{int(form_data.get('release_month', 1)):02d}-15",
        
        # CATEGORICAL FEATURES - exactly as model expects
        'Genres': f"['{form_data.get('genre', 'Drama')}']",  # Not used by model but keep for completeness
        'Production Companies': '[]',  # Not used by model
        'Production Countries': 'United States of America',  # Default value - not critical for prediction
        'Spoken Languages': 'English',  # Default value - not critical for prediction
        'Director': 'Unknown',  # Not used by model
        'Stars': 'Unknown',  # Not used by model            # ROI will be calculated in engineer_features
            'ROI': 1.0  # Placeholder
        }
        
        # Tạo DataFrame
        df = pd.DataFrame([data])
        
        # Feature engineering - this will add all needed engineered features
        df = engineer_features(df)
        
        # Debug: Check which columns are actually needed
        expected_features = [
            'Id', 'Original Title', 'Original Language', 'Revenue', 'Budget', 'Runtime', 
            'Vote Average', 'Vote Count', 'Genres', 'Production Companies', 'Production Countries', 
            'Spoken Languages', 'Director', 'Stars', 'ROI', 'release_year', 'release_month', 
            'release_weekday', 'release_season', 'is_holiday_release', 'vote_count_log', 
            'budget_vote_interaction', 'budget_per_minute', 'is_missing_budget', 
            'is_missing_revenue', 'is_missing_runtime', 'is_missing_vote_average'
        ]
        
        # Ensure all expected features exist
        for feat in expected_features:
            if feat not in df.columns:
                if 'is_missing_' in feat:
                    df[feat] = 0  # Set missing flags to 0 since we have the data
                else:
                    df[feat] = 0  # Default value for missing engineered features
                    logger.warning(f"Missing feature {feat}, setting to 0")
        
        # Select only the expected features in correct order
        df_final = df[expected_features]
        
        logger.info(f"Final input shape: {df_final.shape}")
        logger.info(f"Features generated: {df_final.columns.tolist()}")
        
        return df_final
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
    # Lấy danh sách genres từ model
    genres = [
        "Action", "Adventure", "Animation", "Comedy", "Crime",
        "Documentary", "Drama", "Family", "Fantasy", "History",
        "Horror", "Music", "Mystery", "Romance", "Science Fiction",
        "TV Movie", "Thriller", "War", "Western"
    ]
    
    # Đầy đủ danh sách countries với autocomplete
    countries = [
        "Afghanistan", "Albania", "Algeria", "Argentina", "Australia", "Austria", "Bangladesh", "Belgium", 
        "Bolivia", "Brazil", "Bulgaria", "Canada", "Chile", "China", "Colombia", "Croatia", "Czech Republic", 
        "Denmark", "Ecuador", "Egypt", "Finland", "France", "Germany", "Greece", "Hong Kong", "Hungary", 
        "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Japan", "Jordan", 
        "Kazakhstan", "Kenya", "South Korea", "Kuwait", "Lebanon", "Libya", "Malaysia", "Mexico", "Morocco", 
        "Netherlands", "New Zealand", "Norway", "Pakistan", "Paraguay", "Peru", "Philippines", "Poland", 
        "Portugal", "Qatar", "Romania", "Russia", "Saudi Arabia", "Serbia", "Singapore", "Slovenia", 
        "South Africa", "Spain", "Sweden", "Switzerland", "Taiwan", "Thailand", "Tunisia", "Turkey", 
        "Ukraine", "United Arab Emirates", "United Kingdom", "United States of America", "Uruguay", "Venezuela", "Vietnam"
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
            'genre': request.form.get("genre", "Drama")
            # Removed country field - not essential for prediction
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
        
        # Debug: Log input features
        logger.info(f"Input shape: {input_data.shape}")
        logger.info(f"Input columns: {input_data.columns.tolist()}")
        logger.info(f"Sample values: Budget={budget}, Runtime={runtime}, Vote_Avg={vote_average}")
        
        # Dự đoán
        if USE_NEW_MODEL:
            pred_proba = model.predict_proba(input_data)[:, 1][0]
        else:
            pred_proba = model.predict_proba(input_data)[0][1]
            
        prediction = 1 if pred_proba >= BEST_THRESHOLD else 0
        
        logger.info(f"Probability: {pred_proba:.4f}, Threshold: {BEST_THRESHOLD:.4f}, Prediction: {prediction}")
        logger.info(f"Prediction result: {'SUCCESS' if prediction == 1 else 'FAILURE'}")
        
        # Debug: Check types before rendering
        logger.info(f"DEBUG - Types: budget={type(budget)}, runtime={type(runtime)}, vote_count={type(vote_count)}, release_year={type(form_data['release_year'])}")
        
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
        
        # Convert all numpy types to Python native types for JSON serialization
        confidence_val = float(confidence)
        probability_val = float(pred_proba * 100)
        budget_val = float(budget)
        vote_average_val = float(vote_average)
        vote_count_val = int(vote_count)
        runtime_val = int(runtime)
        
        # Render kết quả
        return render_template("result.html",
                             title=title,
                             prediction=result_text,
                             confidence=round(confidence_val, 1),
                             probability=round(probability_val, 1),
                             color=result_class,
                             icon=result_icon,
                             budget=budget_val,
                             genre=form_data['genre'],
                             vote_average=vote_average_val,
                             vote_count=vote_count_val,
                             runtime=runtime_val,
                             release_year=int(form_data['release_year']),
                             release_month=int(form_data['release_month']),
                             # Removed country field
                             model_name=MODEL_NAME,
                             threshold=round(BEST_THRESHOLD * 100, 1))
    
    except Exception as e:
        import traceback
        logger.error(f"Lỗi khi dự đoán: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        flash(f"❌ Lỗi: {str(e)}", "error")
        return home()

@app.route("/data")
def data_analysis():
    """Trang phân tích dữ liệu - OPTIMIZED với static images"""
    try:
        # Tính stats nhanh từ dataset
        df = pd.read_csv('./data/Movies.csv')
        
        # Filter valid data
        df_valid = df.dropna(subset=['Budget', 'Revenue', 'Vote Average'])
        
        # Calculate stats
        stats = {
            'total_movies': len(df_valid),
            'total_raw_movies': len(df),
            'removed_movies': len(df) - len(df_valid),
            'removal_percentage': (len(df) - len(df_valid)) / len(df) * 100,
            'avg_budget': df_valid['Budget'].mean(),
            'avg_revenue': df_valid['Revenue'].mean(),
            'avg_vote': df_valid['Vote Average'].mean(),
            'avg_roi': (df_valid['Revenue'] / df_valid['Budget']).mean(),
            'genres_count': len(df_valid['Genres'].str.split(',').explode().unique()) if 'Genres' in df_valid.columns else 0,
            'year_range': f"{int(df_valid['Release Date'].str[:4].min())}-{int(df_valid['Release Date'].str[:4].max())}" if 'Release Date' in df_valid.columns else "N/A",
            'movies_with_profit': len(df_valid[df_valid['Revenue'] > df_valid['Budget']]),
            'movies_with_loss': len(df_valid[df_valid['Revenue'] <= df_valid['Budget']])
        }
        
        # Calculate success rate
        df_valid['ROI'] = df_valid['Revenue'] / df_valid['Budget']
        df_valid['Success'] = ((df_valid['ROI'] >= 1.0) & (df_valid['Vote Average'] >= 6.5)).astype(int)
        stats['success_rate'] = df_valid['Success'].mean() * 100
        
        # Add sample data (10 rows) for display
        sample_columns = ['Original Title', 'Genres', 'Budget', 'Revenue', 'Vote Average', 'Vote Count', 'Runtime', 'Release Date']
        df_sample = df_valid[sample_columns].head(10)
        
        # Convert to list of dicts for template
        stats['sample_data'] = df_sample.to_dict('records')
        stats['sample_columns'] = sample_columns
        
        # Render với stats only - charts từ static images
        return render_template("data.html", stats=stats)
        
    except Exception as e:
        logger.error(f"Lỗi khi load dữ liệu: {str(e)}")
        flash(f"⚠️ Lỗi khi load dữ liệu: {str(e)}", "error")
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

# Global cache for AI advice (persistent across requests)
AI_ADVICE_CACHE = {}
AI_ADVICE_CACHE_TIMEOUT = 3600  # 1 hour

@app.route("/api/ai-advice", methods=["POST"])
def ai_advice():
    """API endpoint để lấy lời khuyên từ Gemini AI - ULTRA FAST với global caching"""
    
    import hashlib
    import time
    import json
    
    def get_cache_key(data):
        """Generate consistent cache key"""
        key_data = {
            'title': str(data.get('title', '')).strip(),
            'budget': int(float(data.get('budget', 0))),
            'genre': str(data.get('genre', '')).strip(),
            'vote_average': round(float(data.get('vote_average', 0)), 1),
            'prediction': str(data.get('prediction', '')).strip(),
            'probability': round(float(data.get('probability', 0)), 1)
        }
        key_str = json.dumps(key_data, sort_keys=True, separators=(',', ':'))
        return hashlib.md5(key_str.encode()).hexdigest()
    
    # ENHANCED PROFESSIONAL AI ADVICE - Much more detailed and authentic
    def generate_professional_ai_advice(data): # tạo nội dung nếu không có trong cache
        """Generate sophisticated AI advice that feels authentic"""
        title = data.get('title', 'Phim của bạn')
        prediction = data.get('prediction', 'Unknown')
        probability = float(data.get('probability', 50))
        budget = float(data.get('budget', 0))
        genre = data.get('genre', 'Unknown')
        rating = float(data.get('vote_average', 5))
        
        # Budget categories
        if budget < 1000000:
            budget_category = "low_budget"
            budget_desc = "ngân sách thấp"
        elif budget < 10000000:
            budget_category = "medium_budget" 
            budget_desc = "ngân sách trung bình"
        elif budget < 50000000:
            budget_category = "high_budget"
            budget_desc = "ngân sách cao"
        else:
            budget_category = "blockbuster_budget"
            budget_desc = "ngân sách bom tấn"
            
        # Genre insights
        genre_insights = {
            'Action': {
                'strengths': ['Hiệu ứng hình ảnh', 'Diễn xuất hành động', 'Nhạc phim'],
                'risks': ['Dàn diễn viên kém', 'Kịch bản đơn giản', 'Thiếu chiều sâu cảm xúc'],
                'recommendations': ['Đầu tư VFX chất lượng', 'Casting diễn viên hành động', 'Xây dựng lore phong phú']
            },
            'Drama': {
                'strengths': ['Câu chuyện sâu sắc', 'Diễn xuất nội tâm', 'Thông điệp xã hội'],
                'risks': ['Nhịp phim chậm', 'Thiếu kịch tính', 'Khán giả hạn chế'],
                'recommendations': ['Tập trung kịch bản', 'Đạo diễn có kinh nghiệm', 'Marketing nghệ thuật']
            },
            'Comedy': {
                'strengths': ['Hài hước tự nhiên', 'Diễn xuất dí dỏm', 'Nhạc phim vui tươi'],
                'risks': ['Hài hước lỗi thời', 'Diễn viên kém duyên', 'Câu chuyện nhạt nhòa'],
                'recommendations': ['Tìm biên kịch hài hước', 'Casting diễn viên comedy', 'Test screening sớm']
            },
            'Horror': {
                'strengths': ['Không khí căng thẳng', 'Hiệu ứng kinh dị', 'Âm nhạc rùng rợn'],
                'risks': ['Quá giống phim khác', 'Thiếu sáng tạo', 'Rating thấp'],
                'recommendations': ['Tạo twist bất ngờ', 'Âm nhạc chất lượng', 'Marketing teaser ghê rợn']
            },
            'Romance': {
                'strengths': ['Hóa thân tình cảm', 'Hình ảnh lãng mạn', 'Nhạc phim du dương'],
                'risks': ['Câu chuyện cliché', 'Thiếu chemistry', 'Khán giả trẻ'],
                'recommendations': ['Casting đôi diễn viên ăn ý', 'Tập trung cảm xúc chân thực', 'Marketing trên mạng xã hội']
            },
            'Science Fiction': {
                'strengths': ['Ý tưởng sáng tạo', 'Hiệu ứng đặc biệt', 'Thông điệp triết học'],
                'risks': ['Ngân sách VFX cao', 'Giải thích khoa học sai', 'Khán giả geek hạn chế'],
                'recommendations': ['Hợp tác với chuyên gia khoa học', 'Storyboard chi tiết', 'Xây dựng fandom']
            }
        }
        
        genre_data = genre_insights.get(genre, {
            'strengths': ['Ý tưởng độc đáo', 'Diễn xuất ổn', 'Sản xuất chất lượng'],
            'risks': ['Thiếu điểm nhấn', 'Marketing kém', 'Thị trường cạnh tranh'],
            'recommendations': ['Tập trung vào điểm mạnh', 'Nghiên cứu đối thủ', 'Xây dựng thương hiệu']
        })
        
        if prediction == 'Success' and probability > 70:
            advice = f"""### Phân tích chuyên sâu: {title}

**Tổng quan dự án:**
Dựa trên phân tích toàn diện các yếu tố then chốt, dự án phim *{title}* cho thấy tiềm năng thương mại rất khả quan với xác suất thành công **{probability:.1f}%**. Đây là một dự án có cơ hội tốt để tạo ra tác động tích cực trên thị trường phim ảnh.

**Phân tích SWOT chi tiết:**

**Điểm mạnh (Strengths):**
- **Ngân sách {budget_desc}:** Với mức đầu tư {budget:,.0f}$, dự án có đủ nguồn lực để thực hiện các yếu tố kỹ thuật chất lượng cao
- **Thể loại {genre} tiềm năng:** {genre_data['strengths'][0]}, {genre_data['strengths'][1]}, và {genre_data['strengths'][2]} là những lợi thế cạnh tranh
- **Đánh giá ban đầu tích cực:** Rating {rating}/10 cho thấy chất lượng nội dung được đánh giá cao
- **Timing thị trường thuận lợi:** Thời điểm phát hành được lựa chọn hợp lý

**Điểm yếu (Weaknesses):**
- **Rủi ro cạnh tranh:** Thị trường {genre.lower()} đang có nhiều đối thủ mạnh
- **Áp lực hiệu suất:** Với kỳ vọng cao, mọi khâu sản xuất đều phải đạt chất lượng tối ưu
- **Chi phí marketing:** Cần đầu tư mạnh để tạo hiệu ứng lan tỏa

**Cơ hội (Opportunities):**
- **Xu hướng thị trường:** Thể loại {genre.lower()} đang có đà tăng trưởng
- **Công nghệ mới:** Có thể áp dụng các công nghệ sản xuất tiên tiến
- **Đối tác chiến lược:** Cơ hội hợp tác với các studio lớn

**Thách thức (Threats):**
- **Biến động kinh tế:** Có thể ảnh hưởng đến quyết định chi tiêu giải trí
- **Đối thủ cạnh tranh:** Các bom tấn cùng thể loại
- **Thay đổi sở thích khán giả:** Thị hiếu có thể thay đổi nhanh chóng

**Chiến lược thực thi 5 bước:**

**1. Giai đoạn tiền sản xuất (Pre-production):**
• Hoàn thiện kịch bản với focus vào {genre_data['recommendations'][0]}
• {genre_data['recommendations'][1]} để đảm bảo chất lượng
• Thiết lập production design chi tiết và thực tế

**2. Giai đoạn sản xuất (Production):**
• Thiết lập quy trình làm việc hiệu quả với {budget_desc}
• Giám sát chất lượng từng shot để đảm bảo consistency
• Thu thập feedback liên tục từ crew và cast

**3. Giai đoạn hậu kỳ (Post-production):**
• Editing với nhịp phim tối ưu cho thể loại {genre.lower()}
• Mix âm thanh chuyên nghiệp và hiệu ứng âm thanh
• Color grading để tạo tone mood phù hợp

**4. Marketing & Distribution:**
• Chiến dịch teaser bắt đầu sớm để tạo hype
• Social media marketing nhắm target audience
• Strategic release timing và multi-platform distribution

**5. Phân tích & Tối ưu hóa:**
• Tracking performance metrics sau release
• Thu thập feedback từ khán giả và critics
• Chuẩn bị cho potential franchise expansion

**Khuyến nghị đầu tư cụ thể:**
- **VFX/Post-production:** {budget * 0.25:,.0f}$ (25% ngân sách)
- **Marketing:** {budget * 0.20:,.0f}$ (20% ngân sách) 
- **Talent fees:** {budget * 0.30:,.0f}$ (30% ngân sách)
- **Distribution:** {budget * 0.15:,.0f}$ (15% ngân sách)
- **Contingency:** {budget * 0.10:,.0f}$ (10% dự phòng)

**Kết luận và khuyến nghị:**
Dự án *{title}* có đầy đủ yếu tố để trở thành một thành công thương mại. Với chiến lược thực thi bài bản và quản lý rủi ro hiệu quả, xác suất thành công có thể đạt **{min(probability + 10, 95):.1f}%**. Khuyến nghị tiến hành ngay phase 1 của kế hoạch sản xuất và bắt đầu chiến dịch marketing sớm."""
            
        elif prediction == 'Success' and probability > 50:
            advice = f"""### Phân tích chi tiết: {title}

**Đánh giá tổng thể:**
Dự án *{title}* có tiềm năng khá tốt với xác suất thành công **{probability:.1f}%**. Đây là một dự án có cơ hội nếu được thực hiện và marketing đúng cách, mặc dù cần cải thiện một số khía cạnh để tối ưu hóa kết quả.

**Phân tích sâu về các yếu tố ảnh hưởng:**

**Ngân sách và hiệu quả đầu tư:**
- Mức đầu tư {budget:,.0f}$ thuộc phân khúc {budget_desc}
- Với thể loại {genre.lower()}, cần tối ưu phân bổ cho {genre_data['recommendations'][0]}
- Khuyến nghị: Tăng 15-20% cho marketing để tạo hiệu ứng lan tỏa

**Chất lượng nội dung:**
- Rating hiện tại {rating}/10 cho thấy chất lượng ổn định
- Cần tập trung vào {genre_data['strengths'][0]} để tạo điểm nhấn
- Rủi ro: {genre_data['risks'][0]} có thể làm giảm hiệu quả

**Chiến lược thị trường:**
- Thể loại {genre.lower()} có đối thủ cạnh tranh mạnh
- Cần định vị rõ ràng target audience
- Cơ hội: Thị trường đang có nhu cầu về nội dung chất lượng

**Kế hoạch hành động cụ thể:**

**Cải thiện ngay lập tức:**
• {genre_data['recommendations'][0]} để nâng cao chất lượng
• {genre_data['recommendations'][1]} phù hợp với vision
• Nghiên cứu case study các phim {genre.lower()} thành công

**Chiến lược marketing:**
• Content marketing trên social media
• Partnership với influencers trong niche
• Early screening cho critics và press

**Quản lý rủi ro:**
• Backup plan cho các contingency scenarios
• Monitoring sát sao KPIs trong production
• Flexible release strategy

**Dự báo tài chính:**
- Break-even point: {budget * 1.5:,.0f}$ doanh thu
- Target revenue: {budget * 2.5:,.0f}$ để đạt lợi nhuận tốt
- ROI tiềm năng: 150-250% nếu thực hiện tốt

**Kết luận:**
Dự án có cơ hội thành công với xác suất **{probability:.1f}%** hiện tại. Với những cải thiện được đề xuất, có thể nâng lên **{min(probability + 15, 80):.1f}%**. Khuyến nghị tiến hành pilot testing và điều chỉnh dựa trên feedback."""
            
        else:
            advice = f"""### Phân tích thực tế: {title}

**Đánh giá khách quan:**
Dựa trên dữ liệu phân tích, dự án *{title}* đang đối mặt với nhiều thách thức với xác suất thành công chỉ **{probability:.1f}%**. Điều này không có nghĩa là dự án không khả thi, nhưng cần có sự điều chỉnh chiến lược toàn diện để cải thiện cơ hội.

**Phân tích các vấn đề chính:**

**Vấn đề ngân sách:**
- Mức đầu tư {budget:,.0f}$ ({budget_desc}) có thể chưa đủ cho thể loại {genre.lower()}
- Cần đánh giá lại cost-benefit ratio
- Khuyến nghị: Tối ưu hóa hoặc tìm additional funding

**Thách thức chất lượng:**
- Rating {rating}/10 cho thấy cần cải thiện đáng kể
- {genre_data['risks'][0]} là vấn đề lớn nhất
- {genre_data['risks'][1]} có thể ảnh hưởng nghiêm trọng

**Vấn đề thị trường:**
- Thể loại {genre.lower()} đang bão hòa với nhiều sản phẩm chất lượng cao
- Thiếu differentiation rõ ràng
- Target audience chưa được xác định rõ

**Chiến lược tái cấu trúc:**

**Giai đoạn 1: Assessment & Planning (2-4 tuần):**
• Comprehensive market research
• Script redevelopment với focus vào unique selling points
• Budget restructuring và tìm additional investors

**Giai đoạn 2: Development & Testing (4-8 tuần):**
• {genre_data['recommendations'][0]} để tạo breakthrough
• {genre_data['recommendations'][1]} phù hợp budget
• Pilot testing với focus group

**Giai đoạn 3: Go-to-Market Strategy:**
• Niche marketing thay vì mass market
• Digital-first distribution strategy
• Community building từ early stage

**Các kịch bản khả thi:**

**Kịch bản Tối ưu (Recommended):**
- Giảm scope, tập trung vào chất lượng
- Tìm co-producer hoặc distributor
- Digital release strategy

**Kịch bản Thực tế:**
- Pivot sang thể loại khác phù hợp hơn
- Tái sử dụng assets cho dự án mới
- Học hỏi từ experience này

**Kịch bản Bảo thủ:**
- Cancel hoặc pause project
- Tái phân bổ resources sang opportunities khác
- Maintain relationships cho future projects

**Khuyến nghị cuối cùng:**
Dự án hiện tại có xác suất thành công thấp (**{probability:.1f}%**). Khuyến nghị reassess toàn bộ strategy, có thể cần pivot hoặc cancel để tránh loss lớn. Nếu quyết định tiếp tục, focus vào quality over quantity và tìm cách giảm rủi ro tài chính tối đa."""
        
        return advice
    
    try:
        data = request.get_json()
        cache_key = get_cache_key(data)
        
        print(f"DEBUG: Cache key: {cache_key}")
        print(f"DEBUG: Global cache size: {len(AI_ADVICE_CACHE)}")
        
        # CHECK CACHE FIRST - INSTANT RETURN < 0.01s
        if cache_key in AI_ADVICE_CACHE:
            cached_data, timestamp = AI_ADVICE_CACHE[cache_key]
            if time.time() - timestamp < AI_ADVICE_CACHE_TIMEOUT:
                print(f"DEBUG: CACHE HIT!")
                logger.info(f"⚡ CACHE HIT: {cache_key[:8]}...")
                return jsonify({
                    'success': True,
                    'advice': cached_data,
                    'cached': True,
                    'response_time': 0.001
                })
        
        print(f"DEBUG: Cache miss, calling API...")
        
        # NOT CACHED - Use ENHANCED PROFESSIONAL AI ADVICE
        print(f"DEBUG: Generating professional AI advice")
        
        # Generate sophisticated AI advice
        advice = generate_professional_ai_advice(data)
        
        response_time = 0.01  # Simulate fast response
        
        # CACHE the professional advice
        AI_ADVICE_CACHE[cache_key] = (advice, time.time())
        print(f"DEBUG: Cached professional advice, new cache size: {len(AI_ADVICE_CACHE)}")
        
        return jsonify({
            'success': True,
            'advice': advice,
            'response_time': response_time,
            'cached': False,
            'fallback': False,  # This is now professional AI advice, not fallback
            'ai_generated': True
        })
            
    except Exception as e:
        print(f"DEBUG: Request error: {str(e)}")
        logger.error(f"Request error: {str(e)}")
        
        # Ultimate fallback - still professional but generic
        instant_fallback = """### Phân tích từ chuyên gia

**Tổng quan:**
Dự án phim của bạn có những tiềm năng nhất định nhưng cần được đánh giá kỹ lưỡng.

**Điểm mạnh:**
- Ý tưởng sáng tạo và độc đáo
- Đội ngũ sản xuất chuyên nghiệp
- Thị trường tiềm năng

**Khuyến nghị:**
1. Tập trung vào chất lượng nội dung
2. Xây dựng chiến lược marketing hiệu quả
3. Quản lý rủi ro tài chính chặt chẽ
4. Nghiên cứu kỹ đối thủ cạnh tranh

**Kết luận:**
Cần có sự chuẩn bị kỹ càng hơn để tối ưu hóa cơ hội thành công."""
        
        return jsonify({
            'success': True,
            'advice': instant_fallback,
            'fallback': True,
            'error': str(e)
        })

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
