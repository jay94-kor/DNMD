import streamlit as st
from streamlit_option_menu import option_menu
from pages import login, dashboard, project_management, project_detail, output_management, request_handling, user_management, partner_management, partner_request, callback

def main():
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
        st.write("대시보드: 전체 프로젝트와 예산 상태를 시각화하여 한눈에 파악할 수 있습니다.")
        dashboard.dashboard_screen()
    elif selected == "프로젝트 관리":
        st.write("프로젝트 관리: 새로운 프로젝트를 생성하고 기존 프로젝트를 관리할 수 있습니다.")
        project_management.project_management_screen()
    elif selected == "프로젝트 상세":
        st.write("프로젝트 상세: 특정 프로젝트의 상세 정보를 확인하고 관리할 수 있습니다.")
        project_detail.project_detail_screen()
    elif selected == "산출내역서 관리":
        st.write("산출내역서 관리: 프로젝트의 산출내역서를 관리할 수 있습니다.")
        output_management.output_management_screen()
    elif selected == "수정 요청 처리":
        st.write("수정 요청 처리: 관리자가 사용자로부터의 수정 요청을 검토하고 승인 또는 반려할 수 있습니다.")
        request_handling.request_handling_screen()
    elif selected == "사용자 관리":
        st.write("사용자 관리: 관리자가 사용자 계정을 관리할 수 있습니다.")
        user_management.user_management_screen()
    elif selected == "협력사 관리":
        st.write("협력사 관리: 협력사를 체계적으로 관리할 수 있습니다.")
        partner_management.partner_management_screen()
    elif selected == "협력사 추가 요청":
        st.write("협력사 추가 요청: 사용자가 새로운 협력사를 시스템에 추가 요청할 수 있습니다.")
        partner_request.partner_request_screen()
    elif selected == "callback":
        callback.callback_screen()

if __name__ == "__main__":
    main()
