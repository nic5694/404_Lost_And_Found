import streamlit as st
import cv2
from PIL import Image
import numpy as np
from ultralytics import YOLO
from similarity_model import ImageDetector
import streamlit.components.v1 as components

# Resnet50 for image similarity
model = ImageDetector("resnet50", weights="DEFAULT")
model.embed_dataset("../assets/images")

yolo_model = YOLO("yolov8n.pt")  


def process_image(img):
    """
    Helper function to process an image using the model.
    """
    img.save("temp.jpg")
    similar_images = model.similar_images("temp.jpg", n=5)
    return similar_images


def display_map():
    st.header("Google Map with Address Lookup and Marker")

    google_api_key = "AIzaSyB9C-2uZFowdBBylfeK5XxDw1IHOKBvzOY"

    # Store address in session state to dynamically update it
    if "address" not in st.session_state:
        st.session_state["address"] = ""

    # Address input field
    address_input = st.text_input("Enter an Address:", key="address_input", value=st.session_state["address"])

    # Button to fetch current location
    if st.button("Use Current Location"):
        components.html(
            """
            <script>
                function getLocation() {
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(showPosition, showError);
                    } else {
                        alert("Geolocation is not supported by this browser.");
                    }
                }

                function showPosition(position) {
                    var lat = position.coords.latitude;
                    var lng = position.coords.longitude;
                    var coords = lat + ", " + lng;

                    var geocoder = new google.maps.Geocoder();
                    var latlng = new google.maps.LatLng(lat, lng);
                    geocoder.geocode({'location': latlng}, function(results, status) {
                        if (status === 'OK' && results[0]) {
                            var address = results[0].formatted_address;
                            window.parent.postMessage(JSON.stringify({ "coords": coords, "address": address }), "*");
                        } else {
                            window.parent.postMessage(JSON.stringify({ "coords": coords, "address": "Unknown Location" }), "*");
                        }
                    });
                }

                function showError(error) {
                    let message = "Unknown error";
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            message = "User denied the request for Geolocation.";
                            break;
                        case error.POSITION_UNAVAILABLE:
                            message = "Location information is unavailable.";
                            break;
                        case error.TIMEOUT:
                            message = "The request to get user location timed out.";
                            break;
                    }
                    alert(message);
                }

                getLocation();
            </script>
            """,
            height=0
        )

    # Ensure the map always loads
    default_location = "45.49735595451695,-73.57950983145975"  
    map_html = f'''
        <iframe id="googleMap" width="100%" height="600" frameborder="0" style="border:0" 
        src="https://www.google.com/maps/embed/v1/place?key={google_api_key}&q={address_input or default_location}" 
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
                if (data.address) {
                    // Send the address back to Streamlit
                    window.parent.document.dispatchEvent(new CustomEvent("update_address", {detail: data.address}));
                }
            }, false);
        </script>
        """,
        height=0,
    )

    # JavaScript event listener in Streamlit
    st.session_state["address"] = st.experimental_get_query_params().get("address", [""])[0]



def measure_object_size(box, reference_object_width_px, reference_object_width_cm):
    """
    Measure the size of an object using a reference object.
    """
    x1, y1, x2, y2, label, confidence = box
    width_px = x2 - x1  # Width of the object in pixels
    height_px = y2 - y1  # Height of the object in pixels

    # Calculate scale (pixels per cm) using the reference object
    scale = reference_object_width_px / reference_object_width_cm

    # Calculate real-world size
    width_cm = width_px / scale
    height_cm = height_px / scale

    return width_cm, height_cm


def draw_boxes(
    image, detections, reference_object_width_px=None, reference_object_width_cm=None
):
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

        # Measure and display object size (if reference object is provided)
        if reference_object_width_px and reference_object_width_cm:
            width_cm, height_cm = measure_object_size(
                box, reference_object_width_px, reference_object_width_cm
            )
            size_text = f"Size: {width_cm:.2f} cm x {height_cm:.2f} cm"
            cv2.putText(
                image,
                size_text,
                (x1, y2 + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

    return Image.fromarray(image)  # Convert back to PIL image


def main():
    st.image("../assets/logo.png", width=400)

    st.header("Object Detection & Image Similarity with Google Maps")

    # Let the user choose between real-time video and taking a picture
    mode = st.radio("Choose input mode:", ("Take a Picture", "Real-Time Video"))

    # Input for reference object dimensions (optional)
    reference_object_width_cm = st.number_input(
        "Enter the width of the reference object (in cm):", min_value=0.1, value=10.0
    )
    reference_object_width_px = st.number_input(
        "Enter the width of the reference object (in pixels):", min_value=1, value=100
    )

    # Object Detection Section
    if mode == "Take a Picture":
        # Capture image from webcam
        img_file_buffer = st.camera_input("Take a picture")

        if img_file_buffer is not None:
            # Convert the image buffer to a PIL Image
            img_pil = Image.open(img_file_buffer)

            # Detect objects and draw bounding boxes
            detections = detect_objects(img_pil)
            img_with_boxes = draw_boxes(
                img_pil,
                detections,
                reference_object_width_px,
                reference_object_width_cm,
            )

            # Display the image with bounding boxes
            st.image(
                img_with_boxes, caption="Detected Objects", use_container_width=True
            )

            # Process the image using the model
            similar_images = process_image(img_pil)

            # Display the similar images in a single row
            st.write("Similar Images:")
            cols = st.columns(len(similar_images))  # Create columns for each image
            for (img_path, similarity), col in zip(similar_images.items(), cols):
                resized_img = Image.open(img_path).resize(
                    (150, 150)
                )  # Resize the image
                col.image(
                    resized_img,
                    caption=f"Similarity: {similarity:.2f}",
                    use_container_width=True,
                )

    elif mode == "Real-Time Video":
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

            # Detect objects and draw bounding boxes
            detections = detect_objects(img_pil)
            img_with_boxes = draw_boxes(
                img_pil,
                detections,
                reference_object_width_px,
                reference_object_width_cm,
            )

            # Display the image with bounding boxes
            frame_placeholder.image(
                img_with_boxes, caption="Detected Objects", use_container_width=True
            )

            # Process the image using the model
            similar_images = process_image(img_pil)

            # Display the similar images in a single row
            with result_placeholder.container():
                st.write("Similar Images:")
                cols = st.columns(len(similar_images))  # Create columns for each image
                for (img_path, similarity), col in zip(similar_images.items(), cols):
                    resized_img = Image.open(img_path).resize(
                        (150, 150)
                    )  # Resize the image
                    col.image(
                        resized_img,
                        caption=f"Similarity: {similarity:.2f}",
                        use_container_width=True,
                    )

        # Release the webcam when inference is stopped
        cap.release()

    # Google Maps
    display_map()


if __name__ == "__main__":
    main()
