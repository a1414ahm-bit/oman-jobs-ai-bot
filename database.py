import sqlite3
import os
from config import Config

def get_db_connection():
    os.makedirs(os.path.dirname(Config.DB_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            description TEXT,
            link TEXT UNIQUE NOT NULL,
            source TEXT,
            date_found TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            published_status INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def is_job_exists(link):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM jobs WHERE link = ?', (link,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def save_job(job_data):
    if is_job_exists(job_data['link']):
        return False
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO jobs (title, company, location, description, link, source, published_status)
        VALUES (?, ?, ?, ?, ?, ?, 0)
    ''', (
        job_data.get('title'),
        job_data.get('company', 'غير محدد'),
        job_data.get('location', 'سلطنة عمان'),
        job_data.get('description', ''),
        job_data['link'],
        job_data.get('source', 'General')
    ))
    conn.commit()
    conn.close()
    return True

def mark_as_published(job_link):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE jobs SET published_status = 1 WHERE link = ?', (job_link,))
    conn.commit()
    conn.close()
