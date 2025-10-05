"""
Test prediction endpoint
"""
import requests

url = "http://localhost:5000/predict"

data = {
    "title": "Inception",
    "budget": "160000000",
    "runtime": "148",
    "director_rating": "8.8",
    "actor_rating": "10000",
    "genre": "Science Fiction",
    "release_year": "2010",
    "release_month": "7",
    "country": "United States of America"
}

print("🧪 Testing prediction...")
print(f"Data: {data}")

try:
    response = requests.post(url, data=data)
    print(f"\n✅ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Prediction successful!")
        # Check if there's an error message in the response
        if "Lỗi" in response.text or "Error" in response.text:
            print("⚠️ Warning: Response contains error text")
            # Extract error message
            import re
            errors = re.findall(r'Lỗi:.*?</.*?>', response.text)
            for err in errors:
                print(f"  {err}")
        else:
            print("✅ No errors in response")
    else:
        print(f"❌ Request failed with status {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Exception: {e}")
