import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import datetime
import yaml
from typing import Optional

def calculate_tisserand(a: float, e: float, i: float) -> float:
    """Compute Tisserand parameter w.r.t. Jupiter"""
    a_jupiter = 5.2  # AU
    return (a_jupiter / a) + 2 * np.cos(np.radians(i)) * np.sqrt((a / a_jupiter) * (1 - e**2))

def calculate_threat_score(row: pd.Series) -> float:
    """Simplified threat score based on diameter, velocity, and distance"""
    return (row['diameter_km'] * row['velocity_km_s']) / (row['miss_distance_km'] + 1e-6)

class NEOPreprocessor:
    def __init__(self, config_path: str = 'config/config.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        db_config = self.config['database']['postgresql']
        self.engine = create_engine(
            f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
        )

    def preprocess_from_db(self, output_format: str = 'csv') -> Optional[pd.DataFrame]:
        """Load and preprocess data directly from database"""
        try:
            # Load raw data
            query = """
                SELECT * FROM asteroids 
                WHERE last_updated > NOW() - INTERVAL '1 year'
                ORDER BY close_approach_date DESC
            """
            df = pd.read_sql(query, self.engine)

            # Feature engineering
            df['tisserand'] = df.apply(
                lambda x: calculate_tisserand(
                    x['orbital_semi_major_axis'],
                    x['orbital_eccentricity'],
                    x['orbital_inclination']
                ), axis=1
            )

            df['threat_score'] = df.apply(calculate_threat_score, axis=1)
            df['palermo_scale'] = np.log10(df['threat_score'])  # Simplified
            df['torino_scale'] = pd.cut(
                df['threat_score'],
                bins=[0, 1, 10, 100, 1000, float('inf')],
                labels=[0, 1, 2, 3, 4]
            )

            # Save processed data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if output_format == 'csv':
                output_path = f"data/processed/neo_processed_{timestamp}.csv"
                df.to_csv(output_path, index=False)
            elif output_format == 'parquet':
                output_path = f"data/processed/neo_processed_{timestamp}.parquet"
                df.to_parquet(output_path)
            
            print(f"✅ Processed data saved to {output_path}")
            return df

        except Exception as e:
            print(f"🚨 Preprocessing error: {e}")
            return None

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help="Database (ignored when using --db)")
    parser.add_argument('--output-format', default='csv', choices=['csv', 'parquet'])
    args = parser.parse_args()
    
    processor = NEOPreprocessor()
    processor.preprocess_from_db(args.output_format)