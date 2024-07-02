import json
import os
from datetime import datetime

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'categories.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Warning: {config_path} file not found or invalid. Using default values.")
        return {
            'event_types': ['컨퍼런스', '세미나', '워크샵', '기타'],
            'facilities': ['프로젝터', '마이크', '스피커', '테이블', '의자'],
            'budget_categories': ['장소 대여', '케이터링', '장비 대여', '인건비', '기타']
        }

def get_db_path():
    return os.path.join(os.path.dirname(__file__), 'data', 'event_planner.db')

def format_currency(amount):
    return f"₩{amount:,}"

def calculate_percentage(part, whole):
    return (part / whole) * 100 if whole != 0 else 0

def format_date(date_string):
    date_obj = datetime.strptime(date_string, "%Y-%m-%d")
    return date_obj.strftime("%Y년 %m월 %d일")

def validate_date_range(start_date, end_date):
    return start_date <= end_date