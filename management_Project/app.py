import streamlit as st
from pages import login, dashboard, project_management, project_detail, output_management, request_handling, user_management, partner_management, partner_request, callback

def main():
    st.sidebar.title("네비게이션")
    query_params = st.experimental_get_query_params()
    page = query_params.get("page", ["Login"])[0]

    menu = {
        "홈": "Login",
        "대시보드": "Dashboard",
        "프로젝트 관리": "Project Management",
        "프로젝트 상세": "Project Detail",
        "산출내역서 관리": "Output Management",
        "수정 요청 처리": "Request Handling",
        "사용자 관리": "User Management",
        "협력사 관리": "Partner Management",
        "협력사 추가 요청": "Partner Request"
    }

    for name, page_name in menu.items():
        st.sidebar.write(f"[{name}](?page={page_name})")

    if page == "Login":
        login.login_screen()
    elif page == "Dashboard":
        st.write("대시보드: 전체 프로젝트와 예산 상태를 시각화하여 한눈에 파악할 수 있습니다.")
        dashboard.dashboard_screen()
    elif page == "Project Management":
        st.write("프로젝트 관리: 새로운 프로젝트를 생성하고 기존 프로젝트를 관리할 수 있습니다.")
        project_management.project_management_screen()
    elif page == "Project Detail":
        st.write("프로젝트 상세: 특정 프로젝트의 상세 정보를 확인하고 관리할 수 있습니다.")
        project_detail.project_detail_screen()
    elif page == "Output Management":
        st.write("산출내역서 관리: 프로젝트의 산출내역서를 관리할 수 있습니다.")
        output_management.output_management_screen()
    elif page == "Request Handling":
        st.write("수정 요청 처리: 관리자가 사용자로부터의 수정 요청을 검토하고 승인 또는 반려할 수 있습니다.")
        request_handling.request_handling_screen()
    elif page == "User Management":
        st.write("사용자 관리: 관리자가 사용자 계정을 관리할 수 있습니다.")
        user_management.user_management_screen()
    elif page == "Partner Management":
        st.write("협력사 관리: 협력사를 체계적으로 관리할 수 있습니다.")
        partner_management.partner_management_screen()
    elif page == "Partner Request":
        st.write("협력사 추가 요청: 사용자가 새로운 협력사를 시스템에 추가 요청할 수 있습니다.")
        partner_request.partner_request_screen()
    elif page == "callback":
        callback.callback_screen()

if __name__ == "__main__":
    main()
