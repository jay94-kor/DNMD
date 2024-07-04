import streamlit as st
from streamlit_option_menu import option_menu
from datetime import date, timedelta, datetime
import sqlite3
import json
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill
import os
from typing import Dict, Any, List, Optional
import bcrypt
from contextlib import contextmanager
import logging
import streamlit_authenticator as stauth

logging.basicConfig(filename='app.log', level=logging.ERROR)

DATABASE = 'event_planner.db'
JSON_PATH = os.path.join(os.path.dirname(__file__), 'item_options.json')

EVENT_TABLE_COLUMNS = [
    'event_name', 'client_name', 'manager_name', 'manager_contact', 'event_type', 
    'contract_type', 'scale', 'start_date', 'end_date', 'setup_start', 'teardown',
    'venue_name', 'venue_type', 'address', 'capacity', 'facilities',
    'contract_amount', 'expected_profit', 'components'
]

class EventOptions:
    def __init__(self, item_options):
        self.EVENT_TYPES = item_options['EVENT_TYPES']
        self.CONTRACT_TYPES = item_options['CONTRACT_TYPES']
        self.STATUS_OPTIONS = item_options['STATUS_OPTIONS']
        self.MEDIA_ITEMS = item_options['MEDIA_ITEMS']
        self.CATEGORIES = item_options['CATEGORIES']

# JSON 파일에서 item_options 로드
with open(JSON_PATH, 'r', encoding='utf-8') as file:
    item_options = json.load(file)

event_options = EventOptions(item_options)

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
            
            try:
                conn.execute('''ALTER TABLE events ADD COLUMN password_hash TEXT''')
            except sqlite3.OperationalError:
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
                    st.session_state.step = 0  # 기본 정보 입력 페이지로 이동
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

# 이벤트 데이터 저장 함수
def save_event_data(event_data: Dict[str, Any]) -> None:
    try:
        with db_pool.get_connection() as conn:
            conn.execute(f'''UPDATE events SET 
                {','.join([f'{col} = ?' for col in EVENT_TABLE_COLUMNS])} WHERE id = ?''',
                [event_data.get(col, '') for col in EVENT_TABLE_COLUMNS] + [st.session_state.current_event])
        st.success("이벤트 정보가 저장되었습니다.")
    except sqlite3.Error as e:
        error_msg = f"데이터베이스 저장 중 오류가 발생했습니다: {str(e)}"
        logging.error(error_msg)
        st.error(error_msg)
    except Exception as e:
        error_msg = f"예상치 못한 오류가 발생했습니다: {str(e)}"
        logging.error(error_msg)
        st.error(error_msg)

# 이벤트 삭제 함수
def delete_event(event_id: int) -> None:
    conn = get_db_connection()
    if conn:
        try:
            conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
            conn.commit()
            st.success("프로젝트가 삭제되었습니다.")
        except sqlite3.Error as e:
            st.error(f"프로젝트 삭제 중 오류가 발생했습니다: {str(e)}")
        finally:
            conn.close()

# 이벤트 데이터 불러오기 함수
def load_event_data(event_id: int) -> None:
    conn = get_db_connection()
    if conn:
        try:
            event_data = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
            if event_data:
                st.session_state.event_data = dict(event_data)
                st.session_state.event_data['components'] = json.loads(st.session_state.event_data.get('components', '{}'))
        finally:
            conn.close()

# 기본 정보 입력 함수
def basic_info() -> None:
    event_data = st.session_state.event_data
    st.header("기본 정보")
    
    handle_general_info(event_data)
    handle_event_type(event_data)
    handle_budget_info(event_data)
    
    if event_data['event_type'] == "영상 제작":
        handle_video_production(event_data)
    elif event_data['event_type'] == "오프라인 이벤트":
        handle_offline_event(event_data)

def handle_general_info(event_data: Dict[str, Any]) -> None:
    event_data['scale'] = st.number_input("예상 참여 관객 수", min_value=0, value=int(event_data.get('scale', 0)), key="scale_input_basic")
    event_data['event_name'] = st.text_input("용역명", value=event_data.get('event_name', ''), key="event_name_basic", autocomplete="off")
    event_data['client_name'] = st.text_input("클라이언트명", value=event_data.get('client_name', ''), key="client_name_basic")
    event_data['manager_name'] = st.text_input("담당자명", value=event_data.get('manager_name', ''), key="manager_name_basic", required=True)
    event_data['manager_contact'] = st.text_input("담당자 연락처", value=event_data.get('manager_contact', ''), key="manager_contact_basic", required=True)

