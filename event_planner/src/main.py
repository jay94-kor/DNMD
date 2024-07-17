import streamlit as st
from streamlit_option_menu import option_menu
from components import general_info, venue_info, service_components
from database import init_db, save_event_data, load_event_data
from excel_generator import generate_summary_excel
from utils import safe_operation, render_option_menu
from datetime import date, datetime
import json
import logging
import os

# Logging 설정
logging.basicConfig(filename='app.log', level=logging.ERROR)

# JSON 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
JSON_PATH = os.path.join(BASE_DIR, 'config', 'item_options.json')
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'config.json')

# JSON 파일에서 item_options 로드
with open(JSON_PATH, 'r', encoding='utf-8') as file:
    item_options = json.load(file)

# config.json 파일에서 설정 로드
with open(CONFIG_PATH, 'r', encoding='utf-8') as file:
    config = json.load(file)

# EventOptions 클래스 정의
class EventOptions:
    def __init__(self, item_options):
        self.EVENT_TYPES = item_options['EVENT_TYPES']
        self.CONTRACT_TYPES = item_options['CONTRACT_TYPES']
        self.STATUS_OPTIONS = item_options['STATUS_OPTIONS']
        self.MEDIA_ITEMS = item_options['MEDIA_ITEMS']
        self.CATEGORIES = item_options['CATEGORIES']
        self.CATEGORY_ICONS = item_options['CATEGORY_ICONS']

event_options = EventOptions(item_options)

def main():
    st.set_page_config(page_title="이벤트 기획 정의서", layout="wide")
    st.title("이벤트 기획 정의서")

    init_db()

    if 'event_data' not in st.session_state:
        st.session_state.event_data = {}

    if 'step' not in st.session_state:
        st.session_state.step = 0

    general_info.handle_general_info(st.session_state.event_data)
    venue_info.venue_info()
    service_components.service_components()

    if st.button("저장"):
        save_event_data(st.session_state.event_data)
        st.success("데이터가 성공적으로 저장되었습니다.")

    if st.button("엑셀 파일 생성"):
        safe_operation(generate_summary_excel)()

    functions = {
        0: general_info.handle_general_info,
        1: venue_info.venue_info,
        2: service_components.service_components,
        3: generate_summary_excel
    }

    step_names = ["기본 정보", "장소 정보", "용역 구성 요소", "정의서 생성"]

    menu_placeholder = st.empty()
    content_placeholder = st.empty()
    button_placeholder = st.empty()

    def update_content():
        current_step = st.session_state.step
        event_type = st.session_state.event_data.get('event_type')

        if event_type == "온라인 콘텐츠" and current_step == 1:
            current_step = 2
            st.session_state.step = 2

        with menu_placeholder.container():
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
            st.rerun()
            return

        with content_placeholder.container():
            functions[current_step](st.session_state.event_data)

        with button_placeholder.container():
            col1, col2 = st.columns([1, 1])

            with col1:
                if current_step > 0:
                    if st.button("이전", key="previous_button"):
                        if event_type == "온라인 콘텐츠" and current_step == 2:
                            st.session_state.step = 0
                        else:
                            st.session_state.step -= 1
                        st.rerun()

            with col2:
                if current_step < 3:
                    if st.button("다음", key="next_button"):
                        is_valid, missing_fields = check_required_fields(current_step)
                        if is_valid:
                            if event_type == "온라인 콘텐츠" and current_step == 0:
                                st.session_state.step = 2
                            else:
                                st.session_state.step += 1
                            st.rerun()
                        else:
                            highlight_missing_fields(missing_fields)

    update_content()

if __name__ == "__main__":
    main()