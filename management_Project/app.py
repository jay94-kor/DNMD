import streamlit as st
import pandas as pd
import sqlite3
from sqlalchemy import create_engine

# 데이터베이스 연결 설정
import os
DATABASE = os.path.join(os.getcwd(), 'budget.db')
engine = create_engine(f'sqlite:///{DATABASE}')

# 예산 입력 및 조회 기능
def budget_input():
    project = st.text_input('프로젝트 이름')
    budget = st.number_input('예산 금액', min_value=0)
    
    if st.button('예산 입력'):
        try:
            with engine.connect() as conn:
                conn.execute("INSERT INTO budgets (project, budget) VALUES (?, ?)", (project, budget))
            st.success('예산 입력 완료')
        except Exception as e:
            st.error(f'오류 발생: {str(e)}')

def view_budget():
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM budgets", conn)
    st.dataframe(df)

# 발주 요청 및 예산 차감 기능
def place_order():
    project = st.selectbox('프로젝트 선택', options=get_projects())
    amount = st.number_input('발주 금액', min_value=0)
    
    if st.button('발주 요청'):
        with engine.connect() as conn:
            conn.execute("INSERT INTO orders (project, amount, status) VALUES (?, ?, 'pending')", (project, amount))
            conn.execute("UPDATE budgets SET budget = budget - ? WHERE project = ?", (amount, project))
        st.success('발주 요청 완료 및 예산 차감')

# 예산 현황 조회
def view_remaining_budget():
    with engine.connect() as conn:
        df = pd.read_sql("SELECT project, budget FROM budgets", conn)
    st.dataframe(df)

# 프로젝트 목록 조회
def get_projects():
    with engine.connect() as conn:
        result = conn.execute("SELECT DISTINCT project FROM budgets")
        projects = [row['project'] for row in result]
    return projects

# 테이블 생성 함수
def create_tables():
    with engine.connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT NOT NULL,
                budget REAL NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL
            )
        """)

# 메인 앱 함수
def main():
    create_tables()
    st.title('예산 관리 시스템')
    
    menu = ['예산 입력', '예산 조회', '발주 요청', '잔여 예산 조회']
    choice = st.sidebar.selectbox('메뉴', menu)
    
    if choice == '예산 입력':
        budget_input()
    elif choice == '예산 조회':
        view_budget()
    elif choice == '발주 요청':
        place_order()
    elif choice == '잔여 예산 조회':
        view_remaining_budget()

if __name__ == '__main__':
    main()
