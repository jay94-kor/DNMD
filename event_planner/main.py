import streamlit as st
from streamlit_option_menu import option_menu
from datetime import date, timedelta, datetime
import sqlite3
import json
import pandas as pd
import openpyxl

DATABASE = 'database.db'

# JSON 파일에서 item_options 로드
with open('item_options.json', 'r', encoding='utf-8') as file:
    item_options = json.load(file)

# 데이터베이스 연결 함수
def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        st.error(f"데이터베이스 연결 오류: {e}")
        return None

# 데이터베이스 초기화
def init_db():
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

# 앱 초기화
def init_app():
    if 'step' not in st.session_state:
        st.session_state.step = 0
    if 'event_data' not in st.session_state:
        st.session_state.event_data = {}
    init_db()

def render_option_menu(title, options, icons, default_index, orientation='vertical', key=None):
    return option_menu(title, options, icons=icons, menu_icon="list", default_index=default_index, orientation=orientation, key=key)

def basic_info():
    st.header("기본 정보")
    event_data = st.session_state.event_data
    event_data['scale'] = st.number_input("예상 참여 관객 수", min_value=0, value=int(event_data.get('scale', 0)), key="scale_input")
    event_data['event_name'] = st.text_input("행사명", value=event_data.get('event_name', ''), key="event_name")
    event_data['client_name'] = st.text_input("클라이언트명", value=event_data.get('client_name', ''), key="client_name")

    event_types = ["영상 제작", "오프라인 이벤트"]
    default_index = event_types.index(event_data.get('event_type', event_types[0]))
    event_data['event_type'] = render_option_menu("용역 유형", event_types, ['camera-video', 'calendar-event'], default_index, orientation='horizontal', key="event_type")

    if event_data['event_type'] == "영상 제작":
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
        months = duration // 30
        days = duration % 30
        st.write(f"과업 기간: {months}개월 {days}일")

    if event_data['event_type'] == "오프라인 이벤트":
        event_data['scale'] = st.number_input("예상 참여 관객 수", min_value=0, value=int(event_data.get('scale', 0)))
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("행사 시작일", value=event_data.get('start_date', date.today()))
        with col2:
            end_date = st.date_input("행사 종료일", value=event_data.get('end_date', start_date + timedelta(days=1)))

        if start_date > end_date:
            end_date = start_date + timedelta(days=1)
            st.warning("행사 종료일이 시작일 이전이어서 자동으로 조정되었습니다.")

        event_data['start_date'] = start_date
        event_data['end_date'] = end_date
        
        setup_options = ["전날부터", "당일"]
        teardown_options = ["당일 철수", "다음날 철수"]

        default_setup = setup_options.index(event_data.get('setup', setup_options[0]))
        event_data['setup'] = render_option_menu("셋업 시작", setup_options, ['moon', 'sun'], default_setup, 'horizontal')

        default_teardown = teardown_options.index(event_data.get('teardown', teardown_options[0]))
        event_data['teardown'] = render_option_menu("철수", teardown_options, ['sun', 'sunrise'], default_teardown, 'horizontal')