def handle_event_type(event_data: Dict[str, Any]) -> None:
    default_index = event_options.EVENT_TYPES.index(event_data.get('event_type', event_options.EVENT_TYPES[0]))
    event_data['event_type'] = render_option_menu("용역 유형", event_options.EVENT_TYPES, ['calendar-event', 'camera-video'], default_index, orientation='horizontal', key="event_type")

    default_contract_index = event_options.CONTRACT_TYPES.index(event_data.get('contract_type', event_options.CONTRACT_TYPES[0]))
    event_data['contract_type'] = render_option_menu("용역 종류", event_options.CONTRACT_TYPES, ['file-earmark-text', 'person-lines-fill', 'building'], default_contract_index, orientation='horizontal', key="contract_type")

def handle_budget_info(event_data: Dict[str, Any]) -> None:
    st.header("예산 정보")
    event_data['contract_amount'] = st.number_input("총 계약 금액", min_value=0, value=event_data.get('contract_amount', 0), key="contract_amount")
    event_data['expected_profit'] = st.number_input("총 예상 수익", min_value=0, value=event_data.get('expected_profit', 0), key="expected_profit")

def handle_video_production(event_data: Dict[str, Any]) -> None:
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("과업 시작일", value=event_data.get('start_date', date.today()), key="start_date")
    with col2:
        end_date = st.date_input("과업 종료일", value=event_data.get('end_date', start_date + timedelta(days=365)), key="end_date")

    if start_date > end_date:
        end_date = start_date + timedelta(days=365)
        st.warning("과업 종료일이 시작일 이전이어서 자동으로 조정되었습니다.")

    event_data['start_date'] = start_date
    event_data['end_date'] = end_date
    
    duration = (end_date - start_date).days
    months, days = divmod(duration, 30)
    st.write(f"과업 기간: {months}개월 {days}일")

def handle_offline_event(event_data: Dict[str, Any]) -> None:
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("행사 시작일", value=event_data.get('start_date', date.today()), key="start_date")
    with col2:
        end_date = st.date_input("행사 종료일", value=event_data.get('end_date', start_date + timedelta(days=1)), key="end_date")

    if start_date > end_date:
        end_date = start_date + timedelta(days=1)
        st.warning("행사 종료일이 시작일 이전이어서 자동으로 조정되었습니다.")

    event_data['start_date'] = start_date
    event_data['end_date'] = end_date

    event_data['setup_start'] = st.text_input("셋업 시작", value=event_data.get('setup_start', ''), key="setup_start")
    event_data['teardown'] = st.text_input("철수", value=event_data.get('teardown', ''), key="teardown")

# 장소 정보 입력 함수
def venue_info() -> None:
    event_data = st.session_state.event_data
    st.header("장소 정보")

    event_data['venue_name'] = st.text_input("장소명", value=event_data.get('venue_name', ''), key="venue_name")
    event_data['venue_type'] = st.text_input("장소 유형", value=event_data.get('venue_type', ''), key="venue_type")
    event_data['address'] = st.text_input("주소", value=event_data.get('address', ''), key="address")
    event_data['capacity'] = st.number_input("수용 인원", min_value=0, value=int(event_data.get('capacity', 0)), key="capacity")
    event_data['facilities'] = st.text_area("시설", value=event_data.get('facilities', ''), key="facilities")

# 용역 구성 요소 입력 함수
def service_components() -> None:
    event_data = st.session_state.event_data
    st.header("용역 구성 요소")

    selected_categories = select_categories(event_data)
    event_data['selected_categories'] = selected_categories

    event_data['components'] = event_data.get('components', {})
    for category in selected_categories:
        handle_category(category, event_data)

    event_data['components'] = {k: v for k, v in event_data['components'].items() if k in selected_categories}

def handle_category(category: str, event_data: Dict[str, Any]) -> None:
    st.subheader(category)
    component = event_data['components'].get(category, {})
    
    component['status'] = st.radio(f"{category} 진행 상황", event_options.STATUS_OPTIONS, index=event_options.STATUS_OPTIONS.index(component.get('status', event_options.STATUS_OPTIONS[0])))
    
    component['items'] = st.multiselect(
        f"{category} 항목 선택",
        event_options.CATEGORIES.get(category, []),
        default=component.get('items', []),
        key=f"{category}_items"
    )

    component['budget'] = st.number_input(f"{category} 예산 (만원)", min_value=0, value=component.get('budget', 0), key=f"{category}_budget")

    handle_preferred_vendor(component, category)

    for item in component['items']:
        handle_item_details(item, component)

    event_data['components'][category] = component

