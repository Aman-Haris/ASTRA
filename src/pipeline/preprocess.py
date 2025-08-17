import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import logging
from typing import Optional
from .database import AsteroidDatabase
from datetime import datetime

class NEOPreprocessor:
    def __init__(self, config_path='config/config.yaml'):
        self.db = AsteroidDatabase(config_path)
        self.scaler = StandardScaler()

    def preprocess_from_db(self, output_format: str = 'parquet') -> Optional[pd.DataFrame]:
        try:
            # Load from database
            query = """
                SELECT * FROM asteroids 
                WHERE last_updated > NOW() - INTERVAL '1 year'
            """
            df = pd.read_sql(query, self.db.engine)
            
            if df.empty:
                raise ValueError("No asteroids found in database")
            
            # Feature engineering
            df = self._calculate_features(df)
            df = self._cluster_orbits(df)
            
            # Save processed data
            self._save_data(df, output_format)
            return df
            
        except Exception as e:
            logging.error(f"Preprocessing failed: {str(e)}")
            return None

    def _calculate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate threat scores and derived metrics"""
        # Threat score based on next approach
        df['threat_score'] = (df['diameter_km'] * df['next_approach_velocity']) / (df['next_approach_distance_km'] + 1e-6)
        
        # Palermo scale (logarithmic)
        df['palermo_scale'] = np.log10(df['threat_score'].clip(lower=1e-6))
        
        # Torino scale (binned)
        bins = [-np.inf, 0.1, 1, 10, 100, np.inf]
        labels = [0, 1, 2, 3, 4]
        df['torino_scale'] = pd.cut(df['threat_score'], bins=bins, labels=labels)
        
        return df

    def _cluster_orbits(self, df: pd.DataFrame, n_clusters: int = 5) -> pd.DataFrame:
        """Cluster asteroids by orbital parameters"""
        features = ['orbital_semi_major_axis', 'orbital_eccentricity', 'orbital_inclination']
        X = self.scaler.fit_transform(df[features].fillna(0))
        df['orbit_cluster'] = KMeans(n_clusters=n_clusters).fit_predict(X)
        return df

    def _save_data(self, df: pd.DataFrame, output_format: str):
        path = f"data/processed/asteroids_{datetime.now().strftime('%Y%m%d')}.{output_format}"
        if output_format == 'parquet':
            df.to_parquet(path)
        else:
            df.to_csv(path, index=False)
        logging.info(f"Saved processed data to {path}")