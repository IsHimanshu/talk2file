
import os
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_community.document_loaders import (
    CSVLoader,
    NotebookLoader,
    PyPDFLoader,
    PythonLoader,
    TextLoader,
    UnstructuredEPubLoader,
    UnstructuredFileLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredODTLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
)
from langdetect import detect
from langchain_core.output_parsers import StrOutputParser
FILE_LOADER_MAPPING = {
    ".csv": (CSVLoader, {"encoding": "utf-8"}),
    ".doc": (UnstructuredWordDocumentLoader, {}),
    ".docx": (UnstructuredWordDocumentLoader, {}),
    ".epub": (UnstructuredEPubLoader, {}),
    ".html": (UnstructuredHTMLLoader, {}),
    ".md": (UnstructuredMarkdownLoader, {}),
    ".odt": (UnstructuredODTLoader, {}),
    ".pdf": (PyPDFLoader, {}),
    ".ppt": (UnstructuredPowerPointLoader, {}),
    ".pptx": (UnstructuredPowerPointLoader, {}),
    ".txt": (TextLoader, {"encoding": "utf8"}),
    ".ipynb": (NotebookLoader, {}),
    ".py": (PythonLoader, {}),
}
### define page content output formatter
def format_docs(docs):
    return "\n".join(doc.page_content for doc in docs)


# Function to convert text to embeddings
def text_to_embedding(text, model):
    embedding = model.encode(text, convert_to_tensor=False)
    return embedding.tolist()


def read_file_and_save_to_faiss(directory_name):
    documents = []

    for file in os.listdir(directory_name):
        file_path = os.path.join(directory_name, file)
        file_type = os.path.splitext(file)[1]
        if file_type == "":
            continue
        if file_type in FILE_LOADER_MAPPING:
            loader_class, loader_args = FILE_LOADER_MAPPING[file_type]
            loader = loader_class(file_path, **loader_args)
        else:
            loader = UnstructuredFileLoader(file_path)
        documents.extend(loader.load())

    print("files reading done")

    ### creating chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    all_splits = text_splitter.split_documents(documents)
    print("length of splits: ", len(all_splits))

    # Detect if content is Japanese
    sample_text = all_splits[0].page_content if all_splits else ""
    try:
        is_japanese = detect(sample_text) == 'ja'
    except:
        is_japanese = False

    ### prepare huggingface embedding model
    if is_japanese:
        model_name = "cl-nagoya/ruri-large"  # Ruri-large equivalent for Japanese
        print("Using Japanese-optimized embedding model")
    else:
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        print("Using default embedding model")

    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": False}
    embeddings_huggingFace = HuggingFaceEmbeddings(
        model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
    )

    ### create vectorstore database and convert text into embeddings and save them
    vectorstore = FAISS.from_documents(
        documents=all_splits, embedding=embeddings_huggingFace
    )
    print("vector db created for uploaded documents")

    return vectorstore