#from langchain.document_loaders import TextLoader, PyPDFLoader, CSVLoader, WebBaseLoader
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader,CSVLoader, WebBaseLoader
from langchain.docstore.document import Document
import os
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter,RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

#from web_scrape import *
from web import *

os.environ["OPENAI_API_KEY"] = "your-openai-key"

documents = []
relative_path = '../docs/'
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


webs = [#"https://www.tuni.fi/fi/ajankohtaista/soumya-tripathy-generative-ai-models-enhance-advanced-image-manipulation?navref=curated--grid",
        #"https://shanwangshan.github.io/shanshanwang",
    #"https://blade6570.github.io/soumyatripathy/",

        "https://jessepharrison.github.io/",
        #"https://sites.google.com/view/dr-dev/home",
    #"https://www.iiti.ac.in/people/~puneet/"


        ]
for web in webs:
    loader = RecursiveWebLoader(base_url=web, depth=1)
    scraped_data = loader.load()


    documents.extend(create_langchain_docs(scraped_data))
    # if "tuni" in web:

    #     scraped_data = scrape_website(web, max_depth=1)
    # else:
    #     scraped_data = scrape_website(web, max_depth=2)
    # web_doc = create_langchain_docs(scraped_data)
    # documents.extend(web_doc)
# for doc in documents:
#     print(f"Document from {doc.metadata['source']}:\n{doc.page_content[:500]}...")  # Print first 500 characters


#breakpoint()
text_splitter = RecursiveCharacterTextSplitter(
chunk_size=1000, chunk_overlap=200, separators=[" ", ",", "\n"]
) # degault values is 1000. 200
#breakpoint()
#text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
split_documents = text_splitter.split_documents(documents)


vectordb = Chroma.from_documents(split_documents, embedding=OpenAIEmbeddings(), persist_directory="./db")
vectordb.persist()



# from langchain_community.vectorstores import FAISS
# import faiss
# vectorstore = FAISS.from_documents(split_documents, embedding =OpenAIEmbeddings() )
# vectorstore.save_local("faiss_index")
