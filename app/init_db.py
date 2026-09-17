import sys
import os
import logging
from sqlalchemy import create_engine, text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from app.models import Base
from app.ingestion import ingest_knowledge_base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """Single script to enable pgvector, create database tables, and run knowledge base ingestion."""
    logger.info(f"Connecting to database: {settings.DATABASE_URL.split('@')[-1]}")
    
    try:
        engine = create_engine(settings.DATABASE_URL, connect_args={"connect_timeout": 5})
        with engine.connect() as conn:
            logger.info("Enabling pgvector extension...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
            
        logger.info("Creating database tables...")
        Base.metadata.create_all(engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.warning(f"Database connection note ({e}). Will run local vector store fallback.")
        
    logger.info("Starting Knowledge Base document ingestion and vector embedding...")
    accepted, skipped = ingest_knowledge_base()
    logger.info(f"Initialization Complete! {len(accepted)} chunks indexed, {len(skipped)} redundant chunks filtered.")

if __name__ == "__main__":
    initialize_database()
