import streamlit as st
from streamlit_option_menu import option_menu
from datetime import date, timedelta
import sqlite3
import json
import pandas as pd
import openpyxl

DATABASE = 'database.db'

# 데이터베이스 연결 함수
def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        st.error(f"Database connection error: {e}")
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

    event_data['event_name'] = st.text_input("행사명", value=event_data.get('event_name', ''), key="event_name")
    event_data['client_name'] = st.text_input("클라이언트명", value=event_data.get('client_name', ''), key="client_name")

    event_types = ["영상 제작", "오프라인 이벤트"]
    default_index = event_types.index(event_data.get('event_type', event_types[0]))
    event_data['event_type'] = render_option_menu("용역 유형", event_types, ['camera-video', 'calendar-event'], default_index, orientation='horizontal', key="event_type")

    if event_data['event_type'] == "영상 제작":
        production_types = ["연간 제작건", "단건", "시리즈 물"]
        selected_production_type = st.radio("제작 유형 선택", production_types, index=production_types.index(event_data.get('production_type', production_types[0])), key="production_type")
        event_data['production_type'] = selected_production_type

        if selected_production_type == "연간 제작건":
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
            
            # 과업 기간 계산
            duration = (end_date - start_date).days
            months = duration // 30
            days = duration % 30
            st.write(f"과업 기간: {months}개월 {days}일")

        # 제작 분류 선택 부분
        categories = ["숏폼", "교육영상", "강의영상", "현장 스케치", "유튜브", "다큐멘터리", "광고", "기타"]
        selected_categories = st.multiselect("제작 분류 선택", categories, default=event_data.get('selected_categories', []), key="selected_categories")
        event_data['selected_categories'] = selected_categories

        for i, category in enumerate(selected_categories):
            count = st.number_input(f"{category} 제작 건수", min_value=0, value=event_data.get(f'{category}_count', 0), key=f"category_count_{i}")
            event_data[f'{category}_count'] = count
            st.write(f"{category}: {count}편")

    elif selected_production_type in ["단건", "시리즈 물"]:
        num_videos = st.number_input(f"{selected_production_type} 제작 편수", min_value=1, value=event_data.get('num_videos', 1))
        event_data['num_videos'] = num_videos

        output_schedule = st.date_input("예상 아웃풋 일정", value=event_data.get('output_schedule', date.today()))
        event_data['output_schedule'] = output_schedule

        categories = ["숏폼", "교육영상", "강의영상", "현장 스케치", "유튜브", "다큐멘터리", "광고", "기타"]
        selected_categories = st.multiselect("제작 분류 선택", categories, default=event_data.get('selected_categories', []))
        event_data['selected_categories'] = selected_categories

        for category in selected_categories:
            event_data[f'{category}_count'] = st.number_input(f"{category} 제작 건수", min_value=0, value=event_data.get(f'{category}_count', 0))

    if event_data['event_type'] == "오프라인 이벤트":
        event_data['scale'] = st.number_input("예상 참여 관객 수", min_value=0, value=event_data.get('scale', 0))
        
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

    venue_decided_options = ["예", "아니오"]
    default_venue_decided = venue_decided_options.index(event_data.get('venue_decided', "아니오"))
    event_data['venue_decided'] = render_option_menu("장소가 정확히 정해졌나요?", venue_decided_options, ['check-circle', 'x-circle'], default_venue_decided, 'horizontal')
    
    if event_data['venue_decided'] == "예":
        event_data['venue_name'] = st.text_input("장소명", event_data.get('venue_name', ''))
        venue_types = ["실내", "실외", "혼합", "온라인"]
        default_venue_type = venue_types.index(event_data.get('venue_type', "실내"))
        event_data['venue_type'] = render_option_menu("실내/실외", venue_types, ['house', 'tree', 'houses', 'laptop'], default_venue_type, 'horizontal')

        if event_data['venue_type'] != "온라인":
            event_data['address'] = st.text_input("주소", event_data.get('address', ''))

        capacity_type_options = ["범위", "단일 값"]
        default_capacity_type = capacity_type_options.index(event_data.get('capacity_type', "범위"))
        capacity_type = render_option_menu("수용 인원 입력 방식", capacity_type_options, ['bar-chart', '123'], default_capacity_type, 'horizontal')

        current_capacity = event_data.get('capacity', '0-0')
        if isinstance(current_capacity, int):
            current_min = current_max = current_capacity
        elif isinstance(current_capacity, str) and '-' in current_capacity:
            current_min, current_max = map(int, current_capacity.split('-'))
        else:
            current_min = current_max = 0

        if capacity_type == "범위":
            min_capacity = st.number_input("최소 수용 인원", min_value=0, value=current_min)
            max_capacity = st.number_input("최대 수용 인원", min_value=0, value=current_max)
            event_data['capacity'] = f"{min_capacity}-{max_capacity}"
        else:
            event_data['capacity'] = st.number_input("수용 인원", min_value=0, value=current_min)

        facilities = ["무대", "음향 시스템", "조명 시스템", "프로젝터", "스크린", "Wi-Fi", "주차장", "기타"]
        event_data['facilities'] = st.multiselect("시설 및 장비", facilities, default=event_data.get('facilities', []))
    else:
        event_data['desired_region'] = st.text_input("희망 지역", event_data.get('desired_region', ''))
        event_data['desired_capacity'] = st.number_input("희망 수용 인원", min_value=0, value=int(event_data.get('desired_capacity', 0)))

