from controllers import LostItemController
from fastapi import FastAPI, File, UploadFile, HTTPException
from PIL import Image
import numpy as np
from ultralytics import YOLO

from service.ImageAnalyzerService import ImageAnalyzerService
from service.ImageUploadService import ImageUploadService
from similarity_model import ImageDetector
import io
from pymongo import MongoClient
import gridfs
from dotenv import load_dotenv
import json

load_dotenv()
app = FastAPI()

# Resnet50 for image similarity
model = ImageDetector("resnet50", weights="DEFAULT")
model.update_missing_embeddings()
image_upload_service = ImageUploadService()
image_analyzer_service = ImageAnalyzerService()

# YOLOv8 model for object detection
yolo_model = YOLO("yolov8n.pt")  # Load a pre-trained YOLOv8 model

app.include_router(LostItemController.router)


@app.get("/get_locations")
async def get_locations():
    """
    Fetch all locations from the MongoDB collection.
    """
    return model.fetch_locations()


@app.post("/process_image")
async def process_image(file: UploadFile = File(...)):
    model.update_missing_embeddings()
    if file.filename == "":
        raise HTTPException(status_code=400, detail="No selected file")

    img = Image.open(io.BytesIO(await file.read()))
    img.save("temp.jpg")
    similar_images, image_id_map = model.similar_images("temp.jpg", n=5)

    return {
        "similar_images": json.dumps(similar_images),
        "image_id_map": json.dumps(image_id_map),
    }

@app.post("/similar_description")
async def similar_description(description: str = Form(...)):
    
    similar_images = model.similar_images_description(description, n=5)

    return {"similar_images" :json.dumps(similar_images)}

@app.post("/upload")
async def upload_to_db(file: UploadFile = File(...)):
    if file.filename == "":
        raise HTTPException(status_code=400, detail="No selected file")

    # img = Image.open(io.BytesIO(await file.read()))
    # img.save("temp.jpg")
    # similar_images = model.similar_images("temp.jpg", n=5)
    return


@app.get("/test_ml")
async def test_ml():
    similar_images = model.similar_images("./assets/logo.png", n=5)
    return similar_images


@app.post("/detect_objects")
async def detect_objects(file: UploadFile = File(...)):
    if file.filename == "":
        raise HTTPException(status_code=400, detail="No selected file")

    img = Image.open(io.BytesIO(await file.read()))
    img_np = np.array(img)

    # Perform object detection
    results = yolo_model(img_np)

    # Extract bounding boxes, labels, and confidence scores
    detections = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())  # Bounding box coordinates
            label = yolo_model.names[int(box.cls)]  # Object label
            confidence = box.conf.item()  # Confidence score
            detections.append((x1, y1, x2, y2, label, confidence))

    return detections


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