def handle_preferred_vendor(component: Dict[str, Any], category: str) -> None:
    component['preferred_vendor'] = st.checkbox("이 카테고리에 대해 선호하는 업체가 있습니까?", key=f"{category}_preferred_vendor")
    
    if component['preferred_vendor']:
        component['vendor_reason'] = st.radio(
            "선호하는 이유를 선택해주세요:",
            ["발주처의 지정", "동일 과업 진행 경험", "퀄리티 만족한 경험"],
            key=f"{category}_vendor_reason"
        )
        component['vendor_name'] = st.text_input("선호 업체 상호명", value=component.get('vendor_name', ''), key=f"{category}_vendor_name")
        component['vendor_contact'] = st.text_input("선호 업체 연락처", value=component.get('vendor_contact', ''), key=f"{category}_vendor_contact")
        component['vendor_manager'] = st.text_input("선호 업체 담당자명", value=component.get('vendor_manager', ''), key=f"{category}_vendor_manager")

def handle_item_details(item: str, component: Dict[str, Any]) -> None:
    quantity_key = f'{item}_quantity'
    unit_key = f'{item}_unit'
    details_key = f'{item}_details'

    component[quantity_key] = st.number_input(f"{item} 수량", min_value=0, value=component.get(quantity_key, 0), key=quantity_key)
    
    if item in ["유튜브 (예능)", "유튜브 (교육 / 강의)", "유튜브 (인터뷰 형식)", 
                "숏폼 (재편집)", "숏폼 (신규 제작)", "웹드라마", 
                "2D / 모션그래픽 제작", "3D 영상 제작", "행사 배경 영상", 
                "행사 사전 영상", "스케치 영상 제작", "애니메이션 제작"]:
        component[unit_key] = "편"
    elif item in ["사진 (인물, 컨셉, 포스터 등)", "사진 (행사 스케치)"]:
        component[unit_key] = "컷"
    else:
        component[unit_key] = "개"
    
    component[details_key] = st.text_area(f"{item} 세부사항", value=component.get(details_key, ''), key=details_key)

def select_categories(event_data: Dict[str, Any]) -> List[str]:
    categories = list(item_options['CATEGORIES'].keys())
    default_categories = event_data.get('selected_categories', [])
    default_categories = [cat for cat in default_categories if cat in categories]

    if event_data.get('event_type') == "영상 제작" and "미디어" not in default_categories:
        default_categories.append("미디어")
        st.info("영상 제작 프로젝트를 위해 '미디어' 카테고리가 자동으로 추가되었습니다.")
    elif event_data.get('venue_type') == "온라인" and "미디어" not in default_categories:
        default_categories.append("미디어")
        st.info("온라인 이벤트를 위해 '미디어' 카테고리가 자동으로 추가되었습니다.")

    selected_categories = st.multiselect("카테고리 선택", categories, default=default_categories, key="selected_categories")
    return selected_categories

