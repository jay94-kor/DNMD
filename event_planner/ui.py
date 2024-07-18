import streamlit as st
from streamlit_option_menu import option_menu

def display_guide(guide_text: str) -> None:
    with st.expander("사용자 가이드", expanded=False):
        st.markdown(guide_text)

def render_option_menu(label: str, options: list, key: str) -> str:
    icons = ["🔹" for _ in options]
    selected = option_menu(
        label, options,
        icons=icons,
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "5px", "background-color": "#f0f0f0"},
            "icon": {"color": "#ff6347", "font-size": "20px"},
            "nav-link": {"font-size": "18px", "text-align": "center", "margin":"0px", "--hover-color": "#ffcccc", "--icon-color": "#ff6347"},
            "nav-link-selected": {"background-color": "#ff6347", "color": "white", "--icon-color": "white"},
        },
        key=key
    )
    return selected
