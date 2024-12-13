import os
#from langchain_openai import ChatOpenAI
from langchain.chat_models import ChatOpenAI

#from langchain_openai import OpenAIEmbeddings
from langchain.embeddings import OpenAIEmbeddings

#from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain.chains import ConversationalRetrievalChain
#from langchain.chains import ConversationChain

import chainlit as cl
from pandasai import Agent
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory import  ConversationBufferMemory
#from langchain.vectorstores import FAISS
from chainlit.input_widget import Select
#from langchain_community.vectorstores import FAISS
#import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
#from pandasai.llm.openai import OpenAI
from pandasai import SmartDataframe
import pandas as pd
#from pandasai import PandasAI
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
embeddings = OpenAIEmbeddings()

persist_directory = './db'
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

model = "gpt-3.5-turbo"
#model = "gpt-4"

llm = ChatOpenAI(temperature=0, model_name=model,openai_api_key=openai_api_key,streaming=True)

@cl.on_chat_start
async def on_chat_start():

    files = None

    # Wait for the user to upload a file
    while files == None:
        files = await cl.AskFileMessage(
            content="Please upload a csv file to begin!", accept=["text/csv"]
        ).send()

    file = files[0]
    #print(file)
    df = pd.read_csv(file.path)
    agent_pandas = SmartDataframe(df, config={"llm": llm})
    #agent_pandas = Agent(file.path,config={"llm": llm})


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
#        retriever=vectordb.as_retriever( max_tokens_limit=10000, top_n=4),
        chain_type="stuff",
        memory=memory,
    return_source_documents=True)
    # Let the user know that the system is ready
    cl.user_session.set('data', (df, agent_pandas, agent_conversational))
    cl.user_session.set('current_agent', 'pandas')  # Default agent

    # Provide instructions for agent selection
    msg = cl.Message(content=(
        f"Processed `{file.name}`. Choose an agent to interact with by typing one of the following commands:\n"
        "`use agent pandas` - Switch to PandasAI Agent\n"
        "`use agent conversational` - Switch to Conversational Agent"
    ))
    await msg.send()




@cl.on_message
async def main(message: cl.Message):

    df, agent_pandas, agent_conversational = cl.user_session.get('data')
    if message.content.lower().startswith('use agent'):
        agent_choice = message.content.split(' ')[-1].lower()
        if agent_choice == 'pandas':
            cl.user_session.set('current_agent', 'pandas')
            await cl.Message(content="Switched to PandasAI agent. You can now ask questions related to data.").send()
        elif agent_choice == 'conversational':
            cl.user_session.set('current_agent', 'conversational')
            await cl.Message(content="Switched to the conversational agent. You can now ask general questions.").send()
        else:
            await cl.Message(content="Invalid agent. Please type 'use agent pandas' or 'use agent conversational'.").send()
        return
    current_agent = cl.user_session.get('current_agent', 'pandas')  # Default to 'pandas' if no agent is selected
    #current_agent = cl.user_session.get("agents")
    print(current_agent)

    if current_agent == 'pandas':

        question = message.content
        response = agent_pandas.chat(question)

        print('this is the response:', response)

        if str(response).endswith('.png'):
            image = cl.Image(path="./exports/charts/temp_chart.png", name="image", display="inline")
            await cl.Message(content="This message has an image!",elements=[image] ).send()
            #os.remove("./exports/charts/temp_chart.png")


        else:
            await cl.Message(content=response).send()


    elif current_agent == 'conversational':
        chain = agent_conversational

        #chain = cl.user_session.get("chain")  # type: ConversationalRetrievalChain
        cb = cl.AsyncLangchainCallbackHandler()

        res = await chain.acall(message.content, callbacks=[cb])
        answer = res["answer"]
        source_documents = res["source_documents"]  # type: List[Document]

        text_elements = []  # type: List[cl.Text]

        if source_documents:
            for source_idx, source_doc in enumerate(source_documents):
                source_name = f"source_{source_idx}"
                # Create the text element referenced in the message
                text_elements.append(
                    cl.Text(content=source_doc.page_content, name=source_name, display="side")
                )
            source_names = [text_el.name for text_el in text_elements]

            if source_names:
                answer += f"\nSources: {', '.join(source_names)}"
            else:
                answer += "\nNo sources found"

        await cl.Message(content=answer, elements=text_elements).send()