def venue_info():
    st.header("장소 정보")
    event_data = st.session_state.event_data

    if event_data.get('event_type') == "영상 제작":
        st.write("영상 제작 프로젝트는 장소 정보가 필요하지 않습니다.")
        return
    if 'venue_decided' not in st.session_state:
        st.session_state.venue_decided = "아니오"
    if 'venue_type' not in st.session_state:
        st.session_state.venue_type = "실내"

    venue_decided_options = ["예", "아니오"]
    venue_decided = render_option_menu("장소가 정확히 정해졌나요?", venue_decided_options, ['check-circle', 'x-circle'], venue_decided_options.index(st.session_state.venue_decided), 'horizontal', key="venue_decided_menu")
    if venue_decided != st.session_state.venue_decided:
        st.session_state.venue_decided = venue_decided
    
    venue_types = ["실내", "실외", "혼합", "온라인"]
    venue_type = render_option_menu("실내/실외", venue_types, ['house', 'tree', 'houses', 'laptop'], venue_types.index(st.session_state.venue_type), 'horizontal', key="venue_type_menu")
    if venue_type != st.session_state.venue_type:
        st.session_state.venue_type = venue_type

    capacity_type_options = ["인원 범위로 입력", "인원으로 입력"]
    default_capacity_type = st.session_state.get('capacity_type', capacity_type_options[0])
    default_index = capacity_type_options.index(default_capacity_type) if default_capacity_type in capacity_type_options else 0
    
    capacity_type = render_option_menu("참여 인원 입력 방식", capacity_type_options, ['bar-chart', '123'], 
                                       default_index, 
                                       'horizontal', key="capacity_type_menu")
    if capacity_type != st.session_state.get('capacity_type'):
        st.session_state.capacity_type = capacity_type

    if st.session_state.venue_decided == "예":
        st.session_state.venue_name = st.text_input("장소명", st.session_state.get('venue_name', ''), key="venue_name_input")

        if st.session_state.venue_type != "온라인":
            st.session_state.address = st.text_input("주소", st.session_state.get('address', ''), key="address_input")

        current_capacity = st.session_state.get('capacity', '0-0')
        if isinstance(current_capacity, int):
            current_min = current_max = current_capacity
        elif isinstance(current_capacity, str) and '-' in current_capacity:
            current_min, current_max = map(int, current_capacity.split('-'))
        else:
            current_min = current_max = 0

        if capacity_type == "인원 범위로 입력":
            min_capacity = st.number_input("최소 참여 인원", min_value=0, value=current_min, key="min_capacity_input")
            max_capacity = st.number_input("최대 참여 인원", min_value=min_capacity, value=max(current_max, min_capacity), key="max_capacity_input")
            st.session_state.capacity = f"{min_capacity}-{max_capacity}"
        else:
            st.session_state.capacity = st.number_input("참여 인원", min_value=0, value=current_min, key="capacity_input")

        if st.session_state.venue_type in ["실내", "혼합"]:
            facilities = ["없음", "무대", "음향 시스템", "조명 시스템", "빔 프로젝터", "LED", "Wi-Fi", "주차장", "기타"]
            selected_facilities = st.multiselect("행사장 보유 시설 및 장비", facilities, default=st.session_state.get('facilities', []), key="facilities_input")
            
            if "기타" in selected_facilities:
                other_facilities = st.text_input("기타 시설 및 장비를 입력해주세요", key="other_facilities_input")
                if other_facilities:
                    selected_facilities = [facility if facility != "기타" else f"기타: {other_facilities}" for facility in selected_facilities]
            
            st.session_state.facilities = selected_facilities
        else:
            st.session_state.facilities = []  # 실외인 경우 시설 정보를 비움
    else:
        st.session_state.desired_region = st.text_input("희망 지역", st.session_state.get('desired_region', ''), key="desired_region_input")
        st.session_state.desired_capacity = st.number_input("희망 참여 인원", min_value=0, value=int(st.session_state.get('desired_capacity', 0)), key="desired_capacity_input")