def service_components():
    st.header("용역 구성 요소")
    event_data = st.session_state.event_data

    categories = [
        "기술 및 혁신", "네트워킹", "디자인", "마케팅 및 홍보", "미디어", "부대 행사",
        "섭외 / 인력", "시스템", "F&B", "제작 / 렌탈", "청소 / 관리", "출입 통제", "하드웨어"
    ]

    selected_categories = st.multiselect("카테고리 선택", categories, default=event_data.get('selected_categories', []))
    event_data['selected_categories'] = selected_categories

    event_data['components'] = event_data.get('components', {})
    for category in selected_categories:
        st.subheader(category)
        component = event_data['components'].get(category, {})

        status_options = ["발주처와 협상 진행 중", "확정", "거의 확정", "알 수 없는 상태"]
        component['status'] = st.radio(f"{category} 진행 상황", status_options, index=status_options.index(component.get('status', status_options[0])))

        item_options = {
            "기술 및 혁신": ["홍보용 앱 개발", "홍보용 홈페이지 개발"],
            "네트워킹": ["행사전 미팅 스케줄링", "행사전 참가자 매칭"],
            "디자인": ["로고", "캐릭터", "2D", "3D"],
            "마케팅 및 홍보": ["오프라인 (옥외 매체)", "오프라인 (지하철, 버스, 택시)", "온라인 (뉴스레터)", "온라인 (인플루언서)", "온라인 (키워드)", "온라인 (SNS / 바이럴)", "온라인 (SNS / 유튜브 비용집행)", "PR (기자회견 / 기자 컨택)", "PR (매체 광고)", "PR (보도자료 작성 및 배포)"],
            "미디어": ["2D/모션그래픽 제작", "3D 영상 제작", "드론 렌탈 및 운영", "배경 영상 제작", "사전 영상 제작", "사진 (인물, 컨셉, 포스터 등)", "사진 (행사 스케치)", "스케치 영상 제작", "애니메이션 제작", "중계 라이브 스트리밍", "중계 실시간 자막", "중계 촬영 / 편집", "프로젝션 맵핑 / 미디어 파사드", "VR/AR 콘텐츠 제작"],
            "부대 행사": ["놀이 시설", "레크레이션", "자판기 (아이템 / 굿즈 등)", "자판기 (음료 / 스낵 / 솜사탕 등)", "체험 부스 (게임존)", "체험 부스 (과학 실험)", "체험 부스 (로봇 체험)", "체험 부스 (심리상담)", "체험 부스 (진로상담)", "체험 부스 (퍼스널 컬러)", "체험 부스 (VR/AR)", "키오스크"],
            "섭외 / 인력": ["가수", "강사", "경호 (행사 전반)", "경호 (VIP)", "공연팀 (댄스)", "공연팀 (서커스 / 마술 / 퍼포먼스)", "공연팀 (음악)", "공연팀 (전통)", "배우", "번역", "연사", "요원 (소방안전)", "요원 (응급처치)", "의전 도우미", "인플루언서", "코미디언", "통역 인력 및 장비 세팅", "패널 토론 진행자", "MC (기념식 / 시상식 등)", "MC (축제 / 페스티벌 등)", "STAFF (안전관리)", "STAFF (행사 운영)", "STAFF (행사 진행)"],
            "시스템": ["음향 설치 및 운영", "음향 오퍼레이터", "조명 (공연)", "조명 (스피치 및 일반)", "LED 디스플레이 설치 및 운영"],
            "F&B": ["음료 바 설치", "커피차 대여 및 운영", "푸드 트럭 대여 및 운영", "푸드 트럭 섭외 및 공고", "케이터링 (뷔페)", "케이터링 (도시락)", "케이터링 (스탠딩)", "케이터링 (코스)"],
            "제작 / 렌탈": ["가구 렌탈", "무대 설치", "부스 설치", "시스템 트러스", "천막 설치", "특수효과 (불꽃, 연기 등)"],
            "청소 / 관리": ["폐기물 처리", "화장실 관리"],
            "출입 통제": ["QR코드 체크인", "명찰 제작", "출입증 제작"],
            "하드웨어": ["노트북 렌탈", "태블릿 렌탈", "프린터 렌탈"]
        }

        component['items'] = st.multiselect(f"{category} 항목 선택", item_options.get(category, []), default=component.get('items', []))

        for item in component['items']:
            if item == "행사전 미팅 스케줄링":
                col1, col2 = st.columns(2)
                with col1:
                    component[f'{item}_quantity'] = st.number_input(f"{item} 오픈 희망 일정", min_value=1, value=component.get(f'{item}_quantity', 1))
                with col2:
                    component[f'{item}_unit'] = st.selectbox(
                        f"{item} 단위",
                        options=["주", "일", "월"],
                        index=["주", "일", "월"].index(component.get(f'{item}_unit', "주"))
                    )
                st.write(f"{item} 오픈 희망 일정: 행사 {component[f'{item}_quantity']} {component[f'{item}_unit']} 전")
            else:
                component[f'{item}_quantity'] = st.number_input(f"{item} 수량", min_value=0, value=component.get(f'{item}_quantity', 0))
                component[f'{item}_unit'] = st.text_input(f"{item} 단위", value=component.get(f'{item}_unit', '개'))

        event_data['components'][category] = component

    # 선택되지 않은 카테고리 제거
    event_data['components'] = {k: v for k, v in event_data['components'].items() if k in selected_categories}



