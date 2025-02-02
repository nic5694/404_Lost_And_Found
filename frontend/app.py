import streamlit as st

from browse import main as browse_page
from detect import main as detect_page
from streamlit_option_menu import option_menu


def main():
    with st.sidebar:
        selected = option_menu(
            "404 Lost & Found",
            ["Home", "Browse"],
            icons=["house", "gear"],
            # menu_icon="cast",
            default_index=0,
        )
    if selected == "Home":
        detect_page()
    elif selected == "Browse":
        browse_page()


if __name__ == "__main__":
    main()
