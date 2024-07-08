import streamlit as st
from pages import login, dashboard, project_management, project_detail, output_management, request_handling, user_management, partner_management, partner_request, callback

from streamlit_option_menu import option_menu
from pages import login, dashboard, project_management, project_detail, output_management, request_handling, user_management, partner_management, partner_request, callback

def main():
    st.set_page_config(layout="wide")

    # 세션 관리 추가
    if 'user' not in st.session_state:
        st.session_state.user = None

    # 사이드바 메뉴 설정
    with st.sidebar:
        selected = option_menu(
            "네비게이션",
            ["홈", "대시보드", "프로젝트 관리", "프로젝트 상세", "산출내역서 관리", "수정 요청 처리", "사용자 관리", "협력사 관리", "협력사 추가 요청"],
            icons=["house", "graph-up", "clipboard-data", "clipboard-check", "file-earmark-text", "inbox", "people", "building", "plus-circle"],
            menu_icon="cast",
            default_index=0,
        )

    # 선택한 메뉴에 따라 페이지 로드
    if selected == "홈":
        login.login_screen()
    elif selected == "대시보드":
        dashboard.dashboard_screen()
    elif selected == "프로젝트 관리":
        project_management.project_management_screen()
    elif selected == "프로젝트 상세":
        project_detail.project_detail_screen()
    elif selected == "산출내역서 관리":
        output_management.output_management_screen()
    elif selected == "수정 요청 처리":
        request_handling.request_handling_screen()
    elif selected == "사용자 관리":
        user_management.user_management_screen()
    elif selected == "협력사 관리":
        partner_management.partner_management_screen()
    elif selected == "협력사 추가 요청":
        partner_request.partner_request_screen()

if __name__ == "__main__":
    main()