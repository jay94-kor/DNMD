import streamlit as st
from utils import render_option_menu

def service_components():
    event_data = st.session_state.event_data
    st.header("용역 구성 요소")

    categories = ["무대", "음향", "조명", "영상", "특수효과", "케이터링", "인력", "기타"]
    selected_categories = st.multiselect("카테고리 선택", categories, default=event_data.get('selected_categories', []))
    event_data['selected_categories'] = selected_categories

    for category in selected_categories:
        handle_category(category, event_data)

def handle_category(category, data):
    st.subheader(category)
    component = data.get('components', {}).get(category, {})

    def update_status():
        component['status'] = st.session_state[f"{category}_status"]

    component['status'] = render_option_menu(
        f"{category} 진행 상황",
        ["미정", "진행 중", "완료"],
        f"{category}_status",
        on_change=update_status
    )

    # 아이템 관리
    st.write("아이템")
    for i, item in enumerate(component.get('items', [])):
        cols = st.columns([3, 2, 2, 1])
        with cols[0]:
            item['name'] = st.text_input(f"아이템명 {i+1}", value=item['name'], key=f"{category}_item_name_{i}")
        with cols[1]:
            item['quantity'] = st.number_input(f"수량 {i+1}", value=item['quantity'], min_value=1, step=1, key=f"{category}_item_quantity_{i}")
        with cols[2]:
            item['price'] = st.number_input(f"가격 {i+1}", value=item['price'], min_value=0, step=1000, key=f"{category}_item_price_{i}")
        with cols[3]:
            if st.button("삭제", key=f"{category}_delete_item_{i}"):
                component['items'].pop(i)
                st.rerun()

    if st.button(f"{category}에 아이템 추가"):
        component['items'].append({"name": "", "quantity": 1, "price": 0})
        st.rerun()

    data['components'][category] = component