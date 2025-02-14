
"""
Changes:
- using Aitta for inference instead of OpenAI
- Embeddings handled with SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2") insted of OpenAI, since Aitta does not support embedding requests yet
- Trimmed the chat UI heavily since agent only uses db
"""

import os

from aitta_client import Model, Client, StaticAccessTokenSource
from langchain_community.chat_models import ChatOpenAI

from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

import chainlit as cl

#from dotenv import load_dotenv
#load_dotenv()

#Set up Aitta client (https://dev-aitta.2.rahtiapp.fi/page/client_guide)
poro_access_token = os.getenv("PORO_ACCESS_TOKEN") # get model specific token 
token_source = StaticAccessTokenSource(poro_access_token)
client = Client("https://api-dev-aitta.2.rahtiapp.fi", token_source)

model = Model.load("LumiOpen/Poro-34B-chat", client)
print(model.id)
print(model.openai_api_url)

llm = ChatOpenAI(
    temperature=0,
    model_name=model.id,  
    openai_api_key=token_source.get_access_token(), 
    base_url=model.openai_api_url,
    streaming=False 
)

"""llm = ChatOpenAI(
    temperature=0,
    model_name="LumiOpen/Poro-34B-chat",  
    openai_api_key=poro_access_token, 
    base_url="https://api-dev-aitta.2.rahtiapp.fi/model/LumiOpen~Poro-34B-chat/openai/v1/",
    streaming=False 
)"""

# testing Poro
"""response = llm.invoke("Kerro vitsi.")
print(response)"""

embedding_function = SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2")
persist_directory = './db'
vectordb = Chroma(persist_directory=persist_directory, 
                  embedding_function=embedding_function)

@cl.on_chat_start
async def on_chat_start():
    message_history = ChatMessageHistory()
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        chat_memory=message_history,
        return_messages=True,
    )

    agent_conversational = ConversationalRetrievalChain.from_llm(
        llm,
        retriever=vectordb.as_retriever(search_kwargs={'k': 4}),
        chain_type="stuff",
        memory=memory,
        return_source_documents=True
    )

    cl.user_session.set('agent_conversational', agent_conversational)
    await cl.Message(content="Chat initialized. You can start asking questions.").send()

@cl.on_message
async def main(message: cl.Message):
    agent_conversational = cl.user_session.get('agent_conversational')
    cb = cl.AsyncLangchainCallbackHandler()
    res = await agent_conversational.acall(message.content, callbacks=[cb])
    
    answer = res["answer"]
    source_documents = res["source_documents"]
    text_elements = []
    
    if source_documents:
        for source_idx, source_doc in enumerate(source_documents):
            source_name = f"source_{source_idx}"
            text_elements.append(
                cl.Text(content=source_doc.page_content, name=source_name, display="side")
            )
        source_names = [text_el.name for text_el in text_elements]
        answer += f"\nSources: {', '.join(source_names)}" if source_names else "\nNo sources found"
    
    await cl.Message(content=answer, elements=text_elements).send()