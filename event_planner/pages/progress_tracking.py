import streamlit as st
from database import load_data
from utils import load_config, format_currency

def render():
    st.header("진행 상황")
    
    config = load_config()
    data = load_data()

    if 'service_components' not in data or not data['service_components']:
        st.warning("아직 선택된 용역 구성 요소가 없습니다. '용역 구성 요소' 페이지에서 요소를 추가해주세요.")
        return

    for component in data['service_components']:
        st.subheader(f"{component['category']} - {component['subcategory']}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"상태: {component['status']}")
        
        with col2:
            st.write(f"예산: {format_currency(component['budget'])}")
        
        with col3:
            st.write(f"협력사 컨택 상태: {component['contact_status']}")
        
        st.write(f"추가 정보: {component['additional_info']}")
        
        # 여기에 진행 상황을 업데이트할 수 있는 UI 요소를 추가할 수 있습니다.
        # 예를 들어, 상태를 변경하는 선택 상자나 메모를 추가하는 텍스트 영역 등을 넣을 수 있습니다.
        
        st.write("---")

    if st.button("전체 진행 상황 저장"):
        # 여기에 진행 상황을 저장하는 로직을 추가할 수 있습니다.
        st.success("진행 상황이 저장되었습니다.")