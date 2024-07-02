import streamlit as st
from database import save_data, load_data
from utils import format_currency, calculate_percentage

def render():
    st.header("예산 정보")
    
    data = load_data()

    col1, col2 = st.columns(2)

    with col1:
        total_budget = st.number_input("계약 금액 (원)", min_value=0, value=data.get('total_budget', 0), step=10000)
        st.write(f"계약 금액: {format_currency(total_budget)}")

    with col2:
        expected_profit_percent = st.number_input("예상 영업이익 (%)", min_value=0.0, max_value=100.0, value=data.get('expected_profit', 0.0), step=0.1)
        expected_profit_amount = calculate_percentage(total_budget, expected_profit_percent)
        st.write(f"예상 영업이익: {format_currency(expected_profit_amount)}")

    available_budget = total_budget - expected_profit_amount
    st.write(f"사용 가능 예산: {format_currency(available_budget)}")

    if st.button("저장"):
        save_data({
            'total_budget': total_budget,
            'expected_profit': expected_profit_percent
        })
        st.success("예산 정보가 저장되었습니다.")

    st.write("---")
    st.subheader("예산 분배")

    # 여기에 각 카테고리별 예산 분배를 위한 UI를 추가할 수 있습니다.
    # 예를 들어, 슬라이더나 입력 필드를 사용하여 각 카테고리의 예산 비율을 설정할 수 있습니다.