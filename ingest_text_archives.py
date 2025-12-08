import os
import re
import logging
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ValidationError
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_mistralai import MistralAIEmbeddings
from langchain_core.documents import Document

from src.core.config import settings
from src.core.logging import setup_logging, logger

# Setup logging
setup_logging()

# --- Configuration ---
INPUTS_DIR = "inputs"
VECTOR_DB_PATH = "vector_db/faiss_index" # Match the path expected by vector_store.py

# --- Pydantic Models for Validation ---
class ChunkMetadata(BaseModel):
    source: str
    page: int
    match_id: Optional[str] = None
    category: str = "archive"

class ChunkData(BaseModel):
    """
    Validates a single chunk of text before ingestion.
    """
    text: str = Field(..., min_length=10, description="The cleaned text content")
    metadata: ChunkMetadata

# --- Cleaning Function ---
def clean_text(text: str) -> str:
    """
    Cleans noise from Reddit/Social Media threads.
    """
    # Remove "Posted by u/username"
    text = re.sub(r"Posted by u/[\w\-]+\s*", "", text)
    # Remove timestamps like "2 hours ago", "1 day ago" (heuristic)
    text = re.sub(r"\d+\s+(hours?|days?|minutes?|months?|years?)\s+ago", "", text)
    # Remove generic "share save hide report" links often found in print-to-pdf
    text = re.sub(r"share\s+save\s+hide\s+report", "", text, flags=re.IGNORECASE)
    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text.strip()

# --- Ingestion Pipeline ---
# ... imports ...
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from src.utils.docling_converter import convert_documents_to_markdown

# ... config ...
TEMP_MD_DIR = "temp_markdown"

# ... (models and clean_text remain mostly same, maybe less regex needed)

def ingest_archives():
    logger.info("Starting ingestion pipeline for text archives...")

    if not os.path.exists(INPUTS_DIR):
        logger.error(f"Inputs directory '{INPUTS_DIR}' does not exist.")
        return

    # 1. Detect Markdown files in inputs
    logger.info("Checking for existing Markdown files in inputs...")
    md_files = [os.path.join(INPUTS_DIR, f) for f in os.listdir(INPUTS_DIR) if f.lower().endswith(".md")]
    
    if not md_files:
        logger.warning(f"No Markdown files found in {INPUTS_DIR}. Aborting.")
        return

    # 2. Process: Load MD -> Clean -> Validate -> List[Document]
    logger.info(f"Loading {len(md_files)} markdown files...")
    valid_documents = []
    
    for md_file in md_files:
        try:
            # Load Markdown
            loader = UnstructuredMarkdownLoader(md_file)
            docs = loader.load()
            
            for doc in docs:
                # Docling markdown is usually high quality, but we still clean specific Reddit noise
                cleaned_content = clean_text(doc.page_content)
                
                # Extract basic metadata
                source_file = os.path.basename(md_file).replace(".md", ".pdf") # Trace back to PDF
                
                # Prepare data for validation
                data_to_validate = {
                    "text": cleaned_content,
                    "metadata": {
                        "source": source_file,
                        "page": 1, # Markdown loses page numbers usually, default to 1
                        "category": "reddit_archive"
                    }
                }

                try:
                    # Validate with Pydantic
                    validated_chunk = ChunkData(**data_to_validate)
                    
                    # Create LangChain Document
                    valid_documents.append(
                        Document(
                            page_content=validated_chunk.text,
                            metadata=validated_chunk.metadata.model_dump()
                        )
                    )
                except ValidationError as e:
                    logger.warning(f"Skipping invalid chunk from {source_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Error processing markdown file {md_file}: {e}")

    if not valid_documents:
        logger.warning("No valid documents to process after cleaning and validation.")
        return

    # 3. Semantic Chunking
    # ... (rest of the function same as before)
    logger.info("Splitting text into semantic chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    final_chunks = text_splitter.split_documents(valid_documents)
    # ...
    
    # 4. Embed and Store
    # ... (rest same as before)
    logger.info("Embedding and indexing into FAISS (Mistral)...")
    try:
        embeddings = MistralAIEmbeddings(
            api_key=settings.MISTRAL_API_KEY,
            model="mistral-embed"
        )
        
        vectorstore = FAISS.from_documents(final_chunks, embeddings)
        
        os.makedirs(os.path.dirname(VECTOR_DB_PATH), exist_ok=True)
        # Note: VectorStoreManager in reference used "vector_db" root.
        # We stick to saving to "vector_db" folder index name "faiss_index" if compatible.
        # But vector_store.py loads from "vector_db". FAISS.save_local("path") creates index.faiss inside "path".
        # So we save to "vector_db".
        
        vectorstore.save_local("vector_db") 
        logger.info(f"Vector store successfully saved to 'vector_db/'")
        
    except Exception as e:
        logger.error(f"Error creating vector store: {e}")


if __name__ == "__main__":
    if not settings.MISTRAL_API_KEY:
        logger.error("MISTRAL_API_KEY is not set. Cannot generate embeddings.")
    else:
        ingest_archives()
