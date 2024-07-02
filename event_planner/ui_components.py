import streamlit as st
from streamlit_pills import pills

def sidebar_navigation():
    pages = ["기본 정보", "장소 정보", "예산 정보", "용역 구성 요소", "진행 상황"]
    return st.sidebar.radio("단계 선택", pages)

def pill_selector(label, options, key):
    return pills(label, options, key=key)

def budget_sidebar(total_budget, expected_profit):
    st.sidebar.title("예산 정보")
    st.sidebar.metric("총 예산", f"{total_budget:,}원")
    st.sidebar.metric("예상 수익", f"{expected_profit:.1f}%")
    available_budget = total_budget * (1 - expected_profit / 100)
    st.sidebar.metric("사용 가능 예산", f"{available_budget:,}원")
    return available_budget