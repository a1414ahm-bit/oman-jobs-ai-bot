import requests
from bs4 import BeautifulSoup

TARGET_COUNTRIES = [
    {"name": "سلطنة عمان", "query": "عمان"},
    {"name": "السعودية", "query": "السعودية"},
    {"name": "الإمارات", "query": "الإمارات"},
    {"name": "قطر", "query": "قطر"},
    {"name": "الكويت", "query": "الكويت"},
    {"name": "البحرين", "query": "البحرين"},
    {"name": "مصر", "query": "مصر"}
]

def fetch_real_jobs(country_info):
    country_name = country_info["name"]
    query = country_info["query"]
    
    # محرك بحث مباشر للفرص الوظيفية المنشورة حديثاً
    url = f"https://html.duckduckgo.com/html/?q=وظائف+شاغرة+{query}+تحديث+اليوم"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    jobs = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('a', class_='result__url', limit=3)
            titles = soup.find_all('a', class_='result__snippet', limit=3)
            
            for index, res in enumerate(results):
                link = res.get('href', '')
                title_text = titles[index].text if index < len(titles) else f"فرصة عمل جديدة في {country_name}"
                
                # تنظيف وتنسيق العنوان
                clean_title = title_text.replace("\n", "").strip()[:80]
                
                jobs.append({
                    "title": f"وظيفة شاغرة: {clean_title}",
                    "company": "إعلان توظيف حديث",
                    "country": country_name,
                    "location": country_name,
                    "description": f"تم رصد فرصة عمل جديدة في {country_name}. يمكنك التقديم والاطلاع على التفاصيل عبر الرابط المرفق.",
                    "link": link if link.startswith('http') else f"https://{link}"
                })
    except Exception as e:
        print(f"[-] خطأ أثناء البحث عن وظائف {country_name}: {e}")
        
    return jobs

def collect_all_jobs():
    all_jobs = []
    print("[+] بدء المسح الشامل للإنترنت لجلب أحدث إعلانات الوظائف للخليج ومصر...")
    
    for country in TARGET_COUNTRIES:
        country_jobs = fetch_real_jobs(country)
        all_jobs.extend(country_jobs)
        
    print(f"[+] إجمالي الوظائف المجمعة من الشبكة: {len(all_jobs)}")
    return all_jobs
