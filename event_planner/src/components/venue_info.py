import streamlit as st
from datetime import datetime, timedelta
from utils import render_option_menu

def handle_unknown_venue_status(event_data):
    event_data['desired_region'] = st.selectbox("희망하는 지역", ["서울", "경기", "인천", "부산", "대구", "광주", "대전", "울산", "세종", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"])
    event_data['desired_capacity'] = st.number_input("희망하는 수용 인원", min_value=0, value=int(event_data.get('desired_capacity', 0)))

def handle_known_venue_status(event_data):
    if 'venues' not in event_data:
        event_data['venues'] = [{'name': '', 'address': ''}]

    for i, venue in enumerate(event_data['venues']):
        st.subheader(f"장소 {i+1}")
        venue['name'] = st.text_input(f"장소명 {i+1}", value=venue.get('name', ''), key=f"venue_name_{i}")
        venue['address'] = st.text_input(f"주소 {i+1}", value=venue.get('address', ''), key=f"venue_address_{i}")

    if st.button("장소 추가"):
        event_data['venues'].append({'name': '', 'address': ''})
        st.rerun()

def update_venue_status(value):
    st.session_state.event_data['venue_status'] = value

def venue_info():
    st.header("행사장 정보")

    event_data = st.session_state.event_data

    if 'venue_status' not in event_data:
        event_data['venue_status'] = "알 수 없는 상태"

    event_data['venue_status'] = render_option_menu(
        "장소 확정 상태",
        ["확정", "미확정", "알 수 없는 상태"],
        "venue_status",
        on_change=update_venue_status
    )

    if event_data['venue_status'] == "알 수 없는 상태":
        handle_unknown_venue_status(event_data)
    else:
        handle_known_venue_status(event_data)

    venue_name = st.text_input("행사장 이름", key="venue_name")
    venue_address = st.text_input("행사장 주소", key="venue_address")

    col1, col2 = st.columns(2)
    with col1:
        event_date = st.date_input("행사 날짜", key="event_date")
    with col2:
        event_time = st.time_input("행사 시작 시간", key="event_time")

    event_datetime = datetime.combine(event_date, event_time)

    setup_option = st.radio(
        "셋업 옵션",
        ["전날 셋업", "당일 셋업"],
        key="setup_option"
    )

    if setup_option == "전날 셋업":
        setup_date = event_date - timedelta(days=1)
        st.write(f"셋업 날짜: {setup_date}")
    else:
        st.write("셋업 날짜: 행사 당일")

    teardown_option = st.radio(
        "철수 옵션",
        ["당일 철수", "다음날 철수"],
        key="teardown_option"
    )

    if teardown_option == "다음날 철수":
        teardown_date = event_date + timedelta(days=1)
        st.write(f"철수 날짜: {teardown_date}")
    else:
        st.write("철수 날짜: 행사 당일")

    venue_note = st.text_area("행사장 관련 특이사항", key="venue_note")

    # 행사장 정보를 session_state에 저장
    st.session_state.event_data.update({
        "venue_name": venue_name,
        "venue_address": venue_address,
        "event_datetime": event_datetime,
        "setup_option": setup_option,
        "teardown_option": teardown_option,
        "venue_note": venue_note
    })