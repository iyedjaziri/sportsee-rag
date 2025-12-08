
import os
import logging
from typing import List
from docling.document_converter import DocumentConverter

logger = logging.getLogger(__name__)

def convert_documents_to_markdown(input_dir: str, output_dir: str) -> List[str]:
    """
    Converts all documents in input_dir to Markdown in output_dir using Docling.
    Adapted from reference project P1C3_exercice.py using the Python API.
    """
    converted_files = []
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")

    logger.info(f"Converting documents from '{input_dir}' to '{output_dir}'...")
    
    converter = DocumentConverter()

    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        
        # Process only PDFs for now
        if os.path.isfile(input_path) and filename.lower().endswith(".pdf"):
            base_name = os.path.splitext(filename)[0]
            output_filename = f"{base_name}.md"
            output_path = os.path.join(output_dir, output_filename)
            
            logger.info(f"Processing '{filename}'...")
            
            try:
                result = converter.convert(input_path)
                md_content = result.document.export_to_markdown()
                
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                
                logger.info(f"Successfully converted '{filename}' to Markdown.")
                converted_files.append(output_path)

            except Exception as e:
                logger.error(f"Error converting '{filename}': {e}")
                
    return converted_files
