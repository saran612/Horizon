from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

# Create the SQLAlchemy engine
# Future: We can adjust pool size or use async pg if needed
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base for models
Base = declarative_base()

def get_db():
    """
    Dependency generator function to yield a database session
    and guarantee closing it after requests.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
