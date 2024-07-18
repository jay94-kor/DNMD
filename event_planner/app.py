import streamlit as st
from streamlit_option_menu import option_menu
from ui import display_guide, render_option_menu
from utils import load_json_file, format_currency, format_phone_number, safe_operation
from db import init_db, save_event_data, load_event_data, get_all_events
from event_data import EventOptions, handle_general_info, handle_event_type, handle_budget_info, handle_video_production, handle_offline_event, generate_summary_excel, check_required_fields, highlight_missing_fields, venue_info, service_components, basic_info

# Initialize Database
init_db()

# Load Config
config = load_json_file('config.json')
event_options = EventOptions(config)

# Main Function
def main():
    st.title("이벤트 플래너")

    if 'current_event' not in st.session_state:
        st.session_state.current_event = None
    if 'step' not in st.session_state:
        st.session_state.step = 0
    if 'event_data' not in st.session_state:
        st.session_state.event_data = {}

    functions = {
        0: basic_info,
        1: venue_info,
        2: service_components,
        3: generate_summary_excel
    }

    step_names = ["기본 정보", "장소 정보", "용역 구성 요소", "정의서 생성"]

    current_step = st.session_state.step
    event_type = st.session_state.event_data.get('event_type')

    if event_type == "온라인 콘텐츠" and current_step == 1:
        current_step = 2
        st.session_state.step = 2

    selected_step = option_menu(
        None,
        step_names,
        icons=['info-circle', 'geo-alt', 'list-task', 'file-earmark-spreadsheet'],
        default_index=current_step,
        orientation='horizontal',
        styles={
            "container": {"padding": "0!important", "background-color": "#e3f2fd"},
            "icon": {"color": "#1976d2", "font-size": "25px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin":"0px", "--hover-color": "#bbdefb", "--icon-color": "#1976d2"},
            "nav-link-selected": {"background-color": "#2196f3", "color": "white", "--icon-color": "white"},
        },
    )

    if selected_step != step_names[current_step]:
        new_step = step_names.index(selected_step)
        if event_type == "온라인 콘텐츠" and new_step == 1:
            new_step = 2
        st.session_state.step = new_step
        st.experimental_rerun()

    functions[current_step]()

    col1, col2 = st.columns([1, 1])

    with col1:
        if current_step > 0:
            if st.button("이전", key="previous_button"):
                if event_type == "온라인 콘텐츠" and current_step == 2:
                    st.session_state.step = 0
                else:
                    st.session_state.step -= 1
                st.experimental_rerun()

    with col2:
        if current_step < 3:
            if st.button("다음", key="next_button"):
                is_valid, missing_fields = check_required_fields(current_step)
                if is_valid:
                    if event_type == "온라인 콘텐츠" and current_step == 0:
                        st.session_state.step = 2
                    else:
                        st.session_state.step += 1
                    st.experimental_rerun()
                else:
                    highlight_missing_fields(missing_fields)

if __name__ == "__main__":
    main()
