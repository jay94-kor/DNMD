import streamlit as st
import sqlite3
import json
from datetime import date

# 데이터베이스 초기화 및 관리
def init_db():
    conn = sqlite3.connect('event_planner.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS event_data
                 (key TEXT PRIMARY KEY, value TEXT)''')
    conn.commit()
    conn.close()

def save_data(data):
    conn = sqlite3.connect('event_planner.db')
    c = conn.cursor()
    for key, value in data.items():
        if isinstance(value, (list, dict, date)):
            value = json.dumps(value)
        c.execute("INSERT OR REPLACE INTO event_data (key, value) VALUES (?, ?)",
                  (key, value))
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect('event_planner.db')
    c = conn.cursor()
    c.execute("SELECT key, value FROM event_data")
    result = {}
    for key, value in c.fetchall():
        try:
            result[key] = json.loads(value)
        except json.JSONDecodeError:
            result[key] = value
    conn.close()
    return result

# 유틸리티 함수
def format_date(date_string):
    date_obj = date.fromisoformat(date_string)
    return date_obj.strftime("%Y년 %m월 %d일")

def validate_date_range(start_date, end_date):
    return start_date <= end_date

# 페이지 렌더링 함수들
def render_basic_info(data):
    st.header("기본 정보")
    
    event_name = st.text_input("행사명", value=data.get('event_name', ''))
    client_name = st.text_input("클라이언트명", value=data.get('client_name', ''))
    
    event_types = ['컨퍼런스', '세미나', '워크샵', '기타']
    event_type = st.multiselect("행사 유형", options=event_types, default=data.get('event_type', []))
    
    scale = st.number_input("예상 참여 관객 수", min_value=0, value=int(data.get('scale', 0)))
    
    default_date = date.today()
    start_date = st.date_input("행사 시작일", value=date.fromisoformat(data.get('start_date', default_date.isoformat())))
    end_date = st.date_input("행사 종료일", value=date.fromisoformat(data.get('end_date', default_date.isoformat())))
    
    if not validate_date_range(start_date, end_date):
        st.error("종료일은 시작일과 같거나 이후여야 합니다.")
    
    setup = st.radio("셋업 시작", ["전날부터", "당일"], index=0 if data.get('setup') == "전날부터" else 1)
    teardown = st.radio("철수", ["당일 철수", "다음날 철수"], index=0 if data.get('teardown') == "당일 철수" else 1)

    if st.button("저장"):
        updated_data = {
            'event_name': event_name,
            'client_name': client_name,
            'event_type': event_type,
            'scale': scale,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'setup': setup,
            'teardown': teardown
        }
        save_data(updated_data)
        st.success("기본 정보가 저장되었습니다.")

    st.write("## 행사 정보 요약")
    st.write(f"행사명: {event_name}")
    st.write(f"클라이언트: {client_name}")
    st.write(f"행사 유형: {', '.join(event_type)}")
    st.write(f"예상 참여 관객 수: {scale}명")
    st.write(f"행사 기간: {format_date(start_date.isoformat())} - {format_date(end_date.isoformat())}")
    st.write(f"셋업: {setup}")
    st.write(f"철수: {teardown}")

def render_venue_info(data):
    st.header("장소 정보")
    st.write("장소 정보 페이지 내용을 여기에 구현하세요.")

def render_budget_info(data):
    st.header("예산 정보")
    st.write("예산 정보 페이지 내용을 여기에 구현하세요.")

def render_service_components(data):
    st.header("용역 구성 요소")
    st.write("용역 구성 요소 페이지 내용을 여기에 구현하세요.")

def render_progress_tracking(data):
    st.header("진행 상황")
    st.write("진행 상황 페이지 내용을 여기에 구현하세요.")

# 메인 애플리케이션
def main():
    st.set_page_config(page_title="이벤트 기획 도구", layout="wide")
    st.title("이벤트 기획 도구")

    # 데이터베이스 초기화
    init_db()

    # 데이터 로드
    data = load_data()

    # 사이드바 네비게이션
    pages = {
        "기본 정보": render_basic_info,
        "장소 정보": render_venue_info,
        "예산 정보": render_budget_info,
        "용역 구성 요소": render_service_components,
        "진행 상황": render_progress_tracking
    }
    
    selection = st.sidebar.radio("페이지 선택", list(pages.keys()))

    # 선택된 페이지 렌더링
    pages[selection](data)

    # 푸터
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2023 이벤트 기획 도구")

if __name__ == "__main__":
    main()