def budget_info():
    st.header("예산 정보")
    event_data = st.session_state.event_data

    event_data['contract_amount'] = st.number_input("계약 금액 (원)", min_value=0, value=event_data.get('contract_amount', 0))
    profit_percent = st.number_input("예상 영업이익 (%)", min_value=0.0, max_value=100.0, value=event_data.get('profit_percent', 0.0))
    event_data['profit_percent'] = profit_percent
    
    expected_profit = int(event_data['contract_amount'] * (profit_percent / 100))
    event_data['expected_profit'] = expected_profit

    st.write(f"예상 영업이익: {expected_profit:,} 원")

    if st.checkbox("예상 영업이익 수정"):
        custom_profit = st.number_input("예상 영업이익 (원)", min_value=0, value=expected_profit)
        if st.button("수정 적용"):
            event_data['expected_profit'] = custom_profit
            if event_data['contract_amount'] > 0:
                event_data['profit_percent'] = (custom_profit / event_data['contract_amount']) * 100
            else:
                event_data['profit_percent'] = 0
            st.write(f"수정된 예상 영업이익 비율: {event_data['profit_percent']:.2f}%")
            st.experimental_rerun()

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
def save_data():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        event_data = st.session_state.event_data
        components_json = json.dumps(event_data.get('components', {}))
        cursor.execute('''INSERT OR REPLACE INTO events
                          (event_name, client_name, event_type, scale, start_date, end_date,
                           setup_start, teardown, venue_name, venue_type, address, capacity,
                           facilities, contract_amount, expected_profit, components)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (event_data.get('event_name'), event_data.get('client_name'),
                        json.dumps(event_data.get('event_type')), event_data.get('scale'),
                        event_data.get('start_date'), event_data.get('end_date'),
                        event_data.get('setup'), event_data.get('teardown'),
                        event_data.get('venue_name'), event_data.get('venue_type'),
                        event_data.get('address'), event_data.get('capacity'),
                        json.dumps(event_data.get('facilities')), event_data.get('contract_amount'),
                        event_data.get('expected_profit'), components_json))
        conn.commit()
        conn.close()
        st.success("데이터가 성공적으로 저장되었습니다.")

# 엑셀 보고서 생성 함수
def generate_excel():
    event_data = st.session_state.event_data
    df_full = pd.DataFrame([event_data])
    
    # 'components' 열이 존재하는지 확인하고, 존재하면 JSON으로 변환
    if 'components' in df_full.columns:
        df_full['components'] = df_full['components'].apply(lambda x: json.dumps(x) if x else None)

    df_partial = pd.DataFrame(columns=['카테고리', '진행 상황', '선택된 항목', '세부사항'])
    for category, component in event_data.get('components', {}).items():
        df_partial = df_partial.append({
            '카테고리': category,
            '진행 상황': component['status'],
            '선택된 항목': ', '.join(component['items']),
            '세부사항': ', '.join([f"{item}: {component.get(f'{item}_quantity', '')} {component.get(f'{item}_unit', '')}" for item in component['items']])
        }, ignore_index=True)

    filename = f"이벤트_기획_{event_data['event_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    with pd.ExcelWriter(filename) as writer:
        df_full.to_excel(writer, sheet_name='전체 행사 보고서', index=False)
        df_partial.to_excel(writer, sheet_name='부분 발주요청서', index=False)

    st.success(f"엑셀 보고서가 생성되었습니다: {filename}")
    with open(filename, "rb") as file:
        st.download_button(
            label="엑셀 보고서 다운로드",
            data=file,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def main():
    init_app()
    st.title("이벤트 플래너")

    functions = [basic_info, venue_info, budget_info, service_components]
    functions[st.session_state.step]()

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.session_state.step > 0:
            if st.button("이전", key='prev'):
                st.session_state.step -= 1
                st.experimental_rerun()
    with col3:
        if st.session_state.step < len(functions) - 1:
            if st.button("다음", key='next'):
                st.session_state.step += 1
                st.experimental_rerun()
        else:
            if st.button("완료", key='complete'):
                st.success("이벤트 계획이 완료되었습니다!")
                save_data()
                progress_tracking()
                generate_excel()

if __name__ == "__main__":
    main()
