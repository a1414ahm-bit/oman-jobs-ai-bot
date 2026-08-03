import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
    FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")
    INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
    LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    LINKEDIN_AUTHOR_URN = os.getenv("LINKEDIN_AUTHOR_URN", "")
    DB_PATH = os.path.join("database", "jobs.db")
