from fastapi import APIRouter, Form, File, UploadFile
from pydantic import BaseModel
from models import MongoClient
from . import ImageController

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
    mydb = client["LostAndFoundCluster"]
    mycol = mydb["LostItems"]

    url = await ImageController.upload_image(image)
    #TODO: add call to model to give it a description
    description = ""

    entry = {"timeFound"}

    x = mycol.insert_one(mydict)
    
    return {"message": f"Hello {name} {url}"}

@router.get("/hello")
async def say_hello():
    return {"message": "Hello World"}