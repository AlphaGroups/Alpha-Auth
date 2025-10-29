
from database import Base, engine
from models import *
from utils.class_seeder import seed_classes

def create_tables_and_classes():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

    # Insert classes 1-12 if not already present
    seed_classes()

if __name__ == "__main__":
    create_tables_and_classes()