def service_components():
    st.header("용역 구성 요소")
    event_data = st.session_state.event_data

    if event_data.get('event_type') == "영상 제작":
        selected_categories = ["미디어"]
        st.write("영상 제작 프로젝트를 위해 '미디어' 카테고리가 자동으로 선택되었습니다.")
    elif event_data.get('venue_type') == "온라인":
        selected_categories = ["미디어"]
        st.write("온라인 이벤트를 위해 '미디어' 카테고리가 자동으로 선택되었습니다.")
    else:
        categories = list(item_options.keys())
        selected_categories = st.multiselect("카테고리 선택", categories, default=event_data.get('selected_categories', []))

    event_data['selected_categories'] = selected_categories

    event_data['components'] = event_data.get('components', {})
    for category in selected_categories:
        st.subheader(category)
        component = event_data['components'].get(category, {})

        status_options = ["발주처와 협상 진행 중", "확정", "거의 확정", "알 수 없는 상태"]
        component['status'] = st.radio(f"{category} 진행 상황", status_options, index=status_options.index(component.get('status', status_options[0])))

        component['items'] = st.multiselect(
            f"{category} 항목 선택",
            item_options.get(category, []),
            default=component.get('items', [])
        )

        for item in component['items']:
            if item in ["유튜브 (예능)", "유튜브 (교육 / 강의)", "유튜브 (인터뷰 형식)", 
                        "숏폼 (재편집)", "숏폼 (신규 제작)", "웹드라마", 
                        "2D / 모션그래픽 제작", "3D 영상 제작", "행사 배경 영상", 
                        "행사 사전 영상", "스케치 영상 제작", "애니메이션 제작"]:
                component[f'{item}_quantity'] = st.number_input(f"{item} 수량", min_value=0, value=component.get(f'{item}_quantity', 0))
                component[f'{item}_unit'] = "편"
            
            elif item in ["사진 (인물, 컨셉, 포스터 등)", "사진 (행사 스케치)"]:
                component[f'{item}_quantity'] = st.number_input(f"{item} 수량", min_value=0, value=component.get(f'{item}_quantity', 0))
                component[f'{item}_unit'] = "A컷 장수"
            
            elif item in ["중계 촬영 및 라이브 스트리밍", "중계 실시간 자막"]:
                component[f'{item}_quantity'] = st.number_input(f"{item} 수량", min_value=0, value=component.get(f'{item}_quantity', 0))
                component[f'{item}_unit'] = "회"
                component[f'{item}_camera_recording'] = st.checkbox("카메라별 녹화본 필요", key=f"{item}_camera_recording")
                component[f'{item}_td_recording'] = st.checkbox("TD 중계본 녹화 필요", key=f"{item}_td_recording")
            
            elif item == "중계 편집":
                component[f'{item}_quantity'] = st.number_input(f"{item} 수량", min_value=0, value=component.get(f'{item}_quantity', 0))
                component[f'{item}_unit'] = "편"
                component[f'{item}_edit_types'] = st.multiselect("편집 유형", ["통합본", "요약본", "하이라이트"], default=component.get(f'{item}_edit_types', []))
            
            elif item == "프로젝션 맵핑 / 미디어 파사드":
                component[f'{item}_quantity'] = st.number_input(f"{item} 회차", min_value=0, value=component.get(f'{item}_quantity', 0))
                component[f'{item}_unit'] = "회"
                component[f'{item}_start_date'] = st.date_input(f"{item} 전시 시작일", value=component.get(f'{item}_start_date', date.today()))
                component[f'{item}_end_date'] = st.date_input(f"{item} 전시 종료일", value=component.get(f'{item}_end_date', date.today()))
            
            elif item == "VR/AR 콘텐츠 제작":
                component[f'{item}_quantity'] = st.number_input(f"{item} 수량", min_value=0, value=component.get(f'{item}_quantity', 0))
                component[f'{item}_unit'] = "개"
                component[f'{item}_details'] = st.text_area(f"{item} 상세사항", value=component.get(f'{item}_details', ''), help="상세사항을 반드시 입력해주세요.")

            elif item == "행사전 미팅 스케줄링":
                component[f'{item}_quantity'] = st.number_input(f"{item} 수량", min_value=0, value=component.get(f'{item}_quantity', 0))
                component[f'{item}_unit'] = "회"
                component[f'{item}_details'] = st.text_area(f"{item} 상세사항", value=component.get(f'{item}_details', ''), help="미팅 목적, 참석자 등을 입력해주세요.")

            elif item == "행사전 참가자 매칭":
                component[f'{item}_quantity'] = st.number_input(f"{item} 수량", min_value=0, value=component.get(f'{item}_quantity', 0))
                component[f'{item}_unit'] = "명"
                component[f'{item}_details'] = st.text_area(f"{item} 상세사항", value=component.get(f'{item}_details', ''), help="매칭 기준, 방식 등을 입력해주세요.")

            else:
                component[f'{item}_quantity'] = st.number_input(f"{item} 수량", min_value=0, value=component.get(f'{item}_quantity', 0))
                component[f'{item}_unit'] = st.text_input(f"{item} 단위", value=component.get(f'{item}_unit', '개'))

            event_data['components'][category] = component

            # 선택되지 않은 카테고리 제거
            event_data['components'] = {k: v for k, v in event_data['components'].items() if k in selected_categories}

def budget_info():
    st.header("예산 정보")
    event_data = st.session_state.event_data

    event_data['contract_amount'] = st.number_input("총 계약 금액", min_value=0, value=event_data.get('contract_amount', 0))
    event_data['expected_profit'] = st.number_input("총 예상 수익", min_value=0, value=event_data.get('expected_profit', 0))

    st.subheader("카테고리별 예산")
    total_budget = 0
    for category, component in event_data.get('components', {}).items():
        st.write(f"**{category}**")
        component['budget'] = st.number_input(f"{category} 예산", min_value=0, value=component.get('budget', 0))
        total_budget += component['budget']

    st.write(f"**총 예산: {total_budget}**")

# 진행 상황 추적 함수
def progress_tracking():
    st.header("진행 상황")
    event_data = st.session_state.event_data

    if 'components' in event_data:
        for category, component in event_data['components'].items():
            st.subheader(category)
            st.write(f"진행 상황: {component['status']}")
            st.write(f"선택된 항목: {', '.join(component['items'])}")
            st.write("---")

