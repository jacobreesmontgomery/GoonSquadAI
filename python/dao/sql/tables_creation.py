from models.athlete import Base, Athlete
from models.activity import Activity
from services.database import DatabaseService

# Create the database service
db_service = DatabaseService()
engine = db_service.engine

# Create the tables
try:
    Base.metadata.create_all(engine)
    print("Tables created successfully!")
except Exception as e:
    print(f"Error creating a table: {e}")
    raise
