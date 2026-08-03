from openai import OpenAI
from config import Config

def generate_social_post(job_data):
    if not Config.OPENAI_API_KEY:
        return (
            f"🇴🇲 **وظيفة جديدة في سلطنة عمان**\n\n"
            f"📌 **المسمى الوظيفي:** {job_data['title']}\n"
            f"🏢 **الشركة:** {job_data['company']}\n"
            f"📍 **الموقع:** {job_data['location']}\n\n"
            f"🔗 **للتفاصيل والتقديم:** {job_data['link']}\n\n"
            f"#وظائف_عمان #وظائف_سلطنة_عمان #وظائف #عمان_اليوم #فرص_عمل"
        )

    try:
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        prompt = f"""
        أنت خبير تسويق محتوى وظائف في سلطنة عمان.
        قم بكتابة منشور جذاب ومرتب بناءً على التفاصيل التالية:
        عنوان الوظيفة: {job_data['title']}
        اسم الشركة: {job_data['company']}
        الموقع: {job_data['location']}
        الوصف: {job_data['description'][:300]}
        رابط التقديم: {job_data['link']}
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت مساعد ذكي متخصص في صياغة إعلانات الوظائف."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[-] خطأ في توليد المحتوى: {e}")
        return f"🇴🇲 **فرصة عمل:** {job_data['title']}\n📍 **الموقع:** {job_data['location']}\n🔗 **للتقديم:** {job_data['link']}\n\n#وظائف_عمان"
