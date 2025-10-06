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
            'Production Countries': form_data.get('country', 'United States of America'),  # USED by model
            'Spoken Languages': 'English',  # USED by model 
            'Director': 'Unknown',  # Not used by model
            'Stars': 'Unknown',  # Not used by model
            
            # ROI will be calculated in engineer_features
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
                             country=form_data['country'],
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

@app.route("/api/ai-advice", methods=["POST"])
def ai_advice():
    """API endpoint để lấy lời khuyên từ Gemini AI"""
    
    # Fallback advice khi không connect được API
    fallback_advices = [
        """### Phân tích từ chuyên gia

**Đánh giá tổng quan:**
Dựa trên các chỉ số bạn cung cấp, phim có tiềm năng thương mại tốt. Với ngân sách và đánh giá hiện tại, việc tối ưu hóa chiến lược marketing sẽ là chìa khóa để tăng khả năng thành công.

**Điểm mạnh:**
- **Thể loại đang được ưa chuộng:** Thể loại phim này hiện đang có lượng khán giả ổn định
- **Chất lượng nội dung tốt:** Điểm đánh giá cho thấy phim được đánh giá cao
- **Thời điểm phát hành hợp lý:** Tháng phát hành nằm trong giai đoạn có lượng khán giả tốt

**Điểm cần cải thiện:**
- **Tối ưu ngân sách marketing:** Nên phân bổ 15-20% ngân sách cho quảng bá
- **Mở rộng kênh phân phối:** Cân nhắc phát hành đồng thời trên các nền tảng streaming
- **Tăng cường social media:** Đầu tư vào content marketing và influencer collaboration

**Khuyến nghị hành động:**
1. **Marketing & Phát hành:** Tập trung vào digital marketing và social media campaigns
2. **Ngân sách:** Dự phòng 10% ngân sách cho marketing bổ sung nếu cần
3. **Thị trường:** Nghiên cứu audience insights để tối ưu targeting
4. **Nội dung:** Tạo buzz thông qua behind-the-scenes và early screening events

**Kết luận:**
Phim có nền tảng tốt để thành công. Ưu tiên số 1 là xây dựng chiến lược marketing mạnh mẽ trong 2-3 tháng trước ngày ra mắt.""",

        """### Đánh giá chuyên sâu từ chuyên gia

**Nhìn chung:**
Các chỉ số cho thấy đây là một dự án cân đối. Thành công phụ thuộc nhiều vào execution và timing. Rủi ro ở mức trung bình, có thể giảm thiểu bằng chiến lược đúng đắn.

**Điểm nổi bật:**
- **Budget hợp lý:** Ngân sách phù hợp với quy mô và mục tiêu thị trường
- **Appeal rộng:** Thể loại có khả năng thu hút nhiều nhóm khán giả
- **Quality indicators tích cực:** Các chỉ số chất lượng đang ở mức khả quan

**Thách thức cần vượt qua:**
- **Cạnh tranh cao:** Cần chiến lược differentiation rõ ràng
- **Awareness thấp:** Đầu tư vào brand building và PR campaign
- **Distribution channels:** Mở rộng các kênh phân phối để tối đa hóa reach

**Roadmap đề xuất:**
1. **Pre-launch (3 tháng trước):**
   - Teaser campaign trên social media
   - Press release và media partnership
   - Early screening cho critics và influencers

2. **Launch (1 tháng trước):**
   - Full trailer release
   - Ticket pre-sale campaigns
   - Partnership với brands liên quan

3. **Post-launch:**
   - Word-of-mouth amplification
   - User-generated content campaigns
   - Extended distribution planning

**Xu hướng thị trường:**
Thị trường hiện tại đang chuyển dịch mạnh sang streaming và premium VOD. Cân nhắc chiến lược hybrid release để maximize revenue streams.

**Next steps:**
Tập trung vào việc xây dựng audience base trước khi ra mắt. Đây là yếu tố quyết định thành công.""",

        """### Phân tích chiến lược

**Tổng quan tình hình:**
Dự án có fundamentals tốt nhưng cần đầu tư đúng hướng vào marketing và distribution. Khả năng thành công ở mức 70-75% nếu execute tốt.

**Lợi thế cạnh tranh:**
- **Positioning rõ ràng:** Thể loại và concept dễ communicate với audience
- **Production value tốt:** Ngân sách cho phép đạt quality tiêu chuẩn
- **Market timing:** Thời điểm ra mắt có advantage về calendar

**Risk factors:**
- **Marketing budget:** Đảm bảo đủ resources cho awareness campaign
- **Competition:** Monitor competitors và adjust strategy accordingly
- **Audience engagement:** Build community và create FOMO

**Action items prioritized:**

**HIGH PRIORITY:**
- Finalize marketing strategy và allocate budget
- Secure distribution partnerships
- Plan premiere event và press tour

**MEDIUM PRIORITY:**
- Content marketing calendar
- Influencer collaboration deals
- Social media advertising campaigns

**LOW PRIORITY:**
- Merchandise planning
- Extended content (behind-scenes)
- Post-release engagement strategy

**Benchmark comparison:**
Các phim cùng thể loại và budget tương tự thường đạt ROI 1.5-2.5x nếu marketing tốt. Targeting ROI 2.0x là realistic với proper execution.

**Final recommendation:**
Proceed với confidence, nhưng stay flexible để adjust strategy dựa trên early feedback. Monitor metrics chặt chẽ và ready to pivot nếu cần.""",

        """### Góp ý từ chuyên gia phân tích phim

**Đánh giá ban đầu:**
Phim có foundation tốt với các metrics cơ bản đạt tiêu chuẩn. Cơ hội thành công cao nếu team focus vào execution và audience engagement.

**Những gì làm tốt:**
- **Clear target audience:** Dễ identify và reach target demographic
- **Production quality:** Specs cho thấy investment vào quality
- **Release strategy:** Timing và approach hợp lý với market conditions

**Areas for improvement:**
- **Brand awareness:** Cần campaign mạnh để build recognition
- **Competitive positioning:** Differentiate rõ ràng vs competitors
- **Distribution reach:** Maximize số lượng screens và platforms

**Strategic recommendations:**

**MARKETING:**
- Invest 20-25% total budget vào marketing
- Focus on digital và social media (70% of marketing budget)
- Influencer partnerships với micro-influencers (authentic engagement)
- PR campaign với major entertainment outlets

**DISTRIBUTION:**
- Negotiate với major cinema chains cho prime slots
- Plan streaming release 45-60 days post-theatrical
- Consider international markets nếu content permits

**CONTENT:**
- Create compelling trailers với strong hooks
- Behind-the-scenes content để build interest
- Interactive campaigns (polls, contests, fan engagement)

**Market insights:**
Thị trường đang recover post-pandemic, audience appetite cao cho quality content. Streaming không kill theatrical - chúng complement nhau.

**Comparable titles:**
[Tên phim tương tự] với budget và genre giống đã đạt success nhờ strong word-of-mouth và targeted marketing. Learn từ playbook của họ.

**Bottom line:**
Green light cho project. Success probability cao nếu execute plan đúng cách. Key metrics để track: opening weekend numbers, audience score, và week-over-week retention."""
    ]
    
    try:
        import google.generativeai as genai
        
        # Lấy dữ liệu phim từ request
        data = request.get_json()
        
        # Configure Gemini API
        # Sử dụng API key từ environment hoặc config
        api_key = 'AIzaSyBJJE-2b49j7R8ugRgNVYC-N32QPSE8xN0'
        genai.configure(api_key=api_key)
        
        # Tạo model
        model = genai.GenerativeModel('gemini-2.5-flash')  # Hoặc 'gemini-pro'
        
        # Tạo prompt cho AI
        prompt = f"""
Bạn là một chuyên gia phân tích phim và tư vấn sản xuất điện ảnh — nhưng hãy trả lời **như đang nói chuyện với một người bạn**: thân thiện, trực tiếp, dễ hiểu và thực tế.

Dựa trên kết quả dự đoán từ mô hình Machine Learning, hãy phân tích và tư vấn cho bộ phim dưới đây.

**Thông tin phim:**
- Tên phim: {data.get('title')}
- Dự đoán: {data.get('prediction')}
- Độ tin cậy: {data.get('confidence')}%
- Xác suất thành công: {data.get('probability')}%
- Ngân sách: ${data.get('budget'):,.0f}
- Thể loại: {data.get('genre')}
- Đánh giá trung bình: {data.get('vote_average')}/10
- Số lượng đánh giá: {data.get('vote_count'):,}
- Thời lượng: {data.get('runtime')} phút
- Năm phát hành: {data.get('release_year')}
- Tháng phát hành: {data.get('release_month')}
- Quốc gia: {data.get('country')}

Hãy trả lời bằng tiếng Việt, dùng **markdown** với heading `###`, bullet `-`, và nhấn mạnh bằng `**text**`. Giữ giọng **chuyên gia nhưng gần gũi**, và tập trung vào khuyến nghị có thể thực thi được.

Yêu cầu phần phân tích:

### 1. **Đánh giá tổng quan**
- Nói ngắn gọn (2–4 câu) về khả năng thành công dựa trên các chỉ số chính (probability, confidence, rating, budget, v.v).
- Nếu cần, cho biết mức rủi ro tổng thể: **Thấp / Trung bình / Cao**.

### 2. **Điểm mạnh**
- Liệt kê 3–5 yếu tố tích cực nổi bật (ví dụ: đề tài, độ nhận diện, điểm đánh giá, yếu tố thương mại).
- Mỗi bullet kèm 1 câu giải thích ngắn.

### 3. **Điểm yếu / Rủi ro**
- Liệt kê 3–5 vấn đề cần lưu ý (ví dụ: ngân sách không tương xứng, target kém rõ, cạnh tranh tháng chiếu).
- Với mỗi rủi ro, đề xuất 1 cách giảm thiểu cụ thể.

### 4. **Lời khuyên cụ thể (3–5 đề xuất hành động)**
- Chia làm 4 nhóm nhỏ: **Marketing & phát hành**, **Ngân sách & đầu tư**, **Thời điểm & thị trường mục tiêu**, **Cải thiện nội dung**.
- Với mỗi nhóm, đưa 1–2 khuyến nghị rõ ràng, có thể đo lường (ví dụ: thay đổi ngày ra rạp sang Q4, giảm 15% chi phí non-production, tập trung PR vào cộng đồng X).
- Nếu hợp lý, đề xuất KPI đơn giản để theo dõi (ví dụ: target CTR quảng cáo, số vé mục tiêu tuần đầu).

### 5. **So sánh thị trường & xu hướng**
- Nêu 2–3 phim tương tự (tên + lý do tương đồng) và rút ra bài học thực tế từ chúng.
- Kết luận ngắn về xu hướng thị trường hiện tại ảnh hưởng tới phim này (ví dụ: demand cho phim indie, thị trường streaming, mùa lễ hội).

### 6. **Kết luận ngắn & bước tiếp theo**
- Kết thúc bằng 1–2 câu tóm tắt: có nên đầu tư/đi tiếp không, và ưu tiên hành động tiếp theo là gì.
- (Thân mật) Hỏi một câu mở để tiếp: **"Bạn muốn mình bóc tách sâu vào phần marketing, ngân sách hay kịch bản?"**

Lưu ý: ưu tiên **thực tiễn** hơn là thuật ngữ học thuật — hãy trình bày sao cho nhà sản xuất/đội marketing dễ hiểu và có thể hành động ngay.
"""

        
        # Gọi API Gemini
        response = model.generate_content(prompt)
        
        # Trả về kết quả
        return jsonify({
            'success': True,
            'advice': response.text
        })
        
    except ImportError:
        logger.warning("google-generativeai package not installed, using fallback advice")
        import random
        fallback_advice = random.choice(fallback_advices)
        return jsonify({
            'success': True,
            'advice': fallback_advice,
            'fallback': True
        })
        
    except Exception as e:
        logger.error(f"Error calling Gemini API: {str(e)}, using fallback advice")
        import random
        fallback_advice = random.choice(fallback_advices)
        return jsonify({
            'success': True,
            'advice': fallback_advice,
            'fallback': True
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
