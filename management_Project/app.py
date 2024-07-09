import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from sqlalchemy import create_engine, text
import os
import openai
from io import BytesIO
import openpyxl

# 데이터베이스 연결 설정
DATABASE = os.path.join(os.getcwd(), 'budget.db')
engine = create_engine(f'sqlite:///{DATABASE}')

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

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
                배정예산 INTEGER
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                budget_item_id INTEGER,
                지출금액 INTEGER,
                지출일자 DATE,
                협력사 TEXT,
                FOREIGN KEY (budget_item_id) REFERENCES budget_items (id)
            )
        """))
        conn.commit()

def budget_input():
    st.subheader("예산 항목 입력")
    
    # 데이터베이스에서 기존 데이터 불러오기
    with engine.connect() as conn:
        df = pd.read_sql_query(text("SELECT * FROM budget_items"), conn)
    
    if df.empty:
        df = pd.DataFrame(columns=['대분류', '항목명', '단가', '개수1', '단위1', '개수2', '단위2'])
    
    # 기존 대분류 목록
    existing_categories = list(df['대분류'].unique())
    
    # 새 대분류 입력
    new_category = st.text_input("새 대분류 이름 (기존 대분류 수정 또는 새로 추가)")
    
    # 대분류 선택 (기존 대분류 + 새로 입력한 대분류)
    all_categories = existing_categories + ([new_category] if new_category and new_category not in existing_categories else [])
    selected_category = st.selectbox("대분류 선택", options=all_categories)
    
    # 선택된 대분류에 대한 항목 표시 및 편집
    category_df = df[df['대분류'] == selected_category] if selected_category in existing_categories else pd.DataFrame(columns=df.columns)
    
    edited_df = st.data_editor(
        category_df,
        column_config={
            "항목명": st.column_config.TextColumn(required=True, width="large"),
            "단가": st.column_config.NumberColumn(required=True, min_value=0, width="medium", format="₩%d"),
            "개수1": st.column_config.NumberColumn(required=True, min_value=1, step=1, width="small"),
            "단위1": st.column_config.TextColumn(required=True, width="small"),
            "개수2": st.column_config.NumberColumn(required=True, min_value=1, step=1, width="small"),
            "단위2": st.column_config.TextColumn(required=True, width="small"),
        },
        hide_index=True,
        num_rows="dynamic",
        key=f"budget_editor_{selected_category}"
    )
    
    # 대분류 열 추가
    edited_df['대분류'] = selected_category
    
    # 배정예산 계산
    edited_df['배정예산'] = (edited_df['단가'] * edited_df['개수1'] * edited_df['개수2']).astype(int)
    
    # 지출희망금액 열 추가
    for col in ['지출희망금액1', '지출희망금액2', '지출희망금액3']:
        if col not in edited_df.columns:
            edited_df[col] = 0
    
    # 잔액 계산
    edited_df['잔액'] = (edited_df['배정예산'] - 
                         edited_df['지출희망금액1'].fillna(0) - 
                         edited_df['지출희망금액2'].fillna(0) - 
                         edited_df['지출희망금액3'].fillna(0)).astype(int)

    if st.button("저장"):
        # 기존 데이터프레임 업데이트
        df = df[df['대분류'] != selected_category]  # 현재 대분류 데이터 제거
        df = pd.concat([df, edited_df], ignore_index=True)  # 새로운 데이터 추가
        
        # 데이터베이스에 저장
        with engine.connect() as conn:
            df.to_sql('budget_items', conn, if_exists='replace', index=False)
        st.success("데이터가 성공적으로 저장되었습니다.")
    
    # 전체 예산 항목 표시
    st.subheader("전체 예산 항목")
    st.data_editor(
        df,
        column_config={
            "대분류": st.column_config.TextColumn(required=True, width="medium"),
            "항목명": st.column_config.TextColumn(required=True, width="large"),
            "단가": st.column_config.NumberColumn(required=True, min_value=0, width="medium", format="₩%d"),
            "개수1": st.column_config.NumberColumn(required=True, min_value=1, step=1, width="small"),
            "단위1": st.column_config.TextColumn(required=True, width="small"),
            "개수2": st.column_config.NumberColumn(required=True, min_value=1, step=1, width="small"),
            "단위2": st.column_config.TextColumn(required=True, width="small"),
            "배정예산": st.column_config.NumberColumn(required=True, format="₩%d", width="medium", disabled=True),
            "잔액": st.column_config.NumberColumn(required=True, format="₩%d", width="medium", disabled=True),
            "지출희망금액1": st.column_config.NumberColumn(min_value=0, format="₩%d", width="medium"),
            "지출희망금액2": st.column_config.NumberColumn(min_value=0, format="₩%d", width="medium"),
            "지출희망금액3": st.column_config.NumberColumn(min_value=0, format="₩%d", width="medium"),
        },
        hide_index=True,
        use_container_width=True,
        disabled=["배정예산", "잔액"],
        key="updated_budget_editor"
    )
    
    # 지출 추가 버튼
    if st.button("지출 추가"):
        st.session_state.show_expense_form = True
    
    # 지출 추가 폼
    if 'show_expense_form' in st.session_state and st.session_state.show_expense_form:
        with st.form("expense_form"):
            # 대분류 선택 (빈 값이 아닌 경우만 포함)
            valid_categories = df['대분류'].dropna().unique().tolist()
            selected_category = st.selectbox("대분류 선택", options=valid_categories)
            
            # 선택된 대분류에 해당하는 항목명만 표시
            valid_items = df[df['대분류'] == selected_category]['항목명'].dropna().unique().tolist()
            selected_item = st.selectbox("항목 선택", options=valid_items)
            
            expense_amount = st.number_input("지출 희망 금액", min_value=0, step=1, value=0)
            partner = st.text_input("협력사")
            
            if st.form_submit_button("지출 승인 요청"):
                item_index = df[(df['대분류'] == selected_category) & (df['항목명'] == selected_item)].index[0]
                if expense_amount <= df.loc[item_index, '잔액']:
                    # 빈 지출희망금액 열 찾기
                    for i in range(1, 4):
                        if pd.isna(df.loc[item_index, f'지출희망금액{i}']):
                            df.loc[item_index, f'지출희망금액{i}'] = expense_amount
                            break
                    else:
                        st.error("더 이상 지출을 추가할 수 없습니다.")
                        return
                    
                    # 잔액 재계산
                    df.loc[item_index, '잔액'] = (df.loc[item_index, '배정예산'] - 
                                                    df.loc[item_index, '지출희망금액1'].fillna(0) - 
                                                    df.loc[item_index, '지출희망금액2'].fillna(0) - 
                                                    df.loc[item_index, '지출희망금액3'].fillna(0)).astype(int)
                    
                    st.success("지출 승인 요청이 완료되었습니다.")
                else:
                    st.error("잔액이 부족합니다.")
                
                # 데이터베이스 업데이트
                with engine.connect() as conn:
                    df.to_sql('budget_items', conn, if_exists='replace', index=False)

def add_expense():
    st.subheader("지출 추가")
    
    # 예산 항목 불러오기
    with engine.connect() as conn:
        budget_items = pd.read_sql_query(text("SELECT * FROM budget_items"), conn)
    
    # 사용자 입력
    selected_item = st.selectbox("항목 선택", options=budget_items['항목명'].tolist())
    expense_amount = st.number_input("지출 금액", min_value=0, step=1000)
    expense_date = st.date_input("지출 일자")
    partner = st.text_input("협력사")
    
    if st.button("지출 추가"):
        item_id = budget_items[budget_items['항목명'] == selected_item]['id'].values[0]
        
        # 지출 추가
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO expenses (budget_item_id, 지출금액, 지출일자, 협력사)
                VALUES (:item_id, :amount, :date, :partner)
            """), {"item_id": item_id, "amount": expense_amount, "date": expense_date, "partner": partner})
            conn.commit()
        
        st.success("지출이 추가되었습니다.")

def view_budget():
    st.subheader("예산 및 지출 현황")
    
    with engine.connect() as conn:
        # 예산 항목과 총 지출액 조회
        df = pd.read_sql_query(text("""
            SELECT bi.*, COALESCE(SUM(e.지출금액), 0) as 총지출액,
                   bi.배정예산 - COALESCE(SUM(e.지출금액), 0) as 잔액
            FROM budget_items bi
            LEFT JOIN expenses e ON bi.id = e.budget_item_id
            GROUP BY bi.id
        """), conn)
    
    st.dataframe(df)

def analyze_excel(df):
    # 데이터프레임을 문자열로 변환
    df_str = df.to_string()
    
    # OpenAI API를 사용하여 데이터 분석
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes Excel data and converts it to a specific format."},
            {"role": "user", "content": f"Analyze this Excel data and convert it to the format with columns: 대분류, 항목명, 단가, 개수1, 단위1, 개수2, 단위2, 배정예산. Here's the data:\n\n{df_str}"}
        ]
    )
    
    # API 응답에서 변환된 데이터 추출
    converted_data = response.choices[0].message['content']
    
    # 변환된 데이터를 데이터프레임으로 변환
    converted_df = pd.read_csv(BytesIO(converted_data.encode()), sep='\s+')
    
    return converted_df

def upload_excel():
    st.subheader("엑셀 파일 업로드")
    
    uploaded_file = st.file_uploader("엑셀 파일을 선택하세요", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.write("원본 데이터:")
        st.dataframe(df)
        
        if st.button("데이터 분석 및 변환"):
            converted_df = analyze_excel(df)
            st.write("변환된 데이터:")
            st.dataframe(converted_df)
            
            if st.button("데이터베이스에 저장"):
                with engine.connect() as conn:
                    converted_df.to_sql('budget_items', conn, if_exists='append', index=False)
                st.success("데이터가 성공적으로 저장되었습니다.")

def main():
    create_tables()
    st.title('예산 관리 시스템')
    
    with st.sidebar:
        selected = option_menu("메뉴", ["예산 입력", "지출 추가", "예산 조회", "엑셀 업로드"], 
            icons=['pencil-fill', 'cash-coin', 'eye-fill', 'file-earmark-excel'], menu_icon="list", default_index=0)


    if selected == "예산 입력":
        budget_input()
    elif selected == "지출 추가":
        add_expense()
    elif selected == "예�� 조회":
        view_budget()
    elif selected == "엑셀 업로드":
        upload_excel()

if __name__ == '__main__':
    main()