from database import engine
from sqlalchemy import text

def add_missing_columns():
    with engine.connect() as conn:
        # Add class_id column
        try:
            conn.execute(text("ALTER TABLE students ADD COLUMN class_id INT NULL"))
            conn.commit()
            print("Added class_id column to students table")
        except Exception as e:
            print(f"Error adding class_id column: {e}")
            conn.rollback()
        
        # Add section column
        try:
            conn.execute(text("ALTER TABLE students ADD COLUMN section VARCHAR(10) NULL"))
            conn.commit()
            print("Added section column to students table")
        except Exception as e:
            print(f"Error adding section column: {e}")
            conn.rollback()

if __name__ == "__main__":
    add_missing_columns()