from sqlalchemy import create_engine, Column, Float, String, Boolean, DateTime, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import yaml
from datetime import datetime

Base = declarative_base()

class Asteroid(Base):
    __tablename__ = 'asteroids'
    
    # Core identification
    id = Column(String, primary_key=True)
    name = Column(String)
    designation = Column(String)
    
    # Physical characteristics
    diameter_km = Column(Float)
    absolute_magnitude = Column(Float)
    hazardous = Column(Boolean)
    
    # Orbital parameters (from SBDB)
    orbital_eccentricity = Column(Float)
    orbital_inclination = Column(Float)
    orbital_period_yr = Column(Float)
    orbital_semi_major_axis = Column(Float)
    orbit_class = Column(String)
    
    # Close approach data (from CAD)
    next_approach_date = Column(DateTime)
    next_approach_distance_km = Column(Float)
    next_approach_velocity = Column(Float)
    close_approach_count = Column(Integer)
    
    # Derived metrics
    tisserand = Column(Float)
    palermo_scale = Column(Float)
    torino_scale = Column(Integer)
    orbit_cluster = Column(Integer)
    
    # Raw data storage
    neows_data = Column(JSON)
    sbdb_data = Column(JSON)
    cad_data = Column(JSON)
    
    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow)
    data_sources = Column(String)

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
        
        asteroid = session.query(Asteroid).filter_by(id=data['id']).first()
        if not asteroid:
            asteroid = Asteroid(**data)
            session.add(asteroid)
        else:
            for key, value in data.items():
                setattr(asteroid, key, value)
        
        session.commit()
        session.close()