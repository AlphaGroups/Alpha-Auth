from database import SessionLocal
from models import Class

def seed_classes():
    """
    Ensures that classes 1-12 exist in the database.
    This function can be called during deployment/build to ensure required classes exist.
    """
    db = SessionLocal()
    try:
        # Check if any classes exist
        existing_classes_count = db.query(Class).count()
        
        if existing_classes_count == 0:
            # Create classes 1-12 if none exist
            classes = [Class(name=str(i)) for i in range(1, 13)]
            db.add_all(classes)
            db.commit()
            print("✅ Classes 1–12 inserted during build process")
            return True
        else:
            print(f"ℹ️ {existing_classes_count} classes already exist in database")
            return False
    except Exception as e:
        print(f"❌ Error seeding classes: {str(e)}")
        db.rollback()
        raise e
    finally:
        db.close()


def check_classes_exist():
    """
    Checks if classes 1-12 exist in the database
    """
    db = SessionLocal()
    try:
        existing_classes = db.query(Class).all()
        existing_class_names = [cls.name for cls in existing_classes]
        
        required_classes = [str(i) for i in range(1, 13)]
        missing_classes = [cls for cls in required_classes if cls not in existing_class_names]
        
        return len(missing_classes) == 0, missing_classes
    finally:
        db.close()