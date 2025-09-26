
from database import Base, engine, SessionLocal
from models import *

def create_tables_and_classes():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

    # Insert classes 1-12 if not already present
    db = SessionLocal()
    try:
        if db.query(Class).count() == 0:
            classes = [Class(name=str(i)) for i in range(1, 13)]
            db.add_all(classes)
            db.commit()
            print("Inserted classes 1-12")
        else:
            print("Classes already exist")
    finally:
        db.close()

if __name__ == "__main__":
    create_tables_and_classes()
