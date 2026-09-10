import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from pymongo import MongoClient
from config import settings

logger = logging.getLogger(__name__)

# ============================================================
# DATABASE CONNECTION
# ============================================================

# Try PostgreSQL first; if unavailable, fallback to local SQLite
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
    logger.warning(
        f"PostgreSQL connection failed ({e}). "
        "Falling back to local SQLite database."
    )

    engine = create_engine(
        "sqlite:///./funding_innovation_platform.db",
        connect_args={"check_same_thread": False}
    )


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# ============================================================
# AUTO MIGRATION
# ============================================================

def auto_migrate_schema(target_engine):
    """
    Auto-healing schema migration for developer SQLite
    and PostgreSQL environments.

    This specifically handles the source_id column that
    was missing from older funding_opportunities tables.
    """

    try:
        with target_engine.connect() as conn:

            try:
                # Check whether source_id already exists
                conn.execute(
                    text(
                        "SELECT source_id "
                        "FROM funding_opportunities "
                        "LIMIT 1"
                    )
                )

            except Exception:

                try:
                    conn.execute(
                        text(
                            "ALTER TABLE funding_opportunities "
                            "ADD COLUMN source_id INTEGER "
                            "REFERENCES funding_sources(id) "
                            "ON DELETE SET NULL"
                        )
                    )

                    if hasattr(conn, "commit"):
                        conn.commit()

                    logger.info(
                        "Auto-healing schema migration: "
                        "Successfully added 'source_id' column "
                        "to funding_opportunities."
                    )

                except Exception as ex:
                    logger.debug(
                        f"Migration note: {ex}"
                    )

    except Exception as e:
        logger.debug(
            f"Schema migration check skipped: {e}"
        )


# Run schema migration
auto_migrate_schema(engine)


# ============================================================
# MONGODB
# ============================================================

try:
    mongo_client = MongoClient(
        settings.MONGO_URL,
        serverSelectionTimeoutMS=1000
    )

    mongo_client.admin.command("ping")

    mongo_db = mongo_client[settings.MONGO_DB_NAME]

    logger.info(
        "Connected to MongoDB database successfully."
    )

except Exception as e:
    logger.warning(
        f"MongoDB connection unavailable ({e}). "
        "Running without raw payload document cache."
    )

    mongo_client = None
    mongo_db = None


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# MONGODB HELPER
# ============================================================

def get_mongo_db():
    return mongo_db