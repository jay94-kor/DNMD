import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from sqlalchemy import create_engine, text
import os

# 데이터베이스 연결 설정
DATABASE = os.path.join(os.getcwd(), 'budget.db')
engine = create_engine(f'sqlite:///{DATABASE}')

def create_tables():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS budget_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                항목명 TEXT,
                단가 REAL,
                개 INTEGER,
                규격 TEXT,
                기간 INTEGER,
                단위 TEXT,
                총액 REAL,
                지출희망금액 REAL,
                협력사 TEXT
            )
        """))
        conn.commit()

def budget_input():
    st.subheader("예산 항목 입력")
    
    # 데이터베이스에서 기존 데이터 불러오기
    with engine.connect() as conn:
        df = pd.read_sql_query(text("SELECT * FROM budget_items"), conn)
    
    if df.empty:
        df = pd.DataFrame(columns=['항목명', '단가', '개', '규격', '기간', '단위', '총액', '지출희망금액', '협력사'])
    
    # 데이터 편집기 표시
    edited_df = st.data_editor(
        df,
        column_config={
            "항목명": st.column_config.TextColumn(required=True),
            "단가": st.column_config.NumberColumn(required=True, min_value=0),
            "개": st.column_config.NumberColumn(required=True, min_value=1, step=1),
            "규격": st.column_config.TextColumn(),
            "기간": st.column_config.NumberColumn(required=True, min_value=1, step=1),
            "단위": st.column_config.TextColumn(required=True),
            "총액": st.column_config.NumberColumn(required=True, format="₩%d"),
            "지출희망금액": st.column_config.NumberColumn(required=True, format="₩%d"),
            "협력사": st.column_config.TextColumn(),
        },
        hide_index=True,
        num_rows="dynamic"
    )
    
    # 총액 계산
    edited_df['총액'] = edited_df['단가'] * edited_df['개'] * edited_df['기간']
    
    if st.button("저장"):
        # 데이터베이스에 저장
        with engine.connect() as conn:
            edited_df.to_sql('budget_items', conn, if_exists='replace', index=False)
        st.success("데이터가 성공적으로 저장되었습니다.")

def view_budget():
    st.subheader("예산 조회")
    with engine.connect() as conn:
        df = pd.read_sql_query(text("SELECT * FROM budget_items"), conn)
    st.dataframe(df)

def main():
    create_tables()
    st.title('예산 관리 시스템')
    
    with st.sidebar:
        selected = option_menu("메인 메뉴", ["예산 입력", "예산 조회"], 
            icons=['pencil-fill', 'eye-fill'], menu_icon="list", default_index=0)

    if selected == "예산 입력":
        budget_input()
    elif selected == "예산 조회":
        view_budget()

if __name__ == '__main__':
    main()
