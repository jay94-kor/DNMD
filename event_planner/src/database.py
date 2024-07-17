import sqlite3
import json
from datetime import date, datetime
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = sqlite3.connect('event_planner.db')
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

def save_event_data(event_data):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            event_id = event_data.get('id')
            event_data_json = json.dumps(event_data, ensure_ascii=False, cls=CustomJSONEncoder)
            if event_id:
                cursor.execute('''
                UPDATE events SET event_data = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                ''', (event_data_json, event_id))
            else:
                cursor.execute('''
                INSERT INTO events (event_data) VALUES (?)
                ''', (event_data_json,))
                event_data['id'] = cursor.lastrowid
            conn.commit()
    except Exception as e:
        print(f"Error saving event data: {str(e)}")
        print(f"Event data: {event_data}")
        raise

def load_event_data(event_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT event_data FROM events WHERE id = ?', (event_id,))
        result = cursor.fetchone()
        if result:
            return json.loads(result[0])
    return None