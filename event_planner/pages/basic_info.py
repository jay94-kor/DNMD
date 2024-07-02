import streamlit as st
from streamlit_pills import pills
from datetime import date
from database import save_data, load_data
from utils import load_config

def render():
    st.header("기본 정보")
    
    config = load_config()
    data = load_data()

    col1, col2 = st.columns(2)

    with col1:
        event_name = st.text_input("행사명", value=data.get('event_name', ''))
        client_name = st.text_input("클라이언트명", value=data.get('client_name', ''))
        event_type = pills("행사 유형", config['event_types'], multiselect=True)

    with col2:
        scale = st.number_input("예상 참여 관객 수", min_value=0, value=data.get('scale', 0))
        start_date = st.date_input("행사 시작일", value=date.fromisoformat(data.get('start_date', date.today().isoformat())))
        end_date = st.date_input("행사 종료일", value=date.fromisoformat(data.get('end_date', date.today().isoformat())))

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