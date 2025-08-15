from sqlalchemy import create_engine, Column, Float, String, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import yaml
from datetime import datetime

Base = declarative_base()

class Asteroid(Base):
    __tablename__ = 'asteroids'
    
    # Core fields (required)
    id = Column(String, primary_key=True)
    name = Column(String)
    diameter_km = Column(Float)
    hazardous = Column(Boolean)
    orbital_eccentricity = Column(Float)
    orbital_inclination = Column(Float)
    orbital_period_yr = Column(Float)
    orbital_semi_major_axis = Column(Float)
    
    # Close approach fields
    close_approach_date = Column(DateTime)
    miss_distance_km = Column(Float)
    velocity_km_s = Column(Float)
    
    # Extended fields (optional)
    orbit_class = Column(String)  # Added this field
    source_data = Column(JSON)    # For storing raw API responses
    
    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow)
    data_source = Column(String)  # 'neows', 'sbdb', etc.

class AsteroidDatabase:
    def __init__(self, config_path='config/config.yaml'):
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        db_config = config['database']['postgresql']
        self.engine = create_engine(
            f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
        )
        self.Session = sessionmaker(bind=self.engine)
    
    def init_db(self):
        Base.metadata.create_all(self.engine)
    
    def upsert_asteroid(self, data: dict):
        session = self.Session()
        
        # Filter only valid columns for Asteroid model
        valid_columns = {c.name for c in Asteroid.__table__.columns}
        filtered_data = {k: v for k, v in data.items() if k in valid_columns}
        
        # Store raw data in source_data if needed
        if 'source_data' not in filtered_data:
            filtered_data['source_data'] = data
        
        asteroid = session.query(Asteroid).filter_by(id=data['id']).first()
        if not asteroid:
            asteroid = Asteroid(**filtered_data)
            session.add(asteroid)
        else:
            for key, value in filtered_data.items():
                setattr(asteroid, key, value)
        
        session.commit()
        session.close()