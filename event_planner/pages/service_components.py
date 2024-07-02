import streamlit as st
from streamlit_pills import pills
from database import save_data, load_data
from utils import load_config, format_currency

def render():
    st.header("용역 구성 요소")
    
    config = load_config()
    data = load_data()

    selected_categories = pills("카테고리 선택", [cat['name'] for cat in config['service_categories']], multiselect=True)

    if not selected_categories:
        st.warning("카테고리를 선택해주세요.")
        return

    components = data.get('service_components', [])

    for category in selected_categories:
        st.subheader(category)
        category_data = next(cat for cat in config['service_categories'] if cat['name'] == category)
        
        selected_subcategories = pills("세부 항목 선택", category_data['subcategories'], multiselect=True)

        for subcategory in selected_subcategories:
            with st.expander(subcategory):
                status = st.selectbox("진행 상황", config['progress_statuses'], key=f"{category}_{subcategory}_status")
                budget = st.number_input("예산", min_value=0, value=0, step=10000, key=f"{category}_{subcategory}_budget")
                contact_status = st.selectbox("협력사 컨택 상태", config['contact_statuses'], key=f"{category}_{subcategory}_contact")
                additional_info = st.text_area("추가 세부사항", key=f"{category}_{subcategory}_info")

                component = {
                    'category': category,
                    'subcategory': subcategory,
                    'status': status,
                    'budget': budget,
                    'contact_status': contact_status,
                    'additional_info': additional_info
                }

                if st.button("저장", key=f"{category}_{subcategory}_save"):
                    components = [c for c in components if not (c['category'] == category and c['subcategory'] == subcategory)]
                    components.append(component)
                    save_data({'service_components': components})
                    st.success(f"{subcategory} 정보가 저장되었습니다.")

    if st.button("전체 용역 구성 요소 저장"):
        save_data({'service_components': components})
        st.success("모든 용역 구성 요소가 저장되었습니다.")