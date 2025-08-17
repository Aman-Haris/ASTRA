from pydantic import BaseModel, field_validator, Field
from typing import Optional, Dict, List, Annotated
from datetime import datetime
import logging
import numpy as np

class AsteroidSchema(BaseModel):
    id: str
    name: str
    designation: Optional[str] = None
    diameter_km: Optional[Annotated[float, Field(gt=0, le=1000)]] = None
    absolute_magnitude: Optional[float] = None
    hazardous: bool
    
    # Orbital parameters
    orbital_eccentricity: Optional[Annotated[float, Field(ge=0, lt=1)]] = None
    orbital_inclination: Optional[Annotated[float, Field(ge=0, le=180)]] = None
    orbital_semi_major_axis: Optional[Annotated[float, Field(gt=0)]] = None
    orbit_class: Optional[str] = None
    
    # Close approach data
    next_approach_date: Optional[datetime] = None
    next_approach_distance_km: Optional[Annotated[float, Field(gt=0)]] = None
    next_approach_velocity: Optional[Annotated[float, Field(gt=0)]] = None
    close_approach_count: Optional[int] = None
    
    # Raw data storage
    neows_data: Optional[Dict] = None
    sbdb_data: Optional[Dict] = None
    cad_data: Optional[List[Dict]] = None
    
    @field_validator('cad_data')
    @classmethod
    def validate_cad_data(cls, v):
        if v and len(v) > 1000:  # Prevent excessively large datasets
            return v[:1000]
        return v

def validate_asteroid(data: dict) -> Optional[dict]:
    try:
        validated = AsteroidSchema(**data).model_dump(exclude_none=True)
        
        # Calculate derived fields
        if all(k in validated for k in ['orbital_semi_major_axis', 'orbital_eccentricity', 'orbital_inclination']):
            validated['tisserand'] = calculate_tisserand(
                validated['orbital_semi_major_axis'],
                validated['orbital_eccentricity'],
                validated['orbital_inclination']
            )
        
        return validated
    except Exception as e:
        logging.error(f"Validation failed for {data.get('id')}: {str(e)}")
        return None

def calculate_tisserand(a: float, e: float, i: float) -> float:
    a_jupiter = 5.2
    return (a_jupiter / a) + 2 * np.cos(np.radians(i)) * np.sqrt((a / a_jupiter) * (1 - e**2))