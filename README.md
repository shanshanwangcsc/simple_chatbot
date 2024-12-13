# Simple_chatbot

This is a simple chatbot repo which could answer questions related to the customized documents and a uploaded csv file.
## Create an vitual python environment
The simplest way of creating a python virtual environment is
`python3 -m venv --system-site-packages venv`
## Activate the environment
`source venv/bin/activate`
## Install required python packages
All the required python packages are listed in the *requirement.txt* file.

`pip install -r requirements.txt`

## Build the vectorstore database

The customized source documents can be from any website or the pdf files put in a folder called docs.

`python ingest.py`

This script uses the OPENAI_API_KEY, one can create an .env file and put the key inside.
## Run the chatbot interface
`chainlit run app.py -w`

## Test the chatbot
In the QAs.txt, there are predifined questions and answers related to the titantic data.
