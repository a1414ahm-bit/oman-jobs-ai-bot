import json
import os
import urllib.parse
import feedparser
from google import genai
import requests

# ================= =================
# 1. إعدادات البيئة والمفاتيح
# ================= =================
FACEBOOK_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

CACHE_FILE = "published_jobs.json"

# تهيئة عميل الذكاء الاصطناعي أحدث إصدار
ai_client = None
if GEMINI_API_KEY:
    ai_client = genai.Client(api_key=GEMINI_API_KEY)


# ================= =================
# 2. اختصار الروابط
# ================= =================
def shorten_url(long_url):
    try:
        api_url = f"http://tinyurl.com/api-create.php?url={urllib.parse.quote(long_url)}"
        res = requests.get(api_url, timeout=10)
        if res.status_code == 200:
            return res.text.strip()
    except Exception as e:
        print(f"[!] تعذر اختصار الرابط: {e}")
    return long_url


# ================= =================
# 3. إدارة السجل وقمع التكرار
# ================= =================
def load_published_jobs():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_published_job(job_id):
    jobs = load_published_jobs()
    jobs.add(job_id)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(jobs), f, ensure_ascii=False, indent=2)


# ================= =================
# 4. جلب الوظائف الحقيقية
# ================= =================
def fetch_realtime_jobs():
    sources = [
        {"country": "مصر", "q": "وظائف خالية اليوم مصر"},
        {"country": "السعودية", "q": "وظائف شاغرة السعودية"},
        {"country": "الإمارات", "q": "فرص عمل الإمارات"},
        {"country": "سلطنة عمان", "q": "وظائف عمان"},
    ]

    found_jobs = []
    for src in sources:
        query_str = urllib.parse.quote(src["q"])
        rss_url = f"https://news.google.com/rss/search?q={query_str}&hl=ar&gl=EG&ceid=EG:ar"

        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:3]:
            found_jobs.append(
                {
                    "id": entry.link,
                    "title": entry.title,
                    "link": entry.link,
                    "country": src["country"],
                    "summary": getattr(entry, "summary", entry.title),
                }
            )
    return found_jobs


# ================= =================
# 5. صياغة البوست بالذكاء الاصطناعي
# ================= =================
def generate_ai_post(job_data):
    short_link = shorten_url(job_data["link"])

    if not ai_client:
        return (
            f"📢 فرصة عمل جديدة في {job_data['country']}\n\n"
            f"📌 {job_data['title']}\n\n"
            f"🔗 للتفاصيل والتقديم:\n{short_link}\n\n"
            f"#منصة_فرصة #وظائف_{job_data['country'].replace(' ', '_')}"
        )

    prompt = f"""
    أنت صانع محتوى خبير ومسؤول توظيف لصفحة "منصة فرصة" على فيسبوك.
    مهمتك هي كتابة منشور فيسبوك جذاب وجديد تماماً يغري الباحثين عن عمل للتفاعل والتقديم.

    بيانات الفرصة:
    - العنوان الأساسي: {job_data['title']}
    - الدولة: {job_data['country']}
    - تفاصيل الخبر: {job_data['summary']}
    - رابط التقديم: {short_link}

    شروط الصياغة:
    1. اكتب المنشور بلغة عربية سليمة وبأسلوب تسويقي بشري مشجع (تجنب النسخ الحرفي من عناوين الأخبار).
    2. صغ عنواناً ملفتاً ومبتكراً للوظيفة في السطر الأول.
    3. استخدم التنسيق المنظم (نقاط إيموجي للنصائح، الشروط، أو طريقة التقديم).
    4. اجعل التقديم واضحاً جداً برابط: {short_link}
    5. أضف 4 إلى 5 هاشتاجات قوية ومناسبة مثل #منصة_فرصة وهاشتاجات التوظيف والدولة.
    6. لا تذكر أي معلومات غير موجودة بالبيانات أصلاً.
    """

    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"[!] خطأ أثناء استدعاء الذكاء الاصطناعي: {e}")
        return (
            f"🚨 فرصة عمل جديدة | {job_data['country']}\n\n"
            f"📌 {job_data['title']}\n\n"
            f"🔗 رابط التقديم المباشر:\n{short_link}\n\n"
            f"#منصة_فرصة #وظائف_{job_data['country'].replace(' ', '_')}"
        )


# ================= =================
# 6. النشر على فيسبوك
# ================= =================
def post_to_facebook(post_text):
    if not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN:
        print("[!] لم يتم ضبط مفاتيح الفيسبوك في Secrets.")
        return False

    url = f"https://graph.facebook.com/v26.0/{FACEBOOK_PAGE_ID}/feed"
    payload = {"message": post_text, "access_token": FACEBOOK_ACCESS_TOKEN}

    res = requests.post(url, data=payload)
    if res.status_code == 200:
        print("[+] تم نشر المنشور المصاغ بالذكاء الاصطناعي بنجاح!")
        return True
    else:
        print(f"[!] فشل النشر: {res.status_code} - {res.text}")
        return False


# ================= =================
# 7. التشغيل الرئيسي
# ================= =================
def main():
    print("=== بدء تشغيل بوت منصة فرصة (المطور) ===")
    published_jobs = load_published_jobs()

    all_jobs = fetch_realtime_jobs()
    new_jobs = [j for j in all_jobs if j["id"] not in published_jobs]

    print(f"[+] تم العثور على {len(new_jobs)} وظيفة جديدة.")

    if not new_jobs:
        print("=== لا توجد وظائف جديدة غير مكررة حالياً ===")
        return

    # اختيار وظيفة جديدة
    selected_job = new_jobs[0]

    print(f"[+] صياغة منشور مخصص لـ: {selected_job['title']}")
    post_content = generate_ai_post(selected_job)

    if post_to_facebook(post_content):
        save_published_job(selected_job["id"])
        print("=== تمت العملية بنجاح ===")


if __name__ == "__main__":
    main()
