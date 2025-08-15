from .fetch import NASADataFetcher
import pandas as pd
from datetime import datetime, timedelta

class DataUpdater:
    def __init__(self):
        self.fetcher = NASADataFetcher()
    
    def update_all(self):
        # Get list of known NEOs from NASA's feed
        self._update_known_neos()
        
        # Update close approach data
        date_range = self._get_date_range()
        self.fetcher.fetch_cad(date_range)
    
    def _update_known_neos(self):
        # In a real implementation, you'd fetch the list of NEOs
        # For now we'll use a sample list
        sample_neos = ['3542519', '2000433', '2000719']
        
        for neo_id in sample_neos:
            self.fetcher.fetch_neo(neo_id)
            self.fetcher.fetch_sbdb(neo_id)
    
    def _get_date_range(self):
        today = datetime.now().strftime("%Y-%m-%d")
        next_year = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        return f"{today}..{next_year}"