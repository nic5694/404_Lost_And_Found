from fastapi import File, UploadFile
from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv
import string
import random
class ImageUploadService:
    def __init__(self):
        load_dotenv()
        self.sas_url = os.getenv('AZURE_STORAGE_SAS_URL')
        self.blob_service_client = BlobServiceClient(account_url=self.sas_url)
        self.container_blob = self.blob_service_client.get_container_client(os.getenv('CONTAINER'))

    async def upload_image(self, image: UploadFile) -> str:
        filename = image.filename
        file_extension = filename.rsplit('.', 1)[1]
        random_name = self.id_generator() + '.' + file_extension
        blob_client = self.container_blob.get_blob_client(random_name)
        file_content = await image.read()
        blob_client.upload_blob(data=file_content, overwrite=True)
        url = blob_client.url
        return url

    def id_generator(self, size=32, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))