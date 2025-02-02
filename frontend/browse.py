import streamlit as st
import requests

BACKEND_URL = (
    "https://404lostandfound-aserdfh2csb8cmfh.canadacentral-01.azurewebsites.net"
)

def main():

    lost_items = requests.get(BACKEND_URL + "/lostitem/getAll")

    st.write("Browse Page")
    st.write("Here are the lost items:")

    lost_items = lost_items.json()["items"]

    print(len(lost_items))

    # st.write(lost_items)
    st.write(len(lost_items))

    # for item in lost_items:
    #     st.write("a")

    # for item in lost_items:
        # st.write(item)
        # card(item["image_url"], item["description"], item["time_found"])


def card(image_url, description, time_found):
    st.write("card")
    # st.write(f"Time Found: {time_found}")
    # st.write(f"Description: {description}")
    # st.image(image_url, width=400)