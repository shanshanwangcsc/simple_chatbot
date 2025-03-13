#!/bin/bash

# If you want to activate some venv etc. add it here
python3 -m venv --system-site-packages aitta_venv
source aitta_venv/bin/activate

# Install packages and update packages
echo "Install requirements_poro.txt"
pip install -r requirements_poro.txt
pip install --upgrade langchain langchain-community langchain-core langsmith "pydantic<2"

# Process .pdf to chromadb
echo "Run ingest.py"
python ingest.py

# Set token as env variable
export PORO_ACCESS_TOKEN="your token here"

# Now we need different version for aitta-client :)
pip install --upgrade pydantic

# Run the app
chainlit run app.py -w
