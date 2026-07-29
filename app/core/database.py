from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Step 1: Load variables from .env file
load_dotenv()

# Step 2: Read the database URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Step 3: Create engine — opens connection to PostgreSQL
engine = create_engine(DATABASE_URL)

# Step 4: Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Step 5: Base class for all models
Base = declarative_base()


def get_db():
    """
    This function is used in every API route.
    Opens a database session, gives it to the route,
    then closes it automatically when done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Creates all tables in PostgreSQL based on your models."""
    Base.metadata.create_all(bind=engine)