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
                대분류 TEXT,
                항목명 TEXT,
                단가 REAL,
                개수1 INTEGER,
                단위1 TEXT,
                개수2 INTEGER,
                단위2 TEXT,
                배정예산 REAL,
                잔액 REAL
            )
        """))
        conn.commit()

def budget_input():
    st.subheader("예산 항목 입력")
    
    # 데이터베이스에서 기존 데이터 불러오기
    with engine.connect() as conn:
        df = pd.read_sql_query(text("SELECT * FROM budget_items"), conn)
    
    if df.empty:
        df = pd.DataFrame(columns=['대분류', '항목명', '단가', '개수1', '단위1', '개수2', '단위2', '배정예산', '잔액'])
    
    # 데이터 편집기 표시
    edited_df = st.data_editor(
        df,
        column_config={
            "대분류": st.column_config.TextColumn(required=True, width="medium"),
            "항목명": st.column_config.TextColumn(required=True, width="large"),
            "단가": st.column_config.NumberColumn(required=True, min_value=0, width="medium"),
            "개수1": st.column_config.NumberColumn(required=True, min_value=1, step=1, width="small"),
            "단위1": st.column_config.TextColumn(required=True, width="small"),
            "개수2": st.column_config.NumberColumn(required=True, min_value=1, step=1, width="small"),
            "단위2": st.column_config.TextColumn(required=True, width="small"),
            "배정예산": st.column_config.NumberColumn(required=True, format="₩%d", width="medium"),
            "잔액": st.column_config.NumberColumn(required=True, format="₩%d", width="medium"),
        },
        hide_index=True,
        num_rows="dynamic",
        use_container_width=True,
    )
    
    # 잔액 계산
    edited_df['잔액'] = edited_df['배정예산']
    
    if st.button("저장"):
        # 데이터베이스에 저장
        with engine.connect() as conn:
            edited_df.to_sql('budget_items', conn, if_exists='replace', index=False)
        st.success("데이터가 성공적으로 저장되었습니다.")
    
    # 지출 추가 버튼
    if st.button("지출 추가"):
        st.session_state.show_expense_form = True
    
    # 지출 추가 폼
    if 'show_expense_form' in st.session_state and st.session_state.show_expense_form:
        with st.form("expense_form"):
            selected_category = st.selectbox("대분류 선택", options=edited_df['대분류'].unique().tolist())
            selected_items = edited_df[edited_df['대분류'] == selected_category]['항목명'].tolist()
            selected_item = st.selectbox("항목 선택", options=selected_items)
            expense_amount = st.number_input("지출 희망 금액", min_value=0)
            partner = st.text_input("협력사")
            
            if st.form_submit_button("지출 승인 요청"):
                item_index = edited_df[(edited_df['대분류'] == selected_category) & (edited_df['항목명'] == selected_item)].index[0]
                if expense_amount <= edited_df.loc[item_index, '잔액']:
                    edited_df.loc[item_index, '잔액'] -= expense_amount
                    # 여기에 지출 정보를 별도의 테이블에 저장하는 로직을 추가할 수 있습니다.
                    st.success("지출 승인 요청이 완료되었습니다.")
                else:
                    st.error("잔액이 부족합니다.")
                
                # 데이터베이스 업데이트
                with engine.connect() as conn:
                    edited_df.to_sql('budget_items', conn, if_exists='replace', index=False)

    # 지출 내역 표시
    st.subheader("지출 내역")
    # 여기에 지출 내역을 표시하는 코드를 추가할 수 있습니다.

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
