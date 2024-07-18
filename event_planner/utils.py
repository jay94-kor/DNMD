import json
from datetime import date, datetime
from functools import lru_cache
import os
import re
import sqlite3
from contextlib import contextmanager
import logging

logging.basicConfig(filename='app.log', level=logging.ERROR)

@lru_cache(maxsize=None)
def load_json_file(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def format_currency(amount: float) -> str:
    return f"{amount:,.0f}"

def format_phone_number(number: str) -> str:
    pattern = r'(\d{3})(\d{3,4})(\d{4})'
    return re.sub(pattern, r'\1-\2-\3', number)

@contextmanager
def get_db_connection():
    conn = sqlite3.connect('event_planner.db', check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

def safe_operation(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"{func.__name__} 실행 중 오류 발생: {str(e)}"
            logging.error(error_msg, exc_info=True)
            return None
    return wrapper
