from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Database URL: {SQLALCHEMY_DATABASE_URL}")

# For PostgreSQL, we don't need connect_args={"check_same_thread": False}
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,          # Keep 5 connections ready
    max_overflow=10,      # Allow up to 10 extra if busy
    pool_timeout=30,      # Wait 30s before giving up
    pool_recycle=1800,    # Refresh connection every 30 mins
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session in routes
def get_db():
    print("Database Connected!!!")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()