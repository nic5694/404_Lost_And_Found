import streamlit as st
import requests
import json
from datetime import datetime
from dateutil import parser
import pandas as pd
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components

BACKEND_URL = (
    "https://404lostandfound-aserdfh2csb8cmfh.canadacentral-01.azurewebsites.net"
)

BACKUP_URL = "http://d404lostandfound.canadacentral.cloudapp.azure.com:8000"

GOOGLE_API = "AIzaSyB9C-2uZFowdBBylfeK5XxDw1IHOKBvzOY"


def main():
    # TODO: change to real URL
    response = requests.get(BACKUP_URL + "/lostitem/getAll")

    API_Data = response.json()
    list_data = json.loads(API_Data["items"])
    list_data = filter(lambda x: not x["is_claimed"], list_data)

    st.title("Browse Objects")

    cols = st.columns(3)

    for index, item in enumerate(list_data):
        col = cols[index % 3]  # Cycle through columns
        with col:
            card(
                item["image_url"],
                item["description"],
                item["timeFound"],
                item["_id"],
                item["location"],
            )


def claim(item_id, location):
    # TODO: cahnge back to real URL
    response = requests.put(BACKUP_URL + "/lostitem/claim/" + item_id)

    if response.status_code == 200:
        # TODO: route to map directions page and put location from directions
        st.success("Item claimed!")
    else:
        st.error("Failed to claim item")


def log_to_console(message: str) -> None:
    js_code = f"""
<script>
    console.log({json.dumps(message)});
</script>
"""
    components.html(js_code)


def card(image_url, description, time_found, item_id, location):
    time_found_date = parser.parse(time_found)
    days_ago = (datetime.utcnow() - time_found_date).days

    st.html(
        f"""
    <div class="card" style="border: 1px solid #ddd; border-radius: 10px; padding: 1em; margin-top: 1em; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); height: auto; display: flex; flex-direction: column; justify-content: space-between;">
        <img src="{image_url}" style="max-height: 20em;padding-bottom: 1em; object-fit:contain;" width="100%">
        <h3 style="margin-top: 0;">Found {days_ago} days ago</h3>
        <p>Description: {description}</p>
        <p>Location: <br/>{location[0], location[1]}</p>
    </div>
    """
    )
    if st.button(f"I lost this!", key=item_id, use_container_width=True):
        claim(item_id["$oid"], location)
        show_directions(location)


def show_directions(location):
    """
    Display directions to the location using Google Maps embed.
    """
    lat, lon = location
    st.write(f"Directions to the Location ({lat}, {lon})")
    st.write(
        f'<iframe width="100%" height="400" frameborder="0" style="border:0" '
        f'src="https://www.google.com/maps/embed/v1/directions?origin=current+location&destination={lat},{lon}&key={GOOGLE_API}" '
        f"allowfullscreen></iframe>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
