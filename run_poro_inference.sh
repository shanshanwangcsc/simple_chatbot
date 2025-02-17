#!/bin/bash

# If you want to activate some venv etc. add it here

# Install packages and update packages
echo "Install requirements_poro.txt"
pip install -r requirements_poro.txt
pip install --upgrade langchain langchain-community langchain-core langsmith "pydantic<2"

# Process .pdf to chromadb
echo "Run ingest.py"
python ingest.py

# Set token as env variable
export PORO_ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6ImF0K2p3dCJ9.eyJqdGkiOiJhYmVlNjc0YWU5ZTY0MDk2YTY1OGI4OWQ5NjdmY2VlNSIsImlzcyI6Imh0dHBzOi8vYXBpLWRldi1haXR0YS4yLnJhaHRpYXBwLmZpIiwic3ViIjoiSFNaMlVVT1Y1WFM2N0pET0ZOVlJYS09HTDNTTTdHRjMiLCJhdWQiOlsiaHR0cHM6Ly9hcGktZGV2LWFpdHRhLjIucmFodGlhcHAuZmkiXSwiZXhwIjoxNzQ3MDM2OTI2LCJzY29wZXMiOlsibW9kZWw6THVtaU9wZW4vUG9yby0zNEItY2hhdCIsIkhTWjJVVU9WNVhTNjdKRE9GTlZSWEtPR0wzU003R0YzIl19.SLVfqDDcEkJMvFMClT4nUz7-NkrNHriQ0bYwPOFMcS0"

# Now we need different version for aitta-client :)
pip install --upgrade pydantic

# Run the app 
chainlit run app.py -w