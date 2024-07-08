import streamlit as st
from streamlit_option_menu import option_menu
from pages import login, dashboard, project_management, project_detail, output_management, request_handling, user_management, partner_management, partner_request, callback

def main():
    st.set_page_config(layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False

    if st.session_state.logged_in:
        with st.sidebar:
            menu_items = ["대시보드", "프로젝트 관리", "프로젝트 상세", "산출내역서 관리", "수정 요청 처리", "사용자 관리", "협력사 관리", "협력사 추가 요청"]
            if st.session_state.is_admin:
                menu_items.append("관리자 페이지")
            
            selected = option_menu(
                "네비게이션",
                menu_items,
                icons=["graph-up", "clipboard-data", "clipboard-check", "file-earmark-text", "inbox", "people", "building", "plus-circle", "gear"],
                menu_icon="cast",
                default_index=0,
            )

        if selected == "대시보드":
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
        elif selected == "관리자 페이지" and st.session_state.is_admin:
            admin.admin_screen()
    else:
        login.login_screen()

if __name__ == "__main__":
    main()
