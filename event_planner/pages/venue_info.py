import streamlit as st
from streamlit_pills import pills
from database import save_data, load_data
from utils import load_config

def render():
    st.header("장소 정보")
    
    config = load_config()
    data = load_data()

    venue_decided = st.radio("장소가 정확히 정해졌나요?", ["예", "아니오"], index=0 if data.get('venue_decided', True) else 1)

    if venue_decided == "예":
        venue_name = st.text_input("장소의 정확한 명칭 (예: 서울시청 다목적홀B)", value=data.get('venue_name', ''))
        venue_type = pills("장소 유형", config['venue_types'])
        address = st.text_input("주소", value=data.get('address', ''))
        capacity = st.number_input("수용 인원", min_value=0, value=data.get('capacity', 0))
        
        facilities = pills("시설 및 장비 정보", [{"label": facility, "value": facility} for facility in config['facilities']], multiselect=True)
        
        other_facilities = st.text_input("기타 시설 및 장비 (쉼표로 구분)")
        if other_facilities:
            facilities.extend([f.strip() for f in other_facilities.split(',')])

        st.info("입력한 장소 정보는 데이터베이스에 저장되며, 향후 다른 이벤트에서도 참조할 수 있습니다.")

    else:
        desired_region = st.text_input("희망 지역", value=data.get('desired_region', ''))
        desired_capacity = st.number_input("희망 수용 인원", min_value=0, value=data.get('desired_capacity', 0))
        capacity_flexible = st.checkbox("수용 인원 무관")

        if capacity_flexible:
            desired_capacity = "무관"

        venue_name = ""
        venue_type = ""
        address = ""
        capacity = 0
        facilities = []

    if st.button("저장"):
        save_data({
            'venue_decided': venue_decided == "예",
            'venue_name': venue_name,
            'venue_type': venue_type,
            'address': address,
            'capacity': capacity,
            'facilities': facilities,
            'desired_region': desired_region,
            'desired_capacity': desired_capacity
        })
        st.success("장소 정보가 저장되었습니다.")

    # 저장된 장소 정보 표시
    st.subheader("저장된 장소 정보")
    if venue_decided == "예":
        st.write(f"장소명: {venue_name}")
        st.write(f"장소 유형: {venue_type}")
        st.write(f"주소: {address}")
        st.write(f"수용 인원: {capacity}명")
        st.write(f"시설 및 장비: {', '.join(facilities)}")
    else:
        st.write(f"희망 지역: {desired_region}")
        st.write(f"희망 수용 인원: {desired_capacity}")

    # 데이터베이스에 저장된 다른 장소 정보 표시
    st.subheader("데이터베이스에 저장된 다른 장소 정보")
    # 여기에 데이터베이스에서 다른 장소 정보를 불러와 표시하는 코드를 추가할 수 있습니다.
    # 예를 들어, 테이블 형태로 장소명, 주소, 수용 인원 등을 보여줄 수 있습니다.
    # 이 기능은 데이터베이스 구조와 저장 방식에 따라 구현 방법이 달라질 수 있습니다.