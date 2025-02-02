import streamlit as st
import requests
from PIL import Image
import numpy as np
import cv2
import io
import streamlit.components.v1 as components
import json

# Backend URL
BACKEND_URL = (
    # "https://404lostandfound-aserdfh2csb8cmfh.canadacentral-01.azurewebsites.net"
    "http://d404lostandfound.canadacentral.cloudapp.azure.com:8000"
)

BACKUP_URL = (
    "http://d404lostandfound.canadacentral.cloudapp.azure.com:8000/"
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


def log_to_console(message: str) -> None:
    js_code = f"""
<script>
    console.log({json.dumps(message)});
</script>
"""
    components.html(js_code)

def get_item_by_field(list_data, value):
    """
    Returns the first item in the list `list_data` where the `field` matches the given `value`.
    If no matching item is found, returns None.
    """
    for item in list_data:
        if item.get("image_url") == value:
            return item

def claim(item_id, location):
    #TODO: cahnge back to real URL
    response = requests.put(BACKUP_URL + "/lostitem/claim/" + item_id)

    if response.status_code == 200:
        #TODO: route to map directions page and put location from directions
        st.success("Item claimed!")
    else:
        st.error("Failed to claim item")

def main():
    # st.image("./assets/logo.png", width=400)
    base_path = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_path, "assets", "logo.png")

    st.image(logo_path, width=400)


    # Create tabs
    tab1, tab2 = st.tabs(["Use a picture", "Use Real-Time Detection"])

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
            #TODO: change to real URL
            response = requests.post(f"{BACKUP_URL}/detect_objects", files=files)
            detections = response.json()

            # Draw bounding boxes on the image
            img_with_boxes = draw_boxes(img_pil, detections)

            # Display the image with bounding boxes
            st.image(
                img_with_boxes, caption="Detected Objects", use_container_width=True
            )

            # Send image to backend for similarity search
            #TODO: change to real URL
            response = requests.post(f"{BACKUP_URL}/process_image", files=files)
            try:
                parsed_response = response.json()
                similar_images = json.loads(parsed_response["similar_images"])
                
                #absolute vomit code, but eh it works
                items_response = requests.get(BACKUP_URL + "/lostitem/getAll")

                API_Data = items_response.json()
                list_data  = json.loads(API_Data["items"])
                good_list = []

                for item  in similar_images.items():
                    object = get_item_by_field(list_data, item[0])
                    if object is not None:
                        good_list.append(object)

            except requests.exceptions.JSONDecodeError:
                st.error("Failed to decode JSON response")
                return

            # Display the similar images in a single row
            st.write("   ")
            st.write("Similar Images:")
            cols = st.columns(len(similar_images))  # Create columns for each image
            for (img_url, similarity), col in zip(similar_images.items(), cols):
                
                object = get_item_by_field(list_data, img_url) 
                if object["is_claimed"]:    
                    continue
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
                if col.button(f"I lost this!", key = object["_id"], use_container_width=True):
                    claim(object["_id"], object["location"])

            st.write("Couldn't find your image here?")
            # Button to push the image to the database
            if st.button("Declare Lost Item"):
                #TODO: change to real URL
                response = requests.post(f"{BACKUP_URL}/upload", files=files)
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
            #TODO: change to real URL
            response = requests.post(f"{BACKUP_URL}/detect_objects", files=files)
            detections = response.json()

            # Draw bounding boxes on the image
            img_with_boxes = draw_boxes(img_pil, detections)

            # Display the image with bounding boxes
            frame_placeholder.image(
                img_with_boxes, caption="Detected Objects", use_container_width=True
            )

            # Send image to backend for similarity search
            #TODO: change to real URL
            response = requests.post(f"{BACKUP_URL}/process_image", files=files)
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
