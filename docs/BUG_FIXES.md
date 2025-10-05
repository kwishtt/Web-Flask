# 🐛 Bug Fixes - October 6, 2025

## Bug #1: URL endpoint error trong data.html ✅

### ❌ Error:
```
ERROR:__main__:Lỗi khi tạo biểu đồ: Could not build url for endpoint '#predict'. 
Did you mean 'predict' instead?
```

### ✅ Fix:
```html
<!-- ❌ SAI -->
<a href="{{ url_for('#predict') }}" class="btn">Dự đoán phim mới</a>

<!-- ✅ ĐÚNG -->
<a href="{{ url_for('home') }}#predict" class="btn">Dự đoán phim mới</a>
```

---

## Bug #2: Missing columns khi predict ✅

### ❌ Error:
```
ValueError: columns are missing: {'Production Countries', 'Spoken Languages', 'ROI', 'Revenue'}
```

### ✅ Fix app.py:

**Added 11 missing columns:**
```python
data = {
    'Id': 0,
    'Original Title': form_data.get('title'),
    'Original Language': 'en',
    'Revenue': 0,
    'Genres': f"['{form_data.get('genre')}']",
    'Production Countries': f"['{form_data.get('country')}']",
    'Spoken Languages': "['English']",
    'Production Companies': '[]',
    'Director': 'Unknown',
    'Stars': 'Unknown',
    'ROI': 1.0
}
```

**Status:** ✅ All 27 features now present, prediction works!
