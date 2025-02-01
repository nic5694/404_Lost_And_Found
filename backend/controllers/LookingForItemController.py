from fastapi import APIRouter

router = APIRouter()

@router.post("/lookingforitem/image")
async def add_looking_for_item():

    return {"message": "success"}

@router.post("/lookingforitem/description")
async def add_looking_for_item():

    return {"message": "success"}