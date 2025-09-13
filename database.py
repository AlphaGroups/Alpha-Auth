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

# database.py

# database.py
import os
from typing import Generator, AsyncGenerator, Optional

# prefer ENV; fallback to APP_ENV for backward compatibility
ENV = os.getenv("ENV", os.getenv("APP_ENV", "development")).lower()

# SQL globals (development)
engine = None
SessionLocal = None
Base = None

# Mongo globals (production)
mongo_client = None
mongo_db = None

if ENV == "development":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, declarative_base

    DB_HOST = os.getenv("DB_HOST", "db")        # use "db" in docker-compose
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_NAME = os.getenv("DB_NAME", "auth_db")

    SQLALCHEMY_DATABASE_URL = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    def get_db() -> Generator:
        """Sync dependency for SQLAlchemy sessions."""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

else:
    # production -> MongoDB (async)
    from motor.motor_asyncio import AsyncIOMotorClient

    MONGO_URI = os.getenv("MONGO_URI") or os.getenv("MONGO_URL")
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI must be set when ENV=production")

    mongo_client = AsyncIOMotorClient(MONGO_URI)
    mongo_db_name = os.getenv("MONGO_DB_NAME")
    if mongo_db_name:
        mongo_db = mongo_client[mongo_db_name]
    else:
        mongo_db = mongo_client.get_default_database()

    async def get_db() -> AsyncGenerator:
        """Async dependency returning motor Database object."""
        yield mongo_db
