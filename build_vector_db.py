import sys
import os

# Add project root to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.rag.vector_store import create_vector_db
from src.core.logging import setup_logging

if __name__ == "__main__":
    setup_logging()
    print("Building Vector Database...")
    create_vector_db("inputs")
    print("Done.")
