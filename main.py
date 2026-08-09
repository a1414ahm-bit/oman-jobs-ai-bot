import io
import json
import os
import urllib.parse
import feedparser
from PIL import Image, ImageDraw, ImageFont
import requests
import arabic_reshaper
from bidi.algorithm import get_display

# --- 1. الإعدادات والمفاتيح ---
FACEBOOK_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")
CACHE_FILE = "published_jobs.json"
FONT_PATH = "Amiri-Bold.ttf"


# --- 2. اختصار الروابط الطويلة ---
def shorten_url(long_url):
    try:
        api_url = f"http://tinyurl.com/api-create.php?url={urllib.parse.quote(long_url)}"
        res = requests.get(api_url, timeout=10)
        if res.status_code == 200:
            return res.text.strip()
    except Exception as e:
        print(f"[!] فشل اختصار الرابط: {e}")
    return long_url


# --- 3. تحميل خط عربي تلقائياً ---
def download_arabic_font():
    if not os.path.exists(FONT_PATH):
        print("[+] جاري تحميل الخط العربي...")
        font_url = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Bold.ttf"
        res = requests.get(font_url)
        with open(FONT_PATH, "wb") as f:
            f.write(res.content)


def reshape_text(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


# --- 4. إدارة قاعدة البيانات المؤقتة ---
def load_published_jobs():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_published_jobs(published_set):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(published_set), f, ensure_ascii=False, indent=2)


# --- 5. التصنيف الذكي للتخصصات ---
def categorize_job(title):
    title_lower = title.lower()
    if any(
        w in title_lower
        for w in [
            "برمجة",
            "تطوير",
            "python",
            "developer",
            "مهندس",
            "it",
            "تقنية",
        ]
    ):
        return "تكنولوجيا وهندسة", "💻"
    elif any(
        w in title_lower
        for w in ["تسويق", "مبيعات", "ارباح", "ماركتنج", "sales", "علاقات"]
    ):
        return "تسويق ومبيعات", "📈"
    elif any(
        w in title_lower
        for w in ["محاسب", "مالية", "بنك", "finance", "accounting", "تدقيق"]
    ):
        return "مالية ومحاسبة", "💰"
    elif any(
        w in title_lower
        for w in ["طبيب", "تمريض", "صيدلي", "مستشفى", "medical", "صحة"]
    ):
        return "طب ورعاية صحية", "🏥"
    elif any(
        w in title_lower
        for w in ["معلم", "تدريس", "مدرس", "جامعة", "أستاذ", "تعليم"]
    ):
        return "تعليم وتدريب", "🎓"
    else:
        return "وظائف عامة", "💼"


