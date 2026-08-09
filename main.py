import io
import json
import os
import urllib.parse
import feedparser
from PIL import Image, ImageDraw, ImageFont
import requests

# --- 1. الإعدادات والمفاتيح ---
FACEBOOK_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")
CACHE_FILE = "published_jobs.json"


# --- 2. إدارة قاعدة البيانات المؤقتة ---
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


# --- 3. التصنيف الذكي للتخصصات ---
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


# --- 4. توليد تصميم صورة إعلانية مع خط آمن ---
def generate_job_image(title, category, country):
    img = Image.new("RGB", (1080, 1080), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    draw.rectangle([40, 40, 1040, 1040], outline=(56, 189, 248), width=8)

    draw.text(
        (80, 100), "FORSA | منصة فرصة", fill=(255, 255, 255), font=font
    )
    draw.text(
        (80, 180), f"Country: {country}", fill=(56, 189, 248), font=font
    )
    draw.text(
        (80, 250), f"Category: {category}", fill=(226, 232, 240), font=font
    )

    words = title.split()
    line1 = " ".join(words[:6])
    line2 = " ".join(words[6:12])

    draw.text((80, 420), line1, fill=(255, 255, 255), font=font)
    if line2:
        draw.text((80, 500), line2, fill=(255, 255, 255), font=font)

    draw.text(
        (80, 880),
        "Details inside the post",
        fill=(148, 163, 184),
        font=font,
    )

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes


# --- 5. جلب الوظائف مع ترميز الروابط لتفادي خطأ المسافات ---
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


# --- 6. النشر المباشر على فيسبوك ---
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


# --- 7. التشغيل الرئيسي ---
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

    post_text = (
        f"{job['flag']} {job['country']} | {job['cat_icon']} {job['category']}\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"📌 **الوظيفة:** {job['title']}\n\n"
        f"🔗 **رابط التقديم والتفاصيل:**\n{job['link']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"#منصة_فرصة #وظائف_{job['country'].replace(' ', '_')} #{job['category'].replace(' ', '_')} #توظيف"
    )

    img_bytes = generate_job_image(
        job["title"], job["category"], job["country"]
    )

    if post_photo_to_facebook(post_text, img_bytes):
        published_jobs.add(job["id"])
        save_published_jobs(published_jobs)
        print("=== تم النشر وحفظ البيانات بنجاح ===")


if __name__ == "__main__":
    main()
