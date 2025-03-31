"""
Changes:
- Embeddings handled with SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2") instead of OpenAI
- Only .pdf files
31-3-2025: Embeddings through Aitta
"""

import os
from aitta_client import Model, Client, StaticAccessTokenSource
import openai
from chromadb import Documents, EmbeddingFunction, Embeddings

from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

#from dotenv import load_dotenv
#load_dotenv()

documents = []
relative_path = './docs/'

poro_access_token = os.getenv("PORO_ACCESS_TOKEN")
token_source = StaticAccessTokenSource(poro_access_token)
aitta_client = Client("https://api-dev-aitta.2.rahtiapp.fi", token_source)

model = Model.load("LumiOpen/Poro-34B-chat", aitta_client)
client = openai.OpenAI(api_key=token_source.get_access_token(), base_url=model.openai_api_url)

class AittaEmbeddings(EmbeddingFunction):
    def __init__(self, client, model_id):
        self.client = client
        self.model_id = model_id

    def embed_documents(self, texts: Documents) -> Embeddings:
        """Embed a list of documents."""
        response = self.client.embeddings.create(
            input=texts,
            model=self.model_id
        )
        return [data.embedding for data in response.data]

embedding_function = AittaEmbeddings(client, model.id)

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

persist_directory = "./db"
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)
vectordb.add_documents(split_documents)

print("Finished creating the chromadb.")