# --- 6. توليد صورة احترافية باللغة العربية ---
def generate_job_image(title, category, country):
    download_arabic_font()

    img = Image.new("RGB", (1080, 1080), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    title_font = ImageFont.truetype(FONT_PATH, 50)
    header_font = ImageFont.truetype(FONT_PATH, 60)
    sub_font = ImageFont.truetype(FONT_PATH, 40)

    draw.rectangle([40, 40, 1040, 1040], outline=(56, 189, 248), width=8)

    # كتابة النصوص العربية المنسقة
    draw.text(
        (540, 120),
        reshape_text("منصة فرصة | FORSA"),
        fill=(255, 255, 255),
        font=header_font,
        anchor="mm",
    )
    draw.text(
        (540, 220),
        reshape_text(f"الدولة: {country}"),
        fill=(56, 189, 248),
        font=sub_font,
        anchor="mm",
    )
    draw.text(
        (540, 300),
        reshape_text(f"التصنيف: {category}"),
        fill=(226, 232, 240),
        font=sub_font,
        anchor="mm",
    )

    # تقسيم عنوان الوظيفة لسلسلة أسطر
    words = title.split()
    line1 = " ".join(words[:6])
    line2 = " ".join(words[6:12])
    line3 = " ".join(words[12:])

    draw.text(
        (540, 480),
        reshape_text(line1),
        fill=(255, 255, 255),
        font=title_font,
        anchor="mm",
    )
    if line2:
        draw.text(
            (540, 560),
            reshape_text(line2),
            fill=(255, 255, 255),
            font=title_font,
            anchor="mm",
        )
    if line3:
        draw.text(
            (540, 640),
            reshape_text(line3),
            fill=(255, 255, 255),
            font=title_font,
            anchor="mm",
        )

    draw.text(
        (540, 920),
        reshape_text("التفاصيل ورابط التقديم داخل المنشور"),
        fill=(148, 163, 184),
        font=sub_font,
        anchor="mm",
    )

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes


# --- 7. جلب الوظائف ---
def fetch_jobs():
    sources = [
        {"q": "وظائف", "country": "مصر", "flag": "🇪🇬"},
        {"q": "وظائف", "country": "سلطنة عمان", "flag": "🇴🇲"},
        {"q": "وظائف", "country": "السعودية", "flag": "🇸🇦"},
        {"q": "وظائف", "country": "الإمارات", "flag": "🇦🇪"},
    ]
    all_jobs = []
    for src in sources:
        query_str = urllib.parse.quote(f"{src['q']} {src['country']}")
        url = f"https://news.google.com/rss/search?q={query_str}&hl=ar&gl=EG&ceid=EG:ar"

        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            category, cat_icon = categorize_job(entry.title)
            all_jobs.append(
                {
                    "id": entry.link,
                    "title": entry.title,
                    "link": entry.link,
                    "country": src["country"],
                    "flag": src["flag"],
                    "category": category,
                    "cat_icon": cat_icon,
                }
            )
    return all_jobs


# --- 8. النشر المباشر ---
def post_photo_to_facebook(message, image_bytes):
    if not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN:
        print("[!] لم يتم ضبط المفاتيح في Secrets.")
        return False

    url = f"https://graph.facebook.com/v26.0/{FACEBOOK_PAGE_ID}/photos"
    payload = {"message": message, "access_token": FACEBOOK_ACCESS_TOKEN}
    files = {"source": ("job_image.png", image_bytes, "image/png")}

    response = requests.post(url, data=payload, files=files)
    if response.status_code == 200:
        print("[+] تم النشر بنجاح على منصة فرصة!")
        return True
    else:
        print(f"[!] فشل النشر: {response.status_code} - {response.text}")
        return False


# --- 9. التشغيل الرئيسي ---
def main():
    print("=== بدء تشغيل بوت منصة فرصة ===")
    published_jobs = load_published_jobs()
    collected_jobs = fetch_jobs()

    new_jobs = [j for j in collected_jobs if j["id"] not in published_jobs]
    print(f"[+] عدد الوظائف الجديدة: {len(new_jobs)}")

    if not new_jobs:
        print("=== لا توجد وظائف جديدة للنشر حالياً ===")
        return

    job = new_jobs[0]
    short_link = shorten_url(job["link"])

    # تنظيف العنوان من علامات النجمتين لتنسيق أنظف
    clean_title = job["title"].replace("**", "")

    post_text = (
        f"{job['flag']} {job['country']} | {job['cat_icon']} {job['category']}\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"📌 الوظيفة: {clean_title}\n\n"
        f"🔗 رابط التقديم والتفاصيل:\n{short_link}\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"#منصة_فرصة #وظائف_{job['country'].replace(' ', '_')} #{job['category'].replace(' ', '_')} #توظيف"
    )

    img_bytes = generate_job_image(clean_title, job["category"], job["country"])

    if post_photo_to_facebook(post_text, img_bytes):
        published_jobs.add(job["id"])
        save_published_jobs(published_jobs)
        print("=== تم النشر وحفظ البيانات بنجاح ===")


if __name__ == "__main__":
    main()
