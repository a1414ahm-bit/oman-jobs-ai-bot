import requests
from config import Config

def post_to_facebook(text_content):
    if not Config.FACEBOOK_ACCESS_TOKEN or not Config.FACEBOOK_PAGE_ID:
        print("[!] لم يتم ضبط مفاتيح Facebook Page API.")
        return False

    url = f"https://graph.facebook.com/v18.0/{Config.FACEBOOK_PAGE_ID}/feed"
    payload = {
        'message': text_content,
        'access_token': Config.FACEBOOK_ACCESS_TOKEN
    }
    
    try:
        res = requests.post(url, data=payload)
        if res.status_code == 200:
            print("[+] تم النشر بنجاح على Facebook!")
            return True
        else:
            print(f"[-] فشل النشر على Facebook: {res.text}")
    except Exception as e:
        print(f"[-] خطأ في الاتصال بـ Facebook API: {e}")
    return False
