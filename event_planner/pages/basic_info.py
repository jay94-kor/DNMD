import streamlit as st
from datetime import date
from utils import format_date, validate_date_range

def render(data, config):
    st.header("기본 정보")
    
    event_name = st.text_input("행사명", value=data.get('event_name', ''))
    client_name = st.text_input("클라이언트명", value=data.get('client_name', ''))
    
    event_types = config.get('event_types', [])
    event_type = st.multiselect("행사 유형", options=event_types, default=data.get('event_type', []))
    
    scale = st.number_input("예상 참여 관객 수", min_value=0, value=int(data.get('scale', 0)))
    
    start_date = st.date_input("행사 시작일", value=date.fromisoformat(data.get('start_date', date.today().isoformat())))
    end_date = st.date_input("행사 종료일", value=date.fromisoformat(data.get('end_date', date.today().isoformat())))
    
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
        return updated_data

    st.write("## 행사 정보 요약")
    st.write(f"행사명: {event_name}")
    st.write(f"클라이언트: {client_name}")
    st.write(f"행사 유형: {', '.join(event_type)}")
    st.write(f"예상 참여 관객 수: {scale}명")
    st.write(f"행사 기간: {format_date(start_date.isoformat())} - {format_date(end_date.isoformat())}")
    st.write(f"셋업: {setup}")
    st.write(f"철수: {teardown}")

    return None