import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import logging
from datetime import datetime
from src.pipeline.fetch import NASADataFetcher
from src.pipeline.database import AsteroidDatabase

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='update.log'
)

def main():
    try:
        logging.info("Starting data update...")
        
        # Initialize components
        fetcher = NASADataFetcher()
        db = AsteroidDatabase()
        
        # 1. Update known NEOs
        sample_neos = ['3542519', '2000433', '2000719']
        for neo_id in sample_neos:
            if neo_data := fetcher.fetch_neo(neo_id):
                db.upsert_asteroid(neo_data)
            if sbdb_data := fetcher.fetch_sbdb(neo_id):
                db.upsert_asteroid(sbdb_data)
        
        # 2. Get recent close approaches (from NeoWS, not DONKI)
        if approaches := fetcher.fetch_close_approaches(days=7):
            logging.info(f"Found {len(approaches)} close approaches")
            # Store or process these as needed
        
        logging.info("Update completed successfully")
        
    except Exception as e:
        logging.error(f"Update failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()