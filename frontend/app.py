import streamlit as st
from browse import main as browse_page
from detect import main as detect_page
from visualize import main as visualize_page
from directions import display_map as directions_page
from lostItem import main as lostItem_page
from streamlit_option_menu import option_menu

def main():
    with st.sidebar:
        selected = option_menu(
            "404 Lost & Found",
            ["Home", "Browse", "Report Lost Item","Visualize", "Get Directions"],
            icons=["house", "gear", "search", "map"],
            # menu_icon="cast",
            default_index=0,
        )
    if selected == "Home":
        detect_page()
    elif selected == "Browse":
        browse_page()
    elif selected == "Visualize":
        visualize_page()
    elif selected == "Get Directions":
        directions_page()
    elif selected == "Report Lost Item":
        lostItem_page()

if __name__ == "__main__":
    main()
