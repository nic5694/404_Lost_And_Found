# 404 Lost & Found
![ConUHacks IX Winner](https://img.shields.io/badge/-ConUHacks%20IX%20Winning%20Project-8A2BE2?style=for-the-badge&logo=github&logoColor=white)  

Ever lost something precious and wished you had a digital detective on your side? Meet 404 Lost & Found – your AI-powered personal item finder and data visualization tool

## 🔗 Links  
Check out our demo and project submission:  

[![YouTube](https://img.shields.io/badge/-YouTube-FF0000?logo=youtube&logoColor=white)](https://youtu.be/BHq4QkTe6PE)  
[![Devpost](https://img.shields.io/badge/-Devpost-003E54?logo=devpost&logoColor=white)](https://devpost.com/software/404-lost-found)  

## 📖 Overview  
**404: Lost & Found** is an intelligent lost-and-found platform that combines **YOLOv8 for real-time object detection** and **ResNet for image similarity scoring** to help users identify and recover lost items. Deployed on **Azure Web Apps**, this system features:

- 🎯 **Custom object detection** (YOLO) for precise item localization
- 🔍 **ResNet-based similarity scoring** for matching lost/found items
- ☁️ **Cloud-native architecture** with Azure Blob Storage and MongoDB


## ✨ Key Features  
- **Real-Time Object Detection**: YOLO model identifies items in uploaded images (e.g., "laptop", "backpack", "keys").  
- **Visual Similarity Search**: ResNet-50 generates embeddings for similarity comparisons between items.  
- **Scalable Storage**: Azure Blob Storage manages item images with metadata stored in MongoDB.  
- **FastAPI Backend**: High-performance API endpoints for seamless integration.  


## 🛠️ Tech Stack  
### **AI/ML Core**  
![YOLO](https://img.shields.io/badge/-YOLO-00FFFF?logo=python&logoColor=white)
![ResNet](https://img.shields.io/badge/-ResNet-FF6F00?logo=pytorch&logoColor=white)  
- **YOLOv5** for object detection and bounding box generation  
- **ResNet-50** (pre-trained + fine-tuned) for feature extraction and similarity scoring
- **Azure AI Vision** Pre trained caption generation model

### **Backend & Cloud**  
![FastAPI](https://img.shields.io/badge/-FastAPI-009688?logo=fastapi&logoColor=white)
![Azure](https://img.shields.io/badge/-Azure-0089D6?logo=microsoft-azure&logoColor=white)
![MongoDB](https://img.shields.io/badge/-MongoDB-47A248?logo=mongodb&logoColor=white)  
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
- **FastAPI** REST API with Python 3.10+  
- **Azure Web Apps** (PaaS) for API deployment  
- **Azure Blob Storage** for image management  
- **MongoDB Atlas** for item metadata storage
- **Github Actions** for CI/CD, building and pushing Docker images to ACR
- **Terraform** for Infrastructure as Code (IaC) deployment on Azure

## How to run the project

- To run the project in the backend navigate to the backend folder and run this command:

```bash
python3 -m venv venv
# Then you run the following command
# Windows command prompt
.venv\Scripts\activate.bat

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS and Linux
source .venv/bin/activate
```

- Finally you install the required packages:

```bash
pip install -r requirements.txt
```

- To run the project in the backend navigate to the frontend folder and run this command:

```bash
python3 -m venv venv
# Then you run the following command
# Windows command prompt
.venv\Scripts\activate.bat

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS and Linux
source .venv/bin/activate
```

- Finally you install the required packages:

```bash
pip install -r requirements.txt
```

- Fianlly to run the streamlit application run:

```bash
streamlit run app.py
```
#### How to configure cloud infrastructure
Many of the infrastructure is set up in terraform once it is set up to run locally you will need to add a .env file and add the values to the secrets and keys that you can find in the azure resources once you deploy. Here are a list of environment variables you need to retrieve:

### Additional Setup Instructions

To run the project out of the box, you will need to create the following files that are not included in the git repository:

1. **`.env` file**:
   Create a `.env` file in the `backend` directory with the following content:
```properties
MONGO_CONNECTION_STRING="your_mongo_connection_string"
AZURE_STORAGE_CONNECTION_STRING="your_azure_storage_connection_string"
CONTAINER="your_container_name"
AZURE_STORAGE_SAS_URL="your_azure_storage_sas_url"
VISION_KEY="your_vision_key"
VISION_ENDPOINT="your_vision_endpoint"
```
2. **`terraform.tfvars` file**: Create a `terraform.tfvars` file in the
```properties
resource_group_location = "Canada Central"
resource_group_name_prefix = "rg"
subscription_id = "your_subscription_id"
action_members_emails = ["email1@example.com", "email2@example.com", "email3@example.com"]
```
### Running the project
- To run the backend you navigate to the `backend` directory where their is the `docker-compose.yml` file and run the following command 
```bash
docker compose build
# then run
docker compose up
```
- To run the frontend it is also as simple as running the same commands in the `frontend` directory and run the following commands
```bash
docker compose build
docker compose up
```
This will get you running locally be sure to do this configuration after deploying your infrastructure for the first time and retreiving all the keys and secrets to use the services utilized by the application.
