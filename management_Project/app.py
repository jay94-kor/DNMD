import streamlit as st
from pages import login, signup, dashboard, project_management, project_detail, output_management, request_handling, user_management, partner_management, partner_request

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select a page", ["Login", "Signup", "Dashboard", "Project Management", "Project Detail", "Output Management", "Request Handling", "User Management", "Partner Management", "Partner Request"])

    if page == "Login":
        login.login_screen()
    elif page == "Signup":
        signup.signup_screen()
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

if __name__ == "__main__":
    main()
