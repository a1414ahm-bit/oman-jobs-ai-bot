from database import init_db, save_job, mark_as_published
from scraper.jobs_sources import collect_all_jobs
from ai.content_generator import generate_social_post
from social.facebook import post_to_facebook
from social.linkedin import post_to_linkedin

def run_bot():
    print("=== بدء تشغيل Oman Jobs AI Bot ===")
    
    init_db()
    
    print("[1/4] جاري البحث عن وظائف جديدة...")
    raw_jobs = collect_all_jobs()
    print(f"--> تم العثور على {len(raw_jobs)} وظيفة محتملة.")

    new_jobs = []
    for job in raw_jobs:
        if save_job(job):
            new_jobs.append(job)

    print(f"--> عدد الوظائف الجديدة غير المكررة: {len(new_jobs)}")

    for index, job in enumerate(new_jobs[:5], 1):
        print(f"\n[2/4] معالجة الوظيفة ({index}/{min(5, len(new_jobs))}): {job['title']}")
        
        post_content = generate_social_post(job)
        print("[3/4] تم إنشاء المحتوى التسويقي.")

        print("[4/4] جاري النشر على منصات التواصل الاجتماعي...")
        
        fb_success = post_to_facebook(post_content)
        li_success = post_to_linkedin(post_content)

        if fb_success or li_success:
            mark_as_published(job['link'])
            print(f"[+] تم النشر والتحديث بنجاح للوظيفة: {job['title']}")
        else:
            print(f"[!] تم حفظ الوظيفة في قاعدة البيانات (لم يتم النشر لعدم وجود مفاتيح API).")

    print("\n=== اكتمال المهمة بنجاح ===")

if __name__ == "__main__":
    run_bot()
