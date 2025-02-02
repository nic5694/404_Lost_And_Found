import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

class ImageAnalyzerService:
    def __init__(self):
        load_dotenv()
        try:
            self.endpoint = os.environ["VISION_ENDPOINT"]
            self.key = os.environ["VISION_KEY"]
        except KeyError:
            print("Missing environment variable 'VISION_ENDPOINT' or 'VISION_KEY'")
            print("Set them before running this sample.")
            exit()

        # Create an Image Analysis client
        self.client = ImageAnalysisClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.key)
        )

    def analyze_image_object(self, image: str) -> str:
        result = self.client.analyze_from_url(
            image_url=image,
            visual_features=[VisualFeatures.CAPTION, VisualFeatures.READ],
            gender_neutral_caption=True,
        )
        return (result.caption.text)
