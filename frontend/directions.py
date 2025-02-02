import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import os
load_dotenv()


def display_map():
    st.header("Map Direction")

    google_api_key = os.getenv("GOOGLE_KEY")

    # Default locations
    default_location_1 = "Concordia University, Montreal"
    default_location_2 = "John Abbott College, Montreal"

    # Store addresses in session state
    if "address_1" not in st.session_state:
        st.session_state["address_1"] = default_location_1
    if "address_2" not in st.session_state:
        st.session_state["address_2"] = default_location_2

    # Display input fields with Autocomplete (embedded via HTML)
    autocomplete_html = f"""
        <script src="https://maps.googleapis.com/maps/api/js?key={google_api_key}&libraries=places"></script>
        <script>
            function initAutocomplete() {{
                var input1 = document.getElementById("address1");
                var input2 = document.getElementById("address2");

                input1.value = "{st.session_state['address_1']}";
                input2.value = "{st.session_state['address_2']}";

                var autocomplete1 = new google.maps.places.Autocomplete(input1);
                var autocomplete2 = new google.maps.places.Autocomplete(input2);

                autocomplete1.addListener("place_changed", function() {{
                    var place = autocomplete1.getPlace();
                    document.getElementById("hidden_address1").value = place.formatted_address;
                    updateStreamlit();
                }});

                autocomplete2.addListener("place_changed", function() {{
                    var place = autocomplete2.getPlace();
                    document.getElementById("hidden_address2").value = place.formatted_address;
                    updateStreamlit();
                }});
            }}

            function updateStreamlit() {{
                var address1 = document.getElementById("hidden_address1").value;
                var address2 = document.getElementById("hidden_address2").value;
                var streamlitData = JSON.stringify({{ "address_1": address1, "address_2": address2 }});
                window.parent.postMessage(streamlitData, "*");
            }}

            window.onload = initAutocomplete;
        </script>

        <input id="address1" type="text" placeholder="Enter first address" style="width: 90%; padding: 8px; font-size: 16px;">
        <input id="hidden_address1" type="hidden" value="{st.session_state['address_1']}">

        <input id="address2" type="text" placeholder="Enter second address" style="width: 90%; padding: 8px; font-size: 16px; margin-top: 20px;">
        <input id="hidden_address2" type="hidden" value="{st.session_state['address_2']}">
    """

    components.html(autocomplete_html, height=150)

    # Google Maps iframe for directions
    map_html = f"""
        <iframe width="100%" height="600" frameborder="0" style="border:0" 
        src="https://www.google.com/maps/embed/v1/directions?key={google_api_key}&origin={st.session_state['address_1']}&destination={st.session_state['address_2']}" 
        allowfullscreen></iframe>
    """
    components.html(map_html, height=600)

if __name__ == "__main__":
    display_map()
