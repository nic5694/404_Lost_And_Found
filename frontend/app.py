import streamlit as st
import cv2
from PIL import Image
import numpy as np
from ultralytics import YOLO
from similarity_model import ImageDetector

# Resnet50 for image similarity
model = ImageDetector("resnet50", weights="DEFAULT")
model.embed_dataset("../assets/images")

# YOLOv8 model for object detection
yolo_model = YOLO("yolov8n.pt")  # Load a pre-trained YOLOv8 model


def process_image(img):
    """
    Helper function to process an image using the model.
    """
    img.save("temp.jpg")
    similar_images = model.similar_images("temp.jpg", n=5)

    return similar_images


def detect_objects(image):
    """
    Detect objects in an image using YOLOv8 and return bounding boxes.
    """
    # Perform object detection
    results = yolo_model(image)

    # Extract bounding boxes, labels, and confidence scores
    detections = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())  # Bounding box coordinates
            label = yolo_model.names[int(box.cls)]  # Object label
            confidence = box.conf.item()  # Confidence score
            detections.append((x1, y1, x2, y2, label, confidence))

    return detections


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

    # Let the user choose between real-time video and taking a picture
    mode = st.radio("Choose input mode:", ("Take a Picture", "Real-Time Video"))

    # Input for reference object dimensions (optional)
    reference_object_width_cm = st.number_input(
        "Enter the width of the reference object (in cm):", min_value=0.1, value=10.0
    )
    reference_object_width_px = st.number_input(
        "Enter the width of the reference object (in pixels):", min_value=1, value=100
    )

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
                        use_container_width_width=True,
                    )

        # Release the webcam when inference is stopped
        cap.release()


if __name__ == "__main__":
    main()
