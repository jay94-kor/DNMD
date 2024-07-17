import streamlit as st
import logging
from streamlit_option_menu import option_menu

def safe_operation(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"{func.__name__} 실행 중 오류 발생: {str(e)}"
            st.error(error_msg)
            logging.error(error_msg, exc_info=True)
            return None
    return wrapper

def format_currency(amount):
    return "{:,}".format(amount)

def format_phone_number(phone_number):
    if len(phone_number) == 11:
        return f"{phone_number[:3]}-{phone_number[3:7]}-{phone_number[7:]}"
    elif len(phone_number) == 10:
        return f"{phone_number[:3]}-{phone_number[3:6]}-{phone_number[6:]}"
    else:
        return phone_number

def sanitize_sheet_title(title):
    invalid_chars = ['\\', '/', '*', '[', ']', ':', '?']
    for char in invalid_chars:
        title = title.replace(char, '')
    return title

def render_option_menu(label, options, key, on_change=None):
    icons = ["🔹" for _ in options]
    current_value = st.session_state.get(key, options[0])
    if current_value not in options:
        current_value = options[0]
    default_index = options.index(current_value)
    selected = option_menu(
        label, options,
        icons=icons,
        menu_icon="cast",
        default_index=default_index,
        orientation="horizontal",
        styles={
            "container": {"padding": "5px", "background-color": "#f0f0f0"},
            "icon": {"color": "#ff6347", "font-size": "20px"},
            "nav-link": {"font-size": "18px", "text-align": "center", "margin":"0px", "--hover-color": "#ffcccc", "--icon-color": "#ff6347"},
            "nav-link-selected": {"background-color": "#ff6347", "color": "white", "--icon-color": "white"},
        },
        key=key,
        on_change=on_change
    )
    return selected