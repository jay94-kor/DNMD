import streamlit as st
from utils import format_currency

def handle_budget_info(event_data):
    st.header("예산 정보")
    
    col1, col2 = st.columns(2)
    
    with col1:
        event_data['total_budget'] = st.number_input(
            "총 예산",
            min_value=0,
            value=event_data.get('total_budget', 0),
            step=1000000,
            format="%d",
            help="원 단위로 입력해주세요."
        )
        st.write(f"총 예산: {format_currency(event_data['total_budget'])}원")

    with col2:
        event_data['budget_status'] = st.selectbox(
            "예산 상태",
            options=["확정", "미확정"],
            index=0 if event_data.get('budget_status') == "확정" else 1
        )

    event_data['budget_note'] = st.text_area(
        "예산 관련 특이사항",
        value=event_data.get('budget_note', ''),
        height=100
    )

    st.subheader("예산 항목 상세")
    budget_items = event_data.get('budget_items', [])
    
    for i, item in enumerate(budget_items):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        with col1:
            item['name'] = st.text_input(f"항목명 {i+1}", value=item.get('name', ''), key=f"budget_item_name_{i}")
        with col2:
            item['amount'] = st.number_input(f"금액 {i+1}", value=item.get('amount', 0), step=10000, format="%d", key=f"budget_item_amount_{i}")
        with col3:
            st.write(f"금액: {format_currency(item['amount'])}원")
        with col4:
            if st.button("삭제", key=f"delete_budget_item_{i}"):
                budget_items.pop(i)
                st.rerun()

    if st.button("항목 추가"):
        budget_items.append({"name": "", "amount": 0})
        st.rerun()

    event_data['budget_items'] = budget_items

    total_budget_items = sum(item['amount'] for item in budget_items)
    st.write(f"총 예산 항목 합계: {format_currency(total_budget_items)}원")

    if total_budget_items > event_data['total_budget']:
        st.warning("총 예산 항목 합계가 전체 예산을 초과했습니다.")
    elif total_budget_items < event_data['total_budget']:
        st.info(f"남은 예산: {format_currency(event_data['total_budget'] - total_budget_items)}원")