from .fetch import NASADataFetcher
from .validate import validate_asteroid
from datetime import datetime
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import time

class DataUpdater:
    def __init__(self, config_path='config/config.yaml'):
        self.fetcher = NASADataFetcher(config_path)
        self.batch_size = 20  # Conservative batch size for API limits

    def run_update(self, full_refresh: bool = False) -> bool:
        """Main update routine"""
        try:
            # 1. Fetch all NEOs
            neos = self.fetcher.fetch_all_neos()
            if not neos:
                logging.error("No NEOs found in catalog")
                return False
            
            # 2. Process in batches
            success_count = 0
            for i in range(0, len(neos), self.batch_size):
                batch = neos[i:i + self.batch_size]
                logging.info(f"Processing batch {i//self.batch_size + 1}/{(len(neos)//self.batch_size)+1}")
                
                for neo in batch:
                    try:
                        complete_data = self.fetcher.fetch_neo_complete(neo)
                        if complete_data and (validated := validate_asteroid(complete_data)):
                            self.fetcher.db.upsert_asteroid(validated)
                            success_count += 1
                    except Exception as e:
                        logging.warning(f"Failed on {neo.get('id')}: {str(e)}")
                
                # Respect API rate limits
                time.sleep(5 if "DEMO_KEY" in self.fetcher.api_key else 1)
            
            logging.info(f"Updated {success_count}/{len(neos)} NEOs")
            return True
            
        except Exception as e:
            logging.critical(f"Update failed: {str(e)}")
            return False

def schedule_updates():
    scheduler = BlockingScheduler()
    updater = DataUpdater()
    
    @scheduler.scheduled_job('cron', hour=3)  # Daily at 3 AM
    def daily_update():
        logging.info("Starting scheduled update")
        updater.run_update()
        logging.info("Update completed")
    
    scheduler.start()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', action='store_true', help="Full refresh")
    parser.add_argument('--schedule', action='store_true', help="Enable scheduling")
    args = parser.parse_args()
    
    if args.schedule:
        schedule_updates()
    else:
        DataUpdater().run_update(full_refresh=args.full)