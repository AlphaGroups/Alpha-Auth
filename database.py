# # database.py
# import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base

# DB_HOST = os.getenv("DB_HOST", "localhost")
# DB_PORT = os.getenv("DB_PORT", "3308")
# DB_USER = os.getenv("DB_USER", "user")
# DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
# DB_NAME = os.getenv("DB_NAME", "auth_db")

# SQLALCHEMY_DATABASE_URL = (
#     f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# )

# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()


# # ✅ Dependency for FastAPI routes
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import time
import logging

# Load environment variables based on environment
# In production, environment variables are set by Render directly
# So we don't need to load from .env files
if os.getenv("APP_ENV") == "production":
    pass  # Environment variables are already loaded by Render
else:
    # For development, load from appropriate .env file
    env = os.getenv("ENV", "development")
    if env == "production":
        load_dotenv(".env.production")
    else:
        load_dotenv(".env.development")

# ✅ In production, use DATABASE_URL directly
DATABASE_URL = os.getenv("DATABASE_URL")

# If DATABASE_URL is missing, assume local MySQL (development)
if not DATABASE_URL:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3308")
    DB_USER = os.getenv("DB_USER", "user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_NAME = os.getenv("DB_NAME", "auth_db")

    # For Docker containers, use the service name instead of localhost
    if os.getenv("ENV") == "docker" or os.getenv("APP_ENV") == "development":
        # When running in Docker, the MySQL service is accessible by its container name
        DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@db:{DB_PORT}/{DB_NAME}"
    else:
        DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ✅ Create engine - the database driver will be determined by the URL scheme
def create_engine_with_retry():
    max_retries = 10
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            return create_engine(DATABASE_URL, pool_pre_ping=True)
        except Exception as e:
            if attempt == max_retries - 1:
                logging.error(f"Failed to create database engine after {max_retries} attempts: {str(e)}")
                raise e
            logging.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay}s...")
            time.sleep(retry_delay)

engine = create_engine_with_retry()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
