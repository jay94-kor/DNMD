import streamlit as st
import sqlite3
import hashlib
import json
from contextlib import contextmanager
import logging
import streamlit_authenticator as stauth

logging.basicConfig(filename='app.log', level=logging.ERROR)

DATABASE = 'event_planner.db'

class DatabasePool:
    def __init__(self, database_path: str, max_connections: int = 5):
        self.database_path = database_path
        self.max_connections = max_connections
        self.connections = []

    @contextmanager
    def get_connection(self):
        if len(self.connections) < self.max_connections:
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            self.connections.append(conn)
        else:
            conn = self.connections.pop(0)
        
        try:
            yield conn
        finally:
            self.connections.append(conn)

db_pool = DatabasePool(DATABASE)

def get_db_connection() -> Optional[sqlite3.Connection]:
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.OperationalError as e:
        logging.error(f"Database operational error: {str(e)}")
        st.error("데이터베이스 파일을 찾을 수 없습니다.")
    except sqlite3.DatabaseError as e:
        logging.error(f"Database error: {str(e)}")
        st.error("데이터베이스 파일이 손상되었습니다.")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        st.error(f"예상치 못한 오류가 발생했습니다: {str(e)}")
    return None

def init_db() -> None:
    with db_pool.get_connection() as conn:
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS events
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             event_name TEXT,
                             client_name TEXT,
                             manager_name TEXT,
                             manager_contact TEXT,
                             event_type TEXT,
                             contract_type TEXT,
                             scale INTEGER,
                             start_date DATE,
                             end_date DATE,
                             setup_start TEXT,
                             teardown TEXT,
                             venue_name TEXT,
                             venue_type TEXT,
                             address TEXT,
                             capacity TEXT,
                             facilities TEXT,
                             contract_amount INTEGER,
                             expected_profit INTEGER,
                             components TEXT,
                             password_hash TEXT)''')
            
            # 기존 테이블에 password_hash 컬럼 추가 (이미 존재하는 경우 무시)
            try:
                conn.execute('''ALTER TABLE events ADD COLUMN password_hash TEXT''')
            except sqlite3.OperationalError:
                # 컬럼이 이미 존재하는 경우 무시
                pass

def load_past_events():
    conn = get_db_connection()
    if conn:
        try:
            events = conn.execute("SELECT id, event_name, client_name, contract_amount FROM events").fetchall()
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader("저장된 프로젝트 목록")
            with col2:
                if st.button("새로 만들기", key="create_new_event"):
                    st.session_state.current_event = None
                    st.experimental_rerun()
            
            if events:
                for event in events:
                    col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 1, 1])
                    with col1:
                        st.write(event['event_name'])
                    with col2:
                        st.write(event['client_name'])
                    with col3:
                        st.write(event['contract_amount'])
                    with col4:
                        if st.button("수정", key=f"edit_{event['id']}"):
                            if st.session_state.is_admin:
                                st.session_state.current_event = event['id']
                                st.experimental_rerun()
                            else:
                                show_password_prompt(event['id'], "edit")
                    with col5:
                        if st.button("삭제", key=f"delete_{event['id']}"):
                            if st.session_state.is_admin:
                                delete_event(event['id'])
                                st.experimental_rerun()
                            else:
                                show_password_prompt(event['id'], "delete")
            else:
                st.info("저장된 프로젝트가 없습니다.")
        finally:
            conn.close()

def load_past_events():
    conn = get_db_connection()
    if conn:
        try:
            events = conn.execute("SELECT id, event_name, client_name, contract_amount FROM events").fetchall()
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader("저장된 프로젝트 목록")
            with col2:
                if st.button("새로 만들기", key="create_new_event"):
                    st.session_state.current_event = None
                    st.experimental_rerun()
            
            if events:
                for event in events:
                    col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 1, 1])
                    with col1:
                        st.write(event['event_name'])
                    with col2:
                        st.write(event['client_name'])
                    with col3:
                        st.write(event['contract_amount'])
                    with col4:
                        if st.button("수정", key=f"edit_{event['id']}"):
                            if st.session_state.is_admin:
                                st.session_state.current_event = event['id']
                                st.experimental_rerun()
                            else:
                                show_password_prompt(event['id'], "edit")
                    with col5:
                        if st.button("삭제", key=f"delete_{event['id']}"):
                            if st.session_state.is_admin:
                                delete_event(event['id'])
                                st.experimental_rerun()
                            else:
                                show_password_prompt(event['id'], "delete")
            else:
                st.info("저장된 프로젝트가 없습니다.")
        finally:
            conn.close()

def show_password_prompt(event_id, action):
    st.session_state.temp_event_id = event_id
    st.session_state.temp_action = action
    st.session_state.show_password_prompt = True
    st.experimental_rerun()

def check_project_password(event_id, password):
    conn = get_db_connection()
    if conn:
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            result = conn.execute("SELECT * FROM events WHERE id = ? AND password_hash = ?", 
                                  (event_id, hashed_password)).fetchone()
            return result is not None
        finally:
            conn.close()
    return False

def main():
    st.sidebar.title("이벤트 플래너")
    if st.sidebar.button("홈으로 돌아가기"):
        st.session_state.show_password_prompt = False
        st.session_state.current_event = None
        st.experimental_rerun()

    # 어드민 계정 설정
    admin_credentials = {
        "usernames": {
            "dnmd": {
                "name": "Admin",
                "password": stauth.Hasher(["dnmd1234"]).generate()[0]
            }
        }
    }

    authenticator = stauth.Authenticate(
        admin_credentials,
        "event_planner",
        "auth",
        cookie_expiry_days=30
    )

    name, authentication_status, username = authenticator.login("로그인", "main")

    if authentication_status:
        st.write(f'환영합니다 *{name}*')
        st.session_state.is_admin = True
        authenticator.logout("로그아웃", "main")
    elif authentication_status == False:
        st.error('아이디/비밀번호가 올바르지 않습니다')
    elif authentication_status == None:
        st.warning('아이디와 비밀번호를 입력해주세요')

    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False

    if 'show_password_prompt' not in st.session_state:
        st.session_state.show_password_prompt = False
    if 'current_event' not in st.session_state:
        st.session_state.current_event = None
    if 'temp_event_id' not in st.session_state:
        st.session_state.temp_event_id = None
    if 'temp_action' not in st.session_state:
        st.session_state.temp_action = None

    init_db()

    if st.session_state.show_password_prompt and not st.session_state.is_admin:
        password = st.text_input("프로젝트 비밀번호를 입력하세요:", type="password")
        if st.button("확인"):
            if check_project_password(st.session_state.temp_event_id, password):
                if st.session_state.temp_action == "edit":
                    st.session_state.current_event = st.session_state.temp_event_id
                elif st.session_state.temp_action == "delete":
                    delete_event(st.session_state.temp_event_id)
                st.session_state.show_password_prompt = False
                st.experimental_rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")
    elif st.session_state.is_admin:
        if st.session_state.temp_action == "edit":
            st.session_state.current_event = st.session_state.temp_event_id
        elif st.session_state.temp_action == "delete":
            delete_event(st.session_state.temp_event_id)
        st.session_state.show_password_prompt = False
        st.experimental_rerun()
    else:
        load_past_events()
        if st.session_state.current_event is None:
            create_new_event()
        else:
            edit_event(st.session_state.current_event)

# 나머지 함수들 (create_new_event, edit_event, delete_event 등)은 그대로 유지



