import requests
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import yaml

class NASADataFetcher:
    def __init__(self, config_path: str = 'config/config.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.api_key = self.config['nasa']['api_key']

    def fetch_neo(self, asteroid_id: str) -> Optional[Dict[str, Any]]:
        """Fetch single asteroid data from NeoWS"""
        url = f"https://api.nasa.gov/neo/rest/v1/neo/{asteroid_id}?api_key={self.api_key}"
        return self._fetch_and_process(url, 'neo')

    def fetch_sbdb(self, asteroid_id: str) -> Optional[Dict[str, Any]]:
        """Fetch data from JPL Small-Body Database"""
        url = f"https://ssd-api.jpl.nasa.gov/sbdb.api?sstr={asteroid_id}"
        return self._fetch_and_process(url, 'sbdb')

    def fetch_close_approaches(self, days: int = 30) -> Optional[List[Dict[str, Any]]]:
        """Fetch close approach data from NeoWS feed (NOT DONKI)"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={self.api_key}"
        return self._fetch_and_process(url, 'feed')

    def _fetch_and_process(self, url: str, source_type: str) -> Optional[Dict[str, Any]]:
        try:
            logging.info(f"Fetching {source_type} data from: {url.split('?')[0]}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return self._process_data(response.json(), source_type)
        except Exception as e:
            logging.error(f"Failed to fetch {source_type}: {str(e)}")
            return None

    def _process_data(self, data: Dict[str, Any], source_type: str) -> Optional[Dict[str, Any]]:
        if source_type == 'neo':
            return self._process_neo_data(data)
        elif source_type == 'sbdb':
            return self._process_sbdb_data(data)
        elif source_type == 'feed':
            return self._process_feed_data(data)
        return None

    def _process_neo_data(self, response: Dict[str, Any]) -> Dict[str, Any]:
        close_approach = response['close_approach_data'][0]
        return {
            'id': str(response['id']),
            'name': response['name'],
            'diameter_km': response['estimated_diameter']['kilometers']['estimated_diameter_max'],
            'hazardous': response['is_potentially_hazardous_asteroid'],
            'orbital_eccentricity': float(response['orbital_data']['eccentricity']),
            'orbital_inclination': float(response['orbital_data']['inclination']),
            'orbital_period_yr': float(response['orbital_data']['orbital_period']),
            'orbital_semi_major_axis': float(response['orbital_data']['semi_major_axis']),
            'close_approach_date': close_approach['close_approach_date'],
            'miss_distance_km': float(close_approach['miss_distance']['kilometers']),
            'velocity_km_s': float(close_approach['relative_velocity']['kilometers_per_second'])
        }

    def _process_sbdb_data(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process JPL SBDB response to match our schema"""
        return {
            'id': response.get('object', {}).get('spkid', ''),
            'name': response.get('object', {}).get('fullname', ''),
            'orbit_class': response.get('object', {}).get('orbit_class', {}).get('description', ''),
            'source_data': response,  # Store raw response
            'data_source': 'sbdb'
        }

    def _process_feed_data(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        approaches = []
        for date in response.get('near_earth_objects', {}):
            for neo in response['near_earth_objects'][date]:
                for approach in neo['close_approach_data']:
                    approaches.append({
                        'id': neo['id'],
                        'name': neo['name'],
                        'date': approach['close_approach_date'],
                        'distance_km': float(approach['miss_distance']['kilometers']),
                        'velocity_km_s': float(approach['relative_velocity']['kilometers_per_second'])
                    })
        return approaches