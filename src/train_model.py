import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import joblib
import os

# Load data
data_path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'Movies.csv')
df = pd.read_csv(data_path)

# Filter for Vietnamese movies (as per report)
df = df[df['Production Countries'].str.contains('Vietnam', na=False, case=False)]

# Clean data
df = df.dropna(subset=['Revenue', 'Budget', 'Runtime', 'Vote Average'])
df = df[df['Revenue'] > 0]
df = df[df['Budget'] > 0]
df = df[df['Vote Average'] > 0]

# Create target label (Success/Failure)
df['ROI'] = df['Revenue'] / df['Budget']
df['Success'] = ((df['ROI'] >= 1) & (df['Vote Average'] >= 6.5)).astype(int)

print(f"Dataset shape: {df.shape}")
print(f"Success rate: {df['Success'].mean():.2%}")

# Feature Engineering
df['Release Date'] = pd.to_datetime(df['Release Date'], errors='coerce')
df['Year'] = df['Release Date'].dt.year
df['Month'] = df['Release Date'].dt.month
df['Weekday'] = df['Release Date'].dt.weekday

# Process genres (take first genre)
df['Main_Genre'] = df['Genres'].str.strip('[]').str.split(',').str[0].str.strip(" '")

# Process production countries (take first)
df['Main_Country'] = df['Production Countries'].str.strip('[]').str.split(',').str[0].str.strip(" '")

# Select features
numeric_features = ['Budget', 'Runtime', 'Vote Average', 'Vote Count', 'Year', 'Month', 'Weekday']
categorical_features = ['Main_Genre', 'Main_Country']

# Encode categorical features
encoders = {}
encoded_features = []

for cat_feat in categorical_features:
    le = LabelEncoder()
    df[f'{cat_feat}_encoded'] = le.fit_transform(df[cat_feat].fillna('Unknown'))
    encoders[cat_feat] = le
    encoded_features.append(f'{cat_feat}_encoded')

# Combine features
features = numeric_features + encoded_features
X = df[features].copy()
y = df['Success']

# Scale numeric features (Min-Max as per report)
scaler = MinMaxScaler()
X_scaled = X.copy()
X_scaled[numeric_features] = scaler.fit_transform(X[numeric_features])

# Split data (stratified)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)

# Train models
models = {
    'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
    'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
}

results = {}

for name, model in models.items():
    # Train
    model.fit(X_train, y_train)

    # Predict
    y_pred = model.predict(X_test)

    # Evaluate
    results[name] = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'confusion_matrix': confusion_matrix(y_test, y_pred),
        'classification_report': classification_report(y_test, y_pred)
    }

    # Cross-validation (5-fold)
    cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='f1')
    results[name]['cv_f1_mean'] = cv_scores.mean()
    results[name]['cv_f1_std'] = cv_scores.std()

    print(f"\n{name}:")
    print(f"Accuracy: {results[name]['accuracy']:.3f}")
    print(f"F1-Score: {results[name]['f1']:.3f}")
    print(f"CV F1-Score: {results[name]['cv_f1_mean']:.3f} (+/- {results[name]['cv_f1_std']:.3f})")
    print("Confusion Matrix:")
    print(results[name]['confusion_matrix'])

# Choose best model (Random Forest as per report)
best_model = models['Random Forest']

# Save model and preprocessors
models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(models_dir, exist_ok=True)

joblib.dump(best_model, os.path.join(models_dir, 'movie_success_model.pkl'))
joblib.dump(scaler, os.path.join(models_dir, 'feature_scaler.pkl'))
joblib.dump(encoders, os.path.join(models_dir, 'encoders.pkl'))

# Save feature info
feature_info = {
    'numeric_features': numeric_features,
    'categorical_features': categorical_features,
    'features': features
}
joblib.dump(feature_info, os.path.join(models_dir, 'feature_info.pkl'))

print("\nModel trained and saved successfully!")
print(f"Training data shape: {X_train.shape}")
print(f"Test data shape: {X_test.shape}")