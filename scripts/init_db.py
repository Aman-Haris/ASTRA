import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.pipeline.database import AsteroidDatabase

if __name__ == "__main__":
    db = AsteroidDatabase()
    db.init_db()
    print("Database tables created successfully")