def generate_summary_excel() -> None:
    event_data = st.session_state.event_data
    event_name = event_data.get('event_name', '무제')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    summary_filename = f"이벤트_기획_정의서_{event_name}_{timestamp}.xlsx"
    
    try:
        create_excel_summary(event_data, summary_filename)
        st.success(f"엑셀 정의서가 생성되었습니다: {summary_filename}")
        
        with open(summary_filename, "rb") as file:
            st.download_button(label="전체 행사 요약 정의서 다운로드", data=file, file_name=summary_filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        for category, component in event_data.get('components', {}).items():
            category_filename = f"발주요청서_{category}_{event_name}_{timestamp}.xlsx"
            generate_category_excel(category, component, category_filename)
            with open(category_filename, "rb") as file:
                st.download_button(label=f"{category} 발주요청서 다운로드", data=file, file_name=category_filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"download_{category}")
        
        save_event_data(event_data)
    except Exception as e:
        st.error(f"엑셀 파일 생성 중 오류가 발생했습니다: {str(e)}")

def create_excel_summary(event_data: Dict[str, Any], filename: str) -> None:
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df_full = pd.DataFrame([event_data])
        if 'components' in df_full.columns:
            df_full['components'] = df_full['components'].apply(lambda x: json.dumps(x) if x else None)
        df_full.to_excel(writer, sheet_name='전체 행사 요약', index=False)
        
        workbook = writer.book
        worksheet = workbook['전체 행사 요약']
        add_basic_info(worksheet, event_data)

def add_basic_info(worksheet: openpyxl.worksheet.worksheet.Worksheet, event_data: Dict[str, Any]) -> None:
    worksheet.insert_rows(0, amount=10)
    worksheet['A1'] = "기본 정보"
    worksheet['A2'] = f"용역명: {event_data.get('event_name', '')}"
    worksheet['A3'] = f"고객사: {event_data.get('client_name', '')}"
    worksheet['A4'] = f"행사 유형: {event_data.get('event_type', '')}"
    worksheet['A5'] = f"규모: {event_data.get('scale', '')}명"
    worksheet['A6'] = f"시작일: {event_data.get('start_date', '')}"
    worksheet['A7'] = f"종료일: {event_data.get('end_date', '')}"
    worksheet['A8'] = f"셋업 시작: {event_data.get('setup_start', '')}"
    worksheet['A9'] = f"철수: {event_data.get('teardown', '')}"
    
    worksheet['A11'] = "예산 정보"
    worksheet['A12'] = f"총 계약 금액: {event_data.get('contract_amount', 0)}만원"
    worksheet['A13'] = f"총 예상 수익: {event_data.get('expected_profit', 0)}만원"

    title_font = Font(bold=True, size=14)
    subtitle_font = Font(bold=True, size=12)
    fill = PatternFill(start_color="FFFFE0", end_color="FFFFE0", fill_type="solid")

    for cell in ['A1', 'A11']:
        worksheet[cell].font = title_font
        worksheet[cell].fill = fill

    for cell in ['A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A12', 'A13']:
        worksheet[cell].font = subtitle_font

def generate_category_excel(category: str, component: Dict[str, Any], filename: str) -> None:
    event_data = st.session_state.event_data
    event_name = event_data.get('event_name', '무제')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df_component = pd.DataFrame(columns=['항목', '수량', '단위', '세부사항'])
            for item in component.get('items', []):
                quantity = component.get(f'{item}_quantity', 0)
                unit = component.get(f'{item}_unit', '개')
                details = component.get(f'{item}_details', '')
                df_component = pd.concat([df_component, pd.DataFrame({
                    '항목': [item],
                    '수량': [quantity],
                    '단위': [unit],
                    '세부사항': [details]
                })], ignore_index=True)
            
            df_component.to_excel(writer, sheet_name=f'{category} 발주요청서', index=False)
            
            workbook = writer.book
            worksheet = workbook[f'{category} 발주요청서']
            
            add_category_info(worksheet, event_data, category, component)
        
        st.success(f"엑셀 발주요청서가 생성되었습니다: {filename}")
        
    except Exception as e:
        st.error(f"{category} 발주요청서 생성 중 오류가 발생했습니다: {str(e)}")

def add_category_info(worksheet: openpyxl.worksheet.worksheet.Worksheet, event_data: Dict[str, Any], category: str, component: Dict[str, Any]) -> None:
    worksheet.insert_rows(0, amount=10)
    worksheet['A1'] = "기본 정보"
    worksheet['A2'] = f"용역명: {event_data.get('event_name', '')}"
    worksheet['A3'] = f"고객사: {event_data.get('client_name', '')}"
    worksheet['A4'] = f"행사 유형: {event_data.get('event_type', '')}"
    worksheet['A5'] = f"규모: {event_data.get('scale', '')}명"
    worksheet['A6'] = f"시작일: {event_data.get('start_date', '')}"
    worksheet['A7'] = f"종료일: {event_data.get('end_date', '')}"
    worksheet['A8'] = f"셋업 시작: {event_data.get('setup_start', '')}"
    worksheet['A9'] = f"철수: {event_data.get('teardown', '')}"
    
    worksheet['A11'] = "예산 정보"
    worksheet['A12'] = f"총 계약 금액: {event_data.get('contract_amount', 0)}만원"
    worksheet['A13'] = f"총 예상 수익: {event_data.get('expected_profit', 0)}만원"
    
    worksheet['A15'] = "발주요청서"
    worksheet['A16'] = f"카테고리: {category}"
    worksheet['A17'] = f"진행 상황: {component.get('status', '')}"
    worksheet['A18'] = f"예산: {component.get('budget', 0)}만원"

    worksheet['A19'] = f"선호 업체 여부: {'예' if component.get('preferred_vendor', False) else '아니오'}"
    if component.get('preferred_vendor', False):
        worksheet['A20'] = f"선호 이유: {component.get('vendor_reason', '')}"
        worksheet['A21'] = f"선호 업체 상호명: {component.get('vendor_name', '')}"
        worksheet['A22'] = f"선호 업체 연락처: {component.get('vendor_contact', '')}"
        worksheet['A23'] = f"선호 업체 담당자명: {component.get('vendor_manager', '')}"
    
    title_font = Font(bold=True, size=14)
    subtitle_font = Font(bold=True, size=12)
    fill = PatternFill(start_color="FFFFE0", end_color="FFFFE0", fill_type="solid")

    for cell in ['A1', 'A11', 'A15']:
        worksheet[cell].font = title_font
        worksheet[cell].fill = fill

    for cell in ['A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A12', 'A13', 'A16', 'A17', 'A18']:
        worksheet[cell].font = subtitle_font

def admin_page():
    st.title("관리자 페이지")
    
    st.header("새 사용자 추가")
    new_username = st.text_input("사용자명")
    new_name = st.text_input("이름")
    new_password = st.text_input("비밀번호", type="password")
    new_email = st.text_input("이메일")
    if st.button("사용자 추가"):
        try:
            add_user(new_username, new_name, new_password, new_email)
            st.success("사용자가 추가되었습니다.")
        except sqlite3.IntegrityError:
            st.error("이미 존재하는 사용자명입니다.")
        except Exception as e:
            st.error(f"사용자 추가 중 오류가 발생했습니다: {str(e)}")

    st.header("기존 사용자 목록")
    users = get_users()
    for user in users:
        st.write(f"사용자명: {user['username']}, 이름: {user['name']}")

def event_management():
    menu = st.radio("선택하세요:", ["과거 기록 불러오기", "새로 만들기"])

    if menu == "과거 기록 불러오기":
        load_past_events()
    elif menu == "새로 만들기":
        create_new_event()

    if st.session_state.current_event is not None:
        display_event_info()

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
        selected_step = render_option_menu("단계 선택", step_names, ['info-circle', 'geo-alt', 'list-task', 'file-earmark-spreadsheet'], current_step, orientation='horizontal')
        st.session_state.step = step_names.index(selected_step)
    
    if 0 <= st.session_state.step < len(functions):
        functions[st.session_state.step]()
    else:
        st.error(f"잘못된 단계입니다: {st.session_state.step}")
    
    col1, col2, col3 = st.columns([3,4,3])
    with col1:
        if st.session_state.step > 0 and st.button("이전 단계로"):
            st.session_state.step = max(st.session_state.step - 1, 0)
    with col3:
        if st.session_state.step < 3 and st.button("다음 단계로"):
            st.session_state.step = min(st.session_state.step + 1, 3)

def register_user():
    st.subheader("회원가입")
    new_username = st.text_input("사용자명")
    new_name = st.text_input("이름")
    new_email = st.text_input("이메일")
    new_password = st.text_input("비밀번호", type="password")
    confirm_password = st.text_input("비밀번호 확인", type="password")

    if st.button("회원가입"):
        if new_password != confirm_password:
            st.error("비밀번호가 일치하지 않습니다.")
        elif len(new_password) < 8:
            st.error("비밀번호는 최소 8자 이상이어야 합니다.")
        else:
            try:
                add_user(new_username, new_name, new_password, new_email)
                st.success("회원가입이 완료되었습니다. 이제 로그인할 수 있습니다.")
            except sqlite3.IntegrityError:
                st.error("이미 존재하는 사용자명 또는 이메일입니다.")
            except Exception as e:
                st.error(f"회원가입 중 오류가 발생했습니다: {str(e)}")

def main():
    st.title("이벤트 플래너")
    init_db()

    if 'auth_required' not in st.session_state:
        st.session_state.auth_required = False
    if 'current_event' not in st.session_state:
        st.session_state.current_event = None
    if 'step' not in st.session_state:
        st.session_state.step = 0
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'event_data' not in st.session_state:
        st.session_state.event_data = {}

    if not st.session_state.auth_required:
        load_past_events()
    else:
        st.header("관리자 로그인")
        users = get_users()
        credentials = {"usernames": {}}
        for user in users:
            credentials["usernames"][user["username"]] = {
                "name": user["name"],
                "password": user["password"]
            }

        authenticator = stauth.Authenticate(
            credentials,
            "event_planner",
            "abcdef",
            cookie_expiry_days=30
        )

        name, authentication_status, username = authenticator.login("로그인", "main")

        if authentication_status:
            authenticator.logout("로그아웃", "main")
            st.write(f"환영합니다 *{name}*")
            st.session_state.authenticated = True
            st.session_state.auth_required = False
            load_event_data(st.session_state.current_event)
            display_event_info()
        elif authentication_status == False:
            st.error("사용자명/비밀번호가 일치하지 않습니다.")
        elif authentication_status == None:
            st.warning("사용자명과 비밀번호를 입력해주세요.")

if __name__ == "__main__":
    main()
