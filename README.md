# 404 Lost & Found

ConUHacks

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
