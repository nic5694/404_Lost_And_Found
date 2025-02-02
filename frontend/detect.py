import streamlit as st
import requests
from PIL import Image
import numpy as np
import cv2
import io
import streamlit.components.v1 as components

# Backend URL
BACKEND_URL = (
    "https://404lostandfound-aserdfh2csb8cmfh.canadacentral-01.azurewebsites.net"
)

def draw_boxes(image, detections):
    """
    Draw bounding boxes and size measurements on an image.
    """
    image = np.array(image)  # Convert PIL image to NumPy array
    for box in detections:
        x1, y1, x2, y2, label, confidence = box

        # Draw bounding box
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Display label and confidence
        text = f"{label} {confidence:.2f}"
        cv2.putText(
            image, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
        )

    return Image.fromarray(image)  # Convert back to PIL image

def display_map():
    st.header("Google Map Direction")

    google_api_key = "AIzaSyB9C-2uZFowdBBylfeK5XxDw1IHOKBvzOY"

    # Store address in session state to dynamically update it
    if "address_1" not in st.session_state:
        st.session_state["address_1"] = ""
    if "address_2" not in st.session_state:
        st.session_state["address_2"] = ""

    # Address input fields
    address_input_1 = st.text_input("Enter the first Address:", key="address_input_1", value=st.session_state["address_1"])
    address_input_2 = st.text_input("Enter the second Address:", key="address_input_2", value=st.session_state["address_2"])

    # Set default locations
    default_location_1 = "concordia university, montreal" 
    default_location_2 = "john abbott college, montreal" 
    
    # Create a Google Map iframe to show both addresses and directions
    map_html = f'''
        <iframe id="googleMap" width="100%" height="600" frameborder="0" style="border:0" 
        src="https://www.google.com/maps/embed/v1/directions?key={google_api_key}&origin={address_input_1 or default_location_1}&destination={address_input_2 or default_location_2}" 
        allowfullscreen></iframe>
    '''
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
    st.session_state["address_1"] = st.experimental_get_query_params().get("address_1", [""])[0]
    st.session_state["address_2"] = st.experimental_get_query_params().get("address_2", [""])[0]

def main():
    st.image("./assets/logo.png", width=400)

    # Create tabs
    tab1, tab2 = st.tabs(["Search your item", "Real-Time Detection"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            # Capture image from webcam
            img_file_buffer = st.camera_input("Take a picture")

        with col2:
            # Upload image from file
            uploaded_file = st.file_uploader(
                "Upload an image", type=["jpg", "jpeg", "png"]
            )

        img_pil = None
        if img_file_buffer is not None:
            # Convert the image buffer to a PIL Image
            img_pil = Image.open(img_file_buffer)
        elif uploaded_file is not None:
            # Convert the uploaded file to a PIL Image
            img_pil = Image.open(uploaded_file)

        if img_pil is not None:
            # Send image to backend for object detection
            img_bytes = io.BytesIO()
            img_pil.save(img_bytes, format="JPEG")
            img_bytes.seek(0)
            files = {"file": img_bytes.getvalue()}
            response = requests.post(f"{BACKEND_URL}/detect_objects", files=files)
            detections = response.json()

            # Draw bounding boxes on the image
            img_with_boxes = draw_boxes(img_pil, detections)

            # Display the image with bounding boxes
            st.image(
                img_with_boxes, caption="Detected Objects", use_container_width=True
            )

            # Send image to backend for similarity search
            response = requests.post(f"{BACKEND_URL}/process_image", files=files)
            try:
                similar_images = response.json()
            except requests.exceptions.JSONDecodeError:
                st.error("Failed to decode JSON response")
                return

            # Display the similar images in a single row
            st.write("   ")
            st.write("Similar Images:")
            cols = st.columns(len(similar_images))  # Create columns for each image
            for (img_url, similarity), col in zip(similar_images.items(), cols):
                # Fetch the image from the URL
                img_response = requests.get(img_url)
                img = Image.open(io.BytesIO(img_response.content)).resize(
                    (150, 150)
                )  # Resize the image
                col.image(
                    img,
                    caption=f"Similarity: {similarity:.2f}",
                    use_container_width=True,
                )

            st.write("Couldn't find your image here?")
            # Button to push the image to the database
            if st.button("Declare Lost Item"):
                response = requests.post(f"{BACKEND_URL}/upload", files=files)
                if response.status_code == 200:
                    st.success("Image successfully pushed to the database")
                else:
                    st.error("Failed to push image to the database")

    with tab2:
        # OpenCV webcam capture
        cap = cv2.VideoCapture(1)

        if not cap.isOpened():
            st.error("Could not open webcam.")
            return

        # Placeholder for displaying the webcam feed
        frame_placeholder = st.empty()

        # Placeholder for displaying similar images
        result_placeholder = st.empty()

        # Checkbox to toggle real-time inference
        run_inference = st.checkbox("Enable camera")

        while run_inference:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to capture frame.")
                break

            # Convert the frame to a PIL image
            img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Send image to backend for object detection
            img_bytes = io.BytesIO()
            img_pil.save(img_bytes, format="JPEG")
            img_bytes.seek(0)
            files = {"file": img_bytes.getvalue()}
            response = requests.post(f"{BACKEND_URL}/detect_objects", files=files)
            detections = response.json()

            # Draw bounding boxes on the image
            img_with_boxes = draw_boxes(img_pil, detections)

            # Display the image with bounding boxes
            frame_placeholder.image(
                img_with_boxes, caption="Detected Objects", use_container_width=True
            )

            # Send image to backend for similarity search
            response = requests.post(f"{BACKEND_URL}/process_image", files=files)
            try:
                similar_images = response.json()
            except requests.exceptions.JSONDecodeError:
                st.error("Failed to decode JSON response")
                return

            # Display the similar images in a single row
            with result_placeholder.container():
                st.write("Similar Images:")
                cols = st.columns(len(similar_images))  # Create columns for each image
                for (img_url, similarity), col in zip(similar_images.items(), cols):
                    # Fetch the image from the URL
                    img_response = requests.get(img_url)
                    img = Image.open(io.BytesIO(img_response.content)).resize(
                        (150, 150)
                    )  # Resize the image
                    col.image(
                        img,
                        caption=f"Similarity: {similarity:.2f}",
                        use_container_width=True,
                    )

        # Release the webcam when inference is stopped
        cap.release()

if __name__ == "__main__":
    main()
