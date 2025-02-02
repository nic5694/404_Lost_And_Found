import streamlit as st
import requests
import json
from datetime import datetime
from dateutil import parser
import pandas as pd
import folium
from streamlit_folium import st_folium

BACKEND_URL = (
    "https://404lostandfound-aserdfh2csb8cmfh.canadacentral-01.azurewebsites.net"
)

items = [
    {
        "_id": "679e9480486c93cc13b82d11",
        "timeFound": "2025-02-01 12:34:56",
        "location": ["location1", "location2"],
        "image_url": "https://404lostandfoundacccount.blob.core.windows.net/lostitemcontainer/lostitemcontainer/0ERI9D111CWYIKZKASEUV34RF5HPZUXE.JPG?st=2025-02-01T20%3A04%3A20Z&se=2025-05-24T03%3A04%3A20Z&si=api_container_access&spr=https&sv=2022-11-02&sr=c&sig=cGzA4uiM9VVCmwzCzapSbnQiKBcVFuv%2BVJYcMlo4OW4%3D",
        "description": "",
        "is_claimed": False
    },
    {
        "_id": "679e954855bef841d81cf907",
        "timeFound": "2025-02-01 12:34:56",
        "location": ["location1", "location2"],
        "image_url": "https://404lostandfoundacccount.blob.core.windows.net/lostitemcontainer/lostitemcontainer/USTRVHK3WN8S42EYJLDJJ10LTTAGOETA.JPG?st=2025-02-01T20%3A04%3A20Z&se=2025-05-24T03%3A04%3A20Z&si=api_container_access&spr=https&sv=2022-11-02&sr=c&sig=cGzA4uiM9VVCmwzCzapSbnQiKBcVFuv%2BVJYcMlo4OW4%3D",
        "description": "",
        "is_claimed": False
    },
    {
        "_id": "679e955d55bef841d81cf908",
        "timeFound": "2025-02-01 12:34:56",
        "location": ["location1", "location2"],
        "image_url": "https://404lostandfoundacccount.blob.core.windows.net/lostitemcontainer/lostitemcontainer/EVEE35P2OWQRRRPDG7SB30B3XOQ1YFH0.JPG?st=2025-02-01T20%3A04%3A20Z&se=2025-05-24T03%3A04%3A20Z&si=api_container_access&spr=https&sv=2022-11-02&sr=c&sig=cGzA4uiM9VVCmwzCzapSbnQiKBcVFuv%2BVJYcMlo4OW4%3D",
        "description": "",
        "is_claimed": False
    },
    {
        "_id": "679e957655bef841d81cf909",
        "timeFound": "2025-02-01 12:34:56",
        "location": ["location1", "location2"],
        "image_url": "https://404lostandfoundacccount.blob.core.windows.net/lostitemcontainer/lostitemcontainer/VE6P1T64P7WXR800E76L98GRDOFYGL4P.JPG?st=2025-02-01T20%3A04%3A20Z&se=2025-05-24T03%3A04%3A20Z&si=api_container_access&spr=https&sv=2022-11-02&sr=c&sig=cGzA4uiM9VVCmwzCzapSbnQiKBcVFuv%2BVJYcMlo4OW4%3D",
        "description": "",
        "is_claimed": False
    },
    {
        "_id": "679e95ac55bef841d81cf90a",
        "timeFound": "2025-02-01 12:34:56",
        "location": ["location1", "location2"],
        "image_url": "https://404lostandfoundacccount.blob.core.windows.net/lostitemcontainer/lostitemcontainer/WP2C6C0R11JEAL924MSO309ABKJT7CTS.JPG?st=2025-02-01T20%3A04%3A20Z&se=2025-05-24T03%3A04%3A20Z&si=api_container_access&spr=https&sv=2022-11-02&sr=c&sig=cGzA4uiM9VVCmwzCzapSbnQiKBcVFuv%2BVJYcMlo4OW4%3D",
        "description": "",
        "is_claimed": False
    },
    {
        "_id": "679e95d655bef841d81cf90b",
        "timeFound": "2025-02-01 12:34:56",
        "location": ["location1", "location2"],
        "image_url": "https://404lostandfoundacccount.blob.core.windows.net/lostitemcontainer/lostitemcontainer/CNS0ANWDIHF4EETGHBZO72I0H772T3JL.JPG?st=2025-02-01T20%3A04%3A20Z&se=2025-05-24T03%3A04%3A20Z&si=api_container_access&spr=https&sv=2022-11-02&sr=c&sig=cGzA4uiM9VVCmwzCzapSbnQiKBcVFuv%2BVJYcMlo4OW4%3D",
        "description": "",
        "is_claimed": False
    }
]

def main():
    # response = requests.get(BACKEND_URL + "/lostitem/getAll")

    # API_Data = response.json()
    # list_data  = json.loads(API_Data["items"])
    st.title("Browse Objects")

    cols = st.columns(3)
                      
    for index, item in enumerate(items):
        if not item["is_claimed"]:
            col = cols[index % 3]  # Cycle through columns
            with col:
                card(item["image_url"], item["description"], item["timeFound"], item["_id"], item["location"])

def claim(item_id):
    #TODO: once server is up see if call does what it is supposed to
    response = requests.post(BACKEND_URL + "/lostitem/claim/" + item_id)

    if response.status_code == 200:
        #TODO: route to map directions page and put location from directions
        st.success("Item claimed!")
    else:
        st.error("Failed to claim item")

def card(image_url, description, time_found, item_id, location):
    time_found_date = parser.parse(time_found)
    days_ago = (datetime.utcnow() - time_found_date).days

    st.html(f'''
    <div class="card" style="border: 1px solid #ddd; border-radius: 10px; padding: 1em; margin-top: 1em; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); height: auto; display: flex; flex-direction: column; justify-content: space-between;">
        <img src="{image_url}" style="max-height: 20em;padding-bottom: 1em; object-fit:contain;" width="100%">
        <h3 style="margin-top: 0;">Found {days_ago} days ago</h3>
        <p>Description: {description}</p>
    </div>
    ''')
    if st.button(f"I lost this!", key = item_id, use_container_width=True):
        claim(item_id, location)

if __name__ == "__main__":
    main()