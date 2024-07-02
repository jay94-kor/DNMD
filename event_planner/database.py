import sqlite3
import json
import os
from utils import get_db_path

def init_db():
    # 데이터 디렉토리 생성
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    # 기본 정보 테이블 생성
    c.execute('''CREATE TABLE IF NOT EXISTS basic_info
                 (id INTEGER PRIMARY KEY, event_name TEXT, client_name TEXT, event_type TEXT, scale INTEGER, start_date TEXT, end_date TEXT, setup TEXT, teardown TEXT)''')
    
    # 장소 정보 테이블 생성
    c.execute('''CREATE TABLE IF NOT EXISTS venue_info
                 (id INTEGER PRIMARY KEY, venue_name TEXT, venue_type TEXT, address TEXT, capacity INTEGER, facilities TEXT)''')
    
    # 예산 정보 테이블 생성
    c.execute('''CREATE TABLE IF NOT EXISTS budget_info
                 (id INTEGER PRIMARY KEY, total_budget INTEGER, expected_profit REAL)''')
    
    # 용역 구성 요소 테이블 생성
    c.execute('''CREATE TABLE IF NOT EXISTS service_components
                 (id INTEGER PRIMARY KEY, category TEXT, subcategory TEXT, status TEXT, budget INTEGER, contact_status TEXT, additional_info TEXT)''')
    
    conn.commit()
    conn.close()

def save_data(data):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    # 기본 정보 저장
    c.execute('''INSERT OR REPLACE INTO basic_info 
                 (id, event_name, client_name, event_type, scale, start_date, end_date, setup, teardown) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
              (1, data.get('event_name'), data.get('client_name'), json.dumps(data.get('event_type')),
               data.get('scale'), data.get('start_date'), data.get('end_date'),
               data.get('setup'), data.get('teardown')))
    
    # 장소 정보 저장
    c.execute('''INSERT OR REPLACE INTO venue_info
                 (id, venue_name, venue_type, address, capacity, facilities)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (1, data.get('venue_name'), data.get('venue_type'), data.get('address'),
               data.get('capacity'), json.dumps(data.get('facilities', []))))
    
    # 예산 정보 저장
    c.execute('''INSERT OR REPLACE INTO budget_info
                 (id, total_budget, expected_profit)
                 VALUES (?, ?, ?)''',
              (1, data.get('total_budget'), data.get('expected_profit')))
    
    # 용역 구성 요소 저장
    c.execute('DELETE FROM service_components')  # 기존 데이터 삭제
    for component in data.get('service_components', []):
        c.execute('''INSERT INTO service_components
                     (category, subcategory, status, budget, contact_status, additional_info)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (component.get('category'), component.get('subcategory'), component.get('status'),
                   component.get('budget'), component.get('contact_status'), component.get('additional_info')))
    
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    data = {}
    
    # 기본 정보 로드
    c.execute('SELECT * FROM basic_info WHERE id = 1')
    basic_info = c.fetchone()
    if basic_info:
        data['event_name'], data['client_name'], event_type, data['scale'], data['start_date'], data['end_date'], data['setup'], data['teardown'] = basic_info[1:]
        data['event_type'] = json.loads(event_type) if event_type else []
    
    # 장소 정보 로드
    c.execute('SELECT * FROM venue_info WHERE id = 1')
    venue_info = c.fetchone()
    if venue_info:
        data['venue_name'], data['venue_type'], data['address'], data['capacity'], facilities = venue_info[1:]
        data['facilities'] = json.loads(facilities) if facilities else []
    
    # 예산 정보 로드
    c.execute('SELECT * FROM budget_info WHERE id = 1')
    budget_info = c.fetchone()
    if budget_info:
        data['total_budget'], data['expected_profit'] = budget_info[1:]
    
    # 용역 구성 요소 로드
    c.execute('SELECT * FROM service_components')
    service_components = c.fetchall()
    data['service_components'] = [
        {
            'category': comp[1],
            'subcategory': comp[2],
            'status': comp[3],
            'budget': comp[4],
            'contact_status': comp[5],
            'additional_info': comp[6]
        } for comp in service_components
    ]
    
    conn.close()
    return data