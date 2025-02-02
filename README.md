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
Many of the infrastructure is set up in terraform once it is set up to run locally you will need to add a .env file and add the values to the secrets and keys that you can find in the azure ressources once you deploy. Here are a list of environment variables you need to retreive:
MONGO_CONNECTION_STRING=
AZURE_STORAGE_CONNECTION_STRING=
CONTAINER=
AZURE_STORAGE_SAS_URL=
VISION_KEY=
VISION_ENDPOINT=
