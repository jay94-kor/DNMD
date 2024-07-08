import streamlit as st
from pages import login, dashboard, project_management, project_detail, output_management, request_handling, user_management, partner_management, partner_request, callback

def main():
    st.sidebar.title("Navigation")
    query_params = st.experimental_get_query_params()
    page = query_params.get("page", ["Login"])[0]

    if page == "Login":
        login.login_screen()
    elif page == "Dashboard":
        dashboard.dashboard_screen()
    elif page == "Project Management":
        project_management.project_management_screen()
    elif page == "Project Detail":
        project_detail.project_detail_screen()
    elif page == "Output Management":
        output_management.output_management_screen()
    elif page == "Request Handling":
        request_handling.request_handling_screen()
    elif page == "User Management":
        user_management.user_management_screen()
    elif page == "Partner Management":
        partner_management.partner_management_screen()
    elif page == "Partner Request":
        partner_request.partner_request_screen()
    elif page == "callback":
        callback.callback_screen()

if __name__ == "__main__":
    main()
