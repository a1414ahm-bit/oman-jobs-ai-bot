import requests
import feedparser
from bs4 import BeautifulSoup

def fetch_rss_jobs(rss_url, source_name="RSS Source"):
    jobs = []
    try:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries:
            job = {
                "title": entry.get("title", "وظيفة جديدة"),
                "company": "شركة في عمان",
                "location": "سلطنة عمان",
                "description": entry.get("summary", ""),
                "link": entry.get("link", ""),
                "source": source_name
            }
            if job["link"]:
                jobs.append(job)
    except Exception as e:
        print(f"[-] خطأ أثناء جلب RSS من {source_name}: {e}")
    return jobs

def collect_all_jobs():
    all_jobs = []
    # مصدر افتراضي للبحث عن وظائف عمان عبر Indeed RSS
    rss_sources = [
        ("https://om.indeed.com/rss?q=Oman", "Indeed Oman")
    ]
    
    for url, name in rss_sources:
        all_jobs.extend(fetch_rss_jobs(url, name))
        
    return all_jobs
