from langchain_community.document_loaders import TextLoader, PyMuPDFLoader,CSVLoader, WebBaseLoader
from langchain.docstore.document import Document
import os
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter,RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from web import *
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

documents = []
relative_path = './docs/'
for file in os.listdir(relative_path):
    if file.endswith(".pdf"):
        pdf_path = relative_path + file
        loader = PyMuPDFLoader(pdf_path)
        documents.extend(loader.load())
    elif file.endswith('.docx') or file.endswith('.doc'):
        doc_path = relative_path + file
        loader = Docx2txtLoader(doc_path)
        documents.extend(loader.load())
    elif file.endswith('.txt'):
        text_path = relative_path + file
        loader = TextLoader(text_path)
        documents.extend(loader.load())
    elif file.endswith('.csv_'):
        csv_path = relative_path + file
        loader = CSVLoader(csv_path)
        documents.extend(loader.load())


webs = ["https://shanwangshan.github.io/shanshanwang",
        "https://jessepharrison.github.io/"
        ]
for web in webs:
    loader = RecursiveWebLoader(base_url=web, depth=1)
    scraped_data = loader.load()
    documents.extend(create_langchain_docs(scraped_data))

#breakpoint()
text_splitter = RecursiveCharacterTextSplitter(
chunk_size=1000, chunk_overlap=200, separators=[" ", ",", "\n"]
) # default values is 1000. 200
split_documents = text_splitter.split_documents(documents)

vectordb = Chroma.from_documents(split_documents, embedding=OpenAIEmbeddings(openai_api_key=openai_api_key), persist_directory="./db")
vectordb.persist()
