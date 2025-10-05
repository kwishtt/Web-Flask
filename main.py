from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.config["SECRET_KEY"] = "super-secret-key-change-me"


@app.context_processor
def inject_now():
    return {"now": datetime.utcnow()}

HERO_CONTENT = {
    "title": "Kim Da-mi, nàng thơ của chúng ta",
    "subtitle": "Đây là website do Khuê Đinh tạo ra để ngắm tình đầu mỗi ngày, chúng bạn xem và khen nó",
    "cta_primary": {"label": "Gia nhập fandom", "href": "#contact"},
    "cta_secondary": {"label": "Khám phá vai diễn", "href": "#projects"},
    "portrait": {
        "src": "https://cdn2.tuoitre.vn/471584752817336320/2025/5/23/kim-da-mi-1747991546000221964827.jpg",
        "alt": "Kim Da-mi trong bộ ảnh chân dung",
        "credit": "Ktmjn",
        "credit_url": "https://asianwiki.com/Kim_Da-Mi",
    },
}

FEATURES = [
    {
        "icon": "fluent:heart-20-regular",
        "title": "Nhịp đập cộng đồng",
        "description": "Cập nhật sự kiện, livestream, hoạt động ủng hộ từ các nhóm fan Việt Nam và quốc tế.",
    },
    {
        "icon": "fluent:movie-20-filled",
        "title": "Kho tư liệu phong phú",
        "description": "Thư viện ảnh, hậu trường và bài phỏng vấn được biên tập lại với ghi chú tiếng Việt dễ hiểu.",
    },
    {
        "icon": "fluent:sparkle-20-regular",
        "title": "Lan tỏa yêu thương",
        "description": "Chiến dịch thiện nguyện và dự án fan-art giúp truyền tải nguồn năng lượng tích cực của Da-mi.",
    },
]

PROJECTS = [
    {
        "name": "Itaewon Class (2020)",
        "description": "Vai Jo Yi-seo cá tính, thông minh giúp Kim Da-mi bứt phá trên màn ảnh nhỏ và giành Baeksang danh giá.",
        "tags": ["Phim truyền hình", "JTBC", "Jo Yi-seo"],
        "link": "#",
    },
    {
        "name": "The Witch: Part 1. The Subversion (2018)",
        "description": "Màn debut chấn động với nhân vật Ja-yoon mang đến giải Tân binh xuất sắc tại Rồng Xanh.",
        "tags": ["Điện ảnh", "Hành động", "Ja-yoon"],
        "link": "#",
    },
    {
        "name": "Soulmate (2023)",
        "description": "Tác phẩm cảm động về tình bạn nữ, giúp Da-mi khoe nét diễn tinh tế và nhận cơn mưa lời khen.",
        "tags": ["Điện ảnh", "Melodrama", "Mi-so"],
        "link": "#",
    },
]

TESTIMONIALS = [
    {
        "quote": "Mỗi lần xem Da-mi diễn, mình như bước vào thế giới cảm xúc mới và học cách sống chân thành hơn.",
        "name": "Lan Phương",
        "role": "Dami-er từ 2020",
    },
    {
        "quote": "Cộng đồng ở đây luôn ấm áp. Chúng mình cùng nhau đếm ngược từng dự án mới của Da-mi.",
        "name": "Minh Châu",
        "role": "Admin fanpage Kim Da-mi Việt",
    },
]

PROCESS_STEPS = [
    {
        "title": "Theo dõi",
        "description": "Cập nhật lịch trình, tác phẩm và sự kiện fan meeting thông qua bản tin hằng tuần.",
    },
    {
        "title": "Chia sẻ",
        "description": "Lan tỏa fan art, review phim và những câu chuyện truyền cảm hứng từ Da-mi.",
    },
    {
        "title": "Ủng hộ",
        "description": "Tham gia các dự án thiện nguyện, gửi coffee truck và nhắn nhủ yêu thương tới đoàn phim.",
    },
    {
        "title": "Gắn kết",
        "description": "Gặp gỡ, trò chuyện cùng fandom qua offline meetup và hoạt động gây quỹ chung.",
    },
]

STATS = [
    {"label": "Năm debut", "value": "2017"},
    {"label": "Giải thưởng lớn", "value": "7+"},
    {"label": "Thành viên cộng đồng", "value": "25K"},
]

JOURNAL_POSTS = [
    {
        "title": "Kim Da-mi xác nhận dự án phim mới cùng Park Seo-joon",
        "date": "15 tháng 9, 2025",
        "excerpt": "Hai ngôi sao tái hợp trong tác phẩm điện ảnh đề tài kỳ ảo, dự kiến khởi quay cuối năm nay.",
        "link": "#",
    },
    {
        "title": "Hậu trường tạp chí Elle số tháng 10",
        "date": "01 tháng 9, 2025",
        "excerpt": "Da-mi khoe khí chất đa dạng với concept mùa thu, chia sẻ bí quyết giữ năng lượng tích cực.",
        "link": "#",
    },
]

