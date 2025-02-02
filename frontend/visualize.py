import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import numpy as np

# Backend URL
BACKEND_URL = "http://d404lostandfound.canadacentral.cloudapp.azure.com:8000"
# "https://404lostandfound-aserdfh2csb8cmfh.canadacentral-01.azurewebsites.net"


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
    st.title("Lost and Found Dashboard")

    # Fetch locations from the API
    locations = fetch_locations_from_api()

    if not locations:
        st.warning("No locations found in the database.")
        return

    # Convert the list of locations to a DataFrame
    df = pd.DataFrame(locations, columns=["lat", "lon", "image_url"])

    # Add arbitrary data for demonstration
    df["date"] = pd.date_range(
        start="2023-01-01", periods=len(df), freq="D"
    )  # Arbitrary dates
    df["location_name"] = np.random.choice(
        ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"], len(df)
    )  # Arbitrary locations
    df["is_claimed"] = np.random.choice(
        [True, False], len(df)
    )  # Arbitrary claim status

    # Display statistics
    st.subheader("Key Statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Lost Objects", len(df))
    col2.metric("Claimed Objects", df["is_claimed"].sum())
    col3.metric("Unclaimed Objects", len(df) - df["is_claimed"].sum())

    # Display the map
    st.subheader("Map of Lost Objects")
    m = folium.Map(location=[45.5019, 73.5674], zoom_start=2)

    # Add points to the map
    for _, row in df.iterrows():
        popup_content = f"""
            <img src="{row["image_url"]}" width="150" height="150"><br>
            <b>Coordinates:</b><br/> {row["lat"]}, {row["lon"]}
        """
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=folium.Popup(popup_content, max_width=250),
        ).add_to(m)

    # Display the map using st_folium
    st_folium(m, width=700, height=500)

    # Trend in the Number of Lost Objects Over Time
    st.subheader("Trend in Number of Lost Objects Over Time")
    trend_data = df.resample("M", on="date").size().reset_index(name="count")
    fig_trend = px.line(trend_data, x="date", y="count", title="Monthly Lost Objects")
    st.plotly_chart(fig_trend)

    # Trend in Locations
    st.subheader("Trend in Locations")
    location_counts = df["location_name"].value_counts().reset_index()
    location_counts.columns = ["Location", "Count"]
    fig_location = px.bar(
        location_counts, x="Location", y="Count", title="Lost Objects by Location"
    )
    st.plotly_chart(fig_location)


if __name__ == "__main__":
    main()
