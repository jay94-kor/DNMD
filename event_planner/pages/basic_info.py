import streamlit as st
from datetime import date
from utils import load_config
from database import save_data, load_data

def render():
    st.header("기본 정보")
    
    config = load_config()
    data = load_data()

    event_name = st.text_input("행사명", value=data.get('event_name', ''))
    client_name = st.text_input("클라이언트명", value=data.get('client_name', ''))
    
    # event_type을 multiselect로 변경하고 안전하게 처리
    event_types = config.get('event_types', [])
    if not isinstance(event_types, list):
        event_types = []
    event_type = st.multiselect("행사 유형", options=event_types, default=data.get('event_type', []))
    
    scale = st.number_input("예상 참여 관객 수", min_value=0, value=int(data.get('scale', 0)))
    
    # 날짜 입력을 안전하게 처리
    default_date = date.today()
    start_date = st.date_input("행사 시작일", value=date.fromisoformat(data.get('start_date', default_date.isoformat())))
    end_date = st.date_input("행사 종료일", value=date.fromisoformat(data.get('end_date', default_date.isoformat())))
    
    setup = st.radio("셋업 시작", ["전날부터", "당일"], index=0 if data.get('setup') == "전날부터" else 1)
    teardown = st.radio("철수", ["당일 철수", "다음날 철수"], index=0 if data.get('teardown') == "당일 철수" else 1)

    if st.button("저장"):
        save_data({
            'event_name': event_name,
            'client_name': client_name,
            'event_type': event_type,
            'scale': scale,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'setup': setup,
            'teardown': teardown
        })
        st.success("기본 정보가 저장되었습니다.")

    return {
        "event_name": event_name,
        "client_name": client_name,
        "event_type": event_type,
        "scale": scale,
        "start_date": start_date,
        "end_date": end_date,
        "setup": setup,
        "teardown": teardown
    }