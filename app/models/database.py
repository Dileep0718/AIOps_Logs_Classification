"""

database.py

-----------

Sets up the SQLAlchemy database engine and session.
 
- engine   : the actual connection to PostgreSQL

- SessionLocal : a factory that creates DB sessions

- Base     : all ORM models inherit from this
 
Other files import get_db for dependency injection in FastAPI routes.

"""
 
from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker

from app.config import settings
 
# create the engine — this is the actual connection to PostgreSQL

engine = create_engine(

    settings.DATABASE_URL,

    # pool_pre_ping checks if connection is alive before using it

    # prevents "connection closed" errors after idle periods

    pool_pre_ping=True

)
 
# SessionLocal is a class — each request creates one instance of it

SessionLocal = sessionmaker(

    autocommit=False,

    autoflush=False,

    bind=engine

)
 
# Base class — all ORM models (db_models.py) inherit from this

Base = declarative_base()
 
 
def get_db():

    """

    FastAPI dependency — provides a DB session per request.
 
    Usage in a router:

        def my_endpoint(db: Session = Depends(get_db)):

            ...
 
    The 'finally' ensures the session is always closed

    even if an error occurs mid-request.

    """

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()
 