# Kim Da-mi Universe — Website Flask

Website một trang dành cho fandom Kim Da-mi, được xây dựng bằng Flask với phong cách glassmorphism hiện đại, phù hợp làm landing page giới thiệu cộng đồng fan, tiểu sử và các hoạt động nổi bật.

## ✨ Điểm nhấn nội dung

- Hero giới thiệu fandom, CTA “Gia nhập” và “Khám phá vai diễn”
- Ba thẻ “Điểm nhấn” cập nhật nhịp cộng đồng, kho tư liệu và hoạt động lan tỏa yêu thương
- Mục “Vai diễn” liệt kê những tác phẩm biểu tượng của Kim Da-mi cùng mô tả ngắn gọn
- Testimonial từ fan, khu vực tin tức cập nhật lịch trình mới nhất
- Tiểu sử chi tiết, bảng thông tin nhanh và hành trình sự nghiệp nhiều giai đoạn
- Bộ sưu tập hình ảnh tuyển chọn hiển thị dạng lưới responsive
- Form đăng ký nhận bản tin/hoạt động với thông báo flash tiếng Việt
- Điều hướng responsive, menu di động và hiệu ứng mượt mà giữ nguyên từ thiết kế gốc

## 🗂️ Cấu trúc dự án

```
Website/
├── main.py
├── requirements.txt
├── README.md
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── templates/
    ├── base.html
    └── index.html
```

## 🚀 Bắt đầu nhanh

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Mở trình duyệt tại <http://127.0.0.1:5000> để trải nghiệm.

## 📸 Nguồn hình ảnh mẫu

- Hero: AsianWiki – <https://asianwiki.com/Kim_Da-Mi>
- Gallery #1: MyDramaList – <https://mydramalist.com/people/14221-kim-da-mi>
- Gallery #2: Soompi – bài phỏng vấn “Itaewon Class” (2021)
- Gallery #3: IMDb – <https://www.imdb.com/name/nm9015517/>

> Bạn có thể thay thế bằng ảnh riêng bằng cách tải về thư mục `static/images/` và cập nhật đường dẫn trong `GALLERY_IMAGES`/`HERO_CONTENT`.

## 🧪 Kiểm tra chất lượng

- `python -m compileall .` — đảm bảo các tệp Python biên dịch thành công

## 🔮 Hướng phát triển tiếp theo

- Đồng bộ dữ liệu với Google Sheets hoặc Airtable để đội ngũ fan dễ cập nhật
- Tích hợp gallery ảnh/clip, thêm trang lịch sự kiện và countdown thực tế
- Kết nối form đăng ký với nền tảng gửi mail (ví dụ: Mailchimp, Brevo)
- Viết test bằng `pytest` cho route và thêm trang đa ngôn ngữ (EN/KR)
