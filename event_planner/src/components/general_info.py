import streamlit as st
from streamlit_option_menu import option_menu
from utils import format_phone_number, render_option_menu

def handle_general_info(event_data):
    st.write(f"현재 예상 참여 관객 수: {event_data.get('scale', 0)}명")

    step_suffix = f"_step_{st.session_state.step}_{id(event_data)}"

    def update_event_name():
        event_data['event_name'] = st.session_state[f"event_name_input{step_suffix}"]

    event_data['event_name'] = st.text_input("프로젝트명", value=event_data.get('event_name', ''), key=f"event_name_input{step_suffix}", on_change=update_event_name)
    event_data['client_name'] = st.text_input("클라이언트명", value=event_data.get('client_name', ''), key=f"client_name_basic{step_suffix}", on_change=lambda: event_data.update({'client_name': st.session_state[f"client_name_basic{step_suffix}"]}))
    event_data['manager_name'] = st.text_input("담당 PM", value=event_data.get('manager_name', ''), key=f"manager_name_basic{step_suffix}", on_change=lambda: event_data.update({'manager_name': st.session_state[f"manager_name_basic{step_suffix}"]}))
    event_data['manager_email'] = st.text_input("담당 PM 이메일", value=event_data.get('manager_email', ''), key=f"manager_email_basic{step_suffix}", on_change=lambda: event_data.update({'manager_email': st.session_state[f"manager_email_basic{step_suffix}"]}))

    def update_manager_position():
        event_data['manager_position'] = st.session_state[f"manager_position{step_suffix}"]

    event_data['manager_position'] = render_option_menu(
        "담당자 직급",
        options=["선임", "책임", "수석"],
        key=f"manager_position{step_suffix}",
        on_change=update_manager_position
    )

    manager_contact = st.text_input(
        "담당자 연락처",
        value=event_data.get('manager_contact', ''),
        help="숫자만 입력해주세요 (예: 01012345678)",
        key=f"manager_contact_basic{step_suffix}",
        on_change=lambda: event_data.update({'manager_contact': format_phone_number(''.join(filter(str.isdigit, st.session_state[f"manager_contact_basic{step_suffix}"])))})
    )
    event_data['manager_contact'] = manager_contact