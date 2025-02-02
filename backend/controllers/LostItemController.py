from fastapi import APIRouter, Form, File, UploadFile
from pydantic import BaseModel
from models import MongoClient
from . import ImageController
from bson import ObjectId
from bson.json_util import dumps

client = MongoClient.client

class LostItem(BaseModel):
    image_url: str 
    description: str
    location: str
    time_found: str
    is_claimed: bool

router = APIRouter()

@router.post("/lostitem/add")
async def say_hello(timeFound: str, latitude: float, longitude: float, image: UploadFile = File(...),):
    print(timeFound)
    print(latitude)
    print(longitude)
    print(image)
    mydb = client['LostAndFoundCluster']
    mycol = mydb["LostItems"]

    url = await ImageController.upload_image(image)
    #TODO: add call to model to give it a description
    description = ""

    entry = {"timeFound": timeFound, "location": [latitude,longitude], "image_url": url, "description": description, "is_claimed": False}

    x = mycol.insert_one(entry)
    
    return {"message": f"success"}

@router.put("/lostitem/claim/{id}")
async def say_hello(id: str):
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