from utils import get_db_connection, lru_cache
import json
from datetime import datetime, date
import logging

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

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

def save_event_data(event_data: dict) -> None:
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
        logging.error(f"Error saving event data: {str(e)}")
        logging.error(f"Event data: {event_data}")
        raise

@lru_cache(maxsize=32)
def load_event_data(event_id: int) -> dict:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT event_data FROM events WHERE id = ?', (event_id,))
        result = cursor.fetchone()
        if result:
            event_data = json.loads(result[0])
            for key, value in event_data.items():
                if isinstance(value, str):
                    try:
                        event_data[key] = datetime.fromisoformat(value).date()
                    except ValueError:
                        pass
            return event_data
        return {}

def get_all_events() -> list:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, event_data, created_at FROM events ORDER BY created_at DESC')
        return [(row[0], json.loads(row[1]).get('event_name', 'Unnamed Event'), row[2]) for row in cursor.fetchall()]