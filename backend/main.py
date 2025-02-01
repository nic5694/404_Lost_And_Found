from fastapi import FastAPI
from controllers import LostItemController, LookingForItemController

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(LostItemController.router)
app.include_router(LookingForItemController.router)