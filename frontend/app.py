import streamlit as st
import requests
from PIL import Image
import numpy as np
import cv2
import io

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


def main():
    st.image("./assets/logo.png", width=400)

    # Create tabs
    tab1, tab2 = st.tabs(["Take a Picture", "Real-Time Video"])

    with tab1:
        # Capture image from webcam
        img_file_buffer = st.camera_input("Take a picture")

        if img_file_buffer is not None:
            # Convert the image buffer to a PIL Image
            img_pil = Image.open(img_file_buffer)

            # Send image to backend for object detection
            files = {"file": img_file_buffer.getvalue()}
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
            similar_images = response.json()

            # Display the similar images in a single row
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

    with tab2:
        # OpenCV webcam capture
        cap = cv2.VideoCapture(0)

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
            files = {"file": img_bytes}
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
            similar_images = response.json()

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
