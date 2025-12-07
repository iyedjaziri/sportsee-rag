import sys
import os
import logging

# Add project root to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.rag.vector_store import create_vector_db
from src.core.logging import setup_logging, logger

def build_database(input_dir: str = "inputs"):
    """
    Orchestrates the creation of the vector database.
    """
    logger.info(f"Starting Vector Database build from directory: {input_dir}")
    
    if not os.path.exists(input_dir):
        logger.error(f"Input directory '{input_dir}' does not exist.")
        return

    try:
        create_vector_db(input_dir)
        logger.info("Vector Database built successfully.")
    except Exception as e:
        logger.exception(f"Failed to build Vector Database: {e}")
        raise

if __name__ == "__main__":
    setup_logging()
    build_database()