# 데이터 저장 함수
def save_event_data(event_data):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        components_json = json.dumps(event_data.get('components', {}))
        
        # 날짜를 문자열로 변환
        start_date = event_data.get('start_date').isoformat() if event_data.get('start_date') else None
        end_date = event_data.get('end_date').isoformat() if event_data.get('end_date') else None
        
        cursor.execute('''INSERT OR REPLACE INTO events
                          (event_name, client_name, event_type, scale, start_date, end_date,
                           setup_start, teardown, venue_name, venue_type, address, capacity,
                           facilities, contract_amount, expected_profit, components)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (event_data.get('event_name'), event_data.get('client_name'),
                        json.dumps(event_data.get('event_type')), event_data.get('scale'),
                        start_date, end_date,
                        event_data.get('setup'), event_data.get('teardown'),
                        event_data.get('venue_name'), event_data.get('venue_type'),
                        event_data.get('address'), event_data.get('capacity'),
                        json.dumps(event_data.get('facilities')), event_data.get('contract_amount'),
                        event_data.get('expected_profit'), components_json))
        conn.commit()
        conn.close()
        st.success("데이터가 성공적으로 저장되었습니다.")
    else:
        st.error("데이터베이스 연결에 실패했습니다.")

# 엑셀 보고서 생성 함수
def generate_excel():
    event_data = st.session_state.event_data
    event_name = event_data.get('event_name', '무제')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 전체 행사 보고서 생성
    df_full = pd.DataFrame([event_data])
    if 'components' in df_full.columns:
        df_full['components'] = df_full['components'].apply(lambda x: json.dumps(x) if x else None)
    
    filename = f"이벤트_기획_{event_name}_{timestamp}.xlsx"
    
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df_full.to_excel(writer, sheet_name='전체 행사 보고서', index=False)
            
            # 각 용역 요소별 발주요청서 생성
            for category, component in event_data.get('components', {}).items():
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
                
                sheet_name = f'{category} 발주요청서'
                df_component.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # 추가 정보 기입
                workbook = writer.book
                worksheet = workbook[sheet_name]
                worksheet['A1'] = f"행사명: {event_name}"
                worksheet['A2'] = f"카테고리: {category}"
                worksheet['A3'] = f"진행 상황: {component.get('status', '')}"
                worksheet['A4'] = f"예산: {component.get('budget', 0)}원"
                worksheet.insert_rows(5)  # 빈 행 삽입
        
        st.success(f"엑셀 보고서가 생성되었습니다: {filename}")
        
        with open(filename, "rb") as file:
            st.download_button(
                label="엑셀 보고서 다운로드",
                data=file,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"엑셀 파일 생성 중 오류가 발생했습니다: {str(e)}")

    if st.button("엑셀 보고서 생성"):
        generate_excel()

def summary():
    st.header("요약")
    event_data = st.session_state.event_data

    st.subheader("기본 정보")
    st.write(f"행사명: {event_data.get('event_name', '')}")
    st.write(f"고객사: {event_data.get('client_name', '')}")
    st.write(f"행사 유형: {event_data.get('event_type', '')}")
    st.write(f"규모: {event_data.get('scale', '')}명")
    st.write(f"시작일: {event_data.get('start_date', '')}")
    st.write(f"종료일: {event_data.get('end_date', '')}")
    st.write(f"셋업 시작: {event_data.get('setup_start', '')}")
    st.write(f"철수: {event_data.get('teardown', '')}")

    st.subheader("장소 정보")
    st.write(f"장소명: {event_data.get('venue_name', '')}")
    st.write(f"장소 유형: {event_data.get('venue_type', '')}")
    st.write(f"주소: {event_data.get('address', '')}")
    st.write(f"수용 인원: {event_data.get('capacity', '')}")
    st.write(f"시설: {', '.join(event_data.get('facilities', []))}")

    st.subheader("용역 구성 요소")
    for category, component in event_data.get('components', {}).items():
        st.write(f"**{category}**")
        st.write(f"진행 상황: {component.get('status', '')}")
        st.write(f"선택된 항목: {', '.join(component.get('items', []))}")
        for item in component.get('items', []):
            st.write(f"- {item}: {component.get(f'{item}_quantity', 0)} {component.get(f'{item}_unit', '개')}")

    st.subheader("예산 정보")
    st.write(f"총 계약 금액: {event_data.get('contract_amount', 0)}원")
    st.write(f"총 예상 수익: {event_data.get('expected_profit', 0)}원")

    st.subheader("카테고리별 예산")
    total_budget = 0
    for category, component in event_data.get('components', {}).items():
        budget = component.get('budget', 0)
        st.write(f"{category}: {budget}원")
        total_budget += budget
    st.write(f"**총 예산: {total_budget}원**")

    if st.button("저장"):
        save_event_data(event_data)
        st.success("이벤트 정보가 저장되었습니다.")


def main():
    st.set_page_config(page_title="이벤트 플래너", page_icon="🎉", layout="wide")
    st.title("이벤트 플래너")

    init_app()

    steps = ["기본 정보", "장소 정보", "용역 구성 요소", "예산 정보", "요약"]
    functions = [basic_info, venue_info, service_components, budget_info, summary]

    st.sidebar.title("단계")
    for i, step in enumerate(steps):
        if st.sidebar.button(step, key=f"step_{i}"):
            st.session_state.step = i

    functions[st.session_state.step]()

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.step > 0:
            if st.button("이전"):
                st.session_state.step -= 1
                st.experimental_rerun()

    with col2:
        if st.session_state.step < len(steps) - 1:
            if st.button("다음"):
                st.session_state.step += 1
                st.experimental_rerun()

if __name__ == "__main__":
    main()