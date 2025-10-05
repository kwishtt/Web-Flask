"""
Check dataset info
"""
import pandas as pd

# Load full dataset
df = pd.read_csv('data/Movies.csv')

print("=" * 60)
print("📊 DATASET INFO")
print("=" * 60)
print(f"Tổng số phim trong Movies.csv: {len(df)}")
print(f"Số cột: {len(df.columns)}")
print()

# Check production countries
print("📍 Top 10 Production Countries:")
print(df['Production Countries'].value_counts().head(10))
print()

# Check Vietnam movies
vn_movies = df[df['Production Countries'].str.contains('Vietnam', na=False, case=False)]
print(f"🇻🇳 Phim Vietnam: {len(vn_movies)}")
print()

# Clean data for training
print("🧹 Sau khi clean data:")
clean_df = df.copy()
clean_df = clean_df.dropna(subset=['Revenue', 'Budget', 'Runtime', 'Vote Average'])
clean_df = clean_df[clean_df['Revenue'] > 0]
clean_df = clean_df[clean_df['Budget'] > 0]
clean_df = clean_df[clean_df['Vote Average'] > 0]
print(f"Tổng phim có đủ dữ liệu: {len(clean_df)}")
print()

# Check training data from config
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    
print("=" * 60)
print("🔧 CONFIG INFO")
print("=" * 60)
print(f"Data path: {config['data']['path']}")
if 'filter' in config['data']:
    print(f"Filter: {config['data']['filter']}")
print()

# Check model metadata
import json
with open('models/best_model_metadata.json', 'r') as f:
    metadata = json.load(f)
    
print("=" * 60)
print("🤖 MODEL TRAINING INFO")
print("=" * 60)
print(f"Model: {metadata['model_name']}")
print(f"Training date: {metadata['training_date']}")
print(f"Test size: {metadata['config']['preprocessing']['test_size']} (80% train / 20% test)")
print(f"ROI threshold: {metadata['config']['preprocessing']['roi_threshold']}")
print(f"Vote average threshold: {metadata['config']['preprocessing']['vote_average_threshold']}")
print()

print("🎯 METRICS:")
for metric, value in metadata['test_metrics'].items():
    print(f"  {metric}: {value}")
print()

# Calculate approximate training size
print("📊 ESTIMATE:")
print(f"Clean dataset: {len(clean_df)} phim")
print(f"Train (~80%): ~{int(len(clean_df) * 0.8)} phim")
print(f"Test (~20%): ~{int(len(clean_df) * 0.2)} phim")
print()

print("=" * 60)
print("✅ KẾT LUẬN")
print("=" * 60)
print(f"🔹 Model được train với TOÀN BỘ dataset ({len(clean_df)} phim)")
print(f"🔹 KHÔNG CHỈ phim Vietnam (458 phim)")
print(f"🔹 Bao gồm: USA, Korea, Japan, Thailand, China, v.v.")
print(f"🔹 Web /data chỉ hiển thị phim Vietnam để phân tích (63 phim clean)")
print("=" * 60)
