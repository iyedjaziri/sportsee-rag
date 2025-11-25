import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.core.config import settings
from src.core.logging import logger

VECTOR_DB_PATH = "data/faiss_index"

def create_vector_db(data_path: str = "inputs"):
    """
    Ingests PDF documents from data_path and creates a FAISS index.
    """
    if not os.path.exists(data_path):
        logger.warning(f"Data path {data_path} does not exist.")
        return None

    logger.info(f"Loading documents from {data_path}...")
    loader = DirectoryLoader(data_path, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    
    if not documents:
        logger.warning("No documents found.")
        return None

    logger.info(f"Loaded {len(documents)} documents. Splitting...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    texts = text_splitter.split_documents(documents)
    
    logger.info(f"Created {len(texts)} chunks. Embedding and indexing...")
    embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
    vectorstore = FAISS.from_documents(texts, embeddings)
    
    vectorstore.save_local(VECTOR_DB_PATH)
    logger.info(f"Vector store saved to {VECTOR_DB_PATH}")
    return vectorstore

def get_vector_store():
    """
    Loads the FAISS index from disk.
    """
    embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
    if os.path.exists(VECTOR_DB_PATH):
        return FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
    else:
        logger.warning("Vector store not found. Creating new one...")
        return create_vector_db()

def get_retriever():
    vectorstore = get_vector_store()
    if vectorstore:
        return vectorstore.as_retriever(search_kwargs={"k": 4})
    return None
