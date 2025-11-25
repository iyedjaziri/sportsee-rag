import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from src.core.logging import logger
import os

def run_drift_analysis(current_data_path: str, reference_data_path: str, output_path: str = "data/drift_report.html"):
    """
    Generates a Data Drift report comparing current data to reference data.
    """
    logger.info("Starting Data Drift Analysis...")
    
    if not os.path.exists(current_data_path) or not os.path.exists(reference_data_path):
        logger.error("Data files not found.")
        return

    try:
        # Load data
        # Assuming Excel for now as per project, but could be CSV or SQL query result
        current_df = pd.read_excel(current_data_path, header=1) 
        reference_df = pd.read_excel(reference_data_path, header=1)
        
        # Simple preprocessing to ensure columns match
        # (In a real scenario, we'd share the schema logic from ingestion)
        
        report = Report(metrics=[
            DataDriftPreset(),
        ])
        
        report.run(reference_data=reference_df, current_data=current_df)
        
        report.save_html(output_path)
        logger.info(f"Drift report saved to {output_path}")
        
    except Exception as e:
        logger.exception(f"Error during drift analysis: {e}")

if __name__ == "__main__":
    # Example usage
    # We might not have 'reference' data yet, so we can simulate by splitting the current file
    # or just checking if files exist.
    pass
