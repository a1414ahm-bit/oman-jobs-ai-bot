import requests
from bs4 import BeautifulSoup

def collect_all_jobs():
    jobs = []
    
    # نموذج وظائف افتراضية لضمان عمل البوت والنشر
    mock_jobs = [
        {
            "title": "مهندس برمجة وتطوير موقع",
            "company": "شركة الحلول الرقمية",
            "location": "مسقط، سلطنة عمان",
            "description": "مطلوب مهندس برمجة يتقن Python وReact للعمل لدى شركة رائدة.",
            "link": "https://example.com/job/101"
        },
        {
            "title": "محاسب مالية أول",
            "company": "مجموعة عمان للاستثمار",
            "location": "صحار، سلطنة عمان",
            "description": "مطلوب محاسب خبرة لا تقل عن 3 سنوات في إعداد التقارير المالية.",
            "link": "https://example.com/job/102"
        }
    ]
    
    jobs.extend(mock_jobs)
    return jobs
