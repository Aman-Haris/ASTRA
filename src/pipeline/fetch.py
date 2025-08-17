import requests
import logging
from datetime import datetime, timedelta, time
from typing import Optional, Dict, List
import yaml
from tenacity import retry, stop_after_attempt, wait_exponential
from .database import AsteroidDatabase

class NASADataFetcher:
    def __init__(self, config_path='config/config.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.apis = {
            'neows': self.config['nasa']['endpoints']['neows'],
            'sbdb': "https://ssd-api.jpl.nasa.gov/sbdb.api",
            'cad': "https://ssd-api.jpl.nasa.gov/cad.api"
        }
        self.api_key = self.config['nasa']['api_key']
        self.db = AsteroidDatabase(config_path)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_all_neos(self) -> List[Dict]:
        """Fetch all NEOs using paginated browse API"""
        all_neos = []
        page = 0
        
        while True:
            try:
                url = f"{self.apis['neows']}browse?page={page}&size=20&api_key={self.api_key}"
                data = self._make_request(url)
                
                if not data or 'near_earth_objects' not in data:
                    break
                    
                all_neos.extend(data['near_earth_objects'])
                
                if page >= data['page']['total_pages'] - 1:
                    break
                    
                page += 1
                time.sleep(2 if "DEMO_KEY" in self.api_key else 0.2)
                
            except Exception as e:
                logging.error(f"Error in fetch_all_neos: {str(e)}")
                break

        return all_neos

    def fetch_neo_complete(self, neo: Dict) -> Optional[Dict]:
        """Get unified asteroid data from all APIs"""
        try:
            neo_id = neo['id']
            
            # 1. NeoWS detailed data
            neo_data = self._fetch_neows_detail(neo_id)
            if not neo_data:
                return None

            # 2. SBDB orbital data
            sbdb_data = self._fetch_sbdb_data(neo_id)
            
            # 3. CAD approach data
            cad_data = self._fetch_cad_data(neo_id, years=100)
            
            # Combine all data
            combined = {
                **neo_data,
                'sbdb_data': sbdb_data,
                'cad_data': cad_data,
                'data_sources': 'neows,sbdb,cad',
                'orbit_class': sbdb_data.get('orbit_class', {}).get('name', '') if sbdb_data else '',
                'close_approach_count': len(cad_data) if cad_data else 0
            }
            
            # Add next approach if available
            if cad_data:
                next_approach = min(cad_data, key=lambda x: x['cd'])
                combined.update({
                    'next_approach_date': datetime.strptime(next_approach['cd'], "%Y-%b-%d %H:%M"),
                    'next_approach_distance_km': float(next_approach['dist']) * 149597870.7,
                    'next_approach_velocity': float(next_approach['v_rel'])
                })
            
            return combined
            
        except Exception as e:
            logging.error(f"Failed to fetch complete data for {neo_id}: {str(e)}")
            return None

    def _fetch_neows_detail(self, neo_id: str) -> Optional[Dict]:
        url = f"{self.apis['neows']}/neo/{neo_id}?api_key={self.api_key}"
        data = self._make_request(url)
        if not data:
            return None
            
        return {
            'id': str(data['id']),
            'name': data['name'],
            'diameter_km': data['estimated_diameter']['kilometers']['estimated_diameter_max'],
            'hazardous': data['is_potentially_hazardous_asteroid'],
            'neows_data': data
        }

    def _fetch_sbdb_data(self, neo_id: str) -> Optional[Dict]:
        url = f"{self.apis['sbdb']}?sstr={neo_id}"
        return self._make_request(url)

    def _fetch_cad_data(self, neo_id: str, years: int = 100) -> Optional[List[Dict]]:
        params = {
            'des': neo_id,
            'date-min': '1900-01-01',  # Full historical data
            'date-max': (datetime.now() + timedelta(days=365*years)).strftime("%Y-%m-%d"),
            'diameter': 'true'
        }
        url = f"{self.apis['cad']}?{'&'.join(f'{k}={v}' for k,v in params.items())}"
        response = self._make_request(url)
        return response.get('data', []) if response else []

    def _make_request(self, url: str) -> Optional[Dict]:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Request failed: {url} - {str(e)}")
            return None