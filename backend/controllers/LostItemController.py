from fastapi import APIRouter, Form, File, UploadFile
from pydantic import BaseModel
from models import MongoClient
from service import ImageUploadService, ImageAnalyzerService
from bson import ObjectId
from bson.json_util import dumps
import random
import string

client = MongoClient.client
upload_service = ImageUploadService.ImageUploadService()
image_analyzer_service = ImageAnalyzerService.ImageAnalyzerService()

class LostItem(BaseModel):
    image_url: str 
    description: str
    location: str
    time_found: str
    is_claimed: bool

def id_generator(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

router = APIRouter()

@router.post("/lostitem/add")
async def add_new_lost_item(timeFound: str = Form(...), latitude: float =  Form(...), longitude: float =  Form(...), image: UploadFile = File(...)):
    mydb = client['LostAndFoundCluster']
    mycol = mydb["LostItems"]
    image.filename = id_generator() + '.' + ".jpg"
    url = await upload_service.upload_image(image)
    description = image_analyzer_service.analyze_image_object(url)
    entry = {"timeFound": timeFound, "location": [latitude,longitude], "image_url": url, "description": description, "is_claimed": False}
    x = mycol.insert_one(entry)
    return {"message": f"success"}

@router.put("/lostitem/claim/{id}")
async def update_lost_item(id: str):
    mydb = client['LostAndFoundCluster']
    mycol = mydb["LostItems"]

    # Update the item with the given ID
    result = mycol.update_one({'_id': ObjectId(id)}, {'$set': {'is_claimed': True}}, upsert = False)

    if result.modified_count == 1:
        return {"message": "Item claimed successfully"}
    else:
        return {"message": "Item not found or already claimed"}
    
@router.get("/lostitem/getAll")
async def getALLURLs():
    mydb = client['LostAndFoundCluster']
    mycol = mydb["LostItems"]

    items = mycol.find({})
    items_list = list(items) 

    items_json = dumps(items_list)  # Convert list to JSON

    return {"items": items_json}