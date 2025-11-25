import sys
import os

# Add project root to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.ingestion import ingest_data
from src.core.logging import setup_logging

if __name__ == "__main__":
    setup_logging()
    
    input_file = "data/raw/regular_NBA.xlsx"
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found.")
        sys.exit(1)
        
    ingest_data(input_file)
