from fastapi import File, UploadFile
from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv
import string
import random

class ImageUploadService:
    def __init__(self):
        load_dotenv()

    sas_url = os.getenv('AZURE_STORAGE_SAS_URL')
    blob_service_client = BlobServiceClient(account_url=sas_url)
    container_blob = blob_service_client.get_container_client(os.getenv('CONTAINER'))

    async def upload_image(image: UploadFile) -> str:
        filename = image.filename
        file_extension = filename.rsplit('.', 1)[1]
        random_name = id_generator() + '.' + file_extension
        blob_client = container_blob.get_blob_client(random_name)
        file_content = await image.read()
        blob_client.upload_blob(data=file_content, overwrite=True)
        url = blob_client.url
        return url

    def id_generator(size=32, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))