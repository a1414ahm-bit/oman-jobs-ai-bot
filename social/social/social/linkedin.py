import requests
from config import Config

def post_to_linkedin(text_content):
    if not Config.LINKEDIN_ACCESS_TOKEN or not Config.LINKEDIN_AUTHOR_URN:
        print("[!] لم يتم ضبط مفاتيح LinkedIn API.")
        return False

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        'Authorization': f'Bearer {Config.LINKEDIN_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    payload = {
        "author": Config.LINKEDIN_AUTHOR_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text_content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    try:
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code in [200, 201]:
            print("[+] تم النشر بنجاح على LinkedIn!")
            return True
        else:
            print(f"[-] فشل النشر على LinkedIn: {res.text}")
    except Exception as e:
        print(f"[-] خطأ في الاتصال بـ LinkedIn API: {e}")
    return False
