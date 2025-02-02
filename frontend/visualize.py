import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import numpy as np
from folium.plugins import HeatMap

# Backend URL
BACKEND_URL = "http://d404lostandfound.canadacentral.cloudapp.azure.com:8000"


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

    start_date = np.datetime64("2025-01-01")
    end_date = np.datetime64("2025-02-02")
    df["date"] = pd.date_range(start=start_date, end=end_date, periods=len(df))
    df["location_name"] = np.random.choice(
        ["Downtown Montreal", "Old Port", "Plateau", "Griffintown", "Westmount"],
        len(df),
    )
    df["is_claimed"] = np.random.choice([True, False], len(df))

    # Display statistics
    st.subheader("Key Statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Lost Objects", len(df))
    col2.metric("Claimed Objects", df["is_claimed"].sum())
    col3.metric("Unclaimed Objects", len(df) - df["is_claimed"].sum())

    # Trend in the Number of Lost Objects Over Time
    st.subheader("Trend in Number of Lost Objects Over Time")

    # Generate random counts for each day in the date range
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    random_counts = np.random.randint(
        0, 20, size=len(date_range)
    )  # Random counts between 0 and 20
    trend_data = pd.DataFrame({"date": date_range, "count": random_counts})

    # Plot the trend using Plotly
    fig_trend = px.line(
        trend_data,
        x="date",
        y="count",
        title="Daily Lost Objects (Jan 1, 2025 - Feb 2, 2025)",
    )
    st.plotly_chart(fig_trend)

    # Filter locations to Downtown Montreal area
    downtown_montreal_bbox = {
        "min_lat": 45.49,
        "max_lat": 45.52,
        "min_lon": -73.58,
        "max_lon": -73.55,
    }
    df_downtown = df[
        (df["lat"] >= downtown_montreal_bbox["min_lat"])
        & (df["lat"] <= downtown_montreal_bbox["max_lat"])
        & (df["lon"] >= downtown_montreal_bbox["min_lon"])
        & (df["lon"] <= downtown_montreal_bbox["max_lon"])
    ]

    # Display the global map
    st.subheader("Map of Lost Objects")
    st.write("Click on the markers to view the lost object.")
    global_map = folium.Map(location=[45.5019, -73.5674], zoom_start=14)

    # Add points to the map
    for _, row in df.iterrows():
        popup_content = f"""
            <img src="{row["image_url"]}" width="150" height="150"><br>
            <b>Coordinates:</b><br/> {row["lat"]}, {row["lon"]}
        """
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=folium.Popup(popup_content, max_width=250),
        ).add_to(global_map)

    # Display the map using st_folium
    st_folium(global_map, width=700, height=500)

    # Trend in Locations
    st.subheader("Trend in Locations")
    if len(df_downtown) > 0:
        # Create a folium map centered on Downtown Montreal
        downtown_map = folium.Map(location=[45.5019, -73.5674], zoom_start=14)

        # Add a heatmap for lost objects
        heat_data = [[row["lat"], row["lon"]] for _, row in df_downtown.iterrows()]
        HeatMap(heat_data).add_to(downtown_map)

        # Display the map using st_folium
        st_folium(downtown_map, width=700, height=500)
    else:
        st.warning("No lost objects found in the Downtown Montreal area.")


if __name__ == "__main__":
    main()
