import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from pymongo import MongoClient
from config import settings

logger = logging.getLogger(__name__)

# Try PostgreSQL first; if unavailable, fallback to local SQLite for instant developer setup
try:
    engine = create_engine(
        settings.POSTGRES_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("Connected to PostgreSQL database successfully.")
except Exception as e:
    logger.warning(f"PostgreSQL connection failed ({e}). Falling back to local SQLite database.")
    engine = create_engine(
        "sqlite:///./funding_innovation_platform.db",
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MongoDB PyMongo Client
try:
    mongo_client = MongoClient(settings.MONGO_URL, serverSelectionTimeoutMS=1000)
    mongo_client.admin.command('ping')
    mongo_db = mongo_client[settings.MONGO_DB_NAME]
    logger.info("Connected to MongoDB database successfully.")
except Exception as e:
    logger.warning(f"MongoDB connection unavailable ({e}). Running without raw payload document cache.")
    mongo_client = None
    mongo_db = None

# Dependency to get DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper to get MongoDB instance
def get_mongo_db():
    return mongo_db