import json

def load_config():
    with open('config/categories.json', 'r', encoding='utf-8') as f:
        categories = json.load(f)
    return categories

def format_currency(amount):
    return f"{amount:,}원"

def calculate_percentage(part, whole):
    return (part / whole) * 100 if whole != 0 else 0