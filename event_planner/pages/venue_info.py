import streamlit as st
from streamlit_pills import pills
from utils import load_config
from database import save_data, load_data

def render():
    st.header("장소 정보")
    
    config = load_config()
    data = load_data()

    venue_name = st.text_input("장소명", value=data.get('venue_name', ''))
    venue_address = st.text_input("주소", value=data.get('venue_address', ''))
    
    # pills 함수 사용 방식 변경
    facility_options = [{"label": facility, "value": facility} for facility in config['facilities']]
    selected_facilities = pills("시설 및 장비 정보", options=facility_options, multiselect=True)

    indoor_outdoor = st.radio("실내/실외", ["실내", "실외", "혼합"], index=["실내", "실외", "혼합"].index(data.get('indoor_outdoor', '실내')))
    
    col1, col2 = st.columns(2)
    with col1:
        area = st.number_input("면적 (m²)", min_value=0, value=data.get('area', 0))
    with col2:
        capacity = st.number_input("수용 인원", min_value=0, value=data.get('capacity', 0))

    parking = st.number_input("주차 가능 대수", min_value=0, value=data.get('parking', 0))
    
    # 선택된 시설들을 리스트로 변환
    facilities = [option["value"] for option in selected_facilities]

    if st.button("저장"):
        save_data({
            'venue_name': venue_name,
            'venue_address': venue_address,
            'facilities': facilities,  # 리스트로 저장
            'indoor_outdoor': indoor_outdoor,
            'area': area,
            'capacity': capacity,
            'parking': parking
        })
        st.success("장소 정보가 저장되었습니다.")