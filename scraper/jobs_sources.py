import requests
import xml.etree.ElementTree as ET
import urllib.parse

TARGET_COUNTRIES = [
    {"name": "سلطنة عمان", "query": "وظائف شاغرة سلطنة عمان"},
    {"name": "السعودية", "query": "وظائف شاغرة السعودية"},
    {"name": "الإمارات", "query": "وظائف شاغرة الإمارات"},
    {"name": "قطر", "query": "وظائف شاغرة قطر"},
    {"name": "الكويت", "query": "وظائف شاغرة الكويت"},
    {"name": "البحرين", "query": "وظائف شاغرة البحرين"},
    {"name": "مصر", "query": "وظائف شاغرة مصر"}
]

def fetch_rss_jobs(country_info):
    country_name = country_info["name"]
    query = country_info["query"]
    
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ar&gl=EG&ceid=EG:ar"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    jobs = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall('.//item')[:2]  # جلب أحدث وظيفتين من كل دولة
            
            for item in items:
                title_elem = item.find('title')
                link_elem = item.find('link')
                
                title = title_elem.text if title_elem is not None else "وظيفة شاغرة جديدة"
                link = link_elem.text if link_elem is not None else "https://google.com"
                
                clean_title = title.split(" - ")[0]
                
                jobs.append({
                    "title": clean_title,
                    "company": "جهة غير محددة",
                    "country": country_name,
                    "location": country_name,
                    "description": f"فرصة عمل جديدة تم رصدها حديثاً في {country_name}. اضغط على الرابط للتفاصيل والتقديم.",
                    "link": link
                })
    except Exception as e:
        print(f"[-] خطأ في جلب وظائف {country_name}: {e}")
        
    return jobs

def collect_all_jobs():
    all_jobs = []
    print("[+] بدء المسح الشامل لجلب أحدث إعلانات الوظائف للخليج ومصر...")
    
    for country in TARGET_COUNTRIES:
        country_jobs = fetch_rss_jobs(country)
        all_jobs.extend(country_jobs)
        
    print(f"[+] إجمالي الوظائف المجمعة من الشبكة: {len(all_jobs)}")
    return all_jobs
