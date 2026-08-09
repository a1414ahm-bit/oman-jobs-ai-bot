import json
import os
import urllib.parse
import feedparser
import google.generativeai as genai
import requests

# ================= =================
# 1. إعدادات البيئة والمفاتيح
# ================= =================
FACEBOOK_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")  # مفتاح Gemini AI

CACHE_FILE = "published_jobs.json"

# تهيئة الذكاء الاصطناعي
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


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
# 3. إدارة قواعد البيانات وقمع التكرار
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
# 4. البحث المتقدم عن الوظائف الحقيقية
# ================= =================
def fetch_realtime_jobs():
    search_queries = [
        "مطلوب موظفين حديث",
        "وظائف خالية اليوم",
        "تعلن شركة عن حاجتها",
    ]
    countries = ["مصر", "السعودية", "الإمارات", "عمان"]

    found_jobs = []

    for country in countries:
        for q in search_queries:
            query = f'"{q}" {country}'
            encoded_query = urllib.parse.quote(query)
            # جلب النتائج اللحظية الحقيقية المرتبة حسب الأحدث
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ar&gl=EG&ceid=EG:ar"

            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:2]:
                found_jobs.append(
                    {
                        "id": entry.link,
                        "title": entry.title,
                        "link": entry.link,
                        "country": country,
                        "summary": getattr(entry, "summary", entry.title),
                    }
                )
    return found_jobs


# ================= =================
# 5. صياغة البوست بالذكاء الاصطناعي (Gemini)
# ================= =================
def generate_ai_post(job_data):
    if not GEMINI_API_KEY:
        # صياغة احتياطية في حال عدم توفر مفتاح AI
        short_link = shorten_url(job_data["link"])
        return (
            f"📢 فرصة عمل جديدة في {job_data['country']}\n\n"
            f"📌 {job_data['title']}\n\n"
            f"🔗 للتفاصيل والتقديم:\n{short_link}\n\n"
            f"#منصة_فرصة #وظائف_{job_data['country']}"
        )

    model = genai.GenerativeModel("gemini-pro")

    short_link = shorten_url(job_data["link"])

    prompt = f"""
    أنت مدير محتوى لمشروع "منصة فرصة" المتخصص في نشر الوظائف.
    قم بكتابة منشور فيسبوك احترافي وبشري للغاية (كأنك خبير توظيف تكتبه بنفسك) بناءً على بيانات الوظيفة التالية:
    - عنوان الوظيفة: {job_data['title']}
    - الدولة: {job_data['country']}
    - تفاصيل إضافية: {job_data['summary']}
    
    التعليمات:
    1. ابدأ بأسلوب مشجع وجذاب وبشري دون رسميات متخشبّة.
    2. استخدم إيموجيز مناسبة وأنيقة بدون مبالغة.
    3. قسم المنشور إلى نقاط واضحة (المسمى الوظيفي، الدولة، التفاصيل).
    4. أدرج هذا الرابط المختصر للتقديم بشكل واضح جداً: {short_link}
    5. أضف هاشتاجات نشطة ومناسبة مثل #منصة_فرصة وهاشتاج الدولة والتخصص.
    6. لا تذكر أي معلومات وهمية لم تذكر في البيانات.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"[!] خطأ في توليد الذكاء الاصطناعي: {e}")
        return f"📢 {job_data['title']}\n\n🔗 التقديم: {short_link}\n\n#منصة_فرصة"


# ================= =================
# 6. النشر المباشر على فيسبوك
# ================= =================
def post_to_facebook(post_text):
    if not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN:
        print("[!] خطأ: لم يتم ضبط بيانات فيسبوك (Secrets).")
        return False

    url = f"https://graph.facebook.com/v26.0/{FACEBOOK_PAGE_ID}/feed"
    payload = {"message": post_text, "access_token": FACEBOOK_ACCESS_TOKEN}

    res = requests.post(url, data=payload)
    if res.status_code == 200:
        print("[+] تم النشر بنجاح بواسطة الذكاء الاصطناعي على منصة فرصة!")
        return True
    else:
        print(f"[!] فشل النشر: {res.status_code} - {res.text}")
        return False


# ================= =================
# 7. التشغيل الرئيسي
# ================= =================
def main():
    print("=== تشغيل بوت منصة فرصة الذكي ===")
    published_jobs = load_published_jobs()

    # 1. البحث عن الوظائف
    raw_jobs = fetch_realtime_jobs()

    # 2. ترشيح الوظائف غير المكررة
    new_jobs = [j for j in raw_jobs if j["id"] not in published_jobs]
    print(f"[+] تم العثور على {len(new_jobs)} وظيفة جديدة.")

    if not new_jobs:
        print("=== لا توجد وظائف جديدة غير مكررة حالياً ===")
        return

    # 3. اختيار أول وظيفة جديدة
    selected_job = new_jobs[0]

    # 4. صياغة المنشور بالذكاء الاصطناعي
    print("[+] جاري صياغة المنشور عبر الذكاء الاصطناعي...")
    ai_post_content = generate_ai_post(selected_job)

    # 5. النشر وحفظ السجل
    if post_to_facebook(ai_post_content):
        save_published_job(selected_job["id"])
        print("=== تمت العملية بنجاح ===")


if __name__ == "__main__":
    main()
