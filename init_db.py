"""
Database Initializer and Seeder Script
Run this script to initialize the MySQL database and seed initial data:
    python init_db.py
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from app.config import settings, BASE_DIR
from app.database import Base, engine, SessionLocal
from app.utils.seed_data import seed_database
import app.models  # Ensures all models are registered

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def create_mysql_database_if_needed():
    """Connects to MySQL server root without database and creates database if missing."""
    try:
        connect_args = {}
        if settings.DB_SSL_CA and os.path.exists(settings.DB_SSL_CA):
            connect_args["ssl_ca"] = str(settings.DB_SSL_CA)
        root_url = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}"
        temp_engine = create_engine(root_url, connect_args=connect_args, isolation_level="AUTOCOMMIT")
        with temp_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
        logger.info(f"MySQL database '{settings.DB_NAME}' checked/created successfully.")
    except Exception as e:
        logger.warning(f"Could not automatically create MySQL database: {e}")

def main():
    logger.info("Starting Media Player Database Initialization...")
    
    # 1. Try creating MySQL database
    if "mysql" in settings.DATABASE_URL:
        create_mysql_database_if_needed()
    
    # 2. Create tables
    logger.info("Creating all tables from SQLAlchemy models...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created successfully.")
    
    # 3. Seed data
    logger.info("Seeding realistic Figma Media Player mock data...")
    db = SessionLocal()
    try:
        result = seed_database(db)
        logger.info(f"Seed result: {result}")
    finally:
        db.close()
    
    logger.info("Database initialization completed successfully!")

if __name__ == "__main__":
    main()
