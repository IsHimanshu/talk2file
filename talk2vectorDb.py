import os
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import AzureChatOpenAI
from langchain_community.vectorstores import FAISS
from langdetect import detect
import getpass
from dotenv import load_dotenv
import os

load_dotenv()
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
# def setup_dll_paths():
#     try:
#         os.add_dll_directory("C:/Program Files/MeCab/bin")
#         print("MeCab DLL directory added successfully")
#     except Exception as e:
#         print(f"Warning: Could not add  DLL directory: {e}")

# # Call this function when importing this module
# setup_dll_paths()



### initalising the llm 
llm = AzureChatOpenAI(

azure_deployment="gpt-4o", # or your deployment

api_version="2024-10-01-preview", # or your api version

temperature=0,

max_tokens=None,

timeout=None,

max_retries=2,

model="gpt-4o",)


### define page content output formatter
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def retrieve_answers_from_faiss(vectorstore, question):
    ### create retriever from the database define its parameters
    print(vectorstore)
    retriever = vectorstore.as_retriever(
        search_type="similarity", search_kwargs={"k": 6}
    )

    # Detect if question is in Japanese
    try:
        is_japanese = detect(question) == 'ja'
    except:
        is_japanese = False

    ### create prompt template
    if is_japanese:
        template = """以下の文脈を使用して、最後の質問に答えてください。
        答えがわからない場合は、わからないとだけ言ってください。答えを作り上げようとしないでください。
        回答は簡潔にしてください。
        
        文脈:
        {context}
        
        質問: {question}
        
        回答:"""
    else:
        template = """Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        keep the answer as concise as possible.
        {context}
        Question: {question}
        Helpful Answer:"""

    custom_rag_prompt = PromptTemplate.from_template(template)
    print("prompt created")
    
    ### create chain of events
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | custom_rag_prompt
        | llm
        | StrOutputParser()
    )
    print(rag_chain)
    
    ### calling the chain using invoke method
    return rag_chain.invoke(question)