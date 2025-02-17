"""
Changes:
- Embeddings handled with SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2") instead of OpenAI
- Only .pdf files 
"""

import os

from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

#from dotenv import load_dotenv
#load_dotenv()

embedding_function = SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2")

documents = []
relative_path = './docs/'

for file in os.listdir(relative_path):
    if file.endswith(".pdf"):
        pdf_path = os.path.join(relative_path, file)
        loader = PyMuPDFLoader(pdf_path)
        pdf_documents = loader.load()
        print(f"PDF {file} contains {len(pdf_documents)} documents.")
        documents.extend(pdf_documents)
    else:
        print("No .pdf files found.")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, separators=[" ", ",", "\n"]
)
split_documents = text_splitter.split_documents(documents)

vectordb = Chroma.from_documents(split_documents, embedding=embedding_function, persist_directory="./db")

print("Finished creating the chromadb.")

