import torch
import os
import math
import requests
from io import BytesIO
from pymongo import MongoClient
import matplotlib.pyplot as plt
import numpy as np
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from kmeans_pytorch import kmeans
from PIL import Image
import random
from bson.decimal128 import Decimal128
from openai import OpenAI



class ImageDetector:
    def __init__(self, model_name, weights="DEFAULT"):
        # dictionary defining the supported NN architectures
        self.embed_dict = {
            "resnet50": self.obtain_children,
            "vgg19": self.obtain_classifier,
            "efficientnet_b0": self.obtain_classifier,
        }

        # MongoDB setup
        self.client = MongoClient(
            "mongodb+srv://api_user:NfuK4XAU6OiTjzrp@lostandfoundcluster.tsmlz.mongodb.net/?retryWrites=true&w=majority&appName=LostAndFoundCluster"
        )
        self.db = self.client["LostAndFoundCluster"]
        self.collection = self.db["LostItems"]

        # assign class attributes
        self.architecture = self.validate_model(model_name)
        self.weights = weights
        self.transform = self.assign_transform(weights)
        self.device = self.set_device()
        self.model = self.initiate_model()
        self.embed = self.assign_layer()

    def validate_model(self, model_name):
        if model_name not in self.embed_dict.keys():
            raise ValueError(f"The model {model_name} is not supported")
        else:
            return model_name

    def assign_transform(self, weights):
        weights_dict = {
            "resnet50": models.ResNet50_Weights,
            "vgg19": models.VGG19_Weights,
            "efficientnet_b0": models.EfficientNet_B0_Weights,
        }

        # try load preprocess from torchvision else assign default
        try:
            w = weights_dict[self.architecture]
            weights = getattr(w, weights)
            preprocess = weights.transforms()
        except Exception:
            preprocess = transforms.Compose(
                [
                    transforms.Resize(224),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                    ),
                ]
            )

        return preprocess

    def set_device(self):
        if torch.cuda.is_available():
            device = "cuda:0"
        else:
            device = "cpu"

        return device

    def initiate_model(self):
        m = getattr(
            models, self.architecture
        )  # equ to assigning m as models.resnet50()
        model = m(weights=self.weights)  # equ to models.resnet50(weights=...)
        model.to(self.device)

        return model.eval()

    def assign_layer(self):
        model_embed = self.embed_dict[self.architecture]()

        return model_embed

    def obtain_children(self):
        model_embed = nn.Sequential(*list(self.model.children())[:-1])

        return model_embed

    def obtain_classifier(self):
        self.model.classifier = self.model.classifier[:-1]

        return self.model

    def calculate_embedding(self, img):
        img = Image.open(img)
        img_trans = self.transform(img)

        # store computational graph on GPU if available
        if self.device == "cuda:0":
            img_trans = img_trans.cuda()

        img_trans = img_trans.unsqueeze(0)

        return self.embed(img_trans)

    def embed_image(self, image_url):
        """
        Fetch an image from a URL, preprocess it, and compute its embedding.
        """
        try:
            # Fetch the image from the URL
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGB")

            # Preprocess the image
            img_trans = self.transform(img)

            # Store computational graph on GPU if available
            if self.device == "cuda:0":
                img_trans = img_trans.cuda()

            img_trans = img_trans.unsqueeze(0)

            # Compute the embedding
            embedding = self.embed(img_trans).cpu().detach().numpy().tolist()
            return embedding

        except Exception as e:
            print(f"Failed to process image from URL {image_url}: {e}")
            return None

    def update_missing_embeddings(self):
        """
        Iterate over all entries in the database and compute/store embeddings for entries where 'embedding' is missing.
        """
        # Query all documents in the collection
        cursor = self.collection.find({"embedding": {"$exists": False}})

        for document in cursor:
            image_url = document["image_url"]
            print(f"Computing embedding for: {image_url}")

            # Compute the embedding
            embedding = self.embed_image(image_url)
            if embedding is not None:
                # Update the document with the new embedding
                self.collection.update_one(
                    {"_id": document["_id"]}, {"$set": {"embedding": embedding}}
                )
                print(f"Embedding stored for: {image_url}")
            else:
                print(f"Skipping due to error: {image_url}")

        return

    def fetch_locations(self):
        """
        Fetch all locations and their corresponding image URLs from the MongoDB collection.
        """
        locations = []

        cursor = self.collection.find(
            {}, {"location": 1, "image_url": 1}
        )  # Fetch location and image_url fields
        for document in cursor:
            if (
                "location" in document
                and isinstance(document["location"], list)
                and len(document["location"]) == 2
            ):
                lat, lon = document["location"]
                if isinstance(lat, Decimal128):
                    lat = float(lat.to_decimal())
                if isinstance(lon, Decimal128):
                    lon = float(lon.to_decimal())
                image_url = document.get("image_url", "")
                locations.append([lat, lon, image_url])

        return locations

    def similar_images(self, target_image_url, n=None):
        """
        Function for comparing target image to embedded image dataset

        Parameters:
        -----------
        target_image_url: str specifying the URL of the target image to compare
            with the saved feature embedding dataset
        n: int specifying the top n most similar images to return
        """

        # Compute the embedding for the target image
        target_vector = self.calculate_embedding(target_image_url)
        if target_vector is None:
            raise ValueError(
                f"Failed to compute embedding for target image: {target_image_url}"
            )

        target_vector = torch.tensor(target_vector).to(self.device)

        # initiate computation of cosine similarity
        cosine = nn.CosineSimilarity(dim=1)

        # iteratively store similarity of stored images to target image
        sim_dict = {}
        image_id_map = {}
        for record in self.collection.find({"embedding": {"$exists": True}}):
            file_path = record["image_url"]
            vector = torch.tensor(record["embedding"]).to(self.device)
            sim = cosine(vector, target_vector)[0].item()
            sim_dict[file_path] = sim
            image_id_map[str(record["_id"])] = file_path

        # sort based on decreasing similarity
        items = sim_dict.items()
        sim_dict = {k: v for k, v in sorted(items, key=lambda i: i[1], reverse=True)}

        # cut to defined top n similar images
        if n is not None:
            sim_dict = dict(list(sim_dict.items())[: int(n)])

        self.output_images(sim_dict, target_image_url)

        return sim_dict, image_id_map

    def is_float(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def similar_images_description(self, target_description, n=None):

        client = OpenAI()
        
        # iteratively store similarity of stored images to target image
        images_with_similarity = []
        tries = 0
        for record in self.collection.find({}):
            score = -1
            tries = 0
            while score >= 1.0 and score <= 0.0:
                tries += 1
                if tries > 5:
                    record["similarity"] = 0.0
                    break
                completion = client.chat.completions.create(
                model="gpt-4o-mini",
                store=False,
                messages=[
                    {"role": "user", "content": f"give me a similarity score between the following two descriptions: \"{target_description}\" and \"{record['description']}\" between 1 and 0.00, where 1 is the exact same and 0 is nothing at all alike. only return a number"},
                ]
                )
                try:
                    score = float(completion.choices[0].message.content)
                except:
                    score = -1
            
            if score != -1:
                record["similarity"] = score
            
            images_with_similarity.append(record)

        #sort based on decreasing similarity
        images_with_similarity = sorted(images_with_similarity, key=lambda i: i["similarity"], reverse=True)

        # cut to defined top n similar images
        if n is not None:
            images_with_similarity = images_with_similarity[:int(n)]

        return images_with_similarity

    def output_images(self, similar, target_image_url):
        self.display_img(target_image_url, "original")

        for k, v in similar.items():
            self.display_img(k, "similarity:" + str(v))

        return

    def display_img(self, image_url, title):
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            plt.imshow(img)
            plt.axis("off")
            plt.title(title)
            plt.show()
        except Exception as e:
            print(f"Failed to display image from URL {image_url}: {e}")

        return


if __name__ == "__main__":
    model = ImageDetector("resnet50")
    print(model.similar_images_description("a red apple", 5))