BIOGRAPHY = {
    "intro": "Kim Da-mi sinh ngày 9 tháng 4 năm 1995 tại Seoul, lớn lên ở Busan và tốt nghiệp Đại học Nghệ thuật Quốc gia Hàn Quốc. Cô được yêu mến nhờ diễn xuất biến hóa, ánh mắt giàu cảm xúc và tinh thần luôn thử thách bản thân ở những vai diễn táo bạo.",
    "sections": [
        {
            "title": "Bước chân vào diễn xuất",
            "content": "Ngay từ những vai diễn đầu tay trong các phim ngắn, Da-mi đã gây chú ý bởi cách thể hiện tự nhiên. Bộ phim đầu tiên trên màn ảnh rộng của cô là “The Witch: Part 1. The Subversion” (2018), giúp cô giành cú đúp giải Tân binh ở hầu hết lễ trao giải lớn.",
        },
        {
            "title": "Tỏa sáng trên màn ảnh nhỏ",
            "content": "Năm 2020, cô hóa thân thành Jo Yi-seo trong “Itaewon Class”, mang đến màu sắc nổi loạn nhưng chân thành. Vai diễn này giúp Da-mi trở thành biểu tượng của thế hệ mới, đồng thời nhận giải Nữ diễn viên mới xuất sắc tại Baeksang Arts Awards.",
        },
        {
            "title": "Không ngừng thử thách",
            "content": "Từ dự án điện ảnh tâm lý “Soulmate” đến phim hành động “The Witch 2”, Da-mi luôn tìm cách khai phá bản thân, biến hóa đa dạng giữa nhiều thể loại và hợp tác cùng những đạo diễn tên tuổi.",
        },
    ],
}

QUICK_FACTS = [
    {"label": "Tên tiếng Hàn", "value": "김다미"},
    {"label": "Ngày sinh", "value": "9 tháng 4, 1995"},
    {"label": "Chiều cao", "value": "170 cm"},
    {"label": "Học vấn", "value": "Đại học Nghệ thuật Quốc gia Hàn Quốc"},
    {"label": "Công ty quản lý", "value": "United Artists Agency"},
]

ACHIEVEMENTS = [
    {
        "year": "2018",
        "title": "Giải Tân binh xuất sắc (Blue Dragon Film Awards)",
        "description": "Vinh danh cho vai Ja-yoon trong “The Witch: Part 1. The Subversion”.",
    },
    {
        "year": "2020",
        "title": "Giải Nữ diễn viên mới xuất sắc (Baeksang Arts Awards)",
        "description": "Thể hiện bùng nổ với nhân vật Jo Yi-seo trong “Itaewon Class”.",
    },
    {
        "year": "2023",
        "title": "Nữ diễn viên được yêu thích nhất (Buil Film Awards)",
        "description": "Vai Mi-so trong “Soulmate” chiếm trọn trái tim khán giả và giới phê bình.",
    },
]

GALLERY_IMAGES = [
    {
        "src": "https://cdn2.tuoitre.vn/471584752817336320/2025/5/23/kim-da-mi-1-17479915456091257807307.jpg",
        "alt": "Kim Da-mi tạo dáng trong bộ ảnh quảng bá",
        "caption": "Phong thái tự tin trong bộ ảnh quảng bá cho “Itaewon Class”.",
        "credit": "Tao",
        "credit_url": "https://mydramalist.com/people/14221-kim-da-mi",
    },
    {
        "src": "https://cdn2.tuoitre.vn/471584752817336320/2025/5/23/kim-da-mi-4-17479915458481355850302.jpg",
        "alt": "Kim Da-mi phỏng vấn cùng tạp chí",
        "caption": "Nụ cười rạng rỡ của Da-mi trong bài phỏng vấn đầu năm 2021.",
        "credit": "Soompi",
        "credit_url": "https://www.soompi.com/article/1453153wpp/kim-da-mi-talks-about-how-she-feels-after-the-success-of-itaewon-class",
    },
    {
        "src": "https://cdn2.tuoitre.vn/471584752817336320/2025/5/23/kim-da-mi-3-17479915457641680383152.jpg",
        "alt": "Kim Da-mi trên thảm đỏ",
        "caption": "Khoảnh khắc trên thảm đỏ lễ trao giải, toát lên thần thái cuốn hút.",
        "credit": "IMDb",
        "credit_url": "https://www.imdb.com/name/nm9015517/",
    },
]


@app.route("/")
def home():
    return render_template(
        "index.html",
        hero=HERO_CONTENT,
        features=FEATURES,
        projects=PROJECTS,
        testimonials=TESTIMONIALS,
        process_steps=PROCESS_STEPS,
        stats=STATS,
        journal_posts=JOURNAL_POSTS,
        bio=BIOGRAPHY,
        quick_facts=QUICK_FACTS,
        achievements=ACHIEVEMENTS,
        gallery=GALLERY_IMAGES,
    )


@app.post("/contact")
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not email or not message:
        flash("Vui lòng điền đầy đủ thông tin trước khi gửi.", "error")
        return redirect(url_for("home") + "#contact")

    flash("Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi trong vòng 24 giờ.", "success")
    return redirect(url_for("home") + "#contact")


if __name__ == "__main__":
    app.run(debug=True)
