import streamlit as st
from pages import basic_info, venue_info, budget_info, service_components, progress_tracking
from database import init_db, load_data, save_data
from utils import load_config
from ui_components import sidebar_navigation

def main():
    st.set_page_config(page_title="이벤트 기획 도구", layout="wide")
    st.title("이벤트 기획 도구")

    # 데이터베이스 초기화
    init_db()

    # 사이드바 네비게이션
    current_page = sidebar_navigation()

    # 데이터 로드
    data = load_data()
    if not isinstance(data, dict):
        data = {}

    # 설정 로드
    config = load_config()
    if not isinstance(config, dict):
        config = {}

    # 메인 컨텐츠
    if current_page == "기본 정보":
        try:
            updated_data = basic_info.render(data, config)
        except Exception as e:
            st.error(f"기본 정보 페이지 렌더링 중 오류 발생: {str(e)}")
            updated_data = None

    # 데이터 저장
    if updated_data:
        save_data(updated_data)
        st.success("데이터가 성공적으로 저장되었습니다.")

if __name__ == "__main__":
    main()