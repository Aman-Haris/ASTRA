#!/usr/bin/env python3
"""
ASTRA - Complete Asteroid Data Pipeline
1. Fetch → 2. Validate → 3. Store → 4. Preprocess
"""

import logging
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.pipeline.update import DataUpdater
from src.pipeline.preprocess import NEOPreprocessor

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/pipeline.log'),
            logging.StreamHandler()
        ]
    )

def run_pipeline(full_refresh: bool = False) -> bool:
    """Run complete data pipeline"""
    try:
        start_time = datetime.now()
        logging.info("Starting ASTRA pipeline")
        
        # 1. Data acquisition and update
        if not DataUpdater().run_update(full_refresh):
            return False
        
        # 2. Preprocessing
        processor = NEOPreprocessor()
        if not processor.preprocess_from_db(output_format='parquet'):
            return False
            
        duration = datetime.now() - start_time
        logging.info(f"Pipeline completed in {duration}")
        return True
        
    except Exception as e:
        logging.critical(f"Pipeline failed: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    configure_logging()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', action='store_true', help="Full refresh")
    args = parser.parse_args()
    
    success = run_pipeline(full_refresh=args.full)
    sys.exit(0 if success else 1)