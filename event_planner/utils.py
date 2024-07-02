import json
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'categories.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Warning: {config_path} file not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Warning: {config_path} is not a valid JSON file.")
        return {}

def format_currency(amount):
    return f"{amount:,}원"

def calculate_percentage(part, whole):
    return (part / whole) * 100 if whole != 0 else 0

def get_project_root():
    return os.path.dirname(os.path.abspath(__file__))

def get_db_path():
    return os.path.join(get_project_root(), 'data', 'event_planner.db')