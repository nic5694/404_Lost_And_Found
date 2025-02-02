import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium

BACKEND_URL = (
    "https://404lostandfound-aserdfh2csb8cmfh.canadacentral-01.azurewebsites.net"
)


def fetch_locations_from_api():
    """
    Fetch locations from the FastAPI endpoint.
    """
    try:
        response = requests.get(BACKEND_URL + "/get_locations")
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch locations from the API: {e}")
        return []

def main():
    st.title("Browse Objects")

    # Fetch locations from the API
    locations = fetch_locations_from_api()

    if not locations:
        st.warning("No locations found in the database.")
        return

    # Convert the list of locations to a DataFrame
    df = pd.DataFrame(locations, columns=["lat", "lon", "image_url"])

    # Create a folium map
    m = folium.Map(location=[45.5019, 73.5674], zoom_start=1)

    # Add points to the map
    for _, row in df.iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=folium.Popup(
                f'<img src="{row["image_url"]}" width="150" height="150">',
                max_width=250,
            ),
        ).add_to(m)

    # Display the map using st_folium
    st_folium(m, width=700, height=500)


if __name__ == "__main__":
    main()