import streamlit as st
from streamlit_option_menu import option_menu
from datetime import date, timedelta, datetime
import sqlite3
import json
import pandas as pd
import openpyxl
import os
from typing import Dict, Any, List, Optional

# 상수 정의
DATABASE = 'database.db'
JSON_PATH = os.path.join(os.path.dirname(__file__), 'item_options.json')
EVENT_TYPES = ["영상 제작", "오프라인 이벤트"]
STATUS_OPTIONS = ["발주처와 협상 진행 중", "확정", "거의 확정", "알 수 없는 상태"]

# JSON 파일에서 item_options 로드
with open(JSON_PATH, 'r', encoding='utf-8') as file:
    item_options = json.load(file)

def get_db_connection() -> Optional[sqlite3.Connection]:
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        st.error(f"데이터베이스 연결 오류: {e}")
        return None

def init_db() -> None:
    conn = get_db_connection()
    if conn:
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS events
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             event_name TEXT,
                             client_name TEXT,
                             event_type TEXT,
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
                             components TEXT)''')
        conn.close()

def init_app() -> None:
    if 'step' not in st.session_state:
        st.session_state.step = 0
    if 'event_data' not in st.session_state:
        st.session_state.event_data = {}
    init_db()

def render_option_menu(title: str, options: List[str], icons: List[str], default_index: int, orientation: str = 'vertical', key: Optional[str] = None) -> str:
    return option_menu(title, options, icons=icons, menu_icon="list", default_index=default_index, orientation=orientation, key=key)

def basic_info() -> None:
    event_data = st.session_state.event_data
    st.header("기본 정보")
    
    event_data['scale'] = st.number_input("예상 참여 관객 수", min_value=0, value=int(event_data.get('scale', 0)), key="scale_input_basic")
    
    event_data['event_name'] = st.text_input("행사명", value=event_data.get('event_name', ''), key="event_name_basic", autocomplete="off")
    event_data['client_name'] = st.text_input("클라이언트명", value=event_data.get('client_name', ''), key="client_name_basic")

    default_index = EVENT_TYPES.index(event_data.get('event_type', EVENT_TYPES[0]))
    event_data['event_type'] = render_option_menu("용역 유형", EVENT_TYPES, ['camera-video', 'calendar-event'], default_index, orientation='horizontal', key="event_type")

    st.header("예산 정보")
    event_data['contract_amount'] = st.number_input("총 계약 금액", min_value=0, value=event_data.get('contract_amount', 0), key="contract_amount")
    event_data['expected_profit'] = st.number_input("총 예상 수익", min_value=0, value=event_data.get('expected_profit', 0), key="expected_profit")

    if event_data['event_type'] == "영상 제작":
        handle_video_production(event_data)
    elif event_data['event_type'] == "오프라인 이벤트":
        handle_offline_event(event_data)

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

def venue_info():
    event_data = st.session_state.event_data
    st.header("장소 정보")

    event_data['venue_name'] = st.text_input("장소명", value=event_data.get('venue_name', ''), key="venue_name")
    event_data['venue_type'] = st.text_input("장소 유형", value=event_data.get('venue_type', ''), key="venue_type")
    event_data['address'] = st.text_input("주소", value=event_data.get('address', ''), key="address")
    event_data['capacity'] = st.number_input("수용 인원", min_value=0, value=int(event_data.get('capacity', 0)), key="capacity")
    event_data['facilities'] = st.text_area("시설", value=event_data.get('facilities', ''), key="facilities")

def service_components():
    event_data = st.session_state.event_data
    st.header("용역 구성 요소")

    selected_categories = select_categories(event_data)
    event_data['selected_categories'] = selected_categories

    event_data['components'] = event_data.get('components', {})
    for category in selected_categories:
        st.subheader(category)
        component = event_data['components'].get(category, {})
        
        component['status'] = st.radio(f"{category} 진행 상황", STATUS_OPTIONS, index=STATUS_OPTIONS.index(component.get('status', STATUS_OPTIONS[0])))
        
        component['items'] = st.multiselect(
            f"{category} 항목 선택",
            item_options.get(category, []),
            default=component.get('items', []),
            key=f"{category}_items"
        )

        component['budget'] = st.number_input(f"{category} 예산", min_value=0, value=component.get('budget', 0), key=f"{category}_budget")

        for item in component['items']:
            handle_item_details(item, component)

        event_data['components'][category] = component

    # 선택되지 않은 카테고리 제거
    event_data['components'] = {k: v for k, v in event_data['components'].items() if k in selected_categories}

def select_categories(event_data: Dict[str, Any]) -> List[str]:
    if event_data.get('event_type') == "영상 제작":
        selected_categories = ["미디어"]
        st.write("영상 제작 프로젝트를 위해 '미디어' 카테고리가 자동으로 선택되었습니다.")
    elif event_data.get('venue_type') == "온라인":
        selected_categories = ["미디어"]
        st.write("온라인 이벤트를 위해 '미디어' 카테고리가 자동으로 선택되었습니다.")
    else:
        categories = list(item_options.keys())
        selected_categories = st.multiselect("카테고리 선택", categories, default=event_data.get('selected_categories', []), key="selected_categories")
    return selected_categories

def handle_item_details(item: str, component: Dict[str, Any]) -> None:
    if item in ["유튜브 (예능)", "유튜브 (교육 / 강의)", "유튜브 (인터뷰 형식)", 
                "숏폼 (재편집)", "숏폼 (신규 제작)", "웹드라마", 
                "2D / 모션그래픽 제작", "3D 영상 제작", "행사 배경 영상", 
                "행사 사전 영상", "스케치 영상 제작", "애니메이션 제작"]:
        component[f'{item}_quantity'] = st.number_input(f"{item} 수량", min_value=0, value=component.get(f'{item}_quantity', 0), key=f"{item}_quantity")
        component[f'{item}_unit'] = "편"
    elif item in ["사진 (인물, 컨셉, 포스터 등)", "사진 (행사 스케치)"]:
        component[f'{item}_quantity'] = st.number_input(f"{item} 수량", min_value=0, value=component.get(f'{item}_quantity', 0), key=f"{item}_quantity")
        component[f'{item}_unit'] = "컷"
    else:
        component[f'{item}_quantity'] = st.number_input(f"{item} 수량", min_value=0, value=component.get(f'{item}_quantity', 0), key=f"{item}_quantity")
        component[f'{item}_unit'] = "개"
    
    component[f'{item}_details'] = st.text_area(f"{item} 세부사항", value=component.get(f'{item}_details', ''), key=f"{item}_details")

def generate_summary_excel():
    event_data = st.session_state.event_data
    event_name = event_data.get('event_name', '무제')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    filename = f"이벤트_기획_정의서_{event_name}_{timestamp}.xlsx"
    
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 전체 행사 요약 정의서 생성
            df_full = pd.DataFrame([event_data])
            if 'components' in df_full.columns:
                df_full['components'] = df_full['components'].apply(lambda x: json.dumps(x) if x else None)
            df_full.to_excel(writer, sheet_name='전체 행사 요약', index=False)
            
            # 기본 정보 추가
            workbook = writer.book
            worksheet = workbook['전체 행사 요약']
            worksheet.insert_rows(0, amount=10)
            worksheet['A1'] = "기본 정보"
            worksheet['A2'] = f"행사명: {event_name}"
            worksheet['A3'] = f"고객사: {event_data.get('client_name', '')}"
            worksheet['A4'] = f"행사 유형: {event_data.get('event_type', '')}"
            worksheet['A5'] = f"규모: {event_data.get('scale', '')}명"
            worksheet['A6'] = f"시작일: {event_data.get('start_date', '')}"
            worksheet['A7'] = f"종료일: {event_data.get('end_date', '')}"
            worksheet['A8'] = f"셋업 시작: {event_data.get('setup_start', '')}"
            worksheet['A9'] = f"철수: {event_data.get('teardown', '')}"
            
            # 예산 정보 추가
            worksheet['A11'] = "예산 정보"
            worksheet['A12'] = f"총 계약 금액: {event_data.get('contract_amount', 0)}원"
            worksheet['A13'] = f"총 예상 수익: {event_data.get('expected_profit', 0)}원"
            
            # 카테고리별 예산 정보 추가
            worksheet['A15'] = "카테고리별 예산"
            row = 16
            for cat, comp in event_data.get('components', {}).items():
                budget = comp.get('budget', 0)
                worksheet[f'A{row}'] = f"{cat}: {budget}원"
                row += 1
        
        st.success(f"엑셀 정의서가 생성되었습니다: {filename}")
        
        with open(filename, "rb") as file:
            st.download_button(
                label="엑셀 정의서 다운로드",
                data=file,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        save_event_data(event_data)
        
    except Exception as e:
        st.error(f"엑셀 파일 생성 중 오류가 발생했습니다: {str(e)}")

def generate_category_excel(category, component):
    event_data = st.session_state.event_data
    event_name = event_data.get('event_name', '무제')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    filename = f"발주요청서_{category}_{event_name}_{timestamp}.xlsx"
    
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
            
            # 추가 정보 기입
            workbook = writer.book
            worksheet = workbook[f'{category} 발주요청서']
            
            # 기본 정보 추가
            worksheet.insert_rows(0, amount=10)
            worksheet['A1'] = "기본 정보"
            worksheet['A2'] = f"행사명: {event_name}"
            worksheet['A3'] = f"고객사: {event_data.get('client_name', '')}"
            worksheet['A4'] = f"행사 유형: {event_data.get('event_type', '')}"
            worksheet['A5'] = f"규모: {event_data.get('scale', '')}명"
            worksheet['A6'] = f"시작일: {event_data.get('start_date', '')}"
            worksheet['A7'] = f"종료일: {event_data.get('end_date', '')}"
            worksheet['A8'] = f"셋업 시작: {event_data.get('setup_start', '')}"
            worksheet['A9'] = f"철수: {event_data.get('teardown', '')}"
            
            # 예산 정보 추가
            worksheet['A11'] = "예산 정보"
            worksheet['A12'] = f"총 계약 금액: {event_data.get('contract_amount', 0)}원"
            worksheet['A13'] = f"총 예상 수익: {event_data.get('expected_profit', 0)}원"
            
            # 발주요청서 정보 추가
            worksheet['A15'] = "발주요청서"
            worksheet['A16'] = f"카테고리: {category}"
            worksheet['A17'] = f"진행 상황: {component.get('status', '')}"
            worksheet['A18'] = f"예산: {component.get('budget', 0)}원"
        
        st.success(f"엑셀 발주요청서가 생성되었습니다: {filename}")
        
        with open(filename, "rb") as file:
            st.download_button(
                label=f"{category} 발주요청서 다운로드",
                data=file,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        save_event_data(event_data)
        
    except Exception as e:
        st.error(f"엑셀 파일 생성 중 오류가 발생했습니다: {str(e)}")

def save_event_data(event_data):
    conn = get_db_connection()
    if conn:
        try:
            with conn:
                conn.execute('''INSERT INTO events (event_name, client_name, event_type, scale, start_date, end_date, setup_start, teardown, venue_name, venue_type, address, capacity, facilities, contract_amount, expected_profit, components)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                             (event_data.get('event_name', ''),
                              event_data.get('client_name', ''),
                              event_data.get('event_type', ''),
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
                              json.dumps(event_data.get('components', {}))))
            st.success("이벤트 정보가 저장되었습니다.")
        except sqlite3.Error as e:
            st.error(f"데이터베이스 저장 중 오류가 발생했습니다: {str(e)}")
        finally:
            conn.close()
    else:
        st.error("데이터베이스 연결에 실패했습니다.")

def main():
    init_app()
    
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
        if not isinstance(current_step, int) or current_step < 0 or current_step >= len(step_names):
            current_step = 0  # 유효하지 않은 값일 경우 기본값으로 설정
        selected_step = option_menu("단계", step_names, 
                                    icons=['info-circle', 'geo-alt', 'list-task', 'file-earmark-spreadsheet'], 
                                    menu_icon="cast", 
                                    default_index=current_step,  # default_index 사용
                                    orientation="horizontal")
        st.session_state.step = step_names.index(selected_step)
    
    if 0 <= st.session_state.step < len(functions):
        functions[st.session_state.step]()
    else:
        st.error(f"잘못된 단계입니다: {st.session_state.step}")
    
    if st.session_state.step < 3:
        col1, col2, col3 = st.columns([6,1,3])
        with col3:
            if st.button("다음 단계로"):
                st.session_state.step = min(st.session_state.step + 1, 3)
                st.experimental_rerun()
    
    if st.session_state.step > 0:
        col1, col2, col3 = st.columns([3,1,6])
        with col1:
            if st.button("이전 단계로"):
                st.session_state.step = max(st.session_state.step - 1, 0)
                st.experimental_rerun()

if __name__ == "__main__":
    main()