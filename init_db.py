#!/usr/bin/env python3
"""
Initialization script to ensure essential data exists in the database.
This script can be run:
1. During the build process
2. Before starting the application
3. As a manual step to fix missing data
"""

import sys
import os
import time
from sqlalchemy.exc import OperationalError, DatabaseError

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.class_seeder import seed_classes, check_classes_exist
from database import engine
from utils.class_seeder import seed_classes

def wait_for_database(max_retries=30, delay=2):
    """
    Wait for the database to be ready before attempting to connect.
    Useful in Docker environments where the DB container might start after the app container.
    """
    for attempt in range(max_retries):
        try:
            # Try to connect to the database
            with engine.connect() as conn:
                # Simple query to test if database is ready
                result = conn.execute("SELECT 1")
                print("✅ Database connection successful!")
                return True
        except (OperationalError, DatabaseError) as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Database not ready yet (attempt {attempt + 1}/{max_retries}): {str(e)}")
                time.sleep(delay)
            else:
                print(f"❌ Failed to connect to database after {max_retries} attempts")
                raise e
    return False

def main():
    print("Starting application initialization...")
    
    # Wait for the database to be ready
    print("Waiting for database to be ready...")
    try:
        wait_for_database()
    except Exception as e:
        print(f"❌ Error waiting for database: {str(e)}")
        sys.exit(1)
    
    # Seed the classes
    print("Seeding classes 1-12 if they don't exist...")
    try:
        success = seed_classes()
        if success:
            print("✅ Essential classes (1-12) have been created successfully!")
        else:
            print("ℹ️ Essential classes (1-12) already existed in the database.")
    except Exception as e:
        print(f"❌ Error during class seeding: {str(e)}")
        sys.exit(1)
    
    # Verify all required classes exist
    print("Verifying all required classes exist...")
    try:
        all_exist, missing = check_classes_exist()
        if all_exist:
            print("✅ All required classes (1-12) are confirmed to exist!")
        else:
            print(f"⚠️ Some classes are missing: {missing}")
    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")
        sys.exit(1)
    
    print("Application initialization completed successfully!")
    print("The application can now start with all essential data in place.")

if __name__ == "__main__":
    main()