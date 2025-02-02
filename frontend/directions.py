import streamlit as st
import streamlit.components.v1 as components
import requests
import json

def display_map():
    st.header("Google Map Direction")

    google_api_key = "AIzaSyB9C-2uZFowdBBylfeK5XxDw1IHOKBvzOY"

    # Store address in session state to dynamically update it
    if "address_1" not in st.session_state:
        st.session_state["address_1"] = ""
    if "address_2" not in st.session_state:
        st.session_state["address_2"] = ""

    # Address input fields with autocomplete suggestions
    address_input_1 = st.text_input(
        "Enter the first Address:",
        key="address_input_1",
        value=st.session_state["address_1"],
        help="Type to search for locations"
    )
    address_input_2 = st.text_input(
        "Enter the second Address:",
        key="address_input_2",
        value=st.session_state["address_2"],
        help="Type to search for locations"
    )

    # Function to get place predictions from Google Places API
    def get_place_predictions(query):
        url = f"https://maps.googleapis.com/maps/api/place/autocomplete/json?input={query}&key={google_api_key}"
        response = requests.get(url)
        predictions = response.json().get("predictions", [])
        return [place["description"] for place in predictions]

    # Fetch suggestions for both address fields while typing
    if address_input_1:
        address_suggestions_1 = get_place_predictions(address_input_1)
        st.write("Suggestions for Address 1:")
        st.write(address_suggestions_1)

    if address_input_2:
        address_suggestions_2 = get_place_predictions(address_input_2)
        st.write("Suggestions for Address 2:")
        st.write(address_suggestions_2)

    # Set default locations
    default_location_1 = "concordia university, montreal"
    default_location_2 = "john abbott college, montreal"

    # Create a Google Map iframe to show both addresses and directions
    map_html = f"""
        <iframe id="googleMap" width="100%" height="600" frameborder="0" style="border:0" 
        src="https://www.google.com/maps/embed/v1/directions?key={google_api_key}&origin={address_input_1 or default_location_1}&destination={address_input_2 or default_location_2}" 
        allowfullscreen></iframe>
    """
    components.html(map_html, height=600)

    # Listen for messages from JavaScript and update the address in session_state
    components.html(
        """
        <script>
            window.addEventListener("message", function(event) {
                if (event.origin !== "http://localhost:8501") return;

                var data = JSON.parse(event.data);
                if (data.address_1) {
                    // Send the addresses back to Streamlit
                    window.parent.document.dispatchEvent(new CustomEvent("update_address_1", {detail: data.address_1}));
                    window.parent.document.dispatchEvent(new CustomEvent("update_address_2", {detail: data.address_2}));
                }
            }, false);
        </script>
        """,
        height=0,
    )


    # JavaScript event listener in Streamlit to capture the updated addresses
    st.session_state["address_1"] = st.experimental_get_query_params().get(
        "address_1", [""]
    )[0]
    st.session_state["address_2"] = st.experimental_get_query_params().get(
        "address_2", [""]
    )[0]


if __name__ == "__main__":
    display_map()