import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings, BASE_DIR

logger = logging.getLogger(__name__)

# Fallback database URL in case MySQL server is offline during initial local runs
SQLITE_FALLBACK_URL = f"sqlite:///{BASE_DIR / 'mediaplayer_fallback.db'}"

def get_engine():
    """Attempt connecting to configured MySQL database; fallback to SQLite with warning if MySQL is unreachable."""
    try:
        connect_args = {}
        if settings.DB_SSL_CA and os.path.exists(settings.DB_SSL_CA):
            connect_args["ssl_ca"] = str(settings.DB_SSL_CA)
            
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args=connect_args,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        # Test connection
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info(f"Connected successfully to MySQL Database: {settings.DB_NAME}")
        return engine
    except Exception as e:
        logger.warning(
            f"Unable to connect to MySQL database ({e}). "
            f"Falling back to local SQLite database for instant development/testing mode: {SQLITE_FALLBACK_URL}"
        )
        engine = create_engine(
            SQLITE_FALLBACK_URL,
            connect_args={"check_same_thread": False},
            echo=False
        )
        return engine

engine = get_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """FastAPI Dependency for database sessions."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
