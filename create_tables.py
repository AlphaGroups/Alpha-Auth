from database import engine, Base
from models import User, Video

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()
