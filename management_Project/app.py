import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from sqlalchemy import create_engine, text
import os

# 금액 포맷 함수 추가
def format_currency(value):
    return f"{value:,.0f}원"

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
                단가 INTEGER,
                개수1 INTEGER,
                단위1 TEXT,
                개수2 INTEGER,
                단위2 TEXT,
                배정예산 INTEGER,
                잔액 INTEGER,
                지출희망금액1 INTEGER,
                지출희망금액2 INTEGER,
                지출희망금액3 INTEGER
            )
        """))
        conn.commit()

def budget_input():
    st.subheader("예산 항목 입력")
    
    # 데이터베이스에서 기존 데이터 불러오기
    with engine.connect() as conn:
        df = pd.read_sql_query(text("SELECT * FROM budget_items"), conn)
    
    if df.empty:
        df = pd.DataFrame(columns=['대분류', '항목명', '단가', '개수1', '단위1', '개수2', '단위2', '배정예산', '잔액', '지출희망금액1', '지출희망금액2', '지출희망금액3'])
    
    # 누락된 열 추가
    for col in ['지출희망금액1', '지출희망금액2', '지출희망금액3']:
        if col not in df.columns:
            df[col] = 0

    # 데이터 편집기 표시
    edited_df = st.data_editor(
        df,
        column_config={
            "대분류": st.column_config.TextColumn(required=True, width="medium"),
            "항목명": st.column_config.TextColumn(required=True, width="large"),
            "단가": st.column_config.NumberColumn(required=True, min_value=0, width="medium", format=format_currency),
            "개수1": st.column_config.NumberColumn(required=True, min_value=1, step=1, width="small"),
            "단위1": st.column_config.TextColumn(required=True, width="small"),
            "개수2": st.column_config.NumberColumn(required=True, min_value=1, step=1, width="small"),
            "단위2": st.column_config.TextColumn(required=True, width="small"),
            "배정예산": st.column_config.NumberColumn(required=True, format=format_currency, width="medium", disabled=True),
            "잔액": st.column_config.NumberColumn(required=True, format=format_currency, width="medium", disabled=True),
            "지출희망금액1": st.column_config.NumberColumn(min_value=0, format=format_currency, width="medium"),
            "지출희망금액2": st.column_config.NumberColumn(min_value=0, format=format_currency, width="medium"),
            "지출희망금액3": st.column_config.NumberColumn(min_value=0, format=format_currency, width="medium"),
        },
        hide_index=True,
        num_rows="dynamic",
        use_container_width=True,
        key="budget_editor"
    )
    
    # 배정예산 및 잔액 계산
    edited_df['배정예산'] = (edited_df['단가'] * edited_df['개수1'] * edited_df['개수2']).astype(int)
    edited_df['잔액'] = (edited_df['배정예산'] - 
                        edited_df['지출희망금액1'].fillna(0) - 
                        edited_df['지출희망금액2'].fillna(0) - 
                        edited_df['지출희망금액3'].fillna(0)).astype(int)

    # 업데이트된 데이터프레임 표시
    st.data_editor(
        edited_df,
        column_config={
            "대분류": st.column_config.TextColumn(required=True, width="medium"),
            "항목명": st.column_config.TextColumn(required=True, width="large"),
            "단가": st.column_config.NumberColumn(required=True, min_value=0, width="medium", format=format_currency),
            "개수1": st.column_config.NumberColumn(required=True, min_value=1, step=1, width="small"),
            "단위1": st.column_config.TextColumn(required=True, width="small"),
            "개수2": st.column_config.NumberColumn(required=True, min_value=1, step=1, width="small"),
            "단위2": st.column_config.TextColumn(required=True, width="small"),
            "배정예산": st.column_config.NumberColumn(required=True, format=format_currency, width="medium", disabled=True),
            "잔액": st.column_config.NumberColumn(required=True, format=format_currency, width="medium", disabled=True),
            "지출희망금액1": st.column_config.NumberColumn(min_value=0, format=format_currency, width="medium"),
            "지출희망금액2": st.column_config.NumberColumn(min_value=0, format=format_currency, width="medium"),
            "지출희망금액3": st.column_config.NumberColumn(min_value=0, format=format_currency, width="medium"),
        },
        hide_index=True,
        use_container_width=True,
        disabled=["배정예산", "잔액"],
        key="updated_budget_editor"
    )
    
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
            # 대분류 선택 (빈 값이 아닌 경우만 포함)
            valid_categories = edited_df['대분류'].dropna().unique().tolist()
            selected_category = st.selectbox("대분류 선택", options=valid_categories)
            
            # 선택된 대분류에 해당하는 항목명만 표시
            valid_items = edited_df[edited_df['대분류'] == selected_category]['항목명'].dropna().unique().tolist()
            selected_item = st.selectbox("항목 선택", options=valid_items)
            
            expense_amount = st.number_input("지출 희망 금액", min_value=0, step=1, value=0)
            partner = st.text_input("협력사")
            
            if st.form_submit_button("��출 승인 요청"):
                item_index = edited_df[(edited_df['대분류'] == selected_category) & (edited_df['항목명'] == selected_item)].index[0]
                if expense_amount <= edited_df.loc[item_index, '잔액']:
                    # 빈 지출희망금액 열 찾기
                    for i in range(1, 4):
                        if pd.isna(edited_df.loc[item_index, f'지출희망금액{i}']):
                            edited_df.loc[item_index, f'지출희망금액{i}'] = expense_amount
                            break
                    else:
                        st.error("더 이상 지출을 추가할 수 없습니다.")
                        return
                    
                    # 잔액 재계산
                    edited_df.loc[item_index, '잔액'] = (edited_df.loc[item_index, '배정예산'] - 
                                                            edited_df.loc[item_index, '지출희망금액1'].fillna(0) - 
                                                            edited_df.loc[item_index, '지출희망금액2'].fillna(0) - 
                                                            edited_df.loc[item_index, '지출희망금액3'].fillna(0)).astype(int)
                    
                    st.success("지출 승인 요청이 완료되었습니다.")
                else:
                    st.error("잔액이 부족합니다.")
                
                # 데이터베이스 업데이트
                with engine.connect() as conn:
                    edited_df.to_sql('budget_items', conn, if_exists='replace', index=False)

    # 지출 내역 표시
    st.subheader("지출 내역")
    st.dataframe(edited_df[['대분류', '항목명', '배정예산', '잔액', '지출희망금액1', '지출희망금액2', '지출희망금액3']])

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
