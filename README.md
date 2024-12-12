# simple_chatbot

This is a simple chatbot repo which could answer questions related to the customized documents and a uploaded csv file.

## Environment requirement
All the required python packages are listed in the *requirement.txt* file.

`pip install -r requirements.txt`

## build the vectorstore database from the customized source documents, which can be any website or the pdfs filed in the *doc* folder.
`python ingest.py`

## run the chatbot interface
`chainlit run app.py -w`