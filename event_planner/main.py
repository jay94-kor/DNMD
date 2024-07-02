import streamlit as st
from streamlit_pills import pills
import sqlite3
from pages import basic_info, venue_info, budget_info, service_components, progress_tracking
from database import init_db, load_data, save_data
from utils import load_config
from ui_components import sidebar_navigation

def main():
    st.set_page_config(page_title="이벤트 기획 도구", layout="wide")
    st.title("이벤트 기획 도구")

    # 데이터베이스 초기화
    init_db()

    # 설정 로드
    config = load_config()

    # 사이드바 네비게이션
    current_page = sidebar_navigation()

    # 메인 컨텐츠
    if current_page == "기본 정보":
        basic_info.render()
    elif current_page == "장소 정보":
        venue_info.render()
    elif current_page == "예산 정보":
        budget_info.render()
    elif current_page == "용역 구성 요소":
        service_components.render()
    elif current_page == "진행 상황":
        progress_tracking.render()

    # 임시 저장 버튼
    if st.button("임시 저장"):
        save_data()
        st.success("데이터가 성공적으로 저장되었습니다.")

if __name__ == "__main__":
    main()