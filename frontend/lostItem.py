import datetime
import requests
import streamlit as st
from PIL import Image
import json
import io
import streamlit.components.v1 as components

# Backend URL
BACKEND_URL = (
    # "https://404lostandfound-aserdfh2csb8cmfh.canadacentral-01.azurewebsites.net"
    "http://d404lostandfound.canadacentral.cloudapp.azure.com:8000"
)

BACKUP_URL = (
    "http://d404lostandfound.canadacentral.cloudapp.azure.com:8000/"
)

# Set default location
default_location_1 = "concordia university, montreal"

def log_to_console(message: str) -> None:
    js_code = f"""
<script>
    console.log({json.dumps(message)});
</script>
"""
    components.html(js_code)

def main():
    google_api_key = "AIzaSyB9C-2uZFowdBBylfeK5XxDw1IHOKBvzOY"

    # Store address in session state to dynamically update it
    if "address_1" not in st.session_state:
        st.session_state["address_1"] = ""

    # Address input field
    address_input_1 = st.text_input(
        "Enter the Address:",
        key="address_input_1",
        value=st.session_state["address_1"],
    )

    

    if address_input_1 != st.session_state["address_1"]:
        st.session_state["address_1"] = address_input_1

    st.text("Add item only once location is set!!")
    img_file_buffer = st.camera_input("Take a picture") 

    img_pil = None
    if img_file_buffer is not None:
        # Convert the image buffer to a PIL Image
        img_pil = Image.open(img_file_buffer)
        
    if img_pil is not None:
        # Send image to backend for object detection
        img_bytes = io.BytesIO()
        img_pil.save(img_bytes, format="JPEG")
        img_bytes.seek(0)
        files = {"image": img_bytes.getvalue()}

        address_to_use = address_input_1 or default_location_1
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address_to_use}&key={google_api_key}"
        response = requests.get(geocode_url)
        data = response.json()

        lat = None
        lng = None
        if data["status"] == "OK":
            lat = data["results"][0]["geometry"]["location"]["lat"]
            lng = data["results"][0]["geometry"]["location"]["lng"]

        if lat is not None and lng is not None:
            data={
                "longitude":lng, 
                "latitude":lat, 
                "timeFound":str(datetime.datetime.now())}
            # Send image to backend
            response = requests.post(f"{BACKEND_URL}/lostitem/add", files=files, data=data)
            st.write("Item reported successfully!")
        else:
            st.warning("Need address to add item!")
            img_pil = None