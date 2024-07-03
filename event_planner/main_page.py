import streamlit as st
import sqlite3
import json
import bcrypt
from main import init_app, basic_info, venue_info, service_components, generate_summary_excel, get_db_connection

def main_page():
    st.title("이벤트 플래너")
    init_app()
    
    if 'event_data' not in st.session_state:
        st.session_state.event_data = {}
    if 'current_event' not in st.session_state:
        st.session_state.current_event = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    menu = st.radio("선택하세요:", ["과거 기록 불러오기", "새로 만들기"])

    if menu == "과거 기록 불러오기":
        load_past_events()
    elif menu == "새로 만들기":
        create_new_event()

    if st.session_state.authenticated:
        display_event_info()

def load_past_events():
    conn = get_db_connection()
    if conn:
        events = conn.execute("SELECT id, event_name FROM events").fetchall()
        event_names = [event['event_name'] for event in events]
        selected_event = st.selectbox("용역명을 선택하세요:", event_names)
        
        if selected_event:
            event_id = next(event['id'] for event in events if event['event_name'] == selected_event)
            if check_password(event_id):
                load_event_data(event_id)
                st.session_state.current_event = event_id
                st.session_state.authenticated = True
                st.experimental_rerun()
        conn.close()

def check_password(event_id):
    conn = get_db_connection()
    if conn:
        stored_password = conn.execute("SELECT password FROM events WHERE id = ?", (event_id,)).fetchone()['password']
        input_password = st.text_input("비밀번호를 입력하세요:", type="password")
        if input_password:
            if bcrypt.checkpw(input_password.encode('utf-8'), stored_password):
                conn.close()
                return True
            else:
                st.error("비밀번호가 일치하지 않습니다.")
        conn.close()
    return False

def create_new_event():
    st.session_state.event_data = {}
    st.session_state.current_event = None
    event_name = st.text_input("새 용역명을 입력하세요:")
    password = st.text_input("비밀번호를 설정하세요:", type="password")
    if event_name and password and st.button("생성"):
        save_new_event(event_name, password)
        st.success("새 용역이 생성되었습니다. 이제 정보를 입력해주세요.")
        st.session_state.authenticated = True
        st.experimental_rerun()

def save_new_event(event_name, password):
    conn = get_db_connection()
    if conn:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        conn.execute("INSERT INTO events (event_name, password) VALUES (?, ?)", (event_name, hashed_password))
        conn.commit()
        conn.close()

def load_event_data(event_id):
    conn = get_db_connection()
    if conn:
        event_data = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
        if event_data:
            st.session_state.event_data = dict(event_data)
            st.session_state.event_data['components'] = json.loads(st.session_state.event_data.get('components', '{}'))
        conn.close()

def display_event_info():
    st.title("이벤트 기획 정의서")
    
    functions = {
        0: basic_info,
        1: venue_info,
        2: service_components,
        3: generate_summary_excel
    }
    
    step_names = ["기본 정보", "장소 정보", "용역 구성 요소", "정의서 생성"]
    
    col1, col2, col3 = st.columns([2,6,2])
    with col2:
        current_step = st.session_state.get('step', 0)
        selected_step = st.selectbox("단계 선택", step_names, index=current_step)
        st.session_state.step = step_names.index(selected_step)
    
    if 0 <= st.session_state.step < len(functions):
        functions[st.session_state.step]()
    else:
        st.error(f"잘못된 단계입니다: {st.session_state.step}")

    if st.button("저장"):
        save_event_data(st.session_state.event_data)
        st.success("이벤트 정보가 저장되었습니다.")

def save_event_data(event_data):
    conn = get_db_connection()
    if conn:
        try:
            with conn:
                conn.execute('''UPDATE events SET 
                                event_name = ?, client_name = ?, event_type = ?, contract_type = ?, scale = ?,
                                start_date = ?, end_date = ?, setup_start = ?, teardown = ?, venue_name = ?,
                                venue_type = ?, address = ?, capacity = ?, facilities = ?, contract_amount = ?,
                                expected_profit = ?, components = ?
                                WHERE id = ?''',
                             (event_data.get('event_name', ''),
                              event_data.get('client_name', ''),
                              event_data.get('event_type', ''),
                              event_data.get('contract_type', ''),
                              event_data.get('scale', 0),
                              event_data.get('start_date', ''),
                              event_data.get('end_date', ''),
                              event_data.get('setup_start', ''),
                              event_data.get('teardown', ''),
                              event_data.get('venue_name', ''),
                              event_data.get('venue_type', ''),
                              event_data.get('address', ''),
                              event_data.get('capacity', ''),
                              event_data.get('facilities', ''),
                              event_data.get('contract_amount', 0),
                              event_data.get('expected_profit', 0),
                              json.dumps(event_data.get('components', {})),
                              st.session_state.current_event))
        except sqlite3.Error as e:
            st.error(f"데이터베이스 저장 중 오류가 발생했습니다: {str(e)}")
        finally:
            conn.close()

if __name__ == "__main__":
    main_page()
