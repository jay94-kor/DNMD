import json
import os

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'categories.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"경고: {config_path} 파일을 찾을 수 없습니다.")
        return {}
    except json.JSONDecodeError:
        print(f"경고: {config_path} 파일의 JSON 형식이 올바르지 않습니다.")
        return {}

def format_currency(amount):
    return f"{amount:,}원"

def calculate_percentage(part, whole):
    return (part / whole) * 100 if whole != 0 else 0

def get_project_root():
    return os.path.dirname(os.path.abspath(__file__))

def get_db_path():
    return os.path.join(get_project_root(), 'data', 'event_planner.db')