from fastapi import APIRouter, Form, File, UploadFile
from pydantic import BaseModel
from models import MongoClient
from . import ImageController
from bson import ObjectId

client = MongoClient.client

class LostItem(BaseModel):
    image_url: str 
    description: str
    location: str
    time_found: str
    is_claimed: bool

router = APIRouter()

@router.post("/lostitem/add")
async def say_hello(timeFound: str = Form(...), location: str = Form(...), image: UploadFile = File(...),):
    mydb = client['LostAndFoundCluster']
    mycol = mydb["LostItems"]

    url = await ImageController.upload_image(image)
    #TODO: add call to model to give it a description
    description = ""

    entry = {"timeFound": timeFound, "location": location, "image_url": url, "description": description, "is_claimed": False}

    x = mycol.insert_one(entry)
    
    return {"message": f"success"}

@router.put("/lostitem/claim/{id}")
async def say_hello(id: str):
    mydb = client['LostAndFoundCluster']
    mycol = mydb["LostItems"]

    # Update the item with the given ID
    result = mycol.update_one({'_id': ObjectId(id)}, {'$set': {'is_claimed': True}}, upsert = False)

    print(result)

    if result.modified_count == 1:
        return {"message": "Item claimed successfully"}
    else:
        return {"message": "Item not found or already claimed"}