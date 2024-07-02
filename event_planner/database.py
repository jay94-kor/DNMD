import sqlite3
import json
import os
from utils import get_db_path

def init_db():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS event_data
                 (key TEXT PRIMARY KEY, value TEXT)''')
    
    conn.commit()
    conn.close()

def save_data(data):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    for key, value in data.items():
        if isinstance(value, (list, dict)):
            value = json.dumps(value)
        c.execute("INSERT OR REPLACE INTO event_data (key, value) VALUES (?, ?)",
                  (key, value))
    
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    c.execute("SELECT key, value FROM event_data")
    result = {}
    for key, value in c.fetchall():
        try:
            result[key] = json.loads(value)
        except json.JSONDecodeError:
            result[key] = value
    
    conn.close()
    return result