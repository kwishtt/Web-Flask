from flask import Flask, render_template, request, flash
import joblib
import numpy as np
import os
from data_analysis import create_data_visualizations

app = Flask(__name__, template_folder='../web/templates', static_folder='../web/static')
app.config["SECRET_KEY"] = "movie-success-predictor-secret"

# Load model and preprocessors
models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
model = joblib.load(os.path.join(models_dir, 'movie_success_model.pkl'))
scaler = joblib.load(os.path.join(models_dir, 'feature_scaler.pkl'))
encoders = joblib.load(os.path.join(models_dir, 'encoders.pkl'))
feature_info = joblib.load(os.path.join(models_dir, 'feature_info.pkl'))

# Get available genres and countries
genres = list(encoders['Main_Genre'].classes_)
countries = list(encoders['Main_Country'].classes_)

@app.route("/")
def home():
    return render_template("index.html", genres=genres, countries=countries)

@app.route("/data")
def data_analysis():
    """Data visualization and analysis page"""
    try:
        visualizations, stats = create_data_visualizations()
        return render_template("data.html", **visualizations, stats=stats)
    except Exception as e:
        flash(f"Lỗi khi tạo biểu đồ: {str(e)}", "error")
        return render_template("index.html", genres=genres, countries=countries)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Get form data
        title = request.form.get("title", "").strip()
        budget = float(request.form.get("budget", 0))
        genre = request.form.get("genre")
        vote_average = float(request.form.get("director_rating", 5))
        vote_count = float(request.form.get("actor_rating", 100))
        runtime = float(request.form.get("runtime", 120))
        release_year = int(request.form.get("release_year", 2024))
        release_month = int(request.form.get("release_month", 1))
        country = request.form.get("country")

        # Validate inputs
        if not title:
            flash("Vui lòng nhập tên phim.", "error")
            return render_template("index.html", genres=genres, countries=countries)

        if budget <= 0 or vote_average < 0 or vote_average > 10 or vote_count <= 0 or runtime <= 0:
            flash("Vui lòng nhập các giá trị hợp lệ.", "error")
            return render_template("index.html", genres=genres, countries=countries)

        # Calculate weekday (approximate - using 15th of month)
        from datetime import datetime
        try:
            release_date = datetime(release_year, release_month, 15)
            weekday = release_date.weekday()
        except:
            weekday = 0  # Default to Monday

        # Encode categorical features
        genre_encoded = encoders['Main_Genre'].transform([genre])[0]
        country_encoded = encoders['Main_Country'].transform([country])[0]

        # Prepare features in correct order (numeric first, then encoded categorical)
        numeric_values = [
            budget, runtime, vote_average, vote_count,
            release_year, release_month, weekday
        ]
        
        # Scale only numeric features
        numeric_scaled = scaler.transform([numeric_values])
        
        # Combine scaled numeric with encoded categorical
        features = np.array([numeric_scaled[0].tolist() + [genre_encoded, country_encoded]])

        # Predict
        prediction = model.predict(features)[0]
        prediction_proba = model.predict_proba(features)[0]

        # Determine result
        if prediction == 1:
            result = "Thành công"
            color = "success"
            confidence = prediction_proba[1]
        else:
            result = "Không thành công"
            color = "danger"
            confidence = prediction_proba[0]

        return render_template("result.html",
                             title=title,
                             prediction=result,
                             confidence=round(confidence * 100, 1),
                             color=color,
                             budget=budget,
                             genre=genre,
                             vote_average=vote_average,
                             vote_count=vote_count,
                             runtime=runtime,
                             release_year=release_year,
                             release_month=release_month,
                             country=country)

    except Exception as e:
        flash(f"Lỗi: {str(e)}", "error")
        return render_template("index.html", genres=genres, countries=countries)

if __name__ == "__main__":
    app.run(debug=